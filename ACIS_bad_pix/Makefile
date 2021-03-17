# -*- makefile -*-
#####################################################################
#																	#
# 	Make file for ACIS Bad Pixel Detection/Bias Computation			#
# 																	#
# 		author: t isobe (tisobe@cfa.harvard.edu)					#
# 		last update: apr 25, 2019									#
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
TASK    = Bad_pixels
VERSION = 1.0
ROOT    = /home/isobe/proj
WEB     = /home/isobe/www
WDIR_BP = $(WEB)/Bad_pixels
WDIR_BI = $(WEB)/Bias_Bkg
SOFT    = /soft
NBIN    = $(ROOT)/bin
NBDATA  = $(ROOT)/bdata
NPYTHON = /data/mta/Script/Python3.6/envs/ska3/bin/python
NPERL   = /usr/bin/perl
NPPKG   = /data/mta/Script/Python3.6/envs/ska3/lib/python3.6/site-packages:/data/mta/Script/Python3.6/lib/python3.6/site-packages/
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
OMAIN   = $(OROOT)/ACIS/$(TASK)
OSCRIPT = $(OMAIN)/Scripts
OWEB    = /data/mta/www
OWEB2   = /data/mta_www
OWDIR   = /data/mta/www
OWDIR_BP= $(OWDIR)/mta_bad_pixel
OWDIR_BI= $(OWDIR)/mta_bias_bkg
OHPATH  = $(OMAIN)/house_keeping
ASCDS   = /home/ascds
OPYTHON = /data/mta/Script/Python3.6/envs/ska3/bin/python
OPPKG   = /data/mta/Script/Python3.6/envs/ska3/lib/python3.6/site-packages:/data/mta/Script/Python3.6/lib/python3.6/site-packages/
OPERL   = /usr/local/bin/perl
OBIN    = /data/mta/MTA/bin
OBDATA  = /data/mta/MTA/data
OWADRS  = cxc.cfa.harvard.edu/mta_days
#
#--- files, directories to be copied/modified
#
SHARE   = *.py *_script README
S_LIST  = $(wildcard *.py *_script) README
HK      = house_keeping
H_LIST  = bias_dir_list_py  bias_home.html  dir_list_py  head  mid  tail
#
#--- Installation
# 
install:
ifdef SHARE
	mkdir -p $(NSCRIPT)
	rsync --times --cvs-exclude $(SHARE)  $(NSCRIPT)/
	rsync -r --times --cvs-exclude $(HK)  $(NSCRIPT)/
	mkdir -p $(INSTALL_SHARE)/Exc
	mkdir -p $(INSTALL_SHARE)/Data/Disp_dir
	mkdir -p $(INSTALL_SHARE)/Bias_data/Bias_save
	mkdir -p $(INSTALL_SHARE)/Bias_data/Info_dir
#
#--- change lines in the python scripts to appropriate ones
#
	for ENT in $(S_LIST); do \
		sed -i "s,$(OPYTHON),$(NPYTHON),g"     $(NSCRIPT)/$$ENT;\
		sed -i "s,$(OPERL),$(NPERL),g"         $(NSCRIPT)/$$ENT;\
		sed -i "s,$(OPPKG),$(NPPKG),g"         $(NSCRIPT)/$$ENT;\
		sed -i "s,$(OHPATH),$(NHPATH),g"       $(NSCRIPT)/$$ENT;\
		sed -i "s,$(OSCRIPT),$(NSCRIPT),g"     $(NSCRIPT)/$$ENT;\
		sed -i "s,$(OWDIR_BP),$(WDIR_BP),g"    $(NSCRIPT)/$$ENT;\
		sed -i "s,$(OWDIR_BI),$(WDIR_BI),g"    $(NSCRIPT)/$$ENT;\
		sed -i "s,$(OMAIN),$(INSTALL_SHARE),g" $(NSCRIPT)/$$ENT;\
		sed -i "s,$(OROOT),$(ROOT),g" 		   $(NSCRIPT)/$$ENT;\
		sed -i "s,$(ASCDS),$(SOFT),g"          $(NSCRIPT)/$$ENT;\
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
		sed -i "s,$(OHPATH),$(NHPATH),g"       $(NSCRIPT)/$(HK)/$$ENT;\
		sed -i "s,$(OWDIR_BP),$(WDIR_BP),g"    $(NSCRIPT)/$(HK)/$$ENT;\
		sed -i "s,$(OWDIR_BI),$(WDIR_BI),g"    $(NSCRIPT)/$(HK)/$$ENT;\
		sed -i "s,$(OSCRIPT),$(NSCRIPT),g"     $(NSCRIPT)/$(HK)/$$ENT;\
		sed -i "s,$(OMAIN),$(INSTALL_SHARE),g" $(NSCRIPT)/$(HK)/$$ENT;\
		sed -i "s,$(OROOT),$(ROOT),g" 		   $(NSCRIPT)/$(HK)/$$ENT;\
		sed -i "s,$(OWDIR_BP),$(WDIR_BP),g"    $(NSCRIPT)/$(HK)/$$ENT;\
		sed -i "s,$(OWDIR_BI),$(WDIR_BI),g"    $(NSCRIPT)/$(HK)/$$ENT;\
	done
endif
ifdef WEB
	mkdir -p $(WDIR_BP)/Html_dir
	mkdir -p $(WDIR_BP)/Plots
	mkdir -p $(WDIR_BP)/Disp_dir

	mkdir -p $(WDIR_BP)/Bias_save
	mkdir -p $(WDIR_BP)/Plots
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

