import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

transcript_path = r"C:\Users\POOJA\.gemini\antigravity\brain\cef9b9c8-19bc-4ceb-88e4-0906a80277e8\.system_generated\logs\transcript_full.jsonl"

with open(transcript_path, "r", encoding="utf-8") as f:
    for line in f:
        obj = json.loads(line)
        if obj.get("step_index") == 55:
            content = obj.get("content", "")
            print(content)
            break
