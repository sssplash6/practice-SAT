import sys, statistics as st
sys.path.insert(0, '/Users/workingmyassof/freshbot/satbank/tools')
from check_rw import register
P = {
"B1.easy": "Historian Marisa J. Fuentes’s Dispossessed Lives (2016) examines eighteenth-century Bridgetown, Barbados, through the experiences of enslaved women whose lives survive in the colonial archive only in ______ form. Drawing on brief mentions in records kept by slave owners and colonial authorities, Fuentes reads these sources alongside black feminist theory to recover what the documents obscure.",
"B2.easy": "Grazing mammals can inadvertently ingest pea aphids along with the alfalfa on which the insects feed. Biologist Moshe Gish and colleagues found that the aphids detect the elevated heat and humidity of an approaching herbivore’s breath and drop off the plant en masse just before it is eaten, a response that allows most of the colony to ______.",
"B3.easy": "Ornithologists long regarded singing by female songbirds as ______, treating song as a trait that evolved primarily through competition among males for mates. A 2014 survey led by biologist Karan Odom, however, documented female song in 71 percent of the species examined and concluded that females also sang in the common ancestor of modern songbirds.",
"B4.easy": "Choreographer Michelle Dorrance often treats tap dancers as ______ as well as dancers. In ETM: Double Down, created with Nicholas Van Young, who designed its percussive electronic tap boards, every step triggers a sound, so the performers’ footwork generates the rhythmic loops and melodies of the evening’s score.",
"B5.easy": "In experiments by psychologists Juliana Schroeder and Nicholas Epley, evaluators who read transcripts of job candidates’ pitches judged the candidates less ______ than did evaluators who heard the same pitches aloud. Listeners rated the speakers as more competent and intelligent and expressed greater interest in hiring them, a difference the researchers traced to vocal cues such as pitch and pacing.",
"B6.easy": "Bark scorpion stings cause intense pain in house mice, rats, and humans, yet grasshopper mice regularly attack and consume the scorpions, grooming only briefly when stung. Biologist Ashlee Rowe and colleagues found that these predators are largely ______ the stings: in their pain-sensing neurons, a variant sodium channel binds the venom’s toxins and thereby blocks the pain signals the venom initiates.",
"B1.medium": "Velvet worms ensnare prey by ejecting a fluid slime that, when mechanically drawn, hardens into stiff biopolymeric fibers. Studying the species Euperipatoides rowelli, a team led by Matthew Harrington found that this transformation is ______: prolonged immersion in water dissolved the fibers, and regenerated fibers could be drawn from the resulting solution.",
"B2.medium": "An eleventh-century manuscript known as the Cambridge Songs preserves melodies for poems from Boethius’s Consolation of Philosophy, but only in neumes, signs that indicate melodic direction and details of vocal delivery without specifying every pitch. Musicologist Sam Barrett could thus ______ the songs only by consulting surviving notations in other manuscripts and testing his hypotheses in performance with singer Benjamin Bagby.",
"B3.medium": "Kiezdeutsch, a way of speaking that emerged among young people in multilingual urban neighborhoods in Germany, is often dismissed as broken German or as immigrants’ failed attempt to speak the standard language. Linguist Heike Wiese contends, however, that its departures from standard German are ______, conforming to grammatical regularities typical of Germanic languages.",
"B4.medium": "Much of the recent work of multidisciplinary artist Cannupa Hanska Luger is ______. For Every One (2018), he used an instructional video to invite communities across the United States and Canada to make clay beads, then assembled more than 4,000 of them, each honoring a missing or murdered Indigenous woman or girl, into a single installation.",
}
def show():
    for tier in ("easy", "medium"):
        rows = []
        for k, p in P.items():
            if k.endswith(tier):
                r = register(p); rows.append(r)
                print(k, len(p.split()), [round(x, 3) for x in r])
        print(tier, "mean", [round(st.mean(x[i] for x in rows), 3) for i in range(3)])
if __name__ == "__main__":
    show()
