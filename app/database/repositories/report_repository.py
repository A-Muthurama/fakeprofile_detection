"""Repository for managing analysis reports in MongoDB"""

from pymongo import MongoClient
import os
from datetime import datetime
# Import ObjectId from bson if available; fall back to pymongo's objectid to satisfy linters/environments
try:
    from bson import ObjectId
except Exception:
    from pymongo import objectid as _objectid
    ObjectId = _objectid.ObjectId

class ReportRepository:
    """Manages analysis reports in MongoDB"""
    
    def __init__(self):
        """Initialize MongoDB connection"""
        # Use local MongoDB by default, or Atlas if MONGO_ATLAS_URI is set
        mongo_uri = os.getenv('MONGO_ATLAS_URI') or os.getenv('MONGO_URI', 'mongodb://localhost:27017/')
        self.client = MongoClient(mongo_uri)
        self.db = self.client[os.getenv('MONGO_DB_NAME', 'fake_profile_detection')]
        self.collection = self.db['analyzed_profiles']
        
        # Create indexes
        self.collection.create_index('profile_url')
        self.collection.create_index('timestamp', expireAfterSeconds=2592000)  # 30 days
    
    def save_report(self, report_data):
        """Save analysis report to database"""
        try:
            result = self.collection.insert_one({
                'profile_url': report_data.get('profile_url'),
                'platform': report_data.get('platform'),
                'result': report_data.get('result', {}),
                'timestamp': datetime.now(),
                'status': 'completed'
            })
            return result.inserted_id
        except Exception as e:
            print(f"Error saving report: {str(e)}")
            return None
    
    def get_report(self, report_id):
        """Get report by ID"""
        try:
            report = self.collection.find_one({'_id': ObjectId(report_id)})
            if report:
                report['_id'] = str(report['_id'])  # Convert ObjectId to string
            return report
        except Exception as e:
            print(f"Error getting report: {str(e)}")
            return None
    
    def get_reports(self, limit=20, offset=0):
        """Get all reports with pagination"""
        try:
            reports = list(self.collection.find()
                          .sort('timestamp', -1)
                          .skip(offset)
                          .limit(limit))
            
            for report in reports:
                report['_id'] = str(report['_id'])
            
            return reports
        except Exception as e:
            print(f"Error getting reports: {str(e)}")
            return []
    
    def delete_report(self, report_id):
        """Delete report by ID"""
        try:
            result = self.collection.delete_one({'_id': ObjectId(report_id)})
            return result.deleted_count > 0
        except Exception as e:
            print(f"Error deleting report: {str(e)}")
            return False
    
    def get_total_reports(self):
        """Get total number of reports"""
        try:
            return self.collection.count_documents({})
        except Exception as e:
            print(f"Error counting reports: {str(e)}")
            return 0
    
    def search_reports(self, query, limit=20):
        """Search reports by URL or platform"""
        try:
            results = list(self.collection.find({
                '$or': [
                    {'profile_url': {'$regex': query, '$options': 'i'}},
                    {'platform': {'$regex': query, '$options': 'i'}}
                ]
            }).limit(limit))
            
            for report in results:
                report['_id'] = str(report['_id'])
            
            return results
        except Exception as e:
            print(f"Error searching reports: {str(e)}")
            return []
    
    def count_by_risk(self, risk_level):
        """Count profiles by risk level"""
        try:
            if risk_level == 'high':
                return self.collection.count_documents({'result.score.final_score': {'$lt': 50}})
            elif risk_level == 'medium':
                return self.collection.count_documents({'result.score.final_score': {'$gte': 50, '$lt': 80}})
            elif risk_level == 'low':
                return self.collection.count_documents({'result.score.final_score': {'$gte': 80}})
            return 0
        except Exception as e:
            print(f"Error counting by risk: {str(e)}")
            return 0
    
    def get_average_score(self):
        """Get average integrity score"""
        try:
            result = self.collection.aggregate([
                {
                    '$group': {
                        '_id': None,
                        'average_score': {'$avg': '$result.score.final_score'}
                    }
                }
            ])
            
            data = list(result)
            if data:
                return round(data[0]['average_score'], 2)
            return 0
        except Exception as e:
            print(f"Error getting average score: {str(e)}")
            return 0
    
    def close(self):
        """Close MongoDB connection"""
        self.client.close()