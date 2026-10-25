import fcntl, json, sys
sys.path.insert(0, '/Users/workingmyassof/freshbot/satbank/spec/rw/fidelity/work/rewrite2_words_in_context_1')
from final import P, O
path = '/Users/workingmyassof/freshbot/satbank/satbank/rw/words_in_context.json'
E = {
"B1.easy": dict(
 explanation="The second sentence says Fuentes works from “brief mentions” of these women in colonial records. Lives that survive only as brief mentions survive in pieces, so the archive preserves them only in fragmentary form.",
 d={"B": ("reversal", "Comprehensive means complete, but the women appear only in brief mentions, the opposite of a full record."),
    "C": ("plausible but unsupported", "The women appear in colonial records, which are documents, not fiction; nothing suggests the archive invents their lives."),
    "D": ("plausible but unsupported", "Nothing says the records overstate the women’s lives; the problem described is how little the records say.")},
 sources=[{"what": "Dispossessed Lives: Enslaved Women, Violence, and the Archive, Marisa J. Fuentes, University of Pennsylvania Press 2016 (Early American Studies); women whose stories appear only briefly in historical records; fragmentary sources combined with black feminist theory; power of slave owners, colonial authorities and the archive", "url": "https://www.mceas.org/publications/book-series/dispossessed-lives-enslaved-women-violence-and-archive"},
          {"what": "Publisher description: in the eighteenth century Bridgetown, Barbados, was heavily populated by enslaved and free women; their stories appear only briefly in historical records", "url": "https://page158books.com/book/9780812224184"}],
 notes="Title italic in print. Theme: history (Caribbean slavery, archival method).",
 rewrite="new subject (Fuentes, Dispossessed Lives) replacing Brancusi Bird in Space; no strikingly/colon-list or rather-than clue; key fragmentary pinned by brief mentions"),
"B2.easy": dict(
 explanation="The aphids drop off the plant “just before it is eaten,” so they are not swallowed along with it. A response that keeps most of the colony from being eaten allows most of the colony to survive.",
 d={"A": ("plausible but unsupported", "Dropping off the plant is described as a way to avoid being swallowed; the text says nothing about reproduction."),
    "B": ("reversal", "The response saves the aphids from being eaten, so saying it allows them to die reverses its effect."),
    "C": ("plausible but unsupported", "The aphids simply drop off the plant; nothing suggests they travel to a new region.")},
 sources=[{"what": "Gish, Dafni and Inbar 2010, Current Biology: pea aphids sense the elevated heat and humidity of an approaching herbivore’s breath and salvage most of the colony by dropping off the plant in large numbers immediately before it is eaten", "url": "https://europepmc.org/article/MED/20692822"},
          {"what": "DOI of the paper", "url": "https://doi.org/10.1016/j.cub.2010.06.065"},
          {"what": "University of Haifa team; potted alfalfa eaten by a goat; about 65% of aphids dropped just before they would have been eaten", "url": "https://sciencedaily.com/releases/2010/08/100809123532.htm"}],
 notes="Theme: natural science (insect behavior).",
 rewrite="new subject (pea aphids flee mammal breath, Gish 2010) replacing Pony Express and telegraph; cause carried by the dropping behavior, no Because clause"),
"B3.easy": dict(
 explanation="“However” signals that Odom’s finding contrasts with the older view. Odom found female song in 71 percent of the species examined, so the older view must have been that female song was unusual; the first sentence agrees, describing song as treated as a trait shaped by males competing for mates.",
 d={"A": ("reversal", "Widespread is what Odom found; “however” sets her finding against the older view, so the older view cannot also be that female song was widespread."),
    "B": ("plausible but unsupported", "The text never discusses whether song is learned or inborn."),
    "D": ("plausible but unsupported", "Nothing in the text concerns when during the year birds sing.")},
 sources=[{"what": "Odom, Hall, Riebel, Omland and Langmore 2014, Nature Communications 5:3379: song historically considered an almost exclusively male trait; female song present in 71% of surveyed species; females sang in the common ancestor of modern songbirds", "url": "https://europepmc.org/search?query=DOI%3A10.1038%2Fncomms4379"},
          {"what": "DOI of the paper", "url": "https://doi.org/10.1038/ncomms4379"},
          {"what": "UMBC news on Karan Odom’s Nature Communications paper", "url": "https://biology.umbc.edu/home/news/post/42025"}],
 notes="Theme: natural science (ornithology). Received view then finding, as in 1.27.",
 rewrite="new subject (female birdsong, Odom 2014) replacing Zaha Hadid; contrast via however and the 71 percent finding, no filler opening date"),
"B4.easy": dict(
 explanation="The example shows what the dancers do in ETM: Double Down: each step triggers a sound, and their footwork produces the loops and melodies of the score. Dancers who produce a score are acting as musicians as well as dancers.",
 d={"A": ("topic echo", "The text credits Van Young with designing the electronic boards; the dancers play the boards, they do not build them."),
    "C": ("plausible but unsupported", "Tap dancing is physical, but the example is about the sounds the dancers produce, not their athletic skill."),
    "D": ("plausible but unsupported", "Nothing in the text says the dancers tell a story; the example concerns sound and the score.")},
 sources=[{"what": "ETM: Double Down choreographed by Michelle Dorrance with collaborator Nicholas Van Young; Van Young’s electronic tap boards set off sound with each step; music builds loops from the dancers’ movements", "url": "https://officiallondontheatre.com/show/dorrance-dance-etm-double-down-395505/"},
          {"what": "Van Young: about 40 boards act as a gigantic electronic drum set; dancers trigger them to play melodies; “we’re creating the music as we dance”", "url": "https://www.classicalcalifornia.org/articles/tapping-a-score-for-etm-double-down"},
          {"what": "Electronic tap trigger boards; the entire stage is an instrument; NYT: Dorrance exposes tap’s true nature, that it is music", "url": "https://www.psu.edu/news/arts-and-entertainment/story/dorrance-dance-revolutionizes-tap-style-etm-feb-27-eisenhower"}],
 notes="Title italic in print. Theme: arts (dance). An acoustic trio also plays in the show, hence much of the score.",
 rewrite="new subject (Dorrance, ETM: Double Down) replacing the slime-mold Tokyo rail experiment; example pins musicians, no surprisingly hook"),
"B5.easy": dict(
 explanation="Listeners rated the speakers as more competent and intelligent and were more interested in hiring them. So evaluators who only read the pitches found the candidates less impressive than listeners did.",
 d={"B": ("plausible but unsupported", "The ratings described concern competence, intelligence and interest in hiring; honesty is never mentioned."),
    "C": ("reversal", "Finding the candidates less dull would mean readers liked them more, but it was the listeners who judged the candidates more favorably."),
    "D": ("topic echo", "Pitches involve speaking, but the study compared how capable the candidates seemed, not how much they talked.")},
 sources=[{"what": "Schroeder and Epley 2015, Psychological Science, The Sound of Intellect: hypothetical employers and professional recruiters rated candidates more competent, thoughtful and intelligent when they heard a pitch rather than read it and were more interested in hiring them; voice conveys intellect", "url": "https://europepmc.org/search?query=DOI%3A10.1177%2F0956797615572906"},
          {"what": "DOI of the paper", "url": "https://doi.org/10.1177/0956797615572906"},
          {"what": "APS summary of the study", "url": "https://psychologicalscience.org/?p=108995"}],
 notes="Theme: social science (psychology).",
 rewrite="new subject (voice and perceived intellect, Schroeder and Epley 2015) replacing hummingbird torpor; negated frame is less ______ than, no record-setting figure"),
"B6.easy": dict(
 explanation="Grasshopper mice eat the scorpions and groom only briefly when stung, and the venom ends up blocking the pain signals it triggers. Mice that feel little pain from the stings are largely insensitive to them.",
 d={"A": ("reversal", "The mice routinely prey on the scorpions and feel little pain, the opposite of being vulnerable to the stings."),
    "B": ("plausible but unsupported", "The stings protect the scorpions, not the mice; nothing says the mice are protected by them."),
    "D": ("plausible but unsupported", "The scorpions deliver the stings; the mice are not responsible for them.")},
 sources=[{"what": "Rowe, Xiao, Rowe, Cummins and Zakon 2013, Science: bark scorpion venom induces pain in house mice, rats and humans; grasshopper mice regularly attack and consume bark scorpions, grooming only briefly when stung; their Nav1.8 variants bind the toxins and block pain signals", "url": "https://europepmc.org/search?query=DOI%3A10.1126%2Fscience.1236451"},
          {"what": "DOI of the paper", "url": "https://doi.org/10.1126/science.1236451"}],
 notes="Theme: natural science (physiology).",
 rewrite="new subject (grasshopper mice and bark scorpion venom, Rowe 2013) replacing A Raisin in the Sun; no stacked landmark facts"),
"B1.medium": dict(
 explanation="The colon introduces what the team found: water dissolved the hardened fibers, and new fibers could be drawn from the solution. A change that can be undone and then made again is reversible.",
 d={"A": ("reversal", "The fibers dissolved in water and were formed again, so the transformation is not permanent."),
    "B": ("wrong nuance", "The slime hardens only “when mechanically drawn,” so the change is triggered, not spontaneous, and the colon is about undoing the change, which spontaneous does not describe."),
    "D": ("plausible but unsupported", "Nothing in the text describes waste; regenerating fibers from dissolved ones reuses the material.")},
 sources=[{"what": "Baer, Schmidt, Haensch, Eder, Mayer and Harrington 2017, Nature Communications 8:974, Euperipatoides rowelli: capture slime mechanically drawn into stiff biopolymeric fibres; fibres dissolve with extended exposure to water and regenerated fibres can be drawn from the solution, a fully recyclable process", "url": "https://europepmc.org/search?query=DOI%3A10.1038%2Fs41467-017-01142-x"},
          {"what": "DOI of the paper", "url": "https://doi.org/10.1038/s41467-017-01142-x"},
          {"what": "McGill: Matthew Harrington; velvet worm slime captures prey and solidifies into stiff fibers that can dissolve in water and be reformed", "url": "https://www.mcgill.ca/newsroom/node/307426"}],
 notes="Theme: natural science (biomaterials).",
 rewrite="new subject (reversible velvet worm slime fibers, Baer and Harrington 2017) replacing Engel's law; no closing still-refer-to tag; denser register"),
"B2.medium": dict(
 explanation="Neumes show melodic direction without specifying every pitch, so the melodies cannot simply be read from the manuscript. Barrett had to rebuild them from notations in other manuscripts and test his hypotheses in performance, which is what it means to reconstruct the songs.",
 d={"A": ("wrong nuance", "Dating is a scholarly task, but the manuscript is already identified as eleventh-century, and the missing pitches explain why the melodies, not the date, were hard to recover."),
    "C": ("topic echo", "The obstacle described is missing pitch information, which has nothing to do with translating the poems."),
    "D": ("plausible but unsupported", "Nothing in the text concerns who composed the songs; the neumes explain why the melodies had to be worked out.")},
 sources=[{"what": "Cambridge University 2016: Cambridge Songs (11th century) leaf with songs from Boethius’s Consolation of Philosophy; neumes indicate melodic direction and details of vocal delivery without specifying every pitch; Barrett gathered surviving notations from other manuscripts; Benjamin Bagby of Sequentia tested the theories in performance; concert at Pembroke College, 23 April 2016", "url": "https://www.cam.ac.uk/research/news/first-performance-in-1000-years-lost-songs-from-the-middle-ages-are-brought-back-to-life"},
          {"what": "Barrett’s performing edition and the Boethius project at the Cambridge Faculty of Music", "url": "https://boethius.mus.cam.ac.uk/files/boethius_cambridge_songs_performing_edition_opt.pdf"}],
 notes="Title italic in print. Theme: humanities (musicology).",
 rewrite="new subject (Boethius songs from neumes, Sam Barrett) replacing naked mole-rat cancer study; cause carried by thus ... only by, no Because ... concluded chain"),
"B3.medium": dict(
 explanation="“However” sets Wiese’s view against the claim that Kiezdeutsch is broken German. She says its departures from standard German conform to grammatical regularities, so they are systematic: they follow rules instead of being random errors.",
 d={"A": ("reversal", "Arbitrary departures would be random, which is close to the dismissive view Wiese argues against; following regularities is the opposite."),
    "B": ("plausible but unsupported", "The text says nothing about whether Kiezdeutsch will last; Wiese’s point concerns its grammar."),
    "C": ("wrong nuance", "Cosmetic means surface-level, but the text describes grammatical regularities, a matter of structure, and never says the differences are minor.")},
 sources=[{"what": "Review of Wiese, Kiezdeutsch: Ein neuer Dialekt entsteht (Beck 2012): born among youth in multilingual urban environments; Wiese rejects the view that it is broken German or immigrants’ failed attempt at speaking German; it shows systematic grammatical regularities, many typical of Germanic languages", "url": "https://transit.berkeley.edu/2013/preseau"},
          {"what": "Heike Wiese, linguist; proposal that Kiezdeutsch is a dialect", "url": "https://en.wikipedia.org/wiki/Heike_Wiese"}],
 notes="Theme: social science (linguistics).",
 rewrite="new subject (Kiezdeutsch, Heike Wiese) replacing ginkgo aging study; contrast via dismissed ... however, no popular-science hook or three-item list"),
"B4.medium": dict(
 explanation="The example shows Luger inviting communities across two countries to make the beads that form Every One. Work that depends on the public taking part in its making is participatory.",
 d={"B": ("plausible but unsupported", "Nothing suggests the work longs for the past; it honors missing and murdered Indigenous women and girls."),
    "C": ("topic echo", "Beads can be decorative, but the beads in Every One were made by communities to represent people, not to decorate."),
    "D": ("reversal", "Insular means closed off from others, the opposite of inviting communities across the United States and Canada to take part.")},
 sources=[{"what": "MAD Burke Prize release: Luger is a multidisciplinary artist; for Every One (2018) a video invited communities across the United States and Canada to create and donate two-inch clay beads; each bead is a memorial to one of the four thousand cases; work exemplifies craft as a community endeavor", "url": "https://cdn.artandobject.com/press-release/mad-announces-cannupa-hanska-luger-winner-inaugural-burke-prize"},
          {"what": "Ceramics Monthly: each bead represents the life of a missing or murdered Indigenous girl or woman in Canada and the US; beads form an image of a young woman; Luger’s work is built on collaboration", "url": "https://ceramicartsnetwork.org/ceramics-monthly/ceramics-monthly-article/cannupa-hanska-luger-engaging-community"},
          {"what": "Instructional video launched January 2018 as a call for collaboration; beads strung into a portrait based on Kali Spitzer’s photograph Sister", "url": "https://collegefund.org/blog/native-artist-to-debut-crowdsourced-art-project-highlighting-murdered-and-missing-indigenous-people/"}],
 notes="Title italic in print. Theme: arts. Bead counts differ by source (nearly 4,000; more than 4,000; four thousand cases), hence about 4,000.",
 rewrite="new subject (Cannupa Hanska Luger, Every One) replacing Gordon Parks; one example pins participatory, no widely celebrated ... remarkably frame"),
}
with open(path + ".lock", "w") as lock:
    fcntl.flock(lock, fcntl.LOCK_EX)
    d = json.load(open(path))
    done = []
    for it in d["items"]:
        k = it["id"].split(".", 1)[1]
        if k not in P:
            continue
        if it.get("rewrite"):
            print("skip, already rewritten", k); continue
        opts, key = O[k]
        e = E[k]
        it["passage"] = P[k]
        it["options"] = opts
        it["answer_letter"] = key
        it["explanation"] = e["explanation"]
        it["distractors"] = {L: {"recipe": r, "why_wrong": w} for L, (r, w) in sorted(e["d"].items())}
        assert sorted(it["distractors"]) == sorted(set("ABCD") - {key}), k
        it["word_count"] = len(P[k].split())
        it["sources"] = e["sources"]
        it["notes"] = e["notes"]
        it["rewrite"] = e["rewrite"]
        it["review"] = None
        done.append(k)
    json.dump(d, open(path, "w"), indent=2, ensure_ascii=False)
print("updated", done)
