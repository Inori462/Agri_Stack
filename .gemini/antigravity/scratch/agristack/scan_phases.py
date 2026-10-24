import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

transcript_path = r"C:\Users\POOJA\.gemini\antigravity\brain\cef9b9c8-19bc-4ceb-88e4-0906a80277e8\.system_generated\logs\transcript_full.jsonl"

with open(transcript_path, "r", encoding="utf-8") as f:
    for line in f:
        obj = json.loads(line)
        c = obj.get("content", "")
        for p in ["Phase 2:", "Phase 3:", "Phase 4:", "Phase 5:", "Phase 6:", "Phase 7:"]:
            if p in c and obj.get("source") == "MODEL":
                print(f"=== {p} at STEP {obj.get('step_index')} ===")
                lines = [l for l in c.split("\n") if l.strip().startswith("#") or "Summary" in l or "proceed" in l or "Phase" in l]
                print("\n".join(lines[:10]))
