import requests

def create_erpnext_doctype(api_url: str, auth: tuple, doctype_name: str, fields: list):
    payload = {
        "doctype": "DocType",
        "name": doctype_name,
        "module": "Custom",
        "custom": 1,
        "fields": fields
    }

    response = requests.post(
        f"{api_url}/api/resource/DocType",
        auth=auth,
        json=payload
    )

    try:
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        print("🔴 Error Response:", response.text)
        return {"error": response.text}


def get_records_for_doctype(api_url: str, auth: tuple, doctype_name: str) -> list:
    response = requests.get(f"{api_url}/api/resource/{doctype_name}", auth=auth)
    if response.status_code == 200:
        return response.json().get("data", [])
    return []

def get_all_doctypes(api_url: str, auth: tuple):
    try:
        url = f"{api_url}/api/method/frappe.client.get_list"
        headers = {"Content-Type": "application/json"}
        payload = {
            "doctype": "DocType",
            "fields": ["name", "module", "issingle", "istable", "custom"],
            "limit_page_length": 999
        }

        response = requests.post(url, headers=headers, auth=auth, json=payload)
        response.raise_for_status()
        data = response.json()

        # Extract only relevant Doctypes
        doctypes = [
            d["name"]
            for d in data["message"]
            if not d["issingle"] and not d["istable"]
            and d["module"] not in ["Core", "Custom", "Email", "Workflow", "Website"]
        ]

        return sorted(doctypes)

    except Exception as e:
        print(f"Error fetching doctypes: {e}")
        return []
    
    


def create_workflow(api_url: str, auth: tuple, workflow_name: str, document_type: str, states: list, transitions: list):
    payload = {
        "doctype": "Workflow",
        "workflow_name": workflow_name,
        "document_type": document_type,
        "is_active": 1,
        "workflow_state_field": "workflow_state",
        "states": states,
        "transitions": transitions
    }

    response = requests.post(
        f"{api_url}/api/resource/Workflow",
        auth=auth,
        json=payload
    )

    try:
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        print("🔴 Workflow Creation Error:", response.text)
        return {"error": response.text}




def create_role(api_url: str, auth: tuple, role_name: str):
    payload = {
        "doctype": "Role",
        "role_name": role_name,
    }

    response = requests.post(
        f"{api_url}/api/resource/Role",
        auth=auth,
        json=payload
    )

    try:
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        print("🔴 Role Creation Error:", response.text)
        return {"error": response.text}
    
    
def set_permission(api_url: str, auth: tuple, doctype: str, role: str, perm_level=0, read=1, write=0, create=0, delete=0, submit=0):
    payload = {
        "doctype": "Custom DocPerm",
        "parenttype": "DocType",
        "parent": doctype,
        "role": role,
        "permlevel": perm_level,
        "read": read,
        "write": write,
        "create": create,
        "delete": delete,
        "submit": submit
    }

    response = requests.post(
        f"{api_url}/api/resource/Custom DocPerm",
        auth=auth,
        json=payload
    )

    try:
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        print("🔴 Permission Error:", response.text)
        return {"error": response.text}


def create_notification(api_url: str, auth: tuple, subject: str, document_type: str, condition: str, message: str):
    payload = {
        "doctype": "Notification",
        "subject": subject,
        "document_type": document_type,
        "event": "Value Change",
        "condition": condition,
        "recipient_by_document_field": "owner",
        "message": message
    }

    response = requests.post(
        f"{api_url}/api/resource/Notification",
        auth=auth,
        json=payload
    )

    try:
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        print("🔴 Notification Error:", response.text)
        return {"error": response.text}



def create_scheduled_reminder(api_url: str, auth: tuple, doctype: str, condition: str, message: str, cron: str):
    """
    Create a Scheduled Reminder using ERPNext Scheduled Job or Notification
    - doctype: the document type (e.g., PRF, Claims)
    - condition: the filter condition (e.g., status="Pending")
    - message: the reminder message
    - cron: the schedule in CRON format (e.g., '0 9 * * 1' for every Monday 9AM)
    """
    payload = {
        "doctype": "Auto Repeat",
        "reference_doctype": doctype,
        "reference_document": "",  # Not tied to one record
        "cron_expression": cron,   # CRON expression for schedule
        "status": "Active",
        "notify_by_email": 1,
        "subject": f"Reminder for {doctype}",
        "message": message,
        "filters": condition
    }

    response = requests.post(
        f"{api_url}/api/resource/Auto Repeat",
        auth=auth,
        json=payload
    )
    return response.json()


def create_department(api_url: str, api_key: str, api_secret: str, department_name: str, company_name: str, parent_department: str = "Management"):
    """
    Create a new Department in ERPNext.
    """
    payload = {
        "doctype": "Department",
        "department_name": department_name,
        "company": company_name,
        "department": department_name,
        "parent_department": parent_department,
        "is_group": 0
    }

    headers = {
        "Authorization": f"token {api_key}:{api_secret}"
    }
    print("👉 DEBUG: Payload being sent to ERPNext:", payload)

    response = requests.post(
        f"{api_url}/api/resource/Department",
        headers=headers,
        json=payload
    )

    try:
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        print("🔴 Department Creation Error:", response.text)
        return {"error": response.text}



def create_user(api_url: str, auth: tuple, first_name: str, email: str):
    """
    Create a new User in ERPNext.
    """
    payload = {
        "doctype": "User",
        "first_name": first_name,
        "email": email,
        "enabled": 1,
        "new_password": "password123",  # default password, client can reset later
        "send_welcome_email": 0
    }

    response = requests.post(
        f"{api_url}/api/resource/User",
        auth=auth,
        json=payload
    )

    try:
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        print("🔴 User Creation Error:", response.text)
        return {"error": response.text}



def assign_role_to_user(api_url: str, auth: tuple, user_email: str, role_name: str):
    """
    Assign an existing Role to a User in ERPNext.
    """
    payload = {
        "user": user_email,
        "role": role_name
    }

    response = requests.post(
        f"{api_url}/api/method/frappe.core.doctype.user.user.add_role",
        auth=auth,
        json=payload
    )

    try:
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        print("🔴 Role Assignment Error:", response.text)
        return {"error": response.text}




def get_boq_records(api_url: str, auth: tuple, project_name: str = None):
    params = {}
    if project_name:
        params["filters"] = f'[["Project BOQ", "project_name", "=", "{project_name}"]]'
    
    response = requests.get(
        f"{api_url}/api/resource/Project BOQ",
        auth=auth,
        params=params
    )
    
    if response.status_code == 200:
        return response.json().get("data", [])
    else:
        return []



def create_management_fee_rule(api_url: str, auth: tuple, department_name: str, fee_amount: float):
    """
    Create a Management Fee record (custom doctype or use Expense Claim if needed).
    """
    payload = {
        "doctype": "Management Fee Rule",  # Assuming you create a simple Doctype called 'Management Fee Rule'
        "department": department_name,
        "monthly_fee": fee_amount
    }

    response = requests.post(
        f"{api_url}/api/resource/Management Fee Rule",
        auth=auth,
        json=payload
    )

    try:
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        print("🔴 Management Fee Rule Error:", response.text)
        return {"error": response.text}


def create_profit_sharing_rule(api_url: str, auth: tuple, department_name: str, role_name: str, percentage: float):
    """
    Create a Profit Sharing Rule record.
    """
    payload = {
        "doctype": "Profit Sharing Rule",  # Assuming you create a simple Doctype called 'Profit Sharing Rule'
        "department": department_name,
        "role": role_name,
        "profit_percentage": percentage
    }

    response = requests.post(
        f"{api_url}/api/resource/Profit Sharing Rule",
        auth=auth,
        json=payload
    )

    try:
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        print("🔴 Profit Sharing Rule Error:", response.text)
        return {"error": response.text}



def create_prf(api_url: str, auth: tuple, project_name: str, item_name: str, quantity: float):
    """
    Create a new Purchase Request Form (PRF) in ERPNext.
    """
    payload = {
        "doctype": "Purchase Request",  # or your PRF doctype name
        "project": project_name,
        "item_name": item_name,
        "quantity": quantity,
        "status": "Draft"  # Initially PRFs are created as Drafts
    }

    response = requests.post(
        f"{api_url}/api/resource/Purchase Request",
        auth=auth,
        json=payload
    )

    try:
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        print("🔴 PRF Creation Error:", response.text)
        return {"error": response.text}



def get_pending_prfs(api_url: str, auth: tuple, department_name: str = None):
    """
    Fetch pending PRFs (Draft or Open) optionally filtered by Department.
    """
    filters = [["Purchase Request", "status", "in", ["Draft", "Open"]]]

    if department_name:
        filters.append(["Purchase Request", "department", "=", department_name])

    params = {
        "filters": str(filters)
    }

    response = requests.get(
        f"{api_url}/api/resource/Purchase Request",
        auth=auth,
        params=params
    )

    if response.status_code == 200:
        return response.json().get("data", [])
    else:
        return []


def create_claim(api_url: str, auth: tuple, project_name: str, claim_name: str, amount: float, due_date: str = None):
    """
    Create a new Claim in ERPNext.
    """
    payload = {
        "doctype": "Project Claim",  # Or whatever your ERPNext Claim Doctype is called
        "project_name": project_name,
        "claim_name": claim_name,
        "amount": amount,
        "due_date": due_date,
        "status": "Draft"
    }

    response = requests.post(
        f"{api_url}/api/resource/Project Claim",
        auth=auth,
        json=payload
    )

    try:
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        print("🔴 Claim Creation Error:", response.text)
        return {"error": response.text}



def get_claims(api_url: str, auth: tuple, project_name: str = None, status: str = None):
    """
    Fetch claims from ERPNext, optionally filtered by project or status.
    """
    filters = []

    if project_name:
        filters.append(["Project Claim", "project_name", "=", project_name])
    if status:
        filters.append(["Project Claim", "status", "=", status])

    params = {
        "filters": str(filters)
    }

    response = requests.get(
        f"{api_url}/api/resource/Project Claim",
        auth=auth,
        params=params
    )

    if response.status_code == 200:
        return response.json().get("data", [])
    else:
        return []


def create_project(api_url: str, auth: tuple, project_name: str, expected_end_date: str = None, estimated_cost: float = None):
    """
    Create a new Project in ERPNext with optional expected end date and estimated cost.
    """

    payload = {
        "doctype": "Project",
        "project_name": project_name,
        "project_type": "External",  # You can change to "Internal" if needed
        "status": "Open"
    }

    # Add optional fields if provided
    if expected_end_date:
        payload["expected_end_date"] = expected_end_date

    if estimated_cost is not None:
        payload["estimated_costing"] = estimated_cost

    try:
        response = requests.post(
            f"{api_url}/api/resource/Project",
            auth=auth,
            json=payload
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print("🔴 Project Creation Error:", e)
        return {"error": str(e)}


def assign_project_roles(api_url: str, auth: tuple, project_name: str, user_role_pairs: list):
    """
    Assign multiple users to a project with specific roles.
    user_role_pairs: list of tuples (user_email, role)
    """
    # Fetch the existing Project first
    response = requests.get(
        f"{api_url}/api/resource/Project/{project_name}",
        auth=auth
    )

    if response.status_code != 200:
        print("🔴 Failed to fetch project:", response.text)
        return {"error": "Project not found or API error"}

    project_data = response.json().get("data", {})

    # Prepare the updated team members
    team_members = []

    for user_email, role in user_role_pairs:
        team_members.append({
            "doctype": "Project Team",
            "user": user_email,
            "role": role
        })

    # Update the project with team members
    update_payload = {
        "project_name": project_name,
        "team_members": team_members
    }

    update_response = requests.put(
        f"{api_url}/api/resource/Project/{project_name}",
        auth=auth,
        json=update_payload
    )

    try:
        update_response.raise_for_status()
        return update_response.json()
    except requests.exceptions.HTTPError as e:
        print("🔴 Project Role Assignment Error:", update_response.text)
        return {"error": update_response.text}


def generate_contract(api_url: str, auth: tuple, employee_name: str, monthly_salary: float, start_date: str):
    """
    Generate a new Employment Contract for an employee.
    """
    payload = {
        "doctype": "Employment Contract",  # Adjust if your ERPNext uses a different Doctype
        "employee_name": employee_name,
        "monthly_salary": monthly_salary,
        "start_date": start_date,
        "status": "Active"
    }

    response = requests.post(
        f"{api_url}/api/resource/Employment Contract",
        auth=auth,
        json=payload
    )

    try:
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        print("🔴 Employment Contract Creation Error:", response.text)
        return {"error": response.text}


def get_salary_advances(api_url: str, auth: tuple, employee_name: str = None):
    """
    Fetch salary advance requests, optionally filtered by employee name.
    """
    filters = []

    if employee_name:
        filters.append(["Salary Advance", "employee_name", "=", employee_name])

    params = {
        "filters": str(filters)
    }

    response = requests.get(
        f"{api_url}/api/resource/Salary Advance",
        auth=auth,
        params=params
    )

    if response.status_code == 200:
        return response.json().get("data", [])
    else:
        return []


def get_leave_balance(api_url: str, auth: tuple, employee_name: str):
    """
    Fetch leave balance for a specific employee.
    """
    params = {
        "filters": str([["Leave Allocation", "employee_name", "=", employee_name]])
    }

    response = requests.get(
        f"{api_url}/api/resource/Leave Allocation",
        auth=auth,
        params=params
    )

    if response.status_code == 200:
        leave_data = response.json().get("data", [])
        return leave_data
    else:
        return []


def add_vehicle(api_url: str, auth: tuple, vehicle_name: str, department: str = None):
    """
    Add a new Vehicle or Asset to ERPNext.
    """
    payload = {
        "doctype": "Asset",  # Assuming you're using Asset Doctype
        "asset_name": vehicle_name,
        "asset_category": "Vehicle",
        "department": department,
        "status": "Active"
    }

    response = requests.post(
        f"{api_url}/api/resource/Asset",
        auth=auth,
        json=payload
    )

    try:
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        print("🔴 Vehicle/Asset Addition Error:", response.text)
        return {"error": response.text}


def schedule_vehicle_maintenance(api_url: str, auth: tuple, vehicle_name: str, frequency_months: int):
    """
    Schedule maintenance task for a vehicle at given monthly intervals.
    """
    payload = {
        "doctype": "Maintenance Schedule",  # If your ERPNext has this Doctype
        "asset_name": vehicle_name,
        "periodicity": f"{frequency_months} Months",
        "status": "Planned"
    }

    response = requests.post(
        f"{api_url}/api/resource/Maintenance Schedule",
        auth=auth,
        json=payload
    )

    try:
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        print("🔴 Vehicle Maintenance Scheduling Error:", response.text)
        return {"error": response.text}

def get_all_assets(api_url: str, auth: tuple):
    """
    Fetch all vehicles/assets from ERPNext.
    """
    response = requests.get(
        f"{api_url}/api/resource/Asset",
        auth=auth
    )

    if response.status_code == 200:
        return response.json().get("data", [])
    else:
        return []


def add_inventory_item(api_url: str, auth: tuple, item_name: str, quantity: int, department: str = None):
    """
    Add a new inventory item into ERPNext.
    """
    payload = {
        "doctype": "Item",
        "item_name": item_name,
        "opening_stock": quantity,
        "stock_uom": "Nos",  # Assuming unit is "Numbers" (you can adjust if different)
        "default_warehouse": department
    }

    response = requests.post(
        f"{api_url}/api/resource/Item",
        auth=auth,
        json=payload
    )

    try:
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        print("🔴 Inventory Item Addition Error:", response.text)
        return {"error": response.text}


def add_supplier(api_url: str, auth: tuple, supplier_name: str, contact_number: str = None):
    """
    Add a new Supplier into ERPNext.
    """
    payload = {
        "doctype": "Supplier",
        "supplier_name": supplier_name,
        "supplier_group": "All Supplier Groups",  # You can adjust if you have different groups
        "supplier_type": "Company"
    }

    if contact_number:
        payload["contact_number"] = contact_number

    response = requests.post(
        f"{api_url}/api/resource/Supplier",
        auth=auth,
        json=payload
    )

    try:
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        print("🔴 Supplier Addition Error:", response.text)
        return {"error": response.text}




def generate_summary_report(api_url: str, auth: tuple):
    """
    Fetch PRFs, Claims, Expenses, and create a simple summary report.
    """
    summary = {}

    # Fetch PRFs
    prf_response = requests.get(f"{api_url}/api/resource/PRF", auth=auth)
    if prf_response.status_code == 200:
        prfs = prf_response.json().get("data", [])
        summary["Total PRFs"] = len(prfs)
    else:
        summary["Total PRFs"] = "Error Fetching"

    # Fetch Claims
    claim_response = requests.get(f"{api_url}/api/resource/Claim", auth=auth)
    if claim_response.status_code == 200:
        claims = claim_response.json().get("data", [])
        summary["Total Claims"] = len(claims)
    else:
        summary["Total Claims"] = "Error Fetching"

    # Fetch Expenses (if you track expenses in a specific Doctype)
    expense_response = requests.get(f"{api_url}/api/resource/Expense Claim", auth=auth)
    if expense_response.status_code == 200:
        expenses = expense_response.json().get("data", [])
        summary["Total Expenses"] = len(expenses)
    else:
        summary["Total Expenses"] = "Error Fetching"

    # Fetch Projects
    project_response = requests.get(f"{api_url}/api/resource/Project", auth=auth)
    if project_response.status_code == 200:
        projects = project_response.json().get("data", [])
        summary["Total Projects"] = len(projects)
    else:
        summary["Total Projects"] = "Error Fetching"

    return summary


def create_boq_entry(api_url: str, auth: tuple, project_name: str, item_name: str, quantity: float, price: float):
    """
    Create a new BOQ (Bill of Quantities) entry for a project.
    """
    payload = {
        "doctype": "Project BOQ",  # Assuming your ERPNext BOQ Doctype is called 'Project BOQ'
        "boq_item_description": item_name,
        "quantity": quantity,
        "budget_amount_rm": price,
        
    }

    response = requests.post(
        f"{api_url}/api/resource/Project BOQ",
        auth=auth,
        json=payload
    )

    try:
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        print("🔴 BOQ Entry Creation Error:", response.text)
        return {"error": response.text}





def project_exists(api_url: str, auth: tuple, project_name: str) -> bool:
    """
    Check if a project with the given name exists in ERPNext.
    """
    try:
        response = requests.get(
            f"{api_url}/api/resource/Project/{project_name}",
            auth=auth
        )
        if response.status_code == 200:
            return True
        else:
            return False
    except Exception as e:
        print("🔴 Project Check Error:", e)
        return False
