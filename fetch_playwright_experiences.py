#!/usr/bin/env python3
"""
fetch_playwright_experiences.py
Automated pipeline to fetch live, modern Amazon interview experiences from LeetCode
using Playwright browser automation, parse and enrich schema fields, and merge into experiences.json.
"""

import json
import os
import shutil
import subprocess
import sys
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, "data", "experiences.json")
UI_FILE = os.path.join(BASE_DIR, "ui", "experiences.json")
RAW_FILE = os.path.join(BASE_DIR, "data", "raw_scraped.json")
CRAWLER_SCRIPT = os.path.join(BASE_DIR, "crawler.js")

sys.path.insert(0, BASE_DIR)
from fetch_amazon_experiences import (
    extract_role,
    extract_location,
    extract_outcome,
    extract_rounds,
    extract_tips,
    generate_summary
)

def clean_post_text(raw_text, title):
    lines = raw_text.split("\n")
    start_idx = 0
    end_idx = len(lines)

    for i, line in enumerate(lines[:30]):
        if title.lower() in line.lower() or "interview experience" in line.lower():
            start_idx = i
            break

    for i, line in enumerate(lines):
        if i > start_idx and any(m in line for m in ["Comments (", "Sort by:Best", "Trending\n1", "Download App", "Copyright ©"]):
            end_idx = i
            break

    cleaned = "\n".join(lines[start_idx:end_idx]).strip()
    return cleaned if len(cleaned) > 100 else raw_text.strip()

def run_crawler(limit=10):
    print(f"[*] Step 1: Running Playwright crawler for up to {limit} posts...")
    cmd = ["node", CRAWLER_SCRIPT, str(limit)]
    res = subprocess.run(cmd, cwd=BASE_DIR, capture_output=False)
    if res.returncode != 0:
        print("[-] Crawler exited with an error.")
        return False
    return True

def process_and_merge():
    print("[*] Step 2: Processing, enriching, and merging raw scraped posts...")
    if not os.path.exists(RAW_FILE):
        print(f"[-] Raw file not found: {RAW_FILE}")
        return

    with open(RAW_FILE, "r", encoding="utf-8") as f:
        raw_items = json.load(f)

    if not os.path.exists(DATA_FILE):
        existing_data = []
    else:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            existing_data = json.load(f)

    existing_map = {str(item["id"]): item for item in existing_data}
    new_count = 0

    for item in raw_items:
        post_id = str(item["topicId"])
        title = item.get("title", "").strip()
        created_at = item.get("createdAt", "")
        post_date = created_at[:10] if created_at else datetime.now().strftime("%Y-%m-%d")

        raw_full_text = item.get("fullText", "")
        full_text = clean_post_text(raw_full_text, title)

        role = extract_role(title, full_text)
        location = extract_location(title, full_text)
        outcome = extract_outcome(title, full_text)
        rounds = extract_rounds(full_text)
        tips = extract_tips(full_text)

        if not rounds:
            rounds = [
                {
                    "round_name": "Round 1: Technical & Problem Solving",
                    "questions": ["Data Structures & Algorithms problem", "Amazon Leadership Principles discussion"],
                    "details": full_text[:400]
                }
            ]

        if not tips:
            tips = [
                "Structure responses using the STAR method with quantified impact.",
                "Thoroughly practice Monotonic Stacks, Heaps, and Dynamic Programming."
            ]

        summary = generate_summary(title, role, location, outcome, rounds)

        tags = item.get("tags", [])
        if "Amazon" not in tags:
            tags.insert(0, "Amazon")
        if role not in tags:
            tags.append(role)
        if "Interview Experience" not in tags:
            tags.append("Interview Experience")

        record = {
            "id": post_id,
            "title": title,
            "role": role,
            "location": location,
            "outcome": outcome,
            "post_date": post_date,
            "url": item.get("url", f"https://leetcode.com/discuss/post/{post_id}/"),
            "author": item.get("author") or "Anonymous",
            "votes": int(item.get("votes", 0)),
            "views": int(item.get("views", 0)),
            "tags": tags,
            "rounds": rounds,
            "summary": summary,
            "tips": tips,
            "full_text": full_text
        }

        if post_id not in existing_map:
            new_count += 1
            existing_map[post_id] = record
        else:
            existing_map[post_id].update(record)

    merged_list = list(existing_map.values())
    merged_list.sort(key=lambda x: x.get("post_date", "2024-01-01"), reverse=True)

    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(merged_list, f, indent=2, ensure_ascii=False)

    if os.path.exists(os.path.dirname(UI_FILE)):
        shutil.copyfile(DATA_FILE, UI_FILE)

    print(f"[+] Successfully saved {len(merged_list)} records (+{new_count} newly added).")

    # Step 3: Run schema verification
    print("\n[*] Step 3: Verifying dataset schema...")
    v_res = subprocess.run([sys.executable, os.path.join(BASE_DIR, "verify_dataset.py")], capture_output=True, text=True)
    print(v_res.stdout)
    if v_res.returncode == 0:
        print("[SUCCESS] Pipeline completed successfully!")
    else:
        print("[-] Schema validation had issues:\n", v_res.stderr)

def main():
    limit = 10
    if len(sys.argv) > 1:
        try:
            limit = int(sys.argv[1])
        except ValueError:
            pass
    if run_crawler(limit):
        process_and_merge()

if __name__ == "__main__":
    main()
