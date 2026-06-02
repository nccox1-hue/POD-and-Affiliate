---
layout: post
title: "Power Automate Approval Workflow Step by Step: Complete Guide"
date: 2026-05-31
categories: [power-automate]
description: "Learn how to build approval workflows in Power Automate with our complete step-by-step guide. Create efficient business processes today."
---

## Power Automate Approval Workflow Step by Step: Complete Guide

Approval workflows are the backbone of business process automation. Whether you're managing expense requests, document reviews, or leave applications, Power Automate makes it straightforward to route approvals to the right people, track decisions, and automate follow-up actions.

This guide walks you through building a functional approval workflow from scratch, without unnecessary jargon.

## Why Use Power Automate for Approvals?

Manual approval processes are slow. Email chains get lost. You can't track who approved what or when. Power Automate solves this by:

- Routing requests automatically to the correct approver
- Sending notifications at each stage
- Creating an audit trail
- Triggering actions based on approval or rejection (like creating records or sending confirmations)
- Handling multiple approvers and parallel approvals

A typical approval workflow saves 30-40 minutes per request compared to manual email processes. For organisations processing dozens of requests weekly, that's significant.

## Understanding the Core Components

Before you build, understand the five key elements:

**Trigger**: What starts the workflow? (New form submission, email, button click, scheduled time)

**Connector**: How does Power Automate access your data? (SharePoint, Excel, Outlook, Teams, custom APIs)

**Approvals action**: The built-in approval step that sends the request and waits for response

**Condition**: Logic that routes the workflow based on approval or rejection

**Actions**: What happens next (send email, create record, update spreadsheet)

## Step-by-Step: Building Your First Approval Workflow

### Step 1: Choose Your Trigger

Log into Power Automate at [flow.microsoft.com](https://flow.microsoft.com). Click **Create** and select **Cloud flow** > **Automated cloud flow**.

Name your flow something descriptive: "Expense Report Approval" or "Leave Request Workflow".

For **Choose your flow's trigger**, pick one of these common options:

**Button trigger** (fastest to test): Select "Manually trigger a flow". This lets you run the workflow on demand while testing.

**SharePoint trigger** (most common for forms): Select "When an item is created". Connect to your SharePoint site and list.

**Microsoft Forms trigger**: Select "When a new response is submitted" if you're collecting data via Forms.

**Email trigger**: Select "When a new email arrives" to process inbound requests.

For this guide, we'll use SharePoint. After selecting "When an item is created", choose your site and the list where approval requests are stored.

### Step 2: Add the Approval Action

Click **New step** and search for "Approvals". Select the action **Start and wait for an approval**.

This is the core of your workflow. Configure these fields:

**Approval type**: Choose one of five options:
- **Approve/Reject** (simplest — yes or no)
- **Approve/Reject/Reassign** (adds reassignment option)
- **Custom Responses** (define your own options like "Approved", "Needs Changes", "Rejected")

For most workflows, "Approve/Reject" is sufficient.

**Title**: What the approver sees at the top of their request. Use dynamic content (the **fx** button) to pull the request title from your form or SharePoint list. Example: "Expense Report from @{triggerOutputs()?['body/Title']}"

**Assigned to**: Who approves this? Enter their email address. For multiple approvers, separate with semicolons.

You can also use dynamic content here. If you have an "Approver Email" field in your form, reference it: `@{triggerOutputs()?['body/Approver_Email']}`

**Details**: Include relevant information for the approver. Pull fields from your trigger data:

```
Requested by: [Employee Name]
Amount: [Expense Amount]
Category: [Category]
Date Submitted: [Submission Date]
Justification: [Business Purpose]
```

Use the dynamic content picker to insert actual values from your SharePoint list or form response.

**Link to item**: (Optional but recommended) Add a link to the full request so approvers can see attachments or additional details. Use: `@{triggerOutputs()?['body/{Link}']}`

### Step 3: Add a Condition to Handle the Response

Click **New step** and search for "Condition". This determines what happens based on the approval decision.

In the first box (the condition), click and select **Outcome** from dynamic content. This is the result of your approval action.

Set the condition to:
- **is equal to** **Approve**

Leave the second and third boxes blank for now.

### Step 4: Configure Actions for "Approve" Path

In the **If yes** section, add the actions that run when approved. Common options:

**Send an approval notification email**:
- Search for **Send an email (V2)**
- Set **To** to the original requester's email
- Subject: "Your expense report has been approved"
- Body: Include the amount, date, and next steps (e.g., "You'll receive reimbursement within 5 business days")

**Update the SharePoint list**:
- Search for **Update item**
- Select your SharePoint site and list
- Set **ID** to the item ID from your trigger
- Update **Status** to "Approved"
- Update **Approval Date** to `@{utcNow()}`
- Update **Approver Name** (optional) to track who approved

**Create a record in another system**:
- If you use Dynamics 365 or another CRM, create an approval record here

### Step 5: Configure Actions for "Reject" Path

Click **Add an action** in the **If no** section (rejection path).

**Send rejection notification**:
- Search for **Send an email (V2)**
- To: Original requester
- Subject: "Your expense report requires revision"
- Body: Include a reason field if you've added that to your approval action. Use dynamic content to reference **Comments** from the approval response.

**Update the list status**:
- Select **Update item** again
- Set **Status** to "Rejected"
- Add **Rejection Date** and **Rejection Reason** fields if needed

**Optionally reassign**:
- If your approval type supports reassignment, add an action to send an email to a manager: "This request was reassigned. Please review and approve."

## Step 6: Test Your Workflow

Before going live, test thoroughly:

1. Click **Save**
2. Click **Test**
3. Select **Manually trigger your flow**
4. Click **Test**

This runs the trigger step only (if you used a button trigger). For SharePoint triggers, create a test item in your list manually.

Once the flow starts, Power Automate shows you each step. Check that:
- The approval notification arrives in the approver's inbox
- The title and details are clear and complete
- Email links work and open the correct item

Approve the request and verify the "Approve" actions execute (email sent, status updated). Then test rejection.

## Common Workflow Variations

### Multiple Serial Approvers

Need requests to go through several people in sequence?

After the first approval's "Approve" branch, add another **Start and wait for an approval** action for the second approver. Use the same structure: assign to the next person, set their specific details, and add conditions for their approval/rejection.

Serial approvals take longer but ensure thorough review.

### Parallel Approvers

Multiple people reviewing simultaneously?

Use **Approvals - Start and wait for an approval** with multiple email addresses in the **Assigned to** field: `approver1@company.com; approver2@company.com`

Power Automate sends the request to all of them simultaneously. The workflow waits until all have responded (or a timeout occurs, which you can set in advanced options).

### Manager-Based Routing

Route approvals based on employee data?

Add a **Get item** action to pull the employee record from your HR list. Use the **Assigned to** field from that record:

```
@{body('Get_item')?['Approver_Email']}
```

This scales to hundreds of employees without manually updating the flow.

### Conditional Amounts

High-value expenses need extra approval?

Add a **Condition** before your approval action:

- If **Amount** is greater than 5000
  - Send to Finance Director
- Otherwise
  - Send to Team Manager

This keeps low-value requests moving fast while catching high-risk ones.

## Monitoring and Troubleshooting

### Check Flow History

In Power Automate, open your flow and click **Analytics**. You'll see:
- Total runs
- Success rate
- Average duration
- Failed runs (with error details)

Click **All runs** to see individual flow instances and their step-by-step execution.

### Common Issues and Fixes

**Approvals never arrive in inbox**: Check your trigger configuration. Ensure the "Assigned to" field contains a valid email. Test with your own email first.

**Flow times out**: Approval actions wait 30 days by default. If that's insufficient, edit the approval action, click **Settings**, and adjust **timeout**.

**Dynamic content shows no fields**: Ensure your trigger has completed at least once. Power Automate learns available fields from actual data.

**Approver sees blank details**: You're likely referencing fields that don't exist in your data source. Check field names in your SharePoint list or form; they're case-sensitive.

## Best Practices for Approval Workflows

**Be specific in titles**: "Approval Required" is useless. "Travel Expense Approval — £247.50 for client meeting" tells the approver what they're reviewing in one line.

**Include context**: Put the most important information in the approval title and details. Don't force approvers to click links to see basic facts.

**Set expectations**: Clearly state the approval timeline. "Finance will approve within 2 business days" or "Manager approval required within 24 hours" prevents confusion.

**Log everything**: Always update your source system (SharePoint, database) with approval status and dates. You'll need this for audits and reporting.

**Test with real data**: Use actual request data when testing, not dummy examples. Real data often reveals issues with field names, formatting, or missing values.

**Notify all parties**: Send confirmation emails to both approvers and requesters. Transparency reduces follow-up questions.

## Advanced: Integrating with Teams

Want approvals to appear in Microsoft Teams instead of email?

Add a **Post adaptive card in a chat or channel** action (search "Teams") after your approval action. This sends a formatted card with buttons directly to your approvals Teams channel.

Approvers can approve or reject without leaving Teams, and the response flows back to your workflow automatically.

This is particularly useful for remote teams and keeps communication centralised.

## Further Reading and Recommended Tools

To deepen your Power Automate knowledge, consider these resources:

**"Automate It"** by Hannes Ergin and Keziah Bryceland is a practical guide to Power Automate workflows with real-world examples. [Available on Amazon UK](https://www.amazon.co.uk/s?k=power+automate+book&tag=automatework-21).

For hands-on training, **[Udemy's Power Automate courses](https://trk.udemy.com/DWnAjG)** offer structured learning paths with video demonstrations of approval workflows and common scenarios.

The official [Microsoft Power Automate documentation](https://learn.microsoft.com/en-us/power-automate/) is free and regularly updated with new features and best practices.

## Summary

An approval workflow in Power Automate doesn't require complex coding. With a trigger, an approval action, conditions, and follow-up actions, you can eliminate manual email approvals and create transparent, auditable processes.

Start with a simple workflow: one trigger, one approver, two outcome paths. Once you've tested and deployed it, expand to multiple approvers, conditional routing, and integrations with your other business tools.

The time you save compounds. A 30-minute saving per request across 20 weekly requests is over 10 hours monthly — time your team can spend on actual work instead of chasing approvals.

---

*This article contains affiliate links. If you purchase through them I may earn a small commission at no extra cost to you. See [disclosure](/POD-and-Affiliate/privacy/).*