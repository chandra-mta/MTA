#!/usr/bin/env /usr/local/bin/perl
use PGPLOT;

#########################################################################################
#											#
#	sib_corr_plot_lres.perl: this script plots existing data of a specified		#
#					period.						#
#											#
#	input example: 2004 11								#
#											#
#	Author: T. Isobe (tisobe@cfa.harvard.edu)					#
#	Last Update: Apr 22, 2013							#
#											#
#########################################################################################

$uyear      = $ARGV[0];
$month      = $ARGV[1];

if($uyear !~ /\d/ || $month !~ /\d/){
	print "\n     Usage: perl sib_corr_plt_lres_temp.perl <YYYY> <MM> \n\n";
	exit 1;
}

$temp_month = $month;
conv_no_ch_month();

#
#---- replace gif files with "no data" gif file so that if there are no data for a ccd
#---- the html page say "no data available"
#

for($iccd = 0; $iccd < 10; $iccd++){
	$name2 = 'total_data_ccd'."$iccd".'.gif';
	system("cp /data/mta4/MTA/data/no_data.gif ./Plots/$this_month/$name2");
	$name2 = 'indep_plot_ccd'."$iccd".'.gif';
	system("cp /data/mta4/MTA/data/no_data.gif ./Plots/$this_month/$name2");
	system("cp /data/mta4/MTA/data/no_data.gif ./Plots/$this_month/comb_plot.gif");
}


$test = `ls *`;
if($test =~ /Temp_data/){
}else{
	system("mkdir ./Temp_data");    #---- create a temporary working directory
}

#
#---- find a plotting range for date
#
	
$tyear  = $uyear;
$tmonth = $month;
$tday   = 0;
if($uyear == 1999){
       	$sub_date = -202;
}else{
       	$sub_date = 365 * ($uyear - 2000)+ 163;
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
       	if($uyear > 2016){
               	$sub_date++;
       	}
       	if($uyear > 2020){
               	$sub_date++;
       	}
}

conv_date_dom();
$plot_start = $dom - $sub_date;         # ok, this is a compliated way to get a year date
                                       	# but it is because of a  historical reason
$tyear = $uyear;
$tmonth = $month;
if($month == 1){$add_day = 31}
if($month == 2){
	$add_day = 28;
	$chk = 4 * int (0.25 * $uyear);
	if($uyear == $chk){
		$add_day = 29;
	}
}
if($month == 3){$add_day = 31}
if($month == 4){$add_day = 30}
if($month == 5){$add_day = 31}
if($month == 6){$add_day = 30}
if($month == 7){$add_day = 31}
if($month == 8){$add_day = 31}
if($month == 9){$add_day = 30}
if($month == 10){$add_day = 31}
if($month == 11){$add_day = 30}
if($month == 12){$add_day = 31}

$tday = $tday + $add_day;
conv_date_dom();
$plot_end = $dom - $sub_date;

$test = `ls *`;
if($test =~ /Plots/){
}else{
	system("mkdir Plots");
}

plot_sib();
plot_comb();

system("rm -rf ./Temp_data");

#####################################################################
### conv_date_format: change the time format to sec from 1998.1.1.###
#####################################################################

sub conv_date_format{
	
	$ydiff = $year - 1998;
	$acc_date = 365 * $ ydiff;
	if($year > 2000){
		$acc_date++;
	}
	if($year > 2004){
		$acc_date++;
	}
	if($year > 2008){
		$acc_date++;
	}
	if($year > 2012){
			$acc_date++;
	}
	
	if($month == 1){
		$start =   1;
		$end   =  31;
	}elsif($month == 2){
		$start =  32;
		$end   =  59;
	}elsif($month == 3){
		$start =  60;
		$end   =  90;
	}elsif($month == 4){
		$start =  91;
		$end   = 120;
	}elsif($month == 5){
		$start = 121;
		$end   = 151;
	}elsif($month == 6){
		$start = 152;
		$end   = 181;
	}elsif($month == 7){
		$start = 182;
		$end   = 212;
	}elsif($month == 8){
		$start = 213;
		$end   = 243;
	}elsif($month == 9){
		$start = 244;
		$end   = 273;
	}elsif($month == 10){
		$start = 274;
		$end   = 304;
	}elsif($month == 11){
		$start = 305;
		$end   = 334;
	}elsif($month == 12){
		$start = 335;
		$end   = 365;
	}
	if($year == 2000 || $year == 2004 || $year == 2008 || $year == 2012){
		if($month == 2){
			$end++;
		}elsif($month > 2){
			$start++;
			$end++;
		}
	}
	
	$start  += $acc_date;
	$start--;
	$start  *= 86400;

	$end    += $acc_date;
	$end    *= 86400;

	$t_begin = $start;
	$t_end   = $end;
}



#####################################################################
### conv_date_dom: change the time format to dom                  ###
#####################################################################

sub conv_date_dom{

	$ydiff = $tyear - 1999;
	$acc_date = 365 * $ ydiff;
	if($tyear > 2000){
		$acc_date++;
	}
	if($tyear > 2004){
		$acc_date++;
	}
	if($tyear > 2008){
		$acc_date++;
	}
	if($tyear > 2012){
		$acc_date++;
	}

	if($tmonth == 1){
		$dom =   1;
	}elsif($tmonth == 2){
		$dom =  32;
	}elsif($tmonth == 3){
		$dom =  60;
	}elsif($tmonth == 4){
		$dom =  91;
	}elsif($tmonth == 5){
		$dom = 121;
	}elsif($tmonth == 6){
		$dom = 152;
	}elsif($tmonth == 7){
		$dom = 182;
	}elsif($tmonth == 8){
		$dom = 213;
	}elsif($tmonth == 9){
		$dom = 244;
	}elsif($tmonth == 10){
		$dom = 274;
	}elsif($tmonth == 11){
		$dom = 305;
	}elsif($tmonth == 12){
		$dom = 335;
	}
	$chk = 4 * int(0.25 * $tyear);
	if($tyear == $chk){
		if($tmonth > 2){
			$dom++;
		}
	}

	$dom = $dom + $acc_date + $tday - 202;
}

#############################################################################
### plot_sib: plotting sub for SIB                                        ###
#############################################################################


sub plot_sib {
	$zlist = `ls ./Data/lres_*_merged.fits`;
	@data_list = ();
	@z_list = split(/\s+/, $zlist);

	POUTER:
	foreach $file (@z_list){

		@atemp    = split(/lres_ccd/, $file);
		@btemp    = split(/_/, $atemp[1]);
		$iccd     = $btemp[0];
		$ccd_name = 'ccd'."$iccd";
	
		system("dmlist \"$file\[cols time\]\" outfile=./Temp_data/zdump opt=data");
		open(IN, './Temp_data/zdump');
		
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

		OUTER:
		while(<IN>){
			chomp $_;
			@atemp = split(/\s+/, $_);
			if($atemp[1]  =~ /\d/ && $atemp[2] =~ /\d/){
#				$time = ($atemp[2] - 48815999)/86400;	#--- DOM date
				$time = $atemp[2]/86400 - $sub_date;	#--- year date
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
		if($cnt == 0){
			next POUTER;
		}
#
#---- use the next arrry and variable in liear fitting
#

		system("rm -rf ./Temp_data/zdump");
	
		foreach $ent (SSoft, Soft, Med, Hard, Harder, Hardest){
			@xdata    = @date;
			$data_cnt = $cnt;
			system("dmlist \"$file\[cols $ent\]\" outfile=./Temp_data/zdump opt=data");
			open(IN, './Temp_data/zdump');
			$i = 0;
			OUTER:
			while(<IN>){
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
		
		@rad = @all;
		@ydata = @all;
		if($iccd == 5){
			@all_ccd5 = @all;
			@all_time5 = @date;
			$cnt_ccd5 = $i;
		}elsif($iccd == 6){
			@all_ccd6 = @all;
			@all_time6 = @date;
			$cnt_ccd6 = $i;
		}elsif($iccd == 7){
			@all_ccd7 = @all;
			@all_time7 = @date;
			$cnt_ccd7 = $i;
		}
			
#
#--- finding a reasonable fitting range, then a fit a line using a robust fit
#
		find_avg_and_range();

		robust_fit();

		if($plot_start == 0){
			$xmin = $date[0];
		}else{
			$xmin = $plot_start;
		}
		$xmax = $plot_end;
#
#--- find plotting range (y axis)

#
		find_y_range();

#
#--- total data plot
#
		pgbegin(0, '"./Temp_data/pgplot.ps"/cps',1,1);
		pgsubp(1,1);
		pgsch(2);
		pgslw(4);
		$title       = 'Total';
		$color_index = 1;
		pgpap(0.0, 0.3);
		pgsch(2.0);

		plot_fig();

		pgclos;
		
		$name2 = 'total_data_'."$ccd_name".'.gif';

		system("echo ''|gs -sDEVICE=ppmraw  -r256x256 -q -NOPAUSE -sOutputFile=-  ./Temp_data/pgplot.ps| pnmflip -r270 |ppmtogif > Plots/$name2");
		system("rm -rf ./Temp_data/pgplot.ps");

#
#--- indivisual data range plots
#
		pgbegin(0, '"./Temp_data/pgplot.ps"/cps',1,1);
		pgsubp(2,3);
		pgsch(2);
		pgslw(4);
		
		@rad   = @rad1;
		@ydata = @rad;
		find_avg_and_range();
		robust_fit();
		$xmin = $plot_start;
		$xmax = $plot_end;
		find_y_range();
		$title       = 'Super Soft Photons';
		$color_index = 2;
		plot_fig();

		@rad   = @rad2;
		@ydata = @rad;
		find_avg_and_range();
		robust_fit();
		$xmin = $plot_start;
		$xmax = $plot_end;
		find_y_range();
		$title       = 'Soft Photons';
		$color_index = 4;
		plot_fig();

		@rad   = @rad3;
		@ydata = @rad;
		find_avg_and_range();
		robust_fit();
		$xmin = $plot_start;
		$xmax = $plot_end;
		find_y_range();
		$title       = 'Moderate Energy Photons';
		$color_index = 6;
		plot_fig();

		@rad   = @rad4;
		@ydata = @rad;
		find_avg_and_range();
		robust_fit();
		$xmin = $plot_start;
		$xmax = $plot_end;
		find_y_range();
		$title       = 'Hard Photons';
		$color_index = 8;
		plot_fig();

		@rad   = @rad5;
		@ydata = @rad;
		find_avg_and_range();
		robust_fit();
		$xmin = $plot_start;
		$xmax = $plot_end;
		find_y_range();
		$title       = 'Very Hard  Photons';
		$color_index = 10;
		plot_fig();

		@rad   = @rad6;
		@ydata = @rad;
		find_avg_and_range();
#		robust_fit();
		double_fit();
		$xmin = $plot_start;
		$xmax = $plot_end;
		find_y_range();
		$title       = 'Beyond 10 KeV';
		$color_index = 12;
		plot_fig();

		pgclos();
			
		$name2 = 'indep_plot_'."$ccd_name".'.gif';

		system("echo ''|gs -sDEVICE=ppmraw  -r256x256 -q -NOPAUSE -sOutputFile=-  ./Temp_data/pgplot.ps| pnmflip -r270 |ppmtogif >./Plots/$name2");
		system("rm -rf ./Temp_data/pgplot.ps");

	}
	close(FH);
}

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


	@temp  = sort{$a<=>$b} @all_ccd5;
	$ymin  = $temp[0];
	$tcnt  = $cnt_ccd5 - 1;
	$ymax  = $temp[$tcnt];

	@temp  = sort{$a<=>$b} @all_ccd6;
	$ymin2 = $temp[0];
	$tcnt  = $cnt_ccd6 - 1;
	$ymax2 = $temp[$tcnt];

	if($ymin > $ymin2){
		$ymin = $ymin2;
	}
	if($ymax < $ymax2){
		$ymax = $ymax2;
	}

	@temp  = sort{$a<=>$b} @all_ccd7;
	$ymin3 = $temp[0];
	$tcnt  = $cnt_ccd7 - 1;
	$ymax3 = $temp[$tcnt];

	if($ymin > $ymin3){
		$ymin = $ymin3;
	}
	if($ymax < $ymax3){
		$ymax = $ymax3;
	}

	$xt1 = $xmin;
	$xt2 = $xmin + 0.4*($xmax - $xmin);
	$xt3 = $xmin + 0.8*($xmax - $xmin);
	$yt  = $ymax + 0.05*($ymax - $ymin);

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
		

	pglabel("Time (DOY)", "cnts/s","ACIS Rates for This Month");
	pgclos();

	system("echo ''|gs -sDEVICE=ppmraw  -r256x256 -q -NOPAUSE -sOutputFile=-  ./Temp_data/pgplot.ps| pnmflip -r270 | ppmtogif > /data/mta/www/mta_sib/Plots/$this_month/comb_plot.gif");
	system("rm -rf ./Temp_data/pgplot.ps");
}

##########################################################################
### find_avg_and_range: find avg, min, max and define plotting range   ###
##########################################################################

sub find_avg_and_range {
	$sum  = 0;
	$sum2 = 0;
	for($i = 0; $i < $cnt; $i++){
		$sum  += $rad[$i];
		$sum2 += $rad[$i]*$rad[$i];
	}
	if($cnt == 0){
		$avg   = 0.0;
		$sigma = 0.0;
		$ymin  = 0.0;
		$ymax  = 0.0;
	}else{
		$avg   = $sum/$cnt;
		$sigma = sqrt($sum2/$cnt - $avg * $avg);
		@at    = split(//, $avg);
		$avg   = "$at[0]$at[1]$at[2]$at[3]$at[4]";
		@at    = split(//, $sigma);
		$sigma = "$at[0]$at[1]$at[2]$at[3]$at[4]";
	
		@atemp = sort{$a<=>$b} @date;
		$xmin  = $atemp[0];
		$xmax  = $atemp[$cnt - 1];
	
		@atemp = sort{$a<=>$b} @rad;
		$ymin  = 0;
		$ymax  = $atemp[$cnt - 1];
		$ymax *= 1.2;
	}
}


##########################################################################
#### plot_fig: plotting sub                                            ###
##########################################################################

sub plot_fig{
	pgenv($xmin, $xmax, $ymin, $ymax, 0, 0);

	pgsci($color_index);
	for($k = 0; $k < $cnt; $k++){
		pgpt(1,$date[$k], $rad[$k], 1);
	}
	pgsci(1);

	$ypos1 = $int + $slope * $xmin;
	$ypos2 = $int + $slope * $xmax;
	pgmove($xmin, $ypos1);
	pgdraw($xmax, $ypos2);
	
	$xt = 0.05* ($xmax - $xmin) + $xmin;
	$yt = $ymax - 0.1 * ($ymax - $ymin);
	$disp_slope = sprintf "%3.4f", $slope;
	$line = "slope: $disp_slope";
	pgtext($xt, $yt, $line);
#
#---- E > 12 keV has two lines
#
	if($color_index == 12 && $slope2 =~ /\d/){
		$ypos1 = $int2 + $slope2 * $xmin;
		$ypos2 = $int2 + $slope2 * $xmax;
		pgmove($xmin, $ypos1);
		pgdraw($xmax, $ypos2);
		$yt = $yt - 0.1 * abs ($ymax - $ymin);
		$disp_slope = sprintf "%3.4f", $slope2;
		$line = "slope: $disp_slope";
		pgtext($xt, $yt, $line);
	}
	
	pglabel("time (DOY)","cnts/s", "$title");
}


###################################################################
### conv_no_ch_month: change month format to e.g. 1 to Jan      ###
###################################################################

sub conv_no_ch_month{

	if($temp_month == 1){
		$cmonth = "Jan";
	}elsif($temp_month == 2){
		$cmonth = "Feb";
	}elsif($temp_month == 3){
		$cmonth = "Mar";
	}elsif($temp_month == 4){
		$cmonth = "Apr";
	}elsif($temp_month == 5){
		$cmonth = "May";
	}elsif($temp_month == 6){
		$cmonth = "Jun";
	}elsif($temp_month == 7){
		$cmonth = "Jul";
	}elsif($temp_month == 8){
		$cmonth = "Aug";
	}elsif($temp_month == 9){
		$cmonth = "Sep";
	}elsif($temp_month == 10){
		$cmonth = "Oct";
	}elsif($temp_month == 11){
		$cmonth = "Nov";
	}elsif($temp_month == 12){
		$cmonth = "Dec";
	}
}
		

####################################################################
### find_y_range: find appropriate plotting range for y axis     ###
####################################################################

sub find_y_range{
        $tsum  = 0;
        $tsum2 = 0;
        $tcnt  = 0;
        foreach $ent (@rad){
                $tsum  += $ent;
                $tsum2 += $ent * $ent;
                $tcnt++;
        }
        if($tcnt == 0){
                $ymin  = 0;
                $ymax  = 1;
        }else{
                $tavg  = $tsum/$tcnt;
                $tsig  = sqrt($tsum2/$tcnt - $tavg*$tavg);
        
                $ymin  = $tavg - 4.0 * $tsig;
                $ymin *= 10;
                $ymin  = int $ymin;
                $ymin /= 10;
                if($ymin < 0){
                        $ymin = 0;
                }
                $ymax  = $tavg + 4.0 * $tsig;
		if($ymax > 0.5){
                	$ymax *= 10;
                	$ymax  = int $ymax;
                	$ymax /= 10;
#		}elsif($ymax <0.1){
                	$ymax *= 100;
                	$ymax  = int $ymax;
                	$ymax /= 100;
#		}else{
#			$ymax = 0.5;
		}
        
                if($ymax <= $ymin){
                        $ymax = $ymin + 1;
                }
        }
}


####################################################################
### double_fit: limit fitting range from the first liear fit     ###
####################################################################

sub double_fit{

	$top = 0;
	$mid = 0;
	$bot = 0;
	@temp = sort{$a<=>$b} @rad;
	$diff = $temp[$cnt-4] - $temp[4];
	$med  = 0.5* $diff + $temp[4];
	$step = $diff/6.0;
	$bound1 = $med - $step;
	$bound2 = $med + $step;

	foreach $ent (@rad){
		if($ent < $bound1){
			$bot++;
		}elsif($ent > $bound2){
			$top++;
		}else{
			$mid++;
		}
	}


	if($mid < $top || $mid < $bot){
#
#---- fit the first round of linear line
#
		@xtemp = @date;
		@ytemp = @rad;
		$tot   = $cnt;
		least_fit();

#
#----  devide data into two regions; below and above the linear fitting line
#
		@x_save1 = ();
		@y_save1 = ();
		$d_cnt1  = 0;
		@x_save2 = ();
		@y_save2 = ();
		$d_cnt2  = 0;
		@x_save2 = ();
		for($k = 0; $k < $cnt ; $k++){
#			$diff = $rad[$k] - ($int + $slope * $date[$k]);
			$diff = $rad[$k] -  $avg;
			if($diff < 0){
				push(@x_save1, $date[$k]);
				push(@y_save1, $rad[$k]);
				$d_cnt1++;
			}else{
				push(@x_save2, $date[$k]);
				push(@y_save2, $rad[$k]);
				$d_cnt2++;
			}
		}
	
		@xdata = @x_save1;
		@ydata = @y_save1;
		$data_cnt = $d_cnt1;
		robust_fit();
		$int2        = $int;
		$slope2      = $slope;
		$sigm_slope2 = $sigm_slope;
	
		@xdata = @x_save2;
		@ydata = @y_save2;
		$data_cnt = $d_cnt2;
		robust_fit();
	}else{
		robust_fit();
	}
}


####################################################################
### least_fit: least sq. fit routine                             ###
####################################################################

sub least_fit{
        $lsum = 0;
        $lsumx = 0;
        $lsumy = 0;
        $lsumxy = 0;
        $lsumx2 = 0;
        $lsumy2 = 0;

        for($fit_i = 0; $fit_i < $tot;$fit_i++) {
                $lsum++;
                $lsumx += $xtemp[$fit_i];
                $lsumy += $ytemp[$fit_i];
                $lsumx2+= $xtemp[$fit_i]*$xtemp[$fit_i];
                $lsumy2+= $ytemp[$fit_i]*$ytemp[$fit_i];
                $lsumxy+= $xtemp[$fit_i]*$ytemp[$fit_i];
        }

        $delta = $lsum*$lsumx2 - $lsumx*$lsumx;
        if($delta > 0){
                $int   = ($lsumx2*$lsumy - $lsumx*$lsumxy)/$delta;
                $slope = ($lsumxy*$lsum - $lsumx*$lsumy)/$delta;
                $slope = sprintf "%2.4f",$slope;
        }else{
                $int = 999999;
                $slope = 0.0;
        }
	$tot1 = $tot - 1;
	if($delta > 0 && $tot1 > 0){
		$variance = ($lsumy2 + $int*$int*$lsum + $slope*$slope*$lsumx2
		-2.0 *($int*$lsumy + $slope*$lsumxy - $int*$slope*$lsumx))/$tot1;
		$sigm_slope = sqrt($variance*$lsum/$delta);
		$sigm_slope = sprintf "%2.4f",$sigm_slope;
	}else{
		$sigm_slope = 0.0;
	}
}


####################################################################
### robust_fit: linear fit for data with medfit robust fit metho  ##
####################################################################

sub robust_fit{
	$sumx = 0;
	$symy = 0;
	for($n = 0; $n < $data_cnt; $n++){
		$sumx += $xdata[$n];
		$symy += $ydata[$n];
	}
	$xavg = $sumx/$data_cnt;
	$yavg = $sumy/$data_cnt;
#
#--- robust fit works better if the intercept is close to the
#--- middle of the data cluster.
#
	@xbin = ();
	@ybin = ();
	for($n = 0; $n < $data_cnt; $n++){
		$xbin[$n] = $xdata[$n] - $xavg;
		$ybin[$n] = $ydata[$n] - $yavg;
	}

	$total = $data_cnt;
	medfit();

	$alpha += $beta * (-1.0 * $xavg) + $yavg;
	
	$int   = $alpha;
	$slope = $beta;
}


####################################################################
### medfit: robust filt routine                                  ###
####################################################################

sub medfit{

#########################################################################
#									#
#	fit a straight line according to robust fit			#
#	Numerical Recipes (FORTRAN version) p.544			#
#									#
#	Input:		@xbin	independent variable			#
#			@ybin	dependent variable			#
#			total	# of data points			#
#									#
#	Output:		alpha:	intercept				#
#			beta:	slope					#
#									#
#	sub:		rofunc evaluate SUM( x * sgn(y- a - b * x)	#
#			sign   FORTRAN/C sign function			#
#									#
#########################################################################

	my $sx  = 0;
	my $sy  = 0;
	my $sxy = 0;
	my $sxx = 0;

	my (@xt, @yt, $del,$bb, $chisq, $b1, $b2, $f1, $f2, $sigb);
#
#---- first compute least sq solution
#
	for($j = 0; $j < $total; $j++){
		$xt[$j] = $xbin[$j];
		$yt[$j] = $ybin[$j];
		$sx  += $xbin[$j];
		$sy  += $ybin[$j];
		$sxy += $xbin[$j] * $ybin[$j];
		$sxx += $xbin[$j] * $xbin[$j];
	}

	$del = $total * $sxx - $sx * $sx;
#
#----- least sq. solutions
#
	$aa = ($sxx * $sy - $sx * $sxy)/$del;
	$bb = ($total * $sxy - $sx * $sy)/$del;
	$asave = $aa;
	$bsave = $bb;

	$chisq = 0.0;
	for($j = 0; $j < $total; $j++){
		$diff   = $ybin[$j] - ($aa + $bb * $xbin[$j]);
		$chisq += $diff * $diff;
	}
	$sigb = sqrt($chisq/$del);
	$b1   = $bb;
	$f1   = rofunc($b1);
	$b2   = $bb + sign(3.0 * $sigb, $f1);
	$f2   = rofunc($b2);

	$iter = 0;
	OUTER:
	while($f1 * $f2 > 0.0){
		$bb = 2.0 * $b2 - $b1;
		$b1 = $b2; 
		$f1 = $f2;
		$b2 = $bb;
		$f2 = rofunc($b2);
		$iter++;
		if($iter > 100){
			last OUTER;
		}
	}

	$sigb *= 0.01;
	$iter = 0;
	OUTER1:
	while(abs($b2 - $b1) > $sigb){
		$bb = 0.5 * ($b1 + $b2);
		if($bb == $b1 || $bb == $b2){
			last OUTER1;
		}
		$f = rofunc($bb);
		if($f * $f1 >= 0.0){
			$f1 = $f;
			$b1 = $bb;
		}else{	
			$f2 = $f;
			$b2 = $bb;
		}
		$iter++;
		if($iter > 100){
			last OTUER1;
		}
	}
	$alpha = $aa;
	$beta  = $bb;
	if($iter >= 100){
		$alpha = $asave;
		$beta  = $bsave;
	}
	$abdev = $abdev/$total;
}

##########################################################
### rofunc: evaluatate 0 = SUM[ x *sign(y - a bx)]     ###
##########################################################

sub rofunc{
	my ($b_in, @arr, $n1, $nml, $nmh, $sum);

	($b_in) = @_;
	$n1  = $total + 1;
	$nml = 0.5 * $n1;
	$nmh = $n1 - $nml;
	@arr = ();
	for($j = 0; $j < $total; $j++){
		$arr[$j] = $ybin[$j] - $b_in * $xbin[$j];
	}
	@arr = sort{$a<=>$b} @arr;
	$aa = 0.5 * ($arr[$nml] + $arr[$nmh]);
	$sum = 0.0;
	$abdev = 0.0;
	for($j = 0; $j < $total; $j++){
		$d = $ybin[$j] - ($b_in * $xbin[$j] + $aa);
		$abdev += abs($d);
		$sum += $xbin[$j] * sign(1.0, $d);
	}
	return($sum);
}


##########################################################
### sign: sign function                                ###
##########################################################

sub sign{
        my ($e1, $e2, $sign);
        ($e1, $e2) = @_;
        if($e2 >= 0){
                $sign = 1;
        }else{
                $sign = -1;
        }
        return $sign * $e1;
}
