"""PETA (.ptd) archive: header + obfuscated TOC. See docs/re/ptd.md.

Header: 'PETA', u32 toc_end, u32 file_size, u32 sbox_end (0x120), ...; bytes 0x20..0x120 are a 256-byte S-box.
TOC bytes [sbox_end, toc_end) are obfuscated: plain = sbox[enc ^ key], key = -(i - sbox_end) & 0xff.
(Deobfuscation from github.com/rzhumen88/ptd-unpacker, Mirai Nikki 13th Diary Holder, same engine.)
"""
import struct, sys


def header(buf):
    assert buf[:4] == b"PETA", buf[:4]
    toc_end, size, sbox_end = struct.unpack_from("<III", buf, 4)
    return toc_end, size, sbox_end


def obfuscated(buf):
    # guess: u32 at 0x14 is 0x00010030 in res.ptd (obfuscated TOC) and 2 in the nested __PACK__ PTDs (plain TOC)
    return buf[0x16] == 1


def deobf(buf):
    """Return the deobfuscated TOC region buf[sbox_end:toc_end]."""
    toc_end, _, sbox_end = header(buf)
    if not obfuscated(buf):
        return bytes(buf[sbox_end:toc_end])
    sbox = buf[0x20:0x120]
    return bytes(sbox[buf[i] ^ (-(i - sbox_end) & 0xFF)] for i in range(sbox_end, toc_end))


def obf(plain, sbox, sbox_end):
    inv = [0] * 256
    for k, v in enumerate(sbox):
        inv[v] = k
    return bytes(inv[p] ^ (-(j) & 0xFF) for j, p in enumerate(plain))


DIR_SIZE, FILE_SIZE = 0x50, 0x40


def toc(buf):
    """Return (dirs, files). dirs: [(name, first, count)]; files: [dict(path, name, off, size, comp)].
    Deobfuscated TOC: 0x50 bytes of zeros/root, then 0x50-byte dir records (u32 abs offset of the dir's first file
    record, u32 first index, u32 count, u32 0, name[64]), then 0x40-byte file records (u32 byte offset in the archive,
    u32 stored size, u32 flag (1 = YKLZ), u32 0, name[48]). File count = u32 at 0x10."""
    toc_end, size, sbox_end = header(buf)
    nfiles, = struct.unpack_from("<I", buf, 0x10)
    d = deobf(buf)
    dirs = []
    i = DIR_SIZE
    while True:
        a, first, cnt, _ = struct.unpack_from("<4I", d, i)
        name = d[i + 16:i + DIR_SIZE].split(b"\0")[0]
        if not name.startswith(b"RES"):
            break
        dirs.append((name.decode(), first, cnt))
        i += DIR_SIZE
    fstart = i
    owner = {}
    for name, first, cnt in dirs:
        for k in range(first, first + cnt):
            owner[k] = name
    files = []
    for k in range(nfiles):
        o = fstart + k * FILE_SIZE
        off, sz, comp, _ = struct.unpack_from("<4I", d, o)
        name = d[o + 16:o + FILE_SIZE].split(b"\0")[0].decode("ascii")
        files.append(dict(index=k, path=f"{owner.get(k, 'RES')}/{name}", name=name, off=off, size=sz, comp=comp,
                          rec=sbox_end + o))
    return dirs, files


if __name__ == "__main__":
    buf = open(sys.argv[1], "rb").read(0x400000)
    toc_end, size, sbox_end = header(buf)
    print(f"toc_end={toc_end:#x} size={size:#x} sbox_end={sbox_end:#x} hdr={buf[0x10:0x20].hex()}")
    for f in toc(buf)[1]:
        print(f["index"], hex(f["off"]), f["size"], f["comp"], f["path"])
