from setuptools import setup, find_packages

setup(
    name='misinf_spread',
    packages=find_packages(),
    scripts=[],
    long_description=open('README.md').read(),
    url="https://github.com/tambu85/misinfo_spread",
    install_requires=[
        "numpy",
        "scipy",
        "matplotlib",
        "pandas >= 1.3.2",
        "tables"
    ],
)
