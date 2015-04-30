from setuptools import setup, find_packages

from redsample import __version__, __projectname__

setup(
    name = __projectname__,
    version = __version__,
    packages = find_packages(),
    install_requires = [],
    author = 'Tyghe Vallard',
    author_email = 'vallardt@gmail.com',
    description = 'Use redmine to manage sample data',
    license = 'GPL v2',
    keywords = 'inventory, sample, management, redmine',
    url = 'https://github.com/VDBWRAIR/redsample',
    entry_points = {
        'console_scripts': [
            'load_sample_sheet = resample.outline:main',
            'poll_and_rsync = redsample.autosync:main'
        ]
    }
)
