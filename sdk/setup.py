"""
Newton SDK Setup

Installation:
    pip install .

Or from GitHub:
    pip install git+https://github.com/jaredlewiswechs/Newton-api.git#subdirectory=sdk

Or directly:
    pip install newton-sdk
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="newton-sdk",
    version="3.0.0",
    author="Newton Verified Computation Engine",
    author_email="newton@example.com",
    description="Auto-discovering SDK for Newton Verified Computation Engine",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/jaredlewiswechs/Newton-api",
    packages=find_packages(),
    py_modules=["newton"],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.25.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "mypy>=1.0.0",
        ]
    },
    entry_points={
        "console_scripts": [
            "newton=newton:main",
        ],
    },
    keywords="newton verified computation ai sdk api",
    project_urls={
        "Bug Reports": "https://github.com/jaredlewiswechs/Newton-api/issues",
        "Source": "https://github.com/jaredlewiswechs/Newton-api",
        "Documentation": "https://newton-api.onrender.com/docs",
    },
)
