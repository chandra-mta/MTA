# -*- makefile -*-
#####################################################################
#																	#
# 	Make file for ACIS Science Run                       			#
# 																	#
# 		author: t isobe (tisobe@cfa.harvard.edu)					#
# 		last update: May 23, 2018									#
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
TASK    = ACIS_sci_run
VERSION = 1.0
ROOT    = /home/isobe/proj
WEB     = /home/isobe/www
NSITE   = $(WEB)/$(TASK)
NBIN    = $(ROOT)/bin
NBDATA  = $(ROOT)/bdata
NPYTHON = python
NPPKG	= /usr/bin/python2.7/site-packages
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
OMAIN   = $(OROOT)/ACIS/Acis_sci_run
OSCRIPT = $(OMAIN)/Acis_sci_run
OWEB    = /data/mta/www
OSITE   = $(OWEB)/mta_acis_sci_run
OHPATH  = $(OMAIN)/house_keeping
OPYTHON = /proj/sot/ska/bin/python
OPPKG   = /proj/sot/ska/arch/x86_64-linux_CentOS-5/lib/python2.7/site-packages
OBIN    = /data/mta/MTA/bin
OBDATA  = /data/mta/MTA/data
#
#--- files, directories to be copied/modified
#
SHARE   = *.py *_script* README col_list2004
S_LIST  = $(wildcard *.py *_script*) README
HK      = house_keeping
H_LIST  = dir_list  dir_list_py  science_long_term.html  science_run.html  sub_year.html
SUB_LIST=  Corner_pix Events_rej Long_term 
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

