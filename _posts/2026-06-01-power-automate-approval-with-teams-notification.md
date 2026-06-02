```markdown
---
layout: post
title: "Power Automate Approval with Teams Notification: Complete Setup Guide"
date: 2026-06-01
categories: [power-automate]
description: "Set up approval workflows in Power Automate with Teams notifications. Step-by-step guide for automating business approvals."
---

## Power Automate Approval with Teams Notification: Complete Setup Guide

Approval workflows are one of the most practical uses for Power Automate. Rather than chasing people via email or Slack, you can send approvals directly into Teams where your team already works. This guide shows you exactly how to build one.

## Why Use Power Automate Approvals with Teams?

Before diving into the build, let's be clear about what this solves:

- **Approvers see notifications instantly** in Teams, not buried in email
- **You track approval status** automatically without manual follow-ups
- **Rejections trigger different workflows** — like sending the request back to the originator
- **Approval history is logged** for compliance and audit purposes

This matters because approval requests sent only via email often get missed or forgotten.

## What You'll Need

- A Microsoft 365 account with Power Automate access
- A Teams channel (or the ability to send direct messages to users)
- A trigger for your workflow — this could be a form submission, SharePoint list entry, or email
- An approval action in Power Automate

## Step 1: Create Your Trigger

Start by deciding what initiates an approval request. The most common options are:

**Option A: When a SharePoint list item is created**

This works well for formal request lists. Create a SharePoint list with columns for:
- Title
- Requested by (Person column)
- Amount (if financial)
- Reason/Description
- Status (set to "Pending Approval" initially)

**Option B: When a form is submitted**

Use Microsoft Forms or Power Apps form submission as your trigger. Forms give you better control over what data gets captured.

**Option C: When an email arrives**

Use the "When a new email arrives" trigger filtered to a specific mailbox or subject line.

For this guide, we'll use a SharePoint list as the trigger. Here's how to set it up:

1. Go to **Power Automate** and select **Create** > **Automated cloud flow**
2. Name your flow (e.g., "Approval Request to Teams")
3. Choose "When an item is created" as your trigger
4. Select your SharePoint site and list

Once connected, Power Automate shows you all the columns from your list. You'll reference these values later in the approval message.

## Step 2: Add the Approval Action

With your trigger selected, click **New step** and search for "Start and wait for an approval".

Power Automate offers several approval types:

- **Approve/Reject** — Single decision
- **Approve/Reject/Reassign** — Decision with reassignment option
- **Custom Responses** — Multiple specific options

For most workflows, "Approve/Reject" is sufficient. Here's what to fill in:

### Approval type
Select "Approve/Reject – Everyone must approve" if multiple people must approve, or "First to respond" if you want the first decision to end it.

### Title
This appears at the top of the approval. Make it clear and brief:

`New Expense Report from [Requested by] — £[Amount]`

Use dynamic content (the lightning icon) to pull values from your trigger.

### Assigned to
Click this field and select the approver. This can be:
- A specific user
- A dynamic field from your SharePoint list (e.g., a "Manager" column)
- A group email (the first person to respond decides)

### Details
Write the approval body. Include relevant information:

```
Request Type: Expense Report
Submitted by: [Requested by]
Amount: £[Amount]
Reason: [Reason]
Date Submitted: [Created]

Please review and approve or reject this request.
```

Again, use dynamic content to pull actual values from your list.

### Item link
Set this to the SharePoint list item so approvers can view the full details. Click the chain icon and select "Link to item".

## Step 3: Send the Teams Notification

This is where Power Automate becomes genuinely useful. The approval action alone sends an email notification — but Teams notifications are far more visible.

Add a new step and search for "Post a message in a chat or channel".

### Connection
Select your Teams connection (or create one if this is your first time).

### Post in
Choose either:
- **Channel** — Posts in a shared channel (recommended for team approvals)
- **Group chat** — Posts in a group DM
- **User** — Direct message to the approver

For most workflows, posting in a channel keeps everything transparent.

### Team
Select your team.

### Channel
Select the channel where approvals should post.

### Message
Here's where you build the notification. Use this structure:

```
**New Approval Required**

**Submitted by:** [Requested by]
**Type:** Expense Report
**Amount:** £[Amount]
**Reason:** [Reason]

[View full request](link to SharePoint item)

**Approval Status:** Pending
```

You can format Teams messages using markdown. Use `**text**` for bold, `_text_` for italic.

**Important:** The Teams message is separate from the approval action. The approval itself goes to the approver's notification centre, but the Teams message keeps the team informed. Both are useful.

## Step 4: Handle the Approval Response

After the approval action, add a condition to handle the outcome. Click **New step** and add a **Condition**.

In the first field, select the **Outcome** from the approval action.

Set it to:
- **is equal to** → **Approved**

Under the "True" branch (approval granted):
- Update your SharePoint list status to "Approved"
- Send a confirmation message to the requester
- Post a message in Teams confirming approval
- Trigger any downstream processes (email notifications, updates to other systems)

Under the "False" branch (approval rejected):
- Update status to "Rejected"
- Send a rejection email with reason
- Optionally, restart the request or route it elsewhere

Here's how to update the SharePoint list:

1. In the True branch, add **Update item** action
2. Select your SharePoint site and list
3. Set the **ID** to the item ID from your trigger
4. Change **Status** to "Approved"
5. Add any other fields you want to update (date approved, approver name, etc.)

To get the approver's name from the approval action, use dynamic content to reference the **Approval outcome** field — it typically returns just "Approved" or "Rejected", but you can also capture who approved it using the Response Details.

## Step 5: Send Confirmation Messages

After updating the list, send confirmation messages to keep people informed.

**For the requester:**

Add a "Send an email" action:
- **To:** [Requested by email — pull from your list]
- **Subject:** `Your approval request has been [Approval response]`
- **Body:** Include the approval outcome and any next steps

**For the team (post in Teams):**

Add another Teams message:

```
✅ **Approval Granted**

**Submitted by:** [Requested by]
**Amount:** £[Amount]
**Approved by:** [Approver name]
**Date:** [Current time]
```

Use an emoji at the start to make it visually distinct from pending approvals.

## Step 6: Test and Deploy

Before rolling this out, test the entire flow:

1. Create a test item in your SharePoint list
2. Watch the approval appear in the approver's inbox and Teams
3. Click Approve in the notification
4. Verify the status updates and confirmation messages arrive
5. Check that the SharePoint list item shows the new status

Common issues to watch for:

- **Approver not receiving notification** — Check that the "Assigned to" field contains a valid email or user
- **Teams message not posting** — Verify the channel exists and your bot has permissions
- **Dynamic content showing "[Object]"** — You've selected the wrong field; use the lightning icon to pick the correct value
- **Approval timing out** — The default is 30 days; adjust this in the approval action settings if needed

## Advanced: Reassignment and Escalation

If your approval chain is more complex, add a reassignment step.

Use "Approve/Reject/Reassign" approval type instead of the basic one. This adds a **Reassign to** option in the approval notification.

After the approval action, add a condition checking for the "reassigned" outcome, then:

1. Send a message to the new approver
2. Store the reassignment history in your list
3. Start another approval cycle with the new person

This keeps approvals moving without requiring manual intervention.

## Practical Example: Expense Report Workflow

Here's how this looks end-to-end for an expense report:

1. **Employee submits form** → Creates SharePoint list item with amount, vendor, and receipt link
2. **Manager gets approval notification** → Both in Teams and email
3. **Manager approves** → Status updates to "Approved", email sent to employee
4. **Finance team notified in Teams** → They see the approved expense and process payment

This entire chain runs automatically. No chasing, no forgotten approvals, no emails buried in inboxes.

## Tips for Production Use

**Keep approvals simple.** If you need 5 levels of approval, Power Automate can do it, but consider whether the complexity is justified. Most workflows work better with 1-2 decision points.

**Use approval comments.** Enable the "Show comments" option in your approval action so approvers can leave notes explaining rejections.

**Set expiration dates.** If an approval isn't decided within 7 days, automatically escalate or reject it. Use a delay action followed by a condition.

**Archive approval records.** Store approval outcomes in a separate list or export to Excel monthly for audit purposes.

**Test with real users.** Have one manager use the flow for a week before rolling it out company-wide. Real usage reveals edge cases.

## Recommended Tools

To deepen your Power Automate skills, consider these resources:

- [Power Automate Desktop: Learn RPA & Automation](https://trk.udemy.com/DWnAjG) — A comprehensive Udemy course covering flow design patterns and best practices.
- [Microsoft Power Automate Cookbook on Amazon UK](https://www.amazon.co.uk/Microsoft-Power-Automate-Cookbook-workflows/dp/B0CZQM1MQM?tag=automatework-21) — Real-world recipes for approval workflows and beyond.

## Further Reading

- [Power Automate approval action reference](https://learn.microsoft.com/en-us/power-automate/approval-workflows) — Official Microsoft documentation
- [Teams notifications and formatting](https://learn.microsoft.com/en-us/power-automate/approvals-markdown-support) — How to format richer Teams messages

---

*This article contains affiliate links. If you purchase through them I may earn a small commission at no extra cost to you. See [disclosure](/POD-and-Affiliate/privacy/).*
```