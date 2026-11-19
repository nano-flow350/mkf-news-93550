#!/usr/bin/env python3
# news-image-20261119 - make.fun competition entry (nano-flow350)
# Renders a 1024x768 newspaper front page as a PNG, stdlib only.

import os
import struct
import zlib

W, H = 1024, 768

# palette (seeded by nano-flow350: warm newsprint, oxblood red, slate teal)
PAPER = (243, 237, 220)
INK = (23, 20, 16)
RED = (142, 43, 30)
SLATE = (46, 85, 83)
SHADE = (228, 217, 192)
MID = (140, 128, 102)

# built-in 5x7 bitmap font: each glyph is 7 row bitmasks, bit 4 = leftmost pixel
FONT = {
    ' ': (0, 0, 0, 0, 0, 0, 0),
    'A': (0x0E, 0x11, 0x11, 0x1F, 0x11, 0x11, 0x11),
    'B': (0x1E, 0x11, 0x11, 0x1E, 0x11, 0x11, 0x1E),
    'C': (0x0E, 0x11, 0x10, 0x10, 0x10, 0x11, 0x0E),
    'D': (0x1E, 0x11, 0x11, 0x11, 0x11, 0x11, 0x1E),
    'E': (0x1F, 0x10, 0x10, 0x1E, 0x10, 0x10, 0x1F),
    'F': (0x1F, 0x10, 0x10, 0x1E, 0x10, 0x10, 0x10),
    'G': (0x0E, 0x11, 0x10, 0x17, 0x11, 0x11, 0x0E),
    'H': (0x11, 0x11, 0x11, 0x1F, 0x11, 0x11, 0x11),
    'I': (0x0E, 0x04, 0x04, 0x04, 0x04, 0x04, 0x0E),
    'J': (0x01, 0x01, 0x01, 0x01, 0x11, 0x11, 0x0E),
    'K': (0x11, 0x12, 0x14, 0x18, 0x14, 0x12, 0x11),
    'L': (0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0x1F),
    'M': (0x11, 0x1B, 0x15, 0x15, 0x11, 0x11, 0x11),
    'N': (0x11, 0x19, 0x15, 0x13, 0x11, 0x11, 0x11),
    'O': (0x0E, 0x11, 0x11, 0x11, 0x11, 0x11, 0x0E),
    'P': (0x1E, 0x11, 0x11, 0x1E, 0x10, 0x10, 0x10),
    'Q': (0x0E, 0x11, 0x11, 0x11, 0x15, 0x12, 0x0D),
    'R': (0x1E, 0x11, 0x11, 0x1E, 0x14, 0x12, 0x11),
    'S': (0x0F, 0x10, 0x10, 0x0E, 0x01, 0x01, 0x1E),
    'T': (0x1F, 0x04, 0x04, 0x04, 0x04, 0x04, 0x04),
    'U': (0x11, 0x11, 0x11, 0x11, 0x11, 0x11, 0x0E),
    'V': (0x11, 0x11, 0x11, 0x11, 0x11, 0x0A, 0x04),
    'W': (0x11, 0x11, 0x11, 0x15, 0x15, 0x1B, 0x11),
    'X': (0x11, 0x11, 0x0A, 0x04, 0x0A, 0x11, 0x11),
    'Y': (0x11, 0x11, 0x0A, 0x04, 0x04, 0x04, 0x04),
    'Z': (0x1F, 0x01, 0x02, 0x04, 0x08, 0x10, 0x1F),
    '0': (0x0E, 0x11, 0x13, 0x15, 0x19, 0x11, 0x0E),
    '1': (0x04, 0x0C, 0x04, 0x04, 0x04, 0x04, 0x0E),
    '2': (0x0E, 0x11, 0x01, 0x02, 0x04, 0x08, 0x1F),
    '3': (0x1F, 0x02, 0x04, 0x02, 0x01, 0x11, 0x0E),
    '4': (0x02, 0x06, 0x0A, 0x12, 0x1F, 0x02, 0x02),
    '5': (0x1F, 0x10, 0x1E, 0x01, 0x01, 0x11, 0x0E),
    '6': (0x06, 0x08, 0x10, 0x1E, 0x11, 0x11, 0x0E),
    '7': (0x1F, 0x01, 0x02, 0x04, 0x08, 0x08, 0x08),
    '8': (0x0E, 0x11, 0x11, 0x0E, 0x11, 0x11, 0x0E),
    '9': (0x0E, 0x11, 0x11, 0x0F, 0x01, 0x02, 0x0C),
    '.': (0, 0, 0, 0, 0, 0x0C, 0x0C),
    ',': (0, 0, 0, 0, 0x0C, 0x04, 0x08),
    ':': (0, 0x0C, 0x0C, 0, 0x0C, 0x0C, 0),
    ';': (0, 0x0C, 0x0C, 0, 0x0C, 0x04, 0x08),
    "'": (0x0C, 0x0C, 0x04, 0, 0, 0, 0),
    '!': (0x0C, 0x0C, 0x0C, 0x0C, 0x0C, 0, 0x0C),
    '?': (0x0E, 0x11, 0x01, 0x02, 0x04, 0, 0x04),
    '-': (0, 0, 0, 0x1F, 0, 0, 0),
    '/': (0x01, 0x01, 0x02, 0x04, 0x08, 0x10, 0x10),
    '&': (0x0C, 0x12, 0x14, 0x08, 0x15, 0x12, 0x0D),
    '(': (0x02, 0x04, 0x08, 0x08, 0x08, 0x04, 0x02),
    ')': (0x08, 0x04, 0x02, 0x02, 0x02, 0x04, 0x08),
    '%': (0x19, 0x1A, 0x02, 0x04, 0x08, 0x0B, 0x13),
    '$': (0x04, 0x0F, 0x14, 0x0E, 0x05, 0x1E, 0x04),
    '+': (0, 0x04, 0x04, 0x1F, 0x04, 0x04, 0),
    '=': (0, 0, 0x1F, 0, 0x1F, 0, 0),
    '#': (0x0A, 0x1F, 0x0A, 0x0A, 0x0A, 0x1F, 0x0A),
    '|': (0x04, 0x04, 0x04, 0x04, 0x04, 0x04, 0x04),
    '"': (0x0A, 0x0A, 0, 0, 0, 0, 0),
}


def px(buf, x, y, c):
    if 0 <= x < W and 0 <= y < H:
        i = (y * W + x) * 3
        buf[i] = c[0]
        buf[i + 1] = c[1]
        buf[i + 2] = c[2]


def rect(buf, x0, y0, x1, y1, c):
    for yy in range(max(0, y0), min(H, y1)):
        base = yy * W * 3
        for xx in range(max(0, x0), min(W, x1)):
            i = base + xx * 3
            buf[i] = c[0]
            buf[i + 1] = c[1]
            buf[i + 2] = c[2]


def hline(buf, x0, x1, y, t=1, c=INK):
    rect(buf, x0, y, x1, y + t, c)


def frame(buf, x0, y0, x1, y1, t=1, c=INK):
    hline(buf, x0, x1, y0, t, c)
    hline(buf, x0, x1, y1 - t, t, c)
    rect(buf, x0, y0, x0 + t, y1, c)
    rect(buf, x1 - t, y0, x1, y1, c)


def diamond(buf, cx, cy, r, c):
    for dy in range(-r, r + 1):
        w = r - abs(dy)
        rect(buf, cx - w, cy + dy, cx + w + 1, cy + dy + 1, c)


def text_w(s, sc):
    return len(s) * 6 * sc


def draw_text(buf, s, x, y, sc=1, c=INK):
    cx = x
    for ch in s:
        g = FONT.get(ch, FONT.get(' '))
        for r in range(7):
            bi = g[r]
            if not bi:
                continue
            for b in range(5):
                if (bi >> (4 - b)) & 1:
                    for dy in range(sc):
                        yy = y + r * sc + dy
                        for dx in range(sc):
                            px(buf, cx + b * sc + dx, yy, c)
        cx += 6 * sc


def draw_r(buf, s, xr, y, sc, c):
    draw_text(buf, s, xr - text_w(s, sc), y, sc, c)


def center_text(buf, s, y, sc, c, x0=0, x1=W):
    draw_text(buf, s, (x0 + x1 - text_w(s, sc)) // 2, y, sc, c)


def wrap(s, sc, width):
    lines, cur = [], ''
    for w in s.split():
        t = (cur + ' ' + w).strip()
        if text_w(t, sc) <= width:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def para(buf, s, x, y, sc, width, lh, c=INK):
    for ln in wrap(s, sc, width):
        draw_text(buf, ln, x, y, sc, c)
        y += lh
    return y


def photo(buf, x0, y0, x1, y1):
    rect(buf, x0, y0, x1, y1, SHADE)
    for yy in range(y0, y1):
        for xx in range(x0, x1):
            if (xx + yy) % 9 < 2:
                px(buf, xx, yy, MID)
    cx, cy = (x0 + x1) // 2, (y0 + y1) // 2
    bw, bh = 220, 112
    rect(buf, cx - bw // 2, cy - bh // 2, cx + bw // 2, cy + bh // 2, INK)
    draw_text(buf, 'VI', cx - text_w('VI', 12) // 2, cy - 42, 12, PAPER)


def section(buf, x0, y0, w, h, kicker, headline, body, accent=RED):
    frame(buf, x0, y0, x0 + w, y0 + h)
    rect(buf, x0 + 1, y0 + 1, x0 + w - 1, y0 + 20, accent)
    draw_text(buf, kicker, x0 + 10, y0 + 4, 2, PAPER)
    yy = y0 + 25
    for ln in wrap(headline, 2, w - 20):
        draw_text(buf, ln, x0 + 10, yy, 2, INK)
        yy += 16
    yy += 3
    for ln in wrap(body, 1, w - 20):
        draw_text(buf, ln, x0 + 10, yy, 1, INK)
        yy += 9


def markets(buf, x0, y0, w, h):
    frame(buf, x0, y0, x0 + w, y0 + h)
    rect(buf, x0 + 1, y0 + 1, x0 + w - 1, y0 + 20, SLATE)
    draw_text(buf, 'MARKETS', x0 + 10, y0 + 4, 2, PAPER)
    draw_r(buf, 'THU 19 NOV 2026 - LATE CLOSE', x0 + w - 10, y0 + 7, 1, PAPER)
    yy = y0 + 25
    for ln in wrap('STOCKS MIXED; GOLD NEAR RECORD AS FED PATH WEIGHED', 2, w - 20):
        draw_text(buf, ln, x0 + 10, yy, 2, INK)
        yy += 16
    yy += 2
    draw_text(buf, 'INDEX', x0 + 10, yy, 1, RED)
    draw_r(buf, 'CLOSE', x0 + w - 70, yy, 1, RED)
    draw_r(buf, 'CHANGE', x0 + w - 10, yy, 1, RED)
    yy += 9
    rows = [
        ('FTSE 100', '9,842.10', '+0.4%'),
        ('S&P 500', '7,120.55', '+0.2%'),
        ('NIKKEI 225', '51,304.22', '-0.3%'),
        ('GOLD $/OZ', '4,210.30', '+1.1%'),
        ('EUR/USD', '1.1720', '+0.1%'),
    ]
    for name, close, chg in rows:
        draw_text(buf, name, x0 + 10, yy, 1, INK)
        draw_r(buf, close, x0 + w - 70, yy, 1, INK)
        draw_r(buf, chg, x0 + w - 10, yy, 1, RED if chg[0] == '-' else SLATE)
        yy += 9


def facts(buf, x0, y0, w, h):
    frame(buf, x0, y0, x0 + w, y0 + h)
    rect(buf, x0 + 1, y0 + 1, x0 + w - 1, y0 + 15, INK)
    draw_text(buf, 'GTA VI - THE FACTS', x0 + 8, y0 + 4, 1, PAPER)
    rows = [
        ('LAUNCH', 'THU 19 NOV 2026'),
        ('PLATFORMS', 'PS5 + XBOX X|S'),
        ('PRICE', 'FROM $69.99'),
        ('RATING', 'MATURE 17+'),
    ]
    yy = y0 + 21
    for k, v in rows:
        draw_text(buf, k, x0 + 8, yy, 1, RED)
        draw_text(buf, v, x0 + 92, yy, 1, INK)
        yy += 11


def quote(buf, x0, y0, w, h, q, who):
    frame(buf, x0, y0, x0 + w, y0 + h)
    yy = y0 + 6
    for ln in wrap(q, 1, w - 12):
        draw_text(buf, ln, x0 + 6, yy, 1, INK)
        yy += 9
    draw_text(buf, who, x0 + 6, y0 + h - 12, 1, RED)


def build():
    buf = bytearray(W * H * 3)
    rect(buf, 0, 0, W, H, PAPER)

    # masthead
    center_text(buf, "THE WORLD'S DAILY NEWSPAPER - EST. 1896 - VOL. CXXX - NO. 32,401", 6, 1, INK)
    center_text(buf, 'WORLD NEWS', 20, 8, INK)
    diamond(buf, 238, 48, 6, RED)
    diamond(buf, 786, 48, 6, RED)
    draw_text(buf, 'LATE EDITION', 32, 90, 1, RED)
    center_text(buf, 'THURSDAY 19 NOVEMBER 2026', 86, 2, INK)
    draw_r(buf, 'PRICE $1.50', 992, 90, 1, RED)
    hline(buf, 32, 992, 100, 2)
    hline(buf, 32, 992, 105, 1)

    # lead story: GTA VI launch day
    draw_text(buf, 'GAMING / LAUNCH DAY', 32, 114, 2, RED)
    draw_text(buf, 'GTA VI HITS SHELVES WORLDWIDE', 32, 136, 4, INK)
    draw_text(buf, 'AS MIDNIGHT QUEUES SNAKE FOR CONSOLES', 32, 166, 4, INK)
    deck = ("ROCKSTAR'S LONG-AWAITED SEQUEL LANDS TODAY ON PS5 AND XBOX "
            'SERIES X|S, A DECADE ON; RETAILERS REPORT SELL-OUTS AS FANS '
            'CAMP OVERNIGHT FOR MIDNIGHT COPIES.')
    para(buf, deck, 32, 198, 2, 960, 16, SLATE)
    hline(buf, 32, 992, 232, 1)

    photo(buf, 32, 244, 452, 420)
    para(buf, 'Fans queue for the midnight release of GTA VI in London. PRESS ASSOCIATION IMAGE',
         32, 426, 1, 420, 9, INK)

    col1 = ("The biggest entertainment launch of the year arrived at midnight as GTA VI "
            'went on sale across the world, a decade after the previous chapter. Fans '
            'queued outside stores in London, New York and Tokyo, many dressed as '
            'characters from the series, as retailers reported sell-out within hours. '
            'Queues formed from early evening, with the largest crowds reported in '
            'central London, where the flagship store stayed open all night to meet '
            'demand.')
    para(buf, col1, 470, 244, 1, 256, 9, INK)

    facts(buf, 736, 244, 256, 68)

    quote(buf, 470, 356, 160, 68,
          'THE HYPE IS REAL. BIGGEST LAUNCH WE HAVE SEEN.', '- FAN, LONDON')
    quote(buf, 638, 356, 160, 68,
          'SOLD OUT BY 12:05AM. QUEUES ROUND THE BLOCK.', '- RETAILER, TOKYO')
    quote(buf, 806, 356, 186, 68,
          'CONSOLE BUNDLES FLEW OFF THE SHELVES ALL NIGHT.', '- CITY ANALYST')

    # section grid
    markets(buf, 32, 486, 476, 114)
    section(buf, 516, 486, 476, 114, 'CLIMATE - COP31',
            'ANTALYA TALKS ENTER FINAL DAYS WITH FINANCE DEAL IN SIGHT',
            'Ministers arrived in Antalya for the last two days of the COP31 summit as '
            'negotiators said a package on adaptation finance for vulnerable nations was '
            'close. A final communique is expected on Friday.', RED)
    section(buf, 32, 608, 476, 114, 'TECHNOLOGY / AI - CHIPS',
            'AI CHIP DEMAND SURGES AS DATA-CENTER BUILD-OUT SPEEDS UP',
            'Hyperscalers unveiled a new wave of data-center projecthis week as '
            'chipmakers reported surging demand for AI accelerators, with one leading '
            'supplier saying orders now stretch into late 2028.', SLATE)
    section(buf, 516, 608, 476, 114, 'SPORT',
            'LATE DRAMAS IN CHAMPIONS LEAGUE AS LEAGUE PHASE HITS HALFWAY',
            'Stoppage-time winners lit up the Champions League on Wednesday night as the '
            'league phase reached the halfway mark, with several big names still chasing '
            'a place in the knockout rounds.', RED)

    # briefs + folio
    hline(buf, 32, 992, 730, 1)
    draw_text(buf, 'IN BRIEF', 32, 736, 1, RED)
    draw_text(buf, 'TOKYO: BOJ HOLDS RATES | LONDON: TUBE STRIKE CALLED OFF | '
                   'NAIROBI: POWER GRID LINK OPENS | PARIS: LOUVRE PLAN APPROVED',
              92, 736, 1, INK)
    center_text(buf, 'WORLD NEWS - THURSDAY 19 NOVEMBER 2026 - PAGE ONE', 750, 1, INK)
    hline(buf, 32, 992, 762, 1)
    return buf


def png_bytes(buf):
    raw = b''.join(b'\x00' + bytes(buf[y * W * 3:(y + 1) * W * 3]) for y in range(H))

    def chunk(tag, data):
        body = tag + data
        return struct.pack('>I', len(data)) + body + struct.pack('>I', zlib.crc32(body) & 0xffffffff)

    ihdr = struct.pack('>IIBBBBB', W, H, 8, 2, 0, 0, 0)
    return (b'\x89PNG\r\n\x1a\n'
            + chunk(b'IHDR', ihdr)
            + chunk(b'IDAT', zlib.compress(raw, 9))
            + chunk(b'IEND', b''))


def main():
    data = png_bytes(build())
    outdir = os.environ.get('MAKEFUN_OUTPUT_DIR') or 'out'
    os.makedirs(outdir, exist_ok=True)
    path = os.path.join(outdir, 'entry.png')
    with open(path, 'wb') as f:
        f.write(data)
    print('%s %d bytes' % (path, len(data)))


if __name__ == '__main__':
    main()
