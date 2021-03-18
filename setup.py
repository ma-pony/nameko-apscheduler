from setuptools import setup

setup(
    name="nameko-apscheduler",
    version="0.0.1",
    author="Pony Ma",
    author_email="mtf201013@gmail.com",
    description="nameko apscheduler dependency.",
    url="https://github.com/ma-pony/nameko-apscheduler",
    install_requires=[
        "marshmallow>=3.6.0",
        "nameko>=3.0.0-rc8",
        "kombu>=4.6.8",
        "APScheduler>=3.6.3",
    ],
    zip_safe=True,
)
