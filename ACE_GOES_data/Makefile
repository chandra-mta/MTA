# -*- makefile -*-
#####################################################################
#																	#
# 	Make file for ACE/GOES Data Update Scripts      				#
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
#   	NPYTHON: python path 
#
TASK    = MTA_Rad
VERSION = 1.0
ROOT    = /home/isobe/proj
WEB     = /home/isobe/www
WDIR    = $(WEB)/DAILY/mta_rad
SOFT    = /soft
NPYTHON = python
NPERL   = /usr/bin/perl
NPPKG   = /usr/bin/python2.7/site-packages
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
OMAIN   = $(OROOT)/$(TASK)
OSCRIPT = $(OMAIN)/Scripts
OWEB    = /data/mta/www
OWEB2   = /data/mta_www
OWDIR   = /data/mta4/www/DAILY/mta_rad
OHPATH  = /data/mta/Script/MTA_Rad/house_keeping
ASCDS   = /home/ascds
OPYTHON = /proj/sot/ska/bin/python
OPERL   = /usr/local/bin/perl
OPPKG   = /proj/sot/ska/arch/x86_64-linux_CentOS-5/lib/python2.7/site-packages
OWADRS  = cxc.cfa.harvard.edu/mta_day
#
#--- files, directories to be copied
#
SHARE   = get_radiation_data.py README get_rad_wrap_script get_rad_main_script
HK      = house_keeping
HPAGE   = *.html 
#
#--- Installation
# 
install:
ifdef SHARE
	mkdir -p $(NSCRIPT)
	rsync --times --cvs-exclude $(SHARE)  $(NSCRIPT)/
	rsync -r --times --cvs-exclude $(HK)  $(NSCRIPT)/
	mkdir -p $(INSTALL_SHARE)/Exc
#
#--- change lines in the python scripts to appropriate ones
#
	for ENT in $(SHARE); do \
		sed -i "s,$(OPYTHON),$(NPYTHON),g"     $(NSCRIPT)/$$ENT;\
		sed -i "s,$(OPERL),$(NPERL),g"         $(NSCRIPT)/$$ENT;\
		sed -i "s,$(OPPKG),$(NPPKG),g"         $(NSCRIPT)/$$ENT;\
		sed -i "s,$(OHPATH),$(NHPATH),g"       $(NSCRIPT)/$$ENT;\
		sed -i "s,$(OSCRIPT),$(NSCRIPT),g"     $(NSCRIPT)/$$ENT;\
		sed -i "s,$(OMAIN),$(INSTALL_SHARE),g" $(NSCRIPT)/$$ENT;\
		sed -i "s,$(OROOT),$(ROOT),g" 		   $(NSCRIPT)/$$ENT;\
		sed -i "s,$(OWDIR),$(WDIR),g"          $(NSCRIPT)/$$ENT;\
		sed -i "s,$(ASCDS),$(SOFT),g"          $(NSCRIPT)/$$ENT;\
        sed -i "s,$(OWEB),$(WEB),g"            $(NSCRIPT)/$$ENT;\
        sed -i "s,$(OWEB2),$(WEB),g"           $(NSCRIPT)/$$ENT;\
		sed -i "s,$(OWADRS),$(NWADRS),g"       $(NSCRIPT)/$$ENT;\
	done
#
#--- change lines in the dir_list_py to appropriate ones
#
	sed -i "s,$(OWDIR),$(WDIR),g"          $(NSCRIPT)/$(HK)/dir_list_py
	sed -i "s,$(OHPATH),$(NHPATH),g"       $(NSCRIPT)/$(HK)/dir_list_py
	sed -i "s,$(OSCRIPT),$(NSCRIPT),g"     $(NSCRIPT)/$(HK)/dir_list_py
	sed -i "s,$(OMAIN),$(INSTALL_SHARE),g" $(NSCRIPT)/$(HK)/dir_list_py
	sed -i "s,$(OROOT),$(ROOT),g" 		   $(NSCRIPT)/$(HK)/dir_list_py
endif
ifdef WEB
	mkdir -p $(WDIR)/ACE
	mkdir -p $(WDIR)/GOES
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

