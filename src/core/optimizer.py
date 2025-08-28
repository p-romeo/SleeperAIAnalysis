"""Main lineup optimizer that orchestrates the analysis process."""

import time
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime

from src.api.sleeper import SleeperAPI
from src.api.ai_providers import AIAnalyzer, AnalysisResult
from src.core.analyzer import LineupAnalyzer
from src.utils.config import ConfigManager, AppConfig
from src.utils.logger import get_logger

logger = get_logger(__name__)


class LineupOptimizer:
    """Main application class that orchestrates lineup optimization."""
    
    def __init__(self, config_dir: Optional[str] = None):
        """
        Initialize lineup optimizer.
        
        Args:
            config_dir: Optional custom config directory
        """
        self.config_manager = ConfigManager()
        self.config: Optional[AppConfig] = None
        self.sleeper_api: Optional[SleeperAPI] = None
        self.ai_analyzer: Optional[AIAnalyzer] = None
        self.lineup_analyzer: Optional[LineupAnalyzer] = None
        
        # User data
        self.user_data: Optional[Dict[str, Any]] = None
        self.selected_league: Optional[Dict[str, Any]] = None
        
        logger.info("Lineup Optimizer initialized")
    
    def initialize(self, password: str) -> bool:
        """
        Initialize the optimizer with configuration.
        
        Args:
            password: Password for config decryption
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Load configuration
            self.config = self.config_manager.load_config(password)
            if not self.config:
                logger.error("Failed to load configuration")
                return False
            
            # Validate configuration
            if not self.config_manager.validate_config(self.config):
                logger.error("Invalid configuration")
                return False
            
            # Initialize components
            self.sleeper_api = SleeperAPI(self.config)
            self.ai_analyzer = AIAnalyzer(self.config)
            self.lineup_analyzer = LineupAnalyzer(self.sleeper_api, self.ai_analyzer, self.config)
            
            logger.info("Lineup Optimizer initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize optimizer: {e}")
            return False
    
    def get_user_info(self, username: str) -> Optional[Dict[str, Any]]:
        """
        Get user information from Sleeper.
        
        Args:
            username: Sleeper username
            
        Returns:
            User data or None if failed
        """
        try:
            if not self.sleeper_api:
                logger.error("Sleeper API not initialized")
                return None
            
            user_data = self.sleeper_api.get_user(username)
            if user_data:
                self.user_data = user_data
                logger.info(f"User info retrieved for {username}")
                return user_data
            else:
                logger.error(f"User not found: {username}")
                return None
                
        except Exception as e:
            logger.error(f"Failed to get user info: {e}")
            return None
    
    def get_user_leagues(self, season: str = "2024") -> List[Dict[str, Any]]:
        """
        Get leagues for the current user.
        
        Args:
            season: NFL season
            
        Returns:
            List of leagues
        """
        try:
            if not self.sleeper_api or not self.user_data:
                logger.error("Sleeper API or user data not initialized")
                return []
            
            user_id = self.user_data.get('user_id')
            if not user_id:
                logger.error("No user ID found")
                return []
            
            leagues = self.sleeper_api.get_user_leagues(user_id, season)
            logger.info(f"Retrieved {len(leagues)} leagues for user")
            return leagues
            
        except Exception as e:
            logger.error(f"Failed to get user leagues: {e}")
            return []
    
    def select_league(self, league_index: int, leagues: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """
        Select a league by index.
        
        Args:
            league_index: Index of league to select
            leagues: List of available leagues
            
        Returns:
            Selected league or None if invalid
        """
        try:
            if not (0 <= league_index < len(leagues)):
                logger.error(f"Invalid league index: {league_index}")
                return None
            
            self.selected_league = leagues[league_index]
            logger.info(f"Selected league: {self.selected_league.get('name', 'Unknown')}")
            return self.selected_league
            
        except Exception as e:
            logger.error(f"Failed to select league: {e}")
            return None
    
    def get_current_nfl_week(self) -> int:
        """
        Get the current NFL week.
        
        Returns:
            Current NFL week number
        """
        try:
            # This is a simplified implementation
            # In production, you'd want to calculate this based on actual NFL schedule
            current_date = datetime.now()
            
            # NFL season typically starts first Thursday in September
            # This is a rough approximation
            if current_date.month < 9:
                return 0  # Off-season
            elif current_date.month == 9:
                return max(1, (current_date.day - 1) // 7 + 1)
            elif current_date.month <= 12:
                return (current_date.month - 9) * 4 + (current_date.day - 1) // 7 + 1
            else:
                return 18  # End of regular season
            
        except Exception as e:
            logger.error(f"Failed to calculate NFL week: {e}")
            return 10  # Fallback to week 10
    
    def analyze_current_week(self) -> Optional[AnalysisResult]:
        """
        Analyze lineup for the current week.
        
        Returns:
            Analysis result or None if failed
        """
        if not self.selected_league:
            logger.error("No league selected")
            return None
        
        current_week = self.get_current_nfl_week()
        return self.analyze_week(current_week)
    
    def analyze_week(self, week: int) -> Optional[AnalysisResult]:
        """
        Analyze lineup for a specific week.
        
        Args:
            week: NFL week number
            
        Returns:
            Analysis result or None if failed
        """
        try:
            if not self.lineup_analyzer or not self.user_data or not self.selected_league:
                logger.error("Required components not initialized")
                return None
            
            league_id = self.selected_league.get('league_id')
            user_id = self.user_data.get('user_id')
            
            if not league_id or not user_id:
                logger.error("Missing league ID or user ID")
                return None
            
            logger.info(f"Starting analysis for week {week}")
            
            result = self.lineup_analyzer.analyze_week(league_id, user_id, week)
            
            if result:
                logger.info(f"Week {week} analysis completed successfully")
                return result
            else:
                logger.error(f"Week {week} analysis failed")
                return None
                
        except Exception as e:
            logger.error(f"Failed to analyze week {week}: {e}")
            return None
    
    def get_trending_players(self, lookback_hours: int = 24, limit: int = 25) -> List[Dict[str, Any]]:
        """
        Get trending players.
        
        Args:
            lookback_hours: Hours to look back
            limit: Maximum number of players
            
        Returns:
            List of trending players
        """
        try:
            if not self.sleeper_api:
                logger.error("Sleeper API not initialized")
                return []
            
            trending = self.sleeper_api.get_trending_players(lookback_hours, limit)
            players = self.sleeper_api.get_players()
            
            # Enrich trending data with player names
            enriched_trending = []
            for trend in trending:
                player_id = trend.get('player_id', '')
                if player_id in players:
                    player = players[player_id]
                    enriched_trending.append({
                        'player_id': player_id,
                        'name': f"{player.get('first_name', '')} {player.get('last_name', '')}".strip(),
                        'position': player.get('position', ''),
                        'team': player.get('team', ''),
                        'add_count': trend.get('count', 0),
                        'drop_count': trend.get('drop_count', 0)
                    })
            
            logger.info(f"Retrieved {len(enriched_trending)} trending players")
            return enriched_trending
            
        except Exception as e:
            logger.error(f"Failed to get trending players: {e}")
            return []
    
    def get_cache_info(self) -> Dict[str, Any]:
        """
        Get information about the cache.
        
        Returns:
            Cache information
        """
        try:
            if not self.sleeper_api:
                return {}
            
            cache_size = self.sleeper_api.get_cache_size()
            cache_size_mb = cache_size / (1024 * 1024)
            
            return {
                'enabled': self.config.cache_enabled if self.config else False,
                'size_bytes': cache_size,
                'size_mb': round(cache_size_mb, 2),
                'duration_hours': self.config.cache_duration_hours if self.config else 24
            }
            
        except Exception as e:
            logger.error(f"Failed to get cache info: {e}")
            return {}
    
    def clear_cache(self) -> bool:
        """
        Clear all cached data.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            if not self.sleeper_api:
                logger.error("Sleeper API not initialized")
                return False
            
            self.sleeper_api.clear_cache()
            logger.info("Cache cleared successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to clear cache: {e}")
            return False
    
    def get_provider_info(self) -> Dict[str, Any]:
        """
        Get information about the current AI provider.
        
        Returns:
            Provider information
        """
        try:
            if not self.ai_analyzer:
                return {}
            
            return self.ai_analyzer.get_provider_info()
            
        except Exception as e:
            logger.error(f"Failed to get provider info: {e}")
            return {}
    
    def export_analysis(self, result: AnalysisResult, format: str = "json") -> Optional[str]:
        """
        Export analysis result to different formats.
        
        Args:
            result: Analysis result to export
            format: Export format (json, csv, txt)
            
        Returns:
            Exported data as string or None if failed
        """
        try:
            if format.lower() == "json":
                return self._export_json(result)
            elif format.lower() == "csv":
                return self._export_csv(result)
            elif format.lower() == "txt":
                return self._export_txt(result)
            else:
                logger.error(f"Unsupported export format: {format}")
                return None
                
        except Exception as e:
            logger.error(f"Failed to export analysis: {e}")
            return None
    
    def _export_json(self, result: AnalysisResult) -> str:
        """Export to JSON format."""
        import json
        return json.dumps(result.to_dict(), indent=2)
    
    def _export_csv(self, result: AnalysisResult) -> str:
        """Export to CSV format."""
        import csv
        import io
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow([
            'Strategy', 'Position', 'Player', 'Projected Min', 'Projected Max',
            'Risk Level', 'Confidence', 'Reasoning'
        ])
        
        # Write data
        for strategy in result.strategies:
            for position, player in strategy.lineup.items():
                writer.writerow([
                    strategy.name,
                    position,
                    player,
                    strategy.projected_range[0],
                    strategy.projected_range[1],
                    strategy.risk_level,
                    strategy.confidence,
                    strategy.reasoning
                ])
        
        return output.getvalue()
    
    def _export_txt(self, result: AnalysisResult) -> str:
        """Export to plain text format."""
        lines = []
        lines.append("SLEEPER AI LINEUP OPTIMIZER - ANALYSIS RESULTS")
        lines.append("=" * 50)
        lines.append(f"Provider: {result.provider}")
        lines.append(f"Analysis Time: {result.analysis_time:.2f}s")
        lines.append(f"Timestamp: {datetime.fromtimestamp(result.timestamp)}")
        lines.append("")
        
        for i, strategy in enumerate(result.strategies, 1):
            lines.append(f"STRATEGY {i}: {strategy.name}")
            lines.append("-" * 30)
            lines.append(f"Projected Points: {strategy.projected_range[0]:.1f} - {strategy.projected_range[1]:.1f}")
            lines.append(f"Risk Level: {strategy.risk_level}/10")
            lines.append(f"Confidence: {strategy.confidence}%")
            lines.append("")
            lines.append("LINEUP:")
            for position, player in strategy.lineup.items():
                lines.append(f"  {position:6} {player}")
            lines.append("")
            lines.append("REASONING:")
            lines.append(f"  {strategy.reasoning}")
            lines.append("")
            lines.append("PROS:")
            for pro in strategy.pros:
                lines.append(f"  • {pro}")
            lines.append("")
            lines.append("CONS:")
            for con in strategy.cons:
                lines.append(f"  • {con}")
            lines.append("")
            lines.append("=" * 50)
            lines.append("")
        
        return "\n".join(lines)
