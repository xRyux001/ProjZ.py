from setuptools import setup, find_packages

with open("README.md", "r") as stream:
    long_description = stream.read()

setup(
    name = 'ProjZ.py',
    version = '0.0.2',
    url = 'https://github.com/Slimakoi/ProjZ.py',
    download_url = 'https://github.com/Slimakoi/ProjZ.py/tarball/master',
    license = 'MIT',
    author = 'Slimakoi',
    author_email = 'slimeytoficial@gmail.com',
    description = 'A library to create ProjectZ bots.',
    long_description = long_description,
    long_description_content_type = 'text/markdown',
    keywords = [
        'aminoapps',
        'projectz',
        'projectz-bot',
        'projectz-py',
        'projz',
        'projz-bot',
        'projz-py',
        'amino',
        'amino-bot',
        'narvii',
        'api',
        'python',
        'python3',
        'python3.x',
        'slimakoi'
        'unofficial'
    ],
    install_requires = [
        'setuptools',
        'requests',
        'six',
        'websocket-client'
    ],
    setup_requires = [
        'wheel'
    ],
    packages = find_packages()
)
