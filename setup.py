#!python
from setuptools import setup, find_packages

setup(
    name='paginator',
    version="0.1.0",
    description="Library for adding bash 'more' like functionality to your Python application",
    author="Jeroen Dhollander",
    url='https://github.com/jeroen-dhollander/python-paginator',
    packages=find_packages(),
    include_package_data=True,
)
