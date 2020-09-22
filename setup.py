from setuptools import setup
import os

VERSION = '1.0.6'


def get_long_description():
    with open(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), 'README.md'),
        encoding='utf8',
    ) as fp:
        return fp.read()


setup(
    name='git-deploy',
    description='Ansible-based git-subcommand deployment',
    long_description=get_long_description(),
    long_description_content_type='text/markdown',
    author='Northwestern University Knight Lab',
    url='https://github.com/NUKnightLab/git-deploy',
    project_urls={
        'Issues': 'https://github.com/NUKnightLab/git-deploy/issues',
        'Changelog': 'https://github.com/NUKnightLab/git-deploy/blob/master/Changelog.md'
    },
    license='MIT',
    version=VERSION,
    packages=['git_deploy'],
    entry_points="""
        [console_scripts]
        git-deploy=git_deploy.cli:cli
    """,
    install_requires=['click', 'ansible'],
    extras_require={
        'test': ['pytest']
    },
    tests_require=['git-deploy[test]'],
)
