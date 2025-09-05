from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="phone-number-formatter",
    version="1.2.0",
    author="Dominic M. Quaiser",
    author_email="mail@quaiser.dev",
    description="Bulk parse and format phone numbers across regions and formats",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/dominicquaiser/Phone-Number-Formatter",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Communications :: Telephony",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Text Processing",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "apify": ["apify>=2.0,<3.0"],
        "dev": ["pytest>=6.0", "black", "flake8", "mypy"],
        "cli": ["click>=8.0"],
    },
    entry_points={
        "console_scripts": [
            "phone-formatter=phone_number_formatter.cli:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)