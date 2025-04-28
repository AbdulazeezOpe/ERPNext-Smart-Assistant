import re

def parse_doctype_prompt(prompt):
    # Extract Doctype name
    doctype_match = re.search(r"(?:called|named)\s+(.+?)\s+(?:with\s+fields|having\s+fields)", prompt, re.IGNORECASE)
    if doctype_match:
        doctype_name = doctype_match.group(1).strip()
    else:
        doctype_name = "UnnamedDoctype"

    # Extract fields
    fields_section = re.search(r"fields[:\s]+(.+)", prompt, re.IGNORECASE)
    fields = []
    if fields_section:
        raw_fields = fields_section.group(1).split(",")
        for field in raw_fields:
            match = re.match(r"(.+?)\s*\((.+?)\)", field.strip())
            if match:
                label = match.group(1).strip()
                fieldtype = match.group(2).strip()
                # Convert field label to fieldname (lowercase and underscores)
                fieldname = label.lower().replace(" ", "_")
                fields.append({
                    "label": label,
                    "fieldname": fieldname,
                    "fieldtype": fieldtype
                })

    return doctype_name, fields




def parse_workflow_prompt(prompt: str):
    """
    Parses a workflow creation instruction into Doctype, States, and Transitions.
    Example prompt:
    "Set up an approval workflow for PRFs where HOD submits and Director approves."
    """

    # Guess Doctype from sentence
    doctype_match = re.search(r"for\s+(.*?)\s+where", prompt, re.IGNORECASE)
    document_type = doctype_match.group(1).rstrip('s') if doctype_match else "Document"

    # Extract roles involved
    roles = re.findall(r"\b(\w+)\s+(?:submits|approves?)", prompt, re.IGNORECASE)

    if not roles or len(roles) < 2:
        # fallback if not properly matched
        roles = ["HOD", "Director"]

    states = []
    transitions = []

    # Build states
    for i, role in enumerate(roles):
        state = {
            "state": f"Pending {role} Approval" if i < len(roles) - 1 else "Approved",
            "doc_status": 0 if i < len(roles) - 1 else 1,
            "allow_edit": role,
            "update_field": "workflow_state",
            "update_value": f"Pending {roles[i+1]} Approval" if i < len(roles) - 1 else "Approved"
        }
        states.append(state)

    # Build transitions
    for i, role in enumerate(roles[:-1]):
        transition = {
            "state": f"Pending {role} Approval",
            "action": f"Submit to {roles[i+1]}",
            "next_state": f"Pending {roles[i+1]} Approval" if i+1 < len(roles) - 1 else "Approved",
            "allowed_role": role
        }
        transitions.append(transition)

    workflow_name = f"{document_type} Approval Workflow"

    return workflow_name, document_type, states, transitions




def parse_role_permission_prompt(prompt: str):
    """
    Parses a role creation instruction into role name, allowed doctypes, and restricted doctypes.
    Example prompt:
    "Create a Finance role that only allows access to Claims but not Projects."
    """

    role_match = re.search(r"create\s+a\s+(.*?)\s+role", prompt, re.IGNORECASE)
    role_name = role_match.group(1).strip().title() if role_match else "New Role"

    # Find Doctypes they can access
    allowed = re.findall(r"allows?\s+access\s+to\s+(.*?)($|,|but)", prompt, re.IGNORECASE)
    allowed_doctypes = []
    if allowed:
        # Split by "and" or "," if multiple
        allowed_text = allowed[0][0]
        allowed_doctypes = [doctype.strip().rstrip('s') for doctype in re.split(r",|and", allowed_text)]

    # Find Doctypes they should not access
    restricted = re.findall(r"not\s+access\s+(.*?)($|,|and)", prompt, re.IGNORECASE)
    restricted_doctypes = []
    if restricted:
        restricted_text = restricted[0][0]
        restricted_doctypes = [doctype.strip().rstrip('s') for doctype in re.split(r",|and", restricted_text)]

    return role_name, allowed_doctypes, restricted_doctypes



def parse_notification_prompt(prompt: str):
    """
    Parses a notification setup instruction.
    Example prompt:
    "Notify me by email when a claim is fully approved."
    """

    # Try to find document type (claim, PRF, etc.)
    doc_match = re.search(r"when a\s+(.*?)\s+is", prompt, re.IGNORECASE)
    document_type = doc_match.group(1).strip().rstrip('s').title() if doc_match else "Document"

    # Try to find status or condition
    status_match = re.search(r"is\s+(approved|rejected|submitted|completed|pending)", prompt, re.IGNORECASE)
    status_value = status_match.group(1).strip().capitalize() if status_match else "Approved"

    subject = f"{document_type} {status_value}"
    message = f"Your {document_type} has been {status_value.lower()}."
    condition = f"doc.status == '{status_value}'"

    return subject, document_type, condition, message


def parse_reminder_prompt(prompt: str):
    """
    Parse reminder prompts like:
    "Send weekly reminders for all pending PRFs."
    """
    prompt = prompt.lower()
    cron = ""
    document_type = ""
    condition = ""
    message = ""

    # Simple mapping based on common patterns
    if "weekly" in prompt:
        cron = "0 9 * * MON"  # every Monday at 9am
    elif "monthly" in prompt:
        cron = "0 9 1 * *"    # 1st of every month 9am
    elif "daily" in prompt:
        cron = "0 9 * * *"    # every day at 9am
    else:
        cron = "0 9 * * MON"  # fallback to weekly

    if "prf" in prompt:
        document_type = "PRF"  # assuming PRF is a DocType
        condition = "docstatus == 0"  # pending = draft
        message = "Reminder: You have pending PRF(s) awaiting approval."
    
    elif "claim" in prompt:
        document_type = "Claim"
        condition = "docstatus == 0"
        message = "Reminder: You have pending claims to review."

    else:
        document_type = "PRF"  # fallback
        condition = "docstatus == 0"
        message = "Reminder: You have pending documents."

    return document_type, condition, message, cron



def parse_department_prompt(prompt: str):
    """
    Parses a prompt to extract the department name.
    Example: "Create a new department called Signage."
    """
    dept_match = re.search(r"department\s+(named|called)?\s*(\w+)", prompt, re.IGNORECASE)

    if dept_match:
        department_name = dept_match.group(2).strip().title()
    else:
        department_name = "New Department"

    return department_name



def parse_user_assignment_prompt(prompt: str):
    """
    Parses a user assignment prompt.
    Example: "Add a user named Ali to Interior Design as HOD."
    """

    name_match = re.search(r"(?:named|called)?\s*(\w+)", prompt, re.IGNORECASE)
    department_match = re.search(r"to\s+(.*?)\s+as", prompt, re.IGNORECASE)
    role_match = re.search(r"as\s+(.*)", prompt, re.IGNORECASE)

    user_name = name_match.group(1).strip().title() if name_match else "New User"
    department_name = department_match.group(1).strip().title() if department_match else ""
    role_name = role_match.group(1).strip().title() if role_match else "Employee"

    return user_name, department_name, role_name




def parse_financial_prompt(prompt: str):
    """
    Parses prompts related to Management Fee and Profit Sharing.
    """
    prompt = prompt.lower()

    action = None
    department = None
    role = None
    amount = None

    # Detect Management Fee
    if "management fee" in prompt:
        action = "management_fee"
        dept_match = re.search(r"for\s+(.*?)\s+department", prompt)
        amount_match = re.search(r"rm\s?([\d,\.]+)", prompt)
        if dept_match:
            department = dept_match.group(1).strip().title()
        if amount_match:
            amount = float(amount_match.group(1).replace(",", ""))
    
    # Detect Profit Sharing
    elif "profit sharing" in prompt or "profit rule" in prompt:
        action = "profit_sharing"
        dept_match = re.search(r"for\s+(.*?)\s+department", prompt)
        role_match = re.search(r"to\s+(.*?)\s+after", prompt)
        percent_match = re.search(r"(\d+)%", prompt)

        if dept_match:
            department = dept_match.group(1).strip().title()
        if role_match:
            role = role_match.group(1).strip().title()
        if percent_match:
            amount = float(percent_match.group(1))
    
    return action, department, role, amount



def parse_prf_prompt(prompt: str):
    """
    Parses PRF creation prompt.
    """
    prompt = prompt.lower()

    project_name = None
    item_name = None
    quantity = None

    # Find Project Name
    project_match = re.search(r"project\s+(\w+)", prompt)
    if project_match:
        project_name = project_match.group(1)

    # Find Item Name
    item_match = re.search(r"item[:\s]+([\w\s]+?)(,|quantity|$)", prompt)
    if item_match:
        item_name = item_match.group(1).strip()

    # Find Quantity
    quantity_match = re.search(r"quantity[:\s]+([\d\.]+)", prompt)
    if quantity_match:
        quantity = float(quantity_match.group(1))

    return project_name, item_name, quantity


def parse_claim_prompt(prompt: str):
    """
    Parses claim creation or query prompt.
    """
    prompt = prompt.lower()

    project_name = None
    claim_name = None
    amount = None

    # Find Project Name
    project_match = re.search(r"project\s+(\w+)", prompt)
    if project_match:
        project_name = project_match.group(1)

    # Find Claim Name
    claim_match = re.search(r"claim\s+(\w+)", prompt)
    if claim_match:
        claim_name = claim_match.group(1)

    # Find Amount
    amount_match = re.search(r"rm\s?([\d,\.]+)", prompt)
    if amount_match:
        amount = float(amount_match.group(1).replace(",", ""))

    return project_name, claim_name, amount



def parse_project_prompt(prompt: str):
    """
    Parses project creation and role assignment prompts.
    """
    prompt = prompt.lower()

    project_name = None
    start_date = None
    budget_amount = None
    assignments = []  # List of (user, role) pairs

    # Find Project Name
    project_match = re.search(r"project\s+([\w\s]+)", prompt)
    if project_match:
        project_name = project_match.group(1).strip()

    # Find Start Date
    date_match = re.search(r"start[:\s]+([\w\s\d]+)", prompt)
    if date_match:
        start_date = date_match.group(1).strip()

    # Find Budget
    budget_match = re.search(r"budget[:\s]*rm\s?([\d,\.]+)", prompt)
    if budget_match:
        budget_amount = float(budget_match.group(1).replace(",", ""))

    # Find Role Assignments
    if "assign" in prompt and "to" in prompt:
        assign_matches = re.findall(r"assign\s+([\w\s]+?)\s+to\s+([\w\s]+)", prompt)
        for user, role in assign_matches:
            assignments.append((user.strip().title(), role.strip().title()))

    return project_name, start_date, budget_amount, assignments



def parse_hr_prompt(prompt: str):
    """
    Parses HR related prompts like contract creation, salary advance, leave tracking.
    """
    prompt = prompt.lower()

    employee_name = None
    monthly_salary = None
    start_date = None

    # Find Employee Name
    employee_match = re.search(r"for\s+([\w\s]+)", prompt)
    if employee_match:
        employee_name = employee_match.group(1).strip().title()

    # Find Monthly Salary
    salary_match = re.search(r"rm\s?([\d,\.]+)", prompt)
    if salary_match:
        monthly_salary = float(salary_match.group(1).replace(",", ""))

    # Find Start Date
    start_date_match = re.search(r"start[:\s]+([\w\s\d]+)", prompt)
    if start_date_match:
        start_date = start_date_match.group(1).strip()

    return employee_name, monthly_salary, start_date


def parse_vehicle_prompt(prompt: str):
    """
    Parses vehicle/asset-related prompts like addition, maintenance scheduling.
    """
    prompt = prompt.lower()

    vehicle_name = None
    department_name = None
    maintenance_interval_months = None

    # Find Vehicle Name
    vehicle_match = re.search(r"vehicle\s+([\w\s]+)", prompt)
    if vehicle_match:
        vehicle_name = vehicle_match.group(1).strip().title()

    # Find Department
    dept_match = re.search(r"to\s+([\w\s]+)", prompt)
    if dept_match:
        department_name = dept_match.group(1).strip().title()

    # Find Maintenance Frequency
    maintenance_match = re.search(r"every\s+(\d+)\s+month", prompt)
    if maintenance_match:
        maintenance_interval_months = int(maintenance_match.group(1))

    return vehicle_name, department_name, maintenance_interval_months

def parse_inventory_prompt(prompt: str):
    """
    Parses inventory-related prompts like item addition, supplier creation.
    """
    prompt = prompt.lower()

    item_name = None
    quantity = None
    department_name = None
    supplier_name = None
    contact_number = None

    # Find Item Name
    item_match = re.search(r"item\s+([\w\s]+)", prompt)
    if item_match:
        item_name = item_match.group(1).strip().title()

    # Find Quantity
    quantity_match = re.search(r"quantity[:\s]+(\d+)", prompt)
    if quantity_match:
        quantity = int(quantity_match.group(1))

    # Find Department
    dept_match = re.search(r"department[:\s]+([\w\s]+)", prompt)
    if dept_match:
        department_name = dept_match.group(1).strip().title()

    # Find Supplier Name
    supplier_match = re.search(r"supplier\s+([\w\s]+)", prompt)
    if supplier_match:
        supplier_name = supplier_match.group(1).strip().title()

    # Find Contact Number
    contact_match = re.search(r"contact\s+(\d+)", prompt)
    if contact_match:
        contact_number = contact_match.group(1)

    return item_name, quantity, department_name, supplier_name, contact_number


def parse_dashboard_prompt(prompt: str):
    """
    Parses prompts related to dashboard/report generation.
    """
    prompt = prompt.lower()

    target_audience = None
    report_type = None
    frequency = None

    # Detect Target Audience
    if "hod" in prompt:
        target_audience = "HOD"
    elif "director" in prompt:
        target_audience = "Director"
    elif "finance" in prompt:
        target_audience = "Finance"

    # Detect Report Type
    if "prf" in prompt:
        report_type = "PRF"
    elif "claim" in prompt:
        report_type = "Claim"
    elif "expense" in prompt:
        report_type = "Expense"
    elif "project" in prompt:
        report_type = "Project"
    elif "summary" in prompt:
        report_type = "Summary"

    # Detect Frequency
    if "weekly" in prompt:
        frequency = "Weekly"
    elif "monthly" in prompt:
        frequency = "Monthly"
    elif "daily" in prompt:
        frequency = "Daily"

    return target_audience, report_type, frequency
