"""AI provider implementations for lineup analysis."""

import json
import time
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from src.utils.logger import get_logger
from src.utils.config import AppConfig

logger = get_logger(__name__)


@dataclass
class LineupStrategy:
    """Represents a lineup strategy recommendation."""
    
    name: str
    lineup: Dict[str, str]
    projected_range: List[float]
    reasoning: str
    pros: List[str]
    cons: List[str]
    risk_level: int
    confidence: int
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "lineup": self.lineup,
            "projected_range": self.projected_range,
            "reasoning": self.reasoning,
            "pros": self.pros,
            "cons": self.cons,
            "risk_level": self.risk_level,
            "confidence": self.confidence
        }


@dataclass
class AnalysisResult:
    """Represents the complete analysis result."""
    
    strategies: List[LineupStrategy]
    analysis_time: float
    provider: str
    timestamp: float
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "strategies": [s.to_dict() for s in self.strategies],
            "analysis_time": self.analysis_time,
            "provider": self.provider,
            "timestamp": self.timestamp
        }


class AIProviderError(Exception):
    """Custom exception for AI provider errors."""
    pass


class BaseAIProvider(ABC):
    """Abstract base class for AI providers."""
    
    def __init__(self, config: AppConfig):
        """
        Initialize AI provider.
        
        Args:
            config: Application configuration
        """
        self.config = config
        self.provider_name = self.__class__.__name__
        logger.info(f"Initialized {self.provider_name}")
    
    @abstractmethod
    def analyze_lineup(self, context: Dict[str, Any]) -> AnalysisResult:
        """
        Analyze lineup and provide recommendations.
        
        Args:
            context: Lineup analysis context
            
        Returns:
            Analysis result with strategies
        """
        pass
    
    def _build_prompt(self, context: Dict[str, Any]) -> str:
        """
        Build the analysis prompt.
        
        Args:
            context: Analysis context
            
        Returns:
            Formatted prompt string
        """
        return f"""
        Analyze this fantasy football lineup situation and provide 3 optimal lineup strategies.
        
        IMPORTANT: You can ONLY use players that are listed in "MY ROSTER" section. Do NOT recommend players that are not on the roster.
        
        WEEK: {context.get('week', 'Unknown')}
        
        MY ROSTER (ONLY USE THESE PLAYERS):
        {json.dumps(context.get('roster', {}), indent=2)}
        
        OPPONENT'S PROJECTED LINEUP:
        {json.dumps(context.get('opponent', {}), indent=2)}
        
        SCORING SETTINGS:
        {json.dumps(context.get('scoring', {}), indent=2)}
        
        ROSTER PLAYERS DETAILS:
        {json.dumps(context.get('players', [])[:30], indent=2)}
        
        PLAYER PROJECTIONS (Week {context.get('week', 'Unknown')}):
        {json.dumps(context.get('projections', {}), indent=2)}
        
        Provide 3 different lineup strategies using ONLY players from your roster:
        1. Safe Floor (minimize risk)
        2. High Ceiling (maximum upside)
        3. Balanced (mix of both)
        
        For each strategy include:
        - Starting lineup by position (ONLY use players from your roster)
        - Projected point range
        - Key reasoning
        - 3 pros and 3 cons
        - Risk level (1-10)
        - Confidence (0-100%)
        
        Format as JSON with this structure:
        {{
            "strategies": [
                {{
                    "name": "Strategy Name",
                    "lineup": {{"QB": "Player Name", "RB1": "Player Name", ...}},
                    "projected_range": [min, max],
                    "reasoning": "Explanation",
                    "pros": ["pro1", "pro2", "pro3"],
                    "cons": ["con1", "con2", "con3"],
                    "risk_level": 5,
                    "confidence": 75
                }}
            ]
        }}
        """
    
    def _parse_response(self, response_text: str) -> List[LineupStrategy]:
        """
        Parse AI response into structured data.
        
        Args:
            response_text: Raw AI response
            
        Returns:
            List of lineup strategies
        """
        try:
            # Try to extract JSON from response
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1
            
            if start_idx == -1 or end_idx == 0:
                raise ValueError("No JSON found in response")
            
            json_str = response_text[start_idx:end_idx]
            data = json.loads(json_str)
            
            strategies = []
            for strategy_data in data.get("strategies", []):
                strategy = LineupStrategy(
                    name=strategy_data.get("name", "Unknown Strategy"),
                    lineup=strategy_data.get("lineup", {}),
                    projected_range=strategy_data.get("projected_range", [0, 0]),
                    reasoning=strategy_data.get("reasoning", "No reasoning provided"),
                    pros=strategy_data.get("pros", []),
                    cons=strategy_data.get("cons", []),
                    risk_level=int(strategy_data.get("risk_level", 5)),
                    confidence=int(strategy_data.get("confidence", 50))
                )
                strategies.append(strategy)
            
            return strategies
            
        except Exception as e:
            logger.error(f"Failed to parse AI response: {e}")
            logger.debug(f"Raw response: {response_text}")
            raise AIProviderError(f"Failed to parse AI response: {e}")


class OpenAIProvider(BaseAIProvider):
    """OpenAI GPT-4 provider implementation."""
    
    def __init__(self, config: AppConfig):
        super().__init__(config)
        try:
            import openai
            self.client = openai.OpenAI(api_key=config.ai_api_key)
            logger.info("OpenAI client initialized")
        except ImportError:
            raise AIProviderError("OpenAI package not installed")
        except Exception as e:
            raise AIProviderError(f"Failed to initialize OpenAI client: {e}")
    
    def analyze_lineup(self, context: Dict[str, Any]) -> AnalysisResult:
        """
        Analyze lineup using OpenAI GPT-4.
        
        Args:
            context: Lineup analysis context
            
        Returns:
            Analysis result
        """
        start_time = time.time()
        
        try:
            prompt = self._build_prompt(context)
            
            logger.info("Sending request to OpenAI GPT-4...")
            
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert fantasy football analyst with deep knowledge of NFL players, matchups, and strategy."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=3000
            )
            
            response_text = response.choices[0].message.content
            strategies = self._parse_response(response_text)
            
            analysis_time = time.time() - start_time
            
            logger.info(f"OpenAI analysis completed in {analysis_time:.2f}s")
            
            return AnalysisResult(
                strategies=strategies,
                analysis_time=analysis_time,
                provider="OpenAI GPT-4",
                timestamp=time.time()
            )
            
        except Exception as e:
            logger.error(f"OpenAI analysis failed: {e}")
            raise AIProviderError(f"OpenAI analysis failed: {e}")


class AnthropicProvider(BaseAIProvider):
    """Anthropic Claude provider implementation."""
    
    def __init__(self, config: AppConfig):
        super().__init__(config)
        try:
            import anthropic
            self.client = anthropic.Anthropic(api_key=config.ai_api_key)
            logger.info("Anthropic client initialized")
        except ImportError:
            raise AIProviderError("Anthropic package not installed")
        except Exception as e:
            raise AIProviderError(f"Failed to initialize Anthropic client: {e}")
    
    def analyze_lineup(self, context: Dict[str, Any]) -> AnalysisResult:
        """
        Analyze lineup using Anthropic Claude.
        
        Args:
            context: Lineup analysis context
            
        Returns:
            Analysis result
        """
        start_time = time.time()
        
        try:
            prompt = self._build_prompt(context)
            
            logger.info("Sending request to Anthropic Claude...")
            
            response = self.client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=3000,
                messages=[{"role": "user", "content": prompt}]
            )
            
            response_text = response.content[0].text
            strategies = self._parse_response(response_text)
            
            analysis_time = time.time() - start_time
            
            logger.info(f"Anthropic analysis completed in {analysis_time:.2f}s")
            
            return AnalysisResult(
                strategies=strategies,
                analysis_time=analysis_time,
                provider="Anthropic Claude",
                timestamp=time.time()
            )
            
        except Exception as e:
            logger.error(f"Anthropic analysis failed: {e}")
            raise AIProviderError(f"Anthropic analysis failed: {e}")


class MockProvider(BaseAIProvider):
    """Mock provider for testing and development."""
    
    def analyze_lineup(self, context: Dict[str, Any]) -> AnalysisResult:
        """
        Provide mock analysis for testing.
        
        Args:
            context: Lineup analysis context
            
        Returns:
            Mock analysis result
        """
        start_time = time.time()
        
        logger.info("Generating mock analysis...")
        
        # Simulate analysis time
        time.sleep(2)
        
        strategies = [
            LineupStrategy(
                name="Safe Floor Play",
                lineup={
                    "QB": "Josh Allen",
                    "RB1": "Christian McCaffrey",
                    "RB2": "Tony Pollard",
                    "WR1": "Tyreek Hill",
                    "WR2": "Stefon Diggs",
                    "TE": "Travis Kelce",
                    "FLEX": "Calvin Ridley",
                    "DST": "49ers",
                    "K": "Justin Tucker"
                },
                projected_range=[110, 125],
                reasoning="Focus on consistent, high-floor players with proven track records.",
                pros=[
                    "Minimal bust risk",
                    "Reliable scoring floor",
                    "Good for protecting a lead"
                ],
                cons=[
                    "Limited ceiling",
                    "May not win you the week",
                    "Predictable lineup"
                ],
                risk_level=3,
                confidence=75
            ),
            LineupStrategy(
                name="High Ceiling Play",
                lineup={
                    "QB": "Jalen Hurts",
                    "RB1": "Austin Ekeler",
                    "RB2": "Breece Hall",
                    "WR1": "Justin Jefferson",
                    "WR2": "Chris Olave",
                    "TE": "Sam LaPorta",
                    "FLEX": "Brandon Aiyuk",
                    "DST": "Cowboys",
                    "K": "Jake Elliott"
                },
                projected_range=[95, 145],
                reasoning="Target boom potential with players in good matchups.",
                pros=[
                    "League-winning upside",
                    "Multiple correlation stacks",
                    "Great for comeback scenarios"
                ],
                cons=[
                    "Higher bust risk",
                    "Volatile scoring",
                    "Weather dependent"
                ],
                risk_level=8,
                confidence=60
            ),
            LineupStrategy(
                name="Balanced Approach",
                lineup={
                    "QB": "Dak Prescott",
                    "RB1": "Saquon Barkley",
                    "RB2": "Josh Jacobs",
                    "WR1": "A.J. Brown",
                    "WR2": "Mike Evans",
                    "TE": "Mark Andrews",
                    "FLEX": "Garrett Wilson",
                    "DST": "Bills",
                    "K": "Harrison Butker"
                },
                projected_range=[105, 135],
                reasoning="Mix of floor and ceiling plays for optimal risk/reward.",
                pros=[
                    "Good balance of safety and upside",
                    "Flexible game script coverage",
                    "Strong at all positions"
                ],
                cons=[
                    "Not optimized for any scenario",
                    "May leave points on bench",
                    "Jack of all trades, master of none"
                ],
                risk_level=5,
                confidence=70
            )
        ]
        
        analysis_time = time.time() - start_time
        
        logger.info(f"Mock analysis completed in {analysis_time:.2f}s")
        
        return AnalysisResult(
            strategies=strategies,
            analysis_time=analysis_time,
            provider="Mock Provider",
            timestamp=time.time()
        )


class AIAnalyzer:
    """Main AI analyzer that manages different providers."""
    
    def __init__(self, config: AppConfig):
        """
        Initialize AI analyzer.
        
        Args:
            config: Application configuration
        """
        self.config = config
        self.provider = self._create_provider()
        logger.info(f"AI Analyzer initialized with {self.provider.provider_name}")
    
    def _create_provider(self) -> BaseAIProvider:
        """Create the appropriate AI provider based on configuration."""
        if self.config.ai_provider == "openai":
            return OpenAIProvider(self.config)
        elif self.config.ai_provider == "anthropic":
            return AnthropicProvider(self.config)
        elif self.config.ai_provider == "mock":
            return MockProvider(self.config)
        else:
            logger.warning(f"Unknown AI provider: {self.config.ai_provider}, using mock")
            return MockProvider(self.config)
    
    def analyze_lineup(self, context: Dict[str, Any]) -> AnalysisResult:
        """
        Analyze lineup using the configured provider.
        
        Args:
            context: Lineup analysis context
            
        Returns:
            Analysis result
        """
        try:
            return self.provider.analyze_lineup(context)
        except Exception as e:
            logger.error(f"AI analysis failed: {e}")
            # Fallback to mock provider
            logger.info("Falling back to mock provider")
            fallback_provider = MockProvider(self.config)
            return fallback_provider.analyze_lineup(context)
    
    def get_provider_info(self) -> Dict[str, str]:
        """Get information about the current provider."""
        return {
            "name": self.provider.provider_name,
            "type": self.config.ai_provider,
            "configured": bool(self.config.ai_api_key) if self.config.ai_provider != "mock" else True
        }
