```markdown
---
layout: post
title: "How to Remove Duplicates in Excel Power Query: A Complete Guide"
date: 2026-05-31
categories: [excel]
description: "Learn how to remove duplicate rows in Excel Power Query using Remove Duplicates, Group By, and advanced filtering techniques."
---

Duplicate data clutters your spreadsheets and skews your analysis. If you're working with large datasets in Excel, manually identifying and deleting duplicates is impractical. Power Query—Excel's built-in data transformation tool—gives you several robust methods to eliminate duplicates quickly and reliably.

This guide covers every practical approach: the straightforward Remove Duplicates function, the flexible Group By method, and advanced filtering techniques. You'll know exactly which method to use for your specific situation.

## Why Remove Duplicates in Power Query?

Removing duplicates in Power Query rather than the main spreadsheet offers real advantages:

- **Non-destructive**: Your original data stays intact. You're transforming a copy in the query editor.
- **Repeatable**: Once you set up the duplicate removal logic, it runs automatically every time you refresh the data.
- **Scalable**: Handles thousands of rows without performance issues.
- **Flexible**: You can remove exact duplicates or keep the first occurrence of each group.

If you're importing data from databases, CSV files, or APIs, duplicates often creep in. Power Query catches them during the import process before they reach your worksheet.

## Method 1: Using Remove Duplicates (Simplest Approach)

The Remove Duplicates feature is the fastest way to delete exact duplicate rows. Use this when you want to keep only unique records.

### Step-by-step instructions

1. **Open your data source in Power Query**
   - In Excel, go to the **Data** tab
   - Click **Get Data** (or **New Query** if you're on an older version)
   - Select your data source (Excel table, CSV file, database, etc.)
   - The Power Query Editor opens

2. **Select the columns to check for duplicates**
   - In the Power Query Editor, select all columns that contain data (usually this is all of them)
   - If you only want to check specific columns, select those instead
   - For example, if you have Customer ID, Name, and Email, you might only check the Customer ID column

3. **Access the Remove Duplicates feature**
   - Go to the **Home** tab in the Power Query Editor ribbon
   - Click **Remove Rows** (dropdown arrow)
   - Select **Remove Duplicates**

4. **Review the results**
   - Power Query shows you how many rows were removed
   - Preview the data to confirm duplicates are gone
   - Click **OK**

5. **Load the clean data**
   - Click **Close & Load** to send the results to your worksheet
   - Or click **Close & Load To** if you want to specify a destination

**What Power Query does**: It compares the entire row across the columns you selected. If two rows are identical in every column, it keeps only the first occurrence and removes the rest.

### When to use this method

Use Remove Duplicates when:
- You need exact row matches (all columns identical)
- You want to keep the first occurrence of each duplicate
- Your data structure is straightforward with no complex logic needed

### Limitations

This method doesn't let you:
- Keep the last occurrence instead of the first
- Remove duplicates based on specific columns only
- Apply conditional logic (e.g., keep duplicates where one column meets a condition)

For those scenarios, use Method 2.

## Method 2: Using Group By (Most Flexible)

Group By is more powerful than Remove Duplicates. It lets you decide which occurrence to keep, apply aggregations, and handle edge cases.

### Step-by-step instructions

1. **Open Power Query with your data**
   - Follow the same steps as Method 1 to get your data into the Power Query Editor

2. **Go to the Home tab and click Group By**
   - In the **Home** tab, click **Group By**

3. **Configure the grouping**
   - A dialog appears asking which columns define uniqueness
   - Select the column(s) that identify a duplicate
   - For example, if duplicates are identified by Customer ID, select that column
   - Leave **New column name** as is (usually "Count")
   - Under **Operation**, select **Count Rows** (or leave the default)

4. **Click OK**
   - Power Query groups identical values and adds a count column

5. **Remove the count column (optional)**
   - Right-click the count column header
   - Select **Remove**

6. **Load the results**
   - Click **Close & Load**

**What this does**: Group By creates one row per unique value in your selected column(s). All duplicates collapse into a single entry.

### Advanced: Keep specific data from duplicate rows

Sometimes you need to keep more than just the first row. For instance, you might want to keep the first customer name but the most recent order date.

1. **Set up multiple groupings**
   - In the Group By dialog, add multiple operations
   - For the Name column, select **First**
   - For the Date column, select **Max**
   - For the Amount column, select **Sum**

2. **Apply aggregations**
   - Each column can use a different operation: Count, Sum, Average, Min, Max, First, Last, etc.
   - Choose based on what makes sense for your data

3. **Load the result**
   - You now have a deduplicated table with specific values retained from each group

### When to use Group By

Use Group By when:
- You need to deduplicate based on specific columns (not all columns)
- You want to apply logic to other columns (sum amounts, get the maximum date, etc.)
- You need to keep the last occurrence instead of the first
- You want to count how many times each value appeared

## Method 3: Using Filter for Conditional Duplicate Removal

If you need to remove duplicates conditionally—only delete duplicates where a certain column meets criteria—use filtering alongside remove duplicates.

### Step-by-step instructions

1. **Add an index column to track row order**
   - In the Power Query Editor, go to **Add Column** tab
   - Click **Index Column**
   - Keep the default starting number (0 or 1)

2. **Sort by the column that identifies duplicates**
   - Right-click the column containing duplicates
   - Select **Sort Ascending** or **Sort Descending**

3. **Add a custom column to flag duplicates**
   - Go to **Add Column** > **Custom Column**
   - Use this formula to identify duplicates (assuming your data is in column A):
   ```
   = [ColumnName] = [ColumnName2] or [ColumnName] <> [ColumnName2]
   ```
   - For a cleaner approach, use:
   ```
   = List.CountIf(PreviousRows, each _ = [ColumnName]) > 0
   ```

4. **Filter the flag column**
   - Click the filter dropdown on your new column
   - Keep only rows marked as "first occurrence" or "unique"

5. **Remove the helper columns**
   - Delete the index and flag columns you created
   - Click the column header, then **Remove**

6. **Load your results**
   - Click **Close & Load**

### When to use this method

Use conditional filtering when:
- You need to apply business rules to duplicate removal
- You only want to remove certain types of duplicates
- You need to preserve duplicates in specific scenarios

## Practical Example: Customer Database

Here's a real-world scenario: You're importing a customer list from multiple sources, and you have duplicate customer records.

### Your data
| Customer ID | Name | Email | Source |
|---|---|---|---|
| C001 | John Smith | john@example.com | CRM |
| C001 | John Smith | john@example.com | CRM |
| C002 | Sarah Jones | sarah@example.com | Email List |
| C003 | Mike Brown | mike@example.com | CRM |
| C002 | Sarah Jones | sarah@example.com | Website |

### Solution using Group By

1. Import the CSV file into Power Query
2. Click **Group By**
3. Select **Customer ID** as the grouping column
4. Under Operations, set:
   - Name: First
   - Email: First
   - Source: First
5. Click OK
6. Delete the count column
7. Click **Close & Load**

### Result
| Customer ID | Name | Email | Source |
|---|---|---|---|
| C001 | John Smith | john@example.com | CRM |
| C002 | Sarah Jones | sarah@example.com | Email List |
| C003 | Mike Brown | mike@example.com | CRM |

You now have one row per customer with no duplicates.

## Common Mistakes to Avoid

**Mistake 1: Removing duplicates before understanding your data**
- Always preview your data first
- Check whether "duplicates" are genuinely unwanted or legitimate repeat transactions
- For sales data, a customer buying twice is not a duplicate

**Mistake 2: Removing duplicates on all columns when you should target specific ones**
- If you use Remove Duplicates on all columns and have timestamps, every row might be unique
- Use Group By and specify which columns matter for duplicate identification

**Mistake 3: Losing important data**
- When you remove duplicates, you discard the extra rows
- If those rows contain information (like different contact email addresses), you'll lose it
- Use Group By with multiple aggregations to retain relevant data from all rows

**Mistake 4: Not testing on a copy**
- Always test your deduplication logic on a sample
- Verify that the output matches your expectations before running it on production data

## Performance Tips for Large Datasets

If you're working with hundreds of thousands of rows:

- **Remove Duplicates is faster** for simple exact-match scenarios
- **Group By requires more processing** but offers more control
- **Filter early**: If you can narrow down your dataset before deduplicating, do it
- **Disable query folding if necessary**: Right-click a step and select **Delete** if upstream steps are slowing you down

For datasets over 1 million rows, consider using a database query instead of Excel. Power Query performs well, but a SQL database is designed for this workload.

## Refreshing Your Deduplicated Data

Once you've set up duplicate removal in Power Query:

1. **Your logic persists**: Every time you click **Refresh**, the same deduplication rules apply
2. **New duplicates are caught**: If fresh data arrives with duplicates, they're removed automatically
3. **No manual work**: Unlike Excel's built-in Remove Duplicates feature, Power Query remembers your settings

This is especially valuable if you're importing data regularly.

## Combining with Other Power Query Steps

Duplicate removal is usually part of a larger data cleaning pipeline:

1. Load data
2. Remove duplicates
3. Split columns
4. Change data types
5. Filter rows
6. Merge tables
7. Load to Excel or Power BI

Stack your deduplication step logically. Generally, remove duplicates early—before you split, transform, or merge data. This prevents duplicates from reappearing after you've transformed columns.

## Recommended Tools

If you want to deepen your Power Query skills, [**M is for (Data) Monkey** by Ken Puls and Miguel Escobar](https://www.amazon.co.uk/M-Data-Monkey-QueryFormula-Language/dp/1615470611?tag=automatework-21) is the definitive guide. It covers every Power Query technique including advanced deduplication.

For structured, video-based learning, the [Udemy Power Query and Power BI course][UDEMY_AFFILIATE_LINK] walks you through real-world examples including duplicate removal at scale.

## Summary

- **Remove Duplicates**: Fastest for exact row matches
- **Group By**: Most flexible, handles partial duplicates and aggregations
- **Custom filtering**: For conditional logic

Choose Remove Duplicates for simplicity, Group By for control, and custom filtering for edge cases. Test on sample data, understand your business rules about what constitutes a duplicate, and let Power Query handle the heavy lifting automatically on every refresh.

*This article contains affiliate links. If you purchase through them I may earn a small commission at no extra cost to you. See [disclosure](/POD-and-Affiliate/privacy/).*
```