import json

data_path = r"D:\Ai\leetcode\data\experiences.json"
ui_data_path = r"D:\Ai\leetcode\ui\experiences.json"

with open(data_path, "r", encoding="utf-8") as f:
    data = json.load(f)

for item in data:
    # Ensure backward compatible fields for all items
    if "post_date" in item and "date" not in item:
        item["date"] = item["post_date"]
    if "votes" in item and "upvotes" not in item:
        item["upvotes"] = item["votes"]
    
    # Specific targeted enrichments for 6493437
    if str(item.get("id", "")) == "6493437":
        item["title"] = "Amazon SDE-2 Interview Experience | 2.8 YOE | Chennai"
        item["role"] = "SDE-2"
        item["location"] = "Chennai / Gurgaon, India"
        item["outcome"] = "Offer"
        item["yoe"] = "2.8 Years"
        item["current_company"] = "Product MNC"
        item["votes"] = 14
        item["upvotes"] = 14
        item["views"] = 840
        item["post_date"] = "2025-03-04"
        item["date"] = "2025-03-04"
        item["url"] = "https://leetcode.com/discuss/interview-experience/6493437/amazon-sde-2-interview-experience-2-8-yoe-chennai"
        item["leadership_principles"] = [
            "Have Backbone; Disagree and Commit",
            "Customer Obsession",
            "Invent and Simplify",
            "Deliver Results",
            "Ownership"
        ]
        item["rounds"] = [
            {
                "round_name": "Round 1: Online Assessment (OA)",
                "round_type": "Online Assessment",
                "questions": [
                    {
                        "name": "OA Coding Problem 1 (Medium-Hard)",
                        "difficulty": "Medium",
                        "category": "Algorithms",
                        "description": "Solved completely with 100% test cases passing."
                    },
                    {
                        "name": "OA Coding Problem 2 (Medium-Hard)",
                        "difficulty": "Hard",
                        "category": "Algorithms",
                        "description": "Passed 11/17 test cases under strict execution time limit."
                    },
                    {
                        "name": "Work Simulation & Architecture Scenarios",
                        "difficulty": "Medium",
                        "category": "System Design & LP",
                        "description": "Situational engineering decisions, design approach evaluation, and Amazon work culture questions."
                    }
                ],
                "details": "Section 1 consisted of 2 medium/hard coding questions. Solved 1 completely, 11/17 test cases for the second. Section 2 had design based scenarios. Section 3 evaluated behavioral and LP traits."
            },
            {
                "round_name": "Round 2: Technical Onsite - DSA & Problem Solving (1 hr 10 min)",
                "round_type": "Data Structures & Algorithms",
                "duration": "1 hr 10 min",
                "interviewer": "SDE-2 / Senior SDE",
                "questions": [
                    {
                        "name": "Boundary Traversal of Binary Tree",
                        "leetcode_equivalent": "LeetCode 545 - Boundary of Binary Tree",
                        "difficulty": "Medium",
                        "category": "Trees / Traversal",
                        "description": "Print all boundary nodes of a binary tree counterclockwise (root -> left boundary -> leaves -> right boundary). Candidate gave initial 3-traversal solution, then optimized using preorder traversal to print left and all leaves in one go."
                    },
                    {
                        "name": "Number of Islands in 01 Matrix -> Number of Islands II",
                        "leetcode_equivalent": "LeetCode 200 / LeetCode 305",
                        "difficulty": "Medium",
                        "category": "Graphs / BFS / Disjoint Set Union",
                        "description": "Find number of connected components in 01 grid. Interviewer altered adjacency criteria, then evolved into dynamic additions of land (Number of Islands II) where optimal approach and time complexity were discussed."
                    }
                ],
                "lp_questions": [
                    "Tell me about a situation where you had to make a decision without having all the information (Dealing with Ambiguity / Bias for Action)."
                ],
                "details": "General introduction, then Binary Tree Boundary Traversal. Optimized traversal on interviewer hint. Then Number of Islands with dynamic modifications. Concluded with LP behavioral questions."
            },
            {
                "round_name": "Round 3: System Design - LLD & HLD (1 hr)",
                "round_type": "System Design",
                "duration": "1 hr",
                "questions": [
                    {
                        "name": "Low Level Design: File Filtering System",
                        "difficulty": "Medium",
                        "category": "Object-Oriented Design (LLD)",
                        "description": "Design an extensible file filtering system to filter files by extension, size, and custom metadata. Incorporates Strategy / Filter design patterns with extensible chaining."
                    },
                    {
                        "name": "High Level Design: File Synchronization Service",
                        "difficulty": "Hard",
                        "category": "Distributed Systems (HLD)",
                        "description": "Architect a Dropbox/Google Drive style file synchronization platform. Emphasized presenting multiple component options (e.g. metadata storage, change detection, chunking) with trade-offs."
                    }
                ],
                "lp_questions": [
                    "Tell me about a time you made a significant mistake and how you rectified it (Ownership & Earn Trust)."
                ],
                "details": "Started with LLD for File Filtering System (iterated to correct design after initial misunderstanding). Then HLD of File Synchronization Service with deep trade-off analysis for each architectural choice."
            },
            {
                "round_name": "Round 4: Hiring Manager Round (1 hr in-person)",
                "round_type": "Hiring Manager & Leadership",
                "duration": "1 hr",
                "interviewer": "Software Development Manager (SDM)",
                "questions": [
                    {
                        "name": "Resume, Architectural Deep Dive & Conflict Resolution",
                        "difficulty": "Medium",
                        "category": "Leadership & Architecture",
                        "description": "Deep examination of previous project contributions at MNC, past technical challenges, and conflict handling."
                    }
                ],
                "lp_questions": [
                    "Tell me about a time you had a conflict with a peer or manager and how you reached a resolution.",
                    "Describe a high-stakes project delivery under tight constraints."
                ],
                "details": "Extensive mixture of situation-based, resume-based, and previous work-related questions with Amazon Leadership Principles embedded throughout."
            },
            {
                "round_name": "Round 5: Bar Raiser (1 hr virtual)",
                "round_type": "Bar Raiser & System Design",
                "duration": "1 hr",
                "interviewer": "Bar Raiser (External Senior Leader)",
                "questions": [
                    {
                        "name": "HLD: Battery Optimization Service for Amazon Platforms",
                        "difficulty": "Hard",
                        "category": "Distributed Systems / Mobile Infrastructure",
                        "description": "Architect a battery optimization platform for Amazon mobile clients to minimize background drain, batch telemetry and network calls, and throttle requests based on power state."
                    },
                    {
                        "name": "HLD: Database Migration from RDBMS to NoSQL (Zero Downtime)",
                        "difficulty": "Hard",
                        "category": "Databases & Storage",
                        "description": "Migrate production data from RDBMS to NoSQL database while maintaining both high availability and consistency, using dual-write, change data capture (CDC), and reconciliation."
                    }
                ],
                "lp_questions": [
                    "Tell me about a time you had to push back on a key technical or architectural decision.",
                    "Give an example of when you had to dive deep to uncover the root cause of an elusive issue."
                ],
                "details": "Conducted virtually 2 days after on-site rounds. Recruiter previously mentioned coding, but interviewer conducted two deep distributed system design questions (Battery Optimization & RDBMS to NoSQL migration) plus LP questions."
            }
        ]
        item["summary"] = "Amazon SDE-2 interview experience for Chennai/Gurgaon (2.8 YOE). Included OA, DSA (Tree Boundary, Number of Islands II), System Design (File Filter LLD, File Sync HLD), Hiring Manager, and Bar Raiser (Battery Optimization HLD, RDBMS to NoSQL Migration). Candidate received Offer."
        item["tips"] = [
            "For Tree and Matrix problems, discuss your time/space complexity and multiple traversals before coding.",
            "For SDE-2 System Design, don't just state a single solution—always present multiple options (e.g., Push vs Pull, RDBMS vs NoSQL) and explain your rationale.",
            "Bar Raiser interviews can pivot unexpectedly: be prepared for High Level System Design even if recruiter indicates coding.",
            "Prepare 2 distinct STAR stories with quantitative impact for each Amazon Leadership Principle."
        ]

with open(data_path, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

with open(ui_data_path, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print("Successfully updated experiences.json!")
