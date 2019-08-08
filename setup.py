from setuptools import setup, find_packages

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setup(
    name='aip-repackaging',
    version='0.0.1',
    url='https://github.com/djpillen/aip-repackaging',
    author='Dallas Pillen',
    packages=find_packages(),
    scripts=['aip_repackager.py'],
    description='Bentley Historical Library scripts to repackage Archivematica AIPs',
    install_requires=requirements
)