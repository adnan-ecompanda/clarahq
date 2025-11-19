import secrets
import string

BASE_URL = "https://video.clarahq.com"

def generate_meeting_id(length=12):
    chars = string.ascii_letters + string.digits
    return ''.join(secrets.choice(chars) for _ in range(length))

def generate_telehealth_url():
    meeting_id = generate_meeting_id()
    return f"{BASE_URL}/meet/{meeting_id}", meeting_id