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
    ],
    python_requires=">=3.11",
    install_requires=[
        "langchain>=0.1.0",
        "langchain-openai>=0.0.2",
        "langgraph>=0.0.20",
        "pydantic>=2.0.0",
        "python-dotenv>=1.0.0",
        "typing-extensions>=4.8.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-asyncio>=0.21.0",
            "pytest-cov>=4.1.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.5.0",
            "isort>=5.12.0",
        ],
    },
)
