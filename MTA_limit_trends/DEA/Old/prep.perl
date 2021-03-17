#!/usr/bin/perl

#########################################################################################
#	                                            										#
#	prep.perl: prepare data for short time data	                        				#
#	    author: Takashi Isobe (tisobe@cfa.harvard.edu)                                  #
#	    Mar 14, 2000:	first version				                                    #
#       Oct 01, 2015:   modified for dea dumpdata extract                               #
#       Last update:    Jan 11, 2021                                                    #
#											                                            #
#########################################################################################

#
#--- set a couple of directory paths
#
$script_dir = '/data/mta/Script/MTA_limit_trends/Scripts/DEA/';
$repository = "$script_dir".'RDB/';
$input_dir  = '/dsops/GOT/input/';
#
#--- set environmental setting
#
$ENV{"ACISTOOLSDIR"}=$script_dir;                   #---- using lib/acisEng.ttm
#
#--- make back up before procceed
#
#system("cp $repository/deahk_temp.rdb $repository/deahk_temp.rdb~");
#system("cp $repository/deahk_elec.rdb $repository/deahk_elec.rdb~");
#system("cp $repository/deahk_temp_hr.rdb $repository/deahk_temp_hr.rdb~");
#system("cp $repository/deahk_elec_hr.rdb $repository/deahk_elec_hr.rdb~");

#
#--- read today's dump list
#
$ifile = "$script_dir"."today_dump_files";
open(FH, $ifile);

while(<FH>) {
  chomp $_;
  $file = $_;
  #$file = "$input_dir"."$file".'.gz';
  #$file = "$input_dir"."$file";

  @atemp = split(/\//, $file);
  @btemp = split(/_/,  $atemp[-1]);
  $year  = $btemp[0];

#
#---- following is Peter Ford script to extract data from dump data
#
  `/bin/gzip -dc $file |$script_dir/getnrt -O  | $script_dir/deahk.pl`;

  `$script_dir/out2in.pl deahk_temp.tmp deahk_temp_in.tmp $year`;
  `$script_dir/out2in.pl deahk_elec.tmp deahk_elec_in.tmp $year`;
#
#--- 5 min resolution
#
  `$script_dir/average1.pl -i deahk_temp_in.tmp -o deahk_temp.rdb`;
  `cat deahk_temp.rdb >> $repository/deahk_temp_week$year.rdb`;

  `$script_dir/average1.pl -i deahk_elec_in.tmp -o deahk_elec.rdb`;
  `cat deahk_elec.rdb >> $repository/deahk_elec_week$year.rdb`;

    system('rm -rf deahk_temp.rdb deahk_elec.rdb');
#
#--- one hour resolution
#
  `$script_dir/average2.pl -i deahk_temp_in.tmp -o deahk_temp.rdb`;
  `cat  deahk_temp.rdb >> $repository/deahk_temp_short.rdb`;

  `$script_dir/average2.pl -i deahk_elec_in.tmp -o deahk_elec.rdb`;
  `cat deahk_elec.rdb >> $repository/deahk_elec_short.rdb`;

   system('rm -rf deahk_*.tmp deahk_*.rdb ');

#
#--- a day long collection does not work; each files is about 8 hrs long
#
#  `$script_dir/average3.pl -i deahk_temp_in.tmp -o deahk_temp.rdb`;
#  `cat  deahk_temp.rdb >> $repository/deahk_temp.rdb`;
#
#  `$script_dir/average3.pl -i deahk_elec_in.tmp -o deahk_elec.rdb`;
#  `cat deahk_elec.rdb >> $repository/deahk_elec.rdb`;
#
#   system('rm -rf deahk_*.tmp deahk_*.rdb ');

}
close(FH);
