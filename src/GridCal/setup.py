# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
# SPDX-License-Identifier: MPL-2.0
"""
A setuptools based setup module.
See:
https://packaging.python.org/guides/distributing-packages-using-setuptools/
https://github.com/pypa/sampleproject
"""

# Always prefer setuptools over distutils
from setuptools import setup, find_packages
import os

from GridCal.__version__ import __GridCal_VERSION__


here = os.path.abspath(os.path.dirname(__file__))

long_description = '''# GridCal

This software aims to be a complete platform for power systems research and simulation.

[Watch the video https](https://youtu.be/SY66WgLGo54)

[Check out the documentation](https://gridcal.readthedocs.io)


## Installation

pip install GridCal

For more options (including a standalone setup one), follow the
[installation instructions]( https://gridcal.readthedocs.io/en/latest/getting_started/install.html)
from the project's [documentation](https://gridcal.readthedocs.io)
'''

description = 'GridCal is a Power Systems simulation program intended for professional use and research'

base_path = os.path.join('GridCal')

pkgs_to_exclude = ['docs', 'research', 'tests', 'tutorials', 'GridCalEngine']

packages = find_packages(exclude=pkgs_to_exclude)

# ... so we have to do the filtering ourselves
packages2 = list()
for package in packages:
    elms = package.split('.')
    excluded = False
    for exclude in pkgs_to_exclude:
        if exclude in elms:
            excluded = True

    if not excluded:
        packages2.append(package)


package_data = {'GridCal': ['*.md',
                            '*.rst',
                            'LICENSE.txt',
                            'setup.py',
                            'data/cables.csv',
                            'data/transformers.csv',
                            'data/wires.csv',
                            'data/sequence_lines.csv'],
                }

dependencies = ['setuptools>=41.0.1',
                'wheel>=0.37.2',
                "PySide6<=6.6.3.1",  # 5.14 breaks the UI generation for development, 6.7.0 breaks all
                "qtconsole>=4.5.4",
                "pytest>=7.2",
                "darkdetect",
                "pyqtdarktheme",
                "websockets",
                "opencv-python>=4.10.0.84",
                "packaging",
                "GridCalEngine==" + __GridCal_VERSION__,  # the GridCalEngine version must be exactly the same
                ]

extras_require = {
        'gch5 files':  ["tables"]  # this is for h5 compatibility
    }
# Arguments marked as "Required" below must be included for upload to PyPI.
# Fields marked as "Optional" may be commented out.

setup(
    name='GridCal',  # Required
    version=__GridCal_VERSION__,  # Required
    license='MPL2',
    description=description,  # Optional
    long_description=long_description,  # Optional
    long_description_content_type='text/markdown',  # Optional (see note above)
    url='https://github.com/SanPen/GridCal',  # Optional
    author='Santiago Peñate Vera et. Al.',  # Optional
    author_email='santiago@gridcal.org',  # Optional
    classifiers=[
        'License :: OSI Approved :: Mozilla Public License 2.0 (MPL 2.0)',
        'Programming Language :: Python :: 3.8',
    ],
    keywords='power systems planning',  # Optional
    packages=packages2,  # Required
    include_package_data=True,
    python_requires='>=3.8',
    install_requires=dependencies,
    extras_require=extras_require,
    package_data=package_data,
    entry_points={
        'console_scripts': [
            'gridcal = GridCal.ExecuteGridCal:runGridCal',
            'GridCal = GridCal.ExecuteGridCal:runGridCal',
        ],
    },
)
