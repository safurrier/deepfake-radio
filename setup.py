from setuptools import setup, find_packages
import os

def _get_dependencies():
    with open(os.path.join(os.path.dirname(__file__), 'requirements.txt')) as f:
        return f.read().splitlines()

setup(
    name="deepfake_radio",
    version="0.1.0",
    author="Alex Furrier",
    description="T2S4FWF -> (Text to Speech for Fun With Friends)",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    packages=find_packages(),
    # install_requires=_get_dependencies(),
)