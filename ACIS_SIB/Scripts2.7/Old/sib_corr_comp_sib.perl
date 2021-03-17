#!/usr/bin/env /usr/local/bin/perl

#################################################################################################
#												#
#	sib_corr_comp_sib.perl: this script extract acis evt1 files from archeive, and		#
#		       compute SIB using Jim's mta_pipe routine					#
#												#
#       make sure that following settings are done, and Reportdir is actually created		#
#        rm -rf param										#
#        mkdir param										#
#        source /home/mta/bin/reset_param							#
#        setenv PFILES "${PDIRS}:${SYSPFILES}"							#
#        set path = (/home/ascds/DS.release/bin/  $path)					#
#        setenv MTA_REPORT_DIR  /data/mta/Script/ACIS/SIB/Correct_excess/Working_dir/Reportdir/ #
#												#
#	author: t. isobe (tisobe@cfa.harvard.edu)						#
#												#
#	last update: Apr 22, 2013								#
#												#
#################################################################################################

$dir = `pwd`;
chomp $dir;
system("ls Input/*fits > zlist");
open(FH, "./zlist");
open(OUT,'>./Input/input_dat.lis');
while(<FH>){
	chomp $_;
	print OUT "$dir/$_\n";
}
close(OUT);
close(FH);
system("rm -rf zlist");

$test = `ls *`;
if($test =~ /Input/){
}else{
	system("mkdir Outdir");
}

$indir  = "$dir".'/Input/';
$outdir = "$dir".'/Outdir/';
$repdir = "$dir".'/Reportdir/';

#
#---- here is the mta_pipe to extract sib data
#

system("flt_run_pipe -i $indir -r input -o $outdir  -t  mta_monitor_sib.ped -a \"genrpt=no\" ");

#
#--- this script creates a week long data set
#

system("mta_merge_reports sourcedir=$outdir destdir=$repdir limits_db=foo groupfile=foo stprocfile=foo grprocfile=foo compprocfile=foo cp_switch=yes");

