# Sleeper AI Lineup Optimizer 🏈🤖

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Type checked with mypy](https://img.shields.io/badge/mypy-checked-blue)](https://mypy-lang.org/)

> **AI-powered fantasy football lineup optimizer using the Sleeper API**

Transform your fantasy football strategy with AI-driven insights! This application analyzes your roster, opponent, and league settings to provide three strategic lineup recommendations with detailed pros/cons analysis.

## ✨ Features

- **🤖 AI-Powered Analysis**: Choose between OpenAI GPT-4, Anthropic Claude, or mock analysis
- **📊 Smart Lineup Optimization**: Get 3 strategic approaches (Safe Floor, High Ceiling, Balanced)
- **🔒 Secure Configuration**: Encrypted storage of API keys and settings
- **💾 Intelligent Caching**: Local caching of player data to reduce API calls
- **📈 Trending Players**: Track the most added/dropped players
- **📤 Export Options**: Export results to JSON, CSV, or plain text
- **🔄 Retry Logic**: Robust error handling with exponential backoff
- **📱 Cross-Platform**: Works on Windows, macOS, and Linux

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- Sleeper fantasy football account
- OpenAI API key (optional) or Anthropic API key (optional)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/sleeper-ai-lineup-optimizer.git
   cd sleeper-ai-lineup-optimizer
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   python -m src.main
   ```

### First-Time Setup

1. **Choose AI Provider**
   - OpenAI GPT-4 (requires API key)
   - Anthropic Claude (requires API key)
   - Mock Analysis (no API required, for testing)

2. **Enter Sleeper Username**
   - Your Sleeper fantasy football username

3. **Create Encryption Password**
   - This password encrypts your API keys and settings

## 🎯 How It Works

### 1. Data Collection
- Fetches your roster from Sleeper API
- Retrieves opponent's projected lineup
- Gathers league scoring settings
- Loads comprehensive player database

### 2. AI Analysis
- Builds context-aware prompts
- Analyzes matchup scenarios
- Considers player matchups and trends
- Generates strategic recommendations

### 3. Strategy Generation
- **Safe Floor**: Minimize risk with consistent performers
- **High Ceiling**: Maximize upside for comeback scenarios
- **Balanced**: Optimal risk/reward balance

### 4. Results Display
- Detailed lineup recommendations
- Projected point ranges
- Risk assessment (1-10 scale)
- Confidence levels (0-100%)
- Pros and cons for each strategy

## 🔧 Configuration

### AI Providers

#### OpenAI GPT-4
```bash
# Get API key from: https://platform.openai.com/api-keys
export OPENAI_API_KEY="your-api-key-here"
```

#### Anthropic Claude
```bash
# Get API key from: https://console.anthropic.com/
export ANTHROPIC_API_KEY="your-api-key-here"
```

#### Mock Provider
- No API key required
- Perfect for testing and development
- Generates realistic sample data

### Configuration Options

The application stores configuration in `~/.sleeper_optimizer/config.encrypted`:

- `ai_provider`: AI service to use
- `ai_api_key`: API key for the selected provider
- `sleeper_username`: Your Sleeper username
- `cache_enabled`: Enable/disable data caching
- `cache_duration_hours`: How long to cache data
- `max_retries`: API request retry attempts
- `request_timeout`: API request timeout (seconds)

## 📁 Project Structure

```
sleeper-ai-lineup-optimizer/
├── src/                          # Source code
│   ├── __init__.py
│   ├── main.py                   # Application entry point
│   ├── api/                      # External API integrations
│   │   ├── __init__.py
│   │   ├── sleeper.py           # Sleeper API wrapper
│   │   └── ai_providers.py      # AI service providers
│   ├── core/                     # Business logic
│   │   ├── __init__.py
│   │   ├── optimizer.py         # Main optimizer
│   │   └── analyzer.py          # Lineup analysis
│   ├── utils/                    # Utilities
│   │   ├── __init__.py
│   │   ├── config.py            # Configuration management
│   │   ├── encryption.py        # Data encryption
│   │   └── logger.py            # Logging utilities
│   └── ui/                      # User interface
│       ├── __init__.py
│       ├── cli.py               # Command-line interface
│       └── colors.py            # Terminal colors
├── tests/                        # Test suite
├── docs/                         # Documentation
├── requirements.txt              # Python dependencies
├── setup.py                     # Package setup
├── pyproject.toml               # Project configuration
└── README.md                    # This file
```

## 🧪 Testing

### Run Tests
```bash
# Install test dependencies
pip install -e ".[dev]"

# Run all tests
pytest

# Run with coverage
pytest --cov=src

# Run specific test categories
pytest -m "unit"      # Unit tests only
pytest -m "integration"  # Integration tests only
```

### Test Coverage
- Unit tests for each module
- Integration tests for API calls
- Mock tests for AI responses
- Edge case testing

## 🚀 Building

### Create Executable
```bash
# Install build dependencies
pip install -e ".[build]"

# Build executable
pyinstaller --onefile src/main.py --name sleeper-optimizer
```

### Distribution
The built executable will be in `dist/sleeper-optimizer` and can be distributed to users without requiring Python installation.

## 🔒 Security Features

- **Encrypted Configuration**: All sensitive data is encrypted using PBKDF2 + Fernet
- **Secure API Key Storage**: API keys are never stored in plain text
- **Input Validation**: All user inputs are validated and sanitized
- **Rate Limiting**: Built-in rate limiting for API calls
- **Secure Logging**: Sensitive data is never logged

## 📊 Performance Features

- **Intelligent Caching**: Player data cached locally (5MB dataset)
- **Async Operations**: Non-blocking API calls where possible
- **Connection Pooling**: Efficient HTTP connection management
- **Progress Indicators**: Visual feedback for long operations

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Setup
```bash
# Clone and setup
git clone https://github.com/yourusername/sleeper-ai-lineup-optimizer.git
cd sleeper-ai-lineup-optimizer

# Install development dependencies
pip install -e ".[dev]"

# Setup pre-commit hooks
pre-commit install

# Run code quality checks
black src/ tests/
flake8 src/ tests/
mypy src/
```

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Sleeper API**: For providing the fantasy football data
- **OpenAI**: For GPT-4 AI capabilities
- **Anthropic**: For Claude AI capabilities
- **Fantasy Football Community**: For inspiration and feedback

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/sleeper-ai-lineup-optimizer/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/sleeper-ai-lineup-optimizer/discussions)
- **Wiki**: [Project Wiki](https://github.com/yourusername/sleeper-ai-lineup-optimizer/wiki)

## 🔮 Roadmap

- [ ] **Web Interface**: Browser-based UI
- [ ] **Mobile App**: iOS/Android applications
- [ ] **Historical Tracking**: Track recommendation accuracy
- [ ] **Multi-League Support**: Analyze multiple leagues simultaneously
- [ ] **Advanced Analytics**: Player correlation analysis
- [ ] **Weather Integration**: Weather impact on player performance
- [ ] **Injury Updates**: Real-time injury status integration
- [ ] **Trade Analyzer**: AI-powered trade recommendations

---

**Made with ❤️ for fantasy football enthusiasts**

*Good luck with your fantasy season! 🏈🍀*
