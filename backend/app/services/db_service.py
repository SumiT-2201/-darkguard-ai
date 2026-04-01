import sqlite3
import json
import os
from datetime import datetime

class DBService:
    def __init__(self, db_path):
        self.db_path = db_path
        self._init_db()

    def _get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        with self._get_connection() as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS scans (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    url TEXT NOT NULL,
                    domain TEXT,
                    trust_score INTEGER,
                    grade TEXT,
                    findings_list TEXT,
                    categories TEXT,
                    recommendations TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            conn.commit()

    def save_scan(self, report):
        """
        Saves a scan report to SQLite.
        Expects report to be the dict returned by ReportGenerator.
        """
        try:
            with self._get_connection() as conn:
                conn.execute('''
                    INSERT INTO scans (url, domain, trust_score, grade, findings_list, categories, recommendations, timestamp)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    report['url'],
                    report['domain'],
                    report['trust_score'],
                    report['grade'],
                    json.dumps(report['findings_list']),
                    json.dumps(report['categories']),
                    json.dumps(report['recommendations']),
                    report['scan_date']
                ))
                conn.commit()
                return True
        except Exception as e:
            print(f"Error saving scan to SQLite: {e}")
            return False

    def get_history(self, limit=50):
        """
        Retrieves recent scan history.
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.execute('''
                    SELECT * FROM scans ORDER BY timestamp DESC LIMIT ?
                ''', (limit,))
                rows = cursor.fetchall()
                
                history = []
                for row in rows:
                    history.append({
                        "id": row['id'],
                        "url": row['url'],
                        "domain": row['domain'],
                        "trust_score": row['trust_score'],
                        "grade": row['grade'],
                        "findings_list": json.loads(row['findings_list']),
                        "categories": json.loads(row['categories']),
                        "recommendations": json.loads(row['recommendations']),
                        "timestamp": row['timestamp']
                    })
                return history
        except Exception as e:
            print(f"Error fetching history from SQLite: {e}")
            return []

    def get_report(self, report_id):
        """
        Retrieves a single report by ID.
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.execute('SELECT * FROM scans WHERE id = ?', (report_id,))
                row = cursor.fetchone()
                if not row:
                    return None
                    
                return {
                    "id": row['id'],
                    "url": row['url'],
                    "domain": row['domain'],
                    "trust_score": row['trust_score'],
                    "grade": row['grade'],
                    "findings_list": json.loads(row['findings_list']),
                    "categories": json.loads(row['categories']),
                    "recommendations": json.loads(row['recommendations']),
                    "timestamp": row['timestamp']
                }
        except Exception as e:
            print(f"Error fetching report from SQLite: {e}")
            return None
