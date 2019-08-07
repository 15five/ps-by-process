#!/usr/bin/env python

from setuptools import setup, find_packages
import os


BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def long_description():
    """Get the long description from the README"""
    return open(os.path.join(BASE_DIR, 'README.md')).read()


setup(
    name='ps-by-process',
    version='0.0.1',
    description='Send ps metrics (mem, cpu) per process to influxdb',
    url='https://github.com/15five/ps-by-process',
    maintainer='Paul Logston',
    maintainer_email='paul@15five.com',
    author='Paul Logston',
    author_email='paul@15five.com',
    keywords='ps metrics influxdb',
    license='MIT',
    long_description=long_description(),
    packages=find_packages('src'),
    package_dir={'': 'src'},
    install_requires=[
        'influxdb>=5.2.2',
    ],
    entry_points={
        'console_scripts': [
            'psproc=ps_by_proc.main:main',
        ],
    },
    setup_requires=['pytest-runner'],
    tests_require=['pytest'],
    zip_safe=False,
    include_package_data=True,
    classifiers=[
        'Development Status :: 1 - Planning',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Topic :: Internet',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
