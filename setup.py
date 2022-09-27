import setuptools

setuptools.setup(
    name='countryflag',
    version='0.1',
    author='Lendersmark',
    description='A Python package for converting country names into emoji flags',
    url='https://github.com/Lendersmark/countryflag',
    packages=setuptools.find_packages(),
    license="MIT",
    classifiers=[
            "Programming Language :: Python :: 3",
            "License :: OSI Approved :: MIT License",
            "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    py_modules=['countryflag'],
    package_dir={'':'countryflag/src'},
    install_requires=[
        'emoji-country-flag',
        'country_converter'
     ],
     entry_points={
        'console_scripts': [
            'countryflag=countryflag:run'
        ]
    }
)
