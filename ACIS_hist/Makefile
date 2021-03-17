# -*- makefile -*-
#####################################################################
#																	#
# 	Make file for ACIS Histogram mode Trending             			#
# 																	#
# 		author: t isobe (tisobe@cfa.harvard.edu)					#
# 		last update: Apr 25, 2019									#
# 																	#
#####################################################################

#
#--- Change the following lines to appropriate ones
#
#   	TASK: 	 task name;  the script will be kept there
#   	ROOT: 	 main script directory
#   	WEB:  	 main web directory
#       WDIR:	 the directory where the html pages will be kept
#   	NPYTHON: python path 
#
TASK    = ACIS_hist
VERSION = 1.0
ROOT    = /home/isobe/proj
WEB     = /home/isobe/www
NSITE   = $(WEB)/$(TASK)
NBIN    = $(ROOT)/bin
NBDATA  = $(ROOT)/bdata
NPYTHON = /data/mta/Script/Python3.6/envs/ska3/bin/python
NPPKG	= /data/mta/Script/Python3.6/envs/ska3/lib/python3.6/site-packages:/data/mta/Script/Python3.6/lib/python3.6/site-packages/
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
NHPATH  = $(NSCRIPT)/house_keeping
#
#--- changing lines in scripts (they will be replaced by the lines defined above)
#
OROOT	= /data/mta/Script
OMAIN   = $(OROOT)/ACIS/Acis_hist
OSCRIPT = $(OMAIN)/Scripts
OWEB    = /data/mta/www
OWEB2   = /data/mta_www
OSITE   = $(OWEB)/mta_acis_hist
OHPATH  = $(OMAIN)/house_keeping
OPYTHON = /data/mta/Script/Python3.6/envs/ska3/bin/python
OPPKG   = /data/mta/Script/Python3.6/envs/ska3/lib/python3.6/site-packages:/data/mta/Script/Python3.6/lib/python3.6/site-packages/
OBIN    = /data/mta/MTA/bin
OBDATA  = /data/mta/MTA/data
OWADRS  = cxc.cfa.harvard.edu/mta_days
#
#--- files, directories to be copied/modified
#
SHARE   = *.py *_script* README
S_LIST  = $(wildcard *.py *_script*) README 
HK      = house_keeping
H_LIST  = dir_list_py acis_hist_main.html
SUB_LIST=  Fittings  Html_pages Plot_indivisual
#
#--- Installation
# 
install:
ifdef SHARE
	mkdir -p $(NSCRIPT)
	rsync --times --cvs-exclude $(SHARE)  $(NSCRIPT)/
	rsync -r --times --cvs-exclude $(HK)  $(NSCRIPT)/
	mkdir -p $(INSTALL_SHARE)/Data
	mkdir -p $(INSTALL_SHARE)/Data/Dist_data
	mkdir -p $(INSTALL_SHARE)/Exc
#
#--- change lines in the python scripts to appropriate ones
#
	for ENT in $(S_LIST); do \
		sed -i "s,$(OPYTHON),$(NPYTHON),g"     $(NSCRIPT)/$$ENT;\
		sed -i "s,$(OPPKG),$(NPPKG),g"         $(NSCRIPT)/$$ENT;\
		sed -i "s,$(OHPATH),$(NHPATH),g"       $(NSCRIPT)/$$ENT;\
		sed -i "s,$(OSITE),$(NSITE),g"         $(NSCRIPT)/$$ENT;\
		sed -i "s,$(OSCRIPT),$(NSCRIPT),g"     $(NSCRIPT)/$$ENT;\
		sed -i "s,$(OMAIN),$(INSTALL_SHARE),g" $(NSCRIPT)/$$ENT;\
		sed -i "s,$(OROOT),$(ROOT),g" 		   $(NSCRIPT)/$$ENT;\
        sed -i "s,$(OWEB),$(WEB),g"            $(NSCRIPT)/$$ENT;\
        sed -i "s,$(OWEB2),$(WEB),g"           $(NSCRIPT)/$$ENT;\
		sed -i "s,$(OWADRS),$(NWADRS),g"       $(NSCRIPT)/$$ENT;\
	done
#
#--- change lines in the dir_list_py to appropriate ones
#
	for ENT in $(H_LIST); do \
		sed -i "s,$(OBIN),$(NBIN),g"           $(NSCRIPT)/$(HK)/$$ENT;\
		sed -i "s,$(OBDATA),$(NBDATA),g"       $(NSCRIPT)/$(HK)/$$ENT;\
		sed -i "s,$(OSITE),$(NSITE),g"         $(NSCRIPT)/$(HK)/$$ENT;\
		sed -i "s,$(OHPATH),$(NHPATH),g"       $(NSCRIPT)/$(HK)/$$ENT;\
		sed -i "s,$(OSCRIPT),$(NSCRIPT),g"     $(NSCRIPT)/$(HK)/$$ENT;\
		sed -i "s,$(OMAIN),$(INSTALL_SHARE),g" $(NSCRIPT)/$(HK)/$$ENT;\
		sed -i "s,$(OROOT),$(ROOT),g" 		   $(NSCRIPT)/$(HK)/$$ENT;\
	done
endif
ifdef WEB
	mkdir -p $(NSITE)
	for ENT in $(SUB_LIST); do \
		mkdir -p $(NSITE)/$$ENT;\
	done
	rsync --times --cvs-exclude $(NSCRIPT)/$(HK)/acis_hist_main.html $(NSITE)/
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

