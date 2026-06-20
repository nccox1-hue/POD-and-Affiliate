```markdown
---
layout: post
title: How to Make a Fishbone Ishikawa Diagram in Excel
date: 2026-06-20
categories: [excel]
description: Step-by-step guide to creating a fishbone diagram in Excel for root cause analysis. No add-ins needed.
---

*This article contains affiliate links. If you purchase through them I may earn a small commission at no extra cost to you. See [disclosure](/POD-and-Affiliate/privacy/).*

A fishbone diagram (also called an Ishikawa diagram) is a structured visual tool for identifying potential causes of a problem. It organises causes into categories and branches, making it easy to spot patterns and root causes. Excel isn't the most intuitive tool for this task, but you can build a professional-looking fishbone diagram using shapes, connectors, and text. No add-ins required.

This guide walks you through creating one from scratch, then shows you how to adapt it for your own analysis.

## Why Use a Fishbone Diagram?

Before you start building, understand why this format matters:

- **Systematic thinking**: Forces you to categorise causes rather than listing them randomly
- **Team collaboration**: Visual format makes discussions concrete
- **Problem documentation**: Creates a record you can reference later
- **Root cause identification**: Helps distinguish symptoms from actual causes

Manufacturing teams use fishbone diagrams during quality improvement sessions. HR uses them to analyse turnover. Finance teams apply them to variance investigations. The structure works across any domain.

## When to Use Excel vs. Other Tools

Excel isn't ideal for fishbone diagrams. Tools like Miro, Lucidchart, or dedicated quality management software offer templates and auto-layout features. However:

- You may not have access to specialist tools
- Your organisation standardises on Excel
- You want to embed the diagram in an existing workbook
- You need offline-first capability

If you're creating dozens of diagrams regularly, a dedicated tool saves time. For occasional use, Excel works fine.

## Setting Up Your Excel Workbook

Start fresh. Open Excel and set up landscape orientation and a blank worksheet.

**Step 1: Change page orientation**

1. Go to the **Page Layout** tab
2. Click **Orientation** and select **Landscape**
3. Set margins to **Narrow** to maximise space

**Step 2: Adjust row and column width**

1. Select all cells (Ctrl+A)
2. Right-click and choose **Column Width** — set to 3
3. Right-click again and choose **Row Height** — set to 20

This gives you a grid with square-ish cells, making diagonal lines easier to draw.

## Building the Main Spine

The fishbone diagram has a central spine running left to right, with the problem statement at the right end.

**Step 3: Insert the problem box**

1. Go to **Insert > Shapes** and select a rectangle
2. Draw a rectangle on the right side of the sheet, around columns O–P, rows 8–10
3. Right-click the shape and select **Edit Text**
4. Type your problem statement (e.g., "Missed Delivery Deadlines")
5. Format the text: bold, centre-aligned, white font on dark background

**Step 4: Draw the main spine**

1. Go to **Insert > Shapes** and select **Line**
2. Draw a horizontal line from the left edge of your sheet towards the problem box
3. Hold Shift while dragging to keep the line perfectly horizontal
4. Right-click the line and format it: thicker stroke (2pt+), dark colour

The spine should end roughly at the left edge of your problem box.

## Adding the Main Bone Categories

Most fishbone diagrams use four to six main categories. Traditional manufacturing uses:

- Materials
- Methods
- Machine
- Manpower (People)
- Measurement
- Environment

Adjust these for your context. A software project might use: Process, People, Tools, Documentation, External Factors.

**Step 5: Create diagonal branch lines**

1. Go to **Insert > Shapes > Line**
2. Draw a diagonal line from the spine upwards (roughly 45 degrees)
3. Position the first line around column F, angling up-right
4. Draw a matching line below the spine, angling down-right
5. Repeat this process, spacing the pairs evenly along the spine

You'll typically draw 3–4 pairs of diagonal lines (6–8 branches total). For this example, use 6 main branches.

**Step 6: Add category labels**

1. Insert a text box (Insert > Text Box) above the first upper diagonal line
2. Type a category name (e.g., "Materials")
3. Format it: bold, 11pt font, dark colour
4. Repeat for the remaining 5 categories, alternating above and below the spine

Position labels so they're clearly associated with their respective diagonal lines but don't overlap other elements.

## Adding Secondary Bones (Sub-causes)

This is where detail goes. Each main category branches into 2–4 secondary causes.

**Step 7: Add secondary lines**

1. Go to **Insert > Shapes > Line**
2. Draw short lines (2–3cm) branching off each main diagonal at roughly 30–45 degree angles
3. Draw 3–4 secondary lines per main category
4. Keep these lines thinner (1–1.5pt) than the main spine and diagonals

Stagger the secondary lines so labels don't overlap.

**Step 8: Label secondary causes**

1. Insert text boxes next to each secondary line
2. Add specific causes under each category

For example, under "Materials":
- Supplier delays
- Incorrect specifications
- Poor quality batches

Under "Methods":
- Inefficient scheduling
- Lack of prioritisation
- Manual data entry errors

Keep labels concise — 2–4 words maximum.

## Example: Missed Delivery Deadlines

Here's what a complete diagram structure looks like:

**Main categories (primary bones):**
- Materials
- Methods
- Machine
- People
- Measurement
- Environment

**Secondary causes (secondary bones):**

*Materials*
- Supplier delays
- Quality issues
- Incorrect specs

*Methods*
- Poor scheduling
- Manual processes
- No priority system

*Machine*
- Equipment downtime
- Inadequate capacity
- System failures

*People*
- Staff shortages
- Lack of training
- Low morale

*Measurement*
- Inaccurate forecasting
- Unreliable tracking
- Missing data

*Environment*
- Regulatory delays
- Market disruptions
- Transport issues

## Formatting and Polishing

A well-formatted diagram is easier to read and looks professional.

**Step 9: Unify your colour scheme**

1. Select all your lines (hold Ctrl and click each line)
2. Right-click and choose **Format Shape**
3. Set stroke colour to a dark colour (navy, dark grey, or black)
4. Set main spine to 2.5pt, diagonals to 2pt, secondary lines to 1pt

**Step 10: Add borders and backgrounds**

1. Select your problem statement box
2. Right-click and format it with a bold border (3pt) and a contrasting fill colour
3. Keep text readable (white on dark, or dark on light)

**Step 11: Align and balance**

1. Use Excel's alignment tools to ensure symmetry
2. Go to **Home > Arrange > Align** to align shapes
3. Distribute secondary lines evenly along each main diagonal

**Step 12: Add a title and legend (optional)**

1. Insert a text box at the top of the sheet
2. Type your diagram title (e.g., "Root Cause Analysis: Delivery Performance")
3. Add date and team name if this is for documentation

## Making Your Fishbone Reusable

**Step 13: Save as a template**

1. Once your blank fishbone structure is complete (before adding specific causes), save it
2. Go to **File > Save As**
3. Choose **Excel Template (.xltx)** as the file format
4. Name it "Fishbone_Template"

Now you can open this template, add your specific problem statement and causes, and save each analysis separately.

**Step 14: Create a data table companion**

Many teams pair the diagram with a spreadsheet that lists:

1. Each cause
2. How it contributes to the problem
3. Who owns investigating it
4. What data supports this cause

This table lives on a separate sheet in the same workbook, linking the visual analysis to your investigation process.

## Common Mistakes to Avoid

- **Overcrowding**: Too many secondary bones makes the diagram unreadable. Limit to 3–4 per category.
- **Inconsistent sizing**: Keep primary bones roughly the same length. Secondary bones should be noticeably shorter.
- **Poor labelling**: Labels should be short, specific, and positioned so they clearly belong to their line.
- **Mixing cause types**: Stick to actual causes, not solutions. "Poor training" is a cause; "improve training" is a solution.
- **Neglecting balance**: If one side of the spine has many more bones than the other, reconsider your categorisation.

## Moving Beyond Excel

If you regularly create fishbone diagrams, consider these alternatives:

- **[Miro](https://miro.com)** — collaborative whiteboard with fishbone templates
- **[Lucidchart](https://www.lucidchart.com)** — diagramming tool with Ishikawa templates
- **Power BI + Power Automate** — automate data capture and feed results into visual dashboards

For single or occasional diagrams, Excel is sufficient. For team-based root cause analysis in quality or continuous improvement roles, a dedicated tool saves significant time.

## Further Reading and Recommended Tools

To deepen your knowledge of root cause analysis and problem-solving frameworks:

- **[The Goal by Eliyahu Goldratt](https://www.amazon.co.uk/Goal-Process-Ongoing-Improvement/dp/0566086654?tag=automatework-21)** — while not specifically about fishbone diagrams, it covers systems thinking and constraint theory that underpin cause-and-effect analysis
- **[Complete Excel skills course on Udemy](https://trk.udemy.com/DWnAjG)** — if you want to master Excel shapes, connectors, and diagramming features beyond fishbone basics

**Disclosure:** The Amazon and Udemy links are affiliate links. If you purchase through them, I earn a small commission at no extra cost to you.

---

*Next step: Once you've created your fishbone diagram, use it to guide your investigation. For each secondary cause, gather data. Run small tests. Document what you find. The diagram is a starting point, not a conclusion.*
```