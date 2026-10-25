"""Build the part-2 rewritten items (transitions, last 15 ids) and write them under the lock."""
import fcntl, json, sys

P = json.load(open(__file__.rsplit('/', 1)[0] + '/passages.json'))
STEM = "Which choice completes the text with the most logical transition?"
PATH = '/Users/workingmyassof/freshbot/satbank/satbank/rw/transitions.json'


def item(key, letter, options, explanation, distractors, sources, notes, rewrite):
    return {"key": key, "answer_letter": letter, "options": options, "explanation": explanation,
            "distractors": {k: {"recipe": r, "why_wrong": w} for k, (r, w) in distractors.items()},
            "sources": [{"what": w, "url": u} for w, u in sources], "notes": notes, "rewrite": rewrite}


NEW = [
    item("P1_purpose_aptness.medium", "B", ["Regardless,", "Fittingly,", "In other words,", "Conversely,"],
         "The text says that Trafalgar Square commemorates Nelson’s victory at Trafalgar and that his statue looks over the square. Shonibare’s commission for the square’s plinth was a replica of Nelson’s own flagship. A work about Nelson’s ship suits a square built to honor Nelson, so “Fittingly” is the logical transition.",
         {"A": ("false opposition (dismissive concession)", "“Regardless” would mean the square’s link to Nelson has no bearing on the commission, but the commission matches that link exactly."),
          "C": ("wrong grain (restatement)", "The last sentence does not reword the description of the square; it introduces a new fact about a particular artwork."),
          "D": ("false opposition (plain contrast)", "Nothing about the replica of Nelson’s flagship is the reverse of the square’s tribute to Nelson; the two facts agree.")},
         [("Fourth Plinth built 1841 for an equestrian statue (William IV), left empty; first contemporary work in 1999; Nelson’s Ship in a Bottle shown 24 May 2010 to January 2012", "https://en.wikipedia.org/wiki/Fourth_plinth,_Trafalgar_Square"),
          ("square named to commemorate the 1805 Battle of Trafalgar; statue of Nelson at the top of Nelson’s Column", "https://en.wikipedia.org/wiki/Trafalgar_Square"),
          ("1:30 scale replica of HMS Victory in a bottle, commissioned for the Fourth Plinth", "https://batch.artuk.org/discover/artworks/nelsons-ship-in-a-bottle-310258"),
          ("Shonibare, British Nigerian artist; Victory as Nelson’s flagship; bottle size", "https://www.foxnews.com/world/ship-in-bottle-scale-model-of-nelsons-hms-victory-unveiled-at-trafalgar-square")],
         "Aptness: the setting is described first and the fitting choice follows (the official 2.5 runs the other way, from a poem to the name of its school). Sentence-initial blank.",
         "New subject (Shonibare’s Fourth Plinth ship replaces Sojourner Truth); aptness built from setting to fitting commission, no name-echo or gloss; denser register; decoys changed."),
    item("A1_addition.medium", "D", ["Granted,", "That is,", "Instead,", "In addition,"],
         "The first sentence describes one way Wasser’s team tracks ivory: matching tusk DNA to a reference map to find where elephants were killed. The second sentence describes a second, separate technique: finding the two tusks of one elephant in different seizures to link the shipments to one dealer. Because the second sentence adds another method to the first, “In addition” is the logical transition.",
         {"A": ("false opposition (concession)", "“Granted” would concede a point that limits the first sentence, but matching tusks is not a weakness of the mapping method; it is another tool."),
          "B": ("wrong grain (restatement)", "Searching seizures for paired tusks is not a rewording of comparing DNA with a reference map; it is a different technique with a different result."),
          "C": ("false opposition (replacement)", "“Instead” would mean the team uses tusk matching in place of the reference map, but the text presents both as methods the team uses.")},
         [("Wasser et al. 2015, Science: DNA from 28 large seizures compared with 1,350 reference samples of dung, skin and hair from 29 African countries, revealing two poaching hotspots", "https://www.sciencenews.org/article/ivory-dna-pinpoints-poaching-hot-spots"),
          ("reference samples from dung, skin and hair; poaching hotspots", "https://news.mongabay.com/2015/06/using-dna-evidence-to-pinpoint-poaching-zones/"),
          ("Wasser et al. 2018, Science Advances, “Combating transnational organized crime by linking multiple large ivory seizures to the same dealer”: matching tusks of one elephant across seizures", "https://www.sciencenews.org/article/dna-seized-elephant-ivory-unmasks-trafficking-cartels-africa"),
          ("Wasser is a conservation biologist at the University of Washington Center for Conservation Biology", "https://www.washington.edu/news/2022/02/14/ivory-trafficking")],
         "Addition: a second technique of the same team, toward the same goal. Sentence-initial blank; colon inside the blank sentence.",
         "New subject (ivory DNA forensics replaces the Grimm brothers); the second method is a distinct technique rather than an appended fact; denser register; key now the longest option."),
    item("T1_sequence_time.medium", "C", ["For instance,", "Similarly,", "Finally,", "In other words,"],
         "The text describes a long struggle: many institutes failed to rear bluefin tuna from captive-bred parents, and Kindai kept working on the problem from 1970 after others gave up. The last sentence gives the success that came at the end of that effort in 2002. “Finally” marks the end of a long process, so it is the logical transition.",
         {"A": ("wrong grain (example)", "The 2002 success is not one example of Kindai’s persistence or of the difficulties; it is the result reached at the end of them."),
          "B": ("false parallel", "The success is not like the failures described earlier; it is what came after them."),
          "D": ("wrong grain (restatement)", "Producing the first fully farm-raised bluefin in 2002 does not reword the claim that Kindai persisted; it adds a new event.")},
         [("research began 1970; first full-cycle success in June 2002 after 32 years; many institutes tried and failed; Kindai the only institution that continued for 32 years", "https://www.japan.go.jp/tomodachi/_userdata/pdf/2018/spring2018/08_09.pdf"),
          ("Kindai: research began 1970; full-cycle aquaculture achieved June 2002", "https://www.kindai.ac.jp/english/research/research-center/aqua-research/aquaculture/tuna/index.html"),
          ("Kindai hatchery: fish collide with tank walls; cannibalism", "https://www.hatcheryinternational.com/the-bluefin-advantage-inside-kindai-s-ground-breaking-tuna-h-1120/"),
          ("cannibalism and collisions with the tank wall as major causes of juvenile mortality", "https://nagasaki-u.repo.nii.ac.jp/records/15148")],
         "Time: the end of a long effort. Sentence-initial blank followed by a date.",
         "New subject (Kindai bluefin tuna aquaculture replaces Fermat’s Last Theorem); the effort is built from the difficulties and the persistence of one institute; denser register; decoys changed."),
    item("U1_culmination_alt.medium", "A", ["there,", "by comparison,", "in sum,", "nevertheless,"],
         "The first clause names a place, the Jinping Underground Laboratory deep under a mountain, and the clause after the semicolon tells what happens at that place: the PandaX experiment looks for dark matter. “There” points back to the place just named, so it is the logical transition.",
         {"B": ("false opposition (plain contrast)", "Nothing is being compared: the PandaX experiment is not set against the laboratory’s depth but carried out inside it."),
          "C": ("premature summary", "The clause about PandaX does not sum up what came before; it adds a new fact about what the laboratory is used for."),
          "D": ("false opposition (concession)", "“Nevertheless” would mean the experiment runs in spite of the laboratory’s depth, but the depth is what shields it from cosmic rays.")},
         [("CJPL inaugurated December 2010 near the center of a 17.5-km Jinping traffic tunnel; 2,400 m of rock overburden; marble bedrock; deepest operating underground laboratory; PandaX uses liquid xenon to detect recoiling xenon nuclei", "https://arxiv.org/abs/1801.00587"),
          ("laboratory in Liangshan, southern Sichuan; depth 2,400 m; inaugurated 12 December 2010; PandaX among its experiments", "https://en.wikipedia.org/wiki/China_Jinping_Underground_Laboratory"),
          ("rock overburden shields experiments from cosmic radiation", "https://inspirehep.net/files/f8a4f49a0417d1af03af81e582b69f3c")],
         "Place: B happens at the place just named. Blank after a semicolon (lowercase options) rather than sentence-initial as in the official 2.8.",
         "New subject (Jinping laboratory replaces the Stein salon); the place link sits after a semicolon instead of opening a sentence; denser register; decoys changed."),
    item("C1_two_subject.hard", "D", ["accordingly,", "moreover,", "that is,", "by contrast,"],
         "The text says researchers disagree about farming and wildlife. Phalan and colleagues favor farming as little land as possible so more forest is left; Perfecto and Vandermeer say the farmland between forest patches matters most. These are opposing positions on the same question, so “by contrast” is the logical transition.",
         {"A": ("unearned cause", "Perfecto and Vandermeer’s view does not follow from Phalan’s findings; it rejects their conclusion."),
          "B": ("additive decoy", "“Moreover” would add a point that supports the first view, but the second view argues for the opposite approach."),
          "C": ("wrong grain (restatement)", "The second clause does not reword Phalan’s conclusion; it states a different researchers’ competing view.")},
         [("Phalan, Onial, Balmford and Green 2011, Science: birds and trees in southwest Ghana and northern India; most species would have larger populations if farming were confined to the smallest feasible area (land sparing)", "https://sciencedaily.com/releases/2011/09/110901142102.htm"),
          ("Perfecto and Vandermeer: the quality of the agricultural matrix between fragments matters most, because local extinctions are balanced by migration through a high-quality matrix; land sparing called fallacious", "https://archive.foodfirst.org/publication/biodiversity-and-agriculture-natures-matrix-and-the-future-of-conservation/"),
          ("Perfecto and Vandermeer argue against land sparing (Ecosistemas 2012)", "https://revistaecosistemas.net/index.php/ecosistemas/article/view/36")],
         "Contrast: two positions on one question, after a semicolon (lowercase options).",
         "New subject (land sparing vs. land sharing replaces James-Lange vs. Cannon-Bard); a specific study set against named critics; context sentence added; key ties for longest option."),
    item("C3_limiting_fact.hard", "B", ["therefore,", "though,", "for instance,", "likewise,"],
         "The first sentence stresses how closely Sangaré’s music follows the tradition of the Wassoulou region. The next sentence turns to her lyrics, which challenge conventions long accepted in that same region. Because the lyrics pull against the tradition the music draws on, the contrast word “though” is the logical transition.",
         {"A": ("unearned cause", "Building her sound on a regional tradition does not lead her to challenge that region’s customs; the two facts pull in opposite directions."),
          "C": ("wrong grain (example)", "Her lyrics are not an example of a sound rooted in Wassoulou tradition; they are a different part of her work that departs from tradition."),
          "D": ("false parallel", "“Likewise” would mean the lyrics resemble the music, but the music follows tradition while the lyrics challenge it.")},
         [("Wassoulou: mother’s family’s region in southern Mali, pentatonic music; kamelengoni created in the 1960s from the hunters’ donsongoni harp; Moussolou recorded in 1989, warning against polygamy and forced marriage", "https://worldcircuit.co.uk/artists/oumou-sangare/"),
          ("Moussolou: songs drawn from life in a society that continues to embrace polygamy; kamalengoni at the center of the sound", "https://www.encyclopedia.com/people/literature-and-arts/music-popular-and-jazz-biographies/oumou-sangare")],
         "Contrast with the key “though” as an interrupter after the subject noun phrase, inside a sentence. The official 3.7 frame (“Even in this ... work, ______”) is deliberately not used; the subtype label is kept for the cell.",
         "New subject (Oumou Sangaré replaces Kehinde Wiley); the “Even in this ..., ______ though” frame is dropped for an interrupter after the subject; denser register; decoys changed."),
    item("K1_grant_turn.hard", "C", ["For this reason,", "Moreover,", "Admittedly,", "Specifically,"],
         "The first sentence claims that the Papunya paintings continued a very old tradition. The second sentence admits a point against that claim: the paints and boards were new. The last sentence (“Yet ...”) returns to the main claim: the designs came from old ceremonies. A writer who grants a point before turning back to the claim uses “Admittedly,” so it is the logical transition.",
         {"A": ("unearned cause", "The paintings’ link to an old tradition is not the reason their materials were new."),
          "B": ("additive decoy", "“Moreover” would add support for the first sentence, but new materials cut against the claim of continuity; the “Yet” that follows shows the sentence is a concession."),
          "D": ("wrong grain (specification)", "New paints and boards are not a more precise statement of the old tradition the first sentence describes; they are a point against it.")},
         [("1971: Bardon distributed acrylic paints and materials to Aboriginal men at Papunya; first works on composition board and building materials; imagery previously carried in body painting and sand mosaics", "https://www.smithsonianmag.com/arts-culture/contemporary-aboriginal-art-10885394/"),
          ("ceremonial leaders used designs borrowed from ground and body art on industrial surfaces such as Masonite; Bardon a schoolteacher from the early 1970s", "https://camd.org.au/?p=7899"),
          ("Bardon supplied materials to Aboriginal men at Papunya in 1971; Papunya Tula Artists formed 1972", "https://www.nfsa.gov.au/collection/item/papunya-tula-artists")],
         "Concession: claim, then a granted objection, then the claim resumes with “Yet” (not the official “Of course ... Still” or “Of course ... but” frames). Key “Admittedly,” is not keyed in the official bank.",
         "New subject (Papunya painting replaces Monet’s Rouen Cathedral); the “Of course ... Still,” scaffold is replaced by a claim, an “Admittedly” concession and a “Yet” turn; decoys changed."),
    item("K2_qualification.hard", "B", ["Hence,", "That said,", "Likewise,", "Thus,"],
         "The first sentence gives a good reason for switching streetlights to LEDs: they save energy. The next sentence limits that picture: the switch may make light pollution worse for wildlife, as a 2014 study of insects suggests. A transition that accepts a point and then adds a qualification is needed, so “That said” is the logical choice.",
         {"A": ("unearned cause", "Saving energy does not cause the ecological harm; the harm comes from the light itself, as the study shows."),
          "C": ("false parallel", "The ecological cost is not similar to the energy savings; it is a drawback that weighs against them."),
          "D": ("unearned cause", "The possible harm to insects is not a conclusion drawn from the energy savings; it qualifies them.")},
         [("Pawson and Bader 2014, Ecological Applications 24(7):1561–1568: energy-efficient white LEDs replacing HPS lamps; LED light traps captured on average 48% more insects than HPS traps", "https://www.ifsc.usp.br/~reynaldo/para_Carol/11-%20Pawson%20and%20Bader_Ecol_Apps_2014.pdf"),
          ("press summary of the 48 percent finding", "https://techxplore.com/news/2014-10-invertebrates-conventional.html")],
         "Concession: a supported claim, then a qualification; the evidence follows in its own sentence. “Hence” and “Thus” are a deliberate synonym pair of decoys (as in official 3.2).",
         "New subject (LED streetlights and insects replaces Everest vs. Mauna Kea); no trivia aside; denser register; key now the longest option."),
    item("E1_consequence.hard", "A", ["therefore,", "similarly,", "nevertheless,", "meanwhile,"],
         "The DNA study found that moa populations stayed large and genetically stable for 4,000 years until the extinction. That evidence counts against the idea that moa were already declining before people arrived. The last sentence draws that conclusion, so “therefore” is the logical transition.",
         {"B": ("false parallel", "The verdict on the decline claims is not like the DNA finding; it is the conclusion the finding supports."),
          "C": ("false opposition (concession)", "“Nevertheless” would mean the claims are unfounded in spite of the evidence, but the evidence is the reason they are unfounded."),
          "D": ("wrong time", "The last sentence does not describe something happening at the same time as the study; it judges a claim in light of the study.")},
         [("Allentoft et al. 2014, PNAS: 281 moa, four species, mostly from the last 4,000 years before extinction; genetic stability and large populations; contradicts claims of decline before Polynesian settlement in the late 13th century", "https://doi.org/10.1073/pnas.1314972111"),
          ("press coverage of the study", "https://www.smithsonianmag.com/smart-news/genetics-study-suggests-humans-killed-moa-180950241/")],
         "Cause/effect: evidence, then a verdict on a belief, with the key as an interrupter. The belief is stated only in the verdict sentence (the official 3.9 states the myth first, then “However, recent research”).",
         "New subject (moa ancient DNA replaces the War of the Worlds panic); evidence comes first and the verdict sentence names the claim, so there is no myth framing; denser register."),
    item("P1_purpose_aptness.hard", "D", ["Regardless,", "In comparison,", "Meanwhile,", "To that end,"],
         "The first sentence states Heringer’s goal: the money for building the school should stay with the villagers rather than go to outside industries such as cement makers. The second sentence describes what she did to meet that goal: local people built the school from local earth, straw, and bamboo. Because the second sentence is the action taken to serve the goal, “To that end” is the logical transition.",
         {"A": ("false opposition (dismissive concession)", "“Regardless” would mean Heringer’s goal did not matter to how the school was built, but the building method carries out that goal."),
          "B": ("false opposition (plain contrast)", "Nothing is being compared: the second sentence describes the same school, not a different one."),
          "C": ("wrong time", "The construction is not a separate event happening alongside Heringer’s goal; it is the way she pursued it.")},
         [("METI school, Rudrapur: Heringer with Eike Roswag; built September to December 2005; earth, straw, bamboo, brick foundations; local craftsmen and villagers; 2007 Aga Khan Award", "https://en.wikipedia.org/wiki/METI_Handmade_School"),
          ("Heringer: the intention is that the budget remains with the local people and does not go to external markets such as the cement industry", "https://www.moma.org/audio/playlist/248/3189"),
          ("workers from the surrounding community", "https://www.azuremagazine.com/article/anna-heringer-a-community-builder/")],
         "Purpose: a goal stated as the architect’s argument, then the act that serves it (not the official 3.15 “believed ... To that end” frame).",
         "New subject (Anna Heringer’s METI school replaces Noah Webster); the goal is an economic aim, not a belief; denser register; decoys changed."),
    item("A1_addition.hard", "C", ["Consequently,", "Specifically,", "Additionally,", "Nonetheless,"],
         "The first sentence says the memoir tells the story of Bui’s parents, from their childhoods to their escape from Vietnam. The second sentence names another strand of the same book: Bui’s own experience as a new mother. Because it adds a further element of the book, “Additionally” is the logical transition.",
         {"A": ("unearned cause", "Telling her parents’ story does not cause the book to cover Bui’s motherhood; if anything, the last sentence shows the motherhood prompted her look back."),
          "B": ("wrong grain (specification)", "Bui’s own motherhood is not a more exact account of her parents’ lives; it is a separate part of the book."),
          "D": ("false opposition (concession)", "Nothing in the parents’ story makes it surprising that the book also follows Bui herself, so a concession word does not fit.")},
         [("2017 memoir tracing the family’s escape after the fall of South Vietnam", "https://www.arts.gov/initiatives/nea-big-read/best-we-could-do-illustrated-memoir"),
          ("mother grew up in privilege, father had an uprooted childhood in the 1950s; family among the boat people; son born 2005", "https://www.tcj.com/reviews/the-best-we-could-do/"),
          ("Bui interviewed her parents over years, starting with a graduate-school project", "https://www.npr.org/transcripts/634606313"),
          ("opens with Bui giving birth in New York in 2005, which prompts her to explore her parents’ past; alternates between her present as a new mother and her parents’ lives", "https://supersummary.com/the-best-we-could-do/summary")],
         "Addition: a second strand of one work. A follow-up sentence after the blank sentence gives the link between the strands. The echo phrase after the key (official 3.20) is deliberately not used.",
         "New subject (Thi Bui’s memoir replaces Rivera’s Detroit murals); no echo phrase after the key and no colon list; follow-up sentence added; key now the longest option."),
    item("S1_spec_restate.hard", "B", ["Furthermore,", "That is,", "Instead,", "Previously,"],
         "The second sentence gives the name of a principle, Two-Eyed Seeing, without explaining it. The last sentence explains what the name means: seeing with the strengths of Indigenous knowledge through one eye and of Western science through the other, using both together. Because it restates the principle in plain terms, “That is” is the logical transition.",
         {"A": ("additive decoy", "The last sentence does not add a new point to the principle; it explains what the principle itself means."),
          "C": ("false opposition (replacement)", "“Instead” would set the last sentence against Two-Eyed Seeing, but it describes Two-Eyed Seeing."),
          "D": ("wrong time", "The way of seeing described in the last sentence is the 2004 principle itself, not something that came before it.")},
         [("Integrative Science launched at Cape Breton University in 1999; Albert Marshall brought the guiding principle to light in 2004; one eye Indigenous, the other Western, both together", "https://en.wikipedia.org/wiki/Two-Eyed_Seeing"),
          ("Etuaptmumk definition (Cape Breton University wording) and 2004 introduction to guide Integrative Science", "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC8291645/")],
         "Restatement: a named principle, then a plain unpacking of the metaphor.",
         "New subject (Two-Eyed Seeing replaces Sullivan’s “form follows function”); no famous quotation; context sentence added; denser register; decoys changed."),
    item("M1_emphasis.hard", "A", ["In fact,", "Nonetheless,", "Consequently,", "For example,"],
         "The text claims that the 24,000-year survival vastly extended what was known about how long frozen rotifers can survive. The last sentence gives a fact that makes the claim even stronger: earlier reports showed only six to ten years. Although it describes earlier findings, it supports the claim rather than opposing it, so “In fact” is the logical transition.",
         {"B": ("false opposition (concession)", "The short earlier record does not cut against the claim that the finding extended the limits; it shows how large the extension was."),
          "C": ("unearned cause", "The earlier reports came before the 2021 finding, so they cannot be its result."),
          "D": ("wrong grain (example)", "The earlier six-to-ten-year record is not an example of the new finding; it is the old limit the finding surpassed.")},
         [("Shmakova, Malavin et al. 2021, Current Biology: bdelloid rotifer from northeastern Siberian permafrost dated to about 24,000 years; reproduced by parthenogenesis in the lab; previous reports suggested survival of six to ten years frozen; longest reported case of rotifer survival in a frozen state", "https://doi.org/10.1016/j.cub.2021.04.077"),
          ("press summary naming Malavin and Shmakova", "https://www.sci.news/biology/frozen-bdelloid-rotifers-siberian-permafrost-09745.html")],
         "Emphasis, content-contrast trap: B describes an earlier, much smaller record, which supports A’s claim.",
         "New subject (rotifers from permafrost replaces the kakapo); the support is an earlier record, not a restatement of an ‘outlier’ label; no packed trait list; decoys changed."),
    item("U1_culmination_alt.hard", "D", ["in addition,", "therefore,", "for example,", "ultimately,"],
         "The text says that Waste Not began as a way to help the artist’s mother through her grief. The sentence with the blank tells what the work became in the end: a portrait of a whole generation. “Though” already marks the contrast between the start and the outcome, so the blank needs a word for the final result, and “ultimately” is the logical transition.",
         {"A": ("additive decoy", "The sentence does not add a second, separate point; it tells what the private project turned into over time."),
          "B": ("unearned cause", "Beginning as a private consolation is not the reason the work came to be seen as a portrait of a generation; the “Though” clause presents it as a contrast."),
          "C": ("wrong grain (example)", "The installation’s later reputation is not an example of anything stated before; it is the outcome of the project.")},
         [("Waste Not dated 2005; began as an effort to pull the artist’s mother out of grief after his father died in 2002; her possessions including the wood frame of her house", "https://www.moma.org/calendar/exhibitions/960"),
          ("over 10,000 items collected over five decades; father’s death in 2002; Kate Bush: “a portrait of China, and a history of survival through great times of change”", "https://artlyst.com/song-dong-exhibition-for-barbican-2012/"),
          ("first made in Beijing in 2005; title refers to a frugal way of life shaped by a generation that lived through the Cultural Revolution", "https://www.vanartgallery.bc.ca/exhibitions/song-dong-waste-not/")],
         "Culmination: the contrast is marked by a sentence-initial “Though” clause and the blank opens the main clause (not the official 3.2 “; ______ though,” construction).",
         "New subject (Song Dong’s Waste Not replaces the Louisiana Purchase); the “; ______ though,” construction is replaced by a “Though ..., ultimately” sentence; denser register; decoys changed."),
]


def apply():
    with open(PATH + ".lock", "w") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        d = json.load(open(PATH))
        by = {i["id"]: i for i in d["items"]}
        for n in NEW:
            it = by["transitions." + n["key"]]
            it["passage"] = P[n["key"]]
            it["stem"] = STEM
            for k in ("options", "answer_letter", "explanation", "distractors", "sources", "notes", "rewrite"):
                it[k] = n[k]
            it["word_count"] = len(it["passage"].split()) - 1
            it["review"] = None
        json.dump(d, open(PATH, "w"), indent=2, ensure_ascii=False)


if __name__ == "__main__":
    for n in NEW:
        assert n["answer_letter"] not in n["distractors"] and len(n["distractors"]) == 3, n["key"]
        assert P[n["key"]].count("______") == 1
        assert "—" not in n["explanation"] + n["notes"] + n["rewrite"] + "".join(d["why_wrong"] for d in n["distractors"].values()), n["key"]
    if sys.argv[1:] == ["write"]:
        apply()
    print("ok", len(NEW))
