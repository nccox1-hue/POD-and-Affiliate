---
layout: post
title: "How to Merge Tables in Excel Without VLOOKUP Using Power Query"
date: 2026-05-31
categories: [excel, power-bi]
description: "Master table merges in Excel using Power Query. Skip VLOOKUP and use Merge Queries for cleaner, faster data combinations."
---

VLOOKUP is outdated for merging tables. Power Query's Merge Queries feature is faster, cleaner, and handles errors better. Here's how to do it properly.

## Why Power Query Beats VLOOKUP for Merging Tables

VLOOKUP has serious limitations:
- It only looks right. You can't pull data from columns to the left of your lookup column.
- It breaks if your data structure changes.
- It requires formula duplication across hundreds of rows.
- It fails silently with #N/A errors.

Power Query's Merge Queries feature avoids all of these problems. It treats your tables as proper datasets, applies transformations systematically, and gives you a clean result without formula maintenance.

For anyone working with multiple data sources in Excel, Power Query is non-negotiable.

## Prerequisites: Load Your Data into Power Query

Before you merge, both tables must be in Power Query. If you haven't done this yet, it takes 30 seconds.

**Load the first table:**

1. Open your Excel workbook. Select your table (including headers).
2. Go to **Data** tab → **From Table/Range** (or **Get & Transform Data** in older versions).
3. Power Query Editor opens. Click **Load To** → **Only Create Connection**.
4. Name your query something descriptive, like "Customers" or "Sales_Data".

**Do this for your second table too.** You now have two queries ready to merge.

If your data lives in CSV files, databases, or APIs instead, use **Get Data** to import them the same way.

## The Three Types of Table Merges in Power Query

Power Query offers three merge types:

**Left Outer** — Keep all rows from the left table, add matching data from the right table. Use this 90% of the time.

**Right Outer** — Keep all rows from the right table, add matching data from the left.

**Inner** — Keep only rows where both tables have a match.

**Full Outer** — Keep all rows from both tables, whether they match or not.

For most business scenarios, **Left Outer** is what you want.

## Step-by-Step: Merge Two Tables in Power Query

Assume you have a Customers table (with Customer ID and Name) and an Orders table (with Customer ID and Order Amount). You want to add the customer names to your orders.

**Step 1: Open Power Query Editor**

1. In Excel, go to **Data** → **Queries & Connections** (or **Get & Transform**).
2. Right-click the query you want to merge INTO (in this example, Orders). Select **Edit**.

Power Query Editor opens. You'll see your Orders data displayed.

**Step 2: Add the Merge Step**

1. In the Power Query ribbon, click **Merge Queries**.
2. A dialog appears. The left side shows your current table (Orders). Leave it as is.
3. In the **Merge Kind** section, select **Left Outer** (the default).

**Step 3: Set Up the Join Keys**

This is critical. You're telling Power Query which columns match between tables.

1. In the Orders table preview (left side), click the **Customer ID** column header.
2. In the "Merge Kind" dropdown at the bottom, select the **Customers** table.
3. In the Customers table preview (right side), click its **Customer ID** column header.

Both columns are now highlighted in blue. Power Query has identified your join key.

**Step 4: Complete the Merge**

Click **OK**. Power Query adds a new column to your Orders table called "Customers" (or whatever your second table is named). It looks like a table icon in each cell.

**Step 5: Expand the Merged Column**

That table icon means the data is there but collapsed. Expand it:

1. Click the expand arrow icon at the top right of the new "Customers" column.
2. A dialog appears showing all columns from the Customers table.
3. Tick the columns you want to pull through (Customer Name, for example). Untick the rest.
4. Click **OK**.

Power Query now adds a "Customers.Customer Name" column to your Orders table with the matching customer names. That's your merge complete.

**Step 6: Load the Results**

1. Click **Close & Load** (top left of Power Query ribbon).
2. Excel creates a new sheet with your merged table.

The entire operation took under two minutes and required zero formulas.

## Advanced: Merging on Multiple Columns

Sometimes one column isn't enough. Say you need to match on both Customer ID AND Order Date. Power Query handles this:

1. Follow steps 1-3 above, but instead of clicking one column, hold **Ctrl** and click multiple columns in both tables (in the same order).
2. Complete the merge as normal.

Power Query uses all selected columns as the join key. It only returns matches where every column aligns.

## Handling Mismatches: What Happens to Unmatched Rows?

With a **Left Outer** join, rows in your left table that don't match the right table will still appear, but the merged columns will show `null` (Excel displays this as blank).

If you want to remove these rows:

1. After expanding the merged column, click the column header filter arrow.
2. Uncheck "null".
3. Click OK.

Now only matched rows remain. This is faster than VLOOKUP's IFERROR workaround.

## Real-World Example: Sales Analysis with Multiple Data Sources

Here's a practical scenario. You have:

- **Customers table**: Customer ID, Company Name, Region, Credit Limit
- **Orders table**: Order ID, Customer ID, Order Date, Amount
- **Products table**: Product ID, Product Name, Category

You want a single table with Order ID, Customer Name, Region, Product Name, Category, and Amount.

**Step 1:** Load all three tables as queries.

**Step 2:** Merge Orders + Customers on Customer ID (Left Outer). Expand to get Company Name and Region.

**Step 3:** Merge the result + Products on Product ID (Left Outer). Expand to get Product Name and Category.

**Step 4:** Remove columns you don't need (Order ID, Customer ID, Product ID if they're just for joining).

**Step 5:** Click **Close & Load**. Done.

In VLOOKUP, this would require three nested formulas plus error handling. Power Query does it in seconds, visually, with no formulas at all.

## Why This Is Better Than Formulas

- **Maintainability**: If your source data structure changes, update one merge step, not 500 rows of formulas.
- **Performance**: Power Query uses the underlying database engine when connected to SQL or other sources. Formulas evaluate row by row.
- **Error handling**: Mismatches are transparent. VLOOKUP returns #N/A and you hunt for the problem.
- **Audibility**: Other people reading your workbook can see exactly what you did. Formulas are a black box.

## Common Mistakes to Avoid

**Wrong join type**: Left Outer is your default for a reason. Check the dialog carefully.

**Case sensitivity**: By default, Power Query matches text case-insensitively. If you need exact case matching, you'll need to add a custom step (advanced).

**Duplicate values in join key**: If your Customer ID appears twice in the Customers table, every Orders row with that ID will match both, creating duplicates. Clean your source data first.

**Forgetting to remove the join key from the right table**: After merging, you'll have Customer ID twice (once from Orders, once from the expanded Customers columns). Delete the duplicate.

**Loading to a new sheet instead of the same sheet**: The default "Close & Load" creates a new sheet. If you need the result in a specific location, use "Close & Load To" → "Existing Sheet" instead.

## Performance Tips for Large Datasets

Power Query is fast, but if you're merging tables with 500,000+ rows:

1. **Filter early**: Remove unnecessary rows before merging, not after.
2. **Reduce columns**: Delete columns you won't use before merging.
3. **Use native database queries**: If your data lives in SQL Server or a database, query it there instead of importing to Excel.

For smaller datasets (under 100,000 rows), Power Query is fine to use as-is.

## When to Use Other Approaches

Power Query merge is the answer 95% of the time. The other 5%:

- **Very simple one-off lookups**: A single VLOOKUP or INDEX/MATCH is faster to type.
- **Dynamic real-time data**: If your source changes every minute and you need instant updates, consider Power BI or a database connection instead.
- **Extremely complex conditional logic**: Sometimes a formula is clearer than nested Power Query steps.

But for any repeatable data task, Power Query wins.

## Bringing Merged Data into Power BI

If you're using Power BI anyway, you don't need to merge in Excel. Power BI handles table relationships automatically and more efficiently.

Load your tables into Power BI Desktop, define relationships in the model view, and your reports work with merged data without duplicating it. This is the professional approach for serious analytics.

## Further Reading and Recommended Tools

To deepen your Power Query skills, consider these resources:

- **M is for Data Monkey** by Ken Puls and Miguel Escobar is the comprehensive guide to Power Query's underlying M language. Available on [Amazon UK](https://www.amazon.co.uk/s?k=M+is+for+Data+Monkey&tag=automatework-21).
- For hands-on practice, Udemy has several excellent Power Query courses. Search for "Excel Power Query" and filter by highest-rated. [Udemy courses on Power Query][UDEMY_AFFILIATE_LINK] range from beginner to advanced.

Master Power Query and you'll never write a VLOOKUP again. It's a skill that compounds—every data task gets faster.

---

*This article contains affiliate links. If you purchase through them I may earn a small commission at no extra cost to you. See [disclosure](/POD-and-Affiliate/privacy/).*