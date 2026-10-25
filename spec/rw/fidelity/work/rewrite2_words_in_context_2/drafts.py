"""Draft passages for words_in_context part 2; run from the repo root to measure register and length."""
import json
import statistics as s
import sys

sys.path.insert(0, "tools")
from check_rw import register  # noqa: E402

P = {
    "B5.medium": (
        "Measures of teacher quality derived solely from students’ standardized test scores are less ______ "
        "than they may appear, according to economist Kirabo Jackson. Analyzing data on North Carolina ninth "
        "graders, Jackson found that teachers’ effects on attendance, suspensions, and course grades were only "
        "weakly correlated with their effects on test scores, yet these behavioral effects were far stronger "
        "predictors of students’ long-term success in high school."
    ),
    "B6.medium": (
        "Placed in newspapers by enslavers hoping to recapture people who had escaped bondage, the fugitive "
        "slave advertisements now compiled in Cornell University’s Freedom on the Move database are, "
        "paradoxically, ______ resistance to slavery, each one documenting an individual’s flight and "
        "frequently describing the person’s appearance, clothing, mannerisms, and speech."
    ),
    "B1.hard": (
        "Vietnamese packs considerably more information into an average syllable than Basque does, yet when "
        "linguist Christophe Coupé and colleagues compared recordings of speakers of seventeen languages, they "
        "found that speech rate tends to ______ such differences in information density. Languages whose "
        "syllables carry relatively little information, such as Spanish, were spoken faster than those with "
        "information-dense syllables, and all seventeen conveyed information at roughly the same rate."
    ),
    "B2.hard": (
        "In a month-long experiment in small factories in Odisha, India, economists Emily Breza, Supreet Kaur, "
        "and Yogita Shamdasani found that paying the members of a work team different wages lowered the output "
        "of the lowest-paid members and the attendance even of the highest-paid. Yet where workers could plainly "
        "see that better-paid teammates were more productive, the disparity had no discernible effect: workers "
        "apparently objected to pay inequality chiefly when it seemed ______."
    ),
    "B3.hard": (
        "Some development economists have contended that distributing insecticide-treated bed nets free of "
        "charge, rather than at a subsidized price, is ______. Jessica Cohen and Pascaline Dupas found little "
        "to support that contention in Kenya. When they randomized the price at which prenatal clinics offered "
        "nets to pregnant women, recipients of free nets proved no less likely to use them than women who had paid."
    ),
    "B4.hard": (
        "Biologists Erik Duboué, Alex Keene, and Richard Borowsky have characterized sleep in the Mexican "
        "tetra Astyanax mexicanus as evolutionarily ______. Surface-dwelling populations of the fish sleep "
        "roughly thirteen hours a day, for instance, whereas three cave-dwelling populations, each derived "
        "independently from surface ancestors after colonizing dark, food-scarce caverns, have all come to "
        "sleep only two to four hours."
    ),
    "B5.hard": (
        "A smudged margin in a late medieval prayer book might be dismissed as mere damage, but for art "
        "historian Kathryn Rudy such grime is far from ______. Measuring with a densitometer how much darker "
        "certain pages are than others, Rudy has identified the devotional texts that individual readers "
        "handled most intensively; one owner evidently returned repeatedly to suffrages (brief petitionary "
        "prayers) to Saints Sebastian and Adrian, intercessors believed to ward off plague."
    ),
    "B6.hard": (
        "Populations of the mosquito Aedes aegypti that strongly prefer human odor to the odor of other "
        "animals are concentrated in African regions with intense dry seasons, such as the Sahel, where "
        "rainfall is confined to a few months annually. Biologists Noah Rose, Carolyn McBride, and colleagues "
        "propose that the species’ predilection for human hosts originally evolved as ______ its reliance on "
        "water stored by people, which allows the mosquitoes to breed throughout the protracted dry season."
    ),
    "M1.hard": (
        "The following text is from Arnold Bennett’s 1908 novel The Old Wives’ Tale. Sophia keeps a "
        "boardinghouse in Paris during the 1870–71 siege of the city.\n\nSophia might have fed her flock "
        "without resorting to the official rations, but she would not sacrifice the <u>economy</u> which they "
        "represented. She demanded thick clothes for the concierge’s boy, and received boots from Chirac, gloves "
        "from Carlier, and a great overcoat from Niepce. The weather increased in severity, and provisions in price."
    ),
}

if __name__ == "__main__":
    for k, p in P.items():
        r = register(p)
        print(f"{k:10} chars {r[0]:.2f} long {r[1]:.3f} wps {r[2]:.1f} words {len(p.split())}")
    d = {i["id"].split(".", 1)[1]: i for i in json.load(open("satbank/rw/words_in_context.json"))["items"]}
    med = [register(P[k]) for k in ("B5.medium", "B6.medium")] + [register(d[k]["passage"]) for k in ("M1.medium", "M2.medium")]
    hard = [register(P[k]) for k in P if k.endswith("hard")]
    print("MEDIUM mine", [round(s.mean(x[i] for x in med), 3) for i in range(3)], "CB 5.30 .171 27.8")
    print("HARD mine", [round(s.mean(x[i] for x in hard), 3) for i in range(3)], "CB 5.25 .157 31.2")
