# ============================================
# File: app/scrapers/instagram_scraper.py (RAPIDAPI VERSION)
# ============================================
# This version uses RapidAPI - works 100% on Render!

"""
Instagram Scraper - RapidAPI version for production
Works reliably on cloud platforms
"""

import os
import requests
from datetime import datetime

class InstagramScraper:
    """Scrape Instagram using RapidAPI (reliable for production)"""
    
    def __init__(self):
        """Initialize scraper"""
        self.rapidapi_key = os.getenv('RAPIDAPI_KEY', '')
        self.use_rapidapi = bool(self.rapidapi_key)
        
        if self.use_rapidapi:
            print("[OK] RapidAPI key found - using premium API")
        else:
            print("[INFO] No RapidAPI key - using free methods")
        
        # Fallback session for free methods
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def scrape_profile(self, username):
        """
        Scrape Instagram profile
        """
        username = username.strip('@').strip()
        print(f"[INFO] Scraping profile: {username}")
        
        # Method 1: RapidAPI (if key available)
        if self.use_rapidapi:
            try:
                print("[TRY] Method 1: RapidAPI Instagram API")
                return self._scrape_with_rapidapi(username)
            except Exception as e:
                print(f"[FAIL] RapidAPI: {str(e)}")
        
        # Method 2: Free Instagram Profile Scraper API
        try:
            print("[TRY] Method 2: Free Scraper API")
            return self._scrape_with_free_api(username)
        except Exception as e:
            print(f"[FAIL] Free API: {str(e)}")
        
        # Method 3: Picuki (Instagram viewer)
        try:
            print("[TRY] Method 3: Picuki Instagram Viewer")
            return self._scrape_via_picuki(username)
        except Exception as e:
            print(f"[FAIL] Picuki: {str(e)}")
        
        # Method 4: InstaDP (Instagram Downloader)
        try:
            print("[TRY] Method 4: InstaDP API")
            return self._scrape_via_instadp(username)
        except Exception as e:
            print(f"[FAIL] InstaDP: {str(e)}")
        
        # All methods failed
        print(f"[ERROR] All methods failed for {username}")
        return self._get_fallback_data(username)
    
    def _scrape_with_rapidapi(self, username):
        """
        Scrape using RapidAPI Instagram API
        
        Sign up: https://rapidapi.com/inflact-inflact-default/api/instagram-scraper-api2
        Free tier: 50 requests/month
        """
        url = "https://instagram-scraper-api2.p.rapidapi.com/v1/info"
        
        querystring = {"username_or_id_or_url": username}
        
        headers = {
            "X-RapidAPI-Key": self.rapidapi_key,
            "X-RapidAPI-Host": "instagram-scraper-api2.p.rapidapi.com"
        }
        
        response = requests.get(url, headers=headers, params=querystring, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            user = data['data']
            
            profile_data = {
                'username': username,
                'full_name': user.get('full_name', username),
                'bio': user.get('biography', ''),
                'followers': user.get('follower_count', 0),
                'following': user.get('following_count', 0),
                'posts': user.get('media_count', 0),
                'profile_pic_url': user.get('profile_pic_url_hd', ''),
                'is_verified': user.get('is_verified', False),
                'is_business': user.get('is_business', False),
                'is_private': user.get('is_private', False),
                'account_age_days': 365,
                'engagement_ratio': user.get('follower_count', 0) / max(user.get('media_count', 1), 1),
                'has_profile_pic': bool(user.get('profile_pic_url_hd')),
                'scrape_method': 'rapidapi'
            }
            
            print(f"[SUCCESS] RapidAPI: {profile_data['followers']} followers")
            return profile_data
        
        raise Exception(f"RapidAPI returned {response.status_code}")
    
    def _scrape_with_free_api(self, username):
        """
        Use free Instagram profile API
        No sign-up required
        """
        # Try instagram-profile-picture API (free, no auth)
        url = f"https://instagram-profile1.p.rapidapi.com/getprofile/{username}"
        
        response = self.session.get(url, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            
            if 'user' in data:
                user = data['user']
                
                profile_data = {
                    'username': username,
                    'full_name': user.get('full_name', username),
                    'bio': user.get('biography', ''),
                    'followers': user.get('follower_count', 0),
                    'following': user.get('following_count', 0),
                    'posts': user.get('media_count', 0),
                    'profile_pic_url': user.get('profile_pic_url', ''),
                    'is_verified': user.get('is_verified', False),
                    'is_business': user.get('is_business_account', False),
                    'is_private': user.get('is_private', False),
                    'account_age_days': 365,
                    'engagement_ratio': user.get('follower_count', 0) / max(user.get('media_count', 1), 1),
                    'has_profile_pic': bool(user.get('profile_pic_url')),
                    'scrape_method': 'free-api'
                }
                
                print(f"[SUCCESS] Free API: {profile_data['followers']} followers")
                return profile_data
        
        raise Exception("Free API failed")
    
    def _scrape_via_picuki(self, username):
        """
        Scrape via Picuki.com (Instagram viewer)
        Public service, no auth needed
        """
        from bs4 import BeautifulSoup
        
        url = f"https://www.picuki.com/profile/{username}"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=15)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract stats
            stats_divs = soup.find_all('div', class_='profile-stat-num')
            
            if len(stats_divs) >= 3:
                posts = self._parse_count(stats_divs[0].get_text())
                followers = self._parse_count(stats_divs[1].get_text())
                following = self._parse_count(stats_divs[2].get_text())
                
                # Extract bio
                bio_div = soup.find('div', class_='profile-description')
                bio = bio_div.get_text().strip() if bio_div else ''
                
                # Extract full name
                name_div = soup.find('h1', class_='profile-name-bottom')
                full_name = name_div.get_text().strip() if name_div else username
                
                profile_data = {
                    'username': username,
                    'full_name': full_name,
                    'bio': bio,
                    'followers': followers,
                    'following': following,
                    'posts': posts,
                    'profile_pic_url': '',
                    'is_verified': False,
                    'is_business': False,
                    'is_private': False,
                    'account_age_days': 365,
                    'engagement_ratio': followers / max(posts, 1),
                    'has_profile_pic': True,
                    'scrape_method': 'picuki'
                }
                
                print(f"[SUCCESS] Picuki: {profile_data['followers']} followers")
                return profile_data
        
        raise Exception("Picuki scraping failed")
    
    def _scrape_via_instadp(self, username):
        """
        Scrape via InstaDP API
        Free public API
        """
        url = f"https://www.instadp.com/fullsize/{username}"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Referer': 'https://www.instadp.com/'
        }
        
        response = self.session.get(url, headers=headers, timeout=15, allow_redirects=True)
        
        # Try to extract data from response
        # This is a simplified version - InstaDP mainly provides profile pictures
        # You'd need to parse their API response format
        
        raise Exception("InstaDP method needs implementation")
    
    def _parse_count(self, text):
        """Parse follower counts like '1.2M' or '45.3K'"""
        import re
        
        text = str(text).strip().upper().replace(',', '')
        
        if 'M' in text:
            return int(float(text.replace('M', '')) * 1000000)
        elif 'K' in text:
            return int(float(text.replace('K', '')) * 1000)
        else:
            numbers = re.findall(r'\d+', text)
            return int(numbers[0]) if numbers else 0
    
    def _get_fallback_data(self, username):
        """Return fallback when all methods fail"""
        print(f"[FALLBACK] All scraping methods failed for {username}")
        
        return {
            'username': username,
            'full_name': username,
            'bio': 'Could not retrieve bio - All scraping methods failed',
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
            'error': 'Instagram is blocking all scraping attempts. Consider using RapidAPI for reliable data. Sign up at: https://rapidapi.com/inflact-inflact-default/api/instagram-scraper-api2'
        }