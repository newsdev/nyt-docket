import os.path

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


def read(filename):
    return open(os.path.join(os.path.dirname(__file__), filename)).read()


setup(
    name='nyt-docket',
    version='0.0.14',
    author='Jeremy Bowers',
    author_email='jeremy.bowers@nytimes.com',
    url='https://github.com/newsdev/nyt-docket',
    description='Python client for parsing SCOTUS cases from the granted/noted and orders dockets.',
    long_description=read('README.rst'),
    packages=['docket'],
    entry_points={
        'console_scripts': (
            'docket = docket:main',
        ),
    },
    license="Apache License 2.0",
    keywords='SCOTUS data parsing scraping legal law court',
    install_requires=['cement','pymongo','clint','requests','csvkit'],
    classifiers=['Development Status :: 3 - Alpha',
                 'Intended Audience :: Developers',
                 'Programming Language :: Python',
                 'Topic :: Software Development :: Libraries :: Python Modules']
)
