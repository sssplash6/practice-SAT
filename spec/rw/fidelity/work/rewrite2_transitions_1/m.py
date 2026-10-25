import json, sys, statistics as s
sys.path.insert(0, '/Users/workingmyassof/freshbot/satbank/tools')
from check_rw import register
P = json.load(open(sys.argv[1]))
med = {'C1_two_subject.easy':41,'C2_belief_finding.easy':48,'C3_limiting_fact.easy':51,'E1_consequence.easy':48.5,'E2_motive_action.easy':54,'P1_purpose_aptness.easy':47,'A1_addition.easy':54,'X1_example.easy':50,'S1_spec_restate.easy':56,'M1_emphasis.easy':48,'T1_sequence_time.easy':56,'C1_two_subject.medium':44,'C2_belief_finding.medium':50.5,'E1_consequence.medium':56,'E2_motive_action.medium':60}
for tier in ('easy', 'medium'):
    rows = [(k, v) for k, v in P.items() if k.endswith(tier)]
    for k, v in rows:
        r = register(v); n=len(v.split())
        print(f"{k:28} {r[0]:.2f} {100*r[1]:4.1f}% {r[2]:5.1f}  n={n} med={med.get(k)} {'SHORT' if n<med.get(k,0) else ''}{'LONG' if n>66 else ''}")
    m = [s.mean(register(v)[i] for _, v in rows) for i in range(3)]
    print(f"== {tier}: {m[0]:.3f} {100*m[1]:.1f}% {m[2]:.1f}\n")
print("targets: easy 4.98 11.5% 33.2 | medium 5.34 15.3% 34.0")
