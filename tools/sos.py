"""SOS script files (RES/SCRIPT/SC/*.SOS, YKLZ-decompressed). See docs/re/script.md.

Layout (u32 LE header):
  0x00 magic 0x68744c87   0x04 version 2   0x08 0x140   0x0C file size
  0x10 table_off (0x140)  0x14 code_off   0x18 pool_off   0x1C msgtab_off   0x20 strtab_off   0x24 pool_off again
  0x28 u16 table_size, code_size, pool_size, n_msgs, n_strs, u16 (1)
  0x40..0x140  256-byte S-box: pool bytes are stored as enc, plain = sbox[enc ^ (-(i - pool_off) & 0xff)]
  msgtab_off: u16 pool offset per message index (dialogue lines); strtab_off: u16 pool offset per string index
  (speaker names, choices, resource paths). pool: NUL-terminated Shift-JIS strings, deduplicated.
A "slot" is one unique pool offset; tables point at slots, so a rebuild rewrites the pool and both tables.
"""
import struct

MAGIC = 0x68744C87


def parse(d):
    magic, ver, _, size, t_off, c_off, p_off, m_off, s_off, p_off2 = struct.unpack_from("<10I", d, 0)
    assert magic == MAGIC and size == len(d) and p_off == p_off2, (hex(magic), size, len(d))
    t_sz, c_sz, p_sz, n_msg, n_str, one = struct.unpack_from("<6H", d, 0x28)
    assert p_off + p_sz == size and m_off + 2 * n_msg == s_off and s_off + 2 * n_str == p_off, "layout"
    sbox = d[0x40:0x140]
    pool = bytes(sbox[d[i] ^ (-(i - p_off) & 0xFF)] for i in range(p_off, size))
    moffs = struct.unpack_from(f"<{n_msg}H", d, m_off)
    soffs = struct.unpack_from(f"<{n_str}H", d, s_off)
    slots = {}
    o = 0
    while o < len(pool):  # every NUL-terminated run in pool order, referenced or not
        e = pool.index(b"\0", o)
        slots[o] = pool[o:e]
        o = e + 1
    for x in moffs + soffs:
        assert x in slots, f"table points mid-string at {x:#x}"
    return dict(pool_off=p_off, msg_off=m_off, str_off=s_off, moffs=moffs, soffs=soffs, slots=slots)


def is_text(s):
    """Resource names vs. displayable text: any non-ASCII byte, or ASCII without path characters."""
    if not s:
        return False
    if any(b >= 0x80 for b in s):
        return True
    t = s.decode("ascii", "replace")
    return not ("\\" in t or "." in t)


def build(d, new=None):
    """Rebuild with new bytes per slot ({pool_offset: bytes}); slots keep their order, pool re-obfuscated."""
    info = parse(d)
    new = new or {}
    p_off = info["pool_off"]
    pool = bytearray()
    remap = {}
    for o, s in info["slots"].items():
        remap[o] = len(pool)
        pool += new.get(o, s) + b"\0"
    assert len(pool) < 0x10000, "pool over 64 KiB (u16 offsets)"
    sbox = d[0x40:0x140]
    inv = [0] * 256
    for k, v in enumerate(sbox):
        inv[v] = k
    out = bytearray(d[:p_off])
    struct.pack_into(f"<{len(info['moffs'])}H", out, info["msg_off"], *[remap[x] for x in info["moffs"]])
    struct.pack_into(f"<{len(info['soffs'])}H", out, info["str_off"], *[remap[x] for x in info["soffs"]])
    out += bytes(inv[b] ^ (-j & 0xFF) for j, b in enumerate(pool))
    struct.pack_into("<I", out, 0x0C, len(out))
    struct.pack_into("<H", out, 0x2C, len(pool))
    return bytes(out)
