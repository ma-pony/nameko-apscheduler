from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="nameko-apscheduler",
    version="0.0.8",
    author="Pony Ma",
    author_email="mtf201013@gmail.com",
    description="nameko apscheduler dependency.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ma-pony/nameko-apscheduler",
    packages=find_packages(exclude=['test', 'test.*']),
    install_requires=[
        "marshmallow>=2.20.0",
        "nameko>=3.0.0-rc8",
        "kombu>=4.6.8",
        "APScheduler>=3.6.3",
    ],
    zip_safe=True,
    license='Apache License, Version 2.0',
    classifiers=[
        "Programming Language :: Python :: 3",
    ]
)
