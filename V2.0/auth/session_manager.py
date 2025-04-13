import os
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

class SessionManager:
    def __init__(self):
        self.session_file = "session.json"
    
    def save_session(self, auth_token):
        """Save auth token with expiration"""
        session_data = {
            "auth_token": auth_token,
            "expires_at": (datetime.now() + timedelta(days=1)).isoformat()
        }
        with open(self.session_file, "w") as f:
            json.dump(session_data, f)
    
    def load_session(self):
        """Load session if valid"""
        if not os.path.exists(self.session_file):
            return None
        
        with open(self.session_file, "r") as f:
            session_data = json.load(f)
        
        if datetime.fromisoformat(session_data["expires_at"]) < datetime.now():
            return None
        
        return session_data["auth_token"]
    
    def clear_session(self):
        """Remove session data"""
        if os.path.exists(self.session_file):
            os.remove(self.session_file)
