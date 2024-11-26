from setuptools import setup, find_packages

setup(
    name="re-investment-analyzer",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "requests>=2.25.1",
        "pandas>=1.2.0",
        "numpy>=1.19.0",
    ],
    python_requires=">=3.8",
)
