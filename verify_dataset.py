import json
import os
import sys

DATA_FILE = r"D:\Ai\leetcode\data\experiences.json"

if not os.path.exists(DATA_FILE):
    print(f"Error: {DATA_FILE} does not exist.")
    sys.exit(1)

with open(DATA_FILE, "r", encoding="utf-8") as f:
    data = json.load(f)

print(f"Total entries: {len(data)}")

required_fields = [
    ("id", str),
    ("title", str),
    ("role", str),
    ("location", str),
    ("outcome", str),
    ("post_date", str),
    ("url", str),
    ("author", str),
    ("votes", int),
    ("views", int),
    ("tags", list),
    ("rounds", list),
    ("summary", str),
    ("tips", list),
    ("full_text", str)
]

errors = 0
for idx, entry in enumerate(data):
    for field, expected_type in required_fields:
        if field not in entry:
            print(f"Record {idx} missing field {field}")
            errors += 1
        elif not isinstance(entry[field], expected_type):
            print(f"Record {idx} field {field} expected {expected_type} got {type(entry[field])}")
            errors += 1
    # Check rounds structure
    for r in entry.get("rounds", []):
        if not isinstance(r, dict) or "round_name" not in r or "questions" not in r or "details" not in r:
            print(f"Record {idx} invalid round structure: {r}")
            errors += 1

if errors == 0:
    print("[SUCCESS] All entries strictly match the required schema!")
else:
    print(f"[FAIL] Found {errors} schema errors.")

# Display date range
dates = [e["post_date"] for e in data if "post_date" in e]
print(f"Date range: {min(dates)} to {max(dates)}")

# Sample entry preview
print("\n--- Sample Entry 1 Preview ---")
sample = data[0]
for k in ["id", "title", "role", "location", "outcome", "post_date", "author", "votes", "views"]:
    print(f"  {k}: {sample.get(k)}")
print(f"  tags ({len(sample.get('tags', []))}): {sample.get('tags')[:5]}")
print(f"  rounds count: {len(sample.get('rounds', []))}")
for i, r in enumerate(sample.get("rounds", [])[:2]):
    print(f"    Round {i+1}: {r.get('round_name')} | Questions: {r.get('questions')[:2]}")
print(f"  summary: {sample.get('summary')}")
print(f"  tips ({len(sample.get('tips', []))}): {sample.get('tips')[:2]}")
print(f"  full_text length: {len(sample.get('full_text', ''))} chars")
