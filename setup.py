# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
from os import path
from sys import platform
import termslides


with open(path.join('.', 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

with open('requirements.txt', encoding='utf-8') as f:
    install_requires = [line.strip() for line in f.read().split('\n')
                        if not line.strip().startswith('#')]


setup(
    name='termslides',
    version=termslides.__version__,
    description='Script your slides in YAML file and show it in terminal.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    packages=find_packages(),
    install_requires=install_requires,

    author='onelife',
    author_email='onelife.real@gmail.com',
    license=termslides.__license__,
    url='https://github.com/onelife/termslides',
    download_url='https://github.com/onelife/termslides/archive/%s.tar.gz' % termslides.__version__,

    keywords=['terminal', 'slides', 'asscii', 'art'],
    classifiers=[
        'Environment :: Console',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3',
        'Topic :: Text Processing :: Markup',
    ],

    package_data={
        'termslides': [
            'lib/*.jar',
        ],
    },

    entry_points={
        'console_scripts': [
            'termslides = termslides:termslides',
        ],
    }
)
