# SAT Freshman

![commits](https://img.shields.io/github/commit-activity/t/sssplash6/ssat) · live at [prac.fsat.io](https://prac.fsat.io)

**The problem.** Freshman Academy's SAT students practise on question banks that run out. Paid prep sites sell a fixed set of items behind quotas, questions start repeating, and a wrong answer is only marked wrong, never explained by the mistake behind it.

**The idea.** Generate the questions instead of storing them. Each Math question type is a template: a parameter space, a solver, and wrong options built from real student mistakes. One template makes unlimited new questions, and the answers are computed, never guessed.

**What it does now.**

- **Math:** all 19 SAT Math topics, 414 templates. Driven by the official items' own numbers, they reproduce the printed answer for 1,030 of 1,039 College Board questions. No question ships until a second, independently written solver agrees with its answer.
- **Reading and Writing:** a 4,819-question bank across 10 skills, every question reviewed and blind-solved before it goes live.
- **Every wrong answer is a diagnosis.** Each wrong option names the mistake that produces it, and the next question repeats the same trap with new numbers until the student beats it.
- **The site:** practice by skill, full adaptive tests built fresh for every sitting in a Bluebook-style window, score reports, a mistakes review, a study plan to the exam date and a daily challenge. Free, no quotas.

**Stack:** Python 3.12, FastAPI, SQLite, plain HTML/CSS/JS. Runs on our own VPS behind Caddy. AI models are used offline only (turning source questions into templates, writing and reviewing R&W items); serving a question runs no model.

## Run it

```bash
pip install -r deploy/requirements.txt
PYTHONPATH=. python3 -m uvicorn server.app:app --port 8000   # site and API on http://localhost:8000
PYTHONPATH=. python3 -m satbank generate --n 5                # a few Math items with rationales
PYTHONPATH=. python3 -m satbank check                          # the quality gate
```

How the engine works, its limits and the per-page notes: [`ENGINEERING.md`](ENGINEERING.md). Writing a new topic: [`TOPIC-GUIDE.md`](TOPIC-GUIDE.md).
