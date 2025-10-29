"""Setup script for StatSQLi."""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="statsqli",
    version="1.0.0",
    author="StatSQLi Team",
    description="Statistical Time-Based Blind SQL Injection Tool",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/statsqli",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "Topic :: Security",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.28.0",
        "numpy>=1.23.0",
        "scipy>=1.9.0",
    ],
    entry_points={
        "console_scripts": [
            "statsqli=statsqli.main:main",
        ],
    },
)

