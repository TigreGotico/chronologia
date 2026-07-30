import json, glob

ROOT = "/home/miro/AgentWorkspaces/ml/chronologia/.claude/worktrees/agent-a8c59544fa130a9d1"

MIGRATED = {
    "named_day": ["DAY_WORD"],
    "iso_date": ["ISO"],
    "iso_week_date": ["ISOWEEK"],
    "numeric_date": ["NUMDATE"],
    "named_period": ["in? during? article? PART? PERIOD"],
    "weekday_offset": ["indef? QUANT? UNIT from WEEKDAY", "indef? NUM UNIT from WEEKDAY"],
    "named_day_after": ["article? indef? UNIT after DAY_WORD"],
    "named_day_before": ["article? indef? UNIT before DAY_WORD"],
}

removed = 0
changed_files = 0
for f in sorted(glob.glob(ROOT + "/chronologia/locale/*/lang.json")):
    d = json.load(open(f))
    cons = d.get("constructions", {})
    touched = False
    for name, expect in MIGRATED.items():
        if name in cons:
            body = cons[name]
            flags = {k: v for k, v in body.items() if k != "orders"}
            if not flags and sorted(body.get("orders", [])) == sorted(expect):
                del cons[name]
                removed += 1
                touched = True
    if touched:
        changed_files += 1
        with open(f, "w") as fh:
            json.dump(d, fh, indent=2, ensure_ascii=False)
            fh.write("\n")

print("removed", removed, "duplicate blocks across", changed_files, "files")
