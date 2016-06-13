#!/bin/bash

## HvW - 2016-06-12
## Install CKAN development-environment
## Specifically for Debian stretch/testing

source ./ckan_tools_lib.sh
# This lib needs $LOGFILE defined"

LOGFILE="./ckan_install_log.txt"
SOURCE_PARENT="/home/hvwaldow/eawag/ckan"
GIT_SOURCE_CKAN="git@github.com:eawag-rdm/eawag-ckan.git"
SOLR_DOWNLOAD_URL="http://mirror.switch.ch/mirror/apache/dist/lucene/solr/6.0.1/solr-6.0.1.tgz"
CKAN_LOCAL_CONFIG="/etc/ckan/default/development.ini"


# This needs to be adapted to each specific case.
# Usually you would get this file from the backup.
get_development_ini() {
    log_out  "copying development.ini"
    scp vonwalha@inf-vonwalha-pc:/etc/ckan/default/development.ini $CKAN_LOCAL_CONFIG
    log_out  "finished copying development.ini "
}


#install_system_packages 2>>$LOGFILE
#fs_setup $SOURCE_PARENT 2>>$LOGFILE
#mk_virtenv 2>>$LOGFILE
#install_src $GIT_SOURCE_CKAN 2>>$LOGFILE
#frontend-tools 2>>$LOGFILE
#get_development_ini 2>>$LOGFILE
#install_solr $SOLR_DOWNLOAD_URL 2>>$LOGFILE
# ckan_read_solr_config $CKAN_LOCAL_CONFIG 2>>$LOGFILE
# config_solr $SOLR_CORE 2>>$LOGFILE
# ckan_read_db_config $CKAN_LOCAL_CONFIG 2>>$LOGFILE
# db_destroy_local 2>>$LOGFILE
# db_setup_local 2>>$LOGFILE
#ckan_config_comment_plugins "comment" $CKAN_LOCAL_CONFIG 2>>$LOGFILE
db_init_local $CKAN_LOCAL_CONFIG 2>>$LOGFILE
    
