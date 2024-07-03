#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

from setuptools import setup, find_packages

setup(
    name="썸트렌드이슈분석",
    version="0.1",
    python_requires='>=3.10.1',
    description="",
    author="Anonymous",
    author_email="yjs7658@gmail.com",
    license="Apache v2.0",
    url="",
    zip_safe=False,
    packages=find_packages(),
    install_requires=[
        "setuptools",
        "virtualenv",
        "pandas",
        "openpyxl", 
        "adjustText", 
        "beautifulsoup4", 
        "selenium", 
        "langchain", 
        'langchain-openai', 
        'lxml'
        ]
)
