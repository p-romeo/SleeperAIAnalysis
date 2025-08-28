"""Terminal color constants for CLI output."""


class Colors:
    """ANSI color codes for terminal output."""
    
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    
    @classmethod
    def colorize(cls, text: str, color: str) -> str:
        """Apply color to text."""
        return f"{color}{text}{cls.ENDC}"
    
    @classmethod
    def bold(cls, text: str) -> str:
        """Make text bold."""
        return cls.colorize(text, cls.BOLD)
    
    @classmethod
    def success(cls, text: str) -> str:
        """Format success message."""
        return cls.colorize(text, cls.GREEN)
    
    @classmethod
    def error(cls, text: str) -> str:
        """Format error message."""
        return cls.colorize(text, cls.FAIL)
    
    @classmethod
    def warning(cls, text: str) -> str:
        """Format warning message."""
        return cls.colorize(text, cls.WARNING)
    
    @classmethod
    def info(cls, text: str) -> str:
        """Format info message."""
        return cls.colorize(text, cls.CYAN)
