# ============================================
# File: app/scrapers/instagram_scraper.py (PRODUCTION VERSION)
# ============================================
# This version works better on cloud platforms like Render

"""
Instagram Scraper - Cloud-optimized version for production
"""

import os
import time
import json
from datetime import datetime
import requests

class InstagramScraper:
    """Scrape Instagram profiles - production optimized"""
    
    def __init__(self):
        """Initialize scraper"""
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': '*/*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Referer': 'https://www.instagram.com/',
            'X-Requested-With': 'XMLHttpRequest',
        })
        self.instagrapi_client = None
        self._try_init_instagrapi()
    
    def _try_init_instagrapi(self):
        """Try to initialize instagrapi if credentials available"""
        try:
            from instagrapi import Client
            from instagrapi.exceptions import LoginRequired
            
            username = os.getenv('INSTAGRAM_USERNAME')
            password = os.getenv('INSTAGRAM_PASSWORD')
            
            if username and password:
                try:
                    self.instagrapi_client = Client()
                    self.instagrapi_client.login(username, password)
                    print(f"[OK] Logged in to Instagram as {username}")
                    return True
                except Exception as e:
                    print(f"[WARNING] Login failed: {str(e)}")
                    self.instagrapi_client = None
                    return False
            else:
                print("[INFO] No Instagram credentials - using public methods")
                return False
                
        except ImportError:
            print("[INFO] instagrapi not available - using public methods")
            return False
    
    def scrape_profile(self, username):
        """
        Scrape Instagram profile with multiple fallback methods
        """
        username = username.strip('@').strip()
        print(f"[INFO] Scraping profile: {username}")
        
        # Method 1: Instagrapi (if logged in)
        if self.instagrapi_client:
            try:
                print("[TRY] Method 1: Instagrapi API")
                return self._scrape_with_instagrapi(username)
            except Exception as e:
                print(f"[FAIL] Instagrapi: {str(e)}")
        
        # Method 2: Public Instagram API
        try:
            print("[TRY] Method 2: Public Instagram API")
            return self._scrape_public_api(username)
        except Exception as e:
            print(f"[FAIL] Public API: {str(e)}")
        
        # Method 3: Web scraping via proxy service
        try:
            print("[TRY] Method 3: Third-party API")
            return self._scrape_via_proxy(username)
        except Exception as e:
            print(f"[FAIL] Proxy API: {str(e)}")
        
        # Method 4: Alternative endpoints
        try:
            print("[TRY] Method 4: Alternative endpoint")
            return self._scrape_alternative(username)
        except Exception as e:
            print(f"[FAIL] Alternative: {str(e)}")
        
        # All methods failed
        print(f"[ERROR] All scraping methods failed for {username}")
        return self._get_fallback_data(username)
    
    def _scrape_with_instagrapi(self, username):
        """Scrape using instagrapi (most reliable if logged in)"""
        user_id = self.instagrapi_client.user_id_from_username(username)
        user_info = self.instagrapi_client.user_info(user_id)
        
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
            'account_age_days': 365,
            'engagement_ratio': user_info.follower_count / max(user_info.media_count, 1),
            'has_profile_pic': bool(user_info.profile_pic_url),
            'scrape_method': 'instagrapi'
        }
        
        print(f"[SUCCESS] Instagrapi: {profile_data['followers']} followers")
        return profile_data
    
    def _scrape_public_api(self, username):
        """Scrape using public Instagram endpoints"""
        
        # Try Instagram's public web profile info endpoint
        url = f"https://www.instagram.com/api/v1/users/web_profile_info/?username={username}"
        
        headers = {
            'User-Agent': 'Instagram 76.0.0.15.395 Android',
            'X-IG-App-ID': '936619743392459',
        }
        
        response = self.session.get(url, headers=headers, timeout=15)
        
        if response.status_code == 200:
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
                'engagement_ratio': user['edge_followed_by']['count'] / max(user['edge_owner_to_timeline_media']['count'], 1),
                'has_profile_pic': bool(user.get('profile_pic_url_hd')),
                'scrape_method': 'public-api'
            }
            
            print(f"[SUCCESS] Public API: {profile_data['followers']} followers")
            return profile_data
        
        raise Exception(f"API returned status {response.status_code}")
    
    def _scrape_via_proxy(self, username):
        """Scrape via third-party proxy service (free alternatives)"""
        
        # Use a public Instagram viewer API
        # Note: These are free public services that may have rate limits
        
        # Try storiesig.net API (public Instagram viewer)
        try:
            url = f"https://storiesig.net/api/profile/{username}"
            response = self.session.get(url, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                
                if 'user' in data:
                    user = data['user']
                    
                    profile_data = {
                        'username': username,
                        'full_name': user.get('fullName', username),
                        'bio': user.get('biography', ''),
                        'followers': user.get('followers', 0),
                        'following': user.get('following', 0),
                        'posts': user.get('postsCount', 0),
                        'profile_pic_url': user.get('profilePicUrl', ''),
                        'is_verified': user.get('isVerified', False),
                        'is_business': user.get('isBusiness', False),
                        'is_private': user.get('isPrivate', False),
                        'account_age_days': 365,
                        'engagement_ratio': user.get('followers', 0) / max(user.get('postsCount', 1), 1),
                        'has_profile_pic': bool(user.get('profilePicUrl')),
                        'scrape_method': 'proxy-api'
                    }
                    
                    print(f"[SUCCESS] Proxy API: {profile_data['followers']} followers")
                    return profile_data
        except:
            pass
        
        raise Exception("Proxy API failed")
    
    def _scrape_alternative(self, username):
        """Try alternative public endpoints"""
        
        # Try direct profile page scraping
        try:
            url = f"https://www.instagram.com/{username}/?__a=1&__d=dis"
            
            response = self.session.get(url, timeout=15)
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    
                    if 'graphql' in data and 'user' in data['graphql']:
                        user = data['graphql']['user']
                        
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
                            'engagement_ratio': user['edge_followed_by']['count'] / max(user['edge_owner_to_timeline_media']['count'], 1),
                            'has_profile_pic': bool(user.get('profile_pic_url_hd')),
                            'scrape_method': 'alternative'
                        }
                        
                        print(f"[SUCCESS] Alternative: {profile_data['followers']} followers")
                        return profile_data
                except:
                    pass
        except:
            pass
        
        raise Exception("Alternative endpoint failed")
    
    def _get_fallback_data(self, username):
        """Return fallback when all methods fail"""
        print(f"[FALLBACK] Using simulated data for {username}")
        
        return {
            'username': username,
            'full_name': username,
            'bio': 'Unable to retrieve bio - Instagram may be blocking access',
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
            'error': 'Could not retrieve real data. Instagram may be blocking the server IP address or profile is private. Try adding Instagram login credentials to environment variables.'
        }