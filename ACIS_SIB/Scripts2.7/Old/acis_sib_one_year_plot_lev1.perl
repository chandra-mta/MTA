#!/usr/bin/env /usr/local/bin/perl
use PGPLOT;

#########################################################################################
#											#
#	acis_sib_one_year_plot.perl: this script plots the past one year sib data fro 	#
#				     each CCD.						#
#											#
#	author: t. isobe (tiosbe@cfa.harvard.edu)					#
#											#
#	last update: Arp 22, 2013							#
#											#
#########################################################################################


#######################################
#
#---- setting directories
#
$bin_dir  = '/data/mta/MTA/bin/';
$bdata_dir= '/data/mta/MTA/data/';
$web_dir  = '/data/mta/www/mta_sib/';
$data_dir = '/data/mta/Script/ACIS/SIB/Data/';

#######################################

#
### get today's date
#
($usec, $umin, $uhour, $umday, $umon, $uyear, $uwday, $uyday, $uisdst)= localtime(time);
if($uyear < 1900) {
        $uyear = 1900 + $uyear;
}
$month = $umon + 1;

$temp_month = $month;

$amonth = $month;
if($amonth < 10){
        $amonth = '0'."$amonth";
}

$l_year = $uyear - 1;

if($month == 12){
	$l_month = 1;
	$l_year = $uyear;
}else{
	$l_month = $month + 1;
}

#
#---- make a list of year:month for the past 12 months (including this month)
#

$tyear = $l_year;
for($i = 0; $i < 12; $i++){
	$tmonth = $l_month + $i;
	if($tmonth < 10){
		$amonth = '0'."$tmonth";
	}elsif($tmonth > 12){
		$amonth = $tmonth - 12;
		if($amonth < 10){
			$amonth = '0'."$amonth";
		}
		$tyear = $uyear;
	}else{
		$amonth = $tmonth;
	}
	$d_name = 'Data_'."$tyear".'_'."$amonth";
	push(@d_list, $d_name);
}

#
#---- create a temporary computation directry
#

system("mkdir ./Temp_data");

$alist = `ls -d *`;             #---- clean up param dir
@dlist = split(/\s+/, $alist);
OUTER:
foreach $dir (@dlist){
        if($dir =~ /param/){
                system("rm -rf ./param/*");
                last OUTER;
        }
}

system("mkdir  ./param");


#
#---- go though each ccd
#
for($ccd = 0; $ccd < 10; $ccd++){
	@data_list = ();
	foreach $d_name (@d_list){
		$name = "$data_dir".'/'."$d_name".'/lres_ccd'."$ccd".'_merged.fits*';
		$line = `ls $name`;
		chomp $line;			#---- checking the file actually exits or not.
		if($line ne ''){
			push(@data_list, $line);
		}
	}

	@time    = ();
	@ssoft   = ();
	@soft    = ();
	@med     = ();
	@hard    = ();
	@harder  = ();
	@hardest = ();
	@all     = ();
	$i = 0;
	foreach $data (@data_list){
		$fdata = "$data"."+1";
#
#----- first just read time entry
#
		$line = "$fdata".'[cols time]';
		system("dmlist infile=\"$line\" outfile=./Temp_data/zzout opt=data");

		open(IN, "./Temp_data/zzout");
		$k = 0;
		OUTER:
		while(<IN>){
			chomp $_;
			@atemp = split(/\s+/, $_);
			if($atemp[1] =~ /\d/  && $atemp[2] =~ /\d/){
				$dom = ($atemp[2] - 48815999)/86400;
				push(@time_sec, $dom);
				OUTER:
				for($year = 1999; $year < 2015; $year++){		
					if($year == 1999){
						$acc_date = 163;
					}else{
						$acc_date = 365 * ($year - 1999)+ 163;
						if($acc_date > 2000){
							$acc_date++;
						}
						if($acc_date > 2004){
							$acc_date++;
						}
						if($acc_date > 2008){
							$acc_date++;
						}
						if($acc_date > 2012){
							$acc_date++;
						}
					}
#
#---- time unit is year. a fraction part is not quite accurate (ignoring a leap year), but
#-----it is good enough for plottings.
#
					$diff = ($dom - $acc_date)/365;
					if($diff < 1.0 && $diff > 0.0){
						@dtemp = split(/\./, $diff);
						$year1 = $year + 1;
						$date = "$year1".'.'."$dtemp[1]";
						last OUTER;
					}
				}
					
				push(@time, $date);
				$k++;
			}
		}
		close(IN);
		system("rm -rf ./Temp_data/zzout");
#
#----- read each element separately
#
		foreach $ent ('ssoft', 'soft', 'med', 'hard', 'harder', 'hardest'){

			$line = "$fdata".'[cols '."$ent".']';
			system("dmlist infile=\"$line\" outfile=./Temp_data/zzout opt=data");

			open(IN, "./Temp_data/zzout");
			$j = $i;
			OUTER:
			while(<IN>){
				chomp $_;
				@atemp = split(/\s+/, $_);
				if($atemp[1] =~ /\d/  && $atemp[2] =~ /\d/){
					$diff = 86400 * ($time_sec[$j] - $time_sec[$j - 1]);
					if($diff == 0){
						next OUTER;
					}
#
#---- normalizing for per sec
#
					$rad = $atemp[2]/$diff;
					push(@{$ent},$rad);
					$j++;
				}
			}
			close(IN);
			system("rm -rf ./Temp_data/zzout");
		}
		$i += $k;
	}	

#
#---- full energy range counts are stored in @all
#
	$cnt = 0;
	foreach $ent (@time){
		$sum = $ssoft[$cnt] + $soft[$cnt] + $med[$cnt] + $hard[$cnt] + $harder[$cnt] + $hardest[$cnt];
		push(@all,$sum);
		$cnt++;
	}

	@xdata    = @time;
	$data_cnt = $cnt;
	@rad = @all;
	@ydata = @rad;
	find_avg_and_range();		#--- find an average and  plotting range for y axis
	robust_fit();

	$xmin = $time[0];
	$xmax = $time[$cnt -1];
	$diff = $xmax - $xmin;
	$xmin -= 0.05 * $diff;
	$xmax += 0.55 * $diff;

	find_y_range();

	pgbegin(0, '"./Temp_data/pgplot.ps"/cps',1,1);
	pgsubp(1,1);
	pgsch(2);
	pgslw(4);
	$title = 'Total';
	$color_index = 1;
	pgpap(0.0, 0.3);
	pgsch(2.0);
	plot_fig();
	pgclos;

	$name2 = 'long_total_data_ccd'."$ccd".'.gif';

system("echo ''|gs -sDEVICE=ppmraw  -r256x256 -q -NOPAUSE -sOutputFile=-  ./Temp_data/pgplot.ps|pnmflip -r270 |ppmtogif > $web_dir/Plots/Plot_past_year/$name2");
	system("rm -rf ./Temp_data/pgplot.ps");


	pgbegin(0, '"./Temp_data/pgplot.ps"/cps',1,1);
	pgsubp(2,3);
	pgsch(2);
	pgslw(4);

	@rad = @ssoft;
	@ydata = @rad;
	find_avg_and_range();
	robust_fit();

	$xmin = $time[0];
	$xmax = $time[$cnt -1];
	$diff = $xmax - $xmin;
	$xmin -= 0.05 * $diff;
	$xmax += 0.55 * $diff;

	find_y_range();

	$title = 'Super Soft Photons';
	$color_index = 2;
	plot_fig();

	@rad = @soft;
	@ydata = @rad;
	find_avg_and_range();
	robust_fit();

	$xmin = $time[0];
	$xmax = $time[$cnt -1];
	$diff = $xmax - $xmin;
	$xmin -= 0.05 * $diff;
	$xmax += 0.55 * $diff;

	find_y_range();
	$title = 'Soft Photons';
	$color_index = 4;
	plot_fig();

	@rad = @med;
	@ydata = @rad;
	find_avg_and_range();
	robust_fit();

	$xmin = $time[0];
	$xmax = $time[$cnt -1];
	$diff = $xmax - $xmin;
	$xmin -= 0.05 * $diff;
	$xmax += 0.55 * $diff;

	find_y_range();
	$title = 'Moderate Energy Photons';
	$color_index = 6;
	plot_fig();

	@rad = @hard;
	@ydata = @rad;
	find_avg_and_range();
	robust_fit();

	$xmin = $time[0];
	$xmax = $time[$cnt -1];
	$diff = $xmax - $xmin;
	$xmin -= 0.05 * $diff;
	$xmax += 0.55 * $diff;

	find_y_range();
	$title = 'Hard Photons';
	$color_index = 8;
	plot_fig();

	@rad = @harder;
	@ydata = @rad;
	find_avg_and_range();
	robust_fit();

	$xmin = $time[0];
	$xmax = $time[$cnt -1];
	$diff = $xmax - $xmin;
	$xmin -= 0.05 * $diff;
	$xmax += 0.55 * $diff;

	find_y_range();
	$title = 'Very Hard  Photons';
	$color_index = 10;
	plot_fig();

	@rad = @hardest;
	@ydata = @rad;
	find_avg_and_range();
#	robust_fit();

	$xmin = $time[0];
	$xmax = $time[$cnt -1];
	$diff = $xmax - $xmin;
	$xmin -= 0.05 * $diff;
	$xmax += 0.55 * $diff;

	if($tot > 0){
		double_fit();
		find_y_range();
	}
	$title = 'Beyond 10 KeV';
	$color_index = 12;
	plot_fig();

	pgclos();

	$name2 = 'long_indep_plot_ccd'."$ccd".'.gif';

system("echo ''|gs -sDEVICE=ppmraw  -r256x256 -q -NOPAUSE -sOutputFile=-  ./Temp_data/pgplot.ps|pnmflip -r270 |ppmtogif > $web_dir/Plots/Plot_past_year/$name2");
	system("rm -rf ./Temp_data/pgplot.ps");
}

system("rm -rf ./Temp_data");

##########################################################################
#### plot_fig: plotting sub                                            ###
##########################################################################

sub plot_fig{
        pgenv($xmin, $xmax, $ymin, $ymax, 0, 0);
        pgsci($color_index);
        for($k = 0; $k < $cnt; $k++){
                pgpt(1,$time[$k], $rad[$k], 1);
        }
        pgsci(1);

        $xt = 0.05* ($xmax - $xmin) + $xmin;
        $yt = $ymax - 0.1 * ($ymax - $ymin);
        $ypos1 = $int + $slope * $xmin;
        $ypos2 = $int + $slope * $xmax;
        pgmove($xmin, $ypos1);
        pgdraw($xmax, $ypos2);
	$line = "slope: $slope";
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
#                $line = "slope: $slope2 +/- $sigm_slope2";
                $line = "slope: $slope2";
                pgtext($xt, $yt, $line);
        }
        pglabel("time (Year)","cnts/s", "$title");
}


##########################################################################
### find_avg_and_range: find avg, min, max and define plotting range  ###
##########################################################################

sub find_avg_and_range {
        $sum  = 0;
        $sum2 = 0;
        for($i = 0; $i < $cnt; $i++){
                $sum += $rad[$i];
                $sum2 += $rad[$i]*$rad[$i];
        }
        if($cnt == 0){
                $avg = 0.0;
                $sigma = 0.0;
                $ymin = 0.0;
                $ymax = 0.0;
        }else{
                $avg = $sum/$cnt;
                $sigma = sqrt($sum2/$cnt - $avg*$avg);
                @at = split(//,$avg);
                $avg = "$at[0]$at[1]$at[2]$at[3]$at[4]";
                @at = split(//,$sigma);
                $sigma = "$at[0]$at[1]$at[2]$at[3]$at[4]";

                @atemp = sort{$a<=>$b} @time;
                $xmin = $atemp[0];
                $xmax = $atemp[$cnt - 1];
		$diff = $xmax - $xmin;
		$xmax += 0.55 * $diff;

                @atemp = sort{$a<=>$b} @rad;
                $ymin = 0;
		$ymin = $avg - 3.0 * $sigma;
		$ymin *= 10;
		$ymin = int $ymin;
		$ymin /= 10;
		if($ymin < 0){
			$ymin = 0;
		}
		$ymax = $avg + 3.0 * $sigma;
		$ymax *= 10;
		$ymax = int $ymax;
		$ymax /= 10;

		if($ymax <= $ymin){
			$ymax = $ymin + 1;
		}
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
                $ymin = 0;
                $ymax = 1;
        }else{
                $tavg = $tsum/$tcnt;
                $tsig = sqrt($tsum2/$tcnt - $tavg*$tavg);

                $ymin = $tavg - 4.0 * $tsig;
                $ymin *= 10;
                $ymin = int $ymin;
                $ymin /= 10;
                if($ymin < 0){
                        $ymin = 0;
                }
                $ymax = $tavg + 4.0 * $tsig;
                $ymax *= 10;
                $ymax = int $ymax;
                $ymax /= 10;

                if($ymax <= $ymin){
                        $ymax = $ymin + 1;
                }
        }
}

####################################################################
### robust_fit: linear fit for data with medfit robust fit metho  ##
####################################################################

sub robust_fit{

        @temp = sort{$a<=>$b} @xdata;
        $xtmin = $temp[0];

        $n_cnt = 0;
        @xtrim = ();
        @ytrim = ();
#
#--- robust fit works better if the intercept is close to the
#--- middle of the data cluster. In this case, we just need to
#--- worry about time direction.
#
        for($m = 0; $m < $data_cnt; $m++){
                $xt = $xdata[$m] - $xtmin - 0.5;
                push(@xtrim, $xt);
                push(@ytrim, $ydata[$m]);
                $n_cnt++;
        }
	if($n_cnt > 0){
        	@xbin = @xtrim;
        	@ybin = @ytrim;
        	$total = $n_cnt;
        	medfit();
	
        	$alpha +=  $beta * (-1.0 *  ($xmin + 0.5));
        	$int   = sprintf "%2.4f",$alpha;
        	$slope = sprintf "%2.4f",$beta;
	}else{
		$alpha = 0;
		$int   = 0;
		$slope = 0;
	}
}

####################################################################
### robust_fit: linear fit for data within 3 sigma deviation ##
####################################################################

sub robust_fit_old{

#
#---- fit the first round of linear line
#
        @xtemp = @xdata;
        @ytemp = @ydata;
        $tot   = $data_cnt;
        least_fit();
#
#---- find a sigma from the fitting line
#
        $sum  = 0;
        $sum2 = 0;
        for($k = 0; $k < $data_cnt ; $k++){
                $diff = $ydata[$k] - ($int + $slope * $xdata[$k]);
                $sum  += $diff;
                $sum2 += $diff * $diff;
        }
#
#---- find 3 sigma deviation
#
        $avg = $sum / $data_cnt;
        $sig = sqrt ($sum2/$data_cnt - $avg * $avg);
        $sig3 = 3.0 * $sig;
#
#---- collect data points in the 3 sigma range (in dependent variable)
#

        @x_trim = ();
        @y_trim = ();
        $cnt_trim = 0;;
        for($k = 0; $k < $data_cnt ; $k++){
                $diff = abs($ydata[$k] - ($int + $slope * $xdata[$k]));
                if($diff < $sig3){
                        push(@x_trim, $xdata[$k]);
                        push(@y_trim, $ydata[$k]);
                        $cnt_trim++;
                }
        }
#
#----- compute new linear fit for the selected data points
#

        @xtemp = @x_trim;
        @ytemp = @y_trim;
        $tot   = $cnt_trim;
        least_fit();

#
#---- repeat one more time to tight up the fit
#
        $sum  = 0;
        $sum2 = 0;
        for($k = 0; $k < $data_cnt ; $k++){
                $diff = $ydata[$k] - ($int + $slope * $xdata[$k]);
                $sum  += $diff;
                $sum2 += $diff * $diff;
        }

        $avg = $sum / $data_cnt;
        $sig = sqrt ($sum2/$data_cnt - $avg * $avg);
        $sig3 = 3.0 * $sig;
        @x_trim = ();
        @y_trim = ();
        $cnt_trim = 0;
        for($k = 0; $k < $data_cnt ; $k++){
                $diff = abs($ydata[$k] - ($int + $slope * $xdata[$k]));
                if($diff < $sig3){
                        push(@x_trim, $xdata[$k]);
                        push(@y_trim, $ydata[$k]);
                        $cnt_trim++;
                }
        }

        @xtemp = @x_trim;
        @ytemp = @y_trim;
        $tot   = $cnt_trim;
        least_fit();
        @xbin = @xtemp;
        @ybin = @ytemp;
        $total = $tot;
        medfit();
        $int   = sprintf "%2.4f",$alpha;
        $slope = sprintf "%2.4f",$beta;
}

####################################################################
### robust_fit: linear fit for data within 3 sigma deviation ##
####################################################################

sub robust_fit_old2{

#
#---- fit the first round of linear line
#---- bin data so that we can weight fitting
#
        @xtemp = @xdata;
        @ytemp = @ydata;
        $tot   = $data_cnt;
	@temp = sort{$a<=>$b} @xtemp;
	$diff = $temp[$tot-1] - $temp[0];
#	$step = 0.05 * $diff;
	$step = 0.10 * $diff;
	for($k = 0; $k < 10; $k++){
		$x_bin[$k] = $step * ($k + 0.5) + $temp[0];
		$y_bin[$k] = 0;
		$y_cnt[$k] = 0;
	}
	OUTER:
	for($i = 0; $i < $tot; $i++){
		for($k = 0; $k < 10; $k++){
			$bot = $step * $k + $temp[0];
			$top = $step * ($k + 1)+ $temp[0];
			if($xtemp[$i] > $bot && $xtemp[$i] <= $top){
				$y_bin[$k] += $ytemp[$i];
				$y_bin2[$k] += $ytemp[$i] * $ytemp[$i];
				$y_cnt[$k]++;
				next OUTER;
			}
		}
	}
	
	$w_ind = 1;		# initiate weighted least fit
	@xtemp = ();
	@ytemp = ();
	@sig_y = ();
	$tot = 0;
	OUTER:
	for($k = 0; $k < 10; $k++){
		if($y_cnt[$k] == 0){
			next OUTER;
		}
		$xtemp[$tot] = $x_bin[$k];
		$ytemp[$tot] = $y_bin[$k]/$y_cnt[$k];
		$sig_y[$tot] = sqrt($y_bin2[$k]/$y_cnt[$k] - $ytemp[$k] * $ytemp[$k]);
	 	$tot++;
	}
        least_fit();

	$w_ind = 0;		# back to non weighted least fit
#
#---- find a sigma from the fitting line
#

        @xtemp = @xdata;
        @ytemp = @ydata;
        $tot   = $data_cnt;

        $sum  = 0;
        $sum2 = 0;
        for($k = 0; $k < $data_cnt ; $k++){
                $diff = $ydata[$k] - ($int + $slope * $xdata[$k]);
                $sum  += $diff;
                $sum2 += $diff * $diff;
        }
#
#---- find 3 sigma deviation
#
        $avg = $sum / $data_cnt;
        $sig = sqrt ($sum2/$data_cnt - $avg * $avg);
        $sig3 = 3.0 * $sig;
#
#---- collect data points in the 3 sigma range (in dependent variable)
#

        @x_trim = ();
        @y_trim = ();
        $cnt_trim = 0;;
        for($k = 0; $k < $data_cnt ; $k++){
                $diff = abs($ydata[$k] - ($int + $slope * $xdata[$k]));
                if($diff < $sig3){
                        push(@x_trim, $xdata[$k]);
                        push(@y_trim, $ydata[$k]);
                        $cnt_trim++;
                }
        }
#
#----- compute new linear fit for the selected data points
#

        @xtemp = @x_trim;
        @ytemp = @y_trim;
        $tot   = $cnt_trim;
        least_fit();

#
#---- repeat one more time to tight up the fit
#
        $sum  = 0;
        $sum2 = 0;
        for($k = 0; $k < $data_cnt ; $k++){
                $diff = $ydata[$k] - ($int + $slope * $xdata[$k]);
                $sum  += $diff;
                $sum2 += $diff * $diff;
        }

        $avg = $sum / $data_cnt;
        $sig = sqrt ($sum2/$data_cnt - $avg * $avg);
        $sig3 = 3.0 * $sig;
        @x_trim = ();
        @y_trim = ();
        $cnt_trim = 0;
        for($k = 0; $k < $data_cnt ; $k++){
                $diff = abs($ydata[$k] - ($int + $slope * $xdata[$k]));
                if($diff < $sig3){
                        push(@x_trim, $xdata[$k]);
                        push(@y_trim, $ydata[$k]);
                        $cnt_trim++;
                }
        }

        @xtemp = @x_trim;
        @ytemp = @y_trim;
        $tot   = $cnt_trim;
        least_fit();
}


####################################################################
####################################################################
####################################################################

sub double_fit{

        $top = 0;
        $mid = 0;
        $bot = 0;
#
#---- fit the first round of linear line
#
        @xtemp = @time;
        @ytemp = @rad;
        $tot   = $cnt;
       	least_fit();
	$sum  = 0; 
	$sum2 = 0;
	for($i = 0; $i < $tot; $i++){
		$diff = $rad[$i] - ($int + $slope * $time[$i]);
		$sum += $diff;
		$sum2 += $diff * $diff;
	}
	$avg  = $sum/$tot;
	$step = 0.5 * sqrt($sum2/$tot - $avg * $avg);

	for($i = 0; $i < $tot; $i++){
		$center = $int + $slope * $time[$i];
		$bound1 = $center - $step;
		$bound2 = $center + $step;
                if($rad[$i] < $bound1){
                        $bot++;
                }elsif($rad[$i] > $bound2){
                        $top++;
                }else{
                        $mid++;
                }
        }

        if($mid < $top && $mid < $bot){
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
                       $diff = $rad[$k] - ($int + $slope * $time[$k]);
#                        $diff = $rad[$k] -  $avg;
                        if($diff < 0){
                                push(@x_save1, $time[$k]);
                                push(@y_save1, $rad[$k]);
                                $d_cnt1++;
                        }else{
                                push(@x_save2, $time[$k]);
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
		if($w_ind == 1){
			$weight = 1.0/($sig_y[$fit_i] *  $sig_y[$fit_i]);
		}else{
			$weight = 1.0;
		}
                $lsum++;
                $lsumx += $xtemp[$fit_i] * $weight;
                $lsumy += $ytemp[$fit_i] * $weight;
                $lsumx2+= $xtemp[$fit_i]*$xtemp[$fit_i] * $weight;
                $lsumy2+= $ytemp[$fit_i]*$ytemp[$fit_i] * $weight;
                $lsumxy+= $xtemp[$fit_i]*$ytemp[$fit_i] * $weight;
        }

        $delta = $lsum*$lsumx2 - $lsumx*$lsumx;
        if($delta > 0){
                $int   = ($lsumx2*$lsumy - $lsumx*$lsumxy)/$delta;
                $slope = ($lsumxy*$lsum - $lsumx*$lsumy)/$delta;
                $slope = sprintf "%2.4f",$slope;
        	$tot1 = $tot - 1;
        	$variance = ($lsumy2 + $int*$int*$lsum + $slope*$slope*$lsumx2
                	-2.0 *($int*$lsumy + $slope*$lsumxy - $int*$slope*$lsumx))/$tot1;
        	$sigm_slope = sqrt($variance*$lsum/$delta);
        	$sigm_slope = sprintf "%2.4f",$sigm_slope;
        }else{
                $int = 999999;
                $slope = 0.0;
		$sigm_slope = 0.0;
        }
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
