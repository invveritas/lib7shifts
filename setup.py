from setuptools import setup, find_packages
# pylint: disable=no-name-in-module,F0401,W0232,C0111,R0201

def readme():
    "Returns the contents of the README.rst file"
    with open("README.rst") as f:
        return f.read()

setup(
    name='lib7shifts',
    version="0.1",
    description='Python 7shifts API client',
    long_description=readme(),
    author='Prairie Dog Brewing CANADA Inc',
    author_email='gerad@prairiedogbrewing.ca',
    url='http://github.com/prairiedogbeer/7shifts-tools',
    packages=find_packages(),
    install_requires=[
        'setuptools',
        'docopt',
        'PyYAML',
        'apiclient',
    ],
    #scripts=[
    #    'bin/foo
    #],
    test_suite="nose.collector",
)
