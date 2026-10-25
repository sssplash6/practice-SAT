import fcntl, json, sys, os
sys.path.insert(0, os.path.dirname(__file__))
from items import ITEMS
path = "satbank/rw/transitions.json"
with open(path + ".lock", "w") as lock:
    fcntl.flock(lock, fcntl.LOCK_EX)
    d = json.load(open(path))
    done = 0
    for it in d["items"]:
        k = it["id"].split(".", 1)[1]
        if k not in ITEMS:
            continue
        new = ITEMS[k]
        it.update(new)
        it["word_count"] = len(new["passage"].replace("______", "").split())
        it["review"] = None
        done += 1
    assert done == 15, done
    json.dump(d, open(path, "w"), indent=2, ensure_ascii=False)
print("updated", done)
