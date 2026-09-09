import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

# LeetCode slug to clean title & difficulty & category dictionary
SLUG_META = {
    "3sum": ("3Sum", "LeetCode 15", "Medium", "Arrays & Strings"),
    "add-two-numbers-ii": ("Add Two Numbers II", "LeetCode 445", "Medium", "Linked List"),
    "alien-dictionary": ("Alien Dictionary", "LeetCode 269", "Hard", "Graph & BFS/DFS"),
    "all-nodes-distance-k-in-binary-tree": ("All Nodes Distance K in Binary Tree", "LeetCode 863", "Medium", "Trees & Binary Trees"),
    "asteroid-collision": ("Asteroid Collision", "LeetCode 735", "Medium", "Arrays & Strings"),
    "backspace-string-compare": ("Backspace String Compare", "LeetCode 844", "Easy", "Arrays & Strings"),
    "basic-calculator-ii": ("Basic Calculator II", "LeetCode 227", "Medium", "Arrays & Strings"),
    "binary-tree-maximum-path-sum": ("Binary Tree Maximum Path Sum", "LeetCode 124", "Hard", "Trees & Binary Trees"),
    "binary-tree-right-side-view": ("Binary Tree Right Side View", "LeetCode 199", "Medium", "Trees & Binary Trees"),
    "boundary-of-binary-tree": ("Boundary of Binary Tree", "LeetCode 545", "Medium", "Trees & Binary Trees"),
    "cheapest-flights-within-k-stops": ("Cheapest Flights Within K Stops", "LeetCode 787", "Medium", "Graph & BFS/DFS"),
    "climbing-stairs": ("Climbing Stairs", "LeetCode 70", "Easy", "Dynamic Programming"),
    "count-good-nodes-in-binary-tree": ("Count Good Nodes in Binary Tree", "LeetCode 1448", "Medium", "Trees & Binary Trees"),
    "course-schedule": ("Course Schedule", "LeetCode 207", "Medium", "Graph & BFS/DFS"),
    "course-schedule-ii": ("Course Schedule II", "LeetCode 210", "Medium", "Graph & BFS/DFS"),
    "cracking-the-safe": ("Cracking the Safe", "LeetCode 753", "Hard", "Graph & BFS/DFS"),
    "design-add-and-search-words-data-structure": ("Design Add and Search Words Data Structure", "LeetCode 211", "Medium", "Trees & Binary Trees"),
    "edit-distance": ("Edit Distance", "LeetCode 72", "Medium", "Dynamic Programming"),
    "find-all-anagrams-in-a-string": ("Find All Anagrams in a String", "LeetCode 438", "Medium", "Arrays & Strings"),
    "find-first-and-last-position-of-element-in-sorted-array": ("Find First and Last Position of Element in Sorted Array", "LeetCode 34", "Medium", "Arrays & Strings"),
    "frog-jump": ("Frog Jump", "LeetCode 403", "Hard", "Dynamic Programming"),
    "generate-parentheses": ("Generate Parentheses", "LeetCode 22", "Medium", "Backtracking"),
    "group-anagrams": ("Group Anagrams", "LeetCode 49", "Medium", "Arrays & Strings"),
    "house-robber-iii": ("House Robber III", "LeetCode 337", "Medium", "Dynamic Programming"),
    "implement-trie-prefix-tree": ("Implement Trie (Prefix Tree)", "LeetCode 208", "Medium", "Trees & Binary Trees"),
    "insert-delete-getrandom-o1": ("Insert Delete GetRandom O(1)", "LeetCode 380", "Medium", "LLD / Concurrency"),
    "integer-to-english-words": ("Integer to English Words", "LeetCode 273", "Hard", "Arrays & Strings"),
    "intersection-of-two-linked-lists": ("Intersection of Two Linked Lists", "LeetCode 160", "Easy", "Linked List"),
    "k-closest-points-to-origin": ("K Closest Points to Origin", "LeetCode 973", "Medium", "Heap / Priority Queue"),
    "koko-eating-bananas": ("Koko Eating Bananas", "LeetCode 875", "Medium", "Binary Search"),
    "kth-smallest-element-in-a-sorted-matrix": ("Kth Smallest Element in a Sorted Matrix", "LeetCode 378", "Medium", "Heap / Priority Queue"),
    "lfu-cache": ("LFU Cache", "LeetCode 460", "Hard", "LLD / Concurrency"),
    "linked-list-cycle-ii": ("Linked List Cycle II", "LeetCode 142", "Medium", "Linked List"),
    "longest-common-prefix": ("Longest Common Prefix", "LeetCode 14", "Easy", "Arrays & Strings"),
    "lowest-common-ancestor-of-a-binary-tree-iii": ("Lowest Common Ancestor of a Binary Tree III", "LeetCode 1650", "Medium", "Trees & Binary Trees"),
    "lru-cache": ("LRU Cache", "LeetCode 146", "Medium", "LLD / Concurrency"),
    "maximal-square": ("Maximal Square", "LeetCode 221", "Medium", "Dynamic Programming"),
    "maximum-width-ramp": ("Maximum Width Ramp", "LeetCode 962", "Medium", "Monotonic Stack"),
    "median-of-two-sorted-arrays": ("Median of Two Sorted Arrays", "LeetCode 4", "Hard", "Binary Search"),
    "merge-intervals": ("Merge Intervals", "LeetCode 56", "Medium", "Intervals"),
    "merge-k-sorted-lists": ("Merge k Sorted Lists", "LeetCode 23", "Hard", "Heap / Priority Queue"),
    "merge-sorted-array": ("Merge Sorted Array", "LeetCode 88", "Easy", "Arrays & Strings"),
    "minimum-cost-to-connect-sticks": ("Minimum Cost to Connect Sticks", "LeetCode 1167", "Medium", "Heap / Priority Queue"),
    "minimum-path-sum": ("Minimum Path Sum", "LeetCode 64", "Medium", "Dynamic Programming"),
    "minimum-remove-to-make-valid-parentheses": ("Minimum Remove to Make Valid Parentheses", "LeetCode 1249", "Medium", "Stack"),
    "nested-list-weight-sum": ("Nested List Weight Sum", "LeetCode 339", "Medium", "Recursion / DFS"),
    "next-permutation": ("Next Permutation", "LeetCode 31", "Medium", "Arrays & Strings"),
    "pacific-atlantic-water-flow": ("Pacific Atlantic Water Flow", "LeetCode 417", "Medium", "Graph & BFS/DFS"),
    "palindrome-number": ("Palindrome Number", "LeetCode 9", "Easy", "Math"),
    "random-pick-with-weight": ("Random Pick with Weight", "LeetCode 528", "Medium", "Binary Search"),
    "range-sum-of-bst": ("Range Sum of BST", "LeetCode 938", "Easy", "Trees & Binary Trees"),
    "reorganize-string": ("Reorganize String", "LeetCode 767", "Medium", "Heap / Priority Queue"),
    "reverse-nodes-in-k-group": ("Reverse Nodes in k-Group", "LeetCode 25", "Hard", "Linked List"),
    "rotting-oranges": ("Rotting Oranges", "LeetCode 994", "Medium", "Graph & BFS/DFS"),
    "search-a-2d-matrix-ii": ("Search a 2D Matrix II", "LeetCode 240", "Medium", "Binary Search"),
    "search-in-rotated-sorted-array": ("Search in Rotated Sorted Array", "LeetCode 33", "Medium", "Binary Search"),
    "simplify-path": ("Simplify Path", "LeetCode 71", "Medium", "Stack"),
    "sliding-window-maximum": ("Sliding Window Maximum", "LeetCode 239", "Hard", "Monotonic Queue / Deque"),
    "sort-colors": ("Sort Colors", "LeetCode 75", "Medium", "Two Pointers"),
    "sum-of-total-strength-of-wizards": ("Sum of Total Strength of Wizards", "LeetCode 2281", "Hard", "Monotonic Stack"),
    "text-justification": ("Text Justification", "LeetCode 68", "Hard", "Arrays & Strings"),
    "top-k-frequent-elements": ("Top K Frequent Elements", "LeetCode 347", "Medium", "Heap / Priority Queue"),
    "top-k-frequent-words": ("Top K Frequent Words", "LeetCode 692", "Medium", "Heap / Priority Queue"),
    "trapping-rain-water": ("Trapping Rain Water", "LeetCode 42", "Hard", "Two Pointers"),
    "two-sum": ("Two Sum", "LeetCode 1", "Easy", "Arrays & Strings"),
    "word-break": ("Word Break", "LeetCode 139", "Medium", "Dynamic Programming"),
    "word-break-ii": ("Word Break II", "LeetCode 140", "Hard", "Backtracking / Trie"),
    "word-search": ("Word Search", "LeetCode 79", "Medium", "Backtracking"),
    "remove-k-digits": ("Remove K Digits", "LeetCode 402", "Medium", "Monotonic Stack"),
    "meeting-rooms-ii": ("Meeting Rooms II", "LeetCode 253", "Medium", "Intervals / Heap"),
    "daily-temperatures": ("Daily Temperatures", "LeetCode 739", "Medium", "Monotonic Stack"),
    "coin-change": ("Coin Change", "LeetCode 322", "Medium", "Dynamic Programming"),
    "subarray-sum-equals-k": ("Subarray Sum Equals K", "LeetCode 560", "Medium", "Prefix Sum / Hash"),
    "capacity-to-ship-packages-within-d-days": ("Capacity to Ship Packages Within D Days", "LeetCode 1011", "Medium", "Binary Search"),
    "task-scheduler": ("Task Scheduler", "LeetCode 621", "Medium", "Heap / Greedy"),
    "distance-between-bus-stopsplus": ("Distance Between Bus Stops", "LeetCode 1184", "Easy", "Arrays & Strings"),
    "insert-delete-getrandom-o1-duplicates-allowed": ("Insert Delete GetRandom O(1) - Duplicates Allowed", "LeetCode 381", "Hard", "LLD / Concurrency"),
    "kth-missing-positive-number": ("Kth Missing Positive Number", "LeetCode 1539", "Easy", "Binary Search"),
    "long-pressed-name": ("Long Pressed Name", "LeetCode 925", "Easy", "Arrays & Strings"),
    "max-consecutive-ones-ii": ("Max Consecutive Ones II", "LeetCode 487", "Medium", "Sliding Window"),
    "maximum-gap-between-stations": ("Maximum Gap Between Stations", "Amazon OA", "Medium", "Arrays & Strings"),
    "maximum-swap": ("Maximum Swap", "LeetCode 670", "Medium", "Greedy"),
    "maximum-total-value-of-covered-indices": ("Maximum Total Value of Covered Indices", "Amazon OA", "Medium", "Dynamic Programming"),
    "minimum-cost-to-make-all-characters-equal": ("Minimum Cost to Make All Characters Equal", "LeetCode 2712", "Medium", "Greedy"),
    "minimum-number-of-days-to-disconnec": ("Minimum Number of Days to Disconnect Island", "LeetCode 1568", "Hard", "Graph & BFS/DFS"),
    "minimum-number-of-days-to-make-m-bouquets": ("Minimum Number of Days to Make m Bouquets", "LeetCode 1482", "Medium", "Binary Search"),
    "minimum-swaps-to-avoid-forbidden-values": ("Minimum Swaps to Avoid Forbidden Values", "Amazon OA", "Hard", "Greedy / Graph"),
    "minimum-time-to-collect-all-apples-in-a-tree": ("Minimum Time to Collect All Apples in a Tree", "LeetCode 1443", "Medium", "Trees & Binary Trees"),
    "missing-element-in-sorted-array": ("Missing Element in Sorted Array", "LeetCode 1060", "Medium", "Binary Search"),
    "regions-cut-by-slashes": ("Regions Cut By Slashes", "LeetCode 959", "Medium", "Graph & BFS/DFS"),
    "remove-one-element-to-make-the-array-strictly-increasing": ("Remove One Element to Make Array Strictly Increasing", "LeetCode 1909", "Easy", "Arrays & Strings"),
    "remove-zero-sum-consecutive-nodes-from-linked-list": ("Remove Zero Sum Consecutive Nodes from Linked List", "LeetCode 1171", "Medium", "Linked List"),
    "shortest-uncommon-substring-in-an-array": ("Shortest Uncommon Substring in an Array", "LeetCode 3076", "Medium", "Trie / Hash Table"),
    "single-element-in-a-sorted-array": ("Single Element in a Sorted Array", "LeetCode 540", "Medium", "Binary Search"),
    "stamping-the-grid": ("Stamping the Grid", "LeetCode 2132", "Hard", "Matrix / Prefix Sum"),
    "the-number-of-employees-which-report-to-each-employee": ("The Number of Employees Which Report to Each Employee", "LeetCode 1731", "Easy", "Database / SQL"),
    "unique-length-3-palindromic-subsequences": ("Unique Length-3 Palindromic Subsequences", "LeetCode 1930", "Medium", "Arrays & Strings")
}

# Also map common LeetCode number references
LC_NUM_MAP = {
    "1": ("Two Sum", "LeetCode 1", "Easy", "Arrays & Strings"),
    "3": ("Longest Substring Without Repeating Characters", "LeetCode 3", "Medium", "Sliding Window"),
    "4": ("Median of Two Sorted Arrays", "LeetCode 4", "Hard", "Binary Search"),
    "5": ("Longest Palindromic Substring", "LeetCode 5", "Medium", "Dynamic Programming"),
    "11": ("Container With Most Water", "LeetCode 11", "Medium", "Two Pointers"),
    "15": ("3Sum", "LeetCode 15", "Medium", "Arrays & Strings"),
    "20": ("Valid Parentheses", "LeetCode 20", "Easy", "Stack"),
    "21": ("Merge Two Sorted Lists", "LeetCode 21", "Easy", "Linked List"),
    "23": ("Merge k Sorted Lists", "LeetCode 23", "Hard", "Heap / Priority Queue"),
    "33": ("Search in Rotated Sorted Array", "LeetCode 33", "Medium", "Binary Search"),
    "42": ("Trapping Rain Water", "LeetCode 42", "Hard", "Two Pointers"),
    "53": ("Maximum Subarray (Kadane's)", "LeetCode 53", "Medium", "Dynamic Programming"),
    "56": ("Merge Intervals", "LeetCode 56", "Medium", "Intervals"),
    "70": ("Climbing Stairs", "LeetCode 70", "Easy", "Dynamic Programming"),
    "76": ("Minimum Window Substring", "LeetCode 76", "Hard", "Sliding Window"),
    "79": ("Word Search", "LeetCode 79", "Medium", "Backtracking"),
    "98": ("Validate Binary Search Tree", "LeetCode 98", "Medium", "Trees & Binary Trees"),
    "102": ("Binary Tree Level Order Traversal", "LeetCode 102", "Medium", "Trees & Binary Trees"),
    "121": ("Best Time to Buy and Sell Stock", "LeetCode 121", "Easy", "Arrays & Strings"),
    "124": ("Binary Tree Maximum Path Sum", "LeetCode 124", "Hard", "Trees & Binary Trees"),
    "138": ("Copy List with Random Pointer", "LeetCode 138", "Medium", "Linked List"),
    "139": ("Word Break", "LeetCode 139", "Medium", "Dynamic Programming"),
    "146": ("LRU Cache", "LeetCode 146", "Medium", "LLD / Concurrency"),
    "198": ("House Robber", "LeetCode 198", "Medium", "Dynamic Programming"),
    "200": ("Number of Islands", "LeetCode 200", "Medium", "Graph & BFS/DFS"),
    "206": ("Reverse Linked List", "LeetCode 206", "Easy", "Linked List"),
    "207": ("Course Schedule", "LeetCode 207", "Medium", "Graph & BFS/DFS"),
    "208": ("Implement Trie", "LeetCode 208", "Medium", "Trees & Binary Trees"),
    "215": ("Kth Largest Element in an Array", "LeetCode 215", "Medium", "Heap / QuickSelect"),
    "221": ("Maximal Square", "LeetCode 221", "Medium", "Dynamic Programming"),
    "236": ("Lowest Common Ancestor of a Binary Tree", "LeetCode 236", "Medium", "Trees & Binary Trees"),
    "238": ("Product of Array Except Self", "LeetCode 238", "Medium", "Arrays & Strings"),
    "239": ("Sliding Window Maximum", "LeetCode 239", "Hard", "Monotonic Queue / Deque"),
    "253": ("Meeting Rooms II", "LeetCode 253", "Medium", "Intervals / Heap"),
    "295": ("Find Median from Data Stream", "LeetCode 295", "Hard", "Heap / Priority Queue"),
    "297": ("Serialize and Deserialize Binary Tree", "LeetCode 297", "Hard", "Trees & Binary Trees"),
    "300": ("Longest Increasing Subsequence", "LeetCode 300", "Medium", "Dynamic Programming"),
    "322": ("Coin Change", "LeetCode 322", "Medium", "Dynamic Programming"),
    "347": ("Top K Frequent Elements", "LeetCode 347", "Medium", "Heap / Priority Queue"),
    "378": ("Kth Smallest Element in a Sorted Matrix", "LeetCode 378", "Medium", "Heap / Priority Queue"),
    "380": ("Insert Delete GetRandom O(1)", "LeetCode 380", "Medium", "LLD / Concurrency"),
    "402": ("Remove K Digits", "LeetCode 402", "Medium", "Monotonic Stack"),
    "417": ("Pacific Atlantic Water Flow", "LeetCode 417", "Medium", "Graph & BFS/DFS"),
    "460": ("LFU Cache", "LeetCode 460", "Hard", "LLD / Concurrency"),
    "543": ("Diameter of Binary Tree", "LeetCode 543", "Easy", "Trees & Binary Trees"),
    "545": ("Boundary Traversal of Binary Tree", "LeetCode 545", "Medium", "Trees & Binary Trees"),
    "560": ("Subarray Sum Equals K", "LeetCode 560", "Medium", "Prefix Sum / Hash"),
    "621": ("Task Scheduler", "LeetCode 621", "Medium", "Heap / Greedy"),
    "739": ("Daily Temperatures", "LeetCode 739", "Medium", "Monotonic Stack"),
    "767": ("Reorganize String", "LeetCode 767", "Medium", "Heap / Greedy"),
    "875": ("Koko Eating Bananas", "LeetCode 875", "Medium", "Binary Search"),
    "994": ("Rotting Oranges", "LeetCode 994", "Medium", "Graph & BFS/DFS"),
    "1011": ("Capacity to Ship Packages Within D Days", "LeetCode 1011", "Medium", "Binary Search"),
    "1167": ("Minimum Cost to Connect Sticks", "LeetCode 1167", "Medium", "Heap / Priority Queue")
}

with open('data/experiences.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print(f"Total experiences loaded: {len(data)}")

enriched_count = 0
total_new_questions = 0

for exp in data:
    text = exp.get("full_text", "")
    title = exp.get("title", "")
    combined = f"{title}\n{text}"
    
    found_questions = []
    seen_keys = set()
    
    # 1. Match LeetCode URLs
    for slug in re.findall(r'leetcode\.com/problems/([a-z0-9\-]+)', combined, re.I):
        s_low = slug.lower()
        if s_low in SLUG_META and s_low not in seen_keys:
            seen_keys.add(s_low)
            name, lc, diff, cat = SLUG_META[s_low]
            found_questions.append({
                "name": name,
                "leetcode_equivalent": lc,
                "difficulty": diff,
                "category": cat,
                "description": f"Encountered in Amazon interview round: {title}",
                "code_snippet": ""
            })

    # 2. Match LeetCode Numbers: e.g. LC 402, LeetCode 253, LC#739
    for m in re.finditer(r'(?:(?:LC|LeetCode)\s*#?\s*(\d{1,4})(?:\s*[:\-–—]\s*([A-Za-z0-9\s\-]+?))?(?=\n|\r|\.|\)|$))', combined, re.I):
        num = m.group(1)
        name_hint = m.group(2).strip() if m.group(2) else ""
        if num in LC_NUM_MAP and num not in seen_keys:
            seen_keys.add(num)
            name, lc, diff, cat = LC_NUM_MAP[num]
            found_questions.append({
                "name": name,
                "leetcode_equivalent": lc,
                "difficulty": diff,
                "category": cat,
                "description": f"Asked in candidate's interview loop: {name_hint or name}",
                "code_snippet": ""
            })
        elif name_hint and len(name_hint) > 3 and num not in seen_keys:
            seen_keys.add(num)
            found_questions.append({
                "name": f"{name_hint} (LeetCode {num})",
                "leetcode_equivalent": f"LeetCode {num}",
                "difficulty": "Medium",
                "category": "Algorithms & Problem Solving",
                "description": f"Amazon coding round: {name_hint}",
                "code_snippet": ""
            })

    # 3. Match Known Top Amazon LeetCode Problems by Name
    named_problems = {
        "trapping rain water": ("Trapping Rain Water", "LeetCode 42", "Hard", "Two Pointers"),
        "lru cache": ("LRU Cache", "LeetCode 146", "Medium", "LLD / Concurrency"),
        "lfu cache": ("LFU Cache", "LeetCode 460", "Hard", "LLD / Concurrency"),
        "course schedule": ("Course Schedule", "LeetCode 207", "Medium", "Graph & BFS/DFS"),
        "course schedule ii": ("Course Schedule II", "LeetCode 210", "Medium", "Graph & BFS/DFS"),
        "rotting oranges": ("Rotting Oranges", "LeetCode 994", "Medium", "Graph & BFS/DFS"),
        "merge intervals": ("Merge Intervals", "LeetCode 56", "Medium", "Intervals"),
        "meeting rooms ii": ("Meeting Rooms II", "LeetCode 253", "Medium", "Intervals"),
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

    low_combined = combined.lower()
    for np_key, (np_name, np_lc, np_diff, np_cat) in named_problems.items():
        if np_key not in seen_keys:
            if re.search(r'\b' + re.escape(np_key) + r'\b', low_combined):
                seen_keys.add(np_key)
                found_questions.append({
                    "name": np_name,
                    "leetcode_equivalent": np_lc,
                    "difficulty": np_diff,
                    "category": np_cat,
                    "description": f"Target problem identified in candidate interview loop: {np_name}",
                    "code_snippet": ""
                })

    # 4. Match System Design / LLD
    for m in re.finditer(r'\b(?:Design|Implement)\s+((?:Amazon\s+)?[A-Z][a-zA-Z0-9\s\-]{4,50}(?:System|Service|Platform|Cache|Locker|Scheduler|Autocomplete|Rate Limiter|API|Storage|Search|Streaming|DJ|Player|Game|Elevator|Parking))', combined):
        sd_name = f"Design {m.group(1).strip()}"
        key = sd_name.lower()
        if key not in seen_keys and len(sd_name) < 70:
            seen_keys.add(key)
            is_lld = any(kw in sd_name.lower() for kw in ["cache", "parking", "elevator", "locker", "game", "player", "scheduler"])
            found_questions.append({
                "name": sd_name,
                "leetcode_equivalent": "",
                "difficulty": "Hard" if not is_lld else "Medium",
                "category": "Low-Level Design (LLD)" if is_lld else "System Design (HLD)",
                "description": f"Architecture and component design question in interview loop: {sd_name}",
                "code_snippet": ""
            })

    # 5. Check if we found specific questions and if rounds has generic fallback
    if found_questions:
        rounds = exp.get("rounds", [])
        has_generic = any(
            any(generic in (q if isinstance(q, str) else q.get('name', '')) 
                for generic in ['Data Structures & Algorithms problem', 'Coding Problem / Technical Discussion', 'Amazon Leadership Principles discussion', 's on Hackerrank'])
            for r in rounds for q in r.get('questions', [])
        )
        
        if has_generic or not rounds:
            enriched_count += 1
            total_new_questions += len(found_questions)
            
            # Replace generic questions in rounds with found questions
            if not rounds:
                exp["rounds"] = [{
                    "round_name": "Technical Assessment",
                    "questions": found_questions,
                    "details": exp.get("summary", "")
                }]
            else:
                # Distribute found questions into rounds
                q_idx = 0
                for r in rounds:
                    # Clean out generic questions
                    clean_qs = [
                        q for q in r.get("questions", [])
                        if not any(g in (q if isinstance(q, str) else q.get('name', '')) 
                                   for g in ['Data Structures & Algorithms problem', 'Amazon Leadership Principles discussion', 'Coding Problem / Technical Discussion', 's on Hackerrank'])
                    ]
                    # Add discovered question
                    if q_idx < len(found_questions):
                        clean_qs.append(found_questions[q_idx])
                        q_idx += 1
                    
                    # If still empty, add default LP if round was generic
                    if not clean_qs and q_idx < len(found_questions):
                        clean_qs.append(found_questions[q_idx])
                        q_idx += 1
                        
                    if clean_qs:
                        r["questions"] = clean_qs

print(f"\n[+] Successfully enriched {enriched_count} interview experiences with {total_new_questions} specific real questions!")

# Save to data/experiences.json and ui/experiences.json
with open('data/experiences.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

with open('ui/experiences.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"[+] Successfully saved updated dataset to data/experiences.json and ui/experiences.json")
