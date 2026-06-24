```markdown
---
layout: post
title: "Excel Get and Transform Data Power Query Tutorial: Complete Beginner's Guide"
date: 2026-06-24
categories: [excel]
description: "Learn Power Query in Excel. Step-by-step tutorial on Get and Transform data, cleaning, and automation for business analysts."
---

*This article contains affiliate links. If you purchase through them I may earn a small commission at no extra cost to you. See [disclosure](/POD-and-Affiliate/privacy/).*

## What is Power Query and Why You Need It

Power Query — officially called "Get and Transform Data" in Excel — is a data extraction and transformation tool built into Excel. It lets you connect to external data sources, clean messy datasets, and automate repetitive data preparation tasks without writing formulas.

If you spend hours copying and pasting data, removing duplicates, or reformatting columns, Power Query will save you significant time. Most importantly, once you build a Power Query workflow, you can refresh the entire process with a single click when new data arrives.

Power Query is available in:
- Excel 2016 and later (Windows)
- Excel 365 (Mac and Windows)
- Power BI Desktop

This tutorial assumes you're using Excel 365 or Excel 2019+ on Windows.

## Where to Find Power Query in Excel

1. Open Excel and click on the **Data** tab in the ribbon
2. Look for the **Get & Transform Data** group
3. You'll see buttons like **New Query**, **From Web**, **From Database**, and **From File**

If you don't see these options, you're likely using an older version of Excel or a limited licence. Upgrade to Excel 365 for full access.

## The Core Power Query Workflow

Power Query operates in four stages:

1. **Connect** — Pull data from a source (CSV, database, website, etc.)
2. **Transform** — Clean, reshape, and prepare the data
3. **Load** — Send the result to a worksheet or data model
4. **Refresh** — Update the data automatically when the source changes

Let's work through each stage with a practical example.

## Step 1: Connecting to Your Data Source

### Loading Data from a CSV File

The easiest way to start is with a CSV file on your computer.

1. Go to **Data** > **Get & Transform Data** > **New Query** > **From File** > **From CSV**
2. Navigate to your CSV file and open it
3. A preview window appears showing the first few rows
4. Click **Load** to import the data into Excel
5. Or click **Transform Data** to open the Power Query Editor first

**Why transform first?** Because you almost always need to clean the data before loading it. Jumping straight to the Editor lets you fix issues before they hit your worksheet.

### Loading Data from Other Sources

Power Query connects to dozens of data sources:

- **Excel workbooks** — Other Excel files
- **Databases** — SQL Server, Oracle, MySQL
- **Web** — Scrape HTML tables from websites
- **APIs** — Pull JSON data from cloud services
- **SharePoint** — Connect to SharePoint lists
- **Dynamics 365** — CRM and ERP data

For this tutorial, we'll focus on CSV and Excel files since they're most common.

## Step 2: The Power Query Editor Interface

Once you click **Transform Data**, the Power Query Editor opens. This is where the magic happens.

The interface has four areas:

1. **Ribbon** — Buttons for adding steps
2. **Queries pane** (left) — Lists all loaded queries
3. **Preview pane** (centre) — Shows your data
4. **Applied Steps pane** (right) — Shows the transformation history

Every action you take becomes a "step" in the Applied Steps list. This is crucial — Power Query remembers every transformation, so you can undo, edit, or delete any step.

## Step 3: Essential Transformations

### Removing Header Rows

If your data has blank rows at the top, remove them first.

1. Click any cell in the header row you want to remove
2. Go to **Home** > **Remove Rows** > **Remove Top Rows**
3. Enter the number of rows to remove (usually 1)

### Promoting Headers

If your first row contains column names:

1. Select any cell in the first data row
2. Go to **Home** > **Use First Row as Headers**

Power Query automatically renames your columns.

### Removing Duplicate Rows

Duplicate records corrupt analysis. Remove them like this:

1. Select the columns you want to check for duplicates (or leave all selected)
2. Go to **Home** > **Remove Rows** > **Remove Duplicates**
3. Power Query marks identical rows and removes them
4. Check the Applied Steps pane to see how many rows were deleted

### Changing Data Types

Wrong data types cause formula errors and slow queries.

1. Click the column header
2. Go to **Home** > **Data Type** and select the correct type (Text, Number, Date, etc.)

Or right-click the column header and select **Change Type**.

**Pro tip:** Always set date columns to **Date**, not **Text**. This prevents sorting and filtering errors.

### Filtering and Sorting

Filter data to exclude unnecessary rows:

1. Click the filter icon (funnel) in the column header
2. Uncheck values you want to exclude
3. Click **OK**

The filter step appears in Applied Steps. You can edit or delete it anytime.

For sorting, right-click a column header and select **Sort Ascending** or **Sort Descending**.

## Step 4: Advanced Transformations

### Splitting Columns

If a column contains multiple values separated by a delimiter (like "Smith, John"):

1. Right-click the column header
2. Select **Split Column** > **By Delimiter**
3. Choose the delimiter (comma, space, colon, etc.)
4. Power Query splits the column into two

This creates new columns automatically.

### Merging Columns

Combine two columns into one:

1. Select the first column
2. Hold Ctrl and click the second column
3. Right-click and select **Merge Columns**
4. Choose the separator (space, dash, comma, etc.)
5. Name the new column

### Grouping and Aggregating

Summarise your data by category:

1. Select the grouping column
2. Go to **Home** > **Group By**
3. Choose the grouping column and the aggregation function (Sum, Count, Average, etc.)
4. Name the output column
5. Click **OK**

This creates a summary table grouped by your chosen column.

### Adding Custom Columns

Create calculated columns using Power Query's formula language (M):

1. Go to **Add Column** > **Custom Column**
2. Enter a name and formula
3. Use column names in brackets, like `[Price] * [Quantity]`
4. Click **OK**

The formula applies to every row instantly.

## Step 5: Loading Your Data

Once transformations are complete, load the data:

1. Go to **Home** > **Close & Load** or press Ctrl+Shift+X
2. Choose your destination:
   - **Close & Load** — Creates a new worksheet
   - **Close & Load To** — Specify a cell or create a pivot table

Power Query creates a linked table. When your source data updates, right-click the table and select **Refresh** to pull the latest version.

## Refreshing Your Data

This is where Power Query saves you hours:

1. Once loaded, your data lives in an Excel table
2. When the source file updates, right-click the table
3. Select **Refresh**
4. All transformations apply automatically to the new data
5. Your Excel formulas recalculate using fresh numbers

You can also set automatic refresh:

1. Right-click the table
2. Select **Query** > **Query Properties**
3. Tick **Refresh data when opening the file**
4. Set a refresh interval if desired

## Practical Example: Cleaning a Customer List

Let's walk through a complete real-world scenario.

**Scenario:** You have a CSV of customer data with:
- Blank header rows
- Mixed name formats (some "FirstName LastName", some "LastName, FirstName")
- Duplicate entries
- Email addresses in mixed case

**Steps:**

1. **Load the CSV** — Go to Data > Get & Transform Data > From File > From CSV
2. **Remove blank rows** — Home > Remove Rows > Remove Top Rows (set to 2)
3. **Use first row as headers** — Home > Use First Row as Headers
4. **Remove duplicates** — Home > Remove Rows > Remove Duplicates
5. **Split the Name column** — Right-click Name > Split Column > By Delimiter > Space
6. **Clean email case** — Add Column > Custom Column > `Text.Lower([Email])`
7. **Load the result** — Home > Close & Load

The entire workflow now exists as a reusable query. Next week, when new customer data arrives, you click refresh and all seven steps execute automatically.

## Common Mistakes to Avoid

**Loading too early**
Don't click "Load" until transformations are complete. Transform first, load last.

**Assuming one-time work is done**
If your source data changes regularly, always build reusable queries. Manual work doesn't scale.

**Ignoring data types**
Text that looks like dates causes sorting errors. Always check data types before loading.

**Over-transforming in Power Query**
Not everything needs to happen in Power Query. Simple calculations can live in Excel formulas. Use Power Query for data cleaning and extraction; use formulas for analysis.

**Deleting steps without checking dependencies**
If you delete a step and something breaks, use Undo (Ctrl+Z). Steps can interact with each other.

## Power Query vs. Excel Formulas

**Use Power Query for:**
- Importing data from external sources
- Cleaning and standardising messy data
- Removing duplicates and blank rows
- Splitting or merging columns
- Recurring data preparation (anything you'd do every week)

**Use Excel formulas for:**
- Calculations specific to your analysis
- Conditional logic (IF, VLOOKUP, etc.)
- Creating custom metrics

The best approach combines both. Use Power Query to import and clean; use formulas to analyse.

## Connecting Power Query to Power BI

Power Query also powers Power BI Desktop. If you master Power Query in Excel, you're halfway to building Power BI reports.

In Power BI, Power Query is even more powerful because you can combine multiple data sources into a single data model. The syntax and steps are identical.

## Further Reading and Recommended Tools

To deepen your Power Query skills, explore these resources:

- [Microsoft's official Power Query documentation](https://support.microsoft.com/en-us/office/about-power-query-in-excel-7104fbee-9e62-4cb9-a02e-5bfb1a6c536a) — Free, comprehensive, authoritative
- [Learn Power Query on Udemy](https://trk.udemy.com/DWnAjG) — Video-based learning, practical projects
- [Excel 2021 Bible by Michael Alexander and Dick Kusleika](https://www.amazon.co.uk/s?k=Excel+2021+Bible&tag=automatework-21) — The definitive Excel reference; includes detailed Power Query chapters

**Affiliate disclosure:** The Amazon and Udemy links above are affiliate links. If you purchase through them, I earn a small commission at no extra cost to you.

---

**Next steps:** Load your first CSV file and try removing duplicates. Once that works, experiment with filtering and splitting columns. Master these basics before moving to advanced techniques.
```