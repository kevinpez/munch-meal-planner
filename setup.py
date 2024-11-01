from setuptools import setup, find_packages

setup(
    name='munch',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        'openai>=1.0.0',
        'flask',
        'python-dotenv',
        'gunicorn',
        'flask-sqlalchemy',
        'flask-migrate',
        'flask-login',
        'setuptools>=65.0'
    ],
    python_requires='>=3.8',
    entry_points={
        'console_scripts': [
            'munch=munch.main:main',
        ],
    },
)
