# setup.py
from setuptools import setup, find_packages

setup(
    name="az_toolkit",
    version="0.1",
    packages=find_packages(),  # 自动找 toolkit/ 下所有模块
    install_requires=[],  # 可选：填 requirements
)

