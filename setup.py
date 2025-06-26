from setuptools import setup, find_packages

setup(
    name="gmaps-scraper",
    version="1.0.0",
    description="Google Maps business data scraper using Selenium",
    author="Your Name",
    author_email="your.email@example.com",
    packages=find_packages(),
    install_requires=[
        "selenium>=4.15.0",
        "webdriver-manager>=4.0.1",
        "pandas>=2.1.0",
        "python-dotenv>=1.0.0",
        "requests>=2.31.0",
        "fake-useragent>=1.4.0",
        "beautifulsoup4>=4.12.2",
        "lxml>=4.9.3",
        "openpyxl>=3.1.2",
        "colorama>=0.4.6"
    ],
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "gmaps-scraper=main:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
)