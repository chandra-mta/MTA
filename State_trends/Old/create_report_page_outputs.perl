#!/usr/bin/perl 

#################################################################################################################
#														#
#	create_report_page_outputs.perl: create two report page for SOT page					#
#														#
#		author: t. isobe (tisobe@cfa.harvard.edu)							#
#														#
#		last update: Aug 24, 2012									#
#														#
#################################################################################################################	


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

system("rm $web_dir/mta_comprehensive_data_summary"); 
system("rm $web_dir/sim_data_summary"); 
system("cat $data_dir/mj_header   $house_keepingmj/comprehensive_data_summary > $web_dir/mta_comprehensive_data_summary");
system("cat $data_dir/sim_header $house_keepingac/sim_data_summary           > $web_dir/sim_data_summary");

system("chgrp mtagroup $web_dir/*");
