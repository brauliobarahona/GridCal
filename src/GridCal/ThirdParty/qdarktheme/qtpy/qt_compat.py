# MIT License
#
# Copyright (c) 2021-2022 Yunosuke Ohsugi
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
"""Module for Qt compat."""
from __future__ import annotations

import os
import sys


class QtImportError(ImportError):
    """Error raise if no bindings could be selected."""


qt_import_error = QtImportError(
    "Failed to import qt-binding. Check packages(pip list)."
    "\n\tAvailable Qt-binding packages: PySide6, PyQt6, PyQt5, PySide2."
)


# Qt6
_QT_API_PYSIDE6 = "PySide6"
_QT_API_PYQT6 = "PyQt6"
# Qt5
_QT_API_PYQT5 = "PyQt5"
_QT_API_PYSIDE2 = "PySide2"


_API_LIST = [_QT_API_PYSIDE6, _QT_API_PYQT6, _QT_API_PYQT5, _QT_API_PYSIDE2]


def _get_loaded_api() -> str | None:
    """Return which API is loaded.

    If this returns anything besides None,
    importing any other Qt-binding is unsafe.
    """
    for api in _API_LIST:
        if sys.modules.get(f"{api}.QtCore"):
            return api
    return None


def _get_environ_api() -> str | None:
    """Return which API is specified in environ."""
    _qt_api_env = os.environ.get("QT_API")
    if _qt_api_env is not None:
        _qt_api_env = _qt_api_env.lower()

    _env_to_module = {
        "pyside6": _QT_API_PYSIDE6,
        "pyqt6": _QT_API_PYQT6,
        "pyqt5": _QT_API_PYQT5,
        "pyside2": _QT_API_PYSIDE2,
        None: None,
    }
    try:
        return _env_to_module[_qt_api_env]
    except KeyError:
        raise KeyError(
            "The environment variable QT_API has the unrecognized value "
            f"{_qt_api_env!r}. "
            f"Valid values are {[k for k in _env_to_module if k is not None]}"
        ) from None


def _get_installed_api() -> str | None:
    """Return which API is installed."""
    # Fix [AttributeError: module 'importlib' has no attribute 'util']
    # See https://stackoverflow.com/a/39661116/13452582
    from importlib import util

    for api in _API_LIST:
        if util.find_spec(api) is not None:
            return api
    return None


QT_API = _get_loaded_api()
if QT_API is None:
    QT_API = _get_environ_api()
if QT_API is None:
    QT_API = _get_installed_api()
