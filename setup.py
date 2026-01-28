"""Setup configuration for timealready"""
from setuptools import setup, find_packages
from pathlib import Path

# Read README for long description
readme = Path("README.md").read_text(encoding="utf-8")

setup(
    name="timealready",
    version="1.0.0",
    author="timealready",
    description="Stop explaining the same errors to AI. Store fixes once, retrieve instantly forever.",
    long_description=readme,
    long_description_content_type="text/markdown",
    url="https://github.com/justin55afdfdsf5ds45f4ds5f45ds4/timealready",
    packages=find_packages(exclude=["tests"]),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Debuggers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.8",
    install_requires=[
        "replicate>=0.25.0",
        "httpx>=0.27.0",
        "python-dotenv>=1.0.0",
    ],
    entry_points={
        "console_scripts": [
            "timealready=timealready:cli_entry",
        ],
    },
    keywords=[
        "ai",
        "debugging",
        "error-fixing",
        "developer-tools",
        "memory",
        "ultracontext",
        "replicate",
        "cli",
    ],
)
