import os.path

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


def read(filename):
    return open(os.path.join(os.path.dirname(__file__), filename)).read()


setup(
    name='nyt-docket',
    version='0.0.2',
    author='Jeremy Bowers',
    author_email='jeremy.bowers@nytimes.com',
    url='https://github.com/newsdev/nyt-docket',
    description='Python client for parsing SCOTUS cases from the granted/noted and orders dockets.',
    long_description=read('README.rst'),
    packages=['docket'],
    license="Apache License 2.0",
    keywords='SCOTUS data parsing scraping legal law court',
    install_requires=['beautifulsoup4==4.4.1','docopt==0.6.2','lxml==3.4.4','numpy==1.9.3','pdfminer==20140328','requests==2.7.0','wheel==0.24.0'],
    classifiers=['Development Status :: 3 - Alpha',
                 'Intended Audience :: Developers',
                 'Programming Language :: Python',
                 'Topic :: Software Development :: Libraries :: Python Modules']
)