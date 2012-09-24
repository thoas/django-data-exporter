# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

version = __import__('data_exporter').__version__

setup(
    name='django-data-exporter',
    version=version,
    description='Export asynchronously your data from your Django models',
    author='Florent Messa',
    author_email='florent.messa@gmail.com',
    url='http://github.com/thoas/django-data-exporter',
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Utilities',
    ]
)
