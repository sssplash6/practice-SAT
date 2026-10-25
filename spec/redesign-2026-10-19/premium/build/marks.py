"""Build web/assets/fonts/Marks.woff2: the marks Geist lacks, from DejaVu Sans 2.37.

Not shipped, not run at build time. Rerun only to change the set:
  python3 -I marks.py <DejaVuSans.ttf> <out.woff2>     (needs fontTools + brotli)
Source: github.com/dejavu-fonts/dejavu-fonts release version_2_37, ttf/DejaVuSans.ttf.
Licence: Bitstream Vera + DejaVu public domain changes (web/assets/fonts/MARKS-LICENSE.txt).
The family is renamed "Marks", as the Vera licence asks of modified copies.
"""
import sys
from fontTools.ttLib import TTFont
from fontTools.fontBuilder import FontBuilder
from fontTools.pens.recordingPen import DecomposingRecordingPen, RecordingPen
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.pens.boundsPen import BoundsPen

# every mark the app prints that Geist lacks (ICONS.md 1a plus a scan of web/), and the
# few Geist has that the brief asked for (‹ › « » · ○ ●: Geist wins those while it is first)
MARKS = "✓✕✗⋯▾▴▸⌄ⓘ↻↺⊘⊖○●◐★✎⚑■□⌫⌇⠿⁻‹›«»·"
GEIST = dict(upm=1000, cap=710, asc=1005, desc=-295, win_asc=1088, win_desc=262)


def main(src, out):
    dv = TTFont(src)
    gs, cmap = dv.getGlyphSet(), dv.getBestCmap()
    k = GEIST['cap'] / dv['glyf']['H'].yMax   # DejaVu's cap (1493 of 2048) lands on Geist's (710 of 1000)

    def outline(name):
        p = DecomposingRecordingPen(gs)
        gs[name].draw(p)
        return p.value

    def contours(rec):
        out, cur = [], []
        for op in rec:
            cur.append(op)
            if op[0] in ('closePath', 'endPath'):
                out.append(cur); cur = []
        return out

    def bounds(rec):
        b = BoundsPen(None)
        rp = RecordingPen(); rp.value = rec; rp.replay(b)
        return b.bounds

    glyphs, metrics, cm = {'.notdef': TTGlyphPen(None).glyph()}, {'.notdef': (round(600 * k), 0)}, {}
    for ch in MARKS:
        cp = ord(ch)
        if cp == 0x24D8:                       # DejaVu has (1)..(10) but no circled i: its ring plus its i
            ring_rec = contours(outline(cmap[0x2460]))
            bx = [bounds(c) for c in ring_rec]
            wide = max(b[2] - b[0] for b in bx)
            ring = [c for c, b in zip(ring_rec, bx) if b[2] - b[0] > wide * .6]
            digit = [b for c, b in zip(ring_rec, bx) if b[2] - b[0] <= wide * .6]
            dy0, dy1 = min(b[1] for b in digit), max(b[3] for b in digit)
            rx0, rx1 = min(b[0] for b in bx), max(b[2] for b in bx)
            irec = outline('i'); ib = bounds(irec)
            s = (dy1 - dy0) / (ib[3] - ib[1])
            tx = (rx0 + rx1) / 2 - (ib[0] + ib[2]) / 2 * s
            ty = dy0 - ib[1] * s
            adv = dv['hmtx'][cmap[0x2460]][0]
            pen = TTGlyphPen(None)
            tp = TransformPen(pen, (k, 0, 0, k, 0, 0))
            for c in ring:
                rp = RecordingPen(); rp.value = c; rp.replay(tp)
            rp = RecordingPen(); rp.value = irec
            rp.replay(TransformPen(pen, (k * s, 0, 0, k * s, k * tx, k * ty)))
        else:
            name = cmap[cp]
            adv = dv['hmtx'][name][0]
            pen = TTGlyphPen(None)
            rp = RecordingPen(); rp.value = outline(name); rp.replay(TransformPen(pen, (k, 0, 0, k, 0, 0)))
        gname = 'uni%04X' % cp
        glyphs[gname] = pen.glyph()
        metrics[gname] = (round(adv * k), 0)
        cm[cp] = gname

    order = list(glyphs)
    fb = FontBuilder(GEIST['upm'], isTTF=True)
    fb.setupGlyphOrder(order)
    fb.setupCharacterMap(cm)
    fb.setupGlyf(glyphs)
    glyf = fb.font['glyf']
    for n in order:                            # lsb = xMin, as TrueType expects
        g = glyf[n]; g.recalcBounds(glyf)
        metrics[n] = (metrics[n][0], getattr(g, 'xMin', 0))
    fb.setupHorizontalMetrics(metrics)
    fb.setupHorizontalHeader(ascent=GEIST['asc'], descent=GEIST['desc'], lineGap=0)
    fb.setupNameTable({
        'familyName': 'Marks', 'styleName': 'Regular', 'uniqueFontIdentifier': 'Marks-Regular-1.0',
        'fullName': 'Marks Regular', 'psName': 'Marks-Regular', 'version': 'Version 1.0',
        'copyright': 'Glyphs from DejaVu Sans 2.37: Copyright (c) 2003 by Bitstream, Inc. All Rights Reserved. '
                     'DejaVu changes are in public domain.',
        'licenseDescription': 'Bitstream Vera Fonts licence with DejaVu public domain changes; see MARKS-LICENSE.txt.',
    })
    fb.setupOS2(sTypoAscender=GEIST['asc'], sTypoDescender=GEIST['desc'], sTypoLineGap=0,
                usWinAscent=GEIST['win_asc'], usWinDescent=GEIST['win_desc'], usWeightClass=400,
                fsSelection=0xC0, sCapHeight=GEIST['cap'], achVendID='NONE', version=4)
    fb.setupPost(keepGlyphNames=False)
    fb.font.flavor = 'woff2'
    fb.save(out)

    # self-check: every mark mapped, nothing else
    f = TTFont(out)
    got = set(f.getBestCmap())
    assert got == {ord(c) for c in MARKS}, sorted(got ^ {ord(c) for c in MARKS})
    print(out, 'glyphs', len(f.getGlyphOrder()), 'code points', len(got))


if __name__ == '__main__':
    main(*sys.argv[1:3])
