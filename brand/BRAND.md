# SAT Freshman — brand reference

Taken from `SAT_FINAL` (the designer's export), 2026-09-20. Assets are copied
into this directory so UI work does not depend on a Downloads folder.

## The name

**SAT Freshman.** The wordmark sets it on two lines — SAT above FRESHMAN — in
the stacked and horizontal lockups alike.

## Colour

| token | hex | where it comes from |
|---|---|---|
| orange | `#F18508` | the mark, and 26% of the lockup's pixels |
| graphite | `#3F3F3F` | the wordmark — **not** black, and not a neutral grey |
| white | `#FFFFFF` | the reversed artwork |

**The orange is `#F18508`, not `#F18D05`.** The two were given to me the other
way round earlier and they are different colours — the middle pair of digits is
transposed. `F18508` is what the logo file actually contains, so it is the one
that is right; anything already built against `F18D05` disagrees with the logo
by a visible amount.

Graphite is worth protecting too. `#3F3F3F` is a warm-neutral dark grey, and
substituting `#000` or a blue-grey would make every page look slightly unlike
the logo sitting on it.

### Contrast, before anyone builds a button

White text on `#F18508` is about **2.4:1** and fails WCAG AA for body text. A
primary button in brand orange needs a dark label — graphite or near-black —
not white. Orange as *text* on white is also too low for small sizes; keep it
for fills, marks and large display type.

## The lockups

Three pairs, each in colour and in white (reversed, for dark grounds):

| file | ratio | use |
|---|---|---|
| `logo-horizontal.png` / `-white` | 5.89 : 1 | headers, wide furniture |
| `logo-stacked.png` / `-white` | 2.03 : 1 | square-ish spaces, splash, share cards |
| `mark.png` / `-white` | 1 : 1 | favicon, avatar, collapsed nav, loading state |

`SAT_LOGO.svg` is the vector master (viewBox 0 0 1080 1080). Prefer it over the
PNGs anywhere it can be used — the PNGs are 4x raster exports.

The **white versions are artwork, not backgrounds**: opened on a white page they
look like empty files. That is correct, and it is why one of them appeared blank
on first inspection.

## The mark

A rounded square with four gaps cut into it, mid-edge — an aperture, a target, a
bracket around something. It reads as "focus on this", which is apt for a
diagnostic product, and it survives being shrunk to a favicon because the
counter is large and the gaps are wide.

## Typography — NOT in this folder

The wordmark is outlined paths, so the export carries no font. It is a heavy
grotesque with tight spacing and flat terminals. **The typeface is unknown and
must be asked for before UI type is chosen** — picking something that merely
resembles it is how a product ends up with a logo that looks pasted on.

Until then, nothing should hard-code a display face.
