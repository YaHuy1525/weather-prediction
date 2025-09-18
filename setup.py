from setuptools import setup,find_packages

with open("requirements.txt") as f:
    requirements = f.read().splitlines()

setup(
    name="Weather-Prediction-Project",
    version="0.1",
    author="yahuy1525",
    packages=find_packages(),
    install_requires = requirements,
)