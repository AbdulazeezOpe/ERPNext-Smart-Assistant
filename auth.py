def check_login(password_input: str) -> bool:
    """
    Simple password check function.
    For now, the correct password is loaded from environment variables.
    """
    import os
    from dotenv import load_dotenv

    load_dotenv()
    correct_password = os.getenv("APP_PASSWORD")

    if password_input == correct_password:
        return True
    return False