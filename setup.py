# -*- coding: utf-8 -*-

from setuptools import setup, find_packages


testpkgs = [
    'websocket-client',
    'redis',
]
install_requires = [
    'aiohttp',
    'websockets',
    'pyDes',
    'asyncio-redis'
]

setup(
    name='pynotif',
    version='0.1',
    description='',
    author='Amin Etesamian',
    author_email='aminetesamian1371@gmail.com',
    url='https://github.com/eteamin/pynotif',
    packages=find_packages(exclude=['ez_setup']),
    install_requires=install_requires,
    tests_require=testpkgs,
    include_package_data=True,
)