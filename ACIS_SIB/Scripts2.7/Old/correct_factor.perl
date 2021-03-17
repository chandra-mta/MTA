#!/usr/bin/perl 

#################################################################################################################
#														#
#	correct_factor.perl: adjust lres reuslts files for the area removed as the sources remvoed		#
#			     perl script: exclude_srouces.perl must be run before using this script as it uses	#
#			     information created by that perl script.						#
#														#
#		author: t. isobe (tisobe@cfa.harvard.edu)							#
#														#
#		last update: Feb 12, 2010									#
#														#
#################################################################################################################

#
#--- read all correciton factor information
#

#open(FH, "/data/mta/Script/ACIS/SIB/Correct_excess/Input/Reg_files/ratio_table");
open(FH, "./Reg_files/ratio_table");
while(<FH>){
	chomp $_;
	@atemp = split(/\s+/, $_);
	$ratio = $atemp[1];


	@btemp = split(/N/, $atemp[0]);
	if($btemp[0] =~ /_/){
		@ctemp = split(/_/, $btemp[0]);
		$msid  = $ctemp[0];
	}else{
		$msid  = $btemp[0];
	}
	$msid  =~ s/acisf//;

	@ctemp = split(/ccd/, $atemp[0]);
	@dtemp = split(/_/, $ctemp[1]);
	$ccd   = $dtemp[0];

	%{ratio.$msid.$ccd} = (ratio => ["$ratio"]);
}
close(FH);

#
#--- find all fits file names processed
#

$input = `ls /data/mta/Script/ACIS/SIB/Correct_excess/Outdir/lres/mtaf*.fits`;
@files = split(/\s+/, $input);

OUTER:
foreach $ent (@files){
	@atemp = split(/N/, $ent);
	@btemp = split(/mtaf/, $atemp[0]);
	$msid  = $btemp[1];
	if($msid =~/_/){
		@atemp = split(/_/, $msid);
		$msid  = $atemp[0];
	}
	@atemp = split(/acis/, $ent);
	@btemp = split(/lres/, $atemp[1]);
	$ccd   = $btemp[0];

	$div   = ${ratio.$msid.$ccd}{ratio}[0];
	if($div >= 1){
		next OUTER;
	}

#
#--- correct the observation rate by devided by the ratio (all sources removed area)/(original are)
#
	if($div > 0){
print "$ent: $div\n";
		
		$line  = "SSoft=SSoft/$div,Soft=Soft/$div,Med=Med/$div,Hard=Hard/$div,Harder=Harder/$div,Hardest=Hardest/$div";
		system("dmtcalc infile=$ent outfile=out.fits expression=\"$line\" clobber=yes");
		system("mv out.fits $ent");
	}else{
		print "WARGNING!!! div <= 0 for $ent\n";
	}
}
