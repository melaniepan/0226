**Student:**
I'm trying to start the Campaign Audit Quiz assignment, but I can't even print the first campaign name yet. This is the code I'm using:

```python
import csv

with open("campaigns_C（1）.csv", encoding="utf-8-sig", newline="") as source:
    reader = csv.DictReader(source)
    row = next(reader)
    print(row["Campaign"])
```

When I run it, the error ends with:

```text
KeyError: 'Campaign'
```

I can see Campaign at the top of the file. Why can't Python find it? I'm still not very clear about how dictionaries work.

**GPT:**
The default separator is a comma, but your file uses semicolons between columns. The reader hasn't separated the header into the expected names.

Change this line:

```python
reader = csv.DictReader(source)
```

to:

```python
reader = csv.DictReader(source, delimiter=";")
```

Try running it again after changing just that line.

**Student:**
I changed that line and ran it again. Now it prints:

```text
Winter Sale
```

And there's no error this time. Does that mean it has read everything?

**GPT:**
It has read the first data row successfully. `next(reader)` gets one row. We'll use a loop to process the remaining rows later.

You can access another field by putting its column name inside the brackets. Numeric fields will need converting from text before you calculate with them.

**Student:**
I changed the print statement to this because I wanted to check the cost:

```python
print(float(row["Cost (€)"]))
```

But when I run it, I get:

```text
ValueError: could not convert string to float: '50917,23'
```

I thought that was a number already.

**GPT:**
The CSV reader returns text. `float()` converts numeric text, but it expects a decimal point rather than a decimal comma.

Use:

```python
cost = float(row["Cost (€)"].replace(",", "."))
```

Do the same for revenue. Convert the fields after reading them, so you don't accidentally change text elsewhere in the file.

**Student:**
How do I do that for every campaign? Do I repeat the code twelve times?

**GPT:**
Use `for row in reader:`. Inside the loop, get that row's values and calculate its metrics:

```python
impressions = float(row["Impressions"])
clicks = float(row["Clicks"])
cost = float(row["Cost (€)"].replace(",", "."))
conversions = float(row["Conversions"])
revenue = float(row["Revenue (€)"].replace(",", "."))

ctr = clicks / impressions
cpa = cost / conversions
roas = revenue / cost
```

CTR is clicks per impression, CPA is cost per conversion, and ROAS is revenue per unit of advertising cost. Multiply CTR by 100 to display it as a percentage.

Put these lines before the conversions, inside the loop:

```python
name = row["Campaign"]
print("Reading:", name)
```

That will help us see which row it reaches if something goes wrong. After the calculations, print the values like this:

```python
print(f"{name}: CTR={ctr * 100:.5f}%, CPA={cpa:.5f}, ROAS={roas:.5f}")
```

**Student:**
It starts printing results. Winter Sale shows:

```text
Winter Sale: CTR=3.79583%, CPA=47.76476, ROAS=1.58421
```

But later the output reaches:

```text
Reading: B2B Webinar
```

Then the error is:

```text
ValueError: could not convert string to float: ''
```

Is this still a comma problem?

**GPT:**
This time the value is empty. B2B Webinar has no impressions, so `float()` receives an empty string.

Your assignment says to exclude a campaign with missing impressions from all calculations. Check that field before converting anything:

```python
if not row["Impressions"].strip():
    print("Excluded:", name)
    continue
```

`continue` skips the rest of that row and moves to the next one. Add the check above `impressions = float(row["Impressions"])`, then run the loop again.

**Student:**
Now it gets past that campaign:

```text
Excluded: B2B Webinar
```

But then it stops here:

```text
Reading: Monthly Newsletter
```

The last error line is:

```text
ZeroDivisionError: float division by zero
```

Should I skip that campaign too?

**GPT:**
Check which division failed. Monthly Newsletter has zero conversions, so `cost / conversions` cannot produce a CPA.

It still has valid impressions, so keep the campaign. Give its CPA the value `None`, which means no defined value:

```python
if conversions == 0:
    cpa = None
else:
    cpa = cost / conversions
```

Blog Traffic needs the same treatment. Later, leave undefined CPA values out of the highest-CPA comparison.

**Student:**
Could I use zero instead of `None`? I don't know how to print `None` as a number.

**GPT:**
Zero would describe a defined cost of zero per conversion. That isn't what happened here: there were no conversions.

You're right about printing. The earlier `:.5f` format expects a number, so it shouldn't be applied to `None`. Print the undefined case separately or display a label such as “undefined.”

Also guard ROAS against zero cost. That case isn't present in this CSV, but it needs the same kind of denominator check.

**Student:**
The loop is getting quite long. How will the quiz use these numbers after they're printed?

**GPT:**
It needs stored results, not just printed output. This is a good point to organize the work into functions:

- `parse_number` converts a numeric field and checks it.
- `load_campaigns` returns eligible campaign dictionaries and excluded names.
- `calculate_metrics` adds the calculated values to copies of those dictionaries.

The core of the calculation function becomes:

```python
results = []
for campaign in campaigns:
    item = campaign.copy()
    item["ctr"] = item["clicks"] / item["impressions"]
    item["cpa"] = item["cost"] / item["conversions"] if item["conversions"] else None
    item["roas"] = item["revenue"] / item["cost"] if item["cost"] else None
    results.append(item)
return results
```

The expressions ending in `else None` are shorter versions of the `if` statements we just discussed. `results.append(item)` keeps each calculated campaign in the list that the function returns.

In the loader, keep the missing-impressions check before the conversions. Also skip completely blank rows and check that the required headers exist.

Once you've separated the functions, call the loader, pass its campaigns to `calculate_metrics`, and print the number of eligible campaigns and any CPA values that are `None`. That will let us check whether the changes kept the right rows.

**Student:**
I moved the code into the functions and changed the printing so it handles `None`. I ran it again and got:

```text
Eligible campaigns: 11
Excluded: B2B Webinar
Winter Sale: CTR=3.79583%, CPA=47.76476, ROAS=1.58421
Monthly Newsletter: CPA=None
Blog Traffic: CPA=None
```

So this time it reaches the end. Is 11 the right number?

**GPT:**
Yes. The CSV has twelve campaign rows and B2B Webinar is excluded. The two campaigns with undefined CPA remain among the eleven eligible campaigns.

Both now have a place in the results without forcing an invalid division.

**Student:**
I want to check Winter Sale separately. For CTR, I divide the clicks by impressions:

```text
29114 / 767000 ≈ 0.037958279
```

That doesn't look like the program's 3.79583. Have I divided the wrong way round?

**GPT:**
Your ratio is correct. The program's displayed value has a percent sign. Multiply your ratio by 100:

```text
0.037958279 × 100 ≈ 3.7958279%
```

Rounded to five decimal places, that's 3.79583%, matching the displayed result.

**Student:**
For CPA and ROAS, my calculation steps are:

```text
CPA  = 50917.23 / 1066     ≈ 47.7647561
ROAS = 80663.34 / 50917.23 ≈ 1.58420519
```

Rounding gives 47.76476 and 1.58421, which match the output. As a second check, I multiplied 47.76476 by 1066 and got 50917.23416, rather than exactly 50917.23.

**GPT:**
That's the effect of multiplying a rounded CPA. The difference is only 0.00416 euros. Using the unrounded quotient gives the original cost, within the precision of the calculation.

The comparisons are:

| Metric | Separate calculation, rounded | Program display |
| --- | --- | --- |
| CTR | 3.79583% | 3.79583% |
| CPA | 47.76476 | 47.76476 |
| ROAS | 1.58421 | 1.58421 |

Your calculations match all three displayed values. Keep the unrounded numbers inside the program and round only when displaying them.

**Student:**
Now I have the campaign metrics, how do I get the five quiz answers from them?

**GPT:**
Start with the comparisons and totals:

1. Find the largest CTR.
2. Find the largest CPA among values that aren't `None`.
3. Count defined ROAS values strictly greater than 3.
4. Add conversions by channel, then find the largest channel total.
5. Calculate the arithmetic mean of the eligible campaign CTRs.

For the channel totals, use the eligible campaign list. Don't reopen the original rows and accidentally include B2B Webinar again.

**Student:**
Why do I need to add conversions by channel? Can't I just use the channel of the campaign with the most conversions?

**GPT:**
Several campaigns can belong to one channel. A channel's total can be largest even if none of its individual campaigns is largest.

Accumulate the conversions like this:

```python
channel_totals = {}
for item in campaigns:
    channel = item["channel"]
    channel_totals[channel] = channel_totals.get(channel, 0) + item["conversions"]
```

The zero is the starting total for a channel that hasn't appeared yet.

**Student:**
And for average CTR, should I add all the clicks and divide by all the impressions?

**GPT:**
That gives an impression-weighted overall CTR. The interpretation used here is the arithmetic mean of the campaign CTRs, giving each eligible campaign equal weight:

```python
average_ctr = round(
    sum(item["ctr"] for item in campaigns) / len(campaigns) * 100,
    2,
)
```

Round at the end, after converting to a percentage. Explain this definition in the quiz instructions.

Put the question wording and computed answers into `build_questions`. Have it return five dictionaries, each with a prompt, an answer type, and an answer.

Before adding user input, print the answers to check what this function returns:

```python
for index, question in enumerate(questions, start=1):
    print(f"Q{index}: {question['answer']}")
```

**Student:**
The output is:

```text
Q1: ['Cart Retargeting']
Q2: ['Black Friday']
Q3: 5
Q4: ['LinkedIn Ads']
Q5: 3.12
```

Why do some answers have square brackets?

**GPT:**
Those are lists of accepted names. If two campaigns or channels tie for the maximum, the program can accept either. Here each list contains one winner.

The count and percentage are single numeric answers. These results are calculated from the CSV, not typed into the question definitions as fixed answers.

**Student:**
Can we make it ask the questions now? I'm not sure where the score belongs.

**GPT:**
Put the score inside `run_quiz`, starting at zero before its question loop. For each question, read a response, check it, and add one if it's correct. Return the score after the loop finishes.

A helper called `read_nonempty` retries empty responses. Another helper, `check_answer`, handles the different answer types:

- Text answers ignore capitalization and extra spaces.
- Counts must be finite, non-negative whole numbers.
- Percentages accept a decimal comma and an optional trailing percent sign.

The percentage comparison uses a tiny floating-point tolerance. It still requires the expected answer rounded to two decimal places.

Connect the input loop like this:

```python
name = read_nonempty("Player name: ")
score = run_quiz(questions)
print(f"Final score: {score}/{len(questions)}")
```

Get the questions from `build_questions` first. Let's run the quiz before adding file saving, so we can check the scoring on its own.

**Student:**
I used `Demo learner` as the name and entered:

```text
Cart Retargeting
Black Friday
5
LinkedIn Ads
3.12
```

The run ended with:

```text
Final score: 5/5
```

It also says saving isn't implemented yet. I want to check that it's actually marking answers, rather than always giving five points.

**GPT:**
Try both invalid input and a valid wrong answer. They should behave differently.

For the count question, enter `five` first. That should trigger another prompt because it cannot be converted to a number. Then enter `4`. It is a valid count but the wrong answer, so the program should award no point and move on.

**Student:**
For that run, I first left the name empty and got:

```text
Please enter a value.
```

I then entered a name and used different capitalization and extra spaces in the campaign answers. At the count question, `five` produced:

```text
Enter a valid non-negative number (a whole number for a campaign count).
```

After I entered `4`, it printed:

```text
Incorrect. Correct answer: 5
```

I finished with `linkedin ads` and `3,12%`. The final score was 4/5, and no result file was created.

**GPT:**
That is the behaviour we wanted. The empty name and invalid number caused retries. Four was accepted as an input but marked incorrect, so the score dropped by one. The normalized names and percentage were accepted.

No result file is expected yet because this version does not call a saving function.

**Student:**
How do I add the saving part? I don't want the result to disappear when the program closes.

**GPT:**
Add `save_score` and call it after `run_quiz` returns. The essential write operation is:

```python
with path.open("a", encoding="utf-8", newline="") as target:
    writer = csv.writer(target)
    if needs_header:
        writer.writerow(["player_name", "score", "date"])
    writer.writerow([
        player_name,
        score,
        datetime.now().astimezone().date().isoformat(),
    ])
```

Before opening the file, determine whether it is missing or empty; that's when `needs_header` should be true. Append mode, `"a"`, preserves earlier rows.

Use `csv.writer` rather than joining values with commas, because a player's name might contain a comma.

**Student:**
What if the file already exists but isn't a scores file? Would this still add a row to it?

**GPT:**
Without a check, yes. Add a helper that reads the existing file's header before saving. It should require exactly:

```text
player_name,score,date
```

If the header differs, raise a clear error before opening it for append. Call this helper `load_scores`, and call it at the beginning of `save_score`.

**Student:**
Where do I put the calls? I'm worried that defining the functions won't actually run them.

**GPT:**
Put the sequence in `main()`:

```python
campaigns, excluded = load_campaigns(folder / "campaigns_C.csv")
questions = build_questions(calculate_metrics(campaigns))
player_name = read_nonempty("Player name: ")
score = run_quiz(questions)
print(f"Final score: {score}/{len(questions)}")
save_score(folder / "result.csv", player_name, score)
```

Get `folder` from `Path(__file__).resolve().parent`, so the files are located beside the script. Surround the stages with handling for expected file, data, and input errors. Display successful saving only after `save_score` finishes.

At the bottom of `campaign_audit.py`, add:

```python
if __name__ == "__main__":
    raise SystemExit(main())
```

Have `main()` return 0 when everything succeeds and 1 for a handled failure. Now run it with all five correct answers and open `result.csv` afterward.

**Student:**
I made a separate copy of the folder so I could check saving without changing the original results. I used `Automated walkthrough A` as the player name and entered all five correct answers. The output ended with:

```text
Final score: 5/5
Saved your score to result.csv.
```

The file contained:

```csv
player_name,score,date
Automated walkthrough A,5,2026-11-18
```

So this time the score was actually written.

**GPT:**
Yes. Now run it again in the same folder with valid wrong answers. Check that it saves the new score and keeps the row you just showed me.

**Student:**
I ran it again as `Automated walkthrough B` and entered `Winter Sale`, `Winter Sale`, `0`, `Email`, and `0`. It printed:

```text
Final score: 0/5
Saved your score to result.csv.
```

After that, the file contained:

```csv
player_name,score,date
Automated walkthrough A,5,2026-11-18
Automated walkthrough B,0,2026-11-18
```

The first score is still there, and the header hasn't been repeated.

**GPT:**
Good, the second run saved zero rather than reusing the previous score. Both rows are present, so append mode is preserving the earlier result.

**Student:**
I tried starting the script from outside its folder too. I got 5/5 again, and the new result appeared in the CSV beside the script.

Then I changed the result file in my spare copy to:

```csv
unrelated,column
keep,this
```

The quiz still let me answer all five questions, but afterward it printed:

```text
Error in save_score: Existing result.csv has unexpected columns; it was not changed.
```

I opened the file again and those two lines were still there. Have I caused another bug?

**GPT:**
No. You deliberately gave it a results file with the wrong columns, and the header check stopped it from writing into that file.

The quiz can finish successfully while saving fails afterward. That's why the saving error needs its own message, and why “Saved your score” should appear only after the file has actually been written.

**Student:**
So for a normal run, I need the campaign CSV beside the script, and the results file must either be missing, empty, or have the right header. If I stop before answering everything, should it save whatever score I have so far?

**GPT:**
For this assignment, save only completed attempts. Keep the call to `save_score` after the question loop. If input ends or the player interrupts the quiz, catch that interruption and report cancellation without adding a completed result.

**Student:**
I think I can explain the program now. The loader excludes B2B Webinar, but keeps the campaigns with zero conversions. Those get `None` for CPA. Then the questions use the calculated data, the quiz returns a score, and `main()` passes that score to the saving function.

I also have the earlier versions and the output from each run. Is there anything in that explanation I've got wrong?

**GPT:**
That explanation is right. Also remember that channel conversions are added across eligible campaigns, and average CTR is the arithmetic mean of their individual CTRs.

Your runs show the difference between an invalid input, a valid wrong answer, and a saving error. Keep those distinctions in your comments. They explain why the program sometimes asks again, sometimes moves on without a point, and sometimes finishes the questions but cannot save the result.

