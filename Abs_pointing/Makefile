# -*- makefile -*-
#####################################################################
#																	#
# 	Make file for Celestial Locaiton Monitor Routine				#
# 																	#
# 		author: t isobe (tisobe@cfa.harvard.edu)					#
# 		last update: Jun 15, 2018									#
# 																	#
#####################################################################

#
#--- Change the following lines to appropriate ones
#
#   	TASK: 	 task name;  the script will be kept there
#   	ROOT: 	 main script directory
#   	WEB:  	 main web directory
#       WDIR:	 the directory where the html pages will be kept
#       NHTML:   the html address
#       NBIN:    extra scripts are kept here
#       NBDATA:	 special shared data are kept here
#   	NPYTHON: python path 
#
TASK    = Abs_pointing
VERSION = 1.0
ROOT    = /home/isobe/proj
WEB     = /home/isobe/www
WDIR    = $(WEB)/$(TASK)
NHTML   = /cxc.cfa.harvard.edu/mta_test
NBIN    = $(ROOT)/bin
NBDATA  = $(ROOT)/bdata
SOFT    = /soft
NPYTHON = python
NPERL   = /usr/bin/perl
NWADRS  = cxc.cfa.harvard.edu/mta
#
#--- Define generic installation paths
#
ifndef INSTALL
	INSTALL = $(ROOT)
endif

ifndef TASK
	TASK = share
endif

ifndef INSTALL_SHARE
	INSTALL_SHARE = $(INSTALL)/$(TASK)
endif
#
#--- this is where all scripts will be kept
#
NSCRIPT = $(INSTALL_SHARE)/Scripts
NPATH   = $(NSCRIPT)/house_keeping
#
#--- changing lines in scripts (they will be replaced by the lines defined above)
#
OROOT   = /data/mta/Script
OMAIN   = $(OROOT)/ALIGNMENT/Abs_pointing
OSCRIPT = $(OMAIN)/Abs_pointing
OWEB    = /data/mta/www
OWEB2   = /data/mta_www
OPATH   = $(OMAIN)/house_keeping
OBIN    = /data/mta/MTA/bin
OBDATA  = /data/mta/MTA/data
OWDIR   = /data/mta/www/mta_aiming
OHTML   = /cxc.cfa.harvard.edu/mta
OHTML2  = /cxc.cfa.harvard.edu/mta_days
ASCDS   = /home/ascds
OPYTHON = /proj/sot/ska/bin/python
OPERL   = /usr/local/bin/perl
OWADRS  = cxc.cfa.harvard.edu/mta_days
#
#--- files, directories to be copied
#
SHARE   = *.py  *_script* README
S_LIST  = $(wildcard *.py *_script*) README
HK      = house_keeping
HPAGE   = *.html
W_LIST  = $(wildcard *.html)
#
#--- Installation
# 
install:
ifdef SHARE
	mkdir -p $(NSCRIPT)
	rsync --times --cvs-exclude $(SHARE)  $(NSCRIPT)/
	rsync -r --times --cvs-exclude $(HK)  $(NSCRIPT)/
	mkdir -p $(INSTALL_SHARE)/Data
	mkdir -p $(INSTALL_SHARE)/Exc
#
#--- change lines in the perl scripts to appropriate ones
#
	for ENT in $(S_LIST); do \
		sed -i "s,$(OPYTHON),$(NPYTHON),g"     $(NSCRIPT)/$$ENT;\
		sed -i "s,$(OPERL),$(NPERL),g"         $(NSCRIPT)/$$ENT;\
		sed -i "s,$(OBIN),$(NSCRIPT),g"        $(NSCRIPT)/$$ENT;\
		sed -i "s,$(OPATH),$(NPATH),g"         $(NSCRIPT)/$$ENT;\
		sed -i "s,$(OSCRIPT),$(NSCRIPT),g"     $(NSCRIPT)/$$ENT;\
		sed -i "s,$(OMAIN),$(INSTALL_SHARE),g" $(NSCRIPT)/$$ENT;\
		sed -i "s,$(OROOT),$(ROOT),g"          $(NSCRIPT)/$$ENT;\
		sed -i "s,$(OWDIR),$(WDIR),g"          $(NSCRIPT)/$$ENT;\
		sed -i "s,$(OHTML),$(NHTML),g"         $(NSCRIPT)/$$ENT;\
		sed -i "s,$(OHTML2),$(NHTML),g"        $(NSCRIPT)/$$ENT;\
		sed -i "s,$(ASCDS),$(SOFT),g"          $(NSCRIPT)/$$ENT;\
        sed -i "s,$(OWEB),$(WEB),g"            $(NSCRIPT)/$$ENT;\
        sed -i "s,$(OWEB2),$(WEB),g"           $(NSCRIPT)/$$ENT;\
		sed -i "s,$(OWADRS),$(NWADRS),g"       $(NSCRIPT)/$$ENT;\
	done
#
#--- change lines in the dir_list to appropriate ones
#
	sed -i "s,$(OBIN),$(NBIN),g"           $(NSCRIPT)/$(HK)/dir_list
	sed -i "s,$(OBDATA),$(NBDATA),g"       $(NSCRIPT)/$(HK)/dir_list
	sed -i "s,$(OPATH),$(NPATH),g"         $(NSCRIPT)/$(HK)/dir_list
	sed -i "s,$(OWDIR),$(WDIR),g"          $(NSCRIPT)/$(HK)/dir_list
	sed -i "s,$(OSCRIPT),$(NSCRIPT),g"     $(NSCRIPT)/$(HK)/dir_list
	sed -i "s,$(OMAIN),$(INSTALL_SHARE),g" $(NSCRIPT)/$(HK)/dir_list
	sed -i "s,$(OHTML),$(NHTML),g"         $(NSCRIPT)/$(HK)/dir_list
	sed -i "s,$(OHTML2),$(NHTML),g"        $(NSCRIPT)/$(HK)/dir_list
endif
#
#--- copying html pages
#
ifdef WEB
	mkdir -p $(WDIR)
	rsync  -r --times --cvs-exclude $(HPAGE) $(WDIR)
	ln -s $(INSTALL_SHARE)/Data  $(WDIR)/Data
	mkdir -p $(WDIR)/Plots
#
#--- change links to appropriate ones
#
	for ENT in $(W_LIST); do \
		sed -i "s,$(OHTML),$(NHTML),g"        $(WDIR)/$$ENT;\
		sed -i "s,$(OHTML2),$(NHTML),g"       $(WDIR)/$$ENT;\
	done
endif
#
#--- Create a distribution tar file for this program
#
dist:
	mkdir $(TASK)-$(VERSION)
	rsync -aruvz --cvs-exclude --exclude $(TASK)-$(VERSION) * $(TASK)-$(VERSION)
	tar cvf $(TASK)-$(VERSION).tar $(TASK)-$(VERSION)
	gzip --best $(TASK)-$(VERSION).tar
	rm -rf $(TASK)-$(VERSION)/

