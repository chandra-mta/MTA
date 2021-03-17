#!/usr/bin/perl

$start = $ARGV[0];
$stop  = $ARGV[1];
chomp $start;
chomp $stop;

$loginfile = '/data/mta/Script/Sol_panel/house_keeping/loginfile';

print "$start<---->$stop\n";

system('rm *fits');
system("dataseeker.pl infile=test outfile=dataseek_avg.fits search_crit='columns=pt_suncent_ang,sc_altitude timestart=$start timestop=$stop' loginFile=$loginfile ");
system("dataseeker.pl infile=test outfile=dataseek_deahk_temp.0.fits search_crit='columns=DEAHK16_avg       timestart=$start timestop=$stop'  loginFile=$loginfile");
system('chmod 777 *fits');
