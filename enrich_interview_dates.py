import json
import re
from datetime import datetime

data_path = r"D:\Ai\leetcode\data\experiences.json"
ui_data_path = r"D:\Ai\leetcode\ui\experiences.json"

with open(data_path, "r", encoding="utf-8") as f:
    data = json.load(f)

MONTH_MAP = {
    'jan': 'January', 'feb': 'February', 'mar': 'March', 'apr': 'April',
    'may': 'May', 'jun': 'June', 'jul': 'July', 'aug': 'August',
    'sep': 'September', 'oct': 'October', 'nov': 'November', 'dec': 'December'
}

def clean_date_string(s):
    # Standardize spaces and hyphens
    s = s.replace('–', '-').replace('—', '-')
    s = re.sub(r'\s+', ' ', s).strip()
    return s

def extract_interview_date(item):
    if str(item.get("id", "")) == "6493437":
        return "February - March 2025"

    title = item.get("title", "")
    text = item.get("full_text", "")
    post_date_str = item.get("post_date") or item.get("date") or ""
    post_year = post_date_str.split("-")[0] if post_date_str else "2025"

    # 1. Look for explicit "Interview Date: ..." or "Interview Invitation ... Interview Date: Feb 27 - Mar 3"
    m_iv = re.search(r'Interview Date\s*[:\-]\s*([A-Za-z0-9\s,\-]+?)(?:\n|\r|\.|\*|\(|$)', text, re.IGNORECASE)
    if m_iv:
        val = clean_date_string(m_iv.group(1))
        if 3 <= len(val) <= 25 and any(c.isalpha() for c in val):
            if not any(y in val for y in ["2024", "2025", "2026"]):
                val = f"{val}, {post_year}"
            return val

    # 2. Look for explicit Month + Year in title (e.g., "Feb 2025", "March 2025", "November 2024")
    m_title = re.search(r'\b(Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\s*(20\d\d)?\b', title, re.IGNORECASE)
    if m_title:
        m_prefix = m_title.group(1)[:3].lower()
        month_full = MONTH_MAP.get(m_prefix, m_title.group(1).capitalize())
        year = m_title.group(2) or post_year
        return f"{month_full} {year}"

    # 3. Look for "interview scheduled on <Date>" or "Round 1: ... <Date>"
    m_sched = re.search(r'(?:interview scheduled on|interview date is|took my OA on|interview was on|interview was scheduled for)\s*(\d{1,2}(?:st|nd|rd|th)?\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*|\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{1,2}(?:st|nd|rd|th)?)', text, re.IGNORECASE)
    if m_sched:
        return f"{m_sched.group(1).title()} {post_year}"

    # 4. Fallback to post date formatted nicely: "March 2025" or "November 2024"
    if post_date_str:
        try:
            dt = datetime.strptime(post_date_str[:10], "%Y-%m-%d")
            return dt.strftime("%B %Y")
        except Exception:
            pass

    return "2024-2025"

for item in data:
    item["interview_date"] = extract_interview_date(item)
    if not item.get("post_date") and item.get("date"):
        item["post_date"] = item["date"]
    if not item.get("date") and item.get("post_date"):
        item["date"] = item["post_date"]

with open(data_path, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

with open(ui_data_path, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print("Enriched interview_date across all entries successfully!")
