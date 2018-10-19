#!coding:utf8
import sys

try:
    from setuptools import setup
except:
    from distutils.core import setup
VERSION = "1.0.1"


if __name__ == "__main__":
    with open('requirements.txt') as f:
        required = f.read().splitlines()
    setup(
        name="gonepass",
        version=VERSION,
        packages=['gonepass'],
        url='https://github.com/guokecjl/gonepass_tornado',
        license='',
        author='Geetest',
        author_email='admin@geetest.com',
        description='Gop Python SDK',
        install_requires=required,
    )