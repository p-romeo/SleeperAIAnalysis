"""Core lineup analysis logic."""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from src.api.sleeper import SleeperAPI
from src.api.ai_providers import AIAnalyzer, AnalysisResult
from src.api.fantasy_scoring import FantasyScoringService
from src.utils.config import AppConfig
from src.utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class Player:
    """Represents a fantasy football player."""
    
    id: str
    name: str
    position: str
    team: str
    status: Optional[str] = None
    
    @classmethod
    def from_sleeper_data(cls, player_id: str, sleeper_data: Dict[str, Any]) -> "Player":
        """Create Player from Sleeper API data."""
        return cls(
            id=player_id,
            name=f"{sleeper_data.get('first_name', '')} {sleeper_data.get('last_name', '')}".strip(),
            position=sleeper_data.get('position', ''),
            team=sleeper_data.get('team', ''),
            status=sleeper_data.get('status', None)
        )


@dataclass
class Roster:
    """Represents a fantasy football roster."""
    
    roster_id: str
    owner_id: str
    players: List[Player]
    taxi: List[str] = None
    practice_squad: List[str] = None
    
    @classmethod
    def from_sleeper_data(cls, sleeper_data: Dict[str, Any], all_players: Dict[str, Any]) -> "Roster":
        """Create Roster from Sleeper API data."""
        players = []
        for player_id in sleeper_data.get('players', []):
            if player_id in all_players:
                player = Player.from_sleeper_data(player_id, all_players[player_id])
                players.append(player)
        
        return cls(
            roster_id=sleeper_data.get('roster_id', ''),
            owner_id=sleeper_data.get('owner_id', ''),
            players=players,
            taxi=sleeper_data.get('taxi', []),
            practice_squad=sleeper_data.get('practice_squad', [])
        )


@dataclass
class Matchup:
    """Represents a fantasy football matchup."""
    
    matchup_id: str
    roster_id: str
    opponent_roster_id: str
    week: int
    points: float
    projected_points: float
    
    @classmethod
    def from_sleeper_data(cls, sleeper_data: Dict[str, Any]) -> "Matchup":
        """Create Matchup from Sleeper API data."""
        return cls(
            matchup_id=sleeper_data.get('matchup_id', ''),
            roster_id=sleeper_data.get('roster_id', ''),
            opponent_roster_id=sleeper_data.get('opponent_roster_id', ''),
            week=sleeper_data.get('week', 0),
            points=sleeper_data.get('points', 0.0),
            projected_points=sleeper_data.get('projected_points', 0.0)
        )


class LineupAnalyzer:
    """Core lineup analysis engine."""
    
    def __init__(self, sleeper_api: SleeperAPI, ai_analyzer: AIAnalyzer, config: AppConfig):
        """
        Initialize lineup analyzer.
        
        Args:
            sleeper_api: Sleeper API wrapper
            ai_analyzer: AI analysis engine
            config: Application configuration
        """
        self.sleeper_api = sleeper_api
        self.ai_analyzer = ai_analyzer
        self.fantasy_scoring = FantasyScoringService(config)
        logger.info("Lineup Analyzer initialized")
    
    def analyze_week(
        self, 
        league_id: str, 
        user_id: str, 
        week: int
    ) -> Optional[AnalysisResult]:
        """
        Analyze lineup for a specific week.
        
        Args:
            league_id: League ID
            user_id: User ID
            week: NFL week
            
        Returns:
            Analysis result or None if failed
        """
        try:
            logger.info(f"Starting analysis for week {week}")
            
            # Gather all necessary data
            context = self._build_analysis_context(league_id, user_id, week)
            if not context:
                logger.error("Failed to build analysis context")
                return None
            
            # Run AI analysis
            logger.info("Running AI analysis...")
            result = self.ai_analyzer.analyze_lineup(context)
            
            logger.info(f"Analysis completed successfully in {result.analysis_time:.2f}s")
            return result
            
        except Exception as e:
            logger.error(f"Analysis failed: {e}")
            return None
    
    def _build_analysis_context(
        self, 
        league_id: str, 
        user_id: str, 
        week: int
    ) -> Optional[Dict[str, Any]]:
        """
        Build context for AI analysis.
        
        Args:
            league_id: League ID
            user_id: User ID
            week: NFL week
            
        Returns:
            Analysis context or None if failed
        """
        try:
            # Get league details
            league = self.sleeper_api.get_league(league_id)
            if not league:
                logger.error(f"Failed to get league {league_id}")
                return None
            
            # Get rosters
            rosters = self.sleeper_api.get_rosters(league_id)
            if not rosters:
                logger.error(f"Failed to get rosters for league {league_id}")
                return None
            
            # Get users
            users = self.sleeper_api.get_users(league_id)
            if not users:
                logger.error(f"Failed to get users for league {league_id}")
                return None
            
            # Get matchups
            matchups = self.sleeper_api.get_matchups(league_id, week)
            if not matchups:
                logger.error(f"Failed to get matchups for week {week}")
                return None
            
            # Get player data
            players = self.sleeper_api.get_players()
            if not players:
                logger.error("Failed to get player data")
                return None
            
            # Find user's roster
            user_roster = None
            for roster in rosters:
                if roster.get('owner_id') == user_id:
                    user_roster = roster
                    break
            
            if not user_roster:
                logger.error(f"Could not find roster for user {user_id}")
                return None
            
            # Find opponent
            opponent_roster = self._find_opponent_roster(
                user_roster, rosters, matchups, users
            )
            
            # Get fantasy scoring data
            scoring_settings = self.fantasy_scoring.get_scoring_settings(league_id)
            
            # Get player projections
            roster_player_ids = user_roster.get('players', [])
            projections = self.fantasy_scoring.get_player_projections(roster_player_ids, week)
            
            # Build context
            context = {
                'week': week,
                'league_name': league.get('name', 'Unknown League'),
                'roster': self._format_roster_for_ai(user_roster, players),
                'opponent': self._format_roster_for_ai(opponent_roster, players) if opponent_roster else {},
                'scoring': scoring_settings,
                'players': self._get_relevant_players(user_roster, players),
                'projections': projections,
                'league_settings': {
                    'num_teams': league.get('settings', {}).get('num_teams'),
                    'league_type': league.get('settings', {}).get('type'),
                    'playoff_teams': league.get('settings', {}).get('playoff_teams')
                }
            }
            
            logger.info("Analysis context built successfully")
            return context
            
        except Exception as e:
            logger.error(f"Failed to build analysis context: {e}")
            return None
    
    def _find_opponent_roster(
        self, 
        user_roster: Dict[str, Any], 
        rosters: List[Dict[str, Any]], 
        matchups: List[Dict[str, Any]], 
        users: List[Dict[str, Any]]
    ) -> Optional[Dict[str, Any]]:
        """Find the opponent's roster for the current week."""
        try:
            # Find user's matchup
            user_matchup = None
            for matchup in matchups:
                if matchup.get('roster_id') == user_roster.get('roster_id'):
                    user_matchup = matchup
                    break
            
            if not user_matchup:
                return None
            
            # Find opponent in same matchup
            opponent_roster_id = None
            for matchup in matchups:
                if (matchup.get('matchup_id') == user_matchup.get('matchup_id') and 
                    matchup.get('roster_id') != user_roster.get('roster_id')):
                    opponent_roster_id = matchup.get('roster_id')
                    break
            
            if not opponent_roster_id:
                return None
            
            # Get opponent roster
            for roster in rosters:
                if roster.get('roster_id') == opponent_roster_id:
                    return roster
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to find opponent roster: {e}")
            return None
    
    def _format_roster_for_ai(
        self, 
        roster: Dict[str, Any], 
        all_players: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Format roster data for AI analysis."""
        if not roster:
            return {}
        
        formatted = {
            'roster_id': roster.get('roster_id', ''),
            'players': []
        }
        
        for player_id in roster.get('players', []):
            if player_id in all_players:
                player = all_players[player_id]
                formatted['players'].append({
                    'id': player_id,
                    'name': f"{player.get('first_name', '')} {player.get('last_name', '')}".strip(),
                    'position': player.get('position', ''),
                    'team': player.get('team', ''),
                    'status': player.get('status', 'Active')
                })
        
        return formatted
    
    def _get_relevant_players(
        self, 
        roster: Dict[str, Any], 
        all_players: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Get relevant player data for analysis (limit to avoid token overflow)."""
        relevant = []
        # Only include players that are actually on the roster
        for player_id in roster.get('players', []):
            if player_id in all_players:
                player = all_players[player_id]
                relevant.append({
                    'id': player_id,
                    'name': f"{player.get('first_name', '')} {player.get('last_name', '')}".strip(),
                    'position': player.get('position', ''),
                    'team': player.get('team', ''),
                    'status': player.get('status', 'Active'),
                    'injury_status': player.get('injury_status', ''),
                    'fantasy_positions': player.get('fantasy_positions', [])
                })
        return relevant[:30]  # Limit to 30 players to avoid token overflow
    
    def get_analysis_summary(self, result: AnalysisResult) -> Dict[str, Any]:
        """
        Get a summary of the analysis result.
        
        Args:
            result: Analysis result
            
        Returns:
            Summary dictionary
        """
        if not result or not result.strategies:
            return {}
        
        # Calculate averages
        avg_risk = sum(s.risk_level for s in result.strategies) / len(result.strategies)
        avg_confidence = sum(s.confidence for s in result.strategies) / len(result.strategies)
        
        # Find best strategy by confidence
        best_strategy = max(result.strategies, key=lambda s: s.confidence)
        
        return {
            'total_strategies': len(result.strategies),
            'analysis_time': result.analysis_time,
            'provider': result.provider,
            'average_risk': round(avg_risk, 1),
            'average_confidence': round(avg_confidence, 1),
            'best_strategy': best_strategy.name,
            'best_confidence': best_strategy.confidence,
            'timestamp': result.timestamp
        }
