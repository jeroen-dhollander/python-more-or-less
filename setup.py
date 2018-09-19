#!python
from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='more-or-less',
    version="0.1.0",
    description="Library for adding 'more' like paging functionality to your Python application",
    long_description=long_description,
    author="Jeroen Dhollander",
    url='https://github.com/jeroen-dhollander/python-more-or-less',
    packages=find_packages(),
    include_package_data=True,
)