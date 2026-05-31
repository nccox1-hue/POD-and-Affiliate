---
layout: post
title: "How to Merge Tables in Excel Without VLOOKUP Using Power Query"
date: 2026-05-31
categories: excel power-query
description: "Stop using VLOOKUP to combine spreadsheets. Power Query's Merge Queries does it faster, handles duplicates cleanly, and updates automatically when your data changes."
---

If you're still using VLOOKUP to combine data from two spreadsheets, this guide will save you hours every month.

Power Query's **Merge Queries** feature does everything VLOOKUP does — and handles things VLOOKUP can't: multiple matching columns, one-to-many relationships, automatic refresh when data changes, and no broken formulas when rows are inserted.

## What you'll build

A clean combined table that pulls matching data from a second sheet — equivalent to a VLOOKUP but more robust and fully automated.

**Example:** You have a sales table with product codes, and a separate price list. You want to pull the price into the sales table for each row. Classic VLOOKUP job — but we'll do it better.

## Step 1: Load both tables into Power Query

First, convert both ranges to Excel Tables (this is important — Power Query works best with named tables).

1. Click anywhere inside your sales data
2. Press **Ctrl+T** → tick "My table has headers" → OK
3. Name the table: in the **Table Design** tab, change the name from Table1 to `Sales`
4. Repeat for your price list table — name it `Prices`

Now load them into Power Query:

1. Click inside the `Sales` table
2. Go to **Data → Get Data → From Table/Range**
3. Power Query opens. Click **Home → Close & Load → Close & Load To...**
4. Choose **Only Create Connection** → OK
5. Repeat for the `Prices` table

Both tables are now available as queries in Power Query.

## Step 2: Merge the queries

1. Go to **Data → Get Data → Combine Queries → Merge**
2. In the top dropdown, select `Sales`
3. Click the column you want to match on — e.g. `Product Code`
4. In the second dropdown, select `Prices`
5. Click the matching column in the Prices table — `Product Code`
6. Leave Join Kind as **Left Outer** (keeps all rows from Sales, adds matching data from Prices)
7. Click OK

## Step 3: Expand the joined column

Power Query adds a new column called `Prices` with a table icon. Click the **expand icon** (two arrows) at the top of that column.

Untick any columns you don't need, tick `Price`, untick "Use original column name as prefix" → OK.

You'll now see the price pulled in for each row.

## Step 4: Load the result

Click **Home → Close & Load**. A new sheet appears with your merged table.

## Why this beats VLOOKUP

| | VLOOKUP | Power Query Merge |
|---|---|---|
| Breaks when rows inserted | Yes | No |
| Handles duplicates | First match only | All matches |
| Match on multiple columns | Complex workaround | Built-in |
| Refreshes automatically | No | Yes (Ctrl+Alt+F5) |
| Formula audit trail | Messy | Clean query steps |

## Refreshing when data changes

When your source data updates, just press **Ctrl+Alt+F5** (Refresh All) and the merged table updates instantly. No re-running formulas, no re-doing the VLOOKUP.

## Recommended reading

If you want to go deeper on Power Query, Ken Puls and Miguel Escobar's [M is for Data Monkey](https://www.amazon.co.uk/dp/1615470344) is the definitive guide. It covers everything from basic merges to complex transformations.

*This post contains affiliate links. See [disclosure](/POD-and-Affiliate/privacy/).*
