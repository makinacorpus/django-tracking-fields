import os
from setuptools import setup, find_packages

with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='django-tracking-fields',
    version='1.0.1',
    packages=find_packages(),
    include_package_data=True,
    license='GPLv3+',
    description=(
        'A Django app allowing the tracking of objects field '
        'in the admin site.'
    ),
    long_description=README,
    url='https://github.com/makinacorpus/django-tracking-fields',
    author='Yann Fouillat (alias Gagaro)',
    author_email='yann.fouillat@makina-corpus.com',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
)
