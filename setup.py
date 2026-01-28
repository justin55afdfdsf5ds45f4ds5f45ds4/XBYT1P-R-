"""Setup configuration for XBYT1P&%R$@"""
from setuptools import setup, find_packages
from pathlib import Path

# Read README for long description
readme = Path("README.md").read_text(encoding="utf-8")

setup(
    name="xbyt1p",
    version="1.0.0",
    author="XBYT1P Team",
    author_email="hello@xbyt1p.dev",
    description="AI agent that learns from mistakes and fixes bugs autonomously",
    long_description=readme,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/xbyt1p",
    packages=find_packages(exclude=["tests", "test_project"]),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Debuggers",
        "Topic :: Software Development :: Quality Assurance",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.9",
    install_requires=[
        "pydantic>=2.0.0",
        "replicate>=0.25.0",
        "python-dotenv>=1.0.0",
        "e2b-code-interpreter>=0.0.10",
    ],
    entry_points={
        "console_scripts": [
            "xbyt1p=codehealer:cli_entry",
        ],
    },
    keywords=[
        "ai",
        "debugging",
        "code-fixing",
        "autonomous-agents",
        "machine-learning",
        "developer-tools",
        "error-handling",
        "sandbox",
        "replicate",
        "e2b",
        "ultracontext",
    ],
)
