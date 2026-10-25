# Premium pass: depth, buttons, motion (measured references)

Measured in a real browser (Playwright, getComputedStyle, hover re-measured) on 2026-10-19 at 1440x900; Stripe also
at 390. Extends [../INSPO-VISUAL.md](../INSPO-VISUAL.md) (layout, type, selected states are there; not repeated).
Shots in `premium/shots/`. "m:" = measured value, "ours:" = adaptation to our tokens (`.pill` 42/10, `--amber`
fill with `--ink-deep` text, warm paper). smoothui motion values were read from its repo source, marked "src".

## 1. Per site

### 1.1 linear.app (home, /features, /changelog; dark)
Shots: `linear-home-1440`, `linear-panels-1440`, `linear-features-1440`, `linear-changelog-1440`.
- Easing tokens (m): `--ease-out-quad (.25,.46,.45,.94)`, `--ease-out-cubic (.215,.61,.355,1)`, `--ease-out-quart
  (.165,.84,.44,1)`, `--ease-out-expo (.19,1,.22,1)`, `--ease-in-out-cubic (.645,.045,.355,1)`. Speeds: quick 100, regular 250.
- Shadow tokens (m): low `0 2px 4px #0000001a`; medium `0 4px 24px #0003`; high `0 7px 32px #00000059`; stack-low
  `0 8px 2px #0000, 0 5px 2px #00000003, 0 3px 2px #0000000a, 0 1px 1px #00000012, 0 0 1px #00000014`.
- Primary (Sign up / Get started): 32 or 44 high, 9999 radius, fill `#E5E5E6` + 1px same border, text `#08090A`
  13/510 (16/510 at 44), padding 0 12 / 0 20, shadow = stack-low. Hover: fill to `#FFFFFF`, nothing else; transform
  none. Transition 160 quad on border, bg, colour, shadow, opacity, filter, transform.
- Secondary (Contact sales): fill `rgba(255,255,255,.05)`; `inset 0 0 0 1px rgba(255,255,255,.03), inset 0 1px 0
  rgba(255,255,255,.04), 0 0 0 1px rgba(0,0,0,.6), 0 4px 4px rgba(0,0,0,.1)`. Log in: text only, colour 100 quad.
- Floating panel (thread): r12 `#161718`, 1px `rgba(255,255,255,.12)`, `0 2px 32px rgba(0,0,0,.25)`; panel header
  hairline drawn as `0 1px 0 rgba(0,0,0,.4)`. Comment card r9: `0 0 0 1px rgba(0,0,0,.2)` outside a 1px `#ffffff14` border.
- Edge highlight: `::after` repeats the border in `#ffffff0f`, masked by `radial-gradient(ellipse 17% 29% at x y,
  #000, transparent)`, so only one stretch of the hairline catches light. `edgeGlow::before`: radial `#ffffff08` with
  stepped colour-mix stops (94/78/58%). Static position here, no transition.
- Icon tile (/features): 96, r24, `rgba(255,255,255,.05)` + `linear-gradient(rgba(255,255,255,.05), transparent)`
  sheen, 1px `#23252A`. Board: `mask-image: linear-gradient(#000 40%, transparent 90%), linear-gradient(to right,
  #000 68%, transparent 96%)` so the product dissolves into the page.
- Header: `backdrop-filter: blur(20px)` on `rgba(11,11,11,.8)` gradient. Focus: `#5E69D1`, 1px; send group `0 0 0 3px rgba(94,106,210,.4)`.
- Motion: dialogOpen `opacity 0, translate(-50%,-49%) scale(.95)` to rest (duration not measured); popover open
  `opacity 0 scale(.9)`; statusFlash `brightness 1 > 1.6 at 8% > 1 by 60%` ease-out-cubic; statusPulse ring
  `opacity .7 scale(.375) > 0 scale(1) at 60%`; Sonner toasts. /features: 124 decorative dots fade 700 ease-out with
  random delays .45-2.4 s, 3 marquees 20-30 s linear. /changelog: zero animations; images r8, no shadow.

### 1.2 vercel.com, /ai-gateway, Geist (/geist/button, /materials, /toast, /tabs)
Shots: `vercel-home-1440`, `vercel-home-grid-1440`, `vercel-product-ai-gateway-1440`, `vercel-geist-button-1440`,
`vercel-geist-materials-1440` (full page), `vercel-geist-toast-stack-1440`.
- Materials (m, light, white surface on `#FAFAFA`; every stack ends with `0 0 0 1px #FAFAFA`):

| Material | Radius | box-shadow before the page ring |
|---|---|---|
| base | 6 | `0 0 0 1px rgba(0,0,0,.08)` |
| small | 6 | base + `0 2px 2px rgba(0,0,0,.04)` |
| medium | 12 | small + `0 8px 8px -8px rgba(0,0,0,.04)` |
| large | 12 | small + `0 8px 16px -4px rgba(0,0,0,.04)` |
| tooltip | 6 | base + `0 1px 1px rgba(0,0,0,.02), 0 4px 8px rgba(0,0,0,.04)` |
| menu | 12 | base + `0 1px 1px .02, 0 4px 8px -4px .04, 0 16px 24px -8px .06` |
| modal | 12 | base + `0 1px 1px .02, 0 8px 16px -4px .04, 0 24px 32px -8px .06` |
| fullscreen | 16 | as modal |

- Dark (m): surface `#0A0A0A` on `#000`; ring `rgba(255,255,255,.145)` then `0 0 0 1px #000`; medium drops become
  `.32` / `.16`; menu and modal keep the light alphas. Page rules: "favor the lowest elevation that still reads",
  "don't stack two Materials on one element".
- Buttons: 32/36/40 high, r6, padding 0 6 / 0 10, 14/500, `transition: .15s (.4,0,.2,1)`, no shadow on fills.
  Amber (closest to ours): `#FF990A` fill, `#0A0A0A` text; hover `#D27504` (about 18% toward brown). Black
  `#171717`. Secondary: white + `0 0 0 1px #EBEBEB`, hover `#F2F2F2`. Focus (keyboard): `0 0 0 2px #fff, 0 0 0 4px #0072F5`.
- Home and product page are flat: header hairline `0 1px 0 rgba(0,0,0,.08)`; a recessed code well `inset 0 1px 2px
  rgba(0,0,0,.18), inset 0 0 24px rgba(0,0,0,.14)`; selected tab = `#EBEBEB` fill, r6, 32 high, 150 bg fade, no indicator.
- Toast stack: r12, menu material; front scale 1, next `scale(.95)` 19 px higher, third `scale(.9)` 37 px higher;
  `transition: .35s cubic-bezier(.25,.75,.6,.98)`.

### 1.3 raycast.com (dark)
Shots: `raycast-home-1440`, `raycast-cards-1440`.
- Primary (Download): 36, r8, `#E6E6E6`, text `#2F3031` 14/500, padding 8 12; `0 0 0 2px rgba(0,0,0,.5), 0 0 14px
  rgba(255,255,255,.19), inset 0 -1px .4px rgba(0,0,0,.2), inset 0 1px .4px #fff`. Hover: fill `#FFF` only.
  Transition bg .2, shadow .2 ease-in-out, transform .1 ease-in-out.
- Nav island: r16, `linear-gradient(137deg, rgba(17,18,20,.75) 5%, rgba(12,13,15,.9) 76%)`, 1px
  `rgba(255,255,255,.06)`, `inset 0 1px 1px rgba(255,255,255,.15)`, blur 5.
- Icon button: r8 36, `linear-gradient(rgba(255,255,255,.03), rgba(255,255,255,.1))`; `inset 0 1px 0 rgba(255,255,255,.05),
  0 0 0 1px rgba(255,255,255,.25), inset 0 -1px 0 rgba(0,0,0,.2)`.
- Card glow tinted with its own hue: r20, `radial-gradient(30% 40% at 52% 37%, #0D6E30, #083518)`; `inset 0 1px 0
  rgba(255,255,255,.1), 0 0 20px 3px rgba(46,212,105,.05), 0 0 40px 20px rgba(46,212,105,.05), inset 0 0 0 1px rgba(255,255,255,.06)`.
- Raised dark card: `inset 0 1px 0 rgba(255,255,255,.1), 0 30px 50px rgba(0,0,0,.4), 0 4px 24px rgba(3,15,129,.09)`.
  Keycap (159 uses): `0 1.5px .5px 2.5px rgba(0,0,0,.4), 0 0 .5px 1px #000, inset 0 2px 1px 1px rgba(0,0,0,.25), inset 0 1px 1px 1px rgba(255,255,255,.2)`.
- Motion: extension cards `opacity 0, translateY(50px) translate(10px) scale(.98)` to rest, 700 ease-out-cubic,
  stagger 80 from 100 (.10, .18, .26 ...); section fade-in-up 20 px 1 s; hero fade from `blur(10px)`.

### 1.4 stripe.com (home, /payments; light)
Shots: `stripe-home-1440`, `stripe-menu-open-1440`, `stripe-payments-1440`, `stripe-payments-390`.
- Elevation: a wide tinted layer plus a tight darker one with negative spread (offset ratio about 1.6:1):
  - s1 `rgba(50,50,93,.25) 0 6px 12px -2px, rgba(0,0,0,.3) 0 3px 7px -3px`
  - s2 `0 13px 27px -5px` / `0 8px 16px -8px`; s3 `0 30px 60px -12px` / `0 18px 36px -18px`; s4 `0 50px 100px -20px` / `0 30px 60px -30px`
  - menu `rgba(0,0,0,.1) 0 30px 60px -50px, rgba(50,50,93,.25) 0 30px 60px -10px`; home card `rgba(50,50,93,.12) 0 16px 32px`.
  - Identical at 390 (no reduction on the phone).
- Buttons: r4, 40/48, padding `11.5 20 12.5` (1 px more below: optical centre), 14-16/400. Hover `#533AFD > #4032C8`,
  300 `(.25,1,.5,1)`. /payments CTA: 33 high, `#9966FF`, hover switches to ink `#0A2540`, 150 ease-out-cubic.
- HoverArrow (m): svg 10x10, line `M0 5h7` opacity 0 > 1, tip `M1 1l4 4-4 4` translateX 0 > 3, 150 ease-out-cubic.
- Live ticker: "Global GDP running on Stripe: 1.73492253%", one span per digit, `tabular-nums` + `"tnum"`,
  `#64748D`; the last digits change in place with no layout shift.
- Menu open: opacity 240 `(.45,.05,.55,.95)`, page behind blurred. Chat card entrance 300 `(.25,1,.5,1)`.

### 1.5 arc.net
Shot: `arc-home-1440`. Noise: `url(noise-light.png)` repeated at native size on solid `#3139FB` bands only; body
`#FFFCEC`. CTA: r22, `rgba(0,0,0,.85)` + blur 3, `0 2px 8px rgba(0,0,0,.25)`; hover fill .65, arrow translateX 2,
200 ease-in-out. Download buttons `0 5px 5px rgba(0,0,0,.1)`.

### 1.6 Revisits: kitchen, smoothui, aceternity (depth and motion only)
Shots: `kitchen-tactile-grid-1440`, `smoothui-glow-hover-card-1440`, `aceternity-buttons-1440`,
`aceternity-primary-button-hover-zoom`, `aceternity-glowing-effect-hover-1440`.
- Kitchen tactile button: 38 wrapper; base r12 h32 at top 6, `#292926`, `inset 0 -1px 0 #141412`; face r12 h32
  `#4A4A46`, `inset 0 1px 0 #64645E`, 12/500. Hover face `translateY(2px)`, active `translateY(6px)` (meets base),
  150 `(.23,1,.32,1)` (= our `--ease`), `motion-reduce:transform-none`.
- Kitchen dark button (Regenerate, r8 28): `inset 0 1px 0 rgba(255,255,255,.18), inset 0 -1px 0 rgba(0,0,0,.2),
  0 1px 2px rgba(0,0,0,.14), 0 2px 4px -2px rgba(0,0,0,.18)`. File chip r8: `0 1px 3px rgba(0,0,0,.1), 0 1px 2px -1px rgba(0,0,0,.1)`.
- Aceternity "Get All-Access" (best coloured button measured): 40, r10, 14/500 white. `::before` inset 0, z -10,
  1px transparent border, backgrounds: sheen `linear-gradient(rgba(255,255,255,.12), transparent 50%)` padding-box,
  fill `linear-gradient(#3F80FF, #2867F2)` padding-box, edge `linear-gradient(#77A5FF, #4A7CEB, #1C54D6)` border-box.
  Shadows: `0 0 0 1px #1A4BC2, inset 0 -3px 6px -3px rgba(8,32,110,.18), 0 1px 1px rgba(16,54,160,.12), 0 2px 4px
  rgba(16,54,160,.16)`. Hover: fill lightens to `#4A88FF > #3570F3`; shadow and transform unchanged.
- Aceternity Next.js Blue: `0 4px 14px rgba(0,118,255,.39)`, hover `0 6px 20px rgba(0,118,255,.23)` (wider, softer),
  200 linear. Shimmer: `linear-gradient(110deg, #000103 45%, #1E2631 55%, #000103)` at `200% 100%`. Preview tab
  thumb: white r7.6, `0 1px 3px rgba(0,0,0,.1), 0 1px 2px -1px rgba(0,0,0,.1)`. Glowing effect: `::after` 1px
  border masked by `conic-gradient(from var(--start), transparent, #fff, transparent 80deg)`, opacity 0 > 1 300.
- smoothui (src): button-copy icon swap `blur(10px) opacity 0 y -25 > rest`, exit y 25, spring 250 bounce 0, spinner
  1000 then check 2000; animated-list enter `opacity 0 scale .95 y 14`, exit `scale .9`, spring 250 bounce .1,
  stagger 50 capped 300, `layout`; count-badge digit enters from y +12 when rising (-12 falling), spring 300 bounce
  .1, badge `scale 0 > 1` spring 250 bounce .2; stepper fill spring 250, check `scale .5 > 1` spring 300 bounce .2,
  active ring `opacity .5 scale 1 > 0 scale 1.6` 600 `(.23,1,.32,1)`; glow card mask `radial-gradient(400px at x y,
  #000 1%, transparent 50%)`, brand at 15%, 200 ease; magnetic strength .3 within 150; emboss shadow 240
  `(.645,.045,.355,1)`; content-skeleton is `animate-pulse` only (no shimmer). All gate on reduced motion.

## 2. What makes these feel premium (measured)
1. Elevation = 1px alpha ring + 1 to 4 soft layers. No measured elevated surface uses a solid grey border;
   all use `0 0 0 1px rgba(0,0,0,.08)` or a white alpha in dark. Ours `.card` uses solid `--line`.
2. Layers pair a tight contact shadow (0 1-2 px, .02-.14) with a wide ambient one whose negative spread hides it at
   the sides (Vercel `0 24 32 -8`, Stripe `0 30 60 -12`).
3. Coloured buttons get depth from inside: top sheen, an edge lighter at the top, a dark inset at the bottom, a ring
   one step darker than the fill, and a small drop (4 px blur max) tinted with the fill hue.
4. Six of six premium primaries keep `transform: none` on hover (Linear, Vercel amber, Raycast, Stripe, Arc,
   Aceternity). Hover = fill step, sometimes a shadow step. Only Kitchen's tactile study moves, and it moves down.
5. Hover deltas are visible: Vercel amber 18% darker; Linear and Raycast to pure white; Aceternity about 6% lighter.
6. Two speeds: controls 100-160 (Linear 100/160 quad, Vercel 150, Stripe 150); panels and stacks 240-350 (Stripe
   menu 240, Geist toasts 350, Linear regular 250). 700-1000 only on marketing hero entries.
7. Shadows are tinted: Stripe navy on a cool page, Raycast cards glow in their own hue, Aceternity navy under blue.
8. Texture is rare: Arc on big solid colour bands only; nobody textures cards or a light product body.
9. Numbers that change roll per digit with `tabular-nums` (Stripe ticker, smoothui count-badge), no layout shift.
10. Reduced motion turns every effect off at the source (Kitchen `motion-reduce:`, smoothui `useReducedMotion`).

## 3. Recipes
Every motion below sits behind `@media (prefers-reduced-motion: no-preference)` and is off under
`html[data-motion="reduce"]` (ui.css rule 10). Shared tokens (ours):
```css
:root { --ease: cubic-bezier(.23,1,.32,1);  /* exists = Kitchen tactile, smoothui ring */
  --ease-quad: cubic-bezier(.25,.46,.45,.94);  /* Linear hovers, 100-160 */
  --ease-io: cubic-bezier(.645,.045,.355,1);   /* Linear in-out, smoothui emboss */
  --sh: 60 52 44;                              /* warm graphite shadow tint; Stripe's 50 50 93 is too cold for paper */
  --ring-a: rgb(var(--sh) / .12); }
:root[data-theme="dark"] { --sh: 0 0 0; --ring-a: rgb(255 255 255 / .09); }
```
R1 Primary `.pill` (ours; Aceternity construction, Vercel amber deltas). Slop risk low.
```css
.pill { border: 1px solid transparent;
  background: linear-gradient(rgb(255 255 255 / .22), rgb(255 255 255 / 0) 50%) padding-box,
    linear-gradient(color-mix(in srgb, var(--amber), #fff 10%), color-mix(in srgb, var(--amber), #000 3%)) padding-box,
    linear-gradient(color-mix(in srgb, var(--amber), #fff 40%), color-mix(in srgb, var(--amber), #000 20%)) border-box;
  box-shadow: 0 0 0 1px color-mix(in srgb, var(--amber), #000 24%), inset 0 -3px 6px -3px rgb(120 55 0 / .3),
    0 1px 1px rgb(140 70 0 / .14), 0 2px 4px rgb(140 70 0 / .16);
  transition: background .12s var(--ease-quad), box-shadow .16s var(--ease-quad), transform .12s var(--ease); }
```
Hover: both fill stops +8% white (dark text gains contrast; Linear, Raycast, Aceternity lighten), add
`0 4px 10px -4px rgb(140 70 0 / .3)`. Check: today's hover is an 8% ink mix, Vercel's measured delta is about 18%;
confirm 8% is visible. Press: `scale(.97)` (exists) and the drop collapses to `0 1px 1px`, inset deepens to `inset 0
1px 3px rgb(120 55 0 / .35)`. Dark: ring `#000 40%` mix, drops `rgb(0 0 0 / .4)`, sheen .16. Height stays 42.
R1b Lite primary (one background): flat `--amber`; `inset 0 1px 0 rgb(255 255 255 / .35), inset 0 -1px 0 rgb(0 0 0
/ .12), 0 0 0 1px rgb(150 75 0 / .35), 0 1px 2px rgb(140 70 0 / .2)` (Raycast / Kitchen pattern).
R2 Secondary `.btn` (Kitchen trigger, Vercel secondary): keep `--well` fill, add `inset 0 1px 0 rgb(255 255 255 /
.6), 0 0 0 1px var(--ring-a), 0 1px 2px -1px rgb(var(--sh) / .12)`; hover fill 5% darker (Vercel `#FFF > #F2F2F2`).
Dark: `inset 0 1px 0 rgb(255 255 255 / .06)`, ring as token, drop `rgb(0 0 0 / .4)`. `.btn.ink` gets Kitchen's dark
stack verbatim (1.6 Regenerate). Reverses INSPO 6.4 (see section 5).
R3 Quiet `.quiet`: no fill, no shadow ever; colour 100 `--ease-quad` (Linear Log in). Depth stays off tertiary.
R4 Elevation scale (Vercel structure, warm tint, ours):
```css
--e0: 0 0 0 1px var(--ring-a);                                                   /* .card at rest */
--e1: var(--e0), 0 1px 2px rgb(var(--sh) / .06), 0 2px 4px -2px rgb(var(--sh) / .06);   /* clickable card, hover */
--e2: var(--e0), 0 1px 1px rgb(var(--sh) / .04), 0 8px 16px -4px rgb(var(--sh) / .08);  /* focal card (#next) */
--e3: var(--e0), 0 1px 1px rgb(var(--sh) / .03), 0 4px 8px -4px rgb(var(--sh) / .06), 0 16px 24px -8px rgb(var(--sh) / .10);  /* menu, popover, toast */
--e4: var(--e0), 0 1px 1px rgb(var(--sh) / .03), 0 8px 16px -4px rgb(var(--sh) / .06), 0 24px 32px -8px rgb(var(--sh) / .12);  /* sheet, palette */
```
Dark: same lines with `--sh: 0 0 0` and alphas x4 to x8 (.24/.32/.4; Vercel medium went .04 to .32 and .16), plus `inset 0
1px 0 rgb(255 255 255 / .04)`. `--e3` replaces `--shadow-float`, `--e4` replaces `--shadow-pop`. One material per element.
R5 Inner highlight: `inset 0 1px 0 rgb(255 255 255 / .7)` on tinted light surfaces (`--tile`, `--well`; invisible on
white); dark `inset 0 1px 0 rgb(255 255 255 / .05)` (Linear .04-.05, Raycast nav .15 is the ceiling).
R6 Tinted shadow rule: neutrals tint `rgb(60 52 44)`; anything under the amber tints `rgb(140 70 0)`; never blue or
navy. Keep Stripe's pair: wide layer `y, 2y blur, -y/5 spread` plus tight layer `0.6y, 1.2y blur, -0.6y spread`.
R7 Surface sheen (Linear tile, Raycast icon button): `.card.raised { background-image: linear-gradient(rgb(255 255
255 / .5), rgb(255 255 255 / 0) 48px); }`; dark `.04`. Focal card only.
R8 Texture (Arc): only on one large solid band if one exists (none today). Slop risk medium.
`::before { position:absolute; inset:0; pointer-events:none; opacity:.05; mix-blend-mode:multiply; background:
url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='160' height='160'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='.9' numOctaves='2' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E"); }` dark: `screen`, .04.
R9 Hover on cards and rows: `--e0 > --e1` plus fill step, 160 `--ease-quad`; no transform. If a lift is wanted:
`translateY(-1px)` max, clickable cards only, with the shadow step. Slop risk high above 1 px.
R10 Press: `scale(.97)` 120 `--ease` (exists). Tactile variant (Kitchen) for at most one button: face 38 + 4 px base
= 42; hover face down 1, active down 4, 150 `--ease`. Slop risk medium.
R11 Focus: keep `--ring` (Vercel measured the same 2+2 shape); on raised buttons `box-shadow: var(--ring), <stack>`;
`:focus-visible` only; 100 `--ease-quad`.
R12 Segmented thumb: track `--well` p2 r10; thumb `--paper` r8, `0 0 0 .5px var(--ring-a), 0 1px 3px rgb(var(--sh) /
.1), 0 1px 2px -1px rgb(var(--sh) / .1)` (Aceternity Preview tab); slides `transform, width` 200 `--ease`. Dark thumb `--mat` + R5.
R13 Tab indicator: one 2px bar under `.tablist`, `transform: translateX(var(--x)); width: var(--w)`, 200 `--ease`;
set from the selected tab's offsetLeft/offsetWidth. Vercel has none; smoothui slides it (INSPO 1.2).
R14 Number ticker (Stripe, smoothui count-badge): one span per digit, `font-variant-numeric: tabular-nums`, digit
column `overflow:hidden; height:1lh`; new digit from `translateY(.6em)` when the value rises (`-.6em` falling), old
exits opposite, 300 `--ease`; only on change, never on load; wrapper has the final value in aria, digits aria-hidden.
R15 Page entry stagger (app scale, not Raycast's 700/50 px):
`@keyframes enter { from { opacity:0; transform: translateY(6px) } }`
`.enter > * { animation: enter .24s var(--ease) both; animation-delay: calc(min(var(--i,0), 6) * 40ms) }` (cap 240 ms;
smoothui caps at 300). First paint of a page only, not on cached back navigation.
R16 List item enter / exit: `@starting-style { .row { opacity:0; transform: translateY(6px) scale(.98) } }`, transition
200 `--ease`; exit `opacity 0, scale(.98)` 150, then the wrapper collapses `grid-template-rows: 1fr > 0fr` 200.
smoothui measured y 14, scale .95/.9: ours halves the travel inside dense lists.
R17 Sheet / dialog: `dialog[open] { animation: sheet-in .22s var(--ease) }`, `from { opacity:0; transform:
translateY(8px) scale(.96) }` (Linear dialogOpen shape; its duration was not measured); `::backdrop` fade 200; close
150. Phone bottom sheet from `translateY(100%)` 300 `cubic-bezier(.32,.72,0,1)` (Vaul curve, not measured here).
R18 Toast: material `--e3`, r12; enter from `translateY(100%) opacity 0`; stack (Geist) 2nd `translateY(-8px)
scale(.95)`, 3rd `translateY(-16px) scale(.9)`, 4th+ opacity 0; `transition: transform .35s cubic-bezier(.25,.75,.6,.98)`.
R19 Success: label or icon swap (smoothui button-copy) at our scale: out `opacity 0, translateY(-8px), blur(4px)`,
in from `translateY(8px)`, 220 `--ease`; check `scale(.5) > 1` 300 `--ease` (smoothui stepper); hold 2000 then
revert. Done pulse (Linear statusPulse): ring `opacity .7 scale(.4) > 0 scale(1)`, 600 ease-out-cubic, once.
R20 Skeleton shimmer: conflicts with ui.css rules 8 and 10 (no shimmer, nothing loops); lead's call. If allowed:
`linear-gradient(110deg, var(--tile) 40%, var(--paper) 50%, var(--tile) 60%) 0 0 / 200% 100%`, background-position
`200% > -200%` 1.6 s linear, stopped once content lands. smoothui itself uses pulse only. Marquees: same conflict.
R21 Progress fill: track `--track` + `inset 0 1px 1px rgb(var(--sh) / .08)` (Vercel well, softened); fill
`linear-gradient(color-mix(in srgb, var(--amber), #fff 12%), var(--amber))` + `inset 0 1px 0 rgb(255 255 255 / .3)`;
`transform: scaleX(var(--v)); transform-origin: left`, 400 `--ease` on change (smoothui stepper fill 250); R19 pulse at 100%.
R22 Recessed field: `.field` and range track `inset 0 1px 2px rgb(var(--sh) / .10)` on `--well`; dark `inset 0 1px 2px
rgb(0 0 0 / .4)`. Pairs with raised buttons so the page has an up and a down.
R23 Hover arrow (Stripe, verbatim): `<svg width="10" height="10" viewBox="0 0 10 10"><path class="l" d="M0 5h7"/><path
class="t" d="M1 1l4 4-4 4"/></svg>`, stroke 1.5; `.l` opacity 0 > 1, `.t` translateX 0 > 3, 150 ease-out-cubic. Slop risk low.
R24 Spotlight border on one focal card (smoothui glow, Linear edge). Slop risk high on grids, medium on one card,
never on question screens: `::after { inset:-1px; border:1px solid color-mix(in srgb, var(--amber), transparent 40%);
border-radius:inherit; pointer-events:none; opacity:0; mask: radial-gradient(180px circle at var(--x) var(--y), #000,
transparent 70%); transition: opacity .2s var(--ease-quad) }`; pointermove sets `--x --y` (rAF), fine pointers only.

## 4. What to avoid (slop or gimmick, with the number behind it)
- Hover lift or hover scale-up: 0 of 6 measured primaries move on hover. Lifts of 4-8 px read as template.
- Glow halos around a light-theme button: Aceternity's `0 4px 14px rgb(0 118 255 / .39)` is the AI-template look;
  Raycast's `0 0 14px` white glow only works on near-black. Ours: drop shadows at rest under 4 px blur, alpha .2 max.
- Fully round pills and 20-28 px card radii (Linear, Vercel, Raycast, Arc use them; check-ui.py bans them for us).
- Looping decoration: moving or conic borders, shimmer on buttons, marquees, random-delay dot grids (Linear
  /features), orbs. Rule 10; Linear's own /changelog runs zero animations.
- Long blur reveals: 700-1000 ms with blur 10 is marketing-hero only (Raycast, Linear /features). Product chrome
  measured 100-350.
- Blue, purple or navy tints on warm paper; rainbow gradient borders (Aceternity glowing effect colours).
- Stacked materials (Vercel rule), card-in-card stages, brutal offset shadows (Aceternity BRUTAL 5 x 1 px), emboss
  or neumorphism across many surfaces, magnetic buttons (target moves under the pointer), 3D tilt cards.
- Backdrop blur on scrolling content; noise on cards or the body.
- The `high-end-visual-design` skill used as a lens prescribes 700 ms+ blur reveals, `rounded-full` pills,
  double-bezel on every card and button-in-button icons. The measurements contradict all four for product chrome
  (100-250 ms, r6-12, one alpha ring, a plain arrow with Stripe's 3 px tip move). Use it for taste, not values.

## 5. Reversals from INSPO-VISUAL (decide once)
1. 1.1 REJECT "four-layer button shadows, tactile pieces": R1, R2 bring layered button shadows back; tactile (R10)
   as one opt-in variant at most.
2. 6.4 "no shadow on `.btn`, shadows only on floats": R2 adds a ring, highlight and contact shadow to `.btn`.
3. ui.css rule 3 "borders: 1px `--line`": R4 switches elevated surfaces to an alpha ring so one token works on
   `--paper`, `--tile` and dark.
4. 3 row 5 `--shadow-float` and `--shadow-pop`: replaced by `--e3` and `--e4`.
5. 2.14 "nothing on load": R15 adds a capped 240 ms entry stagger (rule 10 allows entry motion). Bencho's 2 s
   fade-in stays rejected.
6. Still rejected: 2 px bottom "edge" on cards (R4 uses shadows), shimmer and loops (R20 open for the lead).
