---
layout: post
title: "Excel Dynamic Arrays and Spill Formulas: Complete Guide"
date: 2026-06-29
categories: [excel]
description: "Master Excel dynamic arrays and spill formulas. Learn how to use FILTER, SORT, UNIQUE and more to simplify complex spreadsheets."
---

*This article contains affiliate links. If you purchase through them I may earn a small commission at no extra cost to you. See [disclosure](/POD-and-Affiliate/privacy/).*

Dynamic arrays in Excel fundamentally changed how you write formulas. Instead of using array formulas with Ctrl+Shift+Enter or dragging formulas down thousands of rows, you can now write a single formula that automatically expands across multiple cells—a feature called "spilling." This guide covers what you need to know to use them effectively.

## What Are Dynamic Arrays and Spilling?

Dynamic arrays are a newer Excel feature that automatically expand formulas across cells without requiring you to manually fill down or use older array formula syntax. When a formula returns multiple values, those values "spill" into adjacent cells automatically.

This works in:
- Microsoft Excel 365 (all versions)
- Excel 2021 and later (on Windows and Mac)

It does **not** work in:
- Excel 2019 or earlier
- Excel Online (as of 2024)

The "spill" means the formula extends its results as far as needed. If your formula returns 50 rows of data, all 50 rows populate automatically in one operation.

## The Core Dynamic Array Functions

Excel provides eight core functions designed specifically for dynamic arrays. These are your primary tools.

### FILTER

FILTER extracts rows from a range based on criteria you specify. It's arguably the most useful dynamic array function.

**Syntax:**
```
=FILTER(array, include, [if_empty])
```

**Example:** You have a customer list in columns A:C (Name, Region, Sales). Extract only rows where Region equals "North":

```
=FILTER(A1:C100, B1:B100="North")
```

This returns all matching rows with all three columns, expanding as many rows as needed. If no rows match, you can specify `if_empty` to show a custom message:

```
=FILTER(A1:C100, B1:B100="North", "No North region customers")
```

**Multiple criteria:** Use multiplication to apply AND logic:

```
=FILTER(A1:C100, (B1:B100="North")*(C1:C100>10000))
```

This returns rows where Region is "North" AND Sales exceed 10,000.

### SORT

SORT orders your data by one or more columns in ascending or descending order.

**Syntax:**
```
=SORT(array, [sort_index], [sort_order], [by_col])
```

**Example:** Sort the same customer data by sales (column 3) in descending order:

```
=SORT(A1:C100, 3, -1)
```

Parameters:
- `3` = sort by the 3rd column (Sales)
- `-1` = descending order (use `1` for ascending)
- `by_col` = TRUE if you want to sort columns instead of rows (rarely needed)

### UNIQUE

UNIQUE removes duplicate rows from a range, keeping only the first occurrence of each unique combination.

**Syntax:**
```
=UNIQUE(array, [by_col], [exactly_once])
```

**Example:** Get a list of unique regions from column B:

```
=UNIQUE(B1:B100)
```

If `exactly_once` is TRUE, only values that appear exactly once are returned:

```
=UNIQUE(B1:B100, FALSE, TRUE)
```

### SEQUENCE

SEQUENCE generates a series of numbers. Useful for creating row numbers, ID sequences, or date ranges.

**Syntax:**
```
=SEQUENCE(rows, [columns], [start], [step])
```

**Example:** Create numbers 1 to 100:

```
=SEQUENCE(100)
```

Create a 5×3 grid starting at 10, incrementing by 2:

```
=SEQUENCE(5, 3, 10, 2)
```

This returns:
```
10  12  14
16  18  20
22  24  26
28  30  32
34  36  38
```

### RANDARRAY

RANDARRAY generates random numbers in a dynamic array.

**Syntax:**
```
=RANDARRAY([rows], [columns], [min], [max], [decimal_places])
```

**Example:** Create 10 random integers between 1 and 100:

```
=RANDARRAY(10, 1, 1, 100, 0)
```

Use `decimal_places` as 0 for whole numbers, or omit it for decimals.

### SHUFFLE and SORT (with multiple criteria)

SHUFFLE randomly reorders array elements:

```
=SHUFFLE(A1:A100)
```

Combine multiple functions for complex operations:

```
=SORT(FILTER(A1:C100, B1:B100="North"), 3, -1)
```

This filters for North region, then sorts by sales descending—all in one formula.

### TOCOL and TOROW

Convert ranges into single columns or rows.

**TOCOL:** Stacks a range into a single column (useful for transposing and compacting data)

```
=TOCOL(A1:C100)
```

**TOROW:** Converts a range into a single row

```
=TOROW(A1:C100)
```

## Practical Examples and Workflows

### Creating a Dynamic Filtered Report

You have sales data with Date, Salesperson, Region, and Amount. Create a dashboard that shows only records from a specific region selected in a dropdown cell (say, cell E1).

```
=FILTER(A2:D1000, C2:C1000=$E$1)
```

Now whenever you change E1, the report automatically updates. No manual filtering needed.

### Combining FILTER and SORT

Show the top 10 customers by sales from the North region, sorted highest to lowest:

```
=SORT(FILTER(A2:C1000, B2:B1000="North"), 3, -1)
```

But this returns all matching rows. To limit to 10 rows, wrap it with INDEX and SEQUENCE:

```
=INDEX(SORT(FILTER(A2:C1000, B2:B1000="North"), 3, -1), SEQUENCE(10))
```

### Removing Blanks Automatically

Your data has some empty cells. Clean it up:

```
=FILTER(A1:C100, A1:A100<>"")
```

This removes any row where column A is blank.

### Creating a Unique List with Counts

Use UNIQUE combined with COUNTIF to show how often each value appears:

```
=UNIQUE(A2:A100)
```

In column B, count occurrences:

```
=COUNTIF($A$2:$A$100, A2:A)
```

The formula automatically fills down as UNIQUE expands.

## The #SPILL! Error and How to Fix It

The #SPILL! error occurs when the spill range is blocked by existing data. For example, if your formula would return 50 rows but row 10 already contains data, Excel cannot complete the spill and returns #SPILL!.

**Solutions:**

1. **Clear the blocking cells** — delete any data blocking the spill range
2. **Move the formula** — place it in a location with clear space below and to the right
3. **Use a separate sheet** — create results on a dedicated results sheet
4. **Reduce the range** — if appropriate, filter or limit the source data

Check what's blocking the spill by selecting the cell showing #SPILL!, then looking at the outlined range in your worksheet.

## Implicit Intersection and @ Operator

When you reference a dynamic array in another formula, Excel uses "implicit intersection"—it automatically applies the operation to each row of the array.

**Example:**

```
=FILTER(A1:C100, B1:B100="North")+10
```

This adds 10 to each value in the numeric columns of the filtered result.

If you need to force intersection explicitly, use the `@` operator:

```
=@FILTER(A1:C100, B1:B100="North")
```

This is rarely necessary but useful for clarity in complex nested formulas.

## Performance Considerations

Dynamic array formulas are generally fast, but large operations can slow your spreadsheet:

- **FILTER on massive datasets** — filtering 1 million rows can lag. Consider splitting data across sheets or using Power Query instead
- **Nested dynamic arrays** — combining multiple FILTER, SORT, and UNIQUE functions multiplies calculation time
- **Circular references** — dynamic arrays don't support circular references; design around this limitation
- **Volatile functions** — RANDARRAY recalculates every time Excel updates; this can slow large workbooks

If you notice lag, test whether a Power Query solution is faster for that particular task.

## Dynamic Arrays vs. Power Query

When should you use dynamic arrays instead of Power Query?

**Use dynamic arrays when:**
- You need quick, simple filters or sorts
- Your data changes frequently and you want live updates
- You're building interactive dashboards with cell references
- The operation is a one-off calculation

**Use Power Query when:**
- You're combining data from multiple sources
- You need complex data cleaning or transformation
- You want to schedule automated data imports
- Performance is critical on very large datasets

Both are powerful. Dynamic arrays are faster to write; Power Query is more robust for serious data work.

## Common Mistakes to Avoid

1. **Assuming FILTER returns a filtered view** — FILTER creates a new array. Deleting the formula removes results; it doesn't affect the source data.

2. **Using entire column references** — `=FILTER(A:C, B:B="North")` works but recalculates unnecessarily. Specify a range instead: `=FILTER(A1:C1000, B1:B1000="North")`

3. **Forgetting that results are dynamic** — if you filter and export results to another sheet, remember they'll update if the source changes.

4. **Mixing older array syntax with dynamic arrays** — don't use Ctrl+Shift+Enter on dynamic array formulas. Just press Enter.

5. **Not accounting for headers** — most examples above skip row 1. If your data includes headers in row 1 and you want to preserve them, adjust your range to start at row 2: `=FILTER(A2:C100, B2:B100="North")`

## Advanced Combinations

### Nested FILTER and SORT with Multiple Conditions

```
=SORT(
  FILTER(A2:D1000, (B2:B1000="North")*(C2:C1000>5000)*(D2:D1000<>""), 
  2, 1
)
```

This filters for North region with amount over 5000 and non-blank dates, then sorts by the date column ascending.

### Creating a Dynamic Top 10 List

```
=FILTER(
  SORT(A2:D1000, 4, -1),
  SEQUENCE(10)
)
```

Returns the top 10 rows by column 4 (amount), sorted highest to lowest.

### Combining UNIQUE with FILTER

```
=UNIQUE(FILTER(B2:B1000, A2:A1000="North"))
```

Shows unique values in column B, but only for rows where column A equals "North".

## Further Reading and Resources

To deepen your Excel skills, consider these resources:

- **[Excel Dynamic Arrays on Udemy](https://trk.udemy.com/DWnAjG)** — comprehensive course covering all dynamic array functions with real-world projects
- **[Microsoft Excel Bible by John Walkenbach](https://www.amazon.co.uk/Microsoft-Excel-2024-Bible-Walkenbach/dp/B0D59G7XYK?tag=automatework-21)** — detailed reference covering formulas, dynamic arrays, and advanced techniques

For ongoing updates on Excel features, subscribe to your company's Microsoft 365 roadmap notifications, as dynamic array functions continue to expand.

---

**Key Takeaway:** Dynamic arrays and spill formulas eliminate manual formula dragging and simplify complex data operations. Master FILTER, SORT, and UNIQUE, and you'll handle most dynamic array tasks. For anything beyond that, combine these functions or reach for Power Query.