---
layout: post
title: "How to Set Up Power Automate Scheduled Flows to Run Daily: A Step-by-Step Guide"
date: 2026-06-01
categories: [power-automate, automation]
description: "Learn how to create and configure daily scheduled flows in Power Automate with troubleshooting tips and best practices for reliability."
---

# How to Set Up Power Automate Scheduled Flows to Run Daily

Daily automated tasks are the backbone of modern business operations. Whether you need to send reports, update spreadsheets, archive data, or trigger notifications, Power Automate's scheduled flows let you set these up once and forget about them.

This guide walks you through creating a daily scheduled flow, configuring it correctly, and ensuring it runs reliably.

## What is a Power Automate Scheduled Flow?

A scheduled flow is a Power Automate workflow that runs on a fixed timetable without human intervention. Unlike cloud flows triggered by events (like when an email arrives), scheduled flows run at times you specify—every day, every week, or on custom intervals.

Daily scheduled flows are ideal for:
- Sending daily reports to stakeholders
- Backing up data from one system to another
- Running cleanup tasks on databases or SharePoint lists
- Extracting daily metrics for dashboards
- Consolidating data from multiple sources

The key advantage is consistency. Once configured, your flow runs automatically whether you're at your desk or not.

## Creating a Scheduled Flow in Power Automate

### Step 1: Access Power Automate

Open [Power Automate](https://make.powerautomate.com) in your browser and sign in with your work account.

From the left navigation pane, click **My flows**. Then select **New flow** and choose **Scheduled cloud flow**.

A dialog box appears asking you to name your flow. Enter a clear, descriptive name—something like "Daily Sales Report to Management" rather than "Flow1". This matters more than you'd think when you have dozens of flows running.

### Step 2: Set the Schedule Frequency

After naming your flow, you'll see the schedule configuration panel.

The first dropdown is **Repeat every**. This controls the interval. Set it to:
- **Value**: 1
- **Unit**: Day

This ensures your flow runs once every 24 hours.

If you need it to run multiple times daily, change the value to a smaller unit:
- Run every 12 hours: Value = 12, Unit = Hour
- Run every 6 hours: Value = 6, Unit = Hour

### Step 3: Set the Time Zone and Start Time

Below the repeat settings, click **Show advanced options** to reveal the timezone and scheduling details.

**Time Zone**: Select your local time zone. This is crucial. If you select the wrong timezone, your flow runs at a time eight hours ahead or behind what you expect. For UK-based operations, select "GMT Standard Time" or "GMT Daylight Time" depending on the season.

**Start**: This field shows the date and time your flow first runs. By default, it's set to the current date and time. If you don't want the flow to run immediately, adjust this to a future date and time.

For example, if it's currently 10:00 AM and you want the flow to run daily at 2:00 AM, set the start time to tomorrow at 2:00 AM.

### Step 4: Add Your Flow Actions

Click **+ New step** to start building what your flow actually does.

Common first actions include:
- **Send an email**: Use the "Send an email (V2)" action from Office 365 Outlook
- **Create a file**: Write data to OneDrive or SharePoint
- **Query data**: Use actions from Excel Online, SharePoint, SQL Server, or Dataverse
- **Run a script**: Execute Power Automate desktop flows or Power Fx expressions

Let's work through a practical example: a daily flow that sends a summary email.

### Step 5: Example – Daily Email Summary

Add the **Send an email (V2)** action.

Configure:
- **To**: Enter the recipient's email address (or use a dynamic field from a previous action)
- **Subject**: "Daily Report – [Date]" (you can use dynamic content here)
- **Body**: Compose your message. Include tables, links, and formatted text

To add dynamic content (like today's date), click the **Add dynamic content** button and select from variables or previous action outputs.

If you're pulling data from Excel, add a **Get rows present in a table** action first (using Excel Online). Then reference those rows in your email body using dynamic content.

### Step 6: Save and Test

Click **Save** in the top-right corner.

Power Automate now shows your flow. To test it immediately without waiting for the scheduled time, click the three dots (•••) menu and select **Test**.

Choose **I'll perform the trigger action** and click **Test**. Your flow runs instantly. Check that emails send, files are created, or data is updated as expected.

If something fails, the error message tells you exactly which action broke and why. Common issues include:
- Missing permissions (Excel, SharePoint, email accounts)
- Incorrect field references in dynamic content
- API rate limits (if querying large datasets)

## Advanced Configuration for Daily Flows

### Staggered Start Times Across a Team

If you have multiple users each running a daily summary flow, start times matter. If everyone's flow runs at 9:00 AM, you might hit API throttling limits or slow down your organisation's infrastructure.

Stagger start times by 15 minutes:
- User 1: 9:00 AM
- User 2: 9:15 AM
- User 3: 9:30 AM

Configure each user's flow with a different **Start** time in the schedule settings.

### Conditional Execution

You can use conditions to skip runs on weekends or holidays.

After your trigger, add an **Condition** action:
- **Choose a value**: Use the `dayOfWeek()` function with the trigger time
- **Is equal to**: Select 0 (Sunday) or 6 (Saturday)
- **If yes**: Add a **Terminate** action to stop the flow
- **If no**: Continue with your normal actions

This prevents reports running on Saturdays or Sundays.

### Handling Failures and Retry Logic

By default, if an action fails, the entire flow fails and stops. For critical daily tasks, this is dangerous.

Click the three dots on any action and select **Configure run after**. Choose which action outcomes should trigger the next step:
- Has succeeded
- Has failed
- Is skipped
- Has timed out

For example, if your "Send email" action fails, configure it to retry automatically or to trigger an alternative notification method.

### Monitoring and Logging

Every time your flow runs, Power Automate logs the result. Access the flow's run history to see:
- Start and end times
- Pass or fail status
- Detailed error messages
- Input and output data

Click on any run to drill into what happened. This is essential for troubleshooting if your flow unexpectedly stops running.

## Common Issues with Daily Scheduled Flows

### Flow Doesn't Run at the Scheduled Time

**Cause**: Timezone mismatch or incorrect start date.

**Fix**: Open your flow, click the three dots, select **Edit**, and verify the timezone matches your location. Check that the start date is set to today or earlier.

### Flow Runs Multiple Times

**Cause**: Duplicate triggers or accidental manual runs.

**Fix**: Check that you've created only one scheduled trigger. If you copy a flow, delete the old version. Verify no one else has created a similar flow for the same task.

### Flow Runs but Actions Fail Silently

**Cause**: Permissions or data format issues.

**Fix**: Enable detailed logging. In the action settings, turn on "Result options" and set "Keep inputs and outputs" to "Yes". This reveals exactly what data was passed to each action and where it failed.

### Daily Flow Stops Running After a Week

**Cause**: Flow owner changed roles or left the organisation. Credentials invalidated.

**Fix**: Ensure the flow owner remains active. If they leave, transfer ownership. Check connection credentials haven't expired. Power Automate typically refreshes these automatically, but manual re-authentication is sometimes needed.

## Best Practices for Reliable Daily Flows

**1. Name flows descriptively**
Use the format: "[Frequency] [Task] [Owner]". Example: "Daily Sales Data to Analytics – Tom".

**2. Document your flow**
Add a comment at the start describing what it does and who to contact if it breaks. Use the notes section in Power Automate.

**3. Test across timezones**
If your organisation spans multiple timezones, test that the flow respects each user's local time correctly.

**4. Set up alerts**
Use a separate flow to notify you when critical daily flows fail. Add a "Send me an email notification" action within the failed flow's "Configure run after" settings.

**5. Review run history monthly**
Set a calendar reminder to check your critical flows' run history. Look for patterns of failure or unexpected behaviour.

**6. Avoid peak hours**
Don't schedule flows during peak business hours (9–10 AM, lunch hours, or end-of-day). Schedule them early morning (3–5 AM) or evening (7–9 PM) for better performance.

## Recommended Tools

If you're building complex daily workflows, invest in understanding automation fundamentals. [**Automate Your Life with Excel, Power BI, and Power Automate**](https://www.amazon.co.uk/Automate-Your-Excel-Power-Automate/dp/B0CKLZ3W7Z?tag=automatework-21) on Amazon provides practical examples of daily automation patterns and troubleshooting.

For deeper Power Automate skills, take a structured [Udemy course on Power Automate fundamentals][UDEMY_AFFILIATE_LINK]. A few hours of focused learning saves weeks of trial-and-error.

## Further Reading

- Microsoft's official [Power Automate documentation on scheduled flows](https://learn.microsoft.com/en-us/power-automate/flow-types)
- How to use [dynamic content and expressions](https://learn.microsoft.com/en-us/power-automate/use-expressions-in-conditions) in Power Automate
- Setting up [error handling and retry policies](https://learn.microsoft.com/en-us/power-automate/error-handling)

---

*This article contains affiliate links. If you purchase through them I may earn a small commission at no extra cost to you. See [disclosure](/POD-and-Affiliate/privacy/).*