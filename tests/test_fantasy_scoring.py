"""Tests for fantasy scoring service."""

import pytest
from unittest.mock import Mock, patch
from src.api.fantasy_scoring import FantasyScoringService, FantasyScoringError
from src.utils.config import AppConfig


class TestFantasyScoringService:
    """Test cases for FantasyScoringService."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.config = AppConfig()
        self.service = FantasyScoringService(self.config)
    
    def test_initialization(self):
        """Test service initialization."""
        assert self.service.config == self.config
        assert self.service.espn_base == "https://fantasy.espn.com/apis/v3/games/ffl"
        assert self.service.fantasypros_base == "https://api.fantasypros.com/v2"
    
    def test_get_scoring_settings(self):
        """Test getting scoring settings."""
        settings = self.service.get_scoring_settings("test_league")
        
        assert isinstance(settings, dict)
        assert 'passing_yards' in settings
        assert 'rushing_yards' in settings
        assert 'receptions' in settings
        assert settings['receptions'] == 1.0  # PPR scoring
    
    def test_calculate_player_value(self):
        """Test player value calculation."""
        player_data = {
            'id': 'test_player',
            'name': 'Test Player',
            'position': 'RB'
        }
        
        scoring_settings = self.service.get_scoring_settings("test_league")
        projections = {
            'test_player': {
                'projected_points': 12.5
            }
        }
        
        value = self.service.calculate_player_value(player_data, scoring_settings, projections)
        
        assert value['player_id'] == 'test_player'
        assert value['name'] == 'Test Player'
        assert value['position'] == 'RB'
        assert value['projected_points'] == 12.5
        assert value['value_score'] > 0
        assert 'recommendation' in value
    
    def test_get_recommendation(self):
        """Test recommendation logic."""
        assert self.service._get_recommendation(20) == "Must Start"
        assert self.service._get_recommendation(14) == "Strong Start"
        assert self.service._get_recommendation(10) == "Start"
        assert self.service._get_recommendation(7) == "Flex Consideration"
        assert self.service._get_recommendation(3) == "Bench"
    
    def test_calculate_value_score(self):
        """Test value score calculation."""
        # Test position multipliers
        rb_score = self.service._calculate_value_score('RB', 10.0)
        wr_score = self.service._calculate_value_score('WR', 10.0)
        te_score = self.service._calculate_value_score('TE', 10.0)
        
        assert rb_score == 12.0  # 10.0 * 1.2
        assert wr_score == 11.0  # 10.0 * 1.1
        assert te_score == 13.0  # 10.0 * 1.3
    
    def test_get_player_projections_espn_fallback(self):
        """Test that ESPN projections fall back gracefully."""
        # Test with empty player list
        projections = self.service.get_player_projections([], 1)
        
        # Should return empty dict
        assert projections == {}
    
    def test_estimate_projection(self):
        """Test projection estimation."""
        # Test different weeks
        week1_proj = self.service._estimate_projection('player1', 1)
        week8_proj = self.service._estimate_projection('player1', 8)
        week16_proj = self.service._estimate_projection('player1', 16)
        
        assert 8.0 <= week1_proj <= 15.0
        assert 7.0 <= week8_proj <= 14.0
        assert 6.0 <= week16_proj <= 13.0
