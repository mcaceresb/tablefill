#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages

with open('README.md') as readme_file:
    readme = readme_file.read()

with open('changelog.md') as history_file:
    history = history_file.read()

requirements = [
    'numpy',
]

setup_requirements = [
    'setuptools >= 38.6.0',
    'twine >= 1.11.0'
]

test_requirements = []

setup(
    author       = "Mauricio Cáceres Bravo",
    author_email = 'caceres@nber.org',
    classifiers  = [
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    description  = "Automatically update LaTeX, Markdown, and LyX tables.",
    entry_points = {
        'console_scripts': ['tablefill = tablefill.tablefill:main']
    },
    install_requires              = requirements,
    license                       = "MIT license",
    long_description              = readme + '\n\n' + history,
    long_description_content_type = 'text/markdown',
    keywords                      = 'tablefill',
    name                          = 'tablefill',
    packages                      = find_packages(include = ['tablefill']),
    setup_requires                = setup_requirements,
    test_suite                    = 'tests',
    tests_require                 = test_requirements,
    url                           = 'https://github.com/mcaceresb/tablefill',
    version                       = '0.9.3',
    zip_safe                      = False,
)
