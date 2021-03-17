#!/usr/bin/perl

#########################################################################################
#											#
# sib_corr_get_data.perl: extract acis evt2 fits files from archieve			#
#											#
#	author: t. isobe (tisobe@cfa.harvard.edu)					#
#											#
#	last update: Jun 23, 2006							#
#											#
#########################################################################################

#
#--- get user and pasword
#

$dare   = `cat /data/mta/MTA/data/.dare`;
$hakama = `cat /data/mta/MTA/data/.hakama`;

chomp $dare;
chomp $hakama;

#
#--- a list of data file names
#

@list   = ();

open(FH, "acis_obs");
while(<FH>){
	chomp $_;
	@atemp = split(/\s+/, $_);
	push(@list, $atemp[0]);
}
close(FH);

#
#--- check whether a directory exists
#

$test = `ls *`;
if($test =~ /Input/){
}else{
	system("mkdir Input");
}

#
#--- extract acis evt1 using arc4gl 
#

foreach $file (@list){
        open(OUT, '>./Input/input_line');
        print OUT "operation=retrieve\n";
        print OUT "dataset=flight\n";
        print OUT "detector=acis\n";
        print OUT "level=2\n";
        print OUT "filetype=evt2\n";
        print OUT "filename=$file\n";
        print OUT "go\n";
        close(OUT);

        system("cd Input; echo $hakama  |/home/ascds/DS.release/bin/arc4gl -U$dare -Sarcocc -i./input_line");
	system("gzip -d ./Input/*gz");
}
