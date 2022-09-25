from setuptools import setup
setup(
    name='countryflag',
    version='0.1',
    description='Converts long country names into emoji flags',
    url='https://github.com/Lendersmark/countryflag',
    author='Lendersmark',
    license="MIT",
    install_requires=[
        'emoji-country-flag',
        'country_converter'
     ],
     entry_points={
        'console_scripts': [
            'countryflag=countryflag.countryflag:run'
        ]
    }
)
