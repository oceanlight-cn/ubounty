from setuptools import setup, find_packages

setup(
    name="ubounty",
    version="0.1.0",
    description="Enable maintainers to clear their backlog with one command",
    packages=find_packages(),
    install_requires=[
        "click>=8.0.0",
        "rich>=13.0.0",
        "requests>=2.28.0",
    ],
    entry_points={
        "console_scripts": [
            "ubounty=ubounty.cli:main",
        ],
    },
    python_requires=">=3.8",
)
