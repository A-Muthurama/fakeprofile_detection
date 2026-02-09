import requests
import json

BASE_URL = "http://127.0.0.1:5000/api/v1"

def test_manual_analysis():
    print("[TEST] Testing Manual Profile Audit Endpoint...")
    url = f"{BASE_URL}/manual"
    
    payload = {
        'followers': 120,
        'following': 2000,
        'posts': 5,
        'account_age': 30,
        'bio': "DM for collab",
        'no_pic': True,
        'digits': True
    }
    
    try:
        response = requests.post(url, json=payload)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            score = data.get('score', {}).get('final_score')
            print(f"Manual Analysis Score: {score}")
            print("Risk Level:", data.get('score', {}).get('risk_level'))
        else:
            print("Error:", response.text)
            
    except Exception as e:
        print(f"Request failed: {e}")

def test_message_analysis():
    print("\n[TEST] Testing Scam Message Detector Endpoint...")
    url = f"{BASE_URL}/message"
    
    payload = {
        'message': "Congratulations! You won a lottery prize. Click here to claim your bitcoin investment."
    }
    
    try:
        response = requests.post(url, json=payload)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            score = data.get('score')
            print(f"Scam Probability: {score}")
            print("Triggers:", data.get('triggers'))
        else:
            print("Error:", response.text)
            
    except Exception as e:
        print(f"Request failed: {e}")

def test_existing_analyze():
    print("[TEST] Testing Existing /analyze Endpoint...")
    url = f"{BASE_URL}/analyze"
    payload = {
        "profile_url": "https://instagram.com/test",
        "platform": "instagram"
    }
    try:
        response = requests.post(url, json=payload)
        print(f"Status Code: {response.status_code}")
        # We expect 200 or 500 (if scraping fails) but NOT 404
        if response.status_code == 404:
            print("CRITICAL: Existing endpoint not found!")
        else:
            print("Existing endpoint found.")
    except Exception as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    test_existing_analyze()
    test_manual_analysis()
    test_message_analysis()
