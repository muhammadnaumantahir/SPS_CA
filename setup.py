"""
SPS-CA: Self-Programming Code Assistant
Setup configuration for package installation and distribution.
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="sps-ca",
    version="0.1.0",
    author="Muhammad Nauman Tahir",
    author_email="your_email@virtualuniversity.edu.pk",
    description="Self-Programming Software Prototype - Reference framework for AI-driven code modification and evolution",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/muhammadnaumantahir/SPS_CA",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Topic :: Software Development :: Code Generators",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.11",
    install_requires=[
        "tree-sitter>=0.21.0",
        "tree-sitter-python>=0.21.0",
        "tree-sitter-javascript>=0.21.1",
        "tree-sitter-java>=0.21.0",
        "tree-sitter-go>=0.21.0",
        "tree-sitter-cpp>=0.21.0",
        "pydantic>=2.5.0",
        "requests>=2.31.0",
        "pytest>=7.4.3",
        "pytest-cov>=4.1.0",
        "sqlalchemy>=2.0.23",
        "dataclasses-json>=0.6.1",
        "click>=8.1.7",
        "rich>=13.7.0",
        "python-dotenv>=1.0.0",
    ],
    extras_require={
        "dev": [
            "black>=23.12.0",
            "pylint>=3.0.3",
            "mypy>=1.7.1",
            "isort>=5.13.2",
            "pytest-asyncio>=0.21.1",
        ],
        "docs": [
            "sphinx>=7.2.6",
        ],
    },
    entry_points={
        "console_scripts": [
            "sps-ca=ui.cli_interface:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
