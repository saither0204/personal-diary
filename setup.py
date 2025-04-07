#!/usr/bin/env python3
"""
Setup script for Personal Diary application.
"""
from setuptools import setup, find_packages

setup(
    name="personal-diary",
    version="1.0.0",
    description="A secure personal diary application with encryption",
    author="Sarthak",
    author_email="your.email@example.com",  # Update with your email
    packages=find_packages(),
    install_requires=[
        "cryptography",
    ],
    entry_points={
        "console_scripts": [
            "personal-diary=diary_app:main",
        ],
    },
    python_requires=">=3.6",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "Topic :: Office/Business :: News/Diary",
    ],
)
