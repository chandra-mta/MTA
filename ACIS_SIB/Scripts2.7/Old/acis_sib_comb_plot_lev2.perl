#!/usr/bin/env /usr/local/bin/perl
use PGPLOT;

#########################################################################################
#											#
#	acis_sib_comb_plot.perl: this script plots ccd5, 6, and 7 data 			#
#											#
#	Author: T. Isobe (tisobe@cfa.harvard.edu)					#
#	Last Update: Apr 23, 2013							#
#											#
#########################################################################################

#######################################
#
#---- setting directories
#
$bin_dir  = '/data/mta/MTA/bin/';
$bdata_dir = '/data/mta/MTA/data/';
$data_dir = '/data/mta/Script/ACIS/SIB/Lev2/Data/';
$web_dir  = '/data/mta/www/mta_sib/Lev2/';

$lookup   = '/home/ascds/DS.release/data/dmmerge_header_lookup.txt';	# dmmerge header rule lookup table

#######################################

#
#---- find today's data
#
($hsec, $hmin, $hhour, $hmday, $hmon, $hyear, $hwday, $hyday, $hisdst)= localtime(time);

$uyear  = $hyear + 1900;
$month  = $hmon  + 1;
$cmonth = $month;
if($month < 10){
	$cmonth = '0'."$month";
}

#
#---- find data directries 
#

$this_month = 'Data_'."$uyear".'_'."$cmonth";
$lmonth = $month -1;
$lyear  = $uyear;
if($lmonth < 1){
	$lmonth = 12;
	$lyear  = $uyear -1;
}
if($lmonth < 10){
	$lmonth = '0'."$lmonth";
}
$last_month = 'Data_'."$lyear".'_'."$lmonth";

$tmonth = $lmonth -1;
$tyear  = $lyear;
if($tmonth < 1){
	$tmonth = 12;
	$tyear  = $lyear -1;
}
if($tmonth < 10){
	$tmonth = '0'."$tmonth";
}
$two_month = 'Data_'."$tyear".'_'."$tmonth";

$smonth = $tmonth -1;
$syear  = $tyear;
if($smonth < 1){
	$smonth = 12;
	$syear  = $tyear -1;
}
if($smonth < 10){
	$smonth = '0'."$smonth";
}
$three_month = 'Data_'."$syear".'_'."$smonth";

system("mkdir ./Temp_data");

foreach $ent (5, 6, 7){ 
#
#--- if this month' data does not exist, use past three months' data
#
	$fits = 'lres_ccd'."$ent".'_merged.fits';
	$file1 = "$data_dir/$this_month/$fits";
	$check = `ls $file1`;
	$file2 = "$data_dir/$last_month/$fits";
	$file3 = "$data_dir/$two_month/$fits";
	$file4 = "$data_dir/$three_month/$fits";
#
#---- marge three data fits files
#
	if($check =~ /\w/){
		$line ="$file1,$file2,$file3";
		system("dmmerge infile=\"$line\" outfile=./Temp_data/out.fits outBlock=''  columnList='' lookupTab=\"$lookup\" clobber=yes");
	}else{
		$line ="$file2,$file3,$file4";
		system("dmmerge infile=\"$line\" outfile=./Temp_data/out.fits outBlock=''  columnList='' lookupTab=\"$lookup\" clobber=yes");
	}

	$ffile = './Temp_data/out.fits';

	$line = "$ffile".'[cols time]';
	system("dmlist infile=\"$line\" outfile=./Temp_data/zdump opt=data");

	@date = ();
	@rad1 = ();
	@rad2 = ();
	@rad3 = ();
	@rad4 = ();
	@rad5 = ();
	@rad6 = ();
	@all  = ();
	$cnt  = 0;
	$sub_date = 365 * ($uyear - 1998);
	if($uyear > 2000){
        	$sub_date++;
	}
	if($uyear > 2004){
        	$sub_date++;
	}
	if($uyear > 2008){
        	$sub_date++;
	}
	if($uyear > 2012){
        	$sub_date++;
	}
	
	open(IN, " ./Temp_data/zdump");
	OUTER:
	while(<IN>){
        	chomp $_;
        	@atemp = split(/\s+/, $_);
        	if($atemp[1] =~ /\d/ && $atemp[2] =~ /\d/){
               		$time = ($atemp[2] - 48815999)/86400;   #--- DOM date
#              		$time = $atemp[2]/86400 - $sub_date;    #--- year date
                	push(@date, $time);
                	$rad1[$cnt] = 0;
                	$rad2[$cnt] = 0;
                	$rad3[$cnt] = 0;
                	$rad4[$cnt] = 0;
                	$rad5[$cnt] = 0;
                	$rad6[$cnt] = 0;
                	$all[$cnt]  = 0;
                	$cnt++;
        	}
	}
	close(IN);

#
#---- use the next arrry and variable in liear fitting
#

	system("rm -rf ./Temp_data/zdump");

	foreach $ent (SSoft, Soft, Med, Hard, Harder, Hardest){
		@xdata    = @date;
		$data_cnt = $cnt;

		$line = "$ffile".'[cols '."$ent".']';
		system("dmlist infile=\"$line\" outfile=./Temp_data/zdump opt=data");

        	open(IN, './Temp_data/zdump');
        	$i = 0;
        	OUTER:
        	while(<IN>){
                	chomp $_;
                	@atemp = split(/\s+/, $_);
                	if($atemp[1] =~ /\d/ && $atemp[2] =~ /\d/){
                        	if($i == 0){
                                	$i++;
                                	next OUTER;
                        	}
                        	$diff = 86400 * ($date[$i] - $date[$i - 1]);
                        	if($diff == 0){
                                	$i++;
                                	next OUTER;
                        	}
                        	if($ent eq 'SSoft'){
                                	$rad1[$i] = $atemp[2]/$diff;
                        	}elsif($ent eq 'Soft'){
                                	$rad2[$i] = $atemp[2]/$diff;
                        	}elsif($ent eq 'Med'){
                                	$rad3[$i] = $atemp[2]/$diff;
                        	}elsif($ent eq 'Hard'){
                                	$rad4[$i] = $atemp[2]/$diff;
                        	}elsif($ent eq 'Harder'){
                                	$rad5[$i] = $atemp[2]/$diff;
                        	}elsif($ent eq 'Hardest'){
                        	$rad6[$i] = $atemp[2]/$diff;
                        	}
                        	$all[$i] += $atemp[2]/$diff;
                        	$i++;
                	}
        	}
        	close(IN);
        	system("rm -rf ./Temp_data/zdump");
	}
	$name  = 'all_ccd'."$ent";
	$tname = 'all_time'."$ent";
	$cname = 'cnt_ccd'."$ent";
	@{$name} = @all;
	@{$tname} = @date;
	${$cname} = $i;
}

plot_comb();
system('rm -rf Temp_data');


##########################################################################
### plot_comb: create this month's sib for ccds 5, 6, 7 on one plot    ###
##########################################################################

sub plot_comb{
	@temp  = sort{$a<=>$b} @all_time5;
	$xmin  = $temp[0];
	$tcnt  = $cnt_ccd5 - 1;
	$xmax  = $temp[$tcnt];

	@temp  = sort{$a<=>$b} @all_time6;
	$xmin2 = $temp[0];
	$tcnt  = $cnt_ccd6 - 1;
	$xmax2 = $temp[$tcnt];

	if($xmin > $xmin2){
		$xmin = $xmin2;
	}
	if($xmax < $xmax2){
		$xmax = $xmax2;
	}

	@temp  = sort{$a<=>$b} @all_time7;
	$xmin3 = $temp[0];
	$tcnt  = $cnt_ccd7 - 1;
	$xmax3 = $temp[$tcnt];

	if($xmin > $xmin3){
		$xmin = $xmin3;
	}
	if($xmax < $xmax3){
		$xmax = $xmax3;
	}

        $sum_all  = 0;
        $sum_all2 = 0;
        $cnt_all  = 0;

        foreach $ent (@all_ccd5){
                $sum_all  += $ent;
                $sum_all2 += $ent * $ent;
                $cnt_all++;
        }
        foreach $ent (@all_ccd6){
                $sum_all  += $ent;
                $sum_all2 += $ent * $ent;
                $cnt_all++;
        }
        foreach $ent (@all_ccd6){
                $sum_all  += $ent;
                $sum_all2 += $ent * $ent;
                $cnt_all++;
        }

        $avg = $sum_all/$cnt_all;
        $std = sqrt($sum_all2/$cnt_all - $avg * $avg);

        $ymin = 0;
        $add = 4.0 * $std;
        if($add < $avg){
                $add = $avg;
        }
        $ymax = $avg + $add;


	$xt1 = $xmin;
	$xt2 = $xmin + 0.4*($xmax - $xmin);
	$xt3 = $xmin + 0.8*($xmax - $xmin);
	$yt = $ymax + 0.05*($ymax - $ymin);

	pgbegin(0, '"./Temp_data/pgplot.ps"/cps',1,1);
	pgsubp(1,1);
	pgsch(2);
	pgslw(8);
	
	pgenv($xmin, $xmax, $ymin, $ymax, 0, 0);
	pgsci(2);
	for($k = 0 ; $k < $cnt_ccd5; $k++){
		pgpt(1, $all_time5[$k], $all_ccd5[$k], 1);
	}
	pgtext($xt1, $yt, "CCD5");
	pgsci(4);
	for($k = 0 ; $k < $cnt_ccd6; $k++){
		pgpt(1, $all_time6[$k], $all_ccd6[$k], 1);
	}
	pgtext($xt2, $yt, "CCD6");
	pgsci(5);
	for($k = 0 ; $k < $cnt_ccd7; $k++){
		pgpt(1, $all_time7[$k], $all_ccd7[$k], 1);
	}
	pgtext($xt3, $yt, "CCD7");
	pgsci(1);
	

	pglabel("Time (DOM)", "cnts/s","ACIS Rates");
	pgclos();
	system("echo ''|gs -sDEVICE=ppmraw  -r256x256 -q -NOPAUSE -sOutputFile=-  ./Temp_data/pgplot.ps|pnmflip -r270 | ppmtogif > $web_dir/Plots/comb_plot.gif");
	system("rm -rf ./Temp_data/pgplot.ps");
}
		
