from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="sleeper-ai-lineup-optimizer",
    version="1.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="AI-powered fantasy football lineup optimizer using Sleeper API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/sleeper-ai-lineup-optimizer",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Games/Entertainment",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-asyncio>=0.21.0",
            "pytest-cov>=4.1.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.5.0",
        ],
        "build": [
            "pyinstaller>=5.13.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "sleeper-optimizer=sleeper_ai_lineup_optimizer.main:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
