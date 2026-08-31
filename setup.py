"""SPS-CA package configuration."""

from setuptools import find_packages, setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="sps-ca",
    version="0.2.0",
    author="Muhammad Nauman Tahir",
    description="Research prototype for a governed self-programming coding assistant.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/muhammadnaumantahir/SPS_CA",
    packages=find_packages(),
    python_requires=">=3.11",
    install_requires=[
        "tree-sitter>=0.25.0",
        "tree-sitter-python>=0.23.0",
        "tree-sitter-javascript>=0.23.0",
        "tree-sitter-typescript>=0.23.0",
        "tree-sitter-java>=0.23.0",
        "tree-sitter-go>=0.23.0",
        "tree-sitter-c-sharp>=0.23.0",
        "pydantic>=2.5.0",
        "pydantic-settings>=2.1.0",
        "python-dotenv>=1.0.0",
        "requests>=2.31.0",
        "httpx>=0.25.1",
        "sqlalchemy>=2.0.23",
        "dataclasses-json>=0.6.1",
        "jsonschema>=4.20.0",
        "click>=8.1.7",
        "rich>=13.7.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.3",
            "pytest-cov>=4.1.0",
            "pytest-asyncio>=0.21.1",
            "pytest-timeout>=2.1.0",
            "black>=23.12.0",
            "pylint>=3.0.3",
            "mypy>=1.7.1",
            "isort>=5.13.2",
        ],
        "docs": ["sphinx>=7.2.6"],
    },
    include_package_data=True,
    zip_safe=False,
)
