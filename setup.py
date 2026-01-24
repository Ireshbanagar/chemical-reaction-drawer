"""
Setup script for the Chemical Reaction Drawer application.
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="chemical-reaction-drawer",
    version="0.1.0",
    author="Chemical Reaction Drawer Team",
    author_email="contact@chemreactiondrawer.com",
    description="A desktop application for creating, editing, and visualizing chemical structures and reactions",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/chemreactiondrawer/chemical-reaction-drawer",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Education",
        "Topic :: Scientific/Engineering :: Chemistry",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "pytest>=7.0.0",
        "hypothesis>=6.0.0",
    ],
    extras_require={
        "dev": [
            "pytest-cov>=4.0.0",
            "black>=22.0.0",
            "flake8>=5.0.0",
            "mypy>=1.0.0",
        ],
        "gui": [
            # "PyQt5>=5.15.0",  # Alternative GUI framework
            # "tkinter",  # Built into Python
        ],
        "3d": [
            # "PyOpenGL>=3.1.0",  # For 3D visualization
            # "numpy>=1.20.0",  # For 3D calculations
        ],
        "export": [
            # "Pillow>=9.0.0",  # For image export
            # "reportlab>=3.6.0",  # For PDF export
        ]
    },
    entry_points={
        "console_scripts": [
            "chemical-drawer=chemical_reaction_drawer.main:main",
        ],
    },
)