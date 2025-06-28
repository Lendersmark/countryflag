# Setup.py maintained for compatibility
# All metadata is defined in pyproject.toml as the source of truth
from pathlib import Path

# Import metadata from pyproject.toml
try:
    import tomllib
except ImportError:
    try:
        import tomli as tomllib
    except ImportError:
        # Fallback for older Python versions without tomli
        import configparser
        tomllib = None

def load_pyproject_metadata():
    """Load project metadata from pyproject.toml"""
    pyproject_path = Path(__file__).parent / "pyproject.toml"
    
    if tomllib is None:
        # Basic fallback - return hardcoded values as a last resort
        return {
            "name": "countryflag",
            "version": "1.1.0",
            "description": "A Python package for converting country names into emoji flags",
            "author": "Lendersmark",
            "author_email": "author@example.com",
            "url": "https://github.com/lendersmark/countryflag",
            "license": "MIT",
            "classifiers": [
                "Development Status :: 5 - Production/Stable",
                "Programming Language :: Python :: 3",
                "Programming Language :: Python :: 3.9",
                "Programming Language :: Python :: 3.10",
                "Programming Language :: Python :: 3.11",
                "Programming Language :: Python :: 3.12",
                "License :: OSI Approved :: MIT License",
                "Operating System :: OS Independent",
                "Topic :: Software Development :: Libraries :: Python Modules",
                "Topic :: Text Processing",
                "Intended Audience :: Developers",
            ],
            "python_requires": ">=3.9",
        }
    
    with open(pyproject_path, "rb") as f:
        pyproject_data = tomllib.load(f)
    
    project = pyproject_data["project"]
    
    # Extract author info
    authors = project.get("authors", [])
    author_name = authors[0]["name"] if authors else ""
    author_email = authors[0]["email"] if authors else ""
    
    # Extract URLs
    urls = project.get("urls", {})
    homepage = urls.get("Homepage", "")
    
    return {
        "name": project["name"],
        "version": project["version"],
        "description": project["description"],
        "author": author_name,
        "author_email": author_email,
        "url": homepage,
        "license": "MIT",  # From pyproject.toml license file reference
        "classifiers": project.get("classifiers", []),
        "python_requires": project.get("requires-python", ""),
    }

# Only run setup if this file is executed directly
if __name__ == "__main__":
    # Try to import setuptools, with fallback for modern Python
    try:
        import setuptools
    except ImportError:
        print("Warning: setuptools not available. Please install it or use 'pip install -e .' instead.")
        exit(1)
    
    # Load metadata from pyproject.toml
    metadata = load_pyproject_metadata()
    
    # Read long description from README
    this_directory = Path(__file__).parent
    try:
        long_description = (this_directory / "README.md").read_text(encoding="utf8")
    except FileNotFoundError:
        long_description = ""
    
    setuptools.setup(
        name=metadata["name"],
        version=metadata["version"],
        author=metadata["author"],
        author_email=metadata["author_email"],
        description=metadata["description"],
        long_description=long_description,
        long_description_content_type="text/markdown",
        url=metadata["url"],
        packages=setuptools.find_packages(
            where="src", exclude=["tests"]
        ),
        license=metadata["license"],
        classifiers=metadata["classifiers"],
        python_requires=metadata["python_requires"],
        package_dir={"": "src"},
        # Dependencies are now managed in pyproject.toml [project.dependencies]
        # install_requires removed to prevent conflicts with pyproject.toml
        # Entry points are defined in pyproject.toml [project.scripts]
        # but kept here for backwards compatibility
        entry_points={"console_scripts": ["countryflag=countryflag.cli.main:main"]},
    )
