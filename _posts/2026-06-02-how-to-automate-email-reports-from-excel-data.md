```markdown
---
layout: post
title: "How to Automate Email Reports from Excel Data: Complete Guide"
date: 2026-06-02
categories: [power-automate, excel, automation]
description: "Send Excel reports automatically via email using Power Automate. Step-by-step guide with templates and best practices."
---

# How to Automate Email Reports from Excel Data: Complete Guide

Sending the same Excel reports to the same people every week is busywork. You shouldn't be doing it manually. Whether you're distributing sales figures, performance metrics, or inventory data, automation saves time and eliminates human error.

This guide shows you how to set up automated email reports from Excel data using Power Automate. You'll learn three practical approaches: emailing Excel files directly, sending formatted HTML tables, and embedding Power BI visuals. Pick the method that fits your workflow.

## Why automate email reports?

Before diving into the how, understand the why:

- **Consistency**: Reports go out on schedule, every time
- **Speed**: No manual copying, pasting, or file management
- **Accuracy**: Automated formulas and exports eliminate typos
- **Scalability**: Add recipients without adding work
- **Auditability**: Clear record of what was sent and when

Manual reporting typically costs 2-4 hours per week per person. Even a basic automation saves that time immediately.

## What you need

To follow this guide, you'll need:

- A Microsoft 365 subscription (Excel online and Power Automate)
- Excel file stored in OneDrive or SharePoint (not local machine)
- Power Automate cloud flow access
- Basic understanding of Excel formulas
- Email recipients identified

If your Excel data lives on your local machine, upload it to OneDrive first. Power Automate can't access files that aren't in the cloud.

## Method 1: Email the Excel file directly

This is the simplest approach. Use it when recipients need the full dataset or need to pivot and analyse the data themselves.

### Step 1: Prepare your Excel file

Create or open your report file in Excel. Keep these practices in mind:

- Use a consistent naming convention: `Sales_Report_June2026.xlsx`
- Ensure formulas calculate correctly before automation
- Store the file in OneDrive for Business or a SharePoint library
- Test the file manually first

Let's say you have a sales file at `OneDrive/Reports/Sales_Report.xlsx` with columns for Date, Region, Revenue, and Target.

### Step 2: Create a Power Automate cloud flow

Open [Power Automate](https://flow.microsoft.com) and click **+ Create**.

Select **Cloud flow** → **Scheduled cloud flow**. Name it `Weekly Sales Report Email` and set the schedule:

- Repeat every: 1 week
- On: Monday
- At: 09:00

Click **Create**.

### Step 3: Add the trigger

Your scheduled trigger is already set. Now add an action.

Click **+ New step** and search for **Get file content**. Select the OneDrive action.

- Location: OneDrive for Business
- File: `/Reports/Sales_Report.xlsx`

### Step 4: Send the email with attachment

Click **+ New step** and search for **Send an email**. Choose **Send an email (V2)** from the Office 365 Outlook connector.

Fill in:

- **To**: recipient@company.com (or use a distribution list)
- **Subject**: `Weekly Sales Report – Week of June 2`
- **Body**: 
```
Hi team,

Please find this week's sales report attached. 

Key dates:
- Report period: Monday-Sunday
- Generated: Today's date
- Due back: Friday

Questions? Contact the sales operations team.

Best regards,
[Your name]
```

For the **Attachments** field:

- **Attachment name**: `Sales_Report_@{utcNow('yyyy-MM-dd')}.xlsx`
- **Attachment content**: Select the file content from the previous step

This timestamps the filename so each email has a unique attachment.

### Step 5: Test and enable

Click **Save**. Then click the play button to test immediately. Check your inbox for the email—it should arrive within a minute.

Once confirmed, the flow runs automatically on schedule.

## Method 2: Email a formatted HTML table

Use this when you want the data visible in the email itself, without requiring recipients to open an attachment. This works well for summaries and dashboards.

### Step 1: Prepare your data

Create a summary table in Excel. Keep it concise—no more than 20 rows. Power Automate handles HTML conversion best with clean, simple tables.

Use Excel's built-in table feature: Select your data range and press **Ctrl+T**. Name it something like `SalesTable`.

### Step 2: Create the flow

Open Power Automate and create a new **Scheduled cloud flow** as above.

### Step 3: Get the Excel table

Click **+ New step** and search for **List rows present in a table**. This is the Excel Online connector.

Configure:

- **Location**: OneDrive for Business
- **Document Library**: OneDrive
- **File**: Select your Excel file
- **Table**: Select the table you created (e.g., `SalesTable`)

### Step 4: Convert to HTML table

Click **+ New step** and search for **Create HTML table**. Select the Power Automate action.

- **From**: The value of the previous step (list rows)
- **Columns**: Leave as "Auto"

This transforms your Excel rows into HTML automatically.

### Step 5: Send formatted email

Click **+ New step** → **Send an email (V2)**.

Configure:

- **To**: recipient@company.com
- **Subject**: `Weekly Performance Summary`
- **Body**:

```
Hi team,

Here's this week's performance snapshot:

[Select the HTML table output from the previous step]

Last updated: [Today's date]
```

In the body field, click where you want the table and select **Output** from the Create HTML table step.

### Step 6: Add conditional logic (optional but useful)

You might want to send the report only if certain conditions are met. For example, send the report only if revenue exceeds a threshold.

Click **+ New step** → **Condition**.

Set up a condition like:

- If [Total Revenue] is greater than [Target] → send email
- Otherwise → don't send

This prevents spam when data is incomplete or doesn't meet reporting criteria.

## Method 3: Embed Power BI visuals in emails

For stakeholders who want visual insights without opening attachments, embed Power BI charts directly in emails.

### Prerequisites

- Power BI Premium or Pro licence
- A Power BI report created from your Excel data
- Power BI publish permissions

### Step 1: Create a Power BI report

Upload your Excel file to Power BI and create a simple report with 1-3 key visuals. Keep it clean—busy dashboards don't translate well to email.

### Step 2: Create the Power Automate flow

Set up a **Scheduled cloud flow** as before.

### Step 3: Get Power BI visual

Click **+ New step** and search for **Export to file**. Use the Power BI connector.

Configure:

- **Workspace**: Select your workspace
- **Report**: Select your Power BI report
- **Format**: PowerPoint (exports visuals clearly)

### Step 4: Send email with visual attachment

Click **+ New step** → **Send an email (V2)**.

- **To**: recipient@company.com
- **Subject**: `BI Report – June Performance`
- **Body**: Add context and commentary
- **Attachments**: Use the exported file from Power BI

This gives recipients a visual summary without needing Power BI access.

## Best practices for automated reports

### Schedule thoughtfully

Send reports when people actually read them. Morning emails perform better than afternoon ones. Friday reports are often ignored. Early-week reports drive action.

### Keep subject lines clear

Use patterns recipients recognise: `[Team] Report – [Period]`. Avoid vague subjects like "Update" or "Data".

### Include context, not just data

Every email should answer: What is this? Why should I care? What should I do with it?

### Avoid recipient overload

Don't add people to reports "just in case." If someone doesn't use the data within a month, remove them.

### Version control

Use timestamps in filenames: `Report_2026-06-02.xlsx`. This prevents confusion when recipients compare versions.

### Test for edge cases

What happens if the Excel file is empty? If there's missing data? Add error handling:

Click **+ New step** → **Condition** → check if data exists before sending.

## Troubleshooting common issues

**Email not sending?**
Check recipient email addresses for typos. Verify the account has appropriate permissions. Test with a single recipient first.

**Attachment not appearing?**
Confirm the file is stored in OneDrive or SharePoint, not your local machine. Refresh the Power Automate connection if recently moved the file.

**Timing is wrong?**
Power Automate uses UTC time. Adjust for your timezone. A 9 AM trigger in UTC might not align with your local 9 AM.

**File too large?**
Excel files over 4 MB can cause issues. Split large reports into multiple files or use Power BI instead.

**Recipients complain about formatting?**
HTML tables sometimes render oddly in Outlook. Test in Outlook before deploying to all recipients. Consider attaching the Excel file instead.

## Scaling beyond basic reports

Once your first automation runs reliably, consider:

- **Multiple recipient groups**: Create separate flows for different teams with tailored data
- **Conditional logic**: Send alerts only when metrics cross thresholds
- **Approval workflows**: Route reports for review before sending to external stakeholders
- **Archive automations**: Save sent reports to SharePoint for auditing

If your reporting needs grow complex, explore [Power BI Premium](/POD-and-Affiliate/privacy/) with [Microsoft's Power Automate documentation](https://learn.microsoft.com/en-us/power-automate/) for advanced options.

## Learning Power Automate properly

If you're new to automation, [this Udemy course on Power Automate fundamentals][UDEMY_AFFILIATE_LINK] provides solid grounding in flow design, error handling, and best practices beyond email reporting.

For deeper Excel integration, consider *Automate Your Day with Excel and Power Automate* on [Amazon UK](https://www.amazon.co.uk/Automate-Your-Day-Excel-Power/dp/B0CVTX4PSF?tag=automatework-21), which covers practical scenarios like yours with step-by-step screenshots.

## Quick reference checklist

Before going live with your automation:

- [ ] Excel file is in OneDrive or SharePoint
- [ ] All formulas calculate correctly
- [ ] Recipient email addresses verified
- [ ] Subject line is clear and searchable
- [ ] Email body includes context and next steps
- [ ] Tested the flow at least once manually
- [ ] Schedule is realistic and sustainable
- [ ] Error notifications are configured

## Further reading

- [Power Automate connector reference](https://learn.microsoft.com/en-us/connectors/)
- [Excel best practices for automation](https://support.microsoft.com/en-us/office/best-practices-for-sharing-excel-files)
- [Outlook rules and filters guide](https://support.microsoft.com/en-us/office/manage-email-messages-by-using-rules)

*This article contains affiliate links. If you purchase through them I may earn a small commission at no extra cost to you. See [disclosure](/POD-and-Affiliate/privacy/).*
```