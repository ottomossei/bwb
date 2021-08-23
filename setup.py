  
from setuptools import setup, find_packages

with open('requirements.txt') as requirements_file:
    install_requirements = requirements_file.read().splitlines()

setup(
    name="bwb",
    version="1.0.8",
    description="The fundamental package for backtesting of stock trading with Python.",
    author="ottomossei",
    author_email="seki.jobhunting@gmail.com",
    install_requires=install_requirements,
    url='https://github.com/ottomossei/bwb/',
    license=license,
    packages=find_packages(exclude=['examples'])
)