Contributing Guide
==================
This guide explains how to contribute to the CountryFlag project.

Setting Up Development Environment
----------------------------------
1. Fork and Clone
~~~~~~~~~~~~~~~~~
First, fork the repository on GitHub, then clone your fork:

.. code-block:: bash

   git clone https://github.com/yourusername/countryflag.git
   cd countryflag

2. Create Virtual Environment
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Create and activate a virtual environment:

.. code-block:: bash

   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate

3. Install Dependencies
~~~~~~~~~~~~~~~~~~~~~~~
Install development dependencies:

.. code-block:: bash

   pip install -e ".[dev]"

4. Install Pre-commit Hooks
~~~~~~~~~~~~~~~~~~~~~~~~~~~
Set up pre-commit hooks:

.. code-block:: bash

   pre-commit install

Making Changes
--------------
1. Create a Branch
~~~~~~~~~~~~~~~~~~
Create a branch for your changes:

.. code-block:: bash

   git checkout -b feature/your-feature-name

2. Code Style
~~~~~~~~~~~~~
- Follow PEP 8 guidelines
- Use type hints
- Write docstrings in Google style
- Keep lines under 88 characters
- Run black for code formatting

3. Testing
~~~~~~~~~~
Run tests before submitting changes:

.. code-block:: bash

   # Run all tests
   pytest

   # Run specific test categories
   pytest tests/unit/
   pytest tests/property/
   pytest tests/performance/

4. Documentation
~~~~~~~~~~~~~~~~
Update documentation for any changes:

.. code-block:: bash

   # Build documentation
   sphinx-build -b html docs/source docs/build/html

Submitting Changes
------------------
1. Commit Changes
~~~~~~~~~~~~~~~~~
Follow commit message guidelines:

.. code-block:: bash

   git add .
   git commit -m "feat: add new feature"

2. Push Changes
~~~~~~~~~~~~~~~
Push to your fork:

.. code-block:: bash

   git push origin feature/your-feature-name

3. Create Pull Request
~~~~~~~~~~~~~~~~~~~~~~
Create a pull request on GitHub with:

- Clear description of changes
- Link to any related issues
- Screenshots if applicable
- Test results

Code Review Process
-------------------
1. Automated Checks
~~~~~~~~~~~~~~~~~~~
Your PR will be checked for:

- Test coverage
- Code style
- Type checking
- Documentation

2. Manual Review
~~~~~~~~~~~~~~~~
A maintainer will review your PR for:

- Code quality
- Test coverage
- Documentation
- Overall design

3. Feedback
~~~~~~~~~~~
- Address any feedback promptly
- Keep discussions focused
- Ask questions if unclear

Development Guidelines
----------------------
1. Code Organization
~~~~~~~~~~~~~~~~~~~~
- Keep modules focused
- Follow existing structure
- Use appropriate abstractions

2. Testing
~~~~~~~~~~
- Write unit tests for new code
- Add property tests for complex logic
- Include performance tests when relevant

3. Documentation
~~~~~~~~~~~~~~~~
- Update API documentation
- Add examples for new features
- Keep README.md current

4. Performance
~~~~~~~~~~~~~~
- Consider caching where appropriate
- Profile code changes
- Test with large datasets

5. Security
~~~~~~~~~~~
- Never commit secrets
- Validate all inputs
- Use safe defaults

Getting Help
------------
- Create an issue for bugs
- Ask questions in discussions
- Join our community chat

Release Process
---------------
1. Version Updates
~~~~~~~~~~~~~~~~~~
Update version in:

- pyproject.toml
- setup.py
- __init__.py

2. Documentation
~~~~~~~~~~~~~~~~
- Update docs/CHANGELOG.md
- Review all documentation
- Update version references

3. Testing
~~~~~~~~~~
Run full test suite:

.. code-block:: bash

   tox

4. Create Release
~~~~~~~~~~~~~~~~~
- Create and push tag
- Create GitHub release
- Upload to PyPI

5. Announcements
~~~~~~~~~~~~~~~~
- Update documentation site
- Announce in discussions
- Update any related projects
