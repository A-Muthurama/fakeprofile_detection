import os
import time
from datetime import datetime

class InstagramScraper:
    """Scrape Instagram profiles using instagrapi library"""
    
    def __init__(self):
        """Initialize scraper"""
        self.client = None
        self._init_client()
    
    def _init_client(self):
        """Initialize Instagram client"""
        try:
            from instagrapi import Client
            self.client = Client()
            
            # Try to login if credentials are provided
            username = os.getenv('INSTAGRAM_USERNAME')
            password = os.getenv('INSTAGRAM_PASSWORD')
            
            if username and password:
                try:
                    self.client.login(username, password)
                    print(f"[OK] Logged in to Instagram as {username}")
                except Exception as e:
                    print(f"[WARNING] Could not login: {str(e)}")
                    self.client = None
            else:
                print("[INFO] No Instagram credentials provided. Using public API only.")
                self.client = None
                
        except ImportError:
            print("[ERROR] instagrapi not installed. Install with: pip install instagrapi")
            self.client = None
    
    def scrape_profile(self, username):
        """
        Scrape Instagram profile data
        
        Args:
            username (str): Instagram username
            
        Returns:
            dict: Profile data
        """
        username = username.strip('@').strip()
        
        # Method 1: Try instagrapi (most reliable)
        if self.client:
            try:
                return self._scrape_with_instagrapi(username)
            except Exception as e:
                print(f"[WARNING] Instagrapi failed: {str(e)}")
        
        # Method 2: Try public web scraping
        try:
            return self._scrape_public_web(username)
        except Exception as e:
            print(f"[WARNING] Web scraping failed: {str(e)}")
        
        # Method 3: Try Instagram API (no auth)
        try:
            return self._scrape_instagram_api(username)
        except Exception as e:
            print(f"[WARNING] API scraping failed: {str(e)}")
        
        # Fallback: Return error data
        return self._get_fallback_data(username)
    
    def _scrape_with_instagrapi(self, username):
        """Scrape using instagrapi library (MOST RELIABLE)"""
        try:
            # Get user info
            user_id = self.client.user_id_from_username(username)
            user_info = self.client.user_info(user_id)
            
            profile_data = {
                'username': username,
                'full_name': user_info.full_name or username,
                'bio': user_info.biography or '',
                'followers': user_info.follower_count,
                'following': user_info.following_count,
                'posts': user_info.media_count,
                'profile_pic_url': str(user_info.profile_pic_url) if user_info.profile_pic_url else '',
                'is_verified': user_info.is_verified,
                'is_business': user_info.is_business,
                'is_private': user_info.is_private,
                'account_age_days': self._calculate_account_age(user_info),
                'external_url': user_info.external_url or '',
                'scrape_method': 'instagrapi'
            }
            
            # Calculate engagement ratio
            if profile_data['posts'] > 0:
                profile_data['engagement_ratio'] = profile_data['followers'] / profile_data['posts']
            else:
                profile_data['engagement_ratio'] = 0
            
            profile_data['has_profile_pic'] = bool(profile_data['profile_pic_url'])
            
            print(f"[SUCCESS] Scraped {username}: {profile_data['followers']} followers")
            return profile_data
            
        except Exception as e:
            print(f"[ERROR] Instagrapi scraping failed for {username}: {str(e)}")
            raise
    
    def _scrape_public_web(self, username):
        """Scrape from public Instagram page"""
        import requests
        from bs4 import BeautifulSoup
        import json
        import re
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        }
        
        url = f"https://www.instagram.com/{username}/"
        response = requests.get(url, headers=headers, timeout=15)
        
        if response.status_code != 200:
            raise Exception(f"HTTP {response.status_code}")
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Try to find shared data in script tags
        scripts = soup.find_all('script', type='text/javascript')
        
        for script in scripts:
            if script.string and 'window._sharedData' in script.string:
                # Extract JSON from script
                json_text = script.string.split('window._sharedData = ')[1].split(';</script>')[0]
                data = json.loads(json_text)
                
                user_data = data['entry_data']['ProfilePage'][0]['graphql']['user']
                
                profile_data = {
                    'username': username,
                    'full_name': user_data.get('full_name', username),
                    'bio': user_data.get('biography', ''),
                    'followers': user_data['edge_followed_by']['count'],
                    'following': user_data['edge_follow']['count'],
                    'posts': user_data['edge_owner_to_timeline_media']['count'],
                    'profile_pic_url': user_data.get('profile_pic_url_hd', ''),
                    'is_verified': user_data.get('is_verified', False),
                    'is_business': user_data.get('is_business_account', False),
                    'is_private': user_data.get('is_private', False),
                    'account_age_days': 365,
                    'scrape_method': 'web-scraping'
                }
                
                if profile_data['posts'] > 0:
                    profile_data['engagement_ratio'] = profile_data['followers'] / profile_data['posts']
                else:
                    profile_data['engagement_ratio'] = 0
                
                profile_data['has_profile_pic'] = bool(profile_data['profile_pic_url'])
                
                print(f"[SUCCESS] Web scraped {username}: {profile_data['followers']} followers")
                return profile_data
        
        raise Exception("Could not find profile data in page")
    
    def _scrape_instagram_api(self, username):
        """Try Instagram's public API endpoint"""
        import requests
        import json
        
        # Try the public API endpoint (may or may not work)
        url = f"https://i.instagram.com/api/v1/users/web_profile_info/?username={username}"
        
        headers = {
            'User-Agent': 'Instagram 76.0.0.15.395 Android (24/7.0; 640dpi; 1440x2560; samsung; SM-G930F; herolte; samsungexynos8890; en_US; 138226743)',
            'Accept': '*/*',
            'Accept-Language': 'en-US',
            'X-IG-App-ID': '936619743392459',
        }
        
        response = requests.get(url, headers=headers, timeout=15)
        
        if response.status_code != 200:
            raise Exception(f"API returned {response.status_code}")
        
        data = response.json()
        user = data['data']['user']
        
        profile_data = {
            'username': username,
            'full_name': user.get('full_name', username),
            'bio': user.get('biography', ''),
            'followers': user['edge_followed_by']['count'],
            'following': user['edge_follow']['count'],
            'posts': user['edge_owner_to_timeline_media']['count'],
            'profile_pic_url': user.get('profile_pic_url_hd', ''),
            'is_verified': user.get('is_verified', False),
            'is_business': user.get('is_business_account', False),
            'is_private': user.get('is_private', False),
            'account_age_days': 365,
            'scrape_method': 'api'
        }
        
        if profile_data['posts'] > 0:
            profile_data['engagement_ratio'] = profile_data['followers'] / profile_data['posts']
        else:
            profile_data['engagement_ratio'] = 0
        
        profile_data['has_profile_pic'] = bool(profile_data['profile_pic_url'])
        
        print(f"[SUCCESS] API scraped {username}: {profile_data['followers']} followers")
        return profile_data
    
    def _calculate_account_age(self, user_info):
        """Calculate approximate account age"""
        # This is an approximation since Instagram doesn't provide creation date
        # You could improve this by checking oldest posts
        return 365  # Default to 1 year
    
    def _get_fallback_data(self, username):
        """Return fallback data when all methods fail"""
        return {
            'username': username,
            'full_name': username,
            'bio': 'Could not retrieve bio',
            'followers': 0,
            'following': 0,
            'posts': 0,
            'profile_pic_url': '',
            'is_verified': False,
            'is_business': False,
            'is_private': True,
            'account_age_days': 365,
            'engagement_ratio': 0,
            'has_profile_pic': False,
            'scrape_method': 'fallback',
            'error': 'Failed to scrape profile. Instagram may be blocking access or profile may be private.'
        }