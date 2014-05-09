#!/usr/bin/env python3
# coding: utf-8

from distutils.core import setup

setup(
    name = 'lantern',
    author = "Ilya Murav'jov",
    author_email = 'muravev@yandex.ru',
    py_modules = ["lantern"],
    install_requires = ["tornado"]
)