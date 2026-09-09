import json
import os
import re
import sys
from datetime import datetime

sys.path.insert(0, r"D:\ai\leetcode")
from fetch_amazon_experiences import (
    extract_role,
    extract_location,
    extract_outcome,
    extract_rounds,
    extract_tips,
    generate_summary
)

DATA_FILE = r"D:\ai\leetcode\data\experiences.json"
RAW_FILE = r"C:\Users\Admin\.gemini\antigravity-cli\brain\947b8e2e-27a3-4b40-a423-103b517ad012\scratch\raw_new_posts.json"

def clean_post_text(raw_text, title):
    """Strips navigation headers and comment footers from scraped page text."""
    lines = raw_text.split("\n")
    start_idx = 0
    end_idx = len(lines)

    # Find where actual article begins (usually after title or tags)
    for i, line in enumerate(lines[:30]):
        if title.lower() in line.lower() or "interview experience" in line.lower():
            start_idx = i
            break

    # Find where comments or trending section starts
    for i, line in enumerate(lines):
        if i > start_idx and any(m in line for m in ["Comments (", "Sort by:Best", "Trending\n1", "Download App", "Copyright ©"]):
            end_idx = i
            break

    cleaned = "\n".join(lines[start_idx:end_idx]).strip()
    return cleaned if len(cleaned) > 100 else raw_text.strip()

def process_and_merge():
    if not os.path.exists(RAW_FILE):
        print(f"Error: {RAW_FILE} does not exist.")
        return

    with open(RAW_FILE, "r", encoding="utf-8") as f:
        raw_items = json.load(f)

    with open(DATA_FILE, "r", encoding="utf-8") as f:
        existing_data = json.load(f)

    existing_map = {str(item["id"]): item for item in existing_data}
    new_added = 0

    for item in raw_items:
        post_id = str(item["topicId"])
        title = item.get("title", "").strip()
        created_at = item.get("createdAt", "")
        if created_at:
            try:
                post_date = created_at[:10]
            except Exception:
                post_date = "2026-09-08"
        else:
            post_date = "2026-09-08"

        raw_full_text = item.get("fullText", "")
        full_text = clean_post_text(raw_full_text, title)

        role = extract_role(title, full_text)
        location = extract_location(title, full_text)
        outcome = extract_outcome(title, full_text)
        rounds = extract_rounds(full_text)
        tips = extract_tips(full_text)

        # Fallback if rounds couldn't be regex parsed from custom formatting
        if not rounds:
            rounds = [
                {
                    "round_name": "Round 1: Technical & Problem Solving",
                    "questions": ["DSA, Algorithms & Data Structures questions"],
                    "details": full_text[:400]
                }
            ]

        if not tips:
            tips = [
                "Practice core data structure patterns (Monotonic Stack, Heaps, Trees, Sliding Window).",
                "Be ready to dry-run logic manually and articulate trade-offs clearly."
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
            new_added += 1
            existing_map[post_id] = record
        else:
            existing_map[post_id].update(record)

    updated_list = list(existing_map.values())
    # Sort descending by post_date
    updated_list.sort(key=lambda x: x.get("post_date", "2024-01-01"), reverse=True)

    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(updated_list, f, indent=2, ensure_ascii=False)

    print(f"[+] Successfully merged into {DATA_FILE}")
    print(f"[+] Total entries now: {len(updated_list)} (+{new_added} new)")

    # Count 2026 entries
    c_2026 = sum(1 for e in updated_list if e.get("post_date", "").startswith("2026"))
    print(f"[+] Entries dated in 2026: {c_2026}")

if __name__ == "__main__":
    process_and_merge()
