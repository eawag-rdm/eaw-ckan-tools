#!/bin/bash

## HvW - 2016-06-12
## Install CKAN development-environment
## Specifically for Debian stretch/testing

LOGFILE="./ckan_install_log.txt"
SOURCE_PARENT="/home/hvwaldow/eawag/ckan"
GIT_SOURCE="git@github.com:eawag-rdm/eawag-ckan.git"

install_system_packages() {
    sudo apt-get update &&\
    # Python
    sudo apt-get install -y python-dev &&\
    sudo apt-get install -y python-pip &&\
    sudo apt-get install -y python-virtualenv &&\
    # Postgres
    sudo apt-get install -y postgresql &&\
    sudo apt-get install -y libpq-dev  &&\
    # PostGIS
    sudo apt-get install -y postgis  &&\
    sudo apt-get install -y libxml2-dev &&\
    sudo apt-get install -y libxslt1-dev &&\
    sudo apt-get install -y libgeos-c1v5 &&\
    # Git
    sudo apt-get install -y git  &&\
    # Java JRE for SOLR
    sudo apt-get install openjdk-8-jre-headless &&\
    # NPM for frontend-tools
    sudo apt-get install npm
    if [[ $? == 0 ]]; then
	echo "system packages successfully installed"
    else
	echo "there were error installing the system packages"
    fi
}


# This needs to be adapted to each specific case.
# # Usually youl'd get this file from the backup.
# get_development_ini() {
#     scp vonwalha@inf-vonwalha-pc:/etc/ckan/default/development.ini /



# install_system_packages >>$LOGFILE
# ck-install-source $SOURCE_PARENT $GIT_SOURCE >>$LOGFILE



    
