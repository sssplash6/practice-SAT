# Site v1: the object era

Archived 2026-09-23, when the product moved to a flat, minimal interface.
Nothing here is served. It is kept so any of it can be
brought back, and so nothing depends on claude.ai keeping an artifact alive:
earlier front-page artifacts were deleted and could not be recovered.

The git tag `site-v1` marks the same moment, so `git checkout site-v1 -- web`
restores the whole site exactly as it was.

## `web/`

The site as it stood: a rail, and one drawn object per practice section.

| page | what it was |
|---|---|
| `index.html` | Overview: projected score, trend of the last six mocks, resume row |
| `mock/` | Shoebox Tapes: three shoeboxes of cassettes, one per mock |
| `domain/` | Domain Turntable: a record per domain, dropped on the platter |
| `mixed/` | Sticker Sheets: peel a topic sticker per question onto a page |
| `duels/` | The rank badge, filled in ten steps per `spec/rating.md` |
| `diagnostic/` | The diagnostic entry, sign-up, verification and results |
| `test/` | The test window, built in Bluebook's shape |
| `assets/` | The shell: `app.css`, the rail in `app.js`, the mark |

To look at it: `python3 -m http.server 8791 --directory archive/site-v1/web`.
The practice, mock and diagnostic pages call the API, so they only build sets
when served by `server/app.py`.

## `concepts/`

The front-page concepts and hero animations, which only ever lived as
artifacts. Each file is the page exactly as published, and opens on its own.

| file | what it is | artifact |
|---|---|---|
| `front-pages.html` | the hub: eighteen instrument sketches | [link](https://claude.ai/artifact/S8ApDBY3c7b88kBLeByRqN) |
| `combined-practice-pages.html` | the combined-practice candidates side by side | [link](https://claude.ai/artifact/APufN6UnEMtZSQFvXRCeFA) |
| `jukebox.html` | The Jukebox: queue records by domain letter and topic number | [link](https://claude.ai/artifact/FBpfTXgqsGVG2aLvrozEZL) |
| `mixtape.html` | The Mixtape: record tracks onto a cassette | [link](https://claude.ai/artifact/RETNzaiu4cgcWut3WPqy4i) |
| `record-crates.html` | Record Crates: pull sleeves into a stack | [link](https://claude.ai/artifact/A6E77pHY4qUNMnp8bYvync) |
| `photocopier.html` | The Photocopier: a mock as an exact copy | [link](https://claude.ai/artifact/3mFZdCsqYYAzbEFunfGZof) |
| `duel-loadout.html` | Duel Loadout: load five chambers, one per question | [link](https://claude.ai/artifact/T1YXj7utbH3sED1eYxD8mK) |
| `club-ladder.html` | The Club Ladder: placement engraves your name on the board | [link](https://claude.ai/artifact/MtTXcWFhzVNzcTQcmpRLpm) |
| `spinning-tops.html` | Spinning Tops: a physics duel in a dish | [link](https://claude.ai/artifact/EATQ5kuWwvmemeyAjcxxXr) |
| `rally.html` | The Rally: first to five | [link](https://claude.ai/artifact/NeCXb8RqVjzk1Kqm25552a) |
| `conkers.html` | Conkers: beat a five, become a six | [link](https://claude.ai/artifact/7ShaLUbr7tKrx3z6kpwzEj) |
| `rope-and-ribbon.html` | The Rope and the Ribbon: tug of war from above | [link](https://claude.ai/artifact/ELirLHah9LHyW2Eg1DKdnG) |
| `thumb-war-hero.html` | Thumb War, the six-second Three.js hero loop | [link](https://claude.ai/artifact/LTDAjAH6qhCEjhRSABa3Jz) |
| `arm-wrestle-hero.html` | Arm Wrestle, the seven-second Three.js hero loop | [link](https://claude.ai/artifact/WkBDF1bPMEeKyrsypdQRLY) |
| `the-thumb-war.html` | The Thumb War: the traced line-drawing loop in the duel front page | [link](https://claude.ai/artifact/AJbABtEHinSRdjbN3DgTrM) |
| `diagnostic-entry/` | the dark diagnostic entry, a Design canvas: `Main.dc.html` is its one board | [link](https://claude.ai/artifact/MGaqqVV5HZrt7QL9QpyWCQ) |

The Design canvas board needs the canvas runtime to render, so
`Main.dc.html` reads as source rather than as a page.
