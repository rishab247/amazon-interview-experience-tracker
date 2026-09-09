#!/usr/bin/env python3
"""
daily_sync.py
Automated daily synchronization pipeline for Amazon Interview Experiences.
Queries the LeetCode GraphQL API for new Amazon interview experiences, parses
and enriches the data, updates data/experiences.json & ui/experiences.json,
and dispatches notifications to Telegram via the Telegram Bot API.
"""

import argparse
import html
import json
import os
import re
import ssl
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import gzip
from datetime import datetime

# Configure UTF-8 encoding for stdout/stderr to prevent charmap errors on Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

# Optional requests import with fallback to urllib
try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

# Paths configuration
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
DATA_FILE = os.path.join(PROJECT_ROOT, "data", "experiences.json")
UI_FILE = os.path.join(PROJECT_ROOT, "ui", "experiences.json")

# LeetCode GraphQL configuration
LEETCODE_GRAPHQL_URL = "https://leetcode.com/graphql"
GRAPHQL_HEADERS = {
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept-Encoding": "gzip, deflate",
    "Referer": "https://leetcode.com/discuss/interview-experience",
    "Origin": "https://leetcode.com"
}

GRAPHQL_UGC_ARTICLES_QUERY = """
query ugcArticleDiscussionArticles($keywords: [String]!, $skip: Int, $first: Int) {
  ugcArticleDiscussionArticles(keywords: $keywords, skip: $skip, first: $first) {
    totalNum
    edges {
      node {
        topicId
        title
        summary
        createdAt
        tags {
          name
        }
      }
    }
  }
}
"""

GRAPHQL_UGC_ARTICLE_DETAIL_QUERY = """
query getDiscussPost($topicId: ID) {
  ugcArticleDiscussionArticle(topicId: $topicId) {
    uuid
    topicId
    title
    content
    summary
    createdAt
    hitCount
    tags {
      name
    }
    author {
      userName
      realName
    }
  }
}
"""

# Catalog of known LeetCode problem mappings
LC_NUM_MAP = {
    "1": ("Two Sum", "LeetCode 1", "Easy", "Arrays & Strings"),
    "3": ("Longest Substring Without Repeating Characters", "LeetCode 3", "Medium", "Sliding Window"),
    "4": ("Median of Two Sorted Arrays", "LeetCode 4", "Hard", "Binary Search"),
    "5": ("Longest Palindromic Substring", "LeetCode 5", "Medium", "Dynamic Programming"),
    "11": ("Container With Most Water", "LeetCode 11", "Medium", "Two Pointers"),
    "15": ("3Sum", "LeetCode 15", "Medium", "Two Pointers"),
    "20": ("Valid Parentheses", "LeetCode 20", "Easy", "Stack"),
    "21": ("Merge Two Sorted Lists", "LeetCode 21", "Easy", "Linked List"),
    "22": ("Generate Parentheses", "LeetCode 22", "Medium", "Backtracking"),
    "23": ("Merge k Sorted Lists", "LeetCode 23", "Hard", "Heap / Priority Queue"),
    "33": ("Search in Rotated Sorted Array", "LeetCode 33", "Medium", "Binary Search"),
    "42": ("Trapping Rain Water", "LeetCode 42", "Hard", "Two Pointers"),
    "49": ("Group Anagrams", "LeetCode 49", "Medium", "Arrays & Strings"),
    "53": ("Maximum Subarray (Kadane's)", "LeetCode 53", "Medium", "Dynamic Programming"),
    "56": ("Merge Intervals", "LeetCode 56", "Medium", "Intervals"),
    "70": ("Climbing Stairs", "LeetCode 70", "Easy", "Dynamic Programming"),
    "72": ("Edit Distance", "LeetCode 72", "Medium", "Dynamic Programming"),
    "76": ("Minimum Window Substring", "LeetCode 76", "Hard", "Sliding Window"),
    "79": ("Word Search", "LeetCode 79", "Medium", "Backtracking"),
    "88": ("Merge Sorted Array", "LeetCode 88", "Easy", "Arrays & Strings"),
    "98": ("Validate Binary Search Tree", "LeetCode 98", "Medium", "Trees & Binary Trees"),
    "102": ("Binary Tree Level Order Traversal", "LeetCode 102", "Medium", "Trees & Binary Trees"),
    "121": ("Best Time to Buy and Sell Stock", "LeetCode 121", "Easy", "Arrays & Strings"),
    "124": ("Binary Tree Maximum Path Sum", "LeetCode 124", "Hard", "Trees & Binary Trees"),
    "127": ("Word Ladder", "LeetCode 127", "Hard", "Graph & BFS/DFS"),
    "138": ("Copy List with Random Pointer", "LeetCode 138", "Medium", "Linked List"),
    "139": ("Word Break", "LeetCode 139", "Medium", "Dynamic Programming"),
    "140": ("Word Break II", "LeetCode 140", "Hard", "Backtracking"),
    "146": ("LRU Cache", "LeetCode 146", "Medium", "LLD / Concurrency"),
    "160": ("Intersection of Two Linked Lists", "LeetCode 160", "Easy", "Linked List"),
    "198": ("House Robber", "LeetCode 198", "Medium", "Dynamic Programming"),
    "199": ("Binary Tree Right Side View", "LeetCode 199", "Medium", "Trees & Binary Trees"),
    "200": ("Number of Islands", "LeetCode 200", "Medium", "Graph & BFS/DFS"),
    "206": ("Reverse Linked List", "LeetCode 206", "Easy", "Linked List"),
    "207": ("Course Schedule", "LeetCode 207", "Medium", "Graph & BFS/DFS"),
    "208": ("Implement Trie (Prefix Tree)", "LeetCode 208", "Medium", "Trees & Binary Trees"),
    "210": ("Course Schedule II", "LeetCode 210", "Medium", "Graph & BFS/DFS"),
    "211": ("Design Add and Search Words Data Structure", "LeetCode 211", "Medium", "Trees & Binary Trees"),
    "215": ("Kth Largest Element in an Array", "LeetCode 215", "Medium", "Heap / QuickSelect"),
    "221": ("Maximal Square", "LeetCode 221", "Medium", "Dynamic Programming"),
    "227": ("Basic Calculator II", "LeetCode 227", "Medium", "Arrays & Strings"),
    "236": ("Lowest Common Ancestor of a Binary Tree", "LeetCode 236", "Medium", "Trees & Binary Trees"),
    "238": ("Product of Array Except Self", "LeetCode 238", "Medium", "Arrays & Strings"),
    "239": ("Sliding Window Maximum", "LeetCode 239", "Hard", "Monotonic Queue / Deque"),
    "252": ("Meeting Rooms", "LeetCode 252", "Easy", "Intervals"),
    "253": ("Meeting Rooms II", "LeetCode 253", "Medium", "Intervals / Heap"),
    "269": ("Alien Dictionary", "LeetCode 269", "Hard", "Graph & BFS/DFS"),
    "273": ("Integer to English Words", "LeetCode 273", "Hard", "Arrays & Strings"),
    "286": ("Walls and Gates", "LeetCode 286", "Medium", "Graph & BFS/DFS"),
    "295": ("Find Median from Data Stream", "LeetCode 295", "Hard", "Heap / Priority Queue"),
    "297": ("Serialize and Deserialize Binary Tree", "LeetCode 297", "Hard", "Trees & Binary Trees"),
    "300": ("Longest Increasing Subsequence", "LeetCode 300", "Medium", "Dynamic Programming"),
    "322": ("Coin Change", "LeetCode 322", "Medium", "Dynamic Programming"),
    "339": ("Nested List Weight Sum", "LeetCode 339", "Medium", "Recursion / DFS"),
    "347": ("Top K Frequent Elements", "LeetCode 347", "Medium", "Heap / Priority Queue"),
    "378": ("Kth Smallest Element in a Sorted Matrix", "LeetCode 378", "Medium", "Heap / Priority Queue"),
    "380": ("Insert Delete GetRandom O(1)", "LeetCode 380", "Medium", "LLD / Concurrency"),
    "402": ("Remove K Digits", "LeetCode 402", "Medium", "Monotonic Stack"),
    "417": ("Pacific Atlantic Water Flow", "LeetCode 417", "Medium", "Graph & BFS/DFS"),
    "438": ("Find All Anagrams in a String", "LeetCode 438", "Medium", "Arrays & Strings"),
    "460": ("LFU Cache", "LeetCode 460", "Hard", "LLD / Concurrency"),
    "543": ("Diameter of Binary Tree", "LeetCode 543", "Easy", "Trees & Binary Trees"),
    "545": ("Boundary Traversal of Binary Tree", "LeetCode 545", "Medium", "Trees & Binary Trees"),
    "560": ("Subarray Sum Equals K", "LeetCode 560", "Medium", "Prefix Sum / Hash"),
    "621": ("Task Scheduler", "LeetCode 621", "Medium", "Heap / Greedy"),
    "692": ("Top K Frequent Words", "LeetCode 692", "Medium", "Heap / Priority Queue"),
    "735": ("Asteroid Collision", "LeetCode 735", "Medium", "Stack"),
    "739": ("Daily Temperatures", "LeetCode 739", "Medium", "Monotonic Stack"),
    "767": ("Reorganize String", "LeetCode 767", "Medium", "Heap / Greedy"),
    "787": ("Cheapest Flights Within K Stops", "LeetCode 787", "Medium", "Graph & BFS/DFS"),
    "863": ("All Nodes Distance K in Binary Tree", "LeetCode 863", "Medium", "Trees & Binary Trees"),
    "875": ("Koko Eating Bananas", "LeetCode 875", "Medium", "Binary Search"),
    "973": ("K Closest Points to Origin", "LeetCode 973", "Medium", "Heap / Priority Queue"),
    "994": ("Rotting Oranges", "LeetCode 994", "Medium", "Graph & BFS/DFS"),
    "1011": ("Capacity to Ship Packages Within D Days", "LeetCode 1011", "Medium", "Binary Search"),
    "1167": ("Minimum Cost to Connect Sticks", "LeetCode 1167", "Medium", "Heap / Priority Queue"),
    "1192": ("Critical Connections in a Network", "LeetCode 1192", "Hard", "Graph & BFS/DFS"),
    "1249": ("Minimum Remove to Make Valid Parentheses", "LeetCode 1249", "Medium", "Stack")
}

NAMED_PROBLEMS = {
    "trapping rain water": ("Trapping Rain Water", "LeetCode 42", "Hard", "Two Pointers"),
    "lru cache": ("LRU Cache", "LeetCode 146", "Medium", "LLD / Concurrency"),
    "lfu cache": ("LFU Cache", "LeetCode 460", "Hard", "LLD / Concurrency"),
    "course schedule": ("Course Schedule", "LeetCode 207", "Medium", "Graph & BFS/DFS"),
    "course schedule ii": ("Course Schedule II", "LeetCode 210", "Medium", "Graph & BFS/DFS"),
    "rotting oranges": ("Rotting Oranges", "LeetCode 994", "Medium", "Graph & BFS/DFS"),
    "merge intervals": ("Merge Intervals", "LeetCode 56", "Medium", "Intervals"),
    "meeting rooms ii": ("Meeting Rooms II", "LeetCode 253", "Medium", "Intervals / Heap"),
    "meeting rooms": ("Meeting Rooms", "LeetCode 252", "Easy", "Intervals"),
    "word break": ("Word Break", "LeetCode 139", "Medium", "Dynamic Programming"),
    "word break ii": ("Word Break II", "LeetCode 140", "Hard", "Backtracking"),
    "word ladder": ("Word Ladder", "LeetCode 127", "Hard", "Graph & BFS/DFS"),
    "koko eating bananas": ("Koko Eating Bananas", "LeetCode 875", "Medium", "Binary Search"),
    "daily temperatures": ("Daily Temperatures", "LeetCode 739", "Medium", "Monotonic Stack"),
    "remove k digits": ("Remove K Digits", "LeetCode 402", "Medium", "Monotonic Stack"),
    "reorganize string": ("Reorganize String", "LeetCode 767", "Medium", "Heap / Priority Queue"),
    "sliding window maximum": ("Sliding Window Maximum", "LeetCode 239", "Hard", "Monotonic Queue / Deque"),
    "task scheduler": ("Task Scheduler", "LeetCode 621", "Medium", "Heap / Priority Queue"),
    "find median from data stream": ("Find Median from Data Stream", "LeetCode 295", "Hard", "Heap / Priority Queue"),
    "median of two sorted arrays": ("Median of Two Sorted Arrays", "LeetCode 4", "Hard", "Binary Search"),
    "search in rotated sorted array": ("Search in Rotated Sorted Array", "LeetCode 33", "Medium", "Binary Search"),
    "binary tree maximum path sum": ("Binary Tree Maximum Path Sum", "LeetCode 124", "Hard", "Trees & Binary Trees"),
    "lowest common ancestor": ("Lowest Common Ancestor of a Binary Tree", "LeetCode 236", "Medium", "Trees & Binary Trees"),
    "serialize and deserialize binary tree": ("Serialize and Deserialize Binary Tree", "LeetCode 297", "Hard", "Trees & Binary Trees"),
    "copy list with random pointer": ("Copy List with Random Pointer", "LeetCode 138", "Medium", "Linked List"),
    "critical connections in a network": ("Critical Connections in a Network", "LeetCode 1192", "Hard", "Graph & BFS/DFS"),
    "minimum cost to connect sticks": ("Minimum Cost to Connect Sticks", "LeetCode 1167", "Medium", "Heap / Priority Queue"),
    "capacity to ship packages within d days": ("Capacity to Ship Packages Within D Days", "LeetCode 1011", "Medium", "Binary Search"),
    "asteroid collision": ("Asteroid Collision", "LeetCode 735", "Medium", "Stack"),
    "insert delete getrandom o(1)": ("Insert Delete GetRandom O(1)", "LeetCode 380", "Medium", "LLD / Concurrency"),
    "top k frequent elements": ("Top K Frequent Elements", "LeetCode 347", "Medium", "Heap / Priority Queue"),
    "top k frequent words": ("Top K Frequent Words", "LeetCode 692", "Medium", "Heap / Priority Queue"),
    "pacific atlantic water flow": ("Pacific Atlantic Water Flow", "LeetCode 417", "Medium", "Graph & BFS/DFS"),
    "alien dictionary": ("Alien Dictionary", "LeetCode 269", "Hard", "Graph & BFS/DFS"),
    "longest substring without repeating characters": ("Longest Substring Without Repeating Characters", "LeetCode 3", "Medium", "Sliding Window"),
    "longest palindromic substring": ("Longest Palindromic Substring", "LeetCode 5", "Medium", "Dynamic Programming"),
    "container with most water": ("Container With Most Water", "LeetCode 11", "Medium", "Two Pointers"),
    "3sum": ("3Sum", "LeetCode 15", "Medium", "Two Pointers"),
    "valid parentheses": ("Valid Parentheses", "LeetCode 20", "Easy", "Stack"),
    "number of islands": ("Number of Islands", "LeetCode 200", "Medium", "Graph & BFS/DFS"),
    "walls and gates": ("Walls and Gates", "LeetCode 286", "Medium", "Graph & BFS/DFS"),
    "coin change": ("Coin Change", "LeetCode 322", "Medium", "Dynamic Programming"),
    "subarray sum equals k": ("Subarray Sum Equals K", "LeetCode 560", "Medium", "Arrays & Strings"),
    "diameter of binary tree": ("Diameter of Binary Tree", "LeetCode 543", "Easy", "Trees & Binary Trees"),
    "boundary of binary tree": ("Boundary of Binary Tree", "LeetCode 545", "Medium", "Trees & Binary Trees")
}

AMAZON_LPS = [
    "Customer Obsession", "Ownership", "Bias for Action", "Deliver Results",
    "Dive Deep", "Earn Trust", "Have Backbone; Disagree and Commit",
    "Frugality", "Think Big", "Are Right, A Lot", "Hire and Develop the Best",
    "Insist on the Highest Standards", "Learn and Be Curious",
    "Strive to be Earth's Best Employer", "Success and Scale Bring Broad Responsibility"
]

MONTH_MAP = {
    'jan': 'January', 'feb': 'February', 'mar': 'March', 'apr': 'April',
    'may': 'May', 'jun': 'June', 'jul': 'July', 'aug': 'August',
    'sep': 'September', 'oct': 'October', 'nov': 'November', 'dec': 'December'
}

def make_graphql_request(query, variables, timeout=20):
    """Executes a GraphQL query to LeetCode with gzip decompression and error handling."""
    data = json.dumps({"query": query, "variables": variables}).encode("utf-8")
    req = urllib.request.Request(LEETCODE_GRAPHQL_URL, data=data, headers=GRAPHQL_HEADERS)
    ctx = ssl.create_default_context()

    try:
        with urllib.request.urlopen(req, timeout=timeout, context=ctx) as response:
            raw_content = response.read()
            if response.headers.get("Content-Encoding") == "gzip" or raw_content[:2] == b"\x1f\x8b":
                raw_content = gzip.decompress(raw_content)
            return json.loads(raw_content.decode("utf-8", errors="replace"))
    except urllib.error.HTTPError as e:
        raw_err = e.read()
        if e.headers.get("Content-Encoding") == "gzip" or raw_err[:2] == b"\x1f\x8b":
            raw_err = gzip.decompress(raw_err)
        print(f"[-] LeetCode GraphQL HTTP Error {e.code}: {raw_err.decode('utf-8', errors='replace')[:200]}")
        return None
    except Exception as e:
        print(f"[-] LeetCode GraphQL Network Exception: {e}")
        return None

def extract_role(title, content):
    """Identifies the candidate's target Amazon role."""
    combined = f"{title} {content}".lower()
    title_lower = title.lower()

    if any(k in title_lower for k in ["sde-3", "sde 3", "sde3", "sde iii", "senior sde", "l6 sde", "l6"]):
        return "SDE-3"
    if any(k in title_lower for k in ["sde-2", "sde 2", "sde2", "sde ii", "l5 sde", "l5"]):
        return "SDE-2"
    if any(k in title_lower for k in ["sde-1", "sde 1", "sde1", "sde i", "l4 sde", "l4", "new grad", "university grad", "intern"]):
        return "SDE-1"
    if any(k in title_lower for k in ["sysde", "systems dev", "system dev"]):
        return "Systems Development Engineer"
    if any(k in title_lower for k in ["frontend", "front end", "front-end", "fe engineer", "ui engineer"]):
        return "Frontend Engineer"
    if any(k in title_lower for k in ["applied scientist", "data scientist", "mle", "machine learning"]):
        return "Applied Scientist"
    if any(k in title_lower for k in ["data engineer", "bie", "business intelligence"]):
        return "Data Engineer"
    if any(k in title_lower for k in ["qae", "quality assurance", "sdet", "tester"]):
        return "Quality Assurance Engineer (QAE)"
    if any(k in title_lower for k in ["sdm", "engineering manager", "software development manager"]):
        return "Software Development Manager (SDM)"

    if any(k in combined for k in ["sde-2", "sde 2", "sde2", "l5 sde"]):
        return "SDE-2"
    if any(k in combined for k in ["sde-3", "sde 3", "sde3", "senior sde"]):
        return "SDE-3"
    if any(k in combined for k in ["sde-1", "sde 1", "sde1", "new grad", "entry level"]):
        return "SDE-1"
    if "sysde" in combined:
        return "Systems Development Engineer"
    if "applied scientist" in combined:
        return "Applied Scientist"
    if "frontend" in combined or "front-end" in combined:
        return "Frontend Engineer"
    if "data engineer" in combined:
        return "Data Engineer"

    return "Software Development Engineer"

def extract_location(title, content):
    """
    Extracts the job location.
    Per project requirement: Merges Indian locations
    (Bangalore, Bengaluru, Hyderabad, Pune, Chennai, Delhi, Gurgaon, Noida, etc.) -> 'India'.
    """
    combined = f"{title} {content}".lower()

    # 1. Normalize all Indian cities and references to 'India'
    indian_indicators = [
        "bangalore", "bengaluru", "hyderabad", "pune", "chennai",
        "delhi", "new delhi", "ncr", "gurgaon", "gurugram", "noida",
        "mumbai", "kolkata", "india"
    ]
    for ind in indian_indicators:
        if re.search(r'\b' + re.escape(ind) + r'\b', combined):
            return "India"

    # 2. Other global locations
    if "seattle" in combined:
        return "Seattle, WA, USA"
    if "dublin" in combined:
        return "Dublin, Ireland"
    if "london" in combined:
        return "London, UK"
    if "berlin" in combined or "germany" in combined:
        return "Berlin, Germany"
    if "luxembourg" in combined:
        return "Luxembourg"
    if "vancouver" in combined:
        return "Vancouver, Canada"
    if "toronto" in combined or "canada" in combined:
        return "Toronto, Canada"
    if "sunnyvale" in combined or "bay area" in combined:
        return "Sunnyvale, CA, USA"
    if "austin" in combined:
        return "Austin, TX, USA"
    if "arlington" in combined:
        return "Arlington, VA, USA"
    if "remote" in combined:
        return "Remote"
    if "usa" in combined or " us " in combined or "| us" in combined or "united states" in combined:
        return "USA"

    return "USA"

def extract_outcome(title, content):
    """Extracts the candidate's interview outcome."""
    combined = f"{title} {content}".lower()

    if any(k in combined for k in [
        "[offer]", "got offer", "offered", "received offer", "accepted offer",
        "result: offer", "status: offer", "verdict: offer", "selected", "cleared all rounds"
    ]):
        return "Offer"
    if any(k in combined for k in [
        "[reject]", "[rejected]", "rejected", "rejection", "dinged",
        "result: reject", "status: reject", "verdict: reject", "not selected", "could not clear"
    ]):
        return "Rejected"

    return "Pending"

def extract_interview_date(title, content, post_date_str):
    """Extracts the explicit interview date or derives it from the title/post_date."""
    post_year = post_date_str.split("-")[0] if post_date_str else "2026"

    # 1. Look for explicit "Interview Date: ..." or "Interview Invitation ... Interview Date: Feb 27 - Mar 3"
    m_iv = re.search(r'Interview Date\s*[:\-]\s*([A-Za-z0-9\s,\-]+?)(?:\n|\r|\.|\*|\(|$)', content, re.IGNORECASE)
    if m_iv:
        val = m_iv.group(1).replace('–', '-').replace('—', '-').strip()
        val = re.sub(r'\s+', ' ', val)
        if 3 <= len(val) <= 25 and any(c.isalpha() for c in val):
            if not any(y in val for y in ["2024", "2025", "2026"]):
                val = f"{val}, {post_year}"
            return val

    # 2. Look for explicit Month + Year in title (e.g. "Feb 2025", "March 2026")
    m_title = re.search(
        r'\b(Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\s*(20\d\d)?\b',
        title, re.IGNORECASE
    )
    if m_title:
        m_prefix = m_title.group(1)[:3].lower()
        month_full = MONTH_MAP.get(m_prefix, m_title.group(1).capitalize())
        year = m_title.group(2) or post_year
        return f"{month_full} {year}"

    # 3. Look for "interview scheduled on <Date>" or "Round 1: ... <Date>"
    m_sched = re.search(
        r'(?:interview scheduled on|interview date is|took my OA on|interview was on|interview was scheduled for)\s*(\d{1,2}(?:st|nd|rd|th)?\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*|\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{1,2}(?:st|nd|rd|th)?)',
        content, re.IGNORECASE
    )
    if m_sched:
        return f"{m_sched.group(1).title()} {post_year}"

    # 4. Fallback to post date formatted nicely: "March 2026"
    if post_date_str:
        try:
            dt = datetime.strptime(post_date_str[:10], "%Y-%m-%d")
            return dt.strftime("%B %Y")
        except Exception:
            pass

    return f"September {post_year}"

def extract_rounds_and_questions(content, title):
    """
    Parses rounds, questions, and identifies LeetCode problem mappings.
    Returns structured rounds with question metadata.
    """
    rounds = []
    lines = content.split("\n")
    current_round = None
    round_lines = []

    round_pattern = re.compile(
        r"^(?:\*{0,2})(?:Round\s*\d+|OA\d?|Online\s*Assessment|Screening|Phone\s*Screen|Technical\s*Round\s*\d*|Virtual\s*Onsite\s*Round\s*\d*|Bar\s*Raiser|HM\s*Round|Hiring\s*Manager|System\s*Design|DSA\s*Round|Coding\s*Round\s*\d*|R\d+)(?:\*{0,2})[:\-–—]?",
        re.IGNORECASE
    )

    for line in lines:
        stripped = line.strip()
        if round_pattern.match(stripped):
            if current_round and round_lines:
                rounds.append((current_round, "\n".join(round_lines).strip()))
            current_round = stripped
            round_lines = []
        else:
            if current_round:
                round_lines.append(stripped)

    if current_round and round_lines:
        rounds.append((current_round, "\n".join(round_lines).strip()))

    # If no explicit rounds found, synthesize from paragraphs
    if not rounds and len(content.strip()) > 80:
        paragraphs = [p.strip() for p in content.split("\n\n") if len(p.strip()) > 40]
        if paragraphs:
            for idx, p in enumerate(paragraphs[:4]):
                name = f"Round {idx+1}: Technical Assessment" if idx > 0 else "Round 1: Online Assessment / Phone Screen"
                rounds.append((name, p))

    # Identify questions from text using LeetCode patterns
    found_questions = []
    seen_q_keys = set()
    combined_text = f"{title}\n{content}"

    # 1. Match LC / LeetCode numbers: e.g. LC 253, LeetCode #402
    for m in re.finditer(r'\b(?:LC|LeetCode)\s*(?:#|no\.?)?\s*(\d{1,4})\b(?:\s*[-–—:]\s*([A-Za-z0-9\s]{3,40}))?', combined_text, re.IGNORECASE):
        num = m.group(1)
        name_hint = m.group(2).strip() if m.group(2) else ""
        if num in LC_NUM_MAP and num not in seen_q_keys:
            seen_q_keys.add(num)
            q_name, q_lc, q_diff, q_cat = LC_NUM_MAP[num]
            found_questions.append({
                "name": q_name,
                "leetcode_equivalent": q_lc,
                "difficulty": q_diff,
                "category": q_cat,
                "description": f"Asked in candidate's interview loop: {name_hint or q_name}",
                "code_snippet": ""
            })
        elif name_hint and len(name_hint) > 3 and num not in seen_q_keys:
            seen_q_keys.add(num)
            found_questions.append({
                "name": f"{name_hint} (LeetCode {num})",
                "leetcode_equivalent": f"LeetCode {num}",
                "difficulty": "Medium",
                "category": "Algorithms & Problem Solving",
                "description": f"Amazon coding problem: {name_hint}",
                "code_snippet": ""
            })

    # 2. Match known top Amazon LeetCode questions by name
    low_combined = combined_text.lower()
    for np_key, (np_name, np_lc, np_diff, np_cat) in NAMED_PROBLEMS.items():
        if np_key not in seen_q_keys:
            if re.search(r'\b' + re.escape(np_key) + r'\b', low_combined):
                seen_q_keys.add(np_key)
                found_questions.append({
                    "name": np_name,
                    "leetcode_equivalent": np_lc,
                    "difficulty": np_diff,
                    "category": np_cat,
                    "description": f"Target problem identified in candidate interview loop: {np_name}",
                    "code_snippet": ""
                })

    # 3. Match System Design / LLD topics
    for m in re.finditer(r'\b(?:Design|Implement)\s+((?:Amazon\s+)?[A-Z][a-zA-Z0-9\s\-]{4,50}(?:System|Service|Platform|Cache|Locker|Scheduler|Autocomplete|Rate Limiter|API|Storage|Search|Streaming|DJ|Player|Game|Elevator|Parking))', combined_text):
        sd_name = f"Design {m.group(1).strip()}"
        key = sd_name.lower()
        if key not in seen_q_keys and len(sd_name) < 70:
            seen_q_keys.add(key)
            is_lld = any(kw in sd_name.lower() for kw in ["cache", "parking", "elevator", "locker", "game", "player", "scheduler"])
            found_questions.append({
                "name": sd_name,
                "leetcode_equivalent": "",
                "difficulty": "Hard" if not is_lld else "Medium",
                "category": "Low-Level Design (LLD)" if is_lld else "System Design (HLD)",
                "description": f"Architecture and component design question in interview loop: {sd_name}",
                "code_snippet": ""
            })

    # Fallback generic questions if none extracted
    if not found_questions:
        found_questions.append({
            "name": "Amazon Core Problem Solving & DSA Assessment",
            "leetcode_equivalent": "LeetCode Pattern",
            "difficulty": "Medium",
            "category": "Algorithms & Problem Solving",
            "description": "Core data structure & algorithm problem covering candidate competencies.",
            "code_snippet": ""
        })

    # Build structured round objects
    structured_rounds = []
    q_idx = 0

    if rounds:
        for r_name, r_body in rounds:
            clean_name = r_name.strip().strip("*#_ :")
            round_qs = []
            if q_idx < len(found_questions):
                round_qs.append(found_questions[q_idx])
                q_idx += 1
            else:
                round_qs.append({
                    "name": "Technical Problem Solving & LP Discussion",
                    "leetcode_equivalent": "",
                    "difficulty": "Medium",
                    "category": "Data Structures / LP",
                    "description": f"Questions discussed in {clean_name}",
                    "code_snippet": ""
                })

            structured_rounds.append({
                "round_name": clean_name if clean_name else "Technical Assessment Round",
                "questions": round_qs,
                "details": r_body[:1200]
            })
    else:
        structured_rounds.append({
            "round_name": "Technical Assessment Round",
            "questions": found_questions[:2],
            "details": content[:1200]
        })

    return structured_rounds, found_questions

def extract_tips(content):
    """Extracts Amazon Leadership Principles and preparation tips."""
    tips = []
    lower_content = content.lower()

    for lp in AMAZON_LPS:
        if lp.lower() in lower_content:
            tips.append(f"Focus heavily on Amazon LP: '{lp}'. Prepare 2 distinct STAR stories demonstrating this principle.")

    tip_matches = re.findall(r"(?:tip|advice|suggestion|recommendation|learning)s?[:\-–—\s]+(.+?)(?:\n\n|\Z)", content, re.IGNORECASE | re.DOTALL)
    if tip_matches:
        for match in tip_matches:
            for l in match.split("\n"):
                l_clean = l.strip().strip("-*•123456789.) ")
                if len(l_clean) > 20 and len(l_clean) < 200:
                    tips.append(l_clean)

    standard_tips = [
        "Structure all behavioral answers using the STAR format (Situation, Task, Action, Result) with quantified business impact.",
        "Clarify ambiguous requirements upfront and discuss multiple trade-offs before writing a single line of code.",
        "Amazon Bar Raiser evaluates team culture fit and ownership; never blame colleagues or past management."
    ]
    for st in standard_tips:
        if len(tips) < 4 and st not in tips:
            tips.append(st)

    return tips[:5]

def generate_summary(title, role, location, outcome, rounds):
    """Generates a concise summary of the interview experience."""
    round_count = len(rounds)
    round_names = ", ".join([r["round_name"] for r in rounds[:3]])
    return (
        f"Amazon interview experience for {role} at {location}. "
        f"The candidate went through {round_count} primary evaluation stages ({round_names}) "
        f"focusing on Data Structures, System Design, and Amazon Leadership Principles. Final outcome: {outcome}."
    )

def send_telegram_alert(token, chat_id, message_html):
    """Sends a formatted alert to Telegram via the Telegram Bot API."""
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message_html,
        "parse_mode": "HTML",
        "disable_web_page_preview": False
    }

    if HAS_REQUESTS:
        try:
            resp = requests.post(url, json=payload, timeout=15)
            if resp.status_code == 200:
                return True, "Success"
            return False, f"HTTP {resp.status_code}: {resp.text[:150]}"
        except Exception as e:
            return False, str(e)
    else:
        try:
            data = json.dumps(payload).encode("utf-8")
            req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
            ctx = ssl.create_default_context()
            with urllib.request.urlopen(req, timeout=15, context=ctx) as r:
                return True, "Success"
        except urllib.error.HTTPError as e:
            return False, f"HTTP {e.code}: {e.read().decode('utf-8', errors='replace')[:150]}"
        except Exception as e:
            return False, str(e)

def format_telegram_message(item):
    """Formats an interview experience into an HTML Telegram alert."""
    outcome = item.get("outcome", "Pending")
    outcome_badge = "🎉 Offer" if outcome == "Offer" else ("❌ Rejected" if outcome == "Rejected" else "⏳ Pending")

    # Extract questions
    question_names = []
    for r in item.get("rounds", []):
        for q in r.get("questions", []):
            if isinstance(q, dict) and q.get("name"):
                name = q["name"]
                lc = q.get("leetcode_equivalent")
                diff = q.get("difficulty")
                item_str = name
                if lc:
                    item_str += f" ({lc})"
                if diff:
                    item_str += f" [{diff}]"
                if item_str not in question_names:
                    question_names.append(item_str)
            elif isinstance(q, str) and q.strip() and q not in question_names:
                question_names.append(q)

    if question_names:
        questions_formatted = "\n".join([f"  • {html.escape(q)}" for q in question_names[:4]])
    else:
        questions_formatted = "  • Technical Problem Solving & LP Questions"

    # Extract top tip
    tips = item.get("tips", [])
    top_tip = html.escape(tips[0]) if tips else "Prepare structured STAR stories highlighting Amazon Leadership Principles."

    msg = (
        f"🚀 <b>New Amazon Interview Experience</b>\n\n"
        f"📌 <b>Title:</b> <a href=\"{html.escape(item.get('url', ''))}\">{html.escape(item.get('title', ''))}</a>\n"
        f"💼 <b>Role:</b> {html.escape(item.get('role', 'SDE'))}\n"
        f"📍 <b>Location:</b> {html.escape(item.get('location', 'USA'))}\n"
        f"📅 <b>Interview Date:</b> {html.escape(item.get('interview_date', item.get('post_date', '')))}\n"
        f"📊 <b>Outcome:</b> {outcome_badge}\n\n"
        f"❓ <b>Key Questions Asked:</b>\n"
        f"{questions_formatted}\n\n"
        f"💡 <b>Key Tip / Principle:</b>\n"
        f"  <i>{top_tip}</i>\n\n"
        f"🔗 <a href=\"{html.escape(item.get('url', ''))}\">Read Full Experience on LeetCode</a>"
    )
    return msg

def load_dataset(file_path):
    """Loads JSON dataset from the given path."""
    if not os.path.exists(file_path):
        return []
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"[-] Error loading {file_path}: {e}")
        return []

def save_dataset(file_path, data):
    """Saves dataset cleanly formatted to JSON."""
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def run_daily_sync(limit=50, dry_run=False, test_telegram=False):
    """
    Main orchestration function:
    1. Loads existing experiences.
    2. Queries LeetCode GraphQL for latest Amazon experiences.
    3. Detects newly posted experiences.
    4. Enriches and merges Indian locations to 'India'.
    5. Saves updated datasets.
    6. Dispatches Telegram alerts.
    """
    telegram_token = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
    telegram_chat_id = os.environ.get("TELEGRAM_CHAT_ID", "").strip()

    if test_telegram:
        print("[*] Testing Telegram notification...")
        if not telegram_token or not telegram_chat_id:
            print("[-] Error: TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID is not set in environment.")
            return 1
        test_msg = (
            "🤖 <b>Amazon Interview Explorer Alert System</b>\n\n"
            "✅ Telegram Bot connection successful!\n"
            f"📅 Timestamp: <i>{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</i>\n"
            "Automation pipeline is healthy and operational."
        )
        ok, err = send_telegram_alert(telegram_token, telegram_chat_id, test_msg)
        if ok:
            print("[+] Test Telegram alert sent successfully!")
            return 0
        else:
            print(f"[-] Failed to send Telegram alert: {err}")
            return 1

    print(f"[*] Loading existing experiences from {DATA_FILE}...")
    existing_data = load_dataset(DATA_FILE)
    print(f"[+] Loaded {len(existing_data)} existing records.")

    # Build lookup indices for fast deduplication
    existing_ids = {str(item.get("id")) for item in existing_data if item.get("id")}
    existing_urls = {item.get("url") for item in existing_data if item.get("url")}

    print(f"[*] Querying modern LeetCode UGC GraphQL for latest {limit} Amazon interview experiences...")
    
    # Query modern UGC GraphQL endpoint with Amazon interview keywords
    candidate_edges = []
    seen_topic_ids = set()

    for kw_list in [["Amazon", "interview"], ["Amazon", "SDE"]]:
        variables = {
            "keywords": kw_list,
            "first": min(limit, 50),
            "skip": 0
        }
        resp = make_graphql_request(GRAPHQL_UGC_ARTICLES_QUERY, variables)
        if resp and "data" in resp:
            articles = resp.get("data", {}).get("ugcArticleDiscussionArticles", {}).get("edges", [])
            for edge in articles:
                tid = str((edge.get("node") or {}).get("topicId") or "")
                if tid and tid not in seen_topic_ids:
                    seen_topic_ids.add(tid)
                    candidate_edges.append(edge)

    if not candidate_edges:
        print("[-] Warning: No UGC topics returned from LeetCode. Checking response or connectivity.")
        return 0

    print(f"[+] Retrieved {len(candidate_edges)} candidate UGC topics from LeetCode.")

    new_experiences = []

    for edge in candidate_edges:
        node = edge.get("node") or {}
        post_id = str(node.get("topicId") or "")
        title = (node.get("title") or "").strip()
        summary = (node.get("summary") or "").strip()
        created_at = node.get("createdAt") or ""

        if not post_id:
            continue

        # Skip pinned / meta posts
        if post_id in ["128008", "8492873", "7939302"] or "how to write an interview experience" in title.lower():
            continue

        # Skip if already in database
        post_url = f"https://leetcode.com/discuss/post/{post_id}/"
        legacy_url = f"https://leetcode.com/discuss/interview-experience/{post_id}/"
        if post_id in existing_ids or post_url in existing_urls or legacy_url in existing_urls:
            continue

        # Verify Amazon relevance
        title_lower = title.lower()
        summary_lower = summary.lower()
        tags_raw = node.get("tags") or []
        tag_names = [t.get("name", "").lower() for t in tags_raw if isinstance(t, dict)]

        is_amazon = "amazon" in title_lower or any("amazon" in t for t in tag_names)
        is_interview = any(w in title_lower for w in ["interview", "sde", "oa", "round", "offer", "intern", "assessment", "experience"])
        if not (is_amazon and is_interview):
            continue

        print(f"[*] Discovered new Amazon interview experience #{post_id}: {title[:55]}...")

        # Fetch full modern article details via GraphQL
        content = summary
        author = "Anonymous"
        views = 0
        detail_resp = make_graphql_request(GRAPHQL_UGC_ARTICLE_DETAIL_QUERY, {"topicId": post_id})
        if detail_resp and "data" in detail_resp:
            art = detail_resp.get("data", {}).get("ugcArticleDiscussionArticle") or {}
            content = art.get("content") or summary
            author_info = art.get("author") or {}
            author = author_info.get("userName") or author_info.get("realName") or "Anonymous"
            views = art.get("hitCount") or 0

        # Skip non-experience brief posts (under 75 characters)
        if len(content) < 75 and "interview" not in title.lower():
            continue

        # Extract details
        post_date = created_at[:10] if created_at else datetime.now().strftime("%Y-%m-%d")
        role = extract_role(title, content)
        location = extract_location(title, content)
        outcome = extract_outcome(title, content)
        interview_date = extract_interview_date(title, content, post_date)
        rounds, found_questions = extract_rounds_and_questions(content, title)
        tips = extract_tips(content)
        item_summary = generate_summary(title, role, location, outcome, rounds)

        # Build normalized tags
        tags = [t.get("name") for t in tags_raw if isinstance(t, dict) and t.get("name")]
        if "Amazon" not in tags:
            tags.insert(0, "Amazon")
        if role not in tags:
            tags.append(role)
        if "Interview Experience" not in tags:
            tags.append("Interview Experience")

        record = {
            "id": int(post_id),
            "title": title,
            "role": role,
            "location": location,
            "outcome": outcome,
            "post_date": post_date,
            "interview_date": interview_date,
            "url": post_url,
            "author": author,
            "votes": 0,
            "views": int(views),
            "tags": tags,
            "rounds": rounds,
            "summary": item_summary,
            "tips": tips,
            "leadership_principles": [lp for lp in AMAZON_LPS if lp.lower() in content.lower()],
            "full_text": content
        }

        new_experiences.append(record)
        existing_ids.add(post_id)
        existing_urls.add(post_url)
        time.sleep(0.4)  # Rate limiting precaution

    if not new_experiences:
        print("[+] Daily sync check completed. No new Amazon interview experiences found.")
        print("[+] Dataset is already up-to-date. Exiting cleanly.")
        return 0

    print(f"\n[+] Detected {len(new_experiences)} NEW Amazon interview experience(s)!")
    print("-" * 75)
    for idx, exp in enumerate(new_experiences, 1):
        print(f"{idx}. [{exp['post_date']}] {exp['role']} ({exp['location']}) - {exp['outcome']}")
        print(f"   Title: {exp['title']}")
        print(f"   URL:   {exp['url']}")
    print("-" * 75)

    if dry_run:
        print("[*] Dry-run enabled. Skipping database write and live Telegram alerts.")
        return 0

    # Merge and sort dataset
    updated_data = existing_data + new_experiences
    # Sort descending by post_date, secondary key id descending
    updated_data.sort(key=lambda x: (x.get("post_date", "2024-01-01"), str(x.get("id", ""))), reverse=True)

    # Save to data/experiences.json and ui/experiences.json
    print(f"[*] Saving updated dataset to {DATA_FILE}...")
    save_dataset(DATA_FILE, updated_data)
    print(f"[*] Saving updated dataset to {UI_FILE}...")
    save_dataset(UI_FILE, updated_data)
    print(f"[+] Successfully saved! Total records: {len(updated_data)} (+{len(new_experiences)} new)")

    # Dispatch Telegram notifications
    if telegram_token and telegram_chat_id:
        print(f"[*] Dispatching Telegram alert(s) for {len(new_experiences)} new post(s)...")
        success_count = 0
        for exp in new_experiences:
            msg = format_telegram_message(exp)
            ok, err = send_telegram_alert(telegram_token, telegram_chat_id, msg)
            if ok:
                success_count += 1
                print(f"  [+] Sent alert for: {exp['title'][:45]}...")
            else:
                print(f"  [-] Failed to send alert: {err}")
            time.sleep(0.5)  # Rate limiting precaution

        print(f"[+] Dispatched {success_count}/{len(new_experiences)} Telegram alerts.")
    else:
        print("[-] Telegram credentials not configured (TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID missing).")
        print("[-] Skipping Telegram notification.")

    return 0

def main():
    parser = argparse.ArgumentParser(description="Daily automated sync pipeline for Amazon Interview Experiences.")
    parser.add_argument("--limit", type=int, default=50, help="Number of latest topics to inspect (default: 50)")
    parser.add_argument("--dry-run", action="store_true", help="Perform fetch and detection without writing files or sending alerts")
    parser.add_argument("--test-telegram", action="store_true", help="Send a test message to verify Telegram credentials")
    args = parser.parse_args()

    exit_code = run_daily_sync(limit=args.limit, dry_run=args.dry_run, test_telegram=args.test_telegram)
    sys.exit(exit_code)

if __name__ == "__main__":
    main()
