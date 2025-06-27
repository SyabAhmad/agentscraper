from setuptools import setup, find_packages

setup(
    name="agentscraper",
    version="0.1.0",
    author="Syed Syab Ahmad, Sania Shakeel",
    author_email="Syab.se@hotmail.com, ayashal551@gmail.com",
    description="Agent-based Google scraper with LLM integration",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/SyabAhmad/agentscraper",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[
        "crewai>=0.1.0",
        "requests>=2.25.0",
        "beautifulsoup4>=4.9.0",
        "groq>=0.4.0",
        "lxml>=4.6.0",
    ],
    extras_require={
        "selenium": ["selenium>=4.0.0", "webdriver-manager>=3.8.0"],
    },
)