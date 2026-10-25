"""Write the part-2 rewrites of words_in_context into satbank/rw/words_in_context.json under the lock."""
import fcntl
import json
import re

PATH = "satbank/rw/words_in_context.json"
PFX = "words_in_context."


def wc(p: str) -> int:
    return sum(1 for t in p.split() if re.search(r"[A-Za-z0-9]", t))


NEW = {
    "B5.medium": {
        "passage": "Value-added measures of teacher quality, which typically rely solely on students’ standardized test scores, are less ______ than they may appear, according to economist Kirabo Jackson. Analyzing records of North Carolina ninth graders, Jackson found that teachers’ effects on absences, suspensions, and course grades were only weakly correlated with their test-score effects, yet these behavioral effects predicted students’ eventual high school graduation considerably better.",
        "options": ["limited", "replicable", "contentious", "comprehensive"],
        "answer_letter": "D",
        "explanation": "Jackson found that teachers’ effects on absences, suspensions and grades barely track their effects on test scores, yet predict graduation much better. A measure built only on test scores therefore leaves out an important part of what teachers do: it is less comprehensive than it may appear.",
        "distractors": {
            "A": {"recipe": "reversal", "why_wrong": "Calling the measures less limited than they appear would mean they capture more than expected, but Jackson’s finding shows they miss the behavioral effects that best predict graduation."},
            "B": {"recipe": "plausible but unsupported", "why_wrong": "Nothing in the text concerns whether the measures give the same results when repeated; the finding is about what test scores leave out."},
            "C": {"recipe": "plausible but unsupported", "why_wrong": "The text says nothing about how much debate these measures provoke; it reports what they fail to capture."},
        },
        "sources": [
            {"what": "Jackson, What Do Test Scores Miss? (NBER WP 22226, JPE 2018): extends test-score value-added; teachers affect absences, suspensions, course grades and grade progression; 9th-grade effects predict high-school completion beyond test-score effects", "url": "https://www.nber.org/papers/w22226"},
            {"what": "Same paper, full text: North Carolina 9th-grade cohorts; correlations of test-score effects with effects on suspensions and absences below 0.1, with GPA 0.22; 1 SD behavior effect raises graduation 1.47 points vs 0.12 for test-score value-added", "url": "https://www.nber.org/system/files/working_papers/w22226/w22226.pdf"},
            {"what": "Northwestern IPR summary: data on 9th-grade students in North Carolina; non-cognitive effects far more predictive of long-term success in high school; teachers who raise test scores often do not improve behaviors", "url": "https://www.ipr.northwestern.edu/news/2018/jackson-test-scores.html"},
        ],
        "notes": "",
        "rewrite": "New subject (Kirabo Jackson, teacher effects beyond test scores) replacing the famous Vivian Maier story; colon list and round figures gone; denser register; new options and key.",
    },
    "B6.medium": {
        "passage": "Placed in newspapers by enslavers hoping to recapture people who had escaped bondage, the fugitive slave advertisements now compiled in Cornell University’s Freedom on the Move database constitute, paradoxically, ______ resistance to slavery, each one documenting an individual’s flight and frequently describing the person’s appearance, clothing, mannerisms, and speech.",
        "options": ["a justification for", "a testament to", "an impediment to", "a misreading of"],
        "answer_letter": "B",
        "explanation": "“Paradoxically” sets the ads’ purpose, helping enslavers recapture people, against what they are now: each one documents a person’s flight from slavery. A collection of documented escapes bears witness to resistance, so the ads are a testament to it.",
        "distractors": {
            "A": {"recipe": "plausible but unsupported", "why_wrong": "The ads record escapes, but nothing suggests they argue that resisting slavery was justified; they were written by enslavers trying to undo those escapes."},
            "C": {"recipe": "reversal (the trait of the wrong party)", "why_wrong": "Impeding escape was the enslavers’ aim, which is why the text calls the ads’ present role paradoxical; as records of flight, they now bear witness to resistance."},
            "D": {"recipe": "plausible but unsupported", "why_wrong": "Nothing in the text says the ads misinterpret resistance; they simply document individual escapes and describe the people who fled."},
        },
        "sources": [
            {"what": "Freedom on the Move: Cornell-led database of fugitive slave ads placed in newspapers by enslavers trying to locate fugitives; ads include details of appearance, mannerisms, clothing, speech", "url": "https://news.cornell.edu/node/308201"},
            {"what": "The ads as records of enslaved people liberating themselves; enslavers placed them to recover people they claimed as property", "url": "https://hyperallergic.com/freedom-on-the-move/"},
        ],
        "notes": "",
        "rewrite": "New subject (Freedom on the Move fugitive slave ad database) replacing the schoolbook Erie Canal story and its famous quotes; no explanatory since clause; one dense sentence with a participial clue; new options and key.",
    },
    "B1.hard": {
        "passage": "Vietnamese packs considerably more information into an average syllable than Basque does, yet when linguist Christophe Coupé and colleagues compared recordings of speakers of seventeen languages, they found that speech rate tends to ______ such differences in information density. Languages whose syllables carry relatively little information, such as Spanish, were spoken faster than those with information-dense syllables, and all seventeen conveyed information at roughly the same rate.",
        "options": ["amplify", "offset", "outpace", "dictate"],
        "answer_letter": "B",
        "explanation": "The second sentence shows the trade-off: languages with information-light syllables are spoken faster, and all seventeen end up conveying information at about the same rate. Faster speech makes up for less information per syllable, so speech rate tends to offset differences in information density.",
        "distractors": {
            "A": {"recipe": "reversal", "why_wrong": "If speech rate amplified the differences, information-dense languages would also be the fast ones and their rates would pull further apart, but the text says the light languages are faster and the rates come out about equal."},
            "C": {"recipe": "topic echo", "why_wrong": "“Outpace” suits a text about speed, but the point is not that speech rate moves faster than differences in density; it is that the two balance each other."},
            "D": {"recipe": "plausible but unsupported", "why_wrong": "The text reports that speech rate and information density trade off, not that speech rate determines how much information a language packs into its syllables."},
        },
        "sources": [
            {"what": "Coupé, Oh, Dediu, Pellegrino 2019 (Science Advances): 17 languages, 10 native speakers each reading the same texts; higher speech rates matched by lower information densities (Spanish fast and information-light, Vietnamese and Chinese slower and dense); about 39 bits/s in every language", "url": "https://www.cnrs.fr/en/press/similar-information-rates-across-languages-despite-divergent-speech-rates"},
            {"what": "Paper full text: information density from 4.8 bits per syllable for Basque to 8.0 for Vietnamese; languages more similar in information rate than in density or speech rate", "url": "https://pmc.ncbi.nlm.nih.gov/articles/PMC6984970/"},
        ],
        "notes": "",
        "rewrite": "New subject (Coupé et al. 2019, similar information rates across languages) replacing Granovetter’s weak ties; clue moved to a separate sentence instead of an explanatory colon; new options and key.",
    },
    "B2.hard": {
        "passage": "In a month-long experiment in small factories in Odisha, India, economists Emily Breza, Supreet Kaur, and Yogita Shamdasani found that paying the members of a work team different wages lowered the output of the lowest-paid members and the attendance even of the highest-paid. Yet where workers could plainly see that better-paid teammates were more productive, the disparity had no discernible effect: workers apparently objected to pay inequality chiefly when it seemed ______.",
        "options": ["unwarranted", "merited", "entrenched", "conspicuous"],
        "answer_letter": "A",
        "explanation": "Unequal pay hurt output and attendance except where workers could see that better-paid teammates really were more productive. Inequality with a visible reason did no harm, so workers objected to it when it seemed unwarranted.",
        "distractors": {
            "B": {"recipe": "reversal", "why_wrong": "Pay differences that seemed merited, backed by visibly higher productivity, are exactly the ones that had no discernible effect."},
            "C": {"recipe": "plausible but unsupported", "why_wrong": "Nothing in the text concerns how long-standing the pay differences were; what decided the effect was whether productivity differences could be seen."},
            "D": {"recipe": "wrong nuance", "why_wrong": "Visibility matters in the study, but it is the visibility of teammates’ productivity that removed the effect; nothing suggests workers objected because the pay gap itself was obvious."},
        },
        "sources": [
            {"what": "Breza, Kaur, Shamdasani, The Morale Effects of Pay Inequality (NBER WP 22491, QJE 2018): month-long experiment, 378 workers in small factories in Odisha; output of workers paid less than both co-workers fell; highest- and median-wage workers in pay-disparity units also had lower attendance; no discernible effect when workers could clearly observe productivity differences; fairness violations only when the rationale for pay differences is unclear", "url": "https://www.nber.org/system/files/working_papers/w22491/w22491.pdf"},
        ],
        "notes": "",
        "rewrite": "New subject (Breza, Kaur and Shamdasani pay-inequality experiment) replacing the Jevons paradox; key now needs an inference from the observability result instead of a spelled-out causal chain; new options and key.",
    },
    "B3.hard": {
        "passage": "Some development experts have contended that distributing insecticide-treated bed nets free of charge, rather than at a subsidized price, is ______. Economists Jessica Cohen and Pascaline Dupas found little to support that contention in Kenya. When they randomized the price at which prenatal clinics offered nets to pregnant women, recipients of free nets proved no less likely to use them than women who had paid.",
        "options": ["unsustainable", "wasteful", "cost-effective", "premature"],
        "answer_letter": "B",
        "explanation": "The evidence that undercuts the contention is that free nets were used as often as paid-for ones, so the contention must have been that free nets would go unused. Giving away nets that people will not use is wasteful.",
        "distractors": {
            "A": {"recipe": "wrong nuance", "why_wrong": "Cost to donors is a real objection to free distribution, but evidence about whether women used their nets says nothing about whether such programs can be funded, so it could not undercut that claim."},
            "C": {"recipe": "reversal", "why_wrong": "Finding that free nets are used as much as purchased ones would support the view that free distribution is cost-effective, yet the text says the researchers found little to support the contention."},
            "D": {"recipe": "plausible but unsupported", "why_wrong": "Nothing in the text concerns timing; the study tests whether people who get free nets use them."},
        },
        "sources": [
            {"what": "Cohen and Dupas, Free Distribution or Cost-Sharing? (NBER WP 14406; QJE 2010): it is often argued that cost-sharing is needed to avoid wasting products on people who will not use them; prices randomized at prenatal clinics in Kenya selling ITNs to pregnant women; women who received free nets were not less likely to use them", "url": "https://www.nber.org/papers/w14406"},
            {"what": "Published version in the Quarterly Journal of Economics 125(1)", "url": "https://academic.oup.com/qje/article/125/1/1/1880392"},
        ],
        "notes": "",
        "rewrite": "New subject (Cohen and Dupas bed-net pricing trial) replacing Hardin and Ostrom; key derived from the contrast with the finding, no example list; new options and key.",
    },
    "B4.hard": {
        "passage": "Biologists Erik Duboué, Alex Keene, and Richard Borowsky have characterized sleep in the Mexican tetra Astyanax mexicanus as evolutionarily ______. Surface-dwelling populations of the fish sleep roughly thirteen hours a day, for instance, whereas three cave-dwelling populations, each derived independently from surface ancestors after colonizing dark, food-scarce caverns, have all come to sleep only two to four hours.",
        "options": ["vestigial", "conserved", "malleable", "erratic"],
        "answer_letter": "C",
        "explanation": "The example shows sleep in one species changing drastically, from about thirteen hours to two to four, and doing so separately in three cave populations. A trait that evolution reshapes this readily, and more than once, is malleable.",
        "distractors": {
            "A": {"recipe": "plausible but unsupported", "why_wrong": "A vestigial trait is a leftover that has lost its function, but nothing in the text suggests sleep has lost its function; the cave fish still sleep, only less."},
            "B": {"recipe": "reversal", "why_wrong": "An evolutionarily conserved trait stays much the same across related populations, but sleep in this species differs sharply between surface and cave populations."},
            "D": {"recipe": "wrong nuance", "why_wrong": "The amount of sleep did change, but not unpredictably: three populations that colonized similar caves each arrived at the same short sleep."},
        },
        "sources": [
            {"what": "Duboué, Keene, Borowsky 2011, Evolutionary convergence on sleep loss in cavefish populations (Current Biology, DOI 10.1016/j.cub.2011.03.020): dramatic reduction in sleep in three independently derived cave populations; sleep is an evolutionarily labile phenotype", "url": "https://europepmc.org/article/MED/21474315"},
            {"what": "NYU researchers; Pachón, Tinaja and Molino cave populations; surface fish over 800 minutes of sleep a day, cavefish 110 to 250", "url": "https://www.sciencedaily.com/releases/2011/04/110407121322.htm"},
            {"what": "Surface fish about 13 hours, cavefish 2 to 4 hours; populations lost sleep independently; caves where food is scarce", "url": "https://www.nationalgeographic.com/science/article/sleepless-in-mexico-three-cavefish-groups-independently-evolved-to-lose-sleep"},
        ],
        "notes": "The paper’s own word is “labile”; the key paraphrases it.",
        "rewrite": "New subject (convergent sleep loss in Astyanax cavefish) replacing the textbook four origins of flight; no strikingly opener or colon list; example sentence carries the clue; new options and key.",
    },
    "B5.hard": {
        "passage": "A smudged margin in a late medieval prayer book might be dismissed as mere damage, but for art historian Kathryn Rudy such grime is far from ______. Measuring with a densitometer how much darker certain pages are than others, Rudy has identified the devotional texts that individual readers handled most intensively; one owner, for instance, evidently returned repeatedly to invocations of Saints Sebastian and Adrian, reputed protectors against plague.",
        "options": ["informative", "unsightly", "extraneous", "irreparable"],
        "answer_letter": "C",
        "explanation": "“But” sets Rudy against the view that grime is mere damage, and the next sentence shows her using it as evidence of which prayers readers handled most. Grime that reveals how a book was used is far from extraneous to its study.",
        "distractors": {
            "A": {"recipe": "reversal", "why_wrong": "Rudy uses the grime to identify the prayers readers favored, so it is highly informative; calling it far from informative contradicts the rest of the text."},
            "B": {"recipe": "wrong nuance", "why_wrong": "The contrast with “mere damage” might suggest appearance, but the text is about the grime’s value as evidence, not how it looks; a smudged margin is, if anything, unsightly."},
            "D": {"recipe": "plausible but unsupported", "why_wrong": "Nothing in the text concerns whether the damage could be repaired; Rudy measures the grime rather than removing it."},
        },
        "sources": [
            {"what": "Rudy, Dirty Books: Quantifying Patterns of Use in Medieval Manuscripts Using a Densitometer (JHNA 2, 2010): densitometer measures darkness of handled pages as an index of use; in Ms. 128 G 33 the reader heavily used the suffrages to Saints Sebastian and Adrian, two saints thought to ward off the bubonic plague", "url": "https://jhna.org/articles/dirty-books-quantifying-patterns-of-use-medieval-manuscripts-using-a-densitometer/"},
            {"what": "Rudy argues that cleaning the dirt from such books discards a cultural witness", "url": "https://www.medievalists.net/2012/04/dirty-books-quantifying-patterns-of-use-in-medieval-manuscripts-using-a-densitometer/"},
        ],
        "notes": "",
        "rewrite": "New subject (Kathryn Rudy’s densitometer study of grime in prayer books) replacing Gaudí’s hanging-chain model; “far from” frame instead of the borrowed “by no means”; new options and key.",
    },
    "B6.hard": {
        "passage": "Populations of the mosquito Aedes aegypti that strongly prefer human odor to the odor of other animals are concentrated in African regions with intense dry seasons, such as the Sahel. Biologists Noah Rose, Carolyn McBride, and colleagues propose that the species’ predilection for human hosts originally evolved as ______ its reliance on water stored by people, which allows the mosquitoes to breed throughout the protracted dry season.",
        "options": ["an alternative to", "a safeguard against", "a hindrance to", "a by-product of"],
        "answer_letter": "D",
        "explanation": "Human preference is concentrated where dry seasons are intense, and stored water is what lets the mosquitoes breed through the dry season there. The researchers therefore trace the taste for humans to the reliance on stored water: it originally arose as a by-product of that reliance.",
        "distractors": {
            "A": {"recipe": "wrong nuance", "why_wrong": "An alternative would take the place of the reliance on stored water, but the text finds human preference exactly where mosquitoes depend on stored water; the two go together."},
            "B": {"recipe": "plausible but unsupported", "why_wrong": "Nothing suggests that preferring humans protects mosquitoes from depending on stored water; the text presents that dependence as what lets them breed in the dry season."},
            "C": {"recipe": "reversal", "why_wrong": "The text links human preference and reliance on stored water positively, since both occur where dry seasons are intense; nothing suggests the preference gets in the way of that reliance."},
        },
        "sources": [
            {"what": "Rose, ..., McBride 2020, Climate and Urbanization Drive Mosquito Preference for Humans (Current Biology 30(18)): Aedes aegypti from 27 sites in sub-Saharan Africa; preference for human vs animal odor predicted by dry-season intensity and human density; human-biting originally evolved as a by-product of breeding in human-stored water", "url": "https://collaborate.princeton.edu/en/publications/climate-and-urbanization-drive-mosquito-preference-for-humans/"},
            {"what": "Strong preference for human hosts only where dry seasons are intense, notably the Sahel, where rainfall is concentrated in a couple of months; dependence on human water storage", "url": "https://www.genengnews.com/news/mosquitoes-preference-to-bite-humans-traced-to-climate/"},
        ],
        "notes": "",
        "rewrite": "New subject (Aedes aegypti human preference and dry seasons, Rose and McBride 2020) replacing the viral 392-year Greenland shark; no clause that spells the key out; new options and key.",
    },
    "M1.hard": {
        "passage": "The following text is from Arnold Bennett’s 1908 novel The Old Wives’ Tale. Sophia keeps a boardinghouse in Paris during the 1870–71 siege of the city.\n\nSophia might have fed her flock without resorting to the official rations, but she would not sacrifice the <u>economy</u> which they represented. She demanded thick clothes for the concierge’s boy, and received boots from Chirac, gloves from Carlier, and a great overcoat from Niepce. The weather increased in severity, and provisions in price.",
        "rewrite": "Intro trimmed to one context sentence (no longer explains the boy and the rations); excerpt, options and key unchanged.",
    },
}

if __name__ == "__main__":
    with open(PATH + ".lock", "w") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        d = json.load(open(PATH))
        old_excerpt = None
        for it in d["items"]:
            k = it["id"][len(PFX):]
            if k not in NEW:
                continue
            if k == "M1.hard":
                old_excerpt = it["passage"].split("\n\n", 1)[1]
                assert old_excerpt == NEW[k]["passage"].split("\n\n", 1)[1], "excerpt changed"
            it.update(NEW[k])
            it["word_count"] = wc(it["passage"])
            it["review"] = None
        json.dump(d, open(PATH, "w"), indent=2, ensure_ascii=False)
    print("written", len(NEW))
