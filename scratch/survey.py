import json, glob
from collections import Counter, defaultdict

ROOT = "/home/miro/AgentWorkspaces/ml/chronologia/.claude/worktrees/agent-a8c59544fa130a9d1"

names = Counter()
orders_by_name = defaultdict(lambda: defaultdict(int))
for f in glob.glob(ROOT + "/chronologia/locale/*/lang.json"):
    lang = f.split('/')[-2]
    d = json.load(open(f))
    cons = d.get("constructions", {})
    for name, orders in cons.items():
        names[name] += 1
        key = tuple(sorted(orders)) if isinstance(orders, list) else json.dumps(orders, sort_keys=True)
        orders_by_name[name][key] += 1

base = {"scoped_ordinal", "weekday_ref", "rel_period", "season_ref", "half_period", "month_fuzzy", "daypart_ref"}
for name, cnt in names.most_common(60):
    if name in base:
        continue
    print(cnt, name, len(orders_by_name[name]), "distinct order-sets")
