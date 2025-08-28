"""Command-line interface for the Sleeper AI Lineup Optimizer."""

import os
import sys
from typing import Optional, List, Dict, Any

from src.core.optimizer import LineupOptimizer
from src.utils.config import ConfigManager, AppConfig
from src.utils.logger import get_logger
from src.utils.colors import Colors

logger = get_logger(__name__)


class CLIInterface:
    """Command-line interface for user interaction."""
    
    def __init__(self):
        """Initialize CLI interface."""
        self.optimizer = LineupOptimizer()
        self.config_manager = ConfigManager()
        
        logger.info("CLI Interface initialized")
    
    def clear_screen(self) -> None:
        """Clear the console screen."""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def print_header(self) -> None:
        """Print application header."""
        self.clear_screen()
        print(Colors.CYAN + "=" * 60)
        print("     SLEEPER AI LINEUP OPTIMIZER v1.0")
        print("=" * 60 + Colors.ENDC)
        print()
    
    def print_menu(self, title: str, options: List[str], back_option: bool = True) -> None:
        """Print a formatted menu."""
        print(Colors.BOLD + f"\n{title}\n" + Colors.ENDC)
        print("-" * len(title))
        
        for i, option in enumerate(options, 1):
            print(f"{i}. {option}")
        
        if back_option:
            print(f"{len(options) + 1}. Back")
        
        print()
    
    def get_user_choice(self, max_choice: int, prompt: str = "Enter choice: ") -> Optional[int]:
        """Get user choice with validation."""
        while True:
            try:
                choice = input(prompt).strip()
                if choice.lower() in ['q', 'quit', 'exit']:
                    return None
                
                choice_num = int(choice)
                if 1 <= choice_num <= max_choice:
                    return choice_num
                else:
                    print(Colors.error(f"Please enter a number between 1 and {max_choice}"))
            except ValueError:
                print(Colors.error("Please enter a valid number"))
            except KeyboardInterrupt:
                return None
    
    def setup_initial_config(self) -> bool:
        """Initial setup for first-time users."""
        self.print_header()
        print(Colors.bold("Welcome! Let's set up your configuration.\n"))
        
        # Get AI provider preference
        print("Select AI Provider:")
        print("1. OpenAI (GPT-4)")
        print("2. Anthropic (Claude)")
        print("3. Mock Analysis (for testing)")
        
        choice = self.get_user_choice(3, "\nEnter choice (1-3): ")
        if choice is None:
            return False
        
        if choice == 1:
            provider = "openai"
            print("\nYou'll need an OpenAI API key from https://platform.openai.com/api-keys")
            api_key = input("Enter OpenAI API Key: ").strip()
        elif choice == 2:
            provider = "anthropic"
            print("\nYou'll need an Anthropic API key from https://console.anthropic.com/")
            api_key = input("Enter Anthropic API Key: ").strip()
        else:
            provider = "mock"
            api_key = "mock_key"
            print("\nUsing mock analysis (no API required)")
        
        # Get Sleeper username
        username = input("\nEnter your Sleeper username: ").strip()
        if not username:
            print(Colors.error("Username is required!"))
            return False
        
        # Get FantasyPros API key (optional)
        print("\nFantasyPros API key is optional but provides better projections.")
        print("Get one at: https://www.fantasypros.com/apis/")
        fantasypros_key = input("Enter FantasyPros API key (or press Enter to skip): ").strip()
        
        # Create and save configuration
        config = AppConfig(
            ai_provider=provider,
            ai_api_key=api_key,
            sleeper_username=username,
            fantasypros_api_key=fantasypros_key
        )
        
        try:
            self.config_manager.save_config(config)
            print(Colors.success("\n✓ Configuration saved successfully!"))
            return True
        except Exception as e:
            print(Colors.error(f"\n✗ Failed to save configuration: {e}"))
            return False
    
    def load_configuration(self) -> bool:
        """Load existing configuration or create new."""
        if self.config_manager.config_exists():
            config = self.config_manager.load_config()
            if not config:
                print(Colors.error("Configuration file is corrupted!"))
                print("1. Reset configuration")
                print("2. Exit")
                
                choice = self.get_user_choice(2, "\nEnter choice: ")
                if choice == 1:
                    self.config_manager.delete_config()
                    return self.setup_initial_config()
                else:
                    return False
            
            return True
        else:
            return self.setup_initial_config()
    
    def select_league(self) -> Optional[Dict[str, Any]]:
        """Let user select a league."""
        self.print_header()
        print(Colors.bold("Fetching your leagues...\n"))
        
        # Get user data
        if not self.optimizer.config:
            print(Colors.error("Configuration not loaded!"))
            return None
        
        username = self.optimizer.config.sleeper_username
        user_data = self.optimizer.get_user_info(username)
        if not user_data:
            print(Colors.error("Could not find Sleeper user!"))
            input("\nPress Enter to continue...")
            return None
        
        # Get leagues
        leagues = self.optimizer.get_user_leagues("2024")
        if not leagues:
            print(Colors.warning("No leagues found for 2024 season!"))
            input("\nPress Enter to continue...")
            return None
        
        # Display leagues
        print(f"Found {len(leagues)} league(s):\n")
        for i, league in enumerate(leagues, 1):
            print(f"{i}. {league['name']}")
            print(f"   Type: {league.get('settings', {}).get('type', 'Unknown')}")
            print(f"   Teams: {league.get('settings', {}).get('num_teams', 'Unknown')}")
            print()
        
        # Select league
        choice = self.get_user_choice(len(leagues), "Select league (number): ")
        if choice is None:
            return None
        
        selected_league = self.optimizer.select_league(choice - 1, leagues)
        if selected_league:
            print(Colors.success(f"Selected: {selected_league['name']}"))
            return selected_league
        
        return None
    
    def select_week(self) -> Optional[int]:
        """Let user select which week to optimize."""
        self.print_header()
        print(Colors.bold("Select Week to Optimize\n"))
        
        # Get current NFL week
        current_week = self.optimizer.get_current_nfl_week()
        
        print(f"Current NFL Week: {current_week}")
        print("\nOptions:")
        print(f"1. Current Week ({current_week})")
        print("2. Next Week ({})".format(current_week + 1))
        print("3. Custom Week")
        
        choice = self.get_user_choice(3, "\nEnter choice (1-3): ")
        if choice is None:
            return None
        
        if choice == 1:
            return current_week
        elif choice == 2:
            return current_week + 1
        else:
            try:
                week = int(input("Enter week number (1-18): "))
                if 1 <= week <= 18:
                    return week
                else:
                    print(Colors.error("Week must be between 1 and 18"))
                    return None
            except ValueError:
                print(Colors.error("Please enter a valid week number"))
                return None
    
    def display_results(self, result: Any, week: int) -> None:
        """Display the analysis results."""
        self.print_header()
        print(Colors.bold(f"📊 WEEK {week} LINEUP RECOMMENDATIONS\n"))
        
        if not result or not hasattr(result, 'strategies'):
            print(Colors.error("No analysis results to display"))
            input("\nPress Enter to continue...")
            return
        
        strategies = result.strategies
        
        for i, strategy in enumerate(strategies, 1):
            print(Colors.CYAN + f"\n{'='*60}")
            print(f"STRATEGY {i}: {strategy.name.upper()}")
            print('='*60 + Colors.ENDC)
            
            # Display lineup
            print(Colors.bold("\n📋 LINEUP:"))
            for position, player in strategy.lineup.items():
                print(f"  {position:6} {player}")
            
            # Display projections
            proj_range = strategy.projected_range
            print(Colors.bold(f"\n📈 PROJECTED POINTS:") + 
                  f" {proj_range[0]:.1f} - {proj_range[1]:.1f}")
            
            # Display metrics
            print(Colors.bold(f"⚠️  RISK LEVEL:") + 
                  f" {strategy.risk_level}/10")
            print(Colors.bold(f"🎯 CONFIDENCE:") + 
                  f" {strategy.confidence}%")
            
            # Display reasoning
            print(Colors.bold("\n💡 REASONING:"))
            print(f"  {strategy.reasoning}")
            
            # Display pros/cons
            print(Colors.GREEN + "\n✓ PROS:")
            for pro in strategy.pros:
                print(f"  • {pro}")
            
            print(Colors.WARNING + "\n✗ CONS:")
            for con in strategy.cons:
                print(f"  • {con}")
        
        print(Colors.CYAN + "\n" + "="*60 + Colors.ENDC)
        print(Colors.bold("\n📝 NEXT STEPS:"))
        print("1. Review the recommendations above")
        print("2. Choose your preferred strategy")
        print("3. Manually set your lineup in the Sleeper app")
        print("4. Good luck! 🍀")
        
        # Export options
        self._handle_export_options(result)
        
        input("\n\nPress Enter to return to main menu...")
    
    def _handle_export_options(self, result: Any) -> None:
        """Handle export options for analysis results."""
        print(Colors.bold("\n💾 EXPORT OPTIONS:"))
        print("1. Export to JSON")
        print("2. Export to CSV")
        print("3. Export to TXT")
        print("4. Skip export")
        
        choice = self.get_user_choice(4, "\nEnter choice (1-4): ")
        if choice is None or choice == 4:
            return
        
        formats = ["json", "csv", "txt"]
        export_format = formats[choice - 1]
        
        try:
            exported_data = self.optimizer.export_analysis(result, export_format)
            if exported_data:
                filename = f"lineup_analysis_{export_format}.{export_format}"
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(exported_data)
                print(Colors.success(f"✓ Analysis exported to {filename}"))
            else:
                print(Colors.error("✗ Failed to export analysis"))
        except Exception as e:
            print(Colors.error(f"✗ Export failed: {e}"))
    
    def show_trending_players(self) -> None:
        """Show trending players."""
        self.print_header()
        print(Colors.bold("📈 TRENDING PLAYERS\n"))
        
        trending = self.optimizer.get_trending_players()
        
        if not trending:
            print(Colors.warning("No trending players found"))
            input("\nPress Enter to continue...")
            return
        
        print("Top 10 Most Added Players (Last 24 Hours):\n")
        for i, trend in enumerate(trending[:10], 1):
            print(f"{i:2}. {trend['name']:20} {trend['position']:3} - {trend['team']:3} "
                  f"(Added {trend['add_count']:,} times)")
        
        input("\nPress Enter to continue...")
    
    def show_cache_info(self) -> None:
        """Show cache information."""
        self.print_header()
        print(Colors.bold("🗄️  CACHE INFORMATION\n"))
        
        cache_info = self.optimizer.get_cache_info()
        
        if not cache_info:
            print(Colors.warning("Cache information not available"))
            input("\nPress Enter to continue...")
            return
        
        print(f"Cache Enabled: {'Yes' if cache_info['enabled'] else 'No'}")
        print(f"Cache Size: {cache_info['size_mb']} MB")
        print(f"Cache Duration: {cache_info['duration_hours']} hours")
        
        if cache_info['enabled'] and cache_info['size_mb'] > 0:
            print(f"\nOptions:")
            print("1. Clear cache")
            print("2. Back")
            
            choice = self.get_user_choice(2, "\nEnter choice (1-2): ")
            if choice == 1:
                if self.optimizer.clear_cache():
                    print(Colors.success("✓ Cache cleared successfully"))
                else:
                    print(Colors.error("✗ Failed to clear cache"))
                input("\nPress Enter to continue...")
    
    def show_provider_info(self) -> None:
        """Show AI provider information."""
        self.print_header()
        print(Colors.bold("🤖 AI PROVIDER INFORMATION\n"))
        
        provider_info = self.optimizer.get_provider_info()
        
        if not provider_info:
            print(Colors.warning("Provider information not available"))
            input("\nPress Enter to continue...")
            return
        
        print(f"Provider: {provider_info['name']}")
        print(f"Type: {provider_info['type']}")
        print(f"Configured: {'Yes' if provider_info['configured'] else 'No'}")
        
        input("\nPress Enter to continue...")
    
    def update_configuration(self) -> None:
        """Update configuration."""
        self.print_header()
        print(Colors.bold("⚙️  UPDATE CONFIGURATION\n"))
        
        print("This will reset your current configuration.")
        print("Are you sure you want to continue?")
        print("1. Yes, reset configuration")
        print("2. No, keep current configuration")
        
        choice = self.get_user_choice(2, "\nEnter choice (1-2): ")
        if choice == 1:
            self.config_manager.delete_config()
            new_password = self.setup_initial_config()
            if new_password:
                self.password = new_password
                if self.optimizer.initialize(new_password):
                    print(Colors.success("✓ Configuration updated successfully"))
                else:
                    print(Colors.error("✗ Failed to initialize with new configuration"))
            input("\nPress Enter to continue...")
    
    def run(self) -> None:
        """Main application loop."""
        try:
            # Load configuration
            if not self.load_configuration():
                print(Colors.error("Failed to load configuration"))
                return
            
            # Initialize optimizer
            if not self.optimizer.initialize():
                print(Colors.error("Failed to initialize optimizer"))
                return
            
            # Main loop
            while True:
                self.print_header()
                print(Colors.bold(f"Welcome, {self.optimizer.config.sleeper_username}!\n"))
                
                print("What would you like to do?\n")
                print("1. Optimize Lineup")
                print("2. View Trending Players")
                print("3. Cache Information")
                print("4. AI Provider Info")
                print("5. Update Configuration")
                print("6. Exit")
                
                choice = self.get_user_choice(6, "\nEnter choice (1-6): ")
                if choice is None:
                    break
                
                if choice == 1:
                    # Select league
                    league = self.select_league()
                    if not league:
                        continue
                    
                    # Select week
                    week = self.select_week()
                    if week is None:
                        continue
                    
                    # Analyze matchup
                    self.print_header()
                    print(Colors.bold(f"Analyzing Week {week} Matchup...\n"))
                    
                    result = self.optimizer.analyze_week(week)
                    if result:
                        self.display_results(result, week)
                    else:
                        print(Colors.error("Analysis failed. Please try again."))
                        input("\nPress Enter to continue...")
                
                elif choice == 2:
                    self.show_trending_players()
                
                elif choice == 3:
                    self.show_cache_info()
                
                elif choice == 4:
                    self.show_provider_info()
                
                elif choice == 5:
                    self.update_configuration()
                
                elif choice == 6:
                    print(Colors.success("\nThanks for using Sleeper AI Lineup Optimizer!"))
                    print("Good luck with your fantasy season! 🏈")
                    break
                
        except KeyboardInterrupt:
            print("\n\nExiting...")
        except Exception as e:
            logger.error(f"CLI error: {e}")
            print(f"\n{Colors.error(f'Error: {e}')}")
            input("\nPress Enter to exit...")


def main() -> None:
    """Entry point for CLI application."""
    try:
        cli = CLIInterface()
        cli.run()
    except Exception as e:
        logger.error(f"Application error: {e}")
        print(f"\n{Colors.error(f'Application error: {e}')}")
        input("\nPress Enter to exit...")


if __name__ == "__main__":
    main()
