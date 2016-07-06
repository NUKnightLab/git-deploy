#!/usr/bin/env sh
# For a specific version branch, set the environment variable GIT_DEPLOY_VERSION

WARNING='\033[93m'
FAIL='\033[91m'
ENDC='\033[0m'

ORIG_DIR=`pwd -P`
DEPLOY_DIR=$ORIG_DIR/${GIT_DEPLOY_PROJECT_CONFIG_DIR:-deploy}
GIT_DEPLOY_VERSION=$(awk -F":" '/gitdeploy_version/ {gsub(/"/,"", $2); print $2 }' $DEPLOY_DIR/config.common.yml)

# because MacOS does not support readlink -f
TARGET_FILE=$0
cd `dirname $TARGET_FILE`
TARGET_FILE=`basename $TARGET_FILE`
while [ -L "$TARGET_FILE" ]
do
  TARGET_FILE=`readlink $TARGET_FILE`
    cd `dirname $TARGET_FILE`
      TARGET_FILE=`basename $TARGET_FILE`
    done
    TARGET_DIR=`pwd -P`
    if [ ! -z "$GIT_DEPLOY_VERSION" ]
    then
        GIT_DEPLOY_ORIG_VERSION=`git rev-parse --symbolic-full-name --abbrev-ref HEAD`
        echo "Switching to git-deploy version $GIT_DEPLOY_VERSION"
        git checkout $GIT_DEPLOY_VERSION
        if [[ $? != 0 ]]; then
            echo "${FAIL}Error. Could not checkout correct git-deploy version${ENDC}"
            exit 1
        fi
    fi
DEPLOY_SCRIPT=$TARGET_DIR/git-deploy.py
cd $ORIG_DIR

echo "Switching from current virtualenv $VIRTUAL_ENV"
ENV=$VIRTUAL_ENV
. $GIT_DEPLOY_VIRTUALENV/bin/activate
echo "Switched to virtualenv $VIRTUAL_ENV"

$DEPLOY_SCRIPT $@ --project-virtualenv=$ENV

. $ENV/bin/activate
echo "Switched back to virtualenv $VIRTUAL_ENV"

if [ ! -z "$GIT_DEPLOY_VERSION" ]
then
  cd $TARGET_DIR
  echo "Returning to default git-deploy version: $GIT_DEPLOY_ORIG_VERSION"
  git checkout $GIT_DEPLOY_ORIG_VERSION
  cd $ORIG_DIR
fi
