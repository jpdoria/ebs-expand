import os
from setuptools import setup, find_packages

with open('requirements.txt') as file_requirements:
    requirements = file_requirements.read().splitlines()

setup(
    name='ebs_expand',
    version='1.1.0',
    author='John Paul P. Doria',
    author_email='jp@lazyadm.in',
    description=('Expand root volume of EBS-backed Linux EC2.'),
    license='MIT',
    keywords='aws ec2 ebs expand',
    url='https://github.com/jpdoria/ebs-expand',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'ebs_expand = ebs_expand.ebs_expand:main'
        ]
    },
    install_requires=requirements,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.6',
        'Topic :: System :: Systems Administration',
        'Topic :: Utilities'
    ],
)
