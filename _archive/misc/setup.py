from setuptools import setup, find_packages

setup(
    name="realtinytalk",
    version="1.0.0",
    description="A lightweight programming language with a Monaco-powered web IDE.",
    long_description=open("realTinyTalk/TINYTALK_GUIDE.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="Your Name",
    author_email="your.email@example.com",
    url="https://github.com/yourusername/realtinytalk",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "flask>=2.0.0",
        "monaco-editor>=0.33.0",
    ],
    entry_points={
        "console_scripts": [
            "realtinytalk=realtinytalk.cli:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)