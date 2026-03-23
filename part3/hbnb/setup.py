from setuptools import setup, find_packages

setup(
    name="hbnb",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        'flask',
        'flask-restx',
        'flask-sqlalchemy',
        'flask-bcrypt',
        'flask-jwt-extended',
        'python-dotenv',
        'typing-extensions>=3.7.4',
    ],
)
