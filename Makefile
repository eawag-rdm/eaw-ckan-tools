install : ck-sync ck-install-source ck-switch ck-dev
	cp ck-sync $(HOME)/bin; chmod u+x $(HOME)/bin/ck-sync
	cp ck-install-source $(HOME)/bin; chmod u+x $(HOME)/bin/ck-install-source
	cp ck-switch $(HOME)/bin; chmod u+x $(HOME)/bin/ck-switch
	cp ck-dev $(HOME)/bin; chmod u+x $(HOME)/bin/ck-dev
