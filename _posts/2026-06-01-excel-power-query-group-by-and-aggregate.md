---
layout: post
title: "Excel Power Query Group By and Aggregate: Complete Step-by-Step Guide"
date: 2026-06-01
categories: [excel]
description: "Learn how to group and aggregate data in Power Query. Step-by-step instructions for summarising, filtering, and transforming large datasets efficiently."
---

## Excel Power Query Group By and Aggregate: Complete Step-by-Step Guide

Power Query's Group By feature is one of the most powerful tools for data summarisation in Excel. Rather than spending hours creating pivot tables or manual formulas, you can consolidate thousands of rows into meaningful summaries in minutes.

This guide walks you through every aspect of grouping and aggregating data in Power Query—from basic setup to advanced scenarios you'll encounter in real work.

## What Is Group By in Power Query?

Group By takes raw data and consolidates it based on one or more columns. You specify which column(s) to group by, then choose aggregation functions (sum, count, average, etc.) to apply to the remaining columns.

**Common use cases:**
- Total sales by product or region
- Count of transactions by customer
- Average order value by month
- Maximum temperature by location

The key advantage over pivot tables: once you set up a Group By query, it refreshes automatically when source data changes. You're not locked into a static summary.

## Getting Your Data into Power Query

Before grouping, your data must be in Power Query. Here's how to load it:

1. Open your Excel workbook with the data you want to summarise
2. Select any cell in your data range
3. Go to **Data** tab → **Get & Transform Data** → **From Table/Range**
4. Excel automatically detects your data range. Click **OK**
5. Power Query Editor opens with your data loaded

If your data is external (CSV, database, web), use **Get Data** instead and select your source type.

**Important:** Ensure your data has headers. Power Query uses these to identify columns for grouping.

## Basic Group By: Single Column Grouping

Let's work through a practical example. Suppose you have sales data with columns: Date, Product, Region, Amount.

You want total sales by Product.

### Step-by-step process:

1. In Power Query Editor, go to the **Home** tab
2. Click **Group By** (you'll find it in the Transform section)
3. A dialog box opens with two sections: **Group by** and **New column(s)**

4. Under **Group by**, select **Product** from the dropdown
5. Under **New column(s)**, click **Add aggregation**
6. A new row appears:
   - **New column name**: Enter `Total Sales`
   - **Column**: Select `Amount`
   - **Operation**: Select `Sum`

7. Click **OK**

Power Query now shows one row per product with its total sales. If you had 10,000 rows across 5 products, you now have 5 rows—one per product.

## Multiple Column Grouping

Often you need to group by more than one column. Example: total sales by Product *and* Region.

1. Open Group By dialog (Home → Group By)
2. Under **Group by**, select the first column: **Product**
3. Click **Add grouping column**
4. A second row appears. Select **Region**
5. Add your aggregation as before (New column: Total Sales, Column: Amount, Operation: Sum)
6. Click **OK**

Result: one row per Product-Region combination with its total sales.

You can add as many grouping columns as needed. Each additional column creates finer granularity in your summary.

## Aggregation Functions Explained

Power Query offers several aggregation operations. Here's what each does:

| Operation | Use Case |
|-----------|----------|
| Sum | Total revenue, total units sold |
| Count | Number of transactions, number of items |
| Average | Average order value, average temperature |
| Minimum | Lowest price, earliest date |
| Maximum | Highest price, latest date |
| Standard Deviation | Variability in measurements |
| Median | Middle value (useful when outliers skew averages) |
| Count Distinct | Number of unique customers or products |

### Adding multiple aggregations

You often need several metrics in one query. Example: total sales, average order value, and order count—all by Product.

1. Open Group By dialog
2. Group by: **Product**
3. Add first aggregation: Total Sales (Sum of Amount)
4. Click **Add aggregation** again
5. Add second aggregation: Avg Order Value (Average of Amount)
6. Click **Add aggregation** once more
7. Add third aggregation: Order Count (Count of Amount)
8. Click **OK**

One row per product now shows all three metrics. This replaces what would normally require multiple pivot tables or complex formulas.

## Filtering Before Grouping

You often want to exclude certain records before aggregating. Example: only include orders from the last 12 months.

Always filter *before* grouping. Filtering after grouping is less efficient.

1. Before clicking Group By, select your data
2. Click **Filter Rows** (Home tab, Transform section)
3. Click the dropdown arrow next to your date column
4. Select **Date Filters** → **After**
5. Enter the date (12 months ago)
6. Click **OK**
7. Now apply Group By to the filtered data

This approach is faster because Power Query only groups the rows that match your filter criteria.

## Handling Text and Special Cases

### Text columns during aggregation

When you group by a text column (like Product Name or Region), Power Query automatically groups identical values together. But what if your text has inconsistent casing or extra spaces?

Clean your data before grouping:

1. Right-click the column header
2. Select **Transform** → **Trim** (removes leading/trailing spaces)
3. Select **Transform** → **Capitalize Each Word** or **Lowercase** as needed
4. Now apply Group By

### Null or blank values

By default, Power Query treats blanks and null values as a separate group. If your data has missing values:

1. Click **Remove Rows** before Group By
2. Select **Remove Blank Rows**
3. Choose which columns to check

Alternatively, use **Replace Values** to fill blanks with a placeholder like "Unknown" before grouping.

## Common Grouping Scenarios

### Sales by month (from datetime column)

You have transaction dates but want monthly totals:

1. Right-click your date column
2. Select **Transform** → **Date** → **Month**
3. This creates a new column with just the month number
4. Group By this new month column

Or extract year and month together:

1. Select the date column
2. Home → **Add Column** → **Custom Column**
3. Enter formula: `=Date.ToText([YourDateColumn], "yyyy-MM")`
4. This creates YYYY-MM format (2026-06, 2026-07)
5. Group by this custom column

### Count distinct values

Example: How many unique customers made purchases in each region?

1. Group By: **Region**
2. Add aggregation:
   - New column name: `Unique Customers`
   - Column: `Customer ID`
   - Operation: `Count Distinct`

### Percentage of total

You want each product's sales as a percentage of total sales:

1. Group By Product, Sum Amount (creates Total Sales column)
2. Home → **Add Column** → **Custom Column**
3. Enter formula: `=[Total Sales] / List.Sum([Total Sales])`
4. Right-click the new column → **Transform** → **Multiply** → Enter `100`
5. Format as percentage

## Sorting Your Grouped Data

After grouping, sort by your aggregated column to identify top performers:

1. Click the column header dropdown
2. Select **Sort Descending** (for highest values first)

Or sort by your group column alphabetically:

1. Click the grouping column dropdown
2. Select **Sort A to Z**

## Removing Duplicates Within Groups

Sometimes you need to count unique items within each group before aggregating.

Example: How many unique products were purchased in each region?

1. Before Group By, remove duplicate Product rows *within* each Region
2. Select your data
3. Home → **Remove Rows** → **Remove Duplicates**
4. Select which columns constitute a "duplicate" (Region + Product in this case)
5. Now Group By Region, Count rows

## Combining Group By with Other Transformations

Power Query lets you chain transformations. A typical workflow:

1. Load data
2. Filter rows (remove unwanted records)
3. Clean text (trim, capitalise)
4. Remove duplicates if needed
5. **Group By** to aggregate
6. Sort the results
7. Load to Excel

Each step builds on the previous. You see the result at each stage in Power Query Editor.

## Loading Your Grouped Data

Once your query is complete:

1. Click **Close & Load** (Home tab, upper left)
2. Choose **Load To**:
   - **Table** (creates a new Excel table—recommended)
   - **Pivot Table**
   - **Only create Connection** (if you want to build on this query later)

The grouped data appears in a new sheet or location you specify.

## Refreshing Grouped Queries

One major advantage of Power Query: automatic refresh.

When source data changes:

1. Right-click your query result table in Excel
2. Select **Refresh**

Power Query re-runs the entire grouping and aggregation against the new source data. Your summary updates instantly.

For automatic refresh, go to **Data** → **Queries & Connections** → right-click your query → **Properties** → enable **Refresh on open**.

## Troubleshooting Common Issues

**Problem: "Group By is greyed out"**
- Your data may not be loaded as a table. Reload it via Get & Transform Data.

**Problem: Wrong column showing as grouped**
- Clear your selection and select just one cell in your data range before clicking Group By.

**Problem: Aggregation result is text instead of number**
- The column you're aggregating may be formatted as text. In Power Query, right-click the column → **Change Type** → **Whole Number** or **Decimal Number**.

**Problem: Blanks appearing as a separate group**
- Use **Remove Blank Rows** before grouping, or **Replace Values** to fill them.

## When to Use Group By vs. Pivot Tables

| Use Power Query Group By | Use Pivot Table |
|-------------------------|-----------------|
| Need automatic refresh | One-time analysis |
| Grouping by 3+ columns | Simple 2-column breakdown |
| Complex aggregations | Quick exploratory analysis |
| Building to a dataset for reporting | Interactive slicing and dicing |

Group By is superior for repeatable, automated workflows. Pivot tables remain better for quick exploration.

## Advanced: Nested Grouping and Calculations

For complex scenarios, chain Group By operations:

1. First Group By: Product, Sum Sales
2. Add Column: Rank products by sales
3. Second Group By: Category, Average of Sales

This creates multi-level summaries without manual formulas.

## Recommended Learning Resources

If you want to deepen your Power Query skills beyond Group By, the [M Language in Excel Power Query course on Udemy](https://trk.udemy.com/DWnAjG) covers advanced transformations and custom functions.

For a comprehensive reference, *[M Programming Language for Excel and Power BI](https://www.amazon.co.uk/Programming-Language-Excel-Power-BI/dp/B0D8G8FXVH?tag=automatework-21)* provides detailed explanations of every Power Query function, including Group By variations.

## Key Takeaways

- **Group By** consolidates raw data into meaningful summaries without pivot tables
- Always **filter before grouping** for better performance
- Use **multiple grouping columns** for finer granularity
- Add **multiple aggregations** to create comprehensive summaries in one step
- **Clean text data** (trim, standardise casing) before grouping
- **Refresh** your query when source data changes—automation at its best

Master Group By and you'll handle 80% of data summarisation tasks in Excel without leaving Power Query.

## Further Reading

- [Excel Power Query: Essential Formulas and Functions](https://www.amazon.co.uk/Excel-Power-Query-Essential-Formulas/dp/B0CY8JQPLW?tag=automatework-21)
- [Power BI and Power Query for Data Transformation](https://trk.udemy.com/DWnAjG)
- [Microsoft's Official Power Query M Reference Documentation](https://learn.microsoft.com/en-us/powerquery-m/power-query-m-reference)

---

*This article contains affiliate links. If you purchase through them I may earn a small commission at no extra cost to you. See [disclosure](/POD-and-Affiliate/privacy/).*