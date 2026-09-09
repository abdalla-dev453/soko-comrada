import re

PHONE_RE = re.compile(r"^\+?\d{9,15}$")
MPESA_CODE_RE = re.compile(r"^[A-Z0-9]{10,15}$")


def validate_student_email(email: str, allowed_domains: list[str]) -> bool:
    if not allowed_domains:
        return True
    email = email.strip().lower()
    if "@" not in email:
        return False
    domain = email.rsplit("@", 1)[-1]
    return domain in {d.lower() for d in allowed_domains}


def validate_phone(phone: str) -> bool:
    return bool(PHONE_RE.match(phone.strip()))


def validate_mpesa_code(code: str) -> bool:
    return bool(MPESA_CODE_RE.match(code.strip().upper()))


def normalize_mpesa_code(code: str) -> str:
    return code.strip().upper()
