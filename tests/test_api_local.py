import requests
import json
import time

def test_api():
    base_url = "http://127.0.0.1:5000/api/v1"
    
    print("1. Testing Health Endpoint...")
    try:
        resp = requests.get(f"{base_url}/health")
        print(f"Status: {resp.status_code}")
        print(f"Response: {resp.json()}")
    except Exception as e:
        print(f"Health check failed: {e}")
        return

    print("\n2. Testing Analysis Endpoint (Fake Profile Simulation)...")
    payload_fake = {
        "profile_url": "https://instagram.com/bot_user_test",
        "platform": "instagram"
    }
    try:
        resp = requests.post(f"{base_url}/analyze", json=payload_fake)
        print(f"Status: {resp.status_code}")
        if resp.status_code == 200:
            data = resp.json()
            # print("Score:", data.get('score', {}).get('final_score'))
            # print("Risk Level:", data.get('score', {}).get('risk_level'))
            # print("ML Version:", data.get('ml_version'))
            # print("Subscores:", json.dumps(data.get('score', {}).get('subscores'), indent=2))
            print("Full Response:")
            print(json.dumps(data, indent=2))
        else:
            print("Error:", resp.text)
    except Exception as e:
        print(f"Analysis failed: {e}")

    print("\n3. Testing Analysis Endpoint (Authentic Profile Simulation)...")
    payload_real = {
        "profile_url": "https://instagram.com/authentic_user",
        "platform": "instagram"
    }
    try:
        resp = requests.post(f"{base_url}/analyze", json=payload_real)
        print(f"Status: {resp.status_code}")
        if resp.status_code == 200:
            data = resp.json()
            print("Score:", data.get('score', {}).get('final_score'))
            print("Risk Level:", data.get('score', {}).get('risk_level'))
            print("ML Version:", data.get('ml_version'))
        else:
            print("Error:", resp.text)
    except Exception as e:
        print(f"Analysis failed: {e}")


    print("\n4. Testing Manual Analysis Endpoint...")
    payload_manual = {
        'followers': 120,
        'following': 2000,
        'posts': 5,
        'account_age': 30,
        'bio': "DM for collab",
        'no_pic': True,
        'digits': True
    }
    try:
        resp = requests.post(f"{base_url}/analyze/manual", json=payload_manual)
        print(f"Status: {resp.status_code}")
        if resp.status_code == 200:
            data = resp.json()
            score = data.get('score', {}).get('final_score')
            print(f"Manual Analysis Score: {score}")
            print("Full Response:", json.dumps(data, indent=2))
        else:
            print("Error:", resp.text)
    except Exception as e:
        print(f"Manual Analysis failed: {e}")

    print("\n5. Testing Scam Message Detector Endpoint...")
    payload_message = {
        'message': "Congratulations! You won a lottery prize. Click here to claim your bitcoin investment."
    }
    try:
        resp = requests.post(f"{base_url}/analyze/message", json=payload_message)
        print(f"Status: {resp.status_code}")
        if resp.status_code == 200:
            data = resp.json()
            score = data.get('score')
            print(f"Scam Probability: {score}")
            print("Message Analysis:", data.get('analysis'))
        else:
            print("Error:", resp.text)
    except Exception as e:
        print(f"Message Analysis failed: {e}")

if __name__ == "__main__":
    test_api()
