"""
Newton SDK Setup
================

Install with:
    pip install newton-sdk
    
Or from source:
    pip install -e .
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="newton-sdk",
    version="1.0.0",
    author="Newton",
    author_email="sdk@newton.dev",
    description="Verified computation for everyone",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/newton/newton-sdk",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering",
    ],
    python_requires=">=3.9",
    install_requires=[
        # No required dependencies - pure Python
    ],
    extras_require={
        "grounding": ["googlesearch-python>=1.2.0"],
        "dev": [
            "pytest>=7.0.0",
            "hypothesis>=6.0.0",
            "black>=23.0.0",
            "mypy>=1.0.0",
        ],
    },
    keywords=[
        "verification",
        "constraints",
        "computation",
        "newton",
        "validated",
        "bounded",
    ],
    project_urls={
        "Bug Tracker": "https://github.com/newton/newton-sdk/issues",
        "Documentation": "https://newton.dev/docs",
        "Source": "https://github.com/newton/newton-sdk",
    },
)
