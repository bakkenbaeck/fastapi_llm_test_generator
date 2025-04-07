from setuptools import find_packages, setup

setup(
    name="llm-test-generator-tool",
    version="0.0.1",
    description="A tool to generate tests from fastapi using LLMs",
    author="Nico Lutz",
    author_email="nico@bakkenbaeck.no",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    packages=find_packages(
        include=["fastapi_llm_test_generator", "fastapi_llm_test_generator.*"]
    ),
    include_package_data=True,
    python_requires=">=3.10.0",
    install_requires=[
        "catalogue>=2.0.10",
        "rich-toolkit>=0.14.1",
        "typer>=0.15.2",
    ],
    extras_require={
        "anthropic": ["anthropic>=0.49.0"],
        "asyncpg": ["asyncio>=3.4.3", "asyncpg>=0.30.0"],
        "psycopg2": ["psycopg2>=2.9.10"],
    },
    entry_points={
        "console_scripts": [
            "fastapi-llm-test-generator=fastapi_llm_test_generator.__main__:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "Framework :: FastAPI",
    ],
)
