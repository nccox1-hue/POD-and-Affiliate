```markdown
---
layout: post
title: "Power Automate Send Email When SharePoint List Updated: Complete Guide"
date: 2026-07-01
categories: [power-automate]
description: "Step-by-step instructions to set up Power Automate email notifications when a SharePoint list is updated. No code required."
---

*This article contains affiliate links. If you purchase through them I may earn a small commission at no extra cost to you. See [disclosure](/POD-and-Affiliate/privacy/).*

## Why automate email notifications for SharePoint list updates?

SharePoint lists are central to many business workflows. Whether you're tracking project tasks, managing approvals, or monitoring inventory, people need to know when something changes. Manual checking wastes time. Email notifications ensure the right people stay informed immediately.

Power Automate makes this straightforward. You don't need coding skills — the cloud-based automation platform handles the logic. Once configured, emails trigger automatically whenever your SharePoint list changes.

This guide covers everything: basic setup, filtering updates, adding conditional logic, and troubleshooting common issues.

## What you need before starting

- A Microsoft 365 account with access to Power Automate
- A SharePoint list you can modify
- An email address for testing
- Basic familiarity with SharePoint and Power Automate

You don't need Power Automate Premium for basic notifications, though some advanced features require it. Check the [Power Automate pricing page](https://powerautomate.microsoft.com/en-us/pricing/) to confirm your licence level.

## Step-by-step: Create a basic email notification flow

### Step 1: Start a new cloud flow

1. Log into [Power Automate](https://powerautomate.microsoft.com)
2. Select **Create** from the left menu
3. Choose **Cloud flow** → **Automated cloud flow**
4. Name your flow (e.g., "SharePoint List Update Notification")
5. Select **SharePoint - When an item is created or modified** as the trigger
6. Click **Create**

### Step 2: Configure the SharePoint trigger

1. In the trigger panel, fill in:
   - **Site Address**: Select your SharePoint site from the dropdown
   - **List Name**: Select your target list
2. Leave **Trigger settings** on default for now — this fires every time an item is created or modified

Power Automate will immediately check your SharePoint environment and pull available sites and lists. If your list doesn't appear, ensure you have permissions and try refreshing.

### Step 3: Add the send email action

1. Click **+ New step**
2. Search for "Send an email (V2)"
3. Select the action from the **Office 365 Outlook** connector
4. Sign in to your Outlook account if prompted

### Step 4: Configure the email

Fill in these fields:

- **To**: Enter your email address (or use dynamic content to email the item creator)
- **Subject**: Type something clear, e.g., "SharePoint List Updated: @{triggerOutputs()?['body/Title']}"
- **Body**: Add a message with dynamic content

For the body, use dynamic content to include details from the updated item:

1. Click in the **Body** field
2. Click the lightning bolt icon to open dynamic content
3. Select relevant fields like:
   - **Title** (the item name)
   - **Created** (when it was added)
   - **Modified by** (who changed it)
   - **[Your custom fields]** (any custom columns you've added)

Example body text:

```
A SharePoint list item has been updated.

Item: [Title]
Updated by: [Modified By]
Date: [Modified]

Log in to SharePoint to view details.
```

### Step 5: Save and test

1. Click **Save**
2. Return to your SharePoint list
3. Create a new item or edit an existing one
4. Within seconds, an email should arrive

If no email appears within 2 minutes, check your spam folder or review the flow run history for errors.

## Filtering: Only notify for specific changes

Sending an email for every single update quickly becomes noise. Use filtering to notify only when relevant changes happen.

### Filter by item status

If your list has a "Status" column:

1. Add a condition step after the SharePoint trigger:
   - Click **+ New step**
   - Search for and select **Condition**

2. Configure the condition:
   - **Choose a value** (left field): Click dynamic content, select **Status**
   - **is equal to**: Select from the dropdown
   - **Choose a value** (right field): Type "Completed" (or your target status)

3. In the **If yes** branch, add your Send Email action
4. Leave the **If no** branch empty (no email sent for other statuses)

### Filter by modified fields only

You might only want emails when specific columns change. This requires the **Condition** action with more complex logic:

1. Add a **Condition** step
2. Use the expression editor (click **Expression** tab):
   ```
   not(equals(triggerBody()?['properties/IsNew'], true))
   ```
   This filters out new items, only notifying on edits.

3. For more granular control, use the **Apply to each** action:
   - Add it after the trigger
   - In each email body, reference the changed field dynamically

## Advanced: Send different emails based on what changed

Use multiple condition branches to send different email content depending on which field was updated.

### Setup example: Notify managers only when Priority changes

1. Add a **Condition** after the trigger
2. Set up:
   - Left field: **Priority** (dynamic content)
   - Operator: **is not equal to**
   - Right field: (leave empty)

3. In the **If yes** branch:
   - Add a Send Email action
   - Set **To** to a manager's email address
   - Add a subject like "Priority Changed: @{triggerOutputs()?['body/Title']}"

4. In the **If no** branch:
   - Add a different Send Email action for regular users
   - Or leave it empty if you only want manager notifications

## Common issues and fixes

### Flow doesn't trigger

**Problem**: You've modified a list item but no email arrives.

**Solutions**:
- Check the flow's run history (click the flow, then **28-day run history**)
- Verify you selected the correct SharePoint site and list in the trigger
- Ensure you have Edit permissions on the list
- Test manually: click **Test** in Power Automate, then make a list change

### Wrong recipients receiving emails

**Problem**: Email goes to the wrong person or multiple unwanted recipients.

**Solution**:
- Review your **To** field in the Send Email action
- If using dynamic content, ensure you've selected the correct user field (e.g., **Created By** vs **Modified By**)
- Use conditions to filter recipients by role or department

### Email content is blank or shows "[object Object]"

**Problem**: Dynamic content displays incorrectly in the email body.

**Solution**:
- Use the dynamic content picker (lightning icon) instead of typing field names manually
- For complex fields (like person columns), use expressions:
  ```
  triggerBody()?['properties/ModifiedBy/displayName']
  ```

### Flow runs multiple times for a single update

**Problem**: You receive duplicate emails.

**Solution**:
- Check if the flow has multiple trigger events (remove duplicates)
- Review your list for workflows or other Power Automate flows that might modify items, causing cascading triggers
- Add a **Delay** action at the start to throttle rapid-fire updates

## Best practices for production use

**Test thoroughly before enabling for all users**: Run the flow with a test list and verify email timing, content, and recipients.

**Use appropriate frequency**: If your list updates constantly, consider daily digest emails instead of instant notifications. Add a Schedule action to batch emails.

**Keep email templates clean**: Use line breaks and clear formatting. Avoid cluttering the body with unnecessary fields.

**Archive old flows**: Over time you'll create test flows. Delete unused ones to avoid confusion.

**Document your logic**: Add notes or descriptions to condition branches explaining why certain recipients receive specific emails.

**Monitor flow runs**: Check the run history weekly for errors. Fix failures quickly to prevent missing notifications.

## Going further: Advanced automation scenarios

Once you've mastered basic notifications, consider:

- **Approval workflows**: Route emails to approvers with approval buttons included
- **Microsoft Teams notifications**: Send messages to Teams channels instead of email (faster for urgent updates)
- **Dynamic recipient lists**: Query a separate lookup list to determine who receives notifications based on department or role
- **Escalation**: Send urgent notifications to managers if items aren't updated within a timeframe

To learn more complex Power Automate patterns, consider the [Power Automate automation fundamentals course on Udemy](https://trk.udemy.com/DWnAjG), which covers advanced triggers, conditions, and expressions.

## Recommended tools

If you're building sophisticated SharePoint and automation workflows, these resources help:

- [**Microsoft Power Automate Cookbook on Amazon**](https://www.amazon.co.uk/s?k=power+automate+cookbook&tag=automatework-21) — practical recipes for real-world scenarios
- Power Automate documentation: [Microsoft Learn - Power Automate](https://learn.microsoft.com/en-us/power-automate/)
- SharePoint administration best practices: [Microsoft 365 documentation](https://learn.microsoft.com/en-us/sharepoint/)

## Summary

Email notifications for SharePoint list updates take minutes to set up and eliminate the need for manual checking. Start with the basic flow, test it with a small audience, then expand with conditions and advanced logic as needed.

The beauty of Power Automate is that it scales: the same flow template works for a 10-person team or a 10,000-person organisation.

Set it up today, and your team will be more responsive to list changes tomorrow.

---

**Affiliate disclosure**: This article contains affiliate links to Amazon and Udemy. If you purchase through them, I receive a small commission at no extra cost to you.
```