# Sleeper AI Lineup Optimizer - Documentation

Welcome to the documentation for the Sleeper AI Lineup Optimizer! This document provides comprehensive information about the project, its architecture, and how to use it.

## 📚 Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Installation](#installation)
4. [Configuration](#configuration)
5. [Usage](#usage)
6. [API Reference](#api-reference)
7. [Development](#development)
8. [Troubleshooting](#troubleshooting)

## 🎯 Overview

The Sleeper AI Lineup Optimizer is a Python application that uses artificial intelligence to analyze fantasy football lineups and provide strategic recommendations. It integrates with the Sleeper API to fetch real-time fantasy football data and uses AI services (OpenAI GPT-4, Anthropic Claude, or mock analysis) to generate lineup optimization strategies.

### Key Features

- **AI-Powered Analysis**: Multiple AI provider options
- **Real-Time Data**: Live integration with Sleeper API
- **Strategic Recommendations**: Three different lineup strategies
- **Secure Storage**: Encrypted configuration management
- **Cross-Platform**: Works on Windows, macOS, and Linux
- **Export Options**: Multiple output formats

## 🏗️ Architecture

### Project Structure

```
src/
├── api/                    # External API integrations
│   ├── sleeper.py         # Sleeper API wrapper
│   └── ai_providers.py    # AI service providers
├── core/                   # Business logic
│   ├── optimizer.py       # Main optimizer
│   └── analyzer.py        # Lineup analysis
├── utils/                  # Utilities
│   ├── config.py          # Configuration management
│   ├── encryption.py      # Data encryption
│   └── logger.py          # Logging utilities
└── ui/                     # User interface
    ├── cli.py             # Command-line interface
    └── colors.py          # Terminal colors
```

### Core Components

1. **SleeperAPI**: Handles all interactions with the Sleeper fantasy football API
2. **AIAnalyzer**: Manages AI provider integrations and analysis
3. **LineupAnalyzer**: Core business logic for lineup analysis
4. **LineupOptimizer**: Main orchestrator for the optimization process
5. **CLIInterface**: User interface for command-line interaction

### Data Flow

```
User Input → CLI Interface → Lineup Optimizer → Lineup Analyzer → AI Analyzer → AI Provider
                                    ↓
                            Sleeper API → Player Data, Rosters, Matchups
                                    ↓
                            Results Display ← Export Options
```

## 🚀 Installation

### Prerequisites

- Python 3.8 or higher
- Sleeper fantasy football account
- OpenAI API key (optional) or Anthropic API key (optional)

### Quick Install

```bash
# Clone the repository
git clone https://github.com/yourusername/sleeper-ai-lineup-optimizer.git
cd sleeper-ai-lineup-optimizer

# Install dependencies
pip install -r requirements.txt

# Run the application
python -m src.main
```

### Development Install

```bash
# Install development dependencies
pip install -e ".[dev]"

# Setup pre-commit hooks
pre-commit install

# Run tests
pytest
```

## ⚙️ Configuration

### First-Time Setup

When you first run the application, it will guide you through setup:

1. **Choose AI Provider**
   - OpenAI GPT-4 (requires API key)
   - Anthropic Claude (requires API key)
   - Mock Analysis (no API required)

2. **Enter Sleeper Username**
   - Your Sleeper fantasy football username

3. **Create Encryption Password**
   - This password encrypts your API keys and settings

### Configuration Options

The application stores configuration in `~/.sleeper_optimizer/config.encrypted`:

| Option | Description | Default |
|--------|-------------|---------|
| `ai_provider` | AI service to use | `mock` |
| `ai_api_key` | API key for the selected provider | `""` |
| `sleeper_username` | Your Sleeper username | `""` |
| `cache_enabled` | Enable/disable data caching | `true` |
| `cache_duration_hours` | How long to cache data | `24` |
| `max_retries` | API request retry attempts | `3` |
| `request_timeout` | API request timeout (seconds) | `30` |

### Environment Variables

You can also set configuration via environment variables:

```bash
export SLEEPER_USERNAME="your_username"
export OPENAI_API_KEY="your_openai_key"
export ANTHROPIC_API_KEY="your_anthropic_key"
```

## 💻 Usage

### Basic Usage

```bash
# Run the application
python -m src.main

# Or if installed as a package
sleeper-optimizer
```

### Main Menu Options

1. **Optimize Lineup**: Analyze your lineup for a specific week
2. **View Trending Players**: See the most added/dropped players
3. **Cache Information**: View and manage cached data
4. **AI Provider Info**: Check AI provider status
5. **Update Configuration**: Modify your settings
6. **Exit**: Close the application

### Lineup Optimization Process

1. **Select League**: Choose from your available leagues
2. **Select Week**: Pick the NFL week to analyze
3. **Analysis**: AI analyzes your roster and opponent
4. **Results**: View three strategic recommendations
5. **Export**: Save results in your preferred format

### Export Formats

- **JSON**: Structured data for programmatic use
- **CSV**: Spreadsheet-compatible format
- **TXT**: Human-readable plain text

## 🔌 API Reference

### SleeperAPI Class

```python
class SleeperAPI:
    """Handles all Sleeper API interactions."""
    
    def get_user(username: str) -> Optional[Dict[str, Any]]
    def get_user_leagues(user_id: str, season: str = "2024") -> List[Dict[str, Any]]
    def get_league(league_id: str) -> Optional[Dict[str, Any]]
    def get_rosters(league_id: str) -> List[Dict[str, Any]]
    def get_matchups(league_id: str, week: int) -> List[Dict[str, Any]]
    def get_players() -> Dict[str, Any]
    def get_trending_players(lookback_hours: int = 24, limit: int = 25) -> List[Dict[str, Any]]
```

### AIAnalyzer Class

```python
class AIAnalyzer:
    """Main AI analyzer that manages different providers."""
    
    def analyze_lineup(context: Dict[str, Any]) -> AnalysisResult
    def get_provider_info() -> Dict[str, str]
```

### LineupOptimizer Class

```python
class LineupOptimizer:
    """Main application class that orchestrates lineup optimization."""
    
    def initialize(password: str) -> bool
    def analyze_week(week: int) -> Optional[AnalysisResult]
    def get_trending_players(lookback_hours: int = 24, limit: int = 25) -> List[Dict[str, Any]]
    def export_analysis(result: AnalysisResult, format: str = "json") -> Optional[str]
```

## 🛠️ Development

### Setting Up Development Environment

```bash
# Clone and setup
git clone https://github.com/yourusername/sleeper-ai-lineup-optimizer.git
cd sleeper-ai-lineup-optimizer

# Install development dependencies
pip install -e ".[dev]"

# Setup pre-commit hooks
pre-commit install

# Run code quality checks
make check
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test categories
pytest -m "unit"      # Unit tests only
pytest -m "integration"  # Integration tests only
```

### Code Quality

```bash
# Format code
black src/ tests/

# Check linting
flake8 src/ tests/

# Check types
mypy src/

# Run all checks
make check
```

### Building Executable

```bash
# Build executable
pyinstaller sleeper_optimizer.spec

# Or use make
make build
```

## 🔧 Troubleshooting

### Common Issues

#### Configuration Problems

**Issue**: "Invalid password or corrupted config"
- **Solution**: Reset your configuration and set it up again

**Issue**: "API key required for [provider]"
- **Solution**: Ensure you've entered the correct API key for your chosen provider

#### API Connection Issues

**Issue**: "Failed to get user [username]"
- **Solution**: Verify your Sleeper username is correct and you have internet access

**Issue**: "Request timeout after X attempts"
- **Solution**: Check your internet connection and try again later

#### AI Analysis Issues

**Issue**: "AI analysis failed"
- **Solution**: Check your API key and provider configuration

**Issue**: "Failed to parse AI response"
- **Solution**: The AI provider may have returned an unexpected format; try again

### Debug Mode

Enable debug logging by modifying the log level in your configuration:

```python
# In your config
log_level = "DEBUG"
```

### Getting Help

1. **Check the logs**: Look in `~/.sleeper_optimizer/app.log`
2. **Search issues**: Check GitHub Issues for similar problems
3. **Ask questions**: Use GitHub Discussions
4. **Report bugs**: Create a new issue with detailed information

## 📖 Additional Resources

- [Sleeper API Documentation](https://docs.sleeper.com/)
- [OpenAI API Documentation](https://platform.openai.com/docs)
- [Anthropic API Documentation](https://docs.anthropic.com/)
- [Python Documentation](https://docs.python.org/)
- [Pytest Documentation](https://docs.pytest.org/)

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](../CONTRIBUTING.md) for detailed information on how to contribute to the project.

## 📄 License

This project is licensed under the MIT License. See [LICENSE](../LICENSE) for details.

---

For more information or support, please visit our [GitHub repository](https://github.com/yourusername/sleeper-ai-lineup-optimizer).
