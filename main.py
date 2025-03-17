import json
from pathlib import Path
import tkinter as tk
from security import SecurityManager
from database import DatabaseManager
from notifications import NotificationManager
from backups import BackupManager
from ui import UIManager

def load_config():
    config_path = Path("config.json")
    if not config_path.exists():
        raise FileNotFoundError("Please create config.json with required credentials")
    with open(config_path, 'r') as f:
        return json.load(f)

if __name__ == "__main__":
    config = load_config()
    
    security = SecurityManager(config["encryption_key"])
    db = DatabaseManager("school_fees.db", security)
    notif = NotificationManager(config["email"]["sender"], config["email"]["password"])
    backup = BackupManager(db.conn)
    
    root = tk.Tk()
    app = UIManager(root, db, notif, backup, config["fee_structure"], security)
    root.mainloop()