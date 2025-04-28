import re

def parse_boq_request(user_prompt: str):
    user_prompt = user_prompt.lower()
    
    # Default
    action = None
    project_name = None
    boq_item = None

    # Detect if asking for balance
    if "balance" in user_prompt:
        action = "show_balance"
    
    # Detect if asking to list BOQ items
    elif "list" in user_prompt and "boq" in user_prompt:
        action = "list_boq_items"

    # Extract Project Name (very basic for now)
    match = re.search(r"project\s+(\w+)", user_prompt)
    if match:
        project_name = match.group(1)

    # Extract BOQ item if mentioned
    item_match = re.search(r"for\s+([\w\s]+)\s+in\s+project", user_prompt)
    if item_match:
        boq_item = item_match.group(1).strip()

    return action, project_name, boq_item
