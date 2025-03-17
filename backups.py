import sqlite3
import zipfile
from datetime import datetime
import logging

class BackupManager:
    def __init__(self, db_connection):
        self.conn = db_connection

    def create_backup(self):
        try:
            backup_file = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            sql_file = f"{backup_file}.sql"
            with open(sql_file, 'w') as f:
                for line in self.conn.iterdump():
                    f.write(f'{line}\n')
            
            with zipfile.ZipFile(f"{backup_file}.zip", 'w', zipfile.ZIP_DEFLATED) as zipf:
                zipf.write(sql_file)
            
            import os
            os.remove(sql_file)
            logging.info(f"Backup created: {backup_file}.zip")
            return f"{backup_file}.zip"
        except Exception as e:
            logging.error(f"Backup failed: {str(e)}")
            return None