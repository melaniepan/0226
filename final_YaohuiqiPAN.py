# =============================================================
# Campaign Audit Quiz  —  Session 8 Final Exam
# Mike Castro Demaria — SKEMA Business School — Fall 2026
#

# =============================================================

import csv
import os
from datetime import date

# -------------------------------------------------------------
# Constants: file paths
# -------------------------------------------------------------
INPUT_FILE  = "/workspaces/0226/campaigns_C (1).csv"
OUTPUT_FILE = "result.csv"


# =============================================================
# 1. Read CSV function
#    Input : file path
#    Output: list[dict], each dict is one cleaned campaign
#    Notes:
#      - Delimiter is ';'
#      - The file starts with a BOM (\ufeff) -> handle it
#      - There is an empty column between Conversions and Revenue
#      - Amounts use the European decimal comma
#      - Empty impressions -> store None (excluded later)
# =============================================================
def read_csv(path):
    campaigns = []
    try:
        with open(path, "r", encoding="utf-8-sig", newline="") as f:
            reader = csv.reader(f, delimiter=";")
            rows = list(reader)

        if not rows:
            raise ValueError("CSV file is empty")

        # First row is the header, skip it
        for row in rows[1:]:
            # Skip completely empty rows
            if not row or all(cell.strip() == "" for cell in row):
                continue

            # Row layout:
            # Campaign;Channel;Period;Impressions;Clicks;Cost;Conversions;[empty];Revenue
            # Revenue is at index 8 because of the empty column
            campaign        = row[0].strip()
            channel         = row[1].strip()
            period          = row[2].strip()
            impressions_raw = row[3].strip()
            clicks_raw      = row[4].strip()
            cost_raw        = row[5].strip()
            conversions_raw = row[6].strip()
            revenue_raw     = row[8].strip() if len(row) > 8 else ""

            # --- Data rule 1: empty impressions -> exclude campaign ---
            if impressions_raw == "":
                campaigns.append({
                    "campaign": campaign,
                    "channel": channel,
                    "period": period,
                    "impressions": None,
                    "clicks": None,
                    "cost": None,
                    "conversions": None,
                    "revenue": None,
                })
                continue

            # --- Data rule 3: European decimal comma -> dot ---
            def to_float(s):
                if s == "":
                    return 0.0
                return float(s.replace(",", "."))

            impressions = int(impressions_raw)
            clicks      = int(clicks_raw) if clicks_raw else 0
            cost        = to_float(cost_raw)
            conversions = int(conversions_raw) if conversions_raw else 0
            revenue     = to_float(revenue_raw)

            campaigns.append({
                "campaign": campaign,
                "channel": channel,
                "period": period,
                "impressions": impressions,
                "clicks": clicks,
                "cost": cost,
                "conversions": conversions,
                "revenue": revenue,
            })

        return campaigns

    except FileNotFoundError:
        print(f"[Error] File not found: {path}")
        return []
    except Exception as e:
        print(f"[Error] Failed to read CSV: {e}")
        return []


# =============================================================
# 2. Compute metrics
#    Input : campaigns list
#    Output: each campaign gains ctr / cpa / roas fields
#    Rules:
#      - impressions is None -> campaign excluded entirely
#      - conversions == 0 -> cpa = None (but other metrics kept)
#      - cost == 0 -> cpa / roas set to None to avoid division by zero
# =============================================================
def compute_metrics(campaigns):
    valid = []
    for c in campaigns:
        # Rule 1: empty impressions -> excluded entirely
        if c["impressions"] is None:
            continue

        imp  = c["impressions"]
        clk  = c["clicks"]
        cost = c["cost"]
        conv = c["conversions"]
        rev  = c["revenue"]

        # CTR = clicks / impressions
        ctr = (clk / imp) if imp > 0 else None

        # CPA = cost / conversions (zero conversions -> no CPA)
        cpa = (cost / conv) if conv > 0 else None

        # ROAS = revenue / cost (cost 0 -> cannot compute)
        roas = (rev / cost) if cost > 0 else None

        c["ctr"]  = ctr
        c["cpa"]  = cpa
        c["roas"] = roas
        valid.append(c)

    return valid


# =============================================================
# 3. Compute the five correct answers
#    Input : campaigns with metrics computed
#    Output: dict with the five correct answers
# =============================================================
def compute_answers(campaigns):
    answers = {}

    # Q1: campaign with the best CTR
    best_ctr = max(
        (c for c in campaigns if c["ctr"] is not None),
        key=lambda c: c["ctr"],
    )
    answers["q1"] = best_ctr["campaign"]
    answers["q1_value"] = round(best_ctr["ctr"] * 100, 2)

    # Q2: campaign with the highest CPA (only campaigns that have a CPA)
    with_cpa = [c for c in campaigns if c["cpa"] is not None]
    highest_cpa = max(with_cpa, key=lambda c: c["cpa"])
    answers["q2"] = highest_cpa["campaign"]
    answers["q2_value"] = round(highest_cpa["cpa"], 2)

    # Q3: number of campaigns with ROAS above 3
    answers["q3"] = sum(
        1 for c in campaigns if c["roas"] is not None and c["roas"] > 3
    )

    # Q4: channel with the most total conversions
    channel_conv = {}
    for c in campaigns:
        channel_conv[c["channel"]] = channel_conv.get(c["channel"], 0) + c["conversions"]
    answers["q4"] = max(channel_conv, key=channel_conv.get)
    answers["q4_value"] = channel_conv[answers["q4"]]

    # Q5: average CTR across all campaigns, rounded to two decimals (%)
    ctrs = [c["ctr"] for c in campaigns if c["ctr"] is not None]
    avg_ctr = sum(ctrs) / len(ctrs) if ctrs else 0
    answers["q5"] = round(avg_ctr * 100, 2)   # as a percentage, two decimals

    return answers


# =============================================================
# 4. Interactive function: get the player's name
# =============================================================
def get_player_name():
    while True:
        name = input("Enter your name: ").strip()
        if name:
            return name
        print("Name cannot be empty. Please try again.")


# =============================================================
# 5. Answer-checking helpers (case/space insensitive)
# =============================================================
def normalize(s):
    return str(s).strip().lower()


def check_text_answer(user, correct):
    return normalize(user) == normalize(correct)


def check_number_answer(user, correct, tol=0.01):
    try:
        return abs(float(user.replace(",", ".")) - float(correct)) <= tol
    except ValueError:
        return False


# =============================================================
# 6. Main game logic: ask the five questions and keep the score
# =============================================================
def play_quiz(answers):
    score = 0
    total = 5

    # ---------- Question 1 ----------
    print("\n--- Question 1 ---")
    print("Which campaign has the best CTR?")
    u = input("Your answer: ")
    if check_text_answer(u, answers["q1"]):
        print("Correct!")
        score += 1
    else:
        print(f"Wrong. The correct answer is: {answers['q1']} (CTR = {answers['q1_value']}%)")

    # ---------- Question 2 ----------
    print("\n--- Question 2 ---")
    print("Which campaign has the highest CPA?")
    u = input("Your answer: ")
    if check_text_answer(u, answers["q2"]):
        print("Correct!")
        score += 1
    else:
        print(f"Wrong. The correct answer is: {answers['q2']} (CPA = {answers['q2_value']} EUR)")

    # ---------- Question 3 ----------
    print("\n--- Question 3 ---")
    print("How many campaigns have a ROAS above 3?")
    u = input("Your answer (number): ")
    if check_number_answer(u, answers["q3"]):
        print("Correct!")
        score += 1
    else:
        print(f"Wrong. The correct answer is: {answers['q3']}")

    # ---------- Question 4 ----------
    print("\n--- Question 4 ---")
    print("Which channel generated the most conversions in total?")
    u = input("Your answer: ")
    if check_text_answer(u, answers["q4"]):
        print("Correct!")
        score += 1
    else:
        print(f"Wrong. The correct answer is: {answers['q4']} ({answers['q4_value']} conversions)")

    # ---------- Question 5 ----------
    print("\n--- Question 5 ---")
    print("What is the average CTR across all campaigns, rounded to two decimals?")
    print("(Answer as a percentage, e.g. 7.12 means 7.12%)")
    u = input("Your answer (%): ")
    if check_number_answer(u, answers["q5"]):
        print("Correct!")
        score += 1
    else:
        print(f"Wrong. The correct answer is: {answers['q5']}%")

    return score, total


# =============================================================
# 7. Display the final score
# =============================================================
def show_score(name, score, total):
    print("\n" + "=" * 50)
    print(f"Final score: {score} / {total}")
    pct = score / total * 100
    print(f"Percentage: {pct:.1f}%")
    if pct == 100:
        print("Perfect! Excellent!")
    elif pct >= 60:
        print("Good job!")
    else:
        print("Keep practicing!")
    print("=" * 50)


# =============================================================
# 8. Write result.csv
#    Input : player name, score, date
#    Output: append to result.csv (with header if the file is new)
# =============================================================
def write_result(name, score, total):
    today = date.today().isoformat()
    try:
        file_exists = os.path.exists(OUTPUT_FILE)
        with open(OUTPUT_FILE, "a", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(["player", "score", "total", "date"])
            writer.writerow([name, score, total, today])
        print(f"\nResult saved to: {OUTPUT_FILE}")
    except Exception as e:
        print(f"[Error] Failed to write result file: {e}")


# =============================================================
# 9. main: orchestrate all functions
# =============================================================
def main():
    print("=" * 50)
    print(" Campaign Audit Quiz — Session 8 Final Exam")
    print("=" * 50)

    # Step 1: read CSV
    campaigns = read_csv(INPUT_FILE)
    if not campaigns:
        print("No data loaded. Exiting.")
        return

    # Step 2: compute metrics
    campaigns = compute_metrics(campaigns)
    print(f"\nLoaded {len(campaigns)} valid campaigns (non-empty impressions).")

    # Compute the five correct answers
    answers = compute_answers(campaigns)

    # Step 3: get the player's name + ask the questions
    name = get_player_name()
    score, total = play_quiz(answers)

    # Step 5: display the score
    show_score(name, score, total)

    # Step 6: write result.csv
    write_result(name, score, total)


# =============================================================
# Entry point
# =============================================================
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nProgram interrupted by the user.")
    except Exception as e:
        # Safety net: never crash
        print(f"\n[Unexpected error] {type(e).__name__}: {e}")