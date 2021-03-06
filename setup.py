from setuptools import setup

setup(
    name="nameko-apscheduler",
    version="1.0.0",
    description="",
    url="https://github.com/ma-pony/nameko-apscheduler",
    install_requires=[
        "marshmallow==3.6.0",
        "nameko==3.0.0-rc8",
        "kombu==4.6.8",
        "APScheduler==3.6.3",
    ],
    zip_safe=True,
)
