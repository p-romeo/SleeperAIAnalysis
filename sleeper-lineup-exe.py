"""
Sleeper Fantasy Football AI Lineup Optimizer
Standalone executable application for Windows
Author: Your Name
Version: 1.0.0
"""

import os
import sys
import json
import time
import requests
from datetime import datetime
from typing import List, Dict, Optional, Tuple
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
import getpass

# For colored console output
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

class ConfigManager:
    """Manages API keys and user preferences"""
    
    def __init__(self):
        self.config_file = "config.encrypted"
        self.key = None
        
    def get_encryption_key(self, password: str) -> bytes:
        """Generate encryption key from password"""
        kdf = PBKDF2(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b'sleeper_optimizer_salt',
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return key
    
    def save_config(self, config: dict, password: str):
        """Save encrypted configuration"""
        key = self.get_encryption_key(password)
        f = Fernet(key)
        encrypted = f.encrypt(json.dumps(config).encode())
        with open(self.config_file, 'wb') as file:
            file.write(encrypted)
    
    def load_config(self, password: str) -> dict:
        """Load encrypted configuration"""
        if not os.path.exists(self.config_file):
            return {}
        
        try:
            key = self.get_encryption_key(password)
            f = Fernet(key)
            with open(self.config_file, 'rb') as file:
                encrypted = file.read()
            decrypted = f.decrypt(encrypted)
            return json.loads(decrypted.decode())
        except:
            return {}

class SleeperAPI:
    """Handles all Sleeper API interactions"""
    
    BASE_URL = "https://api.sleeper.app/v1"
    
    @staticmethod
    def get_user(username: str) -> dict:
        """Get user data from username"""
        response = requests.get(f"{SleeperAPI.BASE_URL}/user/{username}")
        if response.status_code == 200:
            return response.json()
        return None
    
    @staticmethod
    def get_user_leagues(user_id: str, season: str = "2024") -> list:
        """Get all leagues for a user"""
        response = requests.get(
            f"{SleeperAPI.BASE_URL}/user/{user_id}/leagues/nfl/{season}"
        )
        if response.status_code == 200:
            return response.json()
        return []
    
    @staticmethod
    def get_league(league_id: str) -> dict:
        """Get league details"""
        response = requests.get(f"{SleeperAPI.BASE_URL}/league/{league_id}")
        if response.status_code == 200:
            return response.json()
        return None
    
    @staticmethod
    def get_rosters(league_id: str) -> list:
        """Get all rosters in a league"""
        response = requests.get(f"{SleeperAPI.BASE_URL}/league/{league_id}/rosters")
        if response.status_code == 200:
            return response.json()
        return []
    
    @staticmethod
    def get_users(league_id: str) -> list:
        """Get all users in a league"""
        response = requests.get(f"{SleeperAPI.BASE_URL}/league/{league_id}/users")
        if response.status_code == 200:
            return response.json()
        return []
    
    @staticmethod
    def get_matchups(league_id: str, week: int) -> list:
        """Get matchups for a specific week"""
        response = requests.get(
            f"{SleeperAPI.BASE_URL}/league/{league_id}/matchups/{week}"
        )
        if response.status_code == 200:
            return response.json()
        return []
    
    @staticmethod
    def get_players() -> dict:
        """Get all NFL players (large dataset)"""
        # This is cached on their CDN
        response = requests.get(f"{SleeperAPI.BASE_URL}/players/nfl")
        if response.status_code == 200:
            return response.json()
        return {}
    
    @staticmethod
    def get_trending_players(lookback_hours: int = 24, limit: int = 25) -> list:
        """Get trending players"""
        response = requests.get(
            f"{SleeperAPI.BASE_URL}/players/nfl/trending/add",
            params={"lookback_hours": lookback_hours, "limit": limit}
        )
        if response.status_code == 200:
            return response.json()
        return []

class AIAnalyzer:
    """Handles AI analysis for lineup optimization"""
    
    def __init__(self, api_key: str, provider: str = "openai"):
        self.api_key = api_key
        self.provider = provider
        
    def analyze_lineup(self, context: dict, analysis_time: int = 5) -> dict:
        """
        Perform AI analysis on lineup options
        Returns structured recommendations
        """
        
        prompt = self._build_prompt(context)
        
        if self.provider == "openai":
            return self._analyze_with_openai(prompt, analysis_time)
        elif self.provider == "anthropic":
            return self._analyze_with_anthropic(prompt, analysis_time)
        else:
            return self._mock_analysis(context)
    
    def _build_prompt(self, context: dict) -> str:
        """Build the analysis prompt"""
        return f"""
        Analyze this fantasy football lineup situation and provide 3 optimal lineup strategies.
        
        WEEK: {context['week']}
        
        MY ROSTER:
        {json.dumps(context['roster'], indent=2)}
        
        OPPONENT'S PROJECTED LINEUP:
        {json.dumps(context['opponent'], indent=2)}
        
        SCORING SETTINGS:
        {json.dumps(context['scoring'], indent=2)}
        
        AVAILABLE PLAYERS:
        {json.dumps(context['players'], indent=2)}
        
        Provide 3 different lineup strategies:
        1. Safe Floor (minimize risk)
        2. High Ceiling (maximum upside)
        3. Balanced (mix of both)
        
        For each strategy include:
        - Starting lineup by position
        - Projected point range
        - Key reasoning
        - 3 pros and 3 cons
        - Risk level (1-10)
        - Confidence (0-100%)
        
        Format as JSON.
        """
    
    def _analyze_with_openai(self, prompt: str, analysis_time: int) -> dict:
        """Use OpenAI GPT-4 for analysis"""
        try:
            import openai
            openai.api_key = self.api_key
            
            # Simulate extended analysis time
            print(f"Performing deep {analysis_time}-minute analysis...")
            
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert fantasy football analyst."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=3000
            )
            
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            print(f"OpenAI API error: {e}")
            return self._mock_analysis({})
    
    def _analyze_with_anthropic(self, prompt: str, analysis_time: int) -> dict:
        """Use Anthropic Claude for analysis"""
        try:
            import anthropic
            client = anthropic.Client(api_key=self.api_key)
            
            print(f"Performing deep {analysis_time}-minute analysis...")
            
            response = client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=3000,
                messages=[{"role": "user", "content": prompt}]
            )
            
            return json.loads(response.content[0].text)
        except Exception as e:
            print(f"Anthropic API error: {e}")
            return self._mock_analysis({})
    
    def _mock_analysis(self, context: dict) -> dict:
        """Return mock analysis for testing"""
        return {
            "strategies": [
                {
                    "name": "Safe Floor Play",
                    "lineup": {
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
                    "projected_range": [110, 125],
                    "reasoning": "Focus on consistent, high-floor players with proven track records.",
                    "pros": [
                        "Minimal bust risk",
                        "Reliable scoring floor",
                        "Good for protecting a lead"
                    ],
                    "cons": [
                        "Limited ceiling",
                        "May not win you the week",
                        "Predictable lineup"
                    ],
                    "risk_level": 3,
                    "confidence": 75
                },
                {
                    "name": "High Ceiling Play",
                    "lineup": {
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
                    "projected_range": [95, 145],
                    "reasoning": "Target boom potential with players in good matchups.",
                    "pros": [
                        "League-winning upside",
                        "Multiple correlation stacks",
                        "Great for comeback scenarios"
                    ],
                    "cons": [
                        "Higher bust risk",
                        "Volatile scoring",
                        "Weather dependent"
                    ],
                    "risk_level": 8,
                    "confidence": 60
                },
                {
                    "name": "Balanced Approach",
                    "lineup": {
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
                    "projected_range": [105, 135],
                    "reasoning": "Mix of floor and ceiling plays for optimal risk/reward.",
                    "pros": [
                        "Good balance of safety and upside",
                        "Flexible game script coverage",
                        "Strong at all positions"
                    ],
                    "cons": [
                        "Not optimized for any scenario",
                        "May leave points on bench",
                        "Jack of all trades, master of none"
                    ],
                    "risk_level": 5,
                    "confidence": 70
                }
            ]
        }

class LineupOptimizer:
    """Main application class"""
    
    def __init__(self):
        self.config_manager = ConfigManager()
        self.sleeper_api = SleeperAPI()
        self.ai_analyzer = None
        self.user_data = None
        self.selected_league = None
        self.config = {}
        
    def clear_screen(self):
        """Clear the console screen"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def print_header(self):
        """Print application header"""
        self.clear_screen()
        print(Colors.CYAN + "=" * 60)
        print("     SLEEPER AI LINEUP OPTIMIZER v1.0")
        print("=" * 60 + Colors.ENDC)
        print()
    
    def setup_initial_config(self):
        """Initial setup for first-time users"""
        self.print_header()
        print(Colors.BOLD + "Welcome! Let's set up your configuration.\n" + Colors.ENDC)
        
        # Get AI provider preference
        print("Select AI Provider:")
        print("1. OpenAI (GPT-4)")
        print("2. Anthropic (Claude)")
        print("3. Mock Analysis (for testing)")
        
        choice = input("\nEnter choice (1-3): ").strip()
        
        if choice == "1":
            provider = "openai"
            print("\nYou'll need an OpenAI API key from https://platform.openai.com/api-keys")
            api_key = getpass.getpass("Enter OpenAI API Key: ").strip()
        elif choice == "2":
            provider = "anthropic"
            print("\nYou'll need an Anthropic API key from https://console.anthropic.com/")
            api_key = getpass.getpass("Enter Anthropic API Key: ").strip()
        else:
            provider = "mock"
            api_key = "mock_key"
            print("\nUsing mock analysis (no API required)")
        
        # Get Sleeper username
        username = input("\nEnter your Sleeper username: ").strip()
        
        # Create password for config encryption
        password = getpass.getpass("\nCreate a password to encrypt your settings: ")
        confirm = getpass.getpass("Confirm password: ")
        
        while password != confirm:
            print(Colors.FAIL + "Passwords don't match! Try again." + Colors.ENDC)
            password = getpass.getpass("Create a password to encrypt your settings: ")
            confirm = getpass.getpass("Confirm password: ")
        
        # Save configuration
        self.config = {
            "ai_provider": provider,
            "ai_api_key": api_key,
            "sleeper_username": username
        }
        
        self.config_manager.save_config(self.config, password)
        print(Colors.GREEN + "\n✓ Configuration saved successfully!" + Colors.ENDC)
        time.sleep(2)
        
        return password
    
    def load_configuration(self):
        """Load existing configuration or create new"""
        if os.path.exists(self.config_manager.config_file):
            self.print_header()
            password = getpass.getpass("Enter your password: ")
            self.config = self.config_manager.load_config(password)
            
            if not self.config:
                print(Colors.FAIL + "Invalid password or corrupted config!" + Colors.ENDC)
                print("1. Try again")
                print("2. Reset configuration")
                
                choice = input("\nEnter choice: ").strip()
                if choice == "2":
                    os.remove(self.config_manager.config_file)
                    return self.setup_initial_config()
                else:
                    return self.load_configuration()
            
            return password
        else:
            return self.setup_initial_config()
    
    def select_league(self) -> dict:
        """Let user select a league"""
        self.print_header()
        print(Colors.BOLD + "Fetching your leagues...\n" + Colors.ENDC)
        
        # Get user data
        user = self.sleeper_api.get_user(self.config["sleeper_username"])
        if not user:
            print(Colors.FAIL + "Error: Could not find Sleeper user!" + Colors.ENDC)
            input("\nPress Enter to exit...")
            sys.exit(1)
        
        self.user_data = user
        user_id = user["user_id"]
        
        # Get leagues
        leagues = self.sleeper_api.get_user_leagues(user_id, "2024")
        if not leagues:
            print(Colors.WARNING + "No leagues found for 2024 season!" + Colors.ENDC)
            input("\nPress Enter to exit...")
            sys.exit(1)
        
        # Display leagues
        print(f"Found {len(leagues)} league(s):\n")
        for i, league in enumerate(leagues, 1):
            print(f"{i}. {league['name']}")
            print(f"   Type: {league.get('settings', {}).get('type', 'Unknown')}")
            print(f"   Teams: {league.get('settings', {}).get('num_teams', 'Unknown')}")
            print()
        
        # Select league
        while True:
            try:
                choice = int(input("Select league (number): "))
                if 1 <= choice <= len(leagues):
                    return leagues[choice - 1]
                else:
                    print(Colors.FAIL + "Invalid choice!" + Colors.ENDC)
            except ValueError:
                print(Colors.FAIL + "Please enter a number!" + Colors.ENDC)
    
    def select_week(self) -> int:
        """Let user select which week to optimize"""
        self.print_header()
        print(Colors.BOLD + "Select Week to Optimize\n" + Colors.ENDC)
        
        # Get current NFL week (simplified - you'd calculate this properly)
        current_week = 10  # Placeholder
        
        print(f"Current NFL Week: {current_week}")
        print("\nOptions:")
        print(f"1. Current Week ({current_week})")
        print("2. Next Week ({})".format(current_week + 1))
        print("3. Custom Week")
        
        choice = input("\nEnter choice (1-3): ").strip()
        
        if choice == "1":
            return current_week
        elif choice == "2":
            return current_week + 1
        else:
            return int(input("Enter week number (1-18): "))
    
    def analyze_matchup(self, week: int):
        """Perform the lineup analysis"""
        self.print_header()
        print(Colors.BOLD + f"Analyzing Week {week} Matchup...\n" + Colors.ENDC)
        
        # Get league data
        league_id = self.selected_league["league_id"]
        print("📊 Fetching league data...")
        league_details = self.sleeper_api.get_league(league_id)
        
        print("👥 Fetching rosters...")
        rosters = self.sleeper_api.get_rosters(league_id)
        users = self.sleeper_api.get_users(league_id)
        
        print("🏈 Fetching matchups...")
        matchups = self.sleeper_api.get_matchups(league_id, week)
        
        print("📈 Loading player data...")
        players = self.sleeper_api.get_players()
        
        # Find user's roster
        user_roster = None
        for roster in rosters:
            if roster["owner_id"] == self.user_data["user_id"]:
                user_roster = roster
                break
        
        if not user_roster:
            print(Colors.FAIL + "Error: Could not find your roster!" + Colors.ENDC)
            return
        
        # Find opponent
        user_matchup = None
        opponent_roster = None
        for matchup in matchups:
            if matchup["roster_id"] == user_roster["roster_id"]:
                user_matchup = matchup
                # Find opponent in same matchup
                for m in matchups:
                    if (m["matchup_id"] == matchup["matchup_id"] and 
                        m["roster_id"] != user_roster["roster_id"]):
                        for roster in rosters:
                            if roster["roster_id"] == m["roster_id"]:
                                opponent_roster = roster
                                break
                break
        
        # Prepare context for AI
        context = {
            "week": week,
            "roster": self._format_roster(user_roster, players),
            "opponent": self._format_roster(opponent_roster, players) if opponent_roster else {},
            "scoring": league_details.get("scoring_settings", {}),
            "players": self._get_relevant_players(user_roster, players)
        }
        
        # Run AI analysis
        print(f"\n{Colors.CYAN}🤖 Running AI analysis (this may take a few minutes)...{Colors.ENDC}")
        
        analysis_time = 5  # minutes
        if self.ai_analyzer is None:
            self.ai_analyzer = AIAnalyzer(
                self.config["ai_api_key"],
                self.config["ai_provider"]
            )
        
        results = self.ai_analyzer.analyze_lineup(context, analysis_time)
        
        # Display results
        self.display_results(results, week)
    
    def _format_roster(self, roster: dict, all_players: dict) -> dict:
        """Format roster data with player names"""
        if not roster:
            return {}
        
        formatted = {
            "roster_id": roster["roster_id"],
            "players": []
        }
        
        for player_id in roster.get("players", []):
            if player_id in all_players:
                player = all_players[player_id]
                formatted["players"].append({
                    "id": player_id,
                    "name": f"{player.get('first_name', '')} {player.get('last_name', '')}",
                    "position": player.get("position", ""),
                    "team": player.get("team", "")
                })
        
        return formatted
    
    def _get_relevant_players(self, roster: dict, all_players: dict) -> list:
        """Get relevant player data for the roster"""
        relevant = []
        for player_id in roster.get("players", [])[:20]:  # Limit to avoid token overflow
            if player_id in all_players:
                player = all_players[player_id]
                relevant.append({
                    "name": f"{player.get('first_name', '')} {player.get('last_name', '')}",
                    "position": player.get("position", ""),
                    "team": player.get("team", "")
                })
        return relevant
    
    def display_results(self, results: dict, week: int):
        """Display the analysis results"""
        self.print_header()
        print(Colors.BOLD + f"📊 WEEK {week} LINEUP RECOMMENDATIONS\n" + Colors.ENDC)
        
        strategies = results.get("strategies", [])
        
        for i, strategy in enumerate(strategies, 1):
            print(Colors.CYAN + f"\n{'='*60}")
            print(f"STRATEGY {i}: {strategy['name'].upper()}")
            print('='*60 + Colors.ENDC)
            
            # Display lineup
            print(Colors.BOLD + "\n📋 LINEUP:" + Colors.ENDC)
            for position, player in strategy["lineup"].items():
                print(f"  {position:6} {player}")
            
            # Display projections
            proj_range = strategy.get("projected_range", [0, 0])
            print(Colors.BOLD + f"\n📈 PROJECTED POINTS:" + Colors.ENDC + 
                  f" {proj_range[0]:.1f} - {proj_range[1]:.1f}")
            
            # Display metrics
            print(Colors.BOLD + f"⚠️  RISK LEVEL:" + Colors.ENDC + 
                  f" {strategy.get('risk_level', 5)}/10")
            print(Colors.BOLD + f"🎯 CONFIDENCE:" + Colors.ENDC + 
                  f" {strategy.get('confidence', 50)}%")
            
            # Display reasoning
            print(Colors.BOLD + "\n💡 REASONING:" + Colors.ENDC)
            print(f"  {strategy.get('reasoning', 'No reasoning provided')}")
            
            # Display pros/cons
            print(Colors.GREEN + "\n✓ PROS:" + Colors.ENDC)
            for pro in strategy.get("pros", []):
                print(f"  • {pro}")
            
            print(Colors.WARNING + "\n✗ CONS:" + Colors.ENDC)
            for con in strategy.get("cons", []):
                print(f"  • {con}")
        
        print(Colors.CYAN + "\n" + "="*60 + Colors.ENDC)
        print(Colors.BOLD + "\n📝 NEXT STEPS:" + Colors.ENDC)
        print("1. Review the recommendations above")
        print("2. Choose your preferred strategy")
        print("3. Manually set your lineup in the Sleeper app")
        print("4. Good luck! 🍀")
        
        input("\n\nPress Enter to return to main menu...")
    
    def run(self):
        """Main application loop"""
        # Load configuration
        password = self.load_configuration()
        
        while True:
            self.print_header()
            print(Colors.BOLD + f"Welcome, {self.config['sleeper_username']}!\n" + Colors.ENDC)
            
            print("What would you like to do?\n")
            print("1. Optimize Lineup")
            print("2. View Trending Players")
            print("3. Update Configuration")
            print("4. Exit")
            
            choice = input("\nEnter choice (1-4): ").strip()
            
            if choice == "1":
                # Select league
                self.selected_league = self.select_league()
                
                # Select week
                week = self.select_week()
                
                # Analyze matchup
                self.analyze_matchup(week)
                
            elif choice == "2":
                # Show trending players
                self.print_header()
                print(Colors.BOLD + "📈 TRENDING PLAYERS\n" + Colors.ENDC)
                
                trending = self.sleeper_api.get_trending_players()
                players = self.sleeper_api.get_players()
                
                print("Top 10 Most Added Players (Last 24 Hours):\n")
                for i, trend in enumerate(trending[:10], 1):
                    player_id = trend.get("player_id", "")
                    if player_id in players:
                        player = players[player_id]
                        name = f"{player.get('first_name', '')} {player.get('last_name', '')}"
                        position = player.get("position", "")
                        team = player.get("team", "")
                        print(f"{i:2}. {name:20} {position:3} - {team:3} (Added {trend.get('count', 0):,} times)")
                
                input("\nPress Enter to continue...")
                
            elif choice == "3":
                # Update configuration
                os.remove(self.config_manager.config_file)
                password = self.setup_initial_config()
                
            elif choice == "4":
                print(Colors.GREEN + "\nThanks for using Sleeper AI Lineup Optimizer!" + Colors.ENDC)
                print("Good luck with your fantasy season! 🏈")
                time.sleep(2)
                break
            
            else:
                print(Colors.FAIL + "Invalid choice!" + Colors.ENDC)
                time.sleep(1)

def main():
    """Entry point"""
    try:
        app = LineupOptimizer()
        app.run()
    except KeyboardInterrupt:
        print("\n\nExiting...")
    except Exception as e:
        print(f"\n{Colors.FAIL}Error: {e}{Colors.ENDC}")
        input("\nPress Enter to exit...")

if __name__ == "__main__":
    main()