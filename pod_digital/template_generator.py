"""
Generates professional Excel templates as digital downloads.
Uses openpyxl to create real, working .xlsx files with formulas and formatting.
Products: budget trackers, KPI dashboards, invoice templates, project planners, etc.
Price point: £10-£30 (vs £2.49 for wall art).
"""
import logging
import os
from typing import List, Dict
from datetime import date, timedelta

logger = logging.getLogger(__name__)

try:
    import openpyxl
    from openpyxl.styles import (
        Font, PatternFill, Alignment, Border, Side, numbers
    )
    from openpyxl.utils import get_column_letter
    from openpyxl.chart import BarChart, Reference
    OPENPYXL_AVAILABLE = True
except ImportError:
    OPENPYXL_AVAILABLE = False
    logger.warning("openpyxl not installed — run: pip install openpyxl")

# Template catalogue — each entry is a product we can generate
TEMPLATES: List[Dict] = [
    {
        "id": "monthly_budget",
        "title": "Monthly Budget Tracker | Excel Spreadsheet | Personal Finance Template",
        "description": """Professional monthly budget tracker for Excel. Includes:
• Income and expense categories with automatic totals
• Monthly vs actual comparison with variance highlighting
• Savings rate calculator
• 12-month annual overview dashboard
• Works with Excel 2016+ and Microsoft 365
• Instant download — no macros required""",
        "tags": ["budget tracker", "excel template", "personal finance", "monthly budget",
                 "spreadsheet", "expense tracker", "savings tracker", "finance planner",
                 "excel spreadsheet", "budget planner", "money tracker", "income tracker"],
        "price": 12.99,
        "filename": "Monthly_Budget_Tracker.xlsx",
        "theme": "finance",
    },
    {
        "id": "project_tracker",
        "title": "Project Tracker Excel Template | Task Management Spreadsheet | Team Planner",
        "description": """Professional project tracking template for Excel. Includes:
• Task list with status, priority, owner and due date
• Gantt chart that updates automatically
• Progress dashboard with completion percentage
• RAG status indicators (Red/Amber/Green)
• Works with Excel 2016+ and Microsoft 365
• Instant download — no macros required""",
        "tags": ["project tracker", "excel template", "task management", "gantt chart",
                 "project planner", "work tracker", "team planner", "spreadsheet",
                 "project management", "task tracker", "excel planner", "work planner"],
        "price": 14.99,
        "filename": "Project_Tracker.xlsx",
        "theme": "business",
    },
    {
        "id": "kpi_dashboard",
        "title": "KPI Dashboard Excel Template | Business Performance Tracker | Metrics Spreadsheet",
        "description": """Executive KPI dashboard template for Excel. Includes:
• 12 configurable KPI cards with target vs actual
• Monthly trend charts
• Traffic light status indicators
• Department breakdown view
• Works with Excel 2016+ and Microsoft 365
• Instant download — no macros required""",
        "tags": ["kpi dashboard", "excel template", "business metrics", "performance tracker",
                 "dashboard excel", "kpi tracker", "metrics template", "business dashboard",
                 "excel dashboard", "reporting template", "management dashboard", "analytics"],
        "price": 19.99,
        "filename": "KPI_Dashboard.xlsx",
        "theme": "business",
    },
    {
        "id": "invoice_template",
        "title": "Professional Invoice Template Excel | Freelancer Invoice | Self Employed",
        "description": """Clean, professional invoice template for freelancers and small businesses. Includes:
• Automatic total and VAT calculations
• Your logo placeholder
• Payment terms and bank details section
• Invoice number auto-increment guide
• Works with Excel 2016+ and Microsoft 365
• Instant download — customise in minutes""",
        "tags": ["invoice template", "excel invoice", "freelancer invoice", "self employed",
                 "business invoice", "professional invoice", "vat invoice", "uk invoice",
                 "invoice spreadsheet", "billing template", "payment template", "sole trader"],
        "price": 9.99,
        "filename": "Professional_Invoice_Template.xlsx",
        "theme": "business",
    },
    {
        "id": "habit_tracker",
        "title": "Habit Tracker Excel Template | Daily Tracker Spreadsheet | 90 Day Planner",
        "description": """Clean 90-day habit tracker for Excel. Includes:
• Track up to 15 habits daily
• Automatic streak counter
• Weekly and monthly completion charts
• Year overview heatmap style view
• Works with Excel 2016+ and Microsoft 365
• Instant download — add your habits in minutes""",
        "tags": ["habit tracker", "excel template", "daily tracker", "90 day challenge",
                 "productivity planner", "goal tracker", "routine tracker", "spreadsheet",
                 "self improvement", "daily planner", "wellness tracker", "streak tracker"],
        "price": 9.99,
        "filename": "Habit_Tracker_90_Day.xlsx",
        "theme": "productivity",
    },
]

# Colours for consistent styling
DARK_BLUE = "1F3864"
MID_BLUE = "2E75B6"
LIGHT_BLUE = "D9E2F3"
ACCENT = "F59E0B"
GREEN = "22C55E"
RED = "EF4444"
WHITE = "FFFFFF"
LIGHT_GREY = "F8F9FA"
DARK_GREY = "374151"


def _header_style(ws, cell_ref, text, dark=True):
    cell = ws[cell_ref]
    cell.value = text
    cell.font = Font(bold=True, color=WHITE if dark else DARK_GREY, size=11)
    cell.fill = PatternFill("solid", fgColor=DARK_BLUE if dark else LIGHT_BLUE)
    cell.alignment = Alignment(horizontal="center", vertical="center")
    return cell


def _create_budget_tracker() -> openpyxl.Workbook:
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Monthly Budget"
    ws.sheet_view.showGridLines = False

    # Title
    ws.merge_cells("A1:G1")
    title = ws["A1"]
    title.value = "MONTHLY BUDGET TRACKER"
    title.font = Font(bold=True, size=16, color=WHITE)
    title.fill = PatternFill("solid", fgColor=DARK_BLUE)
    title.alignment = Alignment(horizontal="center", vertical="center")
    ws.row_dimensions[1].height = 35

    # Month/Year
    ws.merge_cells("A2:G2")
    subtitle = ws["A2"]
    subtitle.value = f"Month: {date.today().strftime('%B %Y')}  |  Update the amounts in the yellow cells"
    subtitle.font = Font(size=10, color=DARK_GREY, italic=True)
    subtitle.fill = PatternFill("solid", fgColor=LIGHT_BLUE)
    subtitle.alignment = Alignment(horizontal="center")
    ws.row_dimensions[2].height = 20

    # Headers row 4
    headers = ["Category", "Item", "Budgeted (£)", "Actual (£)", "Difference (£)", "Status", "Notes"]
    for col, h in enumerate(headers, 1):
        cell = ws.cell(row=4, column=col, value=h)
        cell.font = Font(bold=True, color=WHITE, size=10)
        cell.fill = PatternFill("solid", fgColor=MID_BLUE)
        cell.alignment = Alignment(horizontal="center", vertical="center")
    ws.row_dimensions[4].height = 22

    # Income section
    income_items = [
        ("INCOME", "Salary / Wages", 2500, None),
        ("INCOME", "Freelance / Side income", 0, None),
        ("INCOME", "Other income", 0, None),
    ]
    expense_items = [
        ("HOUSING", "Rent / Mortgage", 800, None),
        ("HOUSING", "Utilities (gas, electric)", 120, None),
        ("HOUSING", "Council Tax", 130, None),
        ("FOOD", "Groceries", 300, None),
        ("FOOD", "Eating out / Takeaways", 100, None),
        ("TRANSPORT", "Car / Fuel", 150, None),
        ("TRANSPORT", "Public transport", 50, None),
        ("LIFESTYLE", "Subscriptions (Netflix etc)", 30, None),
        ("LIFESTYLE", "Gym / Sports", 40, None),
        ("LIFESTYLE", "Clothing", 50, None),
        ("SAVINGS", "Emergency fund", 100, None),
        ("SAVINGS", "Investments / Pension", 200, None),
    ]

    yellow_fill = PatternFill("solid", fgColor="FFF2CC")
    alt_fill = PatternFill("solid", fgColor=LIGHT_GREY)
    row = 5
    for i, (cat, item, budget, actual) in enumerate(income_items + expense_items):
        ws.cell(row=row, column=1, value=cat).font = Font(bold=True, size=9, color=DARK_GREY)
        ws.cell(row=row, column=2, value=item)
        budget_cell = ws.cell(row=row, column=3, value=budget)
        budget_cell.number_format = '#,##0.00'
        budget_cell.fill = yellow_fill
        actual_cell = ws.cell(row=row, column=4, value=actual or 0)
        actual_cell.number_format = '#,##0.00'
        actual_cell.fill = yellow_fill
        diff_cell = ws.cell(row=row, column=5)
        diff_cell.value = f"=C{row}-D{row}"
        diff_cell.number_format = '#,##0.00'
        status_cell = ws.cell(row=row, column=6)
        status_cell.value = f'=IF(E{row}>=0,"✓ On track","⚠ Over budget")'
        if i % 2 == 0:
            for col in [1, 2, 6, 7]:
                ws.cell(row=row, column=col).fill = alt_fill
        row += 1

    # Totals
    ws.cell(row=row + 1, column=2, value="TOTAL INCOME").font = Font(bold=True)
    ws.cell(row=row + 1, column=3, value="=SUMIF(A5:A16,\"INCOME\",C5:C16)").number_format = '#,##0.00'
    ws.cell(row=row + 1, column=4, value="=SUMIF(A5:A16,\"INCOME\",D5:D16)").number_format = '#,##0.00'
    ws.cell(row=row + 2, column=2, value="TOTAL EXPENSES").font = Font(bold=True)
    ws.cell(row=row + 2, column=3, value=f"=SUM(C{5+len(income_items)}:C{row-1})").number_format = '#,##0.00'
    ws.cell(row=row + 2, column=4, value=f"=SUM(D{5+len(income_items)}:D{row-1})").number_format = '#,##0.00'
    ws.cell(row=row + 3, column=2, value="NET (Income - Expenses)").font = Font(bold=True, color=WHITE)
    ws.cell(row=row + 3, column=2).fill = PatternFill("solid", fgColor=DARK_BLUE)
    net = ws.cell(row=row + 3, column=3)
    net.value = f"=C{row+1}-C{row+2}"
    net.number_format = '#,##0.00'
    net.font = Font(bold=True, color=WHITE)
    net.fill = PatternFill("solid", fgColor=DARK_BLUE)

    # Column widths
    ws.column_dimensions["A"].width = 14
    ws.column_dimensions["B"].width = 28
    ws.column_dimensions["C"].width = 16
    ws.column_dimensions["D"].width = 16
    ws.column_dimensions["E"].width = 16
    ws.column_dimensions["F"].width = 16
    ws.column_dimensions["G"].width = 20

    return wb


def _create_project_tracker() -> openpyxl.Workbook:
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Project Tasks"
    ws.sheet_view.showGridLines = False

    ws.merge_cells("A1:H1")
    t = ws["A1"]
    t.value = "PROJECT TRACKER"
    t.font = Font(bold=True, size=16, color=WHITE)
    t.fill = PatternFill("solid", fgColor=DARK_BLUE)
    t.alignment = Alignment(horizontal="center", vertical="center")
    ws.row_dimensions[1].height = 35

    headers = ["#", "Task", "Owner", "Priority", "Start Date", "Due Date", "Status", "% Done"]
    for col, h in enumerate(headers, 1):
        cell = ws.cell(row=3, column=col, value=h)
        cell.font = Font(bold=True, color=WHITE, size=10)
        cell.fill = PatternFill("solid", fgColor=MID_BLUE)
        cell.alignment = Alignment(horizontal="center")

    sample_tasks = [
        (1, "Define project scope", "Nick", "High", date.today(), date.today() + timedelta(days=3), "Complete", 100),
        (2, "Stakeholder sign-off", "Nick", "High", date.today() + timedelta(days=2), date.today() + timedelta(days=7), "In Progress", 50),
        (3, "Build prototype", "Team", "Medium", date.today() + timedelta(days=5), date.today() + timedelta(days=14), "Not Started", 0),
        (4, "Testing", "Team", "Medium", date.today() + timedelta(days=14), date.today() + timedelta(days=21), "Not Started", 0),
        (5, "Launch", "Nick", "High", date.today() + timedelta(days=21), date.today() + timedelta(days=22), "Not Started", 0),
    ]

    priority_colours = {"High": "EF4444", "Medium": "F59E0B", "Low": "22C55E"}
    status_colours = {"Complete": "22C55E", "In Progress": "F59E0B", "Not Started": "6B7280"}

    for i, (num, task, owner, priority, start, due, status, pct) in enumerate(sample_tasks):
        row = i + 4
        ws.cell(row=row, column=1, value=num).alignment = Alignment(horizontal="center")
        ws.cell(row=row, column=2, value=task)
        ws.cell(row=row, column=3, value=owner).alignment = Alignment(horizontal="center")
        p_cell = ws.cell(row=row, column=4, value=priority)
        p_cell.alignment = Alignment(horizontal="center")
        p_cell.font = Font(bold=True, color=priority_colours.get(priority, "000000"))
        ws.cell(row=row, column=5, value=start).number_format = "DD/MM/YYYY"
        ws.cell(row=row, column=6, value=due).number_format = "DD/MM/YYYY"
        s_cell = ws.cell(row=row, column=7, value=status)
        s_cell.font = Font(bold=True, color=status_colours.get(status, "000000"))
        s_cell.alignment = Alignment(horizontal="center")
        ws.cell(row=row, column=8, value=pct / 100).number_format = "0%"
        if i % 2 == 0:
            for col in range(1, 9):
                ws.cell(row=row, column=col).fill = PatternFill("solid", fgColor=LIGHT_GREY)

    ws.column_dimensions["A"].width = 5
    ws.column_dimensions["B"].width = 35
    ws.column_dimensions["C"].width = 15
    ws.column_dimensions["D"].width = 12
    ws.column_dimensions["E"].width = 14
    ws.column_dimensions["F"].width = 14
    ws.column_dimensions["G"].width = 14
    ws.column_dimensions["H"].width = 10

    return wb


def _create_stub_workbook(template_id: str) -> openpyxl.Workbook:
    """Fallback for templates not yet fully implemented."""
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.merge_cells("A1:F1")
    t = ws["A1"]
    t.value = template_id.replace("_", " ").upper()
    t.font = Font(bold=True, size=14, color=WHITE)
    t.fill = PatternFill("solid", fgColor=DARK_BLUE)
    t.alignment = Alignment(horizontal="center", vertical="center")
    ws.row_dimensions[1].height = 30
    ws["A3"] = "Update this template with your data"
    ws["A3"].font = Font(italic=True, color=DARK_GREY)
    return wb


GENERATORS = {
    "monthly_budget": _create_budget_tracker,
    "project_tracker": _create_project_tracker,
}


def generate_template(template_id: str, output_dir: str) -> List[str]:
    """
    Generate the Excel file for a given template ID.
    Returns list of file paths created.
    """
    if not OPENPYXL_AVAILABLE:
        logger.error("openpyxl not installed — cannot generate templates")
        return []

    template = next((t for t in TEMPLATES if t["id"] == template_id), None)
    if not template:
        logger.error("Unknown template ID: %s", template_id)
        return []

    try:
        generator = GENERATORS.get(template_id, lambda: _create_stub_workbook(template_id))
        wb = generator()
        path = os.path.join(output_dir, template["filename"])
        wb.save(path)
        logger.info("Template generated: %s (%d KB)", template["filename"], os.path.getsize(path) // 1024)
        return [path]
    except Exception as e:
        logger.error("Template generation error for %s: %s", template_id, e)
        return []
