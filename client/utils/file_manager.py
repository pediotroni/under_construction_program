import json
from pathlib import Path

def save_user_data(mobile: str, token: str):
    data = {"mobile": mobile, "token": token}
    Path("user.cln").write_text(json.dumps(data), encoding="utf-8")

def load_user_data():
    try:
        return json.loads(Path("user.cln").read_text(encoding="utf-8"))
    except:
        return None