---
layout: post
title: "Build an Automated Email Approval Workflow in Power Automate (No Code)"
date: 2026-05-30
categories: power-automate
description: "Replace email chains and chasing with a proper approval workflow in Power Automate. Set it up once, runs automatically forever."
---

Most approval processes in offices still work like this: someone sends an email, waits, chases, sends a reminder, eventually gets a reply buried three threads deep. There's a better way.

Power Automate's approval connector turns any process — expenses, leave requests, purchase orders, content sign-off — into a structured workflow that runs automatically, tracks status, and sends reminders without anyone chasing.

This guide builds a complete approval workflow from scratch. No code required. Takes about 30 minutes to set up.

## What you'll build

- A form submission triggers an approval request
- The approver gets an email with Approve/Reject buttons
- The submitter gets notified automatically of the outcome
- All responses are logged to a SharePoint list or Excel file

## Prerequisites

- Microsoft 365 account (Power Automate is included)
- Access to Microsoft Forms (for the trigger)
- SharePoint site or OneDrive (for logging — optional but recommended)

## Step 1: Create the request form

Go to [forms.microsoft.com](https://forms.microsoft.com) and create a new form. For an expenses approval, add:

- Name (text)
- Department (choice)
- Amount (number)
- Description (text, long answer)
- Receipt attached? (choice: Yes/No)

Note the form URL — you'll need it.

## Step 2: Create the flow

1. Go to [make.powerautomate.com](https://make.powerautomate.com)
2. Click **Create → Automated cloud flow**
3. Name it "Expense Approval"
4. Search for trigger: **When a new response is submitted** (Microsoft Forms)
5. Select your form → **Create**

## Step 3: Get the form response details

Add a step: **Get response details** (Microsoft Forms)
- Form ID: your form
- Response ID: use the dynamic value `Response ID` from the trigger

This pulls the actual answers from the submitted form into the flow.

## Step 4: Start the approval

Add a step: **Start and wait for an approval** (Approvals)

Fill in:
- **Approval type:** Approve/Reject — First to respond
- **Title:** `Expense Request — [Name] — £[Amount]` (use dynamic values)
- **Assigned to:** the approver's email address
- **Details:** build a summary using the form response values
- **Item link:** optional — link back to the SharePoint record

Power Automate pauses here and waits for the approver to respond. The approver gets an email with Approve and Reject buttons — they can respond directly from email or from the Power Automate approvals centre.

## Step 5: Branch on the outcome

Add a **Condition** step:
- Value: `Outcome` (dynamic value from the approval)
- Condition: `is equal to`
- Value: `Approve`

**If yes (approved):**
Add a **Send an email** step notifying the submitter their request was approved.

**If no (rejected):**
Add a **Send an email** step notifying the submitter it was rejected, including the approver's comments.

## Step 6: Log the result

In both branches, add a step to log the outcome. The easiest option is **Add a row into a table** (Excel Online) pointing to a table in OneDrive — log the name, amount, outcome, approver comments, and timestamp.

## Step 7: Test it

Submit a test response through your form. Within seconds you should receive an approval email. Approve it, and check that the submitter notification and log entry both appear.

## Making it production-ready

A few additions that make this workflow solid:

**Reminders:** Add a **Post an adaptive card** step after the approval starts — this pings the approver in Teams if they haven't responded after 24 hours.

**Multiple approvers:** Change Approval type to "Everyone must approve" for sequential sign-off (e.g. manager then finance).

**Delegation:** Power Automate's approval centre allows approvers to delegate when they're on leave.

## What this replaces

One properly built approval flow eliminates:
- Email chains
- Manual chasing and reminders  
- Lost requests
- No audit trail

Once built it runs unattended, indefinitely.

## Going further

Microsoft's [Power Automate documentation](https://learn.microsoft.com/en-us/power-automate/) is free and comprehensive. For a structured course covering approvals, SharePoint integration and complex flows, the [Power Automate courses on Udemy](https://www.udemy.com/courses/search/?q=power+automate) regularly have solid options.

*This post contains affiliate links. See [disclosure](/POD-and-Affiliate/privacy/).*
