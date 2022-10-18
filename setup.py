import setuptools

# reads the contents of README file
from pathlib import Path

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setuptools.setup(
    name="countryflag",
    version="0.1.2b1",
    author="Lendersmark",
    description="A Python package for converting country names into emoji flags",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Lendersmark/countryflag",
    packages=setuptools.find_packages("src", exclude=["tests"]),  # test is excluded
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    py_modules=["countryflag"],
    package_dir={"": "src"},
    install_requires=["emoji-country-flag", "country_converter"],
    entry_points={"console_scripts": ["countryflag=countryflag:main"]},
)
