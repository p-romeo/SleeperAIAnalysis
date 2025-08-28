"""Sleeper API wrapper with caching and error handling."""

import json
import time
from pathlib import Path
from typing import Dict, List, Optional, Any
import requests
from requests.exceptions import RequestException, Timeout

from src.utils.logger import get_logger
from src.utils.config import AppConfig

logger = get_logger(__name__)


class SleeperAPIError(Exception):
    """Custom exception for Sleeper API errors."""
    pass


class SleeperAPI:
    """Handles all Sleeper API interactions with caching and error handling."""
    
    BASE_URL = "https://api.sleeper.app/v1"
    CACHE_DIR = Path.home() / ".sleeper_optimizer" / "cache"
    
    def __init__(self, config: AppConfig):
        """
        Initialize Sleeper API wrapper.
        
        Args:
            config: Application configuration
        """
        self.config = config
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'SleeperAIOptimizer/1.0.0'
        })
        
        # Ensure cache directory exists
        self.CACHE_DIR.mkdir(parents=True, exist_ok=True)
        
        logger.info("Sleeper API wrapper initialized")
    
    def _make_request(
        self, 
        endpoint: str, 
        params: Optional[Dict[str, Any]] = None,
        retries: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Make HTTP request with retry logic.
        
        Args:
            endpoint: API endpoint
            params: Query parameters
            retries: Number of retries (uses config default if None)
            
        Returns:
            API response data
            
        Raises:
            SleeperAPIError: If request fails after retries
        """
        if retries is None:
            retries = self.config.max_retries
        
        url = f"{self.BASE_URL}{endpoint}"
        
        for attempt in range(retries + 1):
            try:
                logger.debug(f"Making request to {url} (attempt {attempt + 1})")
                
                response = self.session.get(
                    url, 
                    params=params, 
                    timeout=self.config.request_timeout
                )
                
                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 429:
                    # Rate limited
                    wait_time = int(response.headers.get('Retry-After', 60))
                    logger.warning(f"Rate limited, waiting {wait_time} seconds")
                    time.sleep(wait_time)
                    continue
                else:
                    response.raise_for_status()
                    
            except Timeout:
                logger.warning(f"Request timeout (attempt {attempt + 1})")
                if attempt < retries:
                    time.sleep(2 ** attempt)  # Exponential backoff
                    continue
                raise SleeperAPIError(f"Request timeout after {retries + 1} attempts")
                
            except RequestException as e:
                logger.warning(f"Request failed (attempt {attempt + 1}): {e}")
                if attempt < retries:
                    time.sleep(2 ** attempt)
                    continue
                raise SleeperAPIError(f"Request failed after {retries + 1} attempts: {e}")
        
        raise SleeperAPIError(f"Request failed after {retries + 1} attempts")
    
    def _get_cache_path(self, key: str) -> Path:
        """Get cache file path for a given key."""
        return self.CACHE_DIR / f"{key}.json"
    
    def _is_cache_valid(self, cache_path: Path) -> bool:
        """Check if cache file is still valid."""
        if not cache_path.exists():
            return False
        
        if not self.config.cache_enabled:
            return False
        
        # Check if cache is within duration limit
        age_hours = (time.time() - cache_path.stat().st_mtime) / 3600
        return age_hours < self.config.cache_duration_hours
    
    def _save_cache(self, key: str, data: Any) -> None:
        """Save data to cache."""
        if not self.config.cache_enabled:
            return
        
        try:
            cache_path = self._get_cache_path(key)
            with open(cache_path, 'w') as f:
                json.dump(data, f, indent=2)
            logger.debug(f"Data cached to {cache_path}")
        except Exception as e:
            logger.warning(f"Failed to cache data: {e}")
    
    def _load_cache(self, key: str) -> Optional[Any]:
        """Load data from cache if valid."""
        if not self.config.cache_enabled:
            return None
        
        cache_path = self._get_cache_path(key)
        if not self._is_cache_valid(cache_path):
            return None
        
        try:
            with open(cache_path, 'r') as f:
                data = json.load(f)
            logger.debug(f"Data loaded from cache: {cache_path}")
            return data
        except Exception as e:
            logger.warning(f"Failed to load cache: {e}")
            return None
    
    def get_user(self, username: str) -> Optional[Dict[str, Any]]:
        """
        Get user data from username.
        
        Args:
            username: Sleeper username
            
        Returns:
            User data or None if not found
        """
        try:
            cache_key = f"user_{username}"
            cached = self._load_cache(cache_key)
            if cached:
                return cached
            
            data = self._make_request(f"/user/{username}")
            self._save_cache(cache_key, data)
            return data
            
        except SleeperAPIError as e:
            logger.error(f"Failed to get user {username}: {e}")
            return None
    
    def get_user_leagues(self, user_id: str, season: str = "2024") -> List[Dict[str, Any]]:
        """
        Get all leagues for a user.
        
        Args:
            user_id: User ID
            season: NFL season
            
        Returns:
            List of leagues
        """
        try:
            cache_key = f"leagues_{user_id}_{season}"
            cached = self._load_cache(cache_key)
            if cached:
                return cached
            
            data = self._make_request(f"/user/{user_id}/leagues/nfl/{season}")
            self._save_cache(cache_key, data)
            return data
            
        except SleeperAPIError as e:
            logger.error(f"Failed to get leagues for user {user_id}: {e}")
            return []
    
    def get_league(self, league_id: str) -> Optional[Dict[str, Any]]:
        """
        Get league details.
        
        Args:
            league_id: League ID
            
        Returns:
            League data or None if not found
        """
        try:
            cache_key = f"league_{league_id}"
            cached = self._load_cache(cache_key)
            if cached:
                return cached
            
            data = self._make_request(f"/league/{league_id}")
            self._save_cache(cache_key, data)
            return data
            
        except SleeperAPIError as e:
            logger.error(f"Failed to get league {league_id}: {e}")
            return None
    
    def get_rosters(self, league_id: str) -> List[Dict[str, Any]]:
        """
        Get all rosters in a league.
        
        Args:
            league_id: League ID
            
        Returns:
            List of rosters
        """
        try:
            cache_key = f"rosters_{league_id}"
            cached = self._load_cache(cache_key)
            if cached:
                return cached
            
            data = self._make_request(f"/league/{league_id}/rosters")
            self._save_cache(cache_key, data)
            return data
            
        except SleeperAPIError as e:
            logger.error(f"Failed to get rosters for league {league_id}: {e}")
            return []
    
    def get_users(self, league_id: str) -> List[Dict[str, Any]]:
        """
        Get all users in a league.
        
        Args:
            league_id: League ID
            
        Returns:
            List of users
        """
        try:
            cache_key = f"users_{league_id}"
            cached = self._load_cache(cache_key)
            if cached:
                return cached
            
            data = self._make_request(f"/league/{league_id}/users")
            self._save_cache(cache_key, data)
            return data
            
        except SleeperAPIError as e:
            logger.error(f"Failed to get users for league {league_id}: {e}")
            return []
    
    def get_matchups(self, league_id: str, week: int) -> List[Dict[str, Any]]:
        """
        Get matchups for a specific week.
        
        Args:
            league_id: League ID
            week: NFL week
            
        Returns:
            List of matchups
        """
        try:
            cache_key = f"matchups_{league_id}_week_{week}"
            cached = self._load_cache(cache_key)
            if cached:
                return cached
            
            data = self._make_request(f"/league/{league_id}/matchups/{week}")
            self._save_cache(cache_key, data)
            return data
            
        except SleeperAPIError as e:
            logger.error(f"Failed to get matchups for league {league_id} week {week}: {e}")
            return []
    
    def get_players(self) -> Dict[str, Any]:
        """
        Get all NFL players (large dataset).
        
        Returns:
            Player data dictionary
        """
        try:
            cache_key = "players_nfl"
            cached = self._load_cache(cache_key)
            if cached:
                return cached
            
            logger.info("Fetching player data from Sleeper API...")
            data = self._make_request("/players/nfl")
            self._save_cache(cache_key, data)
            logger.info(f"Player data cached ({len(data)} players)")
            return data
            
        except SleeperAPIError as e:
            logger.error(f"Failed to get players: {e}")
            return {}
    
    def get_trending_players(
        self, 
        lookback_hours: int = 24, 
        limit: int = 25
    ) -> List[Dict[str, Any]]:
        """
        Get trending players.
        
        Args:
            lookback_hours: Hours to look back
            limit: Maximum number of players
            
        Returns:
            List of trending players
        """
        try:
            cache_key = f"trending_{lookback_hours}h_{limit}"
            cached = self._load_cache(cache_key)
            if cached:
                return cached
            
            params = {
                "lookback_hours": lookback_hours,
                "limit": limit
            }
            
            data = self._make_request("/players/nfl/trending/add", params)
            self._save_cache(cache_key, data)
            return data
            
        except SleeperAPIError as e:
            logger.error(f"Failed to get trending players: {e}")
            return []
    
    def clear_cache(self) -> None:
        """Clear all cached data."""
        try:
            for cache_file in self.CACHE_DIR.glob("*.json"):
                cache_file.unlink()
            logger.info("Cache cleared")
        except Exception as e:
            logger.error(f"Failed to clear cache: {e}")
    
    def get_cache_size(self) -> int:
        """Get total size of cache in bytes."""
        try:
            total_size = 0
            for cache_file in self.CACHE_DIR.glob("*.json"):
                total_size += cache_file.stat().st_size
            return total_size
        except Exception:
            return 0
