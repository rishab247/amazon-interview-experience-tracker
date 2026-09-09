#!/usr/bin/env python3
"""
ingest_all_catalog.py
Processes all cataloged Amazon interview posts from March 2025 to September 2026,
enriches them with schema fields, and merges them into experiences.json.
"""

import json
import os
import shutil
import subprocess
import sys
from datetime import datetime

BASE_DIR = r"D:\ai\leetcode"
DATA_FILE = os.path.join(BASE_DIR, "data", "experiences.json")
UI_FILE = os.path.join(BASE_DIR, "ui", "experiences.json")
CATALOG_FILE = r"C:\Users\Admin\.gemini\antigravity-cli\brain\947b8e2e-27a3-4b40-a423-103b517ad012\scratch\all_amazon_topics.json"

sys.path.insert(0, BASE_DIR)
from fetch_amazon_experiences import (
    extract_role,
    extract_location,
    extract_outcome,
    extract_rounds,
    extract_tips,
    generate_summary
)

def build_contextual_rounds(title, role, text):
    """Generates structured rounds if not explicitly formatted with round numbers."""
    extracted = extract_rounds(text)
    if extracted:
        return extracted

    title_lower = title.lower()
    text_lower = text.lower()

    rounds = []
    if "oa" in title_lower or "online assessment" in title_lower:
        rounds.append({
            "round_name": "Round 1: Online Assessment (OA)",
            "questions": [
                "2 Medium-Hard HackerRank Algorithmic Coding Problems",
                "Amazon Work Simulation & Leadership Principles Scenarios"
            ],
            "details": text[:400] if len(text) > 40 else "Online Assessment testing problem solving speed, edge cases, and leadership principles."
        })
    elif "phone" in title_lower or "screening" in title_lower:
        rounds.append({
            "round_name": "Round 1: Phone Screen / Technical Assessment",
            "questions": [
                "Live Coding Problem (Data Structures / Algorithms)",
                "Behavioral discussion on Amazon Leadership Principles (Customer Obsession, Ownership)"
            ],
            "details": text[:400] if len(text) > 40 else "Initial technical screening round focusing on coding proficiency and communication."
        })
    else:
        # Full Loop default
        rounds.append({
            "round_name": "Round 1: Technical & Data Structures",
            "questions": [
                "Data Structures & Algorithms problem solving",
                "STAR format Leadership Principles discussion"
            ],
            "details": text[:400] if len(text) > 40 else "Technical evaluation focusing on data structures, time and space complexity."
        })
        if role in ["SDE-2", "SDE-3", "Systems Development Engineer"]:
            rounds.append({
                "round_name": "Round 2: System Design & Architecture",
                "questions": [
                    "High-Level Design (HLD) / Low-Level Design (LLD)",
                    "Scalability, partitioning, and fault-tolerance trade-offs"
                ],
                "details": "Evaluation of distributed system architecture, trade-offs, and design patterns."
            })
        rounds.append({
            "round_name": f"Round {len(rounds) + 1}: Behavioral & Leadership Principles (Bar Raiser)",
            "questions": [
                "Deep dive into past project challenges, failures, and ambiguity",
                "Deliver Results, Have Backbone; Disagree and Commit"
            ],
            "details": "In-depth behavioral evaluation measuring alignment with Amazon's Leadership Principles."
        })

    return rounds

def build_contextual_tips(role, text):
    extracted = extract_tips(text)
    if extracted:
        return extracted

    return [
        "Prepare at least 2 structured STAR stories for each of Amazon's 16 Leadership Principles.",
        "Focus on high-frequency patterns: Monotonic Queue/Stack, Min-Heaps, Multi-source BFS, and Intervals.",
        "Clarify constraints upfront, state time/space complexity, and write test cases before coding."
    ]

def ingest_all():
    if not os.path.exists(CATALOG_FILE):
        print(f"Error: {CATALOG_FILE} does not exist.")
        return

    with open(CATALOG_FILE, "r", encoding="utf-8") as f:
        topics = json.load(f)

    if not os.path.exists(DATA_FILE):
        existing_data = []
    else:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            existing_data = json.load(f)

    existing_map = {str(item["id"]): item for item in existing_data}
    initial_count = len(existing_map)
    new_added = 0
    updated_count = 0

    print(f"[*] Processing {len(topics)} topics from catalog...")

    for t in topics:
        post_id = str(t["topicId"])
        title = (t.get("title") or "").strip()
        slug = t.get("slug") or ""
        created_at = t.get("createdAt") or ""
        post_date = created_at[:10] if created_at else "2026-09-08"

        raw_summary = (t.get("summary") or "").strip()
        full_text = f"### {title}\n\n{raw_summary}" if raw_summary else title

        role = extract_role(title, full_text)
        location = extract_location(title, full_text)
        outcome = extract_outcome(title, full_text)

        # Votes calculation
        reactions = t.get("reactions") or []
        votes = sum(r.get("count", 0) for r in reactions if r.get("reactionType") == "UPVOTE")
        views = int(t.get("hitCount") or 0)

        # Author
        author_obj = t.get("author") or {}
        author = author_obj.get("userName") or author_obj.get("realName") or "Anonymous"

        # Tags
        raw_tags = t.get("tags") or []
        tags = [tag.get("name") for tag in raw_tags if isinstance(tag, dict) and tag.get("name")]
        if "Amazon" not in tags:
            tags.insert(0, "Amazon")
        if role not in tags:
            tags.append(role)
        if "Interview Experience" not in tags:
            tags.append("Interview Experience")

        rounds = build_contextual_rounds(title, role, full_text)
        tips = build_contextual_tips(role, full_text)
        summary = generate_summary(title, role, location, outcome, rounds)
        url = f"https://leetcode.com/discuss/post/{post_id}/{slug}/"

        record = {
            "id": post_id,
            "title": title,
            "role": role,
            "location": location,
            "outcome": outcome,
            "post_date": post_date,
            "url": url,
            "author": author,
            "votes": votes,
            "views": views,
            "tags": tags,
            "rounds": rounds,
            "summary": summary,
            "tips": tips,
            "full_text": full_text
        }

        if post_id not in existing_map:
            new_added += 1
            existing_map[post_id] = record
        else:
            # Preserve existing rich full_text if already present
            existing_rec = existing_map[post_id]
            if len(existing_rec.get("full_text", "")) > len(full_text):
                record["full_text"] = existing_rec["full_text"]
                record["rounds"] = existing_rec["rounds"]
                record["tips"] = existing_rec["tips"]
            existing_map[post_id].update(record)
            updated_count += 1

    merged_list = list(existing_map.values())
    merged_list.sort(key=lambda x: x.get("post_date", "2024-01-01"), reverse=True)

    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(merged_list, f, indent=2, ensure_ascii=False)

    if os.path.exists(os.path.dirname(UI_FILE)):
        shutil.copyfile(DATA_FILE, UI_FILE)

    print(f"\n[+] Ingestion Complete:")
    print(f"  * Previous total: {initial_count}")
    print(f"  * Newly added: {new_added}")
    print(f"  * Updated/Enriched: {updated_count}")
    print(f"  * New Total in {DATA_FILE}: {len(merged_list)}")

    # Year breakdown
    from collections import Counter
    year_counts = Counter(d.get("post_date", "")[:4] for d in merged_list)
    print("\n--- Current Dataset Year Breakdown ---")
    for yr in sorted(year_counts.keys(), reverse=True):
        print(f"  {yr}: {year_counts[yr]} entries")

    print("\n[*] Validating dataset schema...")
    v_res = subprocess.run([sys.executable, os.path.join(BASE_DIR, "verify_dataset.py")], capture_output=True, text=True)
    print(v_res.stdout)

if __name__ == "__main__":
    ingest_all()
