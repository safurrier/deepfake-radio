from setuptools import setup, find_packages
import os

setup(
    name="deepfake_radio",
    version="0.1.0",
    author="Alex Furrier",
    description="T2S4FWF -> (Text to Speech for Fun With Friends)",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    packages=find_packages(),
)