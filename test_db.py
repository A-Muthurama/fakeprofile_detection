import os
from dotenv import load_dotenv
from app.database.repositories.report_repository import ReportRepository

load_dotenv()

# Test connection
print("Testing database connection...")

try:
    repo = ReportRepository()
    
    # Try to save a test report
    test_report = {
        'profile_url': 'https://instagram.com/test',
        'platform': 'instagram',
        'result': {
            'score': {
                'final_score': 85,
                'risk_level': 'LOW RISK'
            }
        }
    }
    
    report_id = repo.save_report(test_report)
    print(f"✓ Test report saved with ID: {report_id}")
    
    # Try to retrieve it
    retrieved = repo.get_report(str(report_id))
    print(f"✓ Test report retrieved: {retrieved['profile_url']}")
    
    # Get total count
    total = repo.get_total_reports()
    print(f"✓ Total reports in database: {total}")
    
    print("\n✅ DATABASE CONNECTION SUCCESSFUL!")
    
    repo.close()
    
except Exception as e:
    print(f"❌ Database Error: {str(e)}")
    
    muthukrishnan8733_db_user
    HzU45KPcqViSVdT9