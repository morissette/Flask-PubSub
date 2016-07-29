"""
Flask-PubSub
-------------

This extension handles basic publish and subscriber
methods for popular resources
"""
from setuptools import setup


setup(
    name='Flask-PubSub',
    version='0.1',
    url='http://github.com/morissette/Flask-PubSub',
    license='MIT',
    author='Matthew Harris',
    author_email='admin@mattharris.org',
    description='Adds Flask PubSub Features',
    long_description=__doc__,
    packages=['flask_pubsub'],
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    install_requires=[
        'Flask',
	'boto3',
        'requests',
        'M2Crypto'
    ],
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Packages'
    ]
)
