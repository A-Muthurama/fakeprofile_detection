
import os
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
import joblib
import random

# Ensure directories exist
os.makedirs('ml_models/trained_models', exist_ok=True)
os.makedirs('ml_models/datasets', exist_ok=True)

def generate_synthetic_data(n_samples=2000):
    """
    Generate synthetic data to train a model for fake profile detection.
    
    Features:
    - followers: Number of followers
    - following: Number of accounts following
    - posts: Number of posts
    - account_age: Age of account in days
    - bio_length: Length of bio text
    - has_profile_pic: 1 if yes, 0 if no
    - username_has_digits: 1 if yes, 0 if no
    - follower_ratio: followers / (following + 1)
    
    Target:
    - is_fake: 1 if fake, 0 if real
    """
    data = []
    
    for _ in range(n_samples // 2):
        # Generate REAL profile features
        followers = int(np.random.lognormal(mean=6, sigma=1.5)) # More followers
        following = int(np.random.lognormal(mean=5, sigma=1))
        posts = int(np.random.exponential(scale=50)) + 10
        account_age = random.randint(365, 3650) # 1-10 years
        bio_length = random.randint(10, 150)
        has_profile_pic = 1
        username_has_digits = 0 if random.random() > 0.2 else 1
        
        data.append({
            'followers': followers,
            'following': following,
            'posts': posts,
            'account_age': account_age,
            'bio_length': bio_length,
            'has_profile_pic': has_profile_pic,
            'username_has_digits': username_has_digits,
            'is_fake': 0
        })

    for _ in range(n_samples // 2):
        # Generate FAKE profile features
        followers = int(np.random.lognormal(mean=3, sigma=1)) # Fewer followers
        following = int(np.random.lognormal(mean=6, sigma=1)) # High following (follow-back bots)
        posts = int(np.random.exponential(scale=5))
        account_age = random.randint(0, 365) # New accounts
        bio_length = random.randint(0, 20)
        has_profile_pic = 0 if random.random() > 0.4 else 1
        username_has_digits = 1 if random.random() > 0.3 else 0
        
        data.append({
            'followers': followers,
            'following': following,
            'posts': posts,
            'account_age': account_age,
            'bio_length': bio_length,
            'has_profile_pic': has_profile_pic,
            'username_has_digits': username_has_digits,
            'is_fake': 1
        })
    
    df = pd.DataFrame(data)
    
    # Feature Engineering: Follower Ratio
    df['follower_ratio'] = df['followers'] / (df['following'] + 1)
    
    return df

def train_model():
    print("Generating synthetic dataset...")
    df = generate_synthetic_data()
    
    X = df.drop('is_fake', axis=1)
    y = df['is_fake']
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    print("Training Random Forest Classifier...")
    # Initialize and train classifier
    clf = RandomForestClassifier(n_estimators=100, random_state=42)
    clf.fit(X_train, y_train)
    
    # Evaluate
    y_pred = clf.predict(X_test)
    print("\nModel Performance:")
    print(f"Accuracy: {accuracy_score(y_test, y_pred):.4f}")
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred))
    
    # Save model and columns
    model_path = 'ml_models/trained_models/fake_profile_detector.pkl'
    joblib.dump({
        'model': clf,
        'features': list(X.columns)
    }, model_path)
    
    print(f"\nModel saved to {model_path}")
    
    # Save dataset for reference
    df.to_csv('ml_models/datasets/synthetic_training_data.csv', index=False)
    print("Dataset saved to ml_models/datasets/synthetic_training_data.csv")

if __name__ == "__main__":
    train_model()
