# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

with open('requirements.txt') as f:
	install_requires = f.read().strip().split('\n')

# get version from __version__ variable in iot_chan/__init__.py
from iot_chan import __version__ as version

setup(
	name='iot_chan',
	version=version,
	description='IOT Chan',
	author='dirk',
	author_email='dirk@kooiot.com',
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
