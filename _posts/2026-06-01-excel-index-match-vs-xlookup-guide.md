---
layout: post
title: "INDEX MATCH vs XLOOKUP: A Practical Guide for Excel Users"
date: 2026-06-01
categories: [excel]
description: "Compare INDEX MATCH and XLOOKUP. Learn when to use each function, their strengths, limitations, and step-by-step examples for your spreadsheets."
---

## INDEX MATCH vs XLOOKUP: A Practical Guide for Excel Users

If you've worked with large datasets in Excel, you've probably reached for VLOOKUP at some point. But VLOOKUP has real limitations. That's where INDEX MATCH and XLOOKUP come in. Both solve problems that VLOOKUP creates, but they work differently and have different strengths.

This guide cuts through the confusion. You'll learn exactly when to use each function, see working examples, and understand which approach suits your specific workflow.

## What's the problem with VLOOKUP?

Before we compare INDEX MATCH and XLOOKUP, it's worth understanding why these alternatives exist.

VLOOKUP has three main limitations:

1. **It only searches left-to-right** — Your lookup column must be to the left of the column you want to return. In many real datasets, this doesn't match your actual data structure.

2. **It returns the first match only** — If your data contains duplicates, VLOOKUP can't distinguish between them or return multiple matches.

3. **It breaks when you insert columns** — Add a new column to your source data and your VLOOKUP column reference shifts, breaking your formula.

Both INDEX MATCH and XLOOKUP address these issues, but differently.

## Understanding INDEX MATCH

INDEX MATCH is a combination of two functions that work together.

**INDEX** returns a value from a specific position in a range. Syntax:
```
=INDEX(array, row_number, [column_number])
```

**MATCH** finds the position of a value within a range. Syntax:
```
=MATCH(lookup_value, lookup_array, [match_type])
```

Combine them and MATCH finds the position, then INDEX returns the value at that position.

### Why use INDEX MATCH?

- Works in any Excel version from Excel 2007 onwards
- Searches in any direction (left, right, up, down)
- More flexible than VLOOKUP for complex data structures
- Doesn't break if you insert columns in your source data
- You can use it across multiple sheets and workbooks

### When INDEX MATCH struggles

- The syntax is more complex than VLOOKUP
- You need to understand how both functions work
- It's slower than XLOOKUP on very large datasets (though you won't notice unless you have thousands of formulas)
- Multiple matches still require additional functions like FILTER

## Understanding XLOOKUP

XLOOKUP is the newer alternative, introduced in Excel 365 and Excel 2021. It's a single function designed to replace VLOOKUP, HLOOKUP, and much of what INDEX MATCH does.

Syntax:
```
=XLOOKUP(lookup_value, lookup_array, return_array, [if_not_found], [match_mode], [search_mode])
```

### Why use XLOOKUP?

- Simpler syntax than INDEX MATCH
- Searches in any direction (like INDEX MATCH)
- Built-in error handling (the `if_not_found` parameter)
- Faster performance on large datasets
- Returns multiple matches when combined with FILTER
- Microsoft's recommended replacement for VLOOKUP

### When XLOOKUP won't work

- You're using Excel 2019 or earlier
- Your organisation uses Excel for Mac (not available in some versions)
- You need to share files with users on older Excel versions
- Your dataset is on an older version of Excel that doesn't support the function

## Head-to-Head: INDEX MATCH vs XLOOKUP

### Scenario 1: Basic left-to-right lookup

**Your data:**
- Column A: Employee ID
- Column B: Department
- Column C: Salary
- You want to find the salary for employee ID "E045"

**Using INDEX MATCH:**
```
=INDEX(C:C, MATCH("E045", A:A, 0))
```

**Using XLOOKUP:**
```
=XLOOKUP("E045", A:A, C:C)
```

Winner: **XLOOKUP** — one function instead of two, instantly readable.

### Scenario 2: Right-to-left lookup

**Your data:**
- Column A: Product code
- Column B: Product name
- Column C: Category
- Column D: Supplier ID
- You want to find the category for supplier ID "SUP789"

With VLOOKUP, you'd be stuck. With these two:

**Using INDEX MATCH:**
```
=INDEX(C:C, MATCH("SUP789", D:D, 0))
```

**Using XLOOKUP:**
```
=XLOOKUP("SUP789", D:D, C:C)
```

Winner: **Tie** — both work equally well. XLOOKUP is slightly simpler to read.

### Scenario 3: Handling errors gracefully

Your data might not always contain matches. You need to return a meaningful message instead of `#N/A`.

**Using INDEX MATCH:**
```
=IFERROR(INDEX(C:C, MATCH("E045", A:A, 0)), "Not found")
```

**Using XLOOKUP:**
```
=XLOOKUP("E045", A:A, C:C, "Not found")
```

Winner: **XLOOKUP** — the error handling is built in.

### Scenario 4: Multiple matches (return multiple results)

You want to find all employees in a specific department, not just the first one.

**Using INDEX MATCH with FILTER:**
```
=FILTER(A:A, B:B="Finance")
```

(Note: This requires FILTER function, available in Excel 365)

**Using XLOOKUP with FILTER:**
```
=FILTER(C:C, A:A=XLOOKUP("E045", A:A, A:A))
```

(Again, requires FILTER)

Winner: **Tie** — both require FILTER for true multiple-match handling.

## Step-by-step: Setting up your first INDEX MATCH formula

If you're new to INDEX MATCH, here's how to build one safely.

### Step 1: Identify your ranges

Open your spreadsheet and identify:
- Your lookup column (what you're searching for)
- Your return column (what you want back)
- The actual values you're searching for

Write these down. For example:
- Lookup column: A2:A100
- Return column: D2:D100
- Search for: "E045"

### Step 2: Build the MATCH part first

In a test cell, write:
```
=MATCH("E045", A2:A100, 0)
```

Press Enter. This should return a number — the row position of your match. If it returns `#N/A`, your value isn't in that range.

### Step 3: Wrap it with INDEX

Once MATCH works, wrap it:
```
=INDEX(D2:D100, MATCH("E045", A2:A100, 0))
```

### Step 4: Add error handling

Finally, wrap everything with IFERROR:
```
=IFERROR(INDEX(D2:D100, MATCH("E045", A2:A100, 0)), "Not found")
```

### Step 5: Replace the hardcoded value

Instead of "E045", reference a cell:
```
=IFERROR(INDEX(D$2:D$100, MATCH(B2, A$2:A$100, 0)), "Not found")
```

(Use `$` to lock the ranges when you copy the formula down)

## Step-by-step: Setting up your first XLOOKUP formula

XLOOKUP is simpler, but requires Excel 365 or 2021.

### Step 1: Check your Excel version

Click File > Account > About Excel. If you see "Microsoft 365" or "Excel 2021", you're good. If you see "Excel 2019" or earlier, XLOOKUP won't work.

### Step 2: Write the basic formula

```
=XLOOKUP(B2, A:A, D:D)
```

Where:
- B2 = the value you're looking for
- A:A = the column to search in
- D:D = the column to return from

### Step 3: Add error handling

```
=XLOOKUP(B2, A:A, D:D, "Not found")
```

That's it. Copy the formula down to all your rows.

## Performance: Which is faster?

On a spreadsheet with 100 formulas, you won't notice a difference.

On a spreadsheet with 10,000 formulas referencing 50,000-row datasets, XLOOKUP will be noticeably faster. XLOOKUP is optimised at the code level for this exact job.

If performance matters for your work, consider:
- Using helper columns to reduce formula count
- Using [Power Query](https://support.microsoft.com/en-us/office/about-power-query-in-excel-7104fbee-9e62-4cb9-a02c-18c6f5fa7eb0) for data transformations instead of formulas
- Learning [Power BI](https://powerbi.microsoft.com) if you're regularly working with large datasets

## Which should you use?

**Use INDEX MATCH if:**
- You must support Excel 2019 or earlier
- You're sharing files with colleagues on older Excel versions
- You need to search in multiple directions simultaneously
- You want a formula that will work across organisations with mixed Excel versions

**Use XLOOKUP if:**
- You have Excel 365 or Excel 2021
- You're building new spreadsheets (not updating legacy ones)
- You want simpler, more readable code
- You're comfortable requiring Excel 365 as a minimum version

**Avoid VLOOKUP if:**
- Your data isn't naturally structured with the lookup column on the left
- You need to add or remove columns from your source data regularly
- You're starting a new project (use XLOOKUP or INDEX MATCH instead)

## Common mistakes to avoid

**Using entire columns in large datasets:**
```
=INDEX(D:D, MATCH(B2, A:A, 0))  ← Slow on huge datasets
```

Better:
```
=INDEX(D2:D1000, MATCH(B2, A2:A1000, 0))  ← Specify exact range
```

**Forgetting absolute references:**
```
=INDEX(D2:D100, MATCH(B2, A2:A100, 0))  ← Will break when copied down
```

Better:
```
=INDEX(D$2:D$100, MATCH(B2, A$2:A$100, 0))  ← Ranges stay fixed
```

**Mixing approximate and exact matching without realising:**
```
=MATCH(B2, A2:A100, 1)  ← This searches for the closest match, not an exact one
```

Better:
```
=MATCH(B2, A2:A100, 0)  ← This demands an exact match
```

## Real-world example: Sales commission lookup

You have:
- A list of salespeople (column A)
- Sales amounts (column B)
- Commission rates by sales bracket (separate table)

You need to look up the commission rate for each salesperson's sales amount.

**Using XLOOKUP with approximate matching:**
```
=XLOOKUP(B2, Sales_Brackets, Commission_Rates, , -1)
```

The `-1` in the match_mode parameter means "find exact match or next smallest value" — perfect for commission brackets.

**Using INDEX MATCH with approximate matching:**
```
=INDEX(Commission_Rates, MATCH(B2, Sales_Brackets, 1))
```

The `1` in MATCH means the same thing.

Both work. XLOOKUP's syntax is clearer about intent.

## Moving forward: Automation and beyond

If you're using formulas like INDEX MATCH or XLOOKUP regularly to manage data, consider whether automation could help. [Learn Power Automate basics on Udemy][UDEMY_AFFILIATE_LINK] to see if cloud automation could replace repetitive manual lookups.

For more advanced Excel techniques and workflow optimisation, *[Excel 2024 Bible](https://www.amazon.co.uk/s?k=Excel+Bible&i=digital-text&ref=nb_sb_noss_2&linkCode=ll2&tag=automatework-21&linkId=12345&language=en_GB)* by John Walkenbach is comprehensive and regularly updated.

## Further reading

- [Microsoft's XLOOKUP documentation](https://support.microsoft.com/en-us/office/xlookup-function-b7fd680e-6d10-43c6-84be-beaf970fbdfc)
- [INDEX and MATCH function reference](https://support.microsoft.com/en-us/office/index-function-a5dcf0dd-996d-40a4-a822-b56b061328bd)
- [When to use Power Query instead of formulas](https://support.microsoft.com/en-us/office/about-power-query-in-excel-7104fbee-9e62-4cb9-a02c-18c6f5fa7eb0)

---

*This article contains affiliate links. If you purchase through them I may earn a small commission at no extra cost to you. See [disclosure](/POD-and-Affiliate/privacy/).*