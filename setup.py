from setuptools import setup, find_packages
import pathlib

HERE = pathlib.Path(__file__).parent
LONG_DESCRIPTION = (HERE / "README.md").read_text(encoding="utf-8")

setup(
    name="gazco-rf-controller",
    version="1.0.0",
    description="Reverse-engineered RF controller for Gazco fireplaces",
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    url="https://github.com/A1Tman/rf-reverse-engineering",
    project_urls={
        "Source": "https://github.com/A1Tman/rf-reverse-engineering",
        "Tracker": "https://github.com/A1Tman/rf-reverse-engineering/issues",
    },

    # Tell setuptools where to find our code
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    include_package_data=True,

    # Runtime dependencies
    install_requires=[
        "rflib>=1.9.5",
        "bitstring>=3.1.9",
    ],

    # Dev-only dependencies (for testing, docs, linting, analysis)
    extras_require={
        "dev": [
            # Testing
            "pytest>=7.2.0,<8.0",
            # Documentation
            "mkdocs>=1.5.0,<2.0",
            "mkdocs-material>=9.0.0",
            # Linting & Type Checking
            "flake8>=5.0.0",
            "mypy>=1.0",
            # Analysis libraries
            "numpy>=1.19.0",
            "matplotlib>=3.3.0",
            "scipy>=1.5.0",
            "pyserial>=3.4",
        ],
    },

    # CLI entry points in snake_case
    entry_points={
        "console_scripts": [
            "gazco_on = gazco_rf.scripts.gazco_on:main",
            "gazco_off = gazco_rf.scripts.gazco_off:main",
            "gazco_up = gazco_rf.scripts.gazco_up:main",
            "gazco_down = gazco_rf.scripts.gazco_down:main",
        ],
    },

    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Topic :: Communications :: Ham Radio",
        "Topic :: Scientific/Engineering",
    ],

    python_requires=">=3.6",
)
