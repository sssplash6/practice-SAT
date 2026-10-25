# results-ui.js (456)
- 40-44 CAUSE incl entry.
- 189 subtitle mock route 'harder M2'/'easier M2'.
- 200 two = o.subjects>1 || modules have >1 subject -> subject-aware chips (223-244: "one group per (subject, module): never a hard-coded M1 / M2 pair"), qlabel/qlabel.addr.
- 301 Peek gauge subject: 'math' hard-coded (should be r.subject; and full test total).
- 307 domains meters from r.domains (server).
- 310-323 Peek strips byMod keyed by it.module (no subject) 'Module n'; fallback infers module by m1 asked when r.mode==='mock'. Merges R&W M1 with Math M1.
- 340 openPlayer UI.review without sitting.subjects.
- 367 progressCard 'Module n' when kind mock.
- 390-391 skillPanel uses UI.TOPIC (math) fallback short=topic slug for rw.
