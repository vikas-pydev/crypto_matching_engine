from setuptools import setup, find_packages

setup(
    name="crypto_matching_engine",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "sortedcontainers",  # Required for order book price levels
        "pydantic",         # Required for data validation
        "loguru",          # Required for logging
    ],
)