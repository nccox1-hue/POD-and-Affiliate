```markdown
---
layout: post
title: "Power Query M Language Basics: A Practical Tutorial for Excel and Power BI"
date: 2026-06-05
categories: [excel, power-bi]
description: "Learn Power Query M language fundamentals with step-by-step examples. Master variables, functions, and data transformation logic for Excel and Power BI."
---

*This article contains affiliate links. If you purchase through them I may earn a small commission at no extra cost to you. See [disclosure](/POD-and-Affiliate/privacy/).*

## What is Power Query M Language?

Power Query M is a functional programming language used to define and execute data transformations in Excel and Power BI. When you use the Power Query editor to clean, reshape, or combine data, you're either building M code visually or writing it directly.

Most users never see M code. They click buttons in the Power Query interface, and the transformations stack up invisibly. But M language is what runs behind the scenes. Understanding it gives you:

- Direct control over complex transformations
- The ability to reuse code across projects
- Debug capability when visual steps fail
- Performance optimisation for large datasets

This tutorial assumes you've used Power Query before but haven't written M code. You'll learn syntax, core functions, and practical patterns you can apply immediately.

## Understanding M Fundamentals

### Expressions and Values

M is an expression-based language. Everything evaluates to a value. The simplest M expression is a literal:

```
"Hello"
5
true
{1, 2, 3}
```

These are strings, numbers, booleans, and lists respectively. M respects data types strictly.

### Variables and Let Statements

The `let` statement is the foundation of M. It lets you define variables, then execute a final expression:

```
let
    Source = Excel.Workbook(File.Contents("C:\data.xlsx")),
    Sheet1 = Source{[Item="Sheet1"]}[Content],
    FilteredData = Table.SelectRows(Sheet1, each [Amount] > 100)
in
    FilteredData
```

Every line before `in` is a variable assignment. The final expression after `in` is what gets returned.

Notice the pattern: you load data, transform it step by step, and return the result. Each step builds on the previous one.

### Comments

Use `//` for single-line comments:

```
let
    // Load the raw data
    Source = Excel.Workbook(File.Contents("C:\data.xlsx")),
    // Select the transactions sheet
    Sheet1 = Source{[Item="Sheet1"]}[Content]
in
    Sheet1
```

## Working with Data Types

### Lists

A list is an ordered collection:

```
{1, 2, 3, 4, 5}
{"apple", "banana", "cherry"}
```

Access items by index (starting at 0):

```
let
    MyList = {"apple", "banana", "cherry"}
in
    MyList{0}  // returns "apple"
```

### Records

A record is a key-value collection:

```
let
    MyRecord = [Name = "Alice", Age = 30, City = "London"]
in
    MyRecord[Name]  // returns "Alice"
```

### Tables

Tables are lists of records with consistent structure:

```
let
    MyTable = #table({"Name", "Age"}, {{"Alice", 30}, {"Bob", 25}})
in
    MyTable
```

The `#table()` function takes column names and a list of rows.

## Essential Power Query M Functions

### Table Functions

**Table.SelectRows** filters rows based on a condition:

```
let
    Source = Excel.Workbook(...),
    Data = Source{[Item="Sheet1"]}[Content],
    Filtered = Table.SelectRows(Data, each [Amount] > 100)
in
    Filtered
```

The `each` keyword creates a function that applies to every row. `[Amount]` refers to the Amount column in the current row.

**Table.AddColumn** adds a new calculated column:

```
let
    Source = Excel.Workbook(...),
    Data = Source{[Item="Sheet1"]}[Content],
    WithVAT = Table.AddColumn(Data, "Total with VAT", each [Amount] * 1.2)
in
    WithVAT
```

**Table.RenameColumns** renames columns:

```
let
    Source = Excel.Workbook(...),
    Data = Source{[Item="Sheet1"]}[Content],
    Renamed = Table.RenameColumns(Data, {{"OldName", "NewName"}})
in
    Renamed
```

**Table.Group** aggregates data by a key:

```
let
    Source = Excel.Workbook(...),
    Data = Source{[Item="Sheet1"]}[Content],
    Grouped = Table.Group(Data, {"Category"}, {
        {"Count", each Table.RowCount(_)},
        {"Total", each List.Sum([Amount])}
    })
in
    Grouped
```

### Text Functions

**Text.Proper** converts text to title case:

```
Text.Proper("london")  // returns "London"
```

**Text.Upper** and **Text.Lower** do what you'd expect:

```
Text.Upper("hello")  // returns "HELLO"
Text.Lower("HELLO")  // returns "hello"
```

**Text.Length** returns the number of characters:

```
Text.Length("Excel")  // returns 5
```

**Text.Replace** substitutes text:

```
Text.Replace("Hello World", "World", "Excel")  // returns "Hello Excel"
```

### List Functions

**List.Sum** adds all values:

```
List.Sum({1, 2, 3, 4})  // returns 10
```

**List.Average** calculates the mean:

```
List.Average({10, 20, 30})  // returns 20
```

**List.Contains** checks for a value:

```
List.Contains({1, 2, 3}, 2)  // returns true
```

**List.Select** filters a list:

```
List.Select({1, 2, 3, 4, 5}, each _ > 2)  // returns {3, 4, 5}
```

## Building a Practical Example

Here's a real-world scenario: you have sales data in Excel. You need to load it, filter to the last 12 months, calculate commission (5% of sales over £1,000), and sum by region.

```
let
    // Load the Excel file
    Source = Excel.Workbook(File.Contents("C:\sales_data.xlsx")),
    SalesSheet = Source{[Item="Sales"]}[Content],
    
    // Change data types
    WithTypes = Table.TransformColumnTypes(SalesSheet, {
        {"Date", type date},
        {"Region", type text},
        {"Amount", type number}
    }),
    
    // Filter to last 12 months
    Today = DateTime.Date(DateTime.LocalNow()),
    OneYearAgo = Date.AddDays(Today, -365),
    RecentSales = Table.SelectRows(WithTypes, each [Date] >= OneYearAgo),
    
    // Calculate commission
    WithCommission = Table.AddColumn(
        RecentSales,
        "Commission",
        each if [Amount] > 1000 then [Amount] * 0.05 else 0
    ),
    
    // Group by region and sum
    ByRegion = Table.Group(
        WithCommission,
        {"Region"},
        {
            {"Total Sales", each List.Sum([Amount])},
            {"Total Commission", each List.Sum([Commission])}
        }
    )
in
    ByRegion
```

Breaking this down:

1. **Source** loads the Excel file
2. **SalesSheet** extracts the named sheet
3. **WithTypes** ensures columns have correct data types
4. **OneYearAgo** calculates the cutoff date
5. **RecentSales** keeps only recent records
6. **WithCommission** adds a calculated column with conditional logic
7. **ByRegion** groups and aggregates

Each step is simple on its own. Together they solve the business problem.

## Conditional Logic with If

Use `if` statements for conditional transformations:

```
if [Amount] > 1000 then "High" else if [Amount] > 500 then "Medium" else "Low"
```

In a column context:

```
let
    Source = Excel.Workbook(...),
    Data = Source{[Item="Sheet1"]}[Content],
    WithCategory = Table.AddColumn(
        Data,
        "Category",
        each if [Amount] > 1000 then "High" else if [Amount] > 500 then "Medium" else "Low"
    )
in
    WithCategory
```

## Handling Errors

The `try` keyword catches errors:

```
let
    Value = try Number.FromText("abc") otherwise 0
in
    Value
```

If the conversion fails, it returns 0 instead of crashing. Use this when importing messy data.

In a table context:

```
let
    Source = Excel.Workbook(...),
    Data = Source{[Item="Sheet1"]}[Content],
    SafeNumbers = Table.AddColumn(
        Data,
        "CleanAmount",
        each try Number.FromText([Amount]) otherwise 0
    )
in
    SafeNumbers
```

## Custom Functions

Define reusable functions with parameters:

```
let
    // Define a function that applies VAT
    ApplyVAT = (amount as number, rate as number) => amount * (1 + rate),
    
    // Use the function
    Result = ApplyVAT(100, 0.2)
in
    Result
```

For table transformations:

```
let
    // Define a function that filters by threshold
    FilterByAmount = (table as table, threshold as number) =>
        Table.SelectRows(table, each [Amount] > threshold),
    
    Source = Excel.Workbook(...),
    Data = Source{[Item="Sheet1"]}[Content],
    Filtered = FilterByAmount(Data, 1000)
in
    Filtered
```

Custom functions live in the same `let` block. Define them before you use them.

## Accessing the Advanced Editor

To write M code directly in Excel or Power BI:

1. Open Power Query (Data > Get & Transform > From Table/Sheet in Excel)
2. In the Power Query editor, click **Home > Advanced Editor**
3. Replace or edit the code directly
4. Click **Done** to apply

The visual transformations you've made are already converted to M. Edit them here for fine control.

## Debugging M Code

When something breaks, look at the error message. Power Query tells you which line failed and why.

Common issues:

- **Type mismatch**: You're trying to add a number to text. Use `Text.From()` to convert.
- **Column not found**: You've misspelled the column name or it doesn't exist yet. Check the spelling.
- **Null or empty values**: A calculation is trying to use data that's missing. Use `each try ... otherwise` to handle it.

Test each step independently. Wrap suspicious functions in `try ... otherwise` blocks.

## Performance Tips

M code runs in-memory. For large datasets:

- Filter early. Remove rows you don't need before grouping or joining.
- Use native Power Query functions instead of custom functions when possible.
- Avoid nested loops or recursive operations.

If a transformation takes too long, break it into smaller steps and profile each one.

## Further Reading and Learning

For deeper study, I recommend [M Language for Power Query](https://www.amazon.co.uk/s?k=power+query+m+language&tag=automatework-21) on Amazon UK — it covers advanced patterns and optimisation.

To accelerate your learning with video tutorials, try this [Power BI and Power Query course on Udemy](https://trk.udemy.com/DWnAjG), which includes dedicated M language sections with real-world projects.

The [official Microsoft documentation for M](https://learn.microsoft.com/en-us/powerquery-m/) is also free and comprehensive.

## Recommended Tools

- **Power BI Desktop**: Free. Write and test M code with immediate feedback.
- **Visual Studio Code**: Use the Power Query SDK extension for syntax highlighting.
- **Excel with Power Query**: Built into modern Excel. Perfect for learning in a familiar environment.

---

**What to do next:** Open Power Query in Excel right now. Grab a simple dataset. Create a new step, open the Advanced Editor, and write a `Table.SelectRows()` expression. Start small. Once you're comfortable filtering and adding columns with M, move to grouping and aggregation. M language is learned by doing, not reading.

Master M, and you'll never need a pivot table again — and your transformations become portable, reusable, and auditable.
```