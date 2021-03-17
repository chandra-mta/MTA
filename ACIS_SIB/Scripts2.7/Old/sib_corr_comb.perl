#!/usr/bin/env /usr/local/bin/perl

#################################################################################################
#												#
#	sib_corr_comb.perl: combine fits files in Outdir					#
#												#
#		author: ti.isobe (tisobe@cfa.harvard.edu)					#
#												#
#		last update: Apr 22, 2013							#
#												#
#################################################################################################

$start = $ARGV[0];		#--- start date in format of 2006:123:00:00:00
$end   = $ARGV[1];		#--- emd date
chomp $start;
chomp $end;

if($start eq '' || $end eq ''){
	print "\n   Usage: perl sib_corr_comb.perl 2006:153:00:00:00 2006:183:00:00:00\n";
	exit 1;
}

#
#--- change time format to sec from 1998.1.1.
#

$tstart = `axTime3 $start t d u s `;
$tstop  = `axTime3 $end   t d u s `;

#
#--- initialize
#

for($i = 0; $i < 10; $i++){
	@{ccd_list.$i} = ();
}

#
#--- find out names of fits files
#

$file = `ls Outdir/lres/*fits`;
@input_list = split(/\s+/, $file);

OUTER:
foreach $ent (@input_list){

#
#--- find out start and finish time of the data
#

	system("dmstat \"$ent\[cols time\]\" centroid=no > ztest");

	open(FH, './ztest');
	while(<FH>){
		chomp $_;
		if($_ =~ /min/){
			@atemp = split(/\s+/, $_);
			$min   = $atemp[2];
			$min   =~ s/\s//g;
		}
		if($_ =~ /max/){
			@atemp = split(/\s+/, $_);
			$max   = $atemp[2];
			$max   =~ s/\s//g;
		}
	}
	close(FH);
	system("rm -rf ztest");
#
#--- if the fits file contains data between tstart and tstop, keep them for
#--- further analysis
#
	if($min > $tstop || $max < $tstart){
		@btemp = split(/_acis/, $ent);
		$head  = "$btemp[0]";
		next OUTER;
	}

	OUTER:
	for($i = 0; $i < 10; $i++){
		if($ent =~ /acis$i/){
			push(@{ccd_list.$i}, $ent);
			next OUTER;
		}
	}
}

$test = `ls *`;
if($test =~ /Data/){
}else{
	system('mkdir Data');
}

for($i = 0; $i < 10; $i++){
	$first = shift(@{ccd_list.$i});

	if($first =~ /\w/){
		system("cp $first ./temp.fits");
	}

	foreach $file (@{ccd_list.$i}){
		system("dmmerge \"$file,temp.fits\" outfile=zmerged.fits outBlock=\"\" columnList=\"\" clobber=yes");
		system("mv ./zmerged.fits ./temp.fits");
	}
	$name = './Data/lres_ccd'."$i".'_merged.fits';
	system("mv ./temp.fits $name");
}
