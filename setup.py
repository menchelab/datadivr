from setuptools import find_packages, setup

setup(
    name="datadivr",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "websockets",
        "asyncio",
    ],
    entry_points={
        "console_scripts": [
            "datadivr-server=datadivr.server:main",
            "datadivr-client=datadivr.client:main",
        ],
    },
)
