#!/usr/bin/perl

#
#--- this will (re)run plot_sim_temp_data.py to create plots from 1999 to <yyyy> (you need to change)
#
#---  t. isobe (tisobe@cfa.harvard.edu)         Jan 18, 2016
#
for($year = 1999; $year < 2016; $year++){
    print "Year: $year\n";
    system("./plot_sim_temp_data.py $year");
}
print "Full range\n";
system("plot_sim_temp_data.py");
