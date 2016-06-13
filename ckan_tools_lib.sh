#!/bin/bash

# This lib needst $LOGFILE defined"

# PLUGINS="ckanext-eaw_theme ckanext_eaw_schema ckanext-eaw_vocabularies
# ckanext-scheming ckanext-reapeating ckanapi ckanext-hierarchy ckanext-spatial"

# PLUGINREPO="https://github.com/eawag-rdm"

# UPSTREAM_BRANCH="release-v2.5.2"

# usage() {
#     echo "Usage: ck-install-source onlyext"
#     echo "       ck-install-source <LOCAL-SOURCEDIR> <GIT-URL[@TAG]>"
#     echo "The first form installs only the extensions"
#     echo "Example: ck-install-source ~/ckan https://github.com/ckan/ckan.git"
#     echo "Example: ck-install-source ~/Ckan/ckan git@github.com:eawag-rdm/eawag-ckan.git"
#     echo
#     echo "Edit the source to adapt the plugins that shoall be installed"
# }

log_out() {
    msg=$1
    echo "******************************" |tee -a $LOGFILE
    echo $(date) |tee -a $LOGFILE
    echo "$msg" |tee -a $LOGFILE
    echo "******************************" |tee -a $LOGFILE
}
install_system_packages() {
    log_out "Installing system packages ..."
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
    sudo apt-get install -y openjdk-8-jre-headless &&\
    sudo apt-get install -y unzip &&\ # for solr installation
    # NPM for frontend-tools
    sudo apt-get install -y npm &&\
    # needed by ckan_tools_lib.sh itself
    sudo apt-get install -y curl
    if [[ $? == 0 ]]; then
	log_out "system packages successfully installed" |tee -a $LOGFILE
    else
	log_out "there were error installing the system packages"
    fi
}

# install solr
# takes the download URL for solr as parameter
# e.g. "http://mirror.switch.ch/mirror/apache/dist/lucene/solr/6.0.1/solr-6.0.1.tgz"
install_solr() {
    solr_url=$1
    solr_file=$(basename $solr_url)
    solr_installscript=${solr_file%.tgz}/bin/install_solr_service.sh
    log_out "installing SOLR"
    olddir=$(pwd)
    cd /tmp
    #wget $solr_url &&\
    tar zxvf $solr_file $solr_installscript --strip-components=2 &&\
    # using default installation into /opt:
    sudo bash ./install_solr_service.sh $solr_file &&\
    sudo rm /tmp/$solr_file /tmp/install_solr_service.sh
    running1=$(sudo systemctl is-active solr)
    running2=$(curl -I -o - http://localhost:8983 2>/dev/null |head -n 1)
    if [[ "$running1" == "active" && "$running2" =~ "302" ]]; then
	log_out "SOLR is up and running"
    else
	log_out "SOLR installation failed somewhere."
	exit 1
    fi
    cd $olddir
}

fs_setup() {
    parent=$1
    log_out "starting filesystem-setup"
    mkdir -p ${parent}/lib/default
    mkdir -p ${parent}/etc/default
    if [[ -e /usr/lib/ckan ]]; then
	sudo rm /usr/lib/ckan
    fi
    if [[ -e /etc/ckan ]]; then
	sudo rm /etc/ckan
    fi
    sudo ln -s ${parent}/lib /usr/lib/ckan    
    sudo ln -s ${parent}/etc /etc/ckan
    echo |tee -a $LOGFILE
    echo "Links:" |tee -a $LOGFILE
    ls -lF /etc/ckan |tee -a $LOGFILE
    ls -lF /usr/lib/ckan |tee -a $LOGFILE
    echo |tee -a $LOGFILE
    echo "Dev. Layout:" |tee -a $LOGFILE
    tree $(realpath ${parent}) |tee -a $LOGFILE
    log_out "finished filesystem-setup"
}

mk_virtenv() {
    log_out "installing the virtual environment"
    virtualenv --no-site-packages /usr/lib/ckan/default
    source /usr/lib/ckan/default/bin/activate
    pip install pip-tools
    deactivate
    log_out "virtual environment installed\npip-tools installed"
}

install_src() {
    gitsrc=$1
    log_out "installing source from ${gitsrc}"
    source /usr/lib/ckan/default/bin/activate
    pip install -vv -e "git+${gitsrc}#egg=ckan"
    ln -s /usr/lib/ckan/default/src/ckan/who.ini /etc/ckan/default/who.ini
    pip install -r /usr/lib/ckan/default/src/ckan/requirements.txt ||\
    pip install -r /usr/lib/ckan/default/src/ckan/dev-requirements.txt
    log_out "finished installing CKAN source\nlinked who.ini\ninstalled CKAN requirements"
    deactivate
}

frontend-tools() {
    log_out "installing frontend tools"
    source /usr/lib/ckan/default/bin/activate
    olddir=$(pwd)
    cd /usr/lib/ckan/default/src/ckan/
    npm install less@1.7.5 nodewatch
    log_out "finished installing frontend tools"
    deactivate
    cd $olddir
}

# read DB configurations local ckan configuration file
ckan_read_db_config() {
    log_out "reading DB parameters from $1"
    TARGET_CONFIG=$1
    read TARGET_DB_USER TARGET_DB_PW TARGET_DB <<< \
    $(grep sqlalchemy.url $TARGET_CONFIG |\
      sed -n '
              s/^.*postgresql:\/\/\(.*\):\(.*\)@localhost\/\(.*\)$/\1 \2 \3/p
             '
    )
    echo -e "CKAN DB config TARGET:\n  db-user: $TARGET_DB_USER" |tee -a $LOGFILE
    echo "  db-password: $TARGET_DB_PW" |tee -a $LOGFILE
    echo "  db-name: $TARGET_DB" |tee -a $LOGFILE
    log_out "done reading DB parameters from config file"
}

ckan_read_solr_config() {
    log_out "reading SOLR parameters from $1"
    TARGET_CONFIG=$1
    read SOLR_CORE <<< $(cat $TARGET_CONFIG |sed -n \
      's|^[^#]*solr_url.*/solr/\(.*\)$|\1|p')
    echo "SOLR core for CKAN: $SOLR_CORE" |tee -a $LOGFILE
    log_out "finished reading SOLR parameters"
}

config_solr() {
    log_out "configuring SOLR for ckan"
    CORE=$1
    sudo mkdir /var/solr/data/$CORE  
    sudo touch /var/solr/data/$CORE/core.properties
    sudo cp -a /opt/solr/server/solr/configsets/basic_configs/conf /var/solr/data/$CORE
    sudo ln -s /usr/lib/ckan/default/src/ckan/ckan/config/solr/schema.xml \
	       /var/solr/data/$CORE/conf/schema.xml
    sudo chown -R solr:solr /var/solr
    sudo systemctl restart solr
    log_out "done configuring SOLR"
}

## destroy local ckan-DB, drop ckan db-user
db_destroy_local() {
    log_out "dropping DB user $TARGET_DB_USER and DB :$TARGET_DB"
    PGPASSWORD=$TARGET_DB_PW dropdb -h localhost -U "$TARGET_DB_USER" "$TARGET_DB"
    sudo -u postgres dropuser $TARGET_DB_USER
    sudo -u postgres psql -l
    log_out "dropped DB user and DB"
}

## To set up a virgin postgres installation
db_setup_local() {
    log_out "creating user $TARGET_DB_USER with password $TARGET_DB_PW"
    sudo -u postgres psql -c "CREATE USER $TARGET_DB_USER WITH PASSWORD '$TARGET_DB_PW'"
    sudo -u postgres createdb -O $TARGET_DB_USER $TARGET_DB -E utf-8
    sudo -u postgres psql -l |cut -d \| -f 1 |grep $TARGET_DB_USER
    hasuser=$?
    sudo -u postgres psql -l |cut -d \| -f 2 |grep $TARGET_DB
    hasdb=$?
    if [[ ! ( $hasuser == 0 && $hasdb == 0 ) ]]; then
	echo "creation of DB $TARGET_DB and/or DB user $TARGET_DB_USER failed"\
	    |tee -a $LOGFILE
	sudo -u postgres psql -l |tee -a $LOGFILE
	exit 1
    else
	sudo -u postgres psql -l |tee -a $LOGFILE
	log_out "created Postgresql user and DB"
    fi
}

# comment/uncomment all plugins in local configuration
ckan_config_comment_plugins() {
    command=$1
    TARGET_CONFIG=$2
    log_out "$command the plugins in ini file"
    if [ "$command" = "comment" ]; then
	cmd='s/^/#/'
    elif [ "$command" = "uncomment" ]; then
	cmd='s/^#//'
    fi
    sudo sed -i '/ckan.plugins *=/,/=/ {
                   /ckan.plugins *=/ '$cmd'
                   /=/ ! '$cmd'
                 }' $TARGET_CONFIG
    log_out "done $command the plugins"
}

## Initialize local DB with CKAN tables
db_init_local() {
    TARGET_CONFIG=$1
    log_out "initializing local CKAN-DB"
    source /usr/lib/ckan/default/bin/activate
    paster --plugin=ckan db init -c $TARGET_CONFIG
    deactivate
    log_out "done initializing local CKAN-DB"
}



git-setup() {
    echo "Configuring git-repos (very EAWAG specific!) ..."
    echo
    source /usr/lib/ckan/default/bin/activate
    cd /usr/lib/ckan/default/src/ckan/
    # add remotes
    git remote add origin git@github.com:eawag-rdm/eawag-ckan.git
    git remote add upstream git@github.com:ckan/ckan.git
    # configure remotes
    git config --unset remote.origin.fetch
    git config --add remote.origin.fetch +refs/heads/master:refs/remotes/origin/master
    git config --add remote.origin.push +refs/heads/master:refs/heads/master
    #


    ##### CONTINUE HERE #######
    git config --unset remote.upstream.fetch 
    git config --add remote.upstream.fetch +refs/heads/$UPSTREAM_BRANCH:refs/remotes/upstream/$UPSTREAM_BRANCH
    git config --add remote.upstream.fetch +refs/heads/upstream_master:refs/remotes/upstream/upstream_master
    #
    # set up branches
    git fetch upstream
    git checkout -b $UPSTREAM_BRANCH upstream/$UPSTREAM_BRANCH
    git config --add branch.$UPSTREAM_BRANCH.pushremote origin
    #
    git fetch upstream
    git checkout -b ckan_master upstream/master
    git config --add branch.ckan_master.pushremote ckan-fork
    #
    git checkout master
    deactivate
}

install-extensions() {
    echo "Installing extensions"
    echo
    source /usr/lib/ckan/default/bin/activate
    for plugin in $PLUGINS; do
	cd /usr/lib/ckan/default/src
	echo "Installing ${PLUGINREPO}/${plugin}.git"
	git clone ${PLUGINREPO}/${plugin}.git
	cd $plugin
	python setup.py develop
	pip install -r requirements.txt || pip install -r pip-requirements.txt || echo "No requirements-file found."
    done
    echo "Don't forget to activate the plugins in /etc/ckan/default/development.ini"
    deactivate
}

# echo "$*"
# if [[ "$*" =~ .*\ -h ]]; then
#     usage
#     exit 0
# elif [[ "$1" == "onlyext" ]]; then
#     install-extensions
# elif [[ $# -ne 2 ]]; then
#     usage
#     exit 1
# else
#     parent="$1"
#     gitsrc="$2"
#     # fs_setup
#     # mk_virtenv
#     # install_src
#     # py-requirements
#     frontend-tools
#     # git-setup
#     # install-extensions
# fi
