from setuptools import setup, find_packages

setup(
    name="autonomous-data-agency",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "langchain>=0.1.0",
        "langchain-openai>=0.0.5",
        "langchain-core>=0.1.0",
        "langgraph>=0.0.20",
        "openai>=1.0.0",
        "google-generativeai>=0.3.0",
        "python-dotenv>=1.0.0",
        "pydantic>=2.0.0",
        "pandas>=2.0.0",
        "numpy>=1.24.0",
        "pyyaml>=6.0",
        "chromadb>=0.4.0",
        "aiohttp>=3.9.0",
        "typing-extensions>=4.0.0",
        "typer>=0.9.0",
        "rich>=13.0.0",
    ],
)
