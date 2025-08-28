"""Main entry point for the Sleeper AI Lineup Optimizer."""

import sys
import os
from pathlib import Path

# Add the src directory to the Python path
src_dir = Path(__file__).parent
sys.path.insert(0, str(src_dir))

from src.ui.cli import main as cli_main
from src.utils.logger import setup_logger

def main():
    """Main entry point for the application."""
    try:
        # Set up logging
        log_file = Path.home() / ".sleeper_optimizer" / "app.log"
        setup_logger(
            name="sleeper_optimizer",
            level="INFO",
            log_file=log_file,
            console_output=True
        )
        
        # Run CLI interface
        cli_main()
        
    except KeyboardInterrupt:
        print("\n\nExiting...")
        sys.exit(0)
    except Exception as e:
        print(f"\nFatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
