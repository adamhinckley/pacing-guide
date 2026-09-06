#!/usr/bin/env python3
"""Build pacing-data.js from the spreadsheet and Gospel Library catalog."""

from __future__ import annotations

import csv
import json
import re
from datetime import date, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CSV_PATH = ROOT / "data" / "pacing-guide.csv"
LESSONS_PATH = ROOT / "data" / "lessons.json"
OUT_PATH = ROOT / "pacing-data.js"

BASE = "https://www.churchofjesuschrist.org"
MANUAL = f"{BASE}/study/manual/old-testament-seminary-manual-2026"
YEAR = 2026

CFM_TITLES = {
    "Job": "Yet Will I Trust in Him",
    "Psalms 1–2": "The Lord Is My Shepherd",
    "Psalms 49": "I Will Declare What He Hath Done for My Soul",
    "Psalms 102": "Let Every Thing That Hath Breath Praise the Lord",
    "Proverbs": "He Shall Direct Thy Paths",
    "Isaiah 1–12": "God Is My Salvation",
    "Isaiah 13": "A Marvellous Work and a Wonder",
    "Isaiah 40": "Comfort Ye My People",
    "Isaiah 50": "He Hath Borne Our Griefs, and Carried Our Sorrows",
    "Isaiah 58": "The Redeemer Shall Come to Zion",
    "Jeremiah 1": "Before I Formed Thee in the Belly I Knew Thee",
    "Jeremiah 31": "I Will Turn Their Mourning into Joy",
    "Ezekiel": "A New Spirit Will I Put within You",
    "Daniel": "There Is No Other God That Can Deliver",
    "Hosea": "I Will Love Them Freely",
    "Amos": "Seek the Lord, and Ye Shall Live",
    "Micah": "He Delighteth in Mercy",
    "Haggai": "Holiness unto the Lord",
    "Malachi": "I Have Loved You, Saith the Lord",
}

WEEK_OVERVIEWS = {
    "Job": f"{MANUAL}/32-job/320-overview",
    "Psalms 1–2": f"{MANUAL}/33-psalms-1-46/330-overview",
    "Psalms 49": f"{MANUAL}/34-psalms-49-86/340-overview",
    "Psalms 102": f"{MANUAL}/35-psalms-102-150/350-overview",
    "Proverbs": f"{MANUAL}/36-proverbs-ecclesiastes/360-overview",
    "Isaiah 1–12": f"{MANUAL}/37-isaiah-1-12/370-overview",
    "Isaiah 13": f"{MANUAL}/38-isaiah-13-35/380-overview",
    "Isaiah 40": f"{MANUAL}/39-isaiah-40-49/390-overview",
    "Isaiah 50": f"{MANUAL}/40-isaiah-50-57/400-overview",
    "Isaiah 58": f"{MANUAL}/41-isaiah-58-66/410-overview",
    "Jeremiah 1": f"{MANUAL}/42-jeremiah-1-20/420-overview",
    "Jeremiah 31": f"{MANUAL}/43-jeremiah-lamentations/430-overview",
    "Ezekiel": f"{MANUAL}/44-ezekiel/440-overview",
    "Daniel": f"{MANUAL}/45-daniel/450-overview",
    "Hosea": f"{MANUAL}/46-hosea-joel/460-overview",
    "Amos": f"{MANUAL}/47-amos-jonah/470-overview",
    "Micah": f"{MANUAL}/48-micah-zephaniah/480-overview",
    "Haggai": f"{MANUAL}/49-haggai-zechariah/490-overview",
    "Malachi": f"{MANUAL}/50-malachi/500-overview",
}


def clean_space(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "").replace("\xa0", " ")).strip()


def normalize_cfm(text: str) -> str:
    text = clean_space(text).replace(" - ", "–").replace(" -", "–")
    text = text.replace("–", "–").replace("-", "–")
    return text


def cfm_key(cfm: str) -> str:
    compact = normalize_cfm(cfm)
    for key in CFM_TITLES:
        if compact.startswith(key) or key in compact[:40]:
            return key
    first = compact.split(";")[0].split(",")[0].strip()
    return first


def lesson_kind(title: str, numbers: list[int]) -> str:
    lower = title.lower()
    if numbers and all(n >= 161 for n in numbers):
        return "life"
    if "doctrinal mastery" in lower:
        return "mastery"
    if "assess your learning" in lower:
        return "assess"
    if "life preparation" in lower:
        return "life"
    return "scripture"


def parse_lesson_numbers(*parts: str) -> list[int]:
    text = " ".join(p for p in parts if p)
    numbers: list[int] = []
    for match in re.finditer(r"#\s*(\d+)(?:\s*[-–]\s*(\d+))?", text):
        start = int(match.group(1))
        end = int(match.group(2)) if match.group(2) else start
        if end < start:
            end = start
        # Guard against accidental huge ranges
        if end - start > 20:
            end = start
        for n in range(start, end + 1):
            if n not in numbers:
                numbers.append(n)
    return numbers


def main() -> None:
    catalog_items = json.loads(LESSONS_PATH.read_text())
    catalog: dict[int, dict] = {}
    for item in catalog_items:
        match = re.match(r"Lesson (\d+)[—–-]\s*(.*)", item["title"])
        if not match:
            continue
        number = int(match.group(1))
        catalog[number] = {
            "number": number,
            "title": match.group(2).strip(),
            "fullTitle": item["title"].replace("—", " – "),
            "url": BASE + item["href"] + "?lang=eng",
        }

    weeks = []
    current = None
    with CSV_PATH.open(newline="", encoding="utf-8") as handle:
        reader = csv.reader(handle)
        header_seen = False
        for row in reader:
            if not row:
                continue
            if not header_seen:
                if row[0].strip().startswith("Come Follow Me"):
                    header_seen = True
                continue

            cfm_raw, date_raw, schedule_raw, notes_raw = (row + [""] * 4)[:4]
            date_raw = clean_space(date_raw)
            schedule = clean_space(schedule_raw)
            notes = clean_space(notes_raw)
            cfm = normalize_cfm(cfm_raw)

            if not date_raw:
                continue
            try:
                day = datetime.strptime(f"{date_raw}-{YEAR}", "%d-%b-%Y").date()
            except ValueError:
                continue

            # Spreadsheet leftover from a prior D&C guide.
            if day.month == 3:
                continue
            if not schedule:
                continue

            if cfm:
                key = cfm_key(cfm)
                current = {
                    "id": f"week-{day.isoformat()}",
                    "cfm": cfm,
                    "cfmTitle": CFM_TITLES.get(key, ""),
                    "overviewUrl": WEEK_OVERVIEWS.get(key, MANUAL),
                    "start": day.isoformat(),
                    "days": [],
                }
                weeks.append(current)
            elif current is None:
                continue

            numbers = parse_lesson_numbers(schedule, notes)
            is_break = bool(re.search(r"no school|break", schedule, re.I))
            lessons = []
            for number in numbers:
                info = catalog.get(number)
                if info:
                    lessons.append(
                        {
                            **info,
                            "kind": lesson_kind(info["fullTitle"], [number]),
                        }
                    )
                else:
                    lessons.append(
                        {
                            "number": number,
                            "title": schedule,
                            "fullTitle": f"Lesson {number}",
                            "url": f"{MANUAL}?lang=eng",
                            "kind": lesson_kind(schedule, [number]),
                        }
                    )

            kind = "break" if is_break else (
                lessons[0]["kind"] if len(lessons) == 1 else (
                    "life" if lessons and all(l["kind"] == "life" for l in lessons) else "scripture"
                )
            )

            label = schedule
            if is_break:
                label = re.sub(r"\s+", " ", schedule)
            elif lessons:
                label = " · ".join(f"{lesson['number']}. {lesson['title']}" for lesson in lessons)

            extra_note = notes
            if extra_note and re.fullmatch(r"(?:#\s*\d+(?:\s*[-–&]\s*#?\s*\d+)*)", extra_note):
                extra_note = ""
            extra_note = re.sub(r"^And\s+", "", extra_note).strip(" ,")
            note_numbers = parse_lesson_numbers(extra_note)
            if extra_note and note_numbers and set(note_numbers).issubset(set(numbers)):
                extra_note = ""

            current["days"].append(
                {
                    "date": day.isoformat(),
                    "schedule": schedule,
                    "label": label,
                    "note": extra_note,
                    "kind": kind,
                    "lessons": lessons,
                }
            )

    payload = {
        "title": "Old Testament Seminary",
        "subtitle": "Fall 2026 pacing guide",
        "manualUrl": MANUAL + "?lang=eng",
        "generated": date.today().isoformat(),
        "weeks": weeks,
    }
    OUT_PATH.write_text(
        "window.PACING = " + json.dumps(payload, indent=2, ensure_ascii=False) + ";\n",
        encoding="utf-8",
    )
    day_count = sum(len(week["days"]) for week in weeks)
    print(f"Wrote {OUT_PATH} ({len(weeks)} weeks, {day_count} class days)")

    import sys

    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from stamp_version import main as stamp_version

    stamp_version()


if __name__ == "__main__":
    main()
