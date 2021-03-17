#!/usr/bin/perl

#################################################################################
#										#
#	state_mj_size_check.perl: check mj data and send out email if there is	#
#				  any anomaly					#
#										#
#		author: t. isobe (tiosbe@cfa.harvard.edu)			#
#										#
#		last update: Aug 24, 2012					#
#										#
#################################################################################

##############################################################
#
#--- setting directories
#
$dir_list = '/data/mta/Script/OBT/MJ/house_keeping/dir_list';
open(FH, $dir_list);
while(<FH>){
    chomp $_;
    @atemp = split(/\s+/, $_);
    ${$atemp[0]} = $atemp[1];
}   
close(FH);
##############################################################

system("ls -l $house_keeping/comprehensive_data_summary* > zsize");
open(FH, './zsize');
$i = 0;
while(<FH>){
	chomp $_;
	@atemp = split(/ /, $_);
	@line = ();
	foreach $ent (@atemp){
		if($ent =~ /\w/){
			push(@line, $ent);
		}
	}
	$size[$i] = $line[3];
	$i++;
}
close(FH);
system("rm zsize");

	
if($size[0] < $size[1]) {
	
	open (FILE, ">/tmp/mjmail.tmp");
	print FILE "Please check: \n";
	print FILE '/data/mta/www/mta_states/MJ/';
	print FILE "$year/mta_comprehensive_data_summary$year\n";
	close FILE;

#	system("/opt/local/bin/mh/send -draftmessage /tmp/mjmail.tmp");
	system("cat /tmp/mjmail.tmp | mailx -s \"Subject: MJ summary problem detected !!\n \" -r  isobe\@head.cfa.harvard.edu  isobe\@head.cfa.harvard.edu ");

	system("rm /tmp/mjmail.tmp");
}
