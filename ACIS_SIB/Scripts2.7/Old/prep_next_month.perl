#!/usr/bin/env /usr/local/bin/perl

#################################################################################################################
#														#
#	prep_next_month.perl: prepare for the next month entries						#
#														#
#		author: t. isobe (tisobe@cfa.harvard.edu)							#
#														#
#		last update: Apr 23, 2013									#
#														#
#################################################################################################################

$year  = $ARGV[0];		# format 2011, 2012, etc
$month = $ARGV[1];		# format 01, 02,..., 10, 11, 12

$outfile = '/data/mta_www/mta_sib/Plots/Plot_'."$year".'_'."$month";

system("mkdir $outfile");

system("cp /data/mta_www/mta_sib/Plots/Plot_2011_02/*html $outfile/");

for($i = 0; $i < 10; $i++){
	$file1 = 'indep_plot_ccd'."$i".'.gif';
	$file2 = 'total_data_ccd'."$i".'.gif';
	system("cp /data/mta4/MTA/data/no_data.gif $file1");
	system("cp /data/mta4/MTA/data/no_data.gif $file2");
}

#
#--- Level 2
#
$outfile = '/data/mta_www/mta_sib/Lev2/Plots/Plot_'."$year".'_'."$month";

system("mkdir $outfile");

system("cp /data/mta_www/mta_sib/Lev2/Plots/Plots_2011_02/*html $outfile/");

for($i = 0; $i < 10; $i++){
	$file1 = 'indep_plot_ccd'."$i".'.gif';
	$file2 = 'total_data_ccd'."$i".'.gif';
	system("cp /data/mta4/MTA/data/no_data.gif $file1");
	system("cp /data/mta4/MTA/data/no_data.gif $file2");
}
	
