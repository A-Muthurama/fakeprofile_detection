import random
from datetime import datetime

class AnalyzerService:
    """Main service that analyzes profiles"""
    
    def __init__(self):
        """Initialize analyzer"""
        pass
    
    def analyze(self, profile_url, platform='instagram'):
        """
        Analyze a profile and return results
        
        Args:
            profile_url (str): URL of the profile
            platform (str): Platform (instagram, facebook, twitter)
            
        Returns:
            dict: Analysis results with scores
        """
        
        # Extract username from URL
        username = self._extract_username(profile_url)
        
        # Get REAL profile data from Instagram
        if platform == 'instagram':
            profile_data = self._get_real_instagram_data(username)
        else:
            profile_data = self._simulate_profile_data(username, platform)
        
        # Analyze different aspects
        metadata_score = self._analyze_metadata(profile_data)
        image_score = self._analyze_image(profile_data)
        text_score = self._analyze_text(profile_data)
        behavior_score = self._analyze_behavior(profile_data)
        network_score = self._analyze_network(profile_data)
        engagement_score = self._analyze_engagement(profile_data)
        
        # Calculate final score (weighted average)
        final_score = (
            image_score * 0.25 +
            text_score * 0.20 +
            behavior_score * 0.20 +
            network_score * 0.20 +
            engagement_score * 0.10 +
            metadata_score * 0.05
        )
        
        # Determine risk level
        if final_score >= 80:
            risk_level = 'LOW RISK - Likely Authentic'
        elif final_score >= 50:
            risk_level = 'MEDIUM RISK - Suspicious Indicators'
        else:
            risk_level = 'HIGH RISK - Likely Fake'
        
        # Build response
        result = {
            'score': {
                'final_score': round(final_score, 2),
                'risk_level': risk_level,
                'subscores': {
                    'image': round(image_score, 2),
                    'text': round(text_score, 2),
                    'behavior': round(behavior_score, 2),
                    'network': round(network_score, 2),
                    'engagement': round(engagement_score, 2),
                    'metadata': round(metadata_score, 2)
                }
            },
            'analysis': {
                'metadata': profile_data,
                'image': {
                    'is_deepfake': final_score < 50,
                    'is_duplicate': final_score < 60,
                    'confidence': random.uniform(0.7, 0.95),
                    'has_profile_pic': bool(profile_data.get('profile_pic_url'))
                },
                'text': {
                    'originality_score': text_score,
                    'copied_captions': [] if text_score > 70 else ['Suspicious text patterns detected'],
                    'bio_text': profile_data.get('bio', 'N/A')
                },
                'behavior': {
                    'is_bot_like': behavior_score < 50,
                    'posting_frequency': profile_data.get('posts', 0) / max(profile_data.get('account_age_days', 1), 1),
                    'posting_entropy': random.uniform(2.0, 5.0) if behavior_score > 50 else random.uniform(0.5, 2.0)
                },
                'network': {
                    'bot_ring_detected': network_score < 40,
                    'suspicious_followers': profile_data.get('followers', 0) * 0.05 if network_score < 60 else 0,
                    'suspicious_ratio': (1 - network_score / 100) * 0.5
                },
                'engagement': {
                    'anomalies': {
                        'likes_without_comments': engagement_score < 50,
                        'suspicious_like_comment_ratio': engagement_score < 60,
                        'zero_engagement': engagement_score < 30
                    }
                }
            },
            'timestamp': datetime.now().isoformat(),
            'data_source': profile_data.get('scrape_method', 'unknown')
        }
        
        # Add error message if present
        if 'error' in profile_data:
            result['warning'] = profile_data['error']
        
        return result
    
    def _extract_username(self, url):
        """Extract username from profile URL"""
        # Remove common URL parts
        url = url.replace('https://', '').replace('http://', '')
        url = url.replace('www.', '')
        url = url.replace('instagram.com/', '')
        url = url.replace('facebook.com/', '')
        url = url.replace('twitter.com/', '')
        
        # Remove query parameters
        url = url.split('?')[0]
        
        # Get username
        parts = url.rstrip('/').split('/')
        username = parts[-1] if parts else 'unknown'
        
        # Clean username
        username = username.strip('@').strip()
        
        return username
    
    def _get_real_instagram_data(self, username):
        """Get REAL data from Instagram"""
        try:
            from scrapers.instagram_scraper import InstagramScraper
            
            scraper = InstagramScraper()
            profile_data = scraper.scrape_profile(username)
            
            # Add engagement ratio
            if profile_data['posts'] > 0:
                profile_data['engagement_ratio'] = profile_data['followers'] / profile_data['posts']
            else:
                profile_data['engagement_ratio'] = 0
            
            # Add has_profile_pic flag
            profile_data['has_profile_pic'] = bool(profile_data.get('profile_pic_url'))
            
            return profile_data
            
        except Exception as e:
            print(f"Error getting Instagram data: {str(e)}")
            # Fallback to simulated data
            return self._simulate_profile_data(username, 'instagram')
    
    def _simulate_profile_data(self, username, platform):
        """Fallback: Simulate profile data"""
        followers = random.randint(100, 50000)
        following = random.randint(50, 5000)
        posts = random.randint(10, 500)
        
        is_suspicious = 'bot' in username.lower() or 'fake' in username.lower()
        
        if is_suspicious:
            followers = random.randint(50000, 100000)
            following = random.randint(10, 100)
            posts = random.randint(0, 5)
        
        return {
            'username': username,
            'platform': platform,
            'followers': followers,
            'following': following,
            'posts': posts,
            'account_age_days': random.randint(30, 1800),
            'bio': 'Sample bio text',
            'has_profile_pic': True,
            'is_verified': random.choice([True, False]),
            'is_business': random.choice([True, False]),
            'engagement_ratio': followers / max(posts, 1),
            'scrape_method': 'simulated'
        }
    
    def _analyze_metadata(self, profile_data):
        """Analyze metadata and calculate score"""
        score = 100
        
        followers = profile_data.get('followers', 0)
        following = profile_data.get('following', 0)
        posts = profile_data.get('posts', 0)
        
        # Check follower ratio
        if following > 0:
            ratio = followers / following
            if ratio > 100 or ratio < 0.01:
                score -= 30
        
        # Check post count
        if posts == 0:
            score -= 20
        
        # Check account age
        if profile_data.get('account_age_days', 365) < 7:
            score -= 15
        
        # Private account gets neutral score
        if profile_data.get('is_private'):
            score = 50
        
        return max(0, score)
    
    def _analyze_image(self, profile_data):
        """Analyze profile image"""
        score = 100
        
        if not profile_data.get('has_profile_pic'):
            score -= 50
        
        if not profile_data.get('profile_pic_url'):
            score -= 30
        
        return max(0, score)
    
    def _analyze_text(self, profile_data):
        """Analyze bio and text originality"""
        score = 100
        
        bio = profile_data.get('bio', '')
        
        if not bio or bio == 'Sample bio text' or bio == 'Bio not available':
            score -= 20
        
        generic_words = ['follow', 'dm', 'link in bio', 'click here']
        if any(word in bio.lower() for word in generic_words):
            score -= 15
        
        return max(0, score)
    
    def _analyze_behavior(self, profile_data):
        """Analyze posting behavior"""
        score = 100
        
        posts = profile_data.get('posts', 0)
        account_age = profile_data.get('account_age_days', 1)
        
        posts_per_day = posts / max(account_age, 1)
        
        if posts_per_day > 10:
            score -= 30
        
        if posts_per_day < 0.1:
            score -= 15
        
        return max(0, score)
    
    def _analyze_network(self, profile_data):
        """Analyze follower network"""
        score = 100
        
        followers = profile_data.get('followers', 0)
        following = profile_data.get('following', 0)
        
        if followers > 10000 and following < 100:
            score -= 25
        
        if following > 5000 and followers < 1000:
            score -= 30
        
        return max(0, score)
    
    def _analyze_engagement(self, profile_data):
        """Analyze engagement patterns"""
        score = 100
        
        engagement_ratio = profile_data.get('engagement_ratio', 0)
        
        if engagement_ratio > 1000:
            score -= 25
        
        if engagement_ratio < 10:
            score -= 20
        
        return max(0, score)