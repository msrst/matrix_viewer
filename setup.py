#!/usr/bin/env python

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = ['numpy >= 1.0', ]

test_requirements = ['pytest>=3', ]

setup(
    author="Matthias Rosenthal",
    python_requires='>=3.6',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    description="A tabular viewer for numpy arrays, python structs and more similar to the MATLAB data viewer",
    entry_points={
        'console_scripts': [
            'matrix_viewer=matrix_viewer.cli:main',
        ],
    },
    install_requires=requirements,
    license="MIT license",
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords='matrix_viewer',
    name='matrix_viewer',
    packages=find_packages(include=['matrix_viewer', 'matrix_viewer.*']),
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/msrst/matrix_viewer',
    version='0.2.0',
    zip_safe=False,
)
