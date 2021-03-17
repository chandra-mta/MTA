# -*- makefile -*-
#####################################################################
#																	#
# 	Make file for Grating											#
# 																	#
# 		author: t isobe (tisobe@cfa.harvard.edu)					#
# 		last update: Sep 27, 2018									#
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
TASK    = Grating
VERSION = 1.0
ROOT    = /home/isobe/proj
WEB     = /home/isobe/www
SOFT    = /soft
NSITE   = $(WEB)/$(TASK)
NBIN    = $(ROOT)/bin
NBDATA  = $(ROOT)/bdata
NPYTHON = python
NPPKG	= /usr/bin/python2.7/site-packages
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
NHPATH  = $(NSCRIPT)/house_keeping
#
#--- changing lines in scripts (they will be replaced by the lines defined above)
#
OROOT	= /data/mta/Script
OMAIN   = $(OROOT)/Grating/
OWEB    = /data/mta_www
OSITE   = $(OWEB)/mta_grat
OHPATH  = $(OMAIN)/house_keeping
ASCDS   = /home/ascds
OPYTHON = /proj/sot/ska/bin/python
OPPKG   = /proj/sot/ska/arch/x86_64-linux_CentOS-5/lib/python2.7/site-packages
OPERL   = /usr/local/bin/perl
OBIN    = /data/mta/MTA/bin
OBDATA  = /data/mta/MTA/data
OWADRS  = cxc.cfa.harvard.edu/mta_days
#
#--- files, directories to be copied/modified
#
SHARE   = Angles  EdE_trend  Focus  Grating_DB  Grating_EdE  Grating_HAK Zero 
S_LIST  = $(wildcard Angles/Scripts/*  EdE_trend/Scripts/*  Focus/Scripts/*  Grating_DB/Scripts/*  Grating_EdE/Scripts/*  Grating_HAK/Scripts/* Zero/Scripts/* Angles/Scripts/house_keeping/*  EdE_trend/Scripts/house_keeping/*  Focus/Scripts/house_keeping/*  Grating_DB/Scripts/house_keeping/*  Grating_EdE/Scripts/house_keeping/*  Grating_HAK/Scripts/house_keeping/* Zero/Scripts/house_keeping/*) 
SUB_LIST = $(SHARE)
#
#--- Installation
# 
install:
ifdef SHARE
	mkdir -p $(INSTALL_SHARE)
	rsync -r --times --cvs-exclude $(SHARE)  $(INSTALL_SHARE)/
#
#--- change lines in the python scripts to appropriate ones
#
	for ENT in $(S_LIST); do \
		sed -i "s,$(OPYTHON),$(NPYTHON),g"     $(INSTALL_SHARE)/$$ENT;\
		sed -i "s,$(OPERL),$(NPERL),g"         $(INSTALL_SHARE)/$$ENT;\
		sed -i "s,$(OPPKG),$(NPPKG),g"         $(INSTALL_SHARE)/$$ENT;\
		sed -i "s,$(OHPATH),$(NHPATH),g"       $(INSTALL_SHARE)/$$ENT;\
		sed -i "s,$(OSITE),$(NSITE),g"         $(INSTALL_SHARE)/$$ENT;\
		sed -i "s,$(OMAIN),$(INSTALL_SHARE),g" $(INSTALL_SHARE)/$$ENT;\
		sed -i "s,$(OROOT),$(ROOT),g" 		   $(INSTALL_SHARE)/$$ENT;\
		sed -i "s,$(ASCDS),$(SOFT),g" 		   $(INSTALL_SHARE)/$$ENT;\
        sed -i "s,$(OWEB),$(WEB),g"            $(INSTALL_SHARE)/$$ENT;\
		sed -i "s,$(OWADRS),$(NWADRS),g"       $(INSTALL_SHARE)/$$ENT;\
	done
endif
ifdef WEB
	mkdir -p $(NSITE)
	rsync --times --cvs-exclude grating_main.html $(NSITE)/
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

