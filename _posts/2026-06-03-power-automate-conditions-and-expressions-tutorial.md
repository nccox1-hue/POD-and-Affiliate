---
layout: post
title: "Power Automate Conditions and Expressions Tutorial: Build Smart Workflows"
date: 2026-06-03
categories: [power-automate, automation]
description: "Master Power Automate conditions and expressions. Learn to build intelligent workflows with if/else logic, multiple conditions, and dynamic expressions."
---

*This article contains affiliate links. If you purchase through them I may earn a small commission at no extra cost to you. See [disclosure](/POD-and-Affiliate/privacy/).*

Conditions and expressions are the decision-making backbone of Power Automate. Without them, your workflows are just linear sequences of actions. With them, you can build intelligent automation that responds to different scenarios, validates data, and handles edge cases.

This tutorial walks you through everything you need to know: from simple if/else blocks to complex expressions that transform data and control flow. You'll see practical examples you can adapt immediately.

## What Are Conditions in Power Automate?

A condition is a control structure that runs different actions based on whether something is true or false. In Power Automate, you add a condition using the **Condition** control, which creates an if/then/else branch in your workflow.

The basic structure is:
- **If** (the condition evaluates to true)
- **Then** (run these actions)
- **Else** (run these actions instead)

You can nest conditions, add multiple criteria, and use expressions to create sophisticated logic.

## Adding a Basic Condition

Here's how to insert a condition into your workflow:

1. Open Power Automate and create a new cloud flow (automated, instant, or scheduled).
2. Add your trigger (for example, "When a file is created in SharePoint").
3. Click **+ New step**.
4. Search for and select **Condition** from the Control actions.
5. In the condition card, you'll see three fields:
   - **Choose a value** (left field)
   - An operator dropdown (middle)
   - **Choose a value** (right field)

6. Click the left field and select a dynamic value from your trigger or previous actions.
7. Select an operator: equals, not equals, is greater than, contains, etc.
8. Enter or select a value for comparison.
9. Add actions in the **If yes** section.
10. Optionally add actions in the **If no** section.

**Example:** You've triggered a flow when an email arrives. You want to check if the subject contains "urgent".

1. In the left field, select **Subject** from the email trigger.
2. Set the operator to **contains**.
3. In the right field, type `urgent`.
4. In **If yes**, add an action to flag the email or create a task.
5. In **If no**, optionally add a different action.

## Operators Explained

Power Automate provides these comparison operators:

| Operator | Use Case |
|----------|----------|
| **is equal to** | Exact match (case-insensitive for text) |
| **is not equal to** | Does not match exactly |
| **is greater than** | Numeric comparison |
| **is less than** | Numeric comparison |
| **is greater than or equal to** | Numeric comparison |
| **is less than or equal to** | Numeric comparison |
| **contains** | Substring match (case-insensitive) |
| **does not contain** | Absence of substring |
| **starts with** | Text begins with value |
| **ends with** | Text ends with value |
| **is empty** | Field has no value |
| **is not empty** | Field has a value |

## Multiple Conditions (AND/OR Logic)

Often you need to check more than one thing. Power Automate lets you combine conditions using AND or OR logic.

### Using AND Logic

AND means all conditions must be true.

**Steps:**
1. Create your first condition as described above.
2. At the bottom of the condition card, click **Edit in advanced mode** (if you want to write expressions) or use the simple interface.
3. To add another row in the simple interface, click **Add** → **Add row**.
4. Set the logical operator to **AND** (appears on the left).
5. Complete the second condition.

**Example:** Run an action only if the email is from your manager AND the subject contains "approval".

```
From = manager@company.com
AND
Subject contains "approval"
```

### Using OR Logic

OR means at least one condition must be true.

**Steps:**
1. Add your first condition.
2. Click **Add** → **Add row** below the first condition.
3. Set the operator to **OR**.
4. Complete the second condition.

**Example:** Send a notification if the status is "Completed" OR "Approved".

```
Status = Completed
OR
Status = Approved
```

### Mixing AND and OR

You can combine these, but Power Automate evaluates AND conditions first (standard logical precedence). For more complex scenarios, use expressions instead.

## Working with Expressions

Expressions are powerful formulas that let you manipulate data, check conditions, and transform values. They're essential for advanced workflows.

### Accessing the Expression Editor

In any field that accepts dynamic content—including condition fields—click the **Expression** tab to write custom logic.

### Common Expression Functions

**String Functions:**
- `concat(string1, string2)` — Combine strings
- `length(string)` — Count characters
- `toLower(string)` / `toUpper(string)` — Change case
- `substring(string, startIndex, length)` — Extract part of string
- `contains(string, substring)` — Check if substring exists
- `split(string, delimiter)` — Break string into array

**Numeric Functions:**
- `add(number1, number2)` — Addition
- `sub(number1, number2)` — Subtraction
- `mul(number1, number2)` — Multiplication
- `div(number1, number2)` — Division
- `mod(number1, number2)` — Remainder

**Logical Functions:**
- `if(condition, trueValue, falseValue)` — Conditional evaluation
- `and(condition1, condition2)` — Logical AND
- `or(condition1, condition2)` — Logical OR
- `not(condition)` — Logical NOT

**Date Functions:**
- `addDays(timestamp, days)` — Add days to a date
- `addHours(timestamp, hours)` — Add hours
- `utcNow()` — Current UTC time
- `convertTimeZone(timestamp, sourceTimeZone, targetTimeZone)` — Convert between zones

### Example: Using Expressions in a Condition

Suppose you want to check if a number field is between 100 and 500.

1. Create a condition.
2. Click the left field.
3. Click the **Expression** tab.
4. Type: `and(greater(field_value, 100), less(field_value, 500))`
   (Replace `field_value` with your actual dynamic value)
5. Click **OK**.
6. Leave the operator as **is equal to** and the right field as **true**.

This works because the expression returns true or false, and you're checking if it equals true.

### Building Complex String Expressions

Let's say you need to create a formatted message combining data from multiple fields.

**Example:** You want to send "Invoice #12345 for Customer: John Smith (Amount: £1,500)"

Use the `concat()` function in an action field:

```
concat('Invoice #', triggerBody()?['InvoiceID'], ' for Customer: ', triggerBody()?['CustomerName'], ' (Amount: £', triggerBody()?['Amount'], ')')
```

Alternatively, use string interpolation with `@{...}`:

```
Invoice #@{triggerBody()?['InvoiceID']} for Customer: @{triggerBody()?['CustomerName']} (Amount: £@{triggerBody()?['Amount']})
```

## Conditional Action: The "If" Expression

Instead of using a Condition control, you can use the `if()` function directly in an action field. This is useful when you need a simple true/false outcome without building a full condition block.

**Syntax:**
```
if(condition, valueIfTrue, valueIfFalse)
```

**Example:** In an email action, set the body to:
```
if(equals(triggerBody()?['Status'], 'Urgent'), 'This is a high-priority item', 'This is a standard item')
```

## Switch Controls for Multiple Outcomes

When you have more than two paths (not just if/else), use a **Switch** control instead of nested conditions.

**Steps:**
1. Click **+ New step**.
2. Search for and select **Switch** from Control actions.
3. In the **On** field, select a dynamic value (often a status field with multiple possible values).
4. Add **Cases** for each possible value.
5. Add a **Default** case for any value not explicitly matched.

**Example:** Route approvals based on department.

1. Set **On** to the Department field.
2. Add Case: "Sales" → send to sales manager.
3. Add Case: "HR" → send to HR manager.
4. Add Case: "IT" → send to IT manager.
5. Add Default: send to general approval queue.

## Common Mistakes to Avoid

**1. Forgetting Case Sensitivity**
Many comparison operators are case-insensitive (`equals`, `contains`), but not all. For strict case-sensitive matching, use expressions: `equals(string, 'Value')` is case-insensitive, but you can use `comparison()` functions if needed.

**2. Mixing Data Types**
Ensure you're comparing apples to apples. If comparing a number to text, convert first: `int(variableName)` or `string(variableName)`.

**3. Null or Empty Checks**
Always check for empty values before using them in expressions. Use `empty(field)` or compare to null.

**4. Nested Conditions Without Limits**
Deep nesting becomes unreadable. Use Switch controls or split into separate flows instead.

**5. Not Testing Edge Cases**
Test your conditions with missing data, unexpected formats, and boundary values.

## Practical Example: A Complete Workflow

Here's a real-world scenario: approval workflow for expense reports.

**Trigger:** When an expense report is submitted in SharePoint.

**Actions:**

1. **Condition 1:** Is the amount > £500?
   - **If yes:** Send to manager for approval.
   - **If no:** Go to Condition 2.

2. **Condition 2:** Is the amount > £2,000?
   - **If yes:** Send to director for approval.
   - **If no:** Auto-approve and create receipt.

3. **Send approval email** (in yes/no branches):
   - Use `concat()` to build the email body with expense details.

4. **Update SharePoint item** with status: "Pending Approval" or "Approved".

## Debugging Conditions and Expressions

When conditions don't behave as expected:

1. **Test run the flow** manually and review the run history.
2. **Inspect dynamic values** — click the input fields to see what data is actually being used.
3. **Use intermediate steps** — add a "Compose" action to check expression output before using it.
4. **Check data types** — a number stored as text won't compare correctly to a numeric value.
5. **Use Power Automate's expression validator** — it flags syntax errors immediately.

## Learning Resources

To deepen your understanding of conditions and expressions, consider these resources:

- [Udemy Power Automate advanced course](https://trk.udemy.com/DWnAjG) covers complex expressions and workflow design in depth.
- *Microsoft Power Automate Cookbook* (available on [Amazon UK](https://www.amazon.co.uk/s?k=Microsoft+Power+Automate+Cookbook&tag=automatework-21)) includes worked examples of conditions in real business scenarios.

## Further Reading

- Microsoft's official [expression reference guide](https://learn.microsoft.com/en-us/azure/logic-apps/workflow-definition-language-functions-reference)
- Power Automate documentation on [control actions](https://learn.microsoft.com/en-us/power-automate/flows/use-conditions)
- Community examples at the [Power Automate community forum](https://powerusers.microsoft.com/t5/Power-Automate/ct/Power-Automate)

## Summary

Conditions and expressions transform Power Automate from a linear automation tool into an intelligent decision engine. Start with simple if/else conditions, master the basic operators, and graduate to expressions when you need more control. Always test your logic with real data, and don't hesitate to use Switch controls or split workflows when conditions get too complex.

The more you use these tools, the faster you'll build robust workflows that handle real-world complexity.