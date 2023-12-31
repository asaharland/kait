"""KAIT - Kubernetes AI Tool."""
from setuptools import setup, find_packages

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = fh.read()

with open("README.md", "r", encoding="UTF-8") as fh:
    long_description = fh.read()

setup(
    name="kait",
    version="0.2.1",
    author="Asa Harland",
    author_email="asajharland@gmail.com",
    description="Kait - Kubernetes AI Tool",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="MIT",
    py_modules=["kait"],
    packages=find_packages(include=["kait*"], exclude=["tests"]),
    install_requires=[requirements],
    entry_points={
        "console_scripts": [
            "kait = kait.main:cli",
        ],
    },
    python_requires=">=3.8, <3.12",
)
