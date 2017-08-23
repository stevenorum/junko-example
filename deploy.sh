#!/bin/bash

TEMP_DIR='junko-zipdir'

TEMPLATE="sunyata/alpha.json"

if [ -e "$1" ] ; then
    TEMPLATE="$1"
fi

# PIP_CONF="${HOME}/.pip/pip.conf"
# PIP_CONF_TEMP="${HOME}/.pip/pip.conf.backup"

# API_HOST="5g1m9emx29.execute-api.us-east-1.amazonaws.com"

# USERNAME="ThisIsAUsername"
# PASSWORD="ThisIsAPassword"

bundle() {
    mkdir $TEMP_DIR
    echo -e '[install]\nprefix=' > ~/.pydistutils.cfg
    # mkdir -p ~/.pip
    # if [ -e "$PIP_CONF" ] ; then
    #     mv $PIP_CONF $PIP_CONF_TEMP
    # fi
    # echo "[global]" >> $PIP_CONF
    # echo "; Extra index to private pypi dependencies" >> $PIP_CONF
    # echo "extra-index-url = https://${USERNAME}:${PASSWORD}@${API_HOST}/prod/repo/" >> $PIP_CONF
    # echo "trusted-host = $API_HOST" >> $PIP_CONF

    pip3 install jinja2 -t $TEMP_DIR/
    pip3 install setuptools -t $TEMP_DIR/
    pip3 install junko -t $TEMP_DIR/ || exit 1
    rm ~/.pydistutils.cfg
    # rm $PIP_CONF
    # if [ -e "$PIP_CONF_TEMP" ] ; then
    #     mv $PIP_CONF_TEMP $PIP_CONF
    # fi
    cp -R junko-example/* $TEMP_DIR/
#    cp -R ../junko/junko $TEMP_DIR/
}

cleanup() {
    rm -rf $TEMP_DIR
}

cleanup
bundle
BASE_CMD="sunyata -v --template $TEMPLATE"
$BASE_CMD --create || $BASE_CMD --deploy
cleanup
