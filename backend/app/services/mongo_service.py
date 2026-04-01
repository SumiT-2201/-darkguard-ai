from pymongo import MongoClient
from datetime import datetime
import os

class MongoService:
    def __init__(self, uri, db_name):
        try:
            self.client = MongoClient(uri, serverSelectionTimeoutMS=5000)
            # Ping to check if server is active
            self.client.admin.command('ping')
            self.db = self.client[db_name]
            self.collection = self.db['scans']
            print(f"✅ Connected to MongoDB: {db_name}")
        except Exception as e:
            print(f"⚠️ MongoDB connection issue: {e}")
            self.client = None
            self.db = None
            self.collection = None

    def is_active(self):
        return self.client is not None and self.db is not None

    def _clean_doc(self, doc):
        """
        Ensures all BSON types (like ObjectId) are converted to JSON-serializable strings.
        """
        if not doc:
            return None
        
        # In-place conversion of common MongoDB BSON types
        if '_id' in doc:
            doc['id'] = str(doc['_id']) # Standard ID for frontend
            doc['_id'] = str(doc['_id']) # Original ID as string
            
        return doc

    def save_scan(self, report):
        """
        Saves a scan report to MongoDB.
        """
        if not self.is_active():
            return False
        
        try:
            # Insert into collection
            self.collection.insert_one(report)
            
            # CRITICAL: Convert the newly added ObjectId to string before returning to routes
            self._clean_doc(report)
            return True
        except Exception as e:
            print(f"Error saving scan to MongoDB: {e}")
            return False

    def get_history(self, limit=50):
        """
        Retrieves recent scan history from MongoDB.
        """
        if not self.is_active():
            return []
        
        try:
            # Fetch latest scans
            cursor = self.collection.find().sort("scan_date", -1).limit(limit)
            
            history = []
            for doc in cursor:
                history.append(self._clean_doc(doc))
            return history
        except Exception as e:
            print(f"Error fetching history from MongoDB: {e}")
            return []

    def get_report(self, report_id):
        """
        Retrieves a single report by MongoDB ObjectId.
        """
        if not self.is_active():
            return None
        
        from bson.objectid import ObjectId
        try:
            doc = self.collection.find_one({"_id": ObjectId(report_id)})
            return self._clean_doc(doc)
        except Exception as e:
            print(f"Error fetching report from MongoDB: {e}")
            return None
