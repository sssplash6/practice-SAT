# results/page.js (684)
- 40 FORMAT mcq/spr 'Grid-in'. 42 DOMAIN_ORDER from UI.DOMAINS. 43 topicName via UI.TOPIC.
- 62-66 startTest POST /mock/new {full, timed} (legacy body).
- 218-219 'Full section' (70 min) / 'One module' (35 min).
- 231-234 target track on 200-800 scale (pos = (v-200)/6 %).
- 244 'Sit a full section ... (70 min)'.
- 258-273 hero(): 263 'Math is measured here; Reading and Writing is your own score until SAT Freshman has R&W questions.' 270 'Math estimate', 272 '/800'.
- 316 chart detail 'harder M2'/'easier M2'. 323-326 bandChart grid:200 (no min/max passed -> defaults? check charts).
- 432 domtrend tip 'one full SAT Math section: two modules, 44 questions. A module is one half of it (22 questions)'. 437-438 colName/colTip 22/20/44.
- 433 doms from DOMAIN_ORDER (UI.DOMAINS).
- 515 sitting score fallback right/asked*800.
- 607 drawSkills filters topics (t.subject||'math')==='math' -> RW skills excluded on Results.
- 367 tests count mock+module+diagnostic; 372 'section'.
# diagnostic/index.html (78)
- 40 '20 questions · 32 min · all four domains evenly'. 42 Start -> /tests/?start=diagnostic; 70-75 TestStart.go({kind:'diagnostic'}) -> POST /session.
- 47 'A first band, about 200 points wide'. 65 UI.scale min 200 max 800.
- 48 'like a real module'.
# signup.html (130): subject-neutral. 55 'once the last module is handed in'. Gate via GET /session/{sid}/results 409=finish.
# verified.html (46): subject-neutral.
