import json, glob
bad = []
for f in glob.glob("/home/miro/AgentWorkspaces/ml/chronologia/.claude/worktrees/agent-a8c59544fa130a9d1/chronologia/locale/*/lang.json"):
    try:
        json.load(open(f))
    except Exception as e:
        bad.append((f, e))
print("bad:", bad)
print("ok" if not bad else "FAIL")
