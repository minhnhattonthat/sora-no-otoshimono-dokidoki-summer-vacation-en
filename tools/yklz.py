"""YKLZ compression (verified against the EBOOT decoder at 0880B8C0; see docs/re/ptd.md).

Header (16 bytes): 'YKLZ', u8 0, u8 0, u8 method (0 stored, 1 LZ), u8 dbits (10), u32 LE out_size, u32 (unused by
the decoder). LZ stream from +0x10: flag byte, MSB first, bit 1 = reference. Reference b1 b2:
len = (b1 >> (dbits-8)) + 3, disp = ((b1 & ((1 << (dbits-8)) - 1)) << 8 | b2) + 1.
The game copies each reference with memcpy: a reference with len > disp (overlapping its own output) decodes wrong in
game (a repacked font lost every pixel equal to the one 2 or 18 bytes before). pack() never writes one;
unpack(strict=True) decodes the game's way to prove it.
"""
import struct


def unpack(data, strict=False):
    if data[:4] != b"YKLZ":
        return data
    method, dbits = data[6], data[7]
    size, = struct.unpack_from("<I", data, 8)
    if method == 0:
        return bytes(data[16:16 + size])
    shift = dbits - 8
    mask = (1 << shift) - 1
    out = bytearray()
    pos = 16
    while len(out) < size:
        flags = data[pos]
        pos += 1
        for _ in range(8):
            if len(out) >= size:
                break
            if flags & 0x80:
                b1, b2 = data[pos], data[pos + 1]
                pos += 2
                n = (b1 >> shift) + 3
                disp = ((b1 & mask) << 8 | b2) + 1
                assert not strict or n <= disp, f"overlapping reference at {pos - 2:#x}: len {n} > disp {disp}"
                for _ in range(n):
                    out.append(out[-disp])
            else:
                out.append(data[pos])
                pos += 1
            flags = (flags << 1) & 0xFF
    return bytes(out)


def pack(raw, dbits=10, tail=b""):
    """Greedy LZ compressor in the same format (any valid stream decodes; byte-identity with the original encoder is not
    required because rebuilt files replace whole archive entries). `tail` = original header bytes 12..15."""
    shift = dbits - 8
    maxlen = (0xFF >> shift) + 3
    maxdisp = 1 << dbits
    out = bytearray(b"YKLZ\x00\x00\x01" + bytes([dbits]) + struct.pack("<I", len(raw)) + (tail or b"\0\0\0\0"))
    heads = {}
    i, n = 0, len(raw)
    while i < n:
        flagpos = len(out)
        out.append(0)
        flags = 0
        for bit in range(8):
            if i >= n:
                break
            best, bestd = 0, 0
            if i + 3 <= n:
                for j in reversed(heads.get(raw[i:i + 3], [])):
                    d = i - j
                    if d > maxdisp:
                        break
                    if d < 3:
                        continue
                    l = 3
                    # the game copies a reference with memcpy (0x088ACA48), so a match may not overlap its own
                    # output (length <= displacement); byte-by-byte decoders like unpack() hide this
                    while l < min(maxlen, d) and i + l < n and raw[j + l] == raw[i + l]:
                        l += 1
                    if l > best:
                        best, bestd = l, d
                        if l == maxlen:
                            break
            if best >= 3:
                flags |= 0x80 >> bit
                dd = bestd - 1
                out += bytes([((best - 3) << shift) | (dd >> 8), dd & 0xFF])
                step = best
            else:
                out.append(raw[i])
                step = 1
            for k in range(i, i + step):
                if k + 3 <= n:
                    heads.setdefault(raw[k:k + 3], []).append(k)
            i += step
        out[flagpos] = flags
    return bytes(out)
