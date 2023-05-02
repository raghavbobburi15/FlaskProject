from setuptools import setup, find_packages

setup(
    install_requires=[
        'pandas',
        'dash',
        'sqlalchemy',
        'datetime',
    ],
    entry_points={
        'console_scripts': [
            'app=app.run:main',
        ],
    },
)