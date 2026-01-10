"""Setup script for autonomous-data-agency."""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="autonomous-data-agency",
    version="0.1.0",
    author="Michael Eng AI",
    description="A framework for orchestrating hierarchical teams of AI agents",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/michael-eng-ai/autonomous-data-agency",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.11",
    install_requires=[
        "langchain>=0.1.0",
        "langchain-openai>=0.0.5",
        "langchain-core>=0.1.0",
        "langgraph>=0.0.20",
        "openai>=1.0.0",
        "google-generativeai>=0.3.0",
        "pydantic>=2.0.0",
        "pandas>=2.0.0",
        "numpy>=1.24.0",
        "pyyaml>=6.0",
        "chromadb>=0.4.0",
        "aiohttp>=3.9.0",
        "python-dotenv>=1.0.0",
        "typing-extensions>=4.8.0",
        "typer>=0.9.0",
        "rich>=13.0.0",
        "fastapi>=0.100.0",
        "uvicorn>=0.20.0",
        "websockets>=11.0",
        "python-multipart>=0.0.6",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-asyncio>=0.21.0",
            "pytest-cov>=4.1.0",
            "pytest-mock>=3.10.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.5.0",
            "isort>=5.12.0",
        ],
    },
)
