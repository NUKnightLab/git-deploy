#!/usr/bin/env sh
# Script to build a virtualenvironment that can be used by git-deploy wrapper
# for Python3 project support with git-deploy. This script creates a Python 2
# in WORKON_HOME and installs Ansible into that environment. The wrapper can then
# use this environment to execute Ansible, which requires Python 2

WARNING='\033[93m'
FAIL='\033[91m'
ENDC='\033[0m'

PYTHON="$(python -V 2>&1)"
if [[ "$PYTHON" =~ "Python 2" ]]
then
    echo "Using python version $PYTHON"
else
    echo "${FAIL}\nPython 2 is required but current version is $PYTHON${ENDC}\n"
    exit
fi

if [ ! -z "$WORKON_HOME" ]
then
    echo "\nThis will create a new virtual environment in $WORKON_HOME. The default name for this virtualenv is 'git-deploy'. If you use a different name for the git-deploy virtualenv, you will need to set the GIT_DEPLOY_VIRTUALENV environment variable in order to use the git-deploy wrapper.\n"
    read -p "$(echo ${WARNING}Use the default virtualenv name \'git-deploy\'?${ENDC} [Y/n] ) " r
    if [[ $r =~ ^([nN][oO]|[nN])$ ]]
    then
        read -p "Enter the name of the virtual environment to be used by git-deploy wrapper: " VE_NAME
    else
        VE_NAME='git-deploy'
    fi
    echo "\nCreating virtual environment: $WORKON_HOME/$VE_NAME\n"
    virtualenv $WORKON_HOME/$VE_NAME

    echo "\nInstalling Ansible into new virtual environment\n"
    . $WORKON_HOME/$VE_NAME/bin/activate
    pip install --upgrade pip
    pip install ansible
else
    echo "${FAIL}\nWORKON_HOME not set. Set the WORKON_HOME environment variable to the location or your virtual environments and run this script again\n${ENDC}"
    echo "${WARNING}\nYou will also need to have set either WORKON_HOME (with default virtualenvirnment named git-deploy in that location) or GIT_DEPLOY_VIRTUALENV in order to use the git-deploy wrapper\n${ENDC}"
fi
