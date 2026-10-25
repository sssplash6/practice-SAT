/* ------------------------------------------------------------ icons (premium build A3, 2026-10-19)
   Drop-in for ui.js's `const ICON = {...}` block (ui.js:438-476). Same call shape: every entry is still
   an inner string for a 24 viewBox, so svg(ICON.x, 18), UI.svg(UI.ICON.x, n) and kit's icon('x') work as
   they are. Every name ui.js, kit.js, runner.js, question.js, words-ui.js, compete-ui.js and contest.js
   draw today is here, plus the missing ones (more, compete, grip, phone, link, calendar_check, caret_*).

   Source: Phosphor Icons, github.com/phosphor-icons/core, raw/regular and raw/fill at commit
   2b75f3ad12b420c9504ef05df8d2564a28f8500e (package 2.1.1). MIT licence, Copyright (c) 2023 Phosphor
   Icons: web/assets/LICENSE-phosphor.txt. Ours, on the same weight rule: dot, eliminate, strikes (24 grid),
   twin_test (Phosphor copy plus a small timer, 256 grid).

   Markup: Phosphor entries sit in <g class="ph" transform="scale(.09375)"> (256 to 24). The one
   stroke-width="16" on that g is only a no-CSS fallback; icons.css sets the real width (1.4px, held in
   screen pixels). No element carries its own stroke-width, so the old duplicate attributes are gone (bug 1).
   Twins (nine nav items, note, bell, moon; flag, bookmark, star in amber): the entry holds two layers,
   <g class="ph ph-f" opacity="0">fill</g><g class="ph ph-o">outline</g>; icons.css shows the fill under
   aria-current, aria-pressed="true", aria-checked="true" or a selected tab. ICON_FILL holds the fills alone.
   flame keeps one layer with class="flame" on its outline (ui.css:413 fills it, ui.js:1545 looks it up).

   Names that do not exist in UI.ICON today: more (index.html:1246 falls back to a local copy).
   Names whose meaning changes, so the caller must switch: question.js `chev` (down) -> caret_down;
   words-ui.js `left`/`right` (carets) -> caret_left/caret_right (here left/right are arrows, as in
   runner.js); ui.js:1426 NAV compete `trophy` -> compete; ui.js:2100 "Save your progress" `dot` -> save. */

const PHF = {
  today:    '<path d="M208,32H184V24a8,8,0,0,0-16,0v8H88V24a8,8,0,0,0-16,0v8H48A16,16,0,0,0,32,48V208a16,16,0,0,0,16,16H208a16,16,0,0,0,16-16V48A16,16,0,0,0,208,32ZM128,168a16,16,0,1,1,16-16A16,16,0,0,1,128,168Zm80-88H48V48H72v8a8,8,0,0,0,16,0V48h80v8a8,8,0,0,0,16,0V48h24Z"/>',
  practice: '<path d="M120,56v48a16,16,0,0,1-16,16H56a16,16,0,0,1-16-16V56A16,16,0,0,1,56,40h48A16,16,0,0,1,120,56Zm80-16H152a16,16,0,0,0-16,16v48a16,16,0,0,0,16,16h48a16,16,0,0,0,16-16V56A16,16,0,0,0,200,40Zm-96,96H56a16,16,0,0,0-16,16v48a16,16,0,0,0,16,16h48a16,16,0,0,0,16-16V152A16,16,0,0,0,104,136Zm96,0H152a16,16,0,0,0-16,16v48a16,16,0,0,0,16,16h48a16,16,0,0,0,16-16V152A16,16,0,0,0,200,136Z"/>',
  review:   '<path d="M224,128A96,96,0,0,1,62.11,197.82a8,8,0,1,1,11-11.64A80,80,0,1,0,71.43,71.43C67.9,75,64.58,78.51,61.35,82L77.66,98.34A8,8,0,0,1,72,112H32a8,8,0,0,1-8-8V64a8,8,0,0,1,13.66-5.66L50,70.7c3.22-3.49,6.54-7,10.06-10.55A96,96,0,0,1,224,128ZM128,72a8,8,0,0,0-8,8v48a8,8,0,0,0,3.88,6.86l40,24a8,8,0,1,0,8.24-13.72L136,123.47V80A8,8,0,0,0,128,72Z"/>',
  words:    '<rect x="24" y="72" width="176" height="144" rx="16"/><path d="M216,40H64a8,8,0,0,0,0,16H216V176a8,8,0,0,0,16,0V56A16,16,0,0,0,216,40Z"/>',
  tests:    '<path d="M200,32H163.74a47.92,47.92,0,0,0-71.48,0H56A16,16,0,0,0,40,48V216a16,16,0,0,0,16,16H200a16,16,0,0,0,16-16V48A16,16,0,0,0,200,32Zm-72,0a32,32,0,0,1,32,32H96A32,32,0,0,1,128,32Zm32,128H96a8,8,0,0,1,0-16h64a8,8,0,0,1,0,16Zm0-32H96a8,8,0,0,1,0-16h64a8,8,0,0,1,0,16Z"/>',
  plan:     '<path d="M228,200a28,28,0,0,1-54.83,8H72a48,48,0,0,1,0-96h96a24,24,0,0,0,0-48H72a8,8,0,0,1,0-16h96a40,40,0,0,1,0,80H72a32,32,0,0,0,0,64H173.17A28,28,0,0,1,228,200Z"/>',
  results:  '<path d="M216,40H40A16,16,0,0,0,24,56V200a16,16,0,0,0,16,16H216a16,16,0,0,0,16-16V56A16,16,0,0,0,216,40ZM200,192H56a8,8,0,0,1-8-8V72a8,8,0,0,1,16,0v76.69l34.34-34.35a8,8,0,0,1,11.32,0L128,132.69,172.69,88H144a8,8,0,0,1,0-16h48a8,8,0,0,1,8,8v48a8,8,0,0,1-16,0V99.31l-50.34,50.35a8,8,0,0,1-11.32,0L104,131.31l-40,40V176H200a8,8,0,0,1,0,16Z"/>',
  compete:  '<path d="M240,200h-8V144a16,16,0,0,0-16-16H176V56a16,16,0,0,0-16-16H96A16,16,0,0,0,80,56V88H40a16,16,0,0,0-16,16v96H16a8,8,0,0,0,0,16H240a8,8,0,0,0,0-16ZM80,200H40V104H80Zm60-64a8,8,0,0,1-16,0V107.1l-1.47.49a8,8,0,0,1-5.06-15.18l12-4A8,8,0,0,1,140,96Zm76,64H176V144h40Z"/>',
  profile:  '<path d="M172,120a44,44,0,1,1-44-44A44.05,44.05,0,0,1,172,120Zm60,8A104,104,0,1,1,128,24,104.11,104.11,0,0,1,232,128Zm-16,0a88.09,88.09,0,0,0-91.47-87.93C77.43,41.89,39.87,81.12,40,128.25a87.65,87.65,0,0,0,22.24,58.16A79.71,79.71,0,0,1,84,165.1a4,4,0,0,1,4.83.32,59.83,59.83,0,0,0,78.28,0,4,4,0,0,1,4.83-.32,79.71,79.71,0,0,1,21.79,21.31A87.62,87.62,0,0,0,216,128Z"/>',
  note:     '<path d="M224,128v80a16,16,0,0,1-16,16H48a16,16,0,0,1-16-16V48A16,16,0,0,1,48,32h80a8,8,0,0,1,0,16H48V208H208V128a8,8,0,0,1,16,0Zm5.66-58.34-96,96A8,8,0,0,1,128,168H96a8,8,0,0,1-8-8V128a8,8,0,0,1,2.34-5.66l96-96a8,8,0,0,1,11.32,0l32,32A8,8,0,0,1,229.66,69.66Zm-17-5.66L192,43.31,179.31,56,200,76.69Z"/>',
  bell:     '<path d="M168,224a8,8,0,0,1-8,8H96a8,8,0,1,1,0-16h64A8,8,0,0,1,168,224Zm53.81-48.06C216.25,166.38,208,139.33,208,104a80,80,0,1,0-160,0c0,35.34-8.26,62.38-13.81,71.94A16,16,0,0,0,48,200H208a16,16,0,0,0,13.8-24.06Z"/>',
  moon:     '<path d="M235.54,150.21a104.84,104.84,0,0,1-37,52.91A104,104,0,0,1,32,120,103.09,103.09,0,0,1,52.88,57.48a104.84,104.84,0,0,1,52.91-37,8,8,0,0,1,10,10,88.08,88.08,0,0,0,109.8,109.8,8,8,0,0,1,10,10Z"/>',
  flag:     '<path d="M232,56V176a8,8,0,0,1-2.76,6c-15.28,13.23-29.89,18-43.82,18-18.91,0-36.57-8.74-53-16.85C105.87,170,82.79,158.61,56,179.77V224a8,8,0,0,1-16,0V56a8,8,0,0,1,2.77-6h0c36-31.18,68.31-15.21,96.79-1.12C167,62.46,190.79,74.2,218.76,50A8,8,0,0,1,232,56Z"/>',
  bookmark: '<path d="M184,32H72A16,16,0,0,0,56,48V224a8,8,0,0,0,12.24,6.78L128,193.43l59.77,37.35A8,8,0,0,0,200,224V48A16,16,0,0,0,184,32Z"/>',
  star:     '<path d="M234.29,114.85l-45,38.83L203,211.75a16.4,16.4,0,0,1-24.5,17.82L128,198.49,77.47,229.57A16.4,16.4,0,0,1,53,211.75l13.76-58.07-45-38.83A16.46,16.46,0,0,1,31.08,86l59-4.76,22.76-55.08a16.36,16.36,0,0,1,30.27,0l22.75,55.08,59,4.76a16.46,16.46,0,0,1,9.37,28.86Z"/>',
  flame:    '<path d="M143.38,17.85a8,8,0,0,0-12.63,3.41l-22,60.41L84.59,58.26a8,8,0,0,0-11.93.89C51,87.53,40,116.08,40,144a88,88,0,0,0,176,0C216,84.55,165.21,36,143.38,17.85Zm40.51,135.49a57.6,57.6,0,0,1-46.56,46.55A7.65,7.65,0,0,1,136,200a8,8,0,0,1-1.32-15.89c16.57-2.79,30.63-16.85,33.44-33.45a8,8,0,0,1,15.78,2.68Z"/>',
  play:     '<path d="M240,128a15.74,15.74,0,0,1-7.6,13.51L88.32,229.65a16,16,0,0,1-16.2.3A15.86,15.86,0,0,1,64,216.13V39.87a15.86,15.86,0,0,1,8.12-13.82,16,16,0,0,1,16.2.3L232.4,114.49A15.74,15.74,0,0,1,240,128Z"/>',
};
const PH = 'transform="scale(.09375)"';     // Phosphor's 256 grid inside our 24 viewBox
const ph = (s, c = '') => `<g class="ph${c}" fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="16" ${PH}>${s}</g>`;
const phf = (s, c = '') => `<g class="ph${c}" fill="currentColor" ${PH}>${s}</g>`;
// a twin: the fill (hidden until active, icons.css) under the outline; amber for the status toggles
const twin = (n, s, amber) => `<g class="ph ph-f${amber ? ' ph-amber' : ''}" fill="currentColor" opacity="0" ${PH}>${PHF[n]}</g>` + ph(s, ' ph-o');
const ICON = {
  today:          twin('today', '<rect x="40" y="40" width="176" height="176" rx="8"/><line x1="176" y1="24" x2="176" y2="56"/><line x1="80" y1="24" x2="80" y2="56"/><line x1="40" y1="88" x2="216" y2="88"/><circle cx="128" cy="152" r="16" fill="currentColor" stroke="none"/>'),
  practice:       twin('practice', '<rect x="48" y="48" width="64" height="64" rx="8"/><rect x="144" y="48" width="64" height="64" rx="8"/><rect x="48" y="144" width="64" height="64" rx="8"/><rect x="144" y="144" width="64" height="64" rx="8"/>'),
  review:         twin('review', '<polyline points="128 80 128 128 168 152"/><polyline points="72 104 32 104 32 64"/><path d="M67.6,192A88,88,0,1,0,65.77,65.77C54,77.69,44.28,88.93,32,104"/>'),
  words:          twin('words', '<rect x="32" y="80" width="160" height="128" rx="8"/><path d="M64,48H216a8,8,0,0,1,8,8V176"/>'),
  tests:          twin('tests', '<line x1="96" y1="152" x2="160" y2="152"/><line x1="96" y1="120" x2="160" y2="120"/><path d="M160,40h40a8,8,0,0,1,8,8V216a8,8,0,0,1-8,8H56a8,8,0,0,1-8-8V48a8,8,0,0,1,8-8H96"/><path d="M88,72V64a40,40,0,0,1,80,0v8Z"/>'),
  plan:           twin('plan', '<circle cx="200" cy="200" r="24"/><path d="M72,56h96a32,32,0,0,1,0,64H72a40,40,0,0,0,0,80H176"/>'),
  results:        twin('results', '<polyline points="224 208 32 208 32 48"/><polyline points="200 72 128 144 96 112 32 176"/><polyline points="200 112 200 72 160 72"/>'),
  compete:        twin('compete', '<path d="M32,208V104a8,8,0,0,1,8-8H88"/><path d="M88,208V56a8,8,0,0,1,8-8h64a8,8,0,0,1,8,8V208"/><path d="M224,208V144a8,8,0,0,0-8-8H168"/><polyline points="120 100 132 96 132 136"/><line x1="16" y1="208" x2="240" y2="208"/>'),
  profile:        twin('profile', '<circle cx="128" cy="128" r="96"/><circle cx="128" cy="120" r="40"/><path d="M63.8,199.37a72,72,0,0,1,128.4,0"/>'),
  note:           twin('note', '<polygon points="128 160 96 160 96 128 192 32 224 64 128 160"/><line x1="168" y1="56" x2="200" y2="88"/><path d="M216,128v80a8,8,0,0,1-8,8H48a8,8,0,0,1-8-8V48a8,8,0,0,1,8-8h80"/>'),
  bell:           twin('bell', '<line x1="96" y1="224" x2="160" y2="224"/><path d="M56,104a72,72,0,0,1,144,0c0,35.82,8.3,64.6,14.9,76A8,8,0,0,1,208,192H48a8,8,0,0,1-6.88-12C47.71,168.6,56,139.81,56,104Z"/>'),
  moon:           twin('moon', '<path d="M108.11,28.11A96.09,96.09,0,0,0,227.89,147.89,96,96,0,1,1,108.11,28.11Z"/>'),
  flag:           twin('flag', '<line x1="48" y1="224" x2="48" y2="56"/><path d="M48,176c64-55.43,112,55.43,176,0V56C160,111.43,112,.57,48,56"/>', 1),
  bookmark:       twin('bookmark', '<path d="M192,224l-64-40L64,224V48a8,8,0,0,1,8-8H184a8,8,0,0,1,8,8Z"/>', 1),
  star:           twin('star', '<path d="M128,189.09l54.72,33.65a8.4,8.4,0,0,0,12.52-9.17l-14.88-62.79,48.7-42A8.46,8.46,0,0,0,224.27,94L160.36,88.8,135.74,29.2a8.36,8.36,0,0,0-15.48,0L95.64,88.8,31.73,94a8.46,8.46,0,0,0-4.79,14.83l48.7,42L60.76,213.57a8.4,8.4,0,0,0,12.52,9.17Z"/>', 1),
  flame:          ph('<path class="flame" d="M112,96l26.27-72C159.86,41.92,208,88.15,208,144a80,80,0,0,1-160,0c0-30.57,14.42-58.26,31-80Z"/><path d="M136,192c20-3.37,36.61-20,40-40"/>'),
  play:           phf(PHF.play),
  x:              ph('<line x1="200" y1="56" x2="56" y2="200"/><line x1="200" y1="200" x2="56" y2="56"/>'),
  check:          ph('<polyline points="40 144 96 200 224 72"/>'),
  plus:           ph('<line x1="40" y1="128" x2="216" y2="128"/><line x1="128" y1="40" x2="128" y2="216"/>'),
  arrow:          ph('<line x1="40" y1="128" x2="216" y2="128"/><polyline points="144 56 216 128 144 200"/>'),
  right:          ph('<line x1="40" y1="128" x2="216" y2="128"/><polyline points="144 56 216 128 144 200"/>'),
  left:           ph('<line x1="216" y1="128" x2="40" y2="128"/><polyline points="112 56 40 128 112 200"/>'),
  chev:           ph('<polyline points="96 48 176 128 96 208"/>'),
  caret_right:    ph('<polyline points="96 48 176 128 96 208"/>'),
  caret_left:     ph('<polyline points="160 208 80 128 160 48"/>'),
  caret_down:     ph('<polyline points="208 96 128 176 48 96"/>', ' ph-turn'),
  caret_up:       ph('<polyline points="48 160 128 80 208 160"/>'),
  up:             ph('<polyline points="48 160 128 80 208 160"/>'),
  down:           ph('<polyline points="208 96 128 176 48 96"/>'),
  skip:           ph('<polyline points="56 48 136 128 56 208"/><polyline points="136 48 216 128 136 208"/>'),
  more:           ph('<circle cx="128" cy="128" r="12" fill="currentColor" stroke="none"/><circle cx="196" cy="128" r="12" fill="currentColor" stroke="none"/><circle cx="60" cy="128" r="12" fill="currentColor" stroke="none"/>'),
  dots:           ph('<circle cx="128" cy="128" r="12" fill="currentColor" stroke="none"/><circle cx="196" cy="128" r="12" fill="currentColor" stroke="none"/><circle cx="60" cy="128" r="12" fill="currentColor" stroke="none"/>'),
  grip:           ph('<circle cx="92" cy="60" r="12" fill="currentColor" stroke="none"/><circle cx="164" cy="60" r="12" fill="currentColor" stroke="none"/><circle cx="92" cy="128" r="12" fill="currentColor" stroke="none"/><circle cx="164" cy="128" r="12" fill="currentColor" stroke="none"/><circle cx="92" cy="196" r="12" fill="currentColor" stroke="none"/><circle cx="164" cy="196" r="12" fill="currentColor" stroke="none"/>'),
  search:         ph('<circle cx="112" cy="112" r="80"/><line x1="168.57" y1="168.57" x2="224" y2="224"/>'),
  bolt:           ph('<polygon points="160 16 144 96 208 120 96 240 112 160 48 136 160 16"/>'),
  help:           ph('<circle cx="128" cy="180" r="12" fill="currentColor" stroke="none"/><path d="M128,144v-8c17.67,0,32-12.54,32-28s-14.33-28-32-28S96,92.54,96,108v4"/><circle cx="128" cy="128" r="96"/>'),
  chat:           ph('<line x1="96" y1="112" x2="160" y2="112"/><line x1="96" y1="144" x2="160" y2="144"/><path d="M79.93,211.11a96,96,0,1,0-35-35h0L32.42,213.46a8,8,0,0,0,10.12,10.12l37.39-12.47Z"/>'),
  panel:          ph('<line x1="88" y1="48" x2="88" y2="208"/><rect x="32" y="48" width="192" height="160" rx="8"/>'),
  dock:           ph('<line x1="88" y1="48" x2="88" y2="208"/><rect x="32" y="48" width="192" height="160" rx="8"/>'),
  float:          ph('<rect x="32" y="56" width="192" height="144" rx="8"/><polyline points="136 200 136 128 224 128"/>'),
  settings:       ph('<circle cx="104" cy="80" r="24"/><circle cx="168" cy="176" r="24"/><line x1="128" y1="80" x2="216" y2="80"/><line x1="40" y1="80" x2="80" y2="80"/><line x1="192" y1="176" x2="216" y2="176"/><line x1="40" y1="176" x2="144" y2="176"/>'),
  signin:         ph('<line x1="24" y1="128" x2="136" y2="128"/><polyline points="96 88 136 128 96 168"/><polyline points="136 40 200 40 200 216 136 216"/>'),
  signout:        ph('<polyline points="112 40 48 40 48 216 112 216"/><line x1="112" y1="128" x2="224" y2="128"/><polyline points="184 88 224 128 184 168"/>'),
  devices:        ph('<rect x="136" y="104" width="128" height="80" rx="16" transform="translate(344 -56) rotate(90)"/><line x1="128" y1="208" x2="88" y2="208"/><path d="M160,176H40a16,16,0,0,1-16-16V64A16,16,0,0,1,40,48H184a16,16,0,0,1,16,16V80"/><line x1="192" y1="112" x2="208" y2="112"/>'),
  phone:          ph('<rect x="64" y="24" width="128" height="208" rx="16"/><line x1="64" y1="56" x2="192" y2="56"/><line x1="64" y1="200" x2="192" y2="200"/>'),
  text:           ph('<polyline points="144 192 80 56 16 192"/><ellipse cx="200" cy="164" rx="32" ry="28"/><path d="M232,192V132c0-15.46-14.33-28-32-28-9.56,0-18.14,2.18-24,8"/><line x1="125.18" y1="152" x2="34.82" y2="152"/>'),
  keyboard:       ph('<rect x="24" y="56" width="208" height="144" rx="8"/><line x1="56" y1="128" x2="200" y2="128"/><line x1="56" y1="96" x2="200" y2="96"/><line x1="56" y1="160" x2="64" y2="160"/><line x1="96" y1="160" x2="160" y2="160"/><line x1="192" y1="160" x2="200" y2="160"/>'),
  save:           ph('<path d="M112,208H72A56,56,0,1,1,85.92,97.74"/><polyline points="120 160 152 128 184 160"/><line x1="152" y1="208" x2="152" y2="128"/><path d="M80,128a80,80,0,1,1,112,73.34"/>'),
  users:          ph('<circle cx="84" cy="108" r="52"/><path d="M10.23,200a88,88,0,0,1,147.54,0"/><path d="M172,160a87.93,87.93,0,0,1,73.77,40"/><path d="M152.69,59.7A52,52,0,1,1,172,160"/>'),
  pause:          ph('<rect x="152" y="40" width="56" height="176" rx="8"/><rect x="48" y="40" width="56" height="176" rx="8"/>'),
  stop:           ph('<rect x="48" y="48" width="160" height="160" rx="8"/>'),
  clock:          ph('<circle cx="128" cy="136" r="88"/><line x1="128" y1="136" x2="168" y2="96"/><line x1="104" y1="16" x2="152" y2="16"/>'),
  calendar:       ph('<rect x="40" y="40" width="176" height="176" rx="8"/><line x1="176" y1="24" x2="176" y2="56"/><line x1="80" y1="24" x2="80" y2="56"/><line x1="40" y1="88" x2="216" y2="88"/>'),
  calendar_check: ph('<rect x="40" y="40" width="176" height="176" rx="8"/><line x1="176" y1="24" x2="176" y2="56"/><line x1="80" y1="24" x2="80" y2="56"/><line x1="40" y1="88" x2="216" y2="88"/><polyline points="92 152 116 176 164 128"/>'),
  calc:           ph('<rect x="80" y="64" width="96" height="48"/><rect x="32" y="48" width="192" height="160" rx="8" transform="translate(256) rotate(90)"/><circle cx="88" cy="148" r="12" fill="currentColor" stroke="none"/><circle cx="128" cy="148" r="12" fill="currentColor" stroke="none"/><circle cx="168" cy="148" r="12" fill="currentColor" stroke="none"/><circle cx="88" cy="188" r="12" fill="currentColor" stroke="none"/><circle cx="128" cy="188" r="12" fill="currentColor" stroke="none"/><circle cx="168" cy="188" r="12" fill="currentColor" stroke="none"/>'),
  graph:          ph('<line x1="72" y1="128" x2="184" y2="128"/><path d="M56,216H85.29a32,32,0,0,0,31.49-26.28L139.22,66.28A32,32,0,0,1,170.71,40H200"/>'),
  ref:            ph('<line x1="40" y1="72" x2="104" y2="72"/><line x1="72" y1="152" x2="72" y2="216"/><line x1="40" y1="184" x2="104" y2="184"/><line x1="152" y1="168" x2="216" y2="168"/><line x1="152" y1="200" x2="216" y2="200"/><line x1="160" y1="48" x2="208" y2="96"/><line x1="208" y1="48" x2="160" y2="96"/>'),
  learn:          ph('<path d="M128,88a32,32,0,0,1,32-32h72V200H160a32,32,0,0,0-32,32"/><path d="M24,200H96a32,32,0,0,1,32,32V88A32,32,0,0,0,96,56H24Z"/><line x1="160" y1="96" x2="200" y2="96"/><line x1="160" y1="128" x2="200" y2="128"/><line x1="160" y1="160" x2="200" y2="160"/>'),
  book:           ph('<path d="M128,88a32,32,0,0,1,32-32h72V200H160a32,32,0,0,0-32,32"/><path d="M24,200H96a32,32,0,0,1,32,32V88A32,32,0,0,0,96,56H24Z"/><line x1="160" y1="96" x2="200" y2="96"/><line x1="160" y1="128" x2="200" y2="128"/><line x1="160" y1="160" x2="200" y2="160"/>'),
  hint:           ph('<line x1="88" y1="232" x2="168" y2="232"/><path d="M78.7,167A79.87,79.87,0,0,1,48,104.45C47.76,61.09,82.72,25,126.07,24a80,80,0,0,1,51.34,142.9A24.3,24.3,0,0,0,168,186v6a8,8,0,0,1-8,8H96a8,8,0,0,1-8-8v-6A24.11,24.11,0,0,0,78.7,167Z"/><path d="M136,56c20,3.37,36.61,20,40,40"/>'),
  speak:          ph('<path d="M80,168H32a8,8,0,0,1-8-8V96a8,8,0,0,1,8-8H80l72-56V224Z"/><line x1="80" y1="88" x2="80" y2="168"/><path d="M192,106.85a32,32,0,0,1,0,42.3"/><path d="M221.67,80a72,72,0,0,1,0,96"/>'),
  report:         ph('<circle cx="128" cy="128" r="96" stroke-miterlimit="10"/><line x1="128" y1="136" x2="128" y2="80"/><circle cx="128" cy="172" r="12" fill="currentColor" stroke="none"/>'),
  history:        ph('<polyline points="128 80 128 128 168 152"/><polyline points="72 104 32 104 32 64"/><path d="M67.6,192A88,88,0,1,0,65.77,65.77C54,77.69,44.28,88.93,32,104"/>'),
  eye:            ph('<path d="M128,56C48,56,16,128,16,128s32,72,112,72,112-72,112-72S208,56,128,56Z"/><circle cx="128" cy="128" r="40"/>'),
  eyeoff:         ph('<line x1="48" y1="40" x2="208" y2="216"/><path d="M154.91,157.6a40,40,0,0,1-53.82-59.2"/><path d="M135.53,88.71a40,40,0,0,1,32.3,35.53"/><path d="M208.61,169.1C230.41,149.58,240,128,240,128S208,56,128,56a126,126,0,0,0-20.68,1.68"/><path d="M74,68.6C33.23,89.24,16,128,16,128s32,72,112,72a118.05,118.05,0,0,0,54-12.6"/>'),
  cover:          ph('<line x1="48" y1="40" x2="208" y2="216"/><path d="M154.91,157.6a40,40,0,0,1-53.82-59.2"/><path d="M135.53,88.71a40,40,0,0,1,32.3,35.53"/><path d="M208.61,169.1C230.41,149.58,240,128,240,128S208,56,128,56a126,126,0,0,0-20.68,1.68"/><path d="M74,68.6C33.23,89.24,16,128,16,128s32,72,112,72a118.05,118.05,0,0,0,54-12.6"/>'),
  expand:         ph('<polyline points="160 48 208 48 208 96"/><line x1="144" y1="112" x2="208" y2="48"/><polyline points="96 208 48 208 48 160"/><line x1="112" y1="144" x2="48" y2="208"/>'),
  shrink:         ph('<polyline points="144 64 144 112 192 112"/><line x1="208" y1="48" x2="144" y2="112"/><polyline points="64 144 112 144 112 192"/><line x1="48" y1="208" x2="112" y2="144"/>'),
  marker:         ph('<polyline points="88 128 24 192 96 216 136 176"/><path d="M184,160l-26.34,26.34a8,8,0,0,1-11.32,0L77.66,117.66a8,8,0,0,1,0-11.32L104,80"/><path d="M248,112l-50.34,50.34a8,8,0,0,1-11.32,0L101.66,77.66a8,8,0,0,1,0-11.32L152,16"/>'),
  pen:            ph('<path d="M92.69,216H48a8,8,0,0,1-8-8V163.31a8,8,0,0,1,2.34-5.65L165.66,34.34a8,8,0,0,1,11.31,0L221.66,79a8,8,0,0,1,0,11.31L98.34,213.66A8,8,0,0,1,92.69,216Z"/><line x1="136" y1="64" x2="192" y2="120"/>'),
  edit:           ph('<path d="M92.69,216H48a8,8,0,0,1-8-8V163.31a8,8,0,0,1,2.34-5.65L165.66,34.34a8,8,0,0,1,11.31,0L221.66,79a8,8,0,0,1,0,11.31L98.34,213.66A8,8,0,0,1,92.69,216Z"/><line x1="136" y1="64" x2="192" y2="120"/>'),
  erase:          ph('<line x1="96" y1="104" x2="160" y2="168"/><path d="M112,216,219.31,108.69a16,16,0,0,0,0-22.63L177.94,44.69a16,16,0,0,0-22.63,0L36.69,163.31a16,16,0,0,0,0,22.63L66.75,216H216"/>'),
  hl:             ph('<circle cx="128" cy="128" r="96"/><path d="M176,211.16V176a8,8,0,0,0-8-8H88a8,8,0,0,0-8,8v35.16"/><path d="M96,168V144a8,8,0,0,1,8-8h48a8,8,0,0,1,8,8v24"/><path d="M147.84,136l-12-57.63c-1.77-8.49-13.89-8.49-15.66,0l-12,57.63"/>'),
  list:           ph('<line x1="88" y1="64" x2="216" y2="64"/><line x1="88" y1="128" x2="216" y2="128"/><line x1="88" y1="192" x2="216" y2="192"/><circle cx="44" cy="64" r="12" fill="currentColor" stroke="none"/><circle cx="44" cy="128" r="12" fill="currentColor" stroke="none"/><circle cx="44" cy="192" r="12" fill="currentColor" stroke="none"/>'),
  grid:           ph('<rect x="48" y="48" width="64" height="64" rx="8"/><rect x="144" y="48" width="64" height="64" rx="8"/><rect x="48" y="144" width="64" height="64" rx="8"/><rect x="144" y="144" width="64" height="64" rx="8"/>'),
  queue:          ph('<line x1="40" y1="64" x2="216" y2="64"/><line x1="40" y1="128" x2="136" y2="128"/><line x1="40" y1="192" x2="136" y2="192"/><polygon points="240 160 176 200 176 120 240 160"/>'),
  filter:         ph('<line x1="64" y1="136" x2="192" y2="136"/><line x1="24" y1="88" x2="232" y2="88"/><line x1="104" y1="184" x2="152" y2="184"/>'),
  image:          ph('<rect x="32" y="48" width="192" height="160" rx="8"/><circle cx="156" cy="100" r="12" fill="currentColor" stroke="none"/><path d="M147.31,164,173,138.34a8,8,0,0,1,11.31,0L224,178.06"/><path d="M32,168.69l54.34-54.35a8,8,0,0,1,11.32,0L191.31,208"/>'),
  camera:         ph('<path d="M208,208H48a16,16,0,0,1-16-16V80A16,16,0,0,1,48,64H80L96,40h64l16,24h32a16,16,0,0,1,16,16V192A16,16,0,0,1,208,208Z"/><circle cx="128" cy="132" r="36"/>'),
  twin:           ph('<polyline points="168 168 216 168 216 40 88 40 88 88"/><rect x="40" y="88" width="128" height="128"/>'),
  copy:           ph('<polyline points="168 168 216 168 216 40 88 40 88 88"/><rect x="40" y="88" width="128" height="128"/>'),
  link:           ph('<line x1="96" y1="160" x2="160" y2="96"/><path d="M112,76.11l30.06-30a48,48,0,0,1,67.88,67.88L179.88,144"/><path d="M76.11,112l-30,30.06a48,48,0,0,0,67.88,67.88L144,179.88"/>'),
  again:          ph('<polyline points="24 56 24 104 72 104"/><path d="M67.59,192A88,88,0,1,0,65.77,65.77L24,104"/>'),
  fix:            ph('<polyline points="184 104 232 104 232 56"/><path d="M188.4,192a88,88,0,1,1,1.83-126.23L232,104"/>'),
  info:           ph('<circle cx="128" cy="128" r="96"/><path d="M120,120a8,8,0,0,1,8,8v40a8,8,0,0,0,8,8"/><circle cx="124" cy="84" r="12" fill="currentColor" stroke="none"/>'),
  trap:           ph('<circle cx="128" cy="128" r="96"/><line x1="128" y1="32" x2="128" y2="72"/><line x1="128" y1="184" x2="128" y2="224"/><line x1="32" y1="128" x2="72" y2="128"/><line x1="184" y1="128" x2="224" y2="128"/>'),
  clean:          ph('<polyline points="88 136 112 160 168 104"/><circle cx="128" cy="128" r="96"/>'),
  sheet:          ph('<path d="M200,224H56a8,8,0,0,1-8-8V40a8,8,0,0,1,8-8h96l56,56V216A8,8,0,0,1,200,224Z"/><polyline points="152 32 152 88 208 88"/><line x1="96" y1="136" x2="160" y2="136"/><line x1="96" y1="168" x2="160" y2="168"/>'),
  trophy:         ph('<line x1="96" y1="224" x2="160" y2="224"/><line x1="128" y1="184" x2="128" y2="224"/><path d="M58,128H48A32,32,0,0,1,16,96V80a8,8,0,0,1,8-8H56"/><path d="M198,128h10a32,32,0,0,0,32-32V80a8,8,0,0,0-8-8H200"/><path d="M56,48H200v63.1c0,39.7-31.75,72.6-71.45,72.9A72,72,0,0,1,56,112Z"/>'),
  twin_test:      ph('<polyline points="88 88 88 40 216 40 216 120"/><rect x="40" y="88" width="104" height="128"/><circle cx="192" cy="180" r="40"/><polyline points="192 156 192 180 208 192"/>'),
  eliminate:      '<g class="ph" fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5"><path d="M3.5 17l3-9 3 9M4.6 14h3.8M12.5 8h3a2.2 2.2 0 0 1 0 4.4h-3zM12.5 12.4h3.4a2.3 2.3 0 0 1 0 4.6h-3.4zM3 20.5L21 3.5"/></g>',
  strikes:        '<g class="ph" fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5"><path d="M4 9l4 6M8 9l-4 6M10 9l4 6M14 9l-4 6M16 9l4 6M20 9l-4 6"/></g>',
  dot:            '<circle cx="12" cy="12" r="4" fill="var(--amber)"/>',
};
const ICON_FILL = Object.fromEntries(Object.keys(PHF).filter(n => n !== 'play').map(n => [n, phf(PHF[n])]));
