#!/usr/bin/env /usr/local/bin/perl
use PGPLOT;

#################################################################################################
#												#
#	acis_sib_long_term_lev2.perl: read all past sib data, and plot them for each CCD	#
#												#
#	author: t. isobe (tisobe@cfa.harvard.edu)						#
#												#
#	last update: Apr 23, 2013								#
#												#
#################################################################################################


#######################################
#
#---- setting directories
#
$bin_dir  = '/data/mta/MTA/bin/';
$bdata_dir = '/data/mta/MTA/data/';
$data_dir  = '/data/mta/Script/ACIS/SIB/Lev2/Data/';
$web_dir  = '/data/mta/www/mta_sib/Lev2/';
#$web_dir  = './';


### set a parameters
	$pol_dim = 2;			#--- polinomial dimension

##################################

system("mkdir ./Temp_data");		#--- create a temporary directory for computations
$alist = `ls -d *`;             	#---- clean up param dir
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
#---- go thought all CCD one by one
#

for($ccd = 0; $ccd < 10; $ccd++){
#for($ccd = 3; $ccd < 4; $ccd++){

#
#---- here is the directories where all the past data are stored
#
#$web_dir2 = '/data/mta/www/mta_sib/Lev2/';
	$name = "$data_dir".'/Data_*_*/lres_ccd'."$ccd".'_merged.fits*';
#	$name = "$web_dir".'/Data/Data_*_*/lres_ccd'."$ccd".'_merged.fits';
	$temp_data_list = `ls $name`;
	@data_list = split(/\s+/, $temp_data_list);

	@time    = ();
	@time_sec= ();
	@ssoft   = ();
	@soft    = ();
	@med     = ();
	@hard    = ();
	@harder  = ();
	@hardest = ();
	@all     = ();


	$i = 0;					# this index counts full entires
	foreach $data (@data_list){
		$fdata = "$data".'+1';
#
#----- first just read time entry
#
		$line = "$fdata".'[cols time]';
		system("dmlist infile=\"$line\" outfile=./Temp_data/zzout opt=data");
		open(IN, "./Temp_data/zzout");

		$k = 0;				# this index counts only in the current fits file
		OUTER:
		while(<IN>){
			chomp $_;
			@atemp = split(/\s+/, $_);
			if($atemp[1] =~ /\d/  && $atemp[2] =~ /\d/){
                                push(@time_sec, $atemp[2]);

				$tday = $atemp[2]/86400;
				OUTER:
				for($dyear = 0; $dyear = 30; $dyear++){
					if($tday < 366){	# this afftects only for year = 1998.
						$year = $dyear + 1998;
						$yday = $tday;
						$date = $year + $yday/365;
						last OUTER;
					}
					$zt = 4 * int (0.25 * $dyear);
					if($zt == $dyear){
						$tydate = 366;
					}else{
						$tydate = 365;
					}
					$tday -=  $tydate * $dyear;
					if($tday <= $tydate){
						$year = $dyear + 1998;
						$yday = $tday;
						$date = $year + $yday/$tydate;
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

			$j = $i;		# j counter also spans only for this fits file output 
			OUTER:
			while(<IN>){
				chomp $_;
				@atemp = split(/\s+/, $_);
				if($atemp[1] =~ /\d/  && $atemp[2] =~ /\d/){
					$diff = $time_sec[$j] - $time_sec[$j - 1];
					if($diff <  100){
						$diff = 500;
					}
#
#---- normalizing count rates to per sec
#
					$rad = $atemp[2]/$diff;
					push(@{$ent}, $rad);
					$j++;
				}
			}
			close(IN);
			system("rm -rf ./Temp_data/zzout");
		}
		$i += $k;			# increase the count steps of the fits file
	}	

#
#---- full energy range counts are stored in @all
#
	$cnt = 0;				# this will be the total counts of the steps
	foreach $ent (@time){
		$sum = $ssoft[$cnt] + $soft[$cnt] + $med[$cnt] + $hard[$cnt] + $harder[$cnt] + $hardest[$cnt];
		push(@all,$sum);
		$cnt++;
	}
#
#---- time1999 is 0 at Jan 1, 1999. this variable is used as an indep var. to compute fitting lines.
#

for($ni = 0; $ni < $cnt; $ni++){
		$time1999[$ni] =$time[$ni] -  1999;
}
	$xmin = $time[0];
	if($xmin < 1999){		#---- just in a case, a strange starting time occured.
		$xmin = 1999.6;		#---- in that case, set this to be a beginning of the plot
	}
	$xmax = $time[$cnt -1];
	$diff = $xmax - $xmin;
	$xmin -= 0.05 * $diff;
	$xmax += 0.05 * $diff + 2;
#
#----- a count rate plot for a accumurated case
#
	@rad = @all;
	@xdata = @time1999;
	@ydata = @rad;
	$rdata_cnt = $cnt;

	find_avg_and_range();		#--- find an average and  plotting range for y axis
#	three_sigma_fit();		#--- select data point in 3 sigma deviation and fit a line
	robust_fit();

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

	system("echo ''|gs -sDEVICE=ppmraw  -r256x256 -q -NOPAUSE -sOutputFile=-  ./Temp_data/pgplot.ps|pnmflip -r270 |ppmtogif > $web_dir/Plots/Plot_long/$name2");
	system("rm -rf ./Temp_data/pgplot.ps");

#
#---- indivisual plots start here
#
	pgbegin(0, '"./Temp_data/pgplot.ps"/cps',1,1);
	pgsubp(2,3);
	pgsch(2);
	pgslw(4);

	@tim1 = ();
	@tim2 = ();
	@yt1  = ();
	@yt2  = ();
	@rad1 = ();
	@rad2 = ();
	$tcnt1= 0;
	$tcnt2= 0;
	
	for($k = 0; $k < $cnt; $k++){
		if($time1999[$k] < 4.20){
			push(@tim1, $time1999[$k]);
			push(@rad1, $ssoft[$k]);
			push(@yt1,  $time[$k]);
			$tcnt1++;
		}elsif($time1999[$k] > 4.26){
			push(@tim2, $time1999[$k]);
			push(@rad2, $ssoft[$k]);
			push(@yt2,  $time[$k]);
			$tcnt2++;
		}
	}


	@rad = @ssoft;
	find_avg_and_range();

	@xrdata = @tim1;
	@yrdata = @rad1;
	$rdata_cnt = $tcnt1;

	robust_fit();

	$int -= $slope * 1999;
	$int1 = $int;
	$slope1 = $slope;

	@xrdata = @tim2;
	@yrdata = @rad2;
	$rdata_cnt = $tcnt2;

	robust_fit();

	$int -= $slope * 1999;
	$int2 = $int;
	$slope2 = $slope;

	$title = 'Super Soft Photons';
	$color_index = 2;
	plot_fig();
#
#---- Soft
#
	@rad = @soft;
	find_avg_and_range();
#	three_sigma_fit();
	@xrdata    = @time1999;
	@yrdata    = @rad;
	$rdata_cnt = $cnt;
	robust_fit();
	$int  -= $slope * 1999;
	$title = 'Soft Photons';
	$color_index = 4;
	plot_fig();
#
#--- Med
#
	@rad = @med;
	find_avg_and_range();
#	three_sigma_fit();
	@xrdata    = @time1999;
	@yrdata    = @rad;
	$rdata_cnt = $cnt;
	robust_fit();
	$int -= $slope * 1999;
	$title = 'Moderate Energy Photons';
	$color_index = 6;
	plot_fig();
#
#--- Hard
#
	@rad = @hard;
	find_avg_and_range();
#	three_sigma_fit();
	@xrdata    = @time1999;
	@yrdata    = @rad;
	$rdata_cnt = $cnt;
	robust_fit();
	$int -= $slope * 1999;
	$title = 'Hard Photons';
	$color_index = 8;
	plot_fig();
#
#--- Harder
#
	@rad = @harder;
	find_avg_and_range();
#	three_sigma_fit();
	@xrdata    = @time1999;
	@yrdata    = @rad;
	$rdata_cnt = $cnt;
	robust_fit();
	$int -= $slope * 1999;
	$title = 'Very Hard  Photons';
	$color_index = 10;
	plot_fig();
#
#--- Hardest
#
	@rad = @hardest;
	@xdata = @time1999;
	@ydata = @rad;
	$data_cnt = $cnt;
	find_avg_and_range();
	double_fit();
	$title = 'Beyond 10 KeV';
	$color_index = 12;
#	plot_fig();
	plot_fig_double();

	pgclos();

	$name2 = 'long_indep_plot_ccd'."$ccd".'.gif';

	system("echo ''|gs -sDEVICE=ppmraw  -r256x256 -q -NOPAUSE -sOutputFile=-  ./Temp_data/pgplot.ps|pnmflip -r270 |ppmtogif > $web_dir/Plots/Plot_long/$name2");
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
	if($color_index == 2){
        	$ypos1 = $int1 + $slope1 * $xmin;
        	$ypos2 = $int1 + $slope1 * 2003.24;
        	pgmove($xmin, $ypos1);
        	pgdraw(2003.24, $ypos2);
		$line = "slope: $slope1";
        	pgtext($xt, $yt, $line);

        	$ypos1 = $int2 + $slope2 * 2003.24;
        	$ypos2 = $int2 + $slope2 * $xmax;
        	pgmove(2003.24, $ypos1);
        	pgdraw($xmax, $ypos2);
		$yt = $yt - 0.1 * abs ($ymax - $ymin);
		$line = "slope: $slope2";
        	pgtext($xt, $yt, $line);
	}else{
        	$ypos1 = $int + $slope * $xmin;
        	$ypos2 = $int + $slope * $xmax;
        	pgmove($xmin, $ypos1);
        	pgdraw($xmax, $ypos2);
        	$line = "slope: $slope";
        	pgtext($xt, $yt, $line);
	}
#
#---- E > 12 keV has two lines
#
        if($color_index == 12 && $slope2 =~ /\d/){
                $ypos1 = $int2 + $slope2 * $xmin;
                $ypos2 = $int2 + $slope2 * $xmax;
                pgmove($xmin, $ypos1);
                pgdraw($xmax, $ypos2);
                $yt = $yt - 0.1 * abs ($ymax - $ymin);
                $line = "slope: $slope2";
                pgtext($xt, $yt, $line);
        }
        pglabel("time (Year)","cnts/s", "$title");
}

##########################################################################
#### plot_fig_double: plotting sub for double line                     ###
##########################################################################

sub plot_fig_double{
        pgenv($xmin, $xmax, $ymin, $ymax, 0, 0);
        pgsci($color_index);
        for($k = 0; $k < $cnt; $k++){
                pgpt(1,$time[$k], $rad[$k], 1);
        }
        pgsci(1);

#
#---- a fitting line plotting; intercept is at (x = 0) Jan 1, 1999.
#
	@tordr = sort{$a<=>$b}@time;
	$y_est = pol_val($pol_dim, $xmin);		#--- compute pol fit for given dim and a[$i]
	pgmove($xmin, $y_est);
#	$step = ($tordr[$cnt-1] - $tordr[1])/$cnt;
	$step = 0.008;
	$cnt2 = int(($xmax - $xmin)/$step);
	for($k = 1; $k < $cnt2; $k++){
		$tx = $step * $k + $tordr[1];
		$tx1999 = $tx - 1999;			#--- making x = 0 at Jan 1, 1999
		$y_est = pol_val($pol_dim, $tx1999);
		pgdraw($tx, $y_est);
	}

#
#---- labeling start here
#
        $xt = 0.05* ($xmax - $xmin) + $xmin;
        $yt = $ymax - 0.1 * ($ymax - $ymin);
        $line = "";
	for($m = 0; $m < $pol_dim; $m++){
		$coeff = digit_clean($a[$m]);		#---- shorten number for a cleaner display
		$tline = "Slope: $coeff";
#		if($m == 0){
#			$tline = "$coeff";
#		}elsif($m == 1){
#			if($coeff < 0){
#				$coeff = abs($coeff);
#				$tline = "$tline"." - $coeff * x";
#			}else{
#				$tline = "$tline"." + $coeff * x";
#			}
#		}elsif($m > 1){
#			if($coeff < 0){
#				$coeff = abs($coeff);
#				$tline = "$tline"." - $coeff * x**$m";
#			}else{
#				$tline = "$tline"." + $coeff * x**$m";
#			}
#		}
	}
	$line = "$line"."$tline";

	pgsch(1.6);
        pgtext($xt, $yt, $line);
	pgsch(2);
#
#---- E > 10 keV has two lines
#
        if($color_index == 12 && $a[1] =~ /\d/){
		@a = @b2;
		$y_est = pol_val($pol_dim, $xmin);
		pgmove($xmin, $y_est);
		for($k = 1; $k < $cnt2; $k++){
			$tx = $step * $k + $tordr[1];
			$tx1999 = $tx - 1999;
			$y_est = pol_val($pol_dim, $tx1999);
			pgdraw($tx, $y_est);
        	}
		
               	$line = "slope: $slope2 +/- $sigm_slope2";
		$yt = $yt - 0.1 * abs ($ymax - $ymin);
        	$line = "";
		for($m = 0; $m < $pol_dim; $m++){
			$coeff = digit_clean($a[$m]);
			$tline = "Slope: $coeff";
#			if($m == 0){
#				$tline = "$coeff";
#			}elsif($m == 1){
#				if($coeff < 0){	
#					$coeff = abs ($coeff);
#					$tline = "$tline"." - $coeff * x";
#				}else{
#					$tline = "$tline"." + $coeff * x";
#				}
#			}elsif($m > 1){
#				if($coeff < 0){
#					$coeff = abs($coeff);
#					$tline = "$tline"." - $coeff * x**$m";
#				}else{
#					$tline = "$tline"." + $coeff * x**$m";
#				}
#			}
		}
		$line = "$line"."$tline";
		pgsch(1.6);
               	pgtext($xt, $yt, $line);
		pgsch(2);
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
		if($xmin < 1999){
			$xmin = 1999.6;
		}
                $xmax = $atemp[$cnt - 1];
		$xmax += 2;


		@xrdata = @time;
		@yrdata = @rad;
		$rdata_cnt = $cnt;
		robust_fit();

		$tavg = $int + $slope * $atemp[$cnt/2];
		$dsum = 0;
		foreach $ent (@rad){
			$dsum += abs($ent - $yavg);
		}
		$dsum /= $cnt;
		$ymax = $tavg + 1.5 * $dsum;
		$ymin = $tavg - $dsum;

                @atemp = sort{$a<=>$b} @rad;
#                $ymin = 0;
#		$ymin = $avg - 3.0 * $sigma;
		$ymin *= 10;
		$ymin = int $ymin;
		$ymin /= 10;
		if($ymin < 0){
			$ymin = 0;
		}
#		$ymax = $avg + 3.0 * $sigma;
		$ymax *= 100;
		$ymax = int $ymax;
		$ymax /= 100;

		if($ymax <= $ymin){
			$ymax = $ymin + 1;
		}
        }
}

####################################################################
### double_fit: fitting 2 lines on  > 10 keV data plot           ###
####################################################################

sub double_fit{

        $top = 0;
        $mid = 0;
        $bot = 0;
#
#---- fit the first round of fitting
#
        @xdata  = @time1999;
        @ydata  = @rad;
	@data_cnt = $cnt;

        three_sigma_fit();

	$y_sum = 0;
	for($j = 0; $j < $data_cnt; $j++){
		$y_sum += $ydata[$j];
	}
	$y_div = $y_sum/$data_cnt;

        for($i = 0; $i < $cnt; $i++){
		$y_est = pol_val($pol_dim,$time1999[$i]);
		$diff = $rad[$i] - $y_est;
                $sum += $diff;
               	$sum2 += $diff * $diff;
        }
        $avg  = $sum/($cnt -1);
        $step = 0.5 * sqrt($sum2/($cnt -1) - $avg * $avg);

        for($i = 0; $i < $cnt; $i++){
		$center = pol_val($pol_dim,$time1999[$i]);
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

#        if($mid < $top && $mid < $bot){
	if($data_cnt > 0){

#
#----  devide data into two regions; below and above the polinomial fitting line
#
                @x_save1 = ();
                @y_save1 = ();
                $d_cnt1  = 0;
                @x_save2 = ();
                @y_save2 = ();
                $d_cnt2  = 0;
                for($k = 0; $k < $data_cnt ; $k++){
			$y_est = pol_val($pol_dim,$time1999[$k]);
			$diff = $rad[$k] - $y_est;
                        if($diff < 0){
                                push(@x_save1, $time1999[$k]);
                                push(@y_save1, $rad[$k]);
                                $d_cnt1++;
                        }else{
                                push(@x_save2, $time1999[$k]);
                                push(@y_save2, $rad[$k]);
                                $d_cnt2++;
                        }
                }

#
#--- lower line fitting
#
##		@xdata = @x_save1;
##		@ydata = @y_save1;
##		$data_cnt = $d_cnt1;
##		if($data_cnt == 0){
##			$int2        = 0;
##			$slope2      = 0;
##			$sigm_slope2 = 0;
##		}else{	
##			robust_fit();
##			$int2        = $int;
##			$slope2      = $slope;
##			$sigm_slope2 = $sigm_slope;
##		}

#
#--- upper line fitting
#
##		@xdata = @x_save2;
##		@ydata = @y_save2;
##		$data_cnt = $d_cnt2;
##		if($data_cnt == 0){
##			$int        = 0;
##			$slope      = 0;
##			$sigm_slope = 0;
##		}else{
##			robust_fit();
##		}
##       }else{
##              robust_fit();
##     }




#
#--- lower line fitting
#
                @xdata = @x_save1;
                @ydata = @y_save1;
                $data_cnt = $d_cnt1;
                if($data_cnt == 0){
                        for($mm = 0; $mm <= $pol_dim; $mm++){
                                $b2[$mm] = 0;
                        }
                }else{
                        three_sigma_fit();
                        for($mm = 0; $mm <= $pol_dim; $mm++){
                                $b2[$mm] = $a[$mm];
                        }
                      $int2        = $int;
                      $slope2      = $slope;
                      $sigm_slope2 = $sigm_slope;

                }

#
#--- upper line fitting
#
                @xdata = @x_save2;
                @ydata = @y_save2;
                $data_cnt = $d_cnt2;
                if($data_cnt == 0){
                        for($mm = 0; $mm <= $pol_dim; $mm++){
                                $a[$mm] = 0;
                        }
                }else{
                        three_sigma_fit();
                }
        }else{
                three_sigma_fit();
        }

}


####################################################################
### three_sigma_fit: linear fit for data within 3 sigma deviation ##
####################################################################

sub three_sigma_fit{

	if($ccd == 4 || $ccd == 9){			#---- ccds 4 and 9 do not have enough
        	@x_in     = @xdata;			#---- data points to do a fancy descrimination
        	@y_in     = @ydata;			#---- so we just take a straight fitting
        	$npts  = $data_cnt;
        	$mode  = 0;
        	$nterms = $pol_dim;
        	svdfit($npts,$nterms);			#---- pol fit routine from Numerical Recipes
	}else{
#
#---- fit the first round of polinomial line fit
#---- bin the data so that we can weight fitting
#
        	@xtemp = @xdata;
        	@ytemp = @ydata;
        	$tot   = $data_cnt;
        	@temp = sort{$a<=>$b} @xtemp;
        	$diff = $temp[$tot-1] - $temp[1];
        	$step = 0.02 * $diff;
        	for($k = 0; $k < 50; $k++){
                	$x_bin[$k] = $step * ($k + 0.5) + $temp[1];
                	$y_bin[$k] = 0;
               		$y_cnt[$k] = 0;
        	}
        	OUTER:
        	for($i = 0; $i < $tot; $i++){
                	for($k = 0; $k < 50; $k++){
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
	
        	@x_in = ();
        	@y_in = ();
        	@sigmay = ();
        	$npts = 0;
        	OUTER:
        	for($k = 0; $k < 50; $k++){
                	if($y_cnt[$k] == 0){
                        	next OUTER;
                	}
               		$x_in[$npts] = $x_bin[$k];
                	$y_in[$npts] = $y_bin[$k]/$y_cnt[$k];
                	$sigmay[$npts] = sqrt($y_bin2[$k]/$y_cnt[$k] - $y_in[$npts] * $y_in[$npts]);
                	$npts++;
        	}
		$mode   = 1;
		$nterms = $pol_dim;
		svdfit($npts,$nterms);
		$mode   = 0;		# back to non weighted fit

#
#---- find a sigma from the fitting line
#
       	 	$sum  = 0;
       	 	$sum2 = 0;
       	 	for($k = 0; $k < $data_cnt ; $k++){
			$y_est = pol_val($pol_dim, $xdata[$k]);
			$diff = $ydata[$k] - $y_est;
       	         	$sum  += $diff;
       	         	$sum2 += $diff * $diff;
       	 	}
#
#---- find 3 sigma deviation
#
       	 	$avg  = $sum / $data_cnt;
       	 	$sig  = sqrt ($sum2/$data_cnt - $avg * $avg);
       	 	$sig3 = 3.0 * $sig;
#
#---- collect data points in the 3 sigma range (in dependent variable)
#

       	 	@x_trim   = ();
       	 	@y_trim   = ();
       	 	$cnt_trim = 0;;
       	 	for($k = 0; $k < $data_cnt ; $k++){
			$y_est = pol_val($pol_dim, $xdata[$k]);
			$diff = $ydata[$k] - $y_est;
       	         	if(abs($diff) < $sig3){
       	                 	push(@x_trim, $xdata[$k]);
       	                 	push(@y_trim, $ydata[$k]);
       	                 	$cnt_trim++;
       	         	}
       	 	}
#
#----- compute new linear fit for the selected data points
#

       	 	@x_in      = @x_trim;
       	 	@y_in      = @y_trim;
		$mode      = 0;
       	 	$npts      = $cnt_trim;
       	 	$nterms    = $pol_dim;
		svdfit($npts,$nterms);

#
#---- repeat one more time to tight up the fit
#
       	 	$sum  = 0;
       	 	$sum2 = 0;
       	 	for($k = 0; $k < $data_cnt ; $k++){
			$y_est = pol_val($pol_dim, $xdata[$k]);
			$diff = $ydata[$k] - $y_est;
       	         	$sum  += $diff;
       	         	$sum2 += $diff * $diff;
       	 	}
	
       	 	$avg      = $sum / $data_cnt;
       	 	$sig      = sqrt ($sum2/$data_cnt - $avg * $avg);
       	 	$sig3     = 3.0 * $sig;
       	 	@x_trim   = ();
       	 	@y_trim   = ();
       	 	$cnt_trim = 0;
       	 	for($k = 0; $k < $data_cnt ; $k++){
			$y_est = pol_val($pol_dim, $xdata[$k]);
			$diff = $ydata[$k] - $y_est;
       	         	if(abs($diff) < $sig3){
       	                 	push(@x_trim, $xdata[$k]);
       	                 	push(@y_trim, $ydata[$k]);
       	                 	$cnt_trim++;
       	         	}
       	 	}
	
       	 	@x_in   = @x_trim;
       	 	@y_in   = @y_trim;
		$mode   = 0;
       	 	$npts   = $cnt_trim;
		$nterms = $pol_dim;
		svdfit($npts,$nterms);
	}
}


#################################################################################
### polfit: polinomial line fitting routine                                   ###
#################################################################################

sub polfit{
#
#---- this code is taken from Data Reduction adn Error Analysis for the
#---- Physical Sciences (Bevington, 1969 older edition). The original is FOTRAN
#---- this code is not used in this computation, but kept for future use.
#
	$nmax = 2 * $nterms;
	for($i = 0; $i < $nmax; $i++){
		$sumx[$i] = 0;
	}
	for($i = 0; $i < $nterms; $i++){
		$sumy[$i] = 0;
	}
	$chisq = 0;

	for($i = 0; $i < $npts; $i++){
		$xi = $x[$i];
		$yi = $y[$i];
		if($mode < 0){
			if($yi < 0){
				$weight = -1.0 /$yi;
			}elsif($yi >  0){
				$weight = 1.0/$yi;
			}else{
				$weight = 1.0;
			}
		}elsif($mode > 0){
			$weight = 1.0/($sigmay[$i] * $sigmay[$i]);
		}else{
			$weight = 1.0;
		}

		$xterm = $weight;
		for($j = 0; $j < $nmax; $j++){
			$sumx[$j] += $xterm;
			$xterm *= $xi;
		}
		$yterm = $weight * $yi;
		for($j = 0; $j < $nterms; $j++){
			$sumy[$j] += $yterm;
			$yterm *= $xi;
		}
		$chisq += $weight * $yi * $yi;
	}

	for($i = 0; $i < $nterms; $i++){
		for($j = 0; $j < $nterms; $j++){
			$n = $i + $j;
			$array[$i][$j] = $sumx[$n];
		}
	}

	$norder = $nterms;
	determ();

	$delta = $d_out;

	if($delta == 0){
		$chisq = 0;
		for($j = 0; $j < $nterms; $j++){
			$a[$j] = 0;
		}
	}else{
		for($l = 0; $l < $nterms; $l++){
			for($j = 0; $j < $nterms;$j++){
				for($k = 0; $k < $nterms; $k++){
					$n = $j + $k;
					$array[$j][$k] = $sumx[$n];
				}
				$array[$j][$l] = $sumy[$j];
			}
			$norder = $nterms;
			determ();
			$a[$l]  = $d_out/$delta;
		}

		for($j = 0; $j < $nterms; $j++){
			$chisq -= 2.0 * $a[$j] * $sumy[$j];
			for($k = 0; $k < $nterms; $k++){
				$n = $j + $k;
				$chisq += $a[$j] * $a[$k] * $sumx[$n];
			}
		}
		$free = $npt - $nterms;
		$chisq = $chisq/$free;
	}
}

#################################################################################
### determ: deteminant computation routine                                    ###
#################################################################################

sub determ{
#
#---- this code is taken from Data Reduction adn Error Analysis for the
#---- Physical Sciences (Bevington, 1969 older edition). The original is FOTRAN
#---- this code is not used in this computation, but kept for future use.
#
	my ($i, $j, $k, $l, $n);
	for($i = 0; $i < $norder; $i++){
		for($j = 0; $j < $norder; $j++){
			$darray[$i][$j] = $array[$i][$j];
		}
	}
	$d_out = 1;
	OUTER:
	for($k = 0; $k < $norder; $k++){
		if($darray[$k][$k] == 0){
			for($j = $k; $j < $norder; $j++){
				if($darray[$k][$j] == 0){
					$d_out = 0;
					last OUTER;
				}
				for($i = $k; $i < $norder; $i++){
					$save = $darray[$i][$j];
					$darray[$i][$j] = $darray[$i][$k];
					$darray[$i][$k] = $save;
				}
				$d_out *= -1.0;
			}
		}

		$d_out *= $darray[$k][$k];
		$diff = $k - $norder;
		if($diff < 0){
			$k1 = $k + 1;
			for($i = $k1; $i < $norder; $i++){
				for($j = $k1; $j < $norder; $j++){
					$darray[$i][$j] -= $darray[$i][$k] * $darray[$k][$j]/$darray[$k][$k];
				}
			}
		}
	}
}

####################################################################
### least_fit: least sq. fit routine                             ###
####################################################################

sub least_fit{
#
#----- this code is not used in this computation
#
        $lsum = 0;
        $lsumx = 0;
        $lsumy = 0;
        $lsumxy = 0;
        $lsumx2 = 0;
        $lsumy2 = 0;


        for($fit_i = 0; $fit_i < $tot; $fit_i++) {
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

########################################################################
###svdfit: polinomial line fit routine                               ###
########################################################################

sub svdfit{
#
#----- this code was taken from Numerical Recipes. the original is FORTRAN
#

	$tol = 1.e-5;

	my($ndata, $ma, @x, @y, @sig);
	($ndata, $ma) = @_;
	for($i = 0; $i < $ndata; $i++){
		$j = $i + 1;
		$x[$j] = $x_in[$i];
		$y[$j] = $y_in[$i];
		$sig[$j] = $sigmay[$i];
	}
#
#---- accumulate coefficients of the fitting matrix
#
	for($i = 1; $i <= $ndata; $i++){
		funcs($x[$i], $ma);
		if($mode == 0){
			$tmp = 1.0;
			$sig[$i] = 1.0;
		}else{
			$tmp = 1.0/$sig[$i];
		}
		for($j = 1; $j <= $ma; $j++){
			$u[$i][$j] = $afunc[$j] * $tmp;
		}
		$b[$i] = $y[$i] * $tmp;
	}
#
#---- singular value decompostion sub
#
	svdcmp($ndata, $ma);		###### this also need $u[$i][$j] and $b[$i]
#
#---- edit the singular values, given tol from the parameter statements
#
	$wmax = 0.0;
	for($j = 1; $j <= $ma; $j++){
		if($w[$j] > $wmax) {$wmax = $w[$j]}
	}
	$thresh = $tol * $wmax;
	for($j = 1; $j <= $ma; $j++){
		if($w[$j] < $thresh){$w[$j] = 0.0}
	}

	svbksb($ndata, $ma);		###### this also needs b, u, v, w. output is a[$j]
#
#---- evaluate chisq
#
	$chisq = 0.0;
	for($i = 1; $i <= $ndata; $i++){
		funcs($x[$i], $ma);
		$sum = 0.0;
		for($j = 1; $j <= $ma; $j++){
			$sum  += $a[$j] * $afunc[$j];
		}
		$diff = ($y[$i] - $sum)/$sig[$i];
		$chisq +=  $diff * $diff;
	}
}


########################################################################
### svbksb: solves a*x = b for a vector x                            ###
########################################################################

sub svbksb {
#
#----- this code was taken from Numerical Recipes. the original is FORTRAN
#
	my($m, $n, $i, $j, $jj, $s);
	($m, $n) = @_;
	for($j = 1; $j <= $n; $j++){
		$s = 0.0;
		if($w[$j] != 0.0) {
			for($i = 1; $i <= $m; $i++){
				$s += $u[$i][$j] * $b[$i];
			}
			$s /= $w[$j];
		}
		$tmp[$j] = $s;
	}

	for($j = 1; $j <= $n; $j++){
		$s = 0.0;
		for($jj = 1; $jj <= $n;	$jj++){
			$s += $v[$j][$jj] * $tmp[$jj];
		}
		$i = $j -1;
		$a[$i] = $s;
	}
}

########################################################################
### svdcmp: compute singular value decomposition                     ###
########################################################################

sub svdcmp {
#
#----- this code wass taken from Numerical Recipes. the original is FORTRAN
#
	my ($m, $n, $i, $j, $k, $l, $mn, $jj, $x, $y, $s, $g);
	($m, $n) = @_;
	
	$g     = 0.0;
	$scale = 0.0;
	$anorm = 0.0;

	for($i = 1; $i <= $n; $i++){
		$l = $i + 1;
		$rv1[$i] = $scale * $g;
		$g = 0.0;
		$s = 0.0;
		$scale = 0.0;
		if($i <= $m){
			for($k = $i; $k <= $m; $k++){
				$scale += abs($u[$k][$i]);
			}
			if($scale != 0.0){
				for($k = $i; $k <= $m; $k++){
					$u[$k][$i] /= $scale;
					$s += $u[$k][$i] * $u[$k][$i];
				}
				$f = $u[$i][$i];

				$ss = $f/abs($f);
				$g = -1.0  * $ss * sqrt($s);
				$h = $f * $g - $s;
				$u[$i][$i] = $f - $g;
				for($j = $l; $j <= $n; $j++){
					$s = 0.0;
					for($k = $i; $k <= $m; $k++){
						$s += $u[$k][$i] * $u[$k][$j];
					}
					$f = $s/$h;
					for($k = $i; $k <= $m; $k++){
						$u[$k][$j] += $f * $u[$k][$i];
					}
				}
				for($k = $i; $k <= $m; $k++){
					$u[$k][$i] *= $scale;
				}
			}
		}

		$w[$i] = $scale * $g;
		$g = 0.0;
		$s = 0.0;
		$scale = 0.0;
		if(($i <= $m) && ($i != $n)){
			for($k = $l; $k <= $n; $k++){
				$scale += abs($u[$i][$k]);
			}
			if($scale != 0.0){
				for($k = $l; $k <= $n; $k++){
					$u[$i][$k] /= $scale;
					$s += $u[$i][$k] * $u[$i][$k];
				}
				$f = $u[$i][$l];

				$ss = $f /abs($f);
				$g  = -1.0 * $ss * sqrt($s);
				$h = $f * $g - $s;
				$u[$i][$l] = $f - $g;
				for($k = $l; $k <= $n; $k++){
					$rv1[$k] = $u[$i][$k]/$h;
				}
				for($j = $l; $j <= $m; $j++){
					$s = 0.0;
					for($k = $l; $k <= $n; $k++){
						$s += $u[$j][$k] * $u[$i][$k];
					}
					for($k = $l; $k <= $n; $k++){
						$u[$j][$k] += $s * $rv1[$k];
					}
				}
				for($k = $l; $k <= $n; $k++){
					$u[$i][$k] *= $scale;
				}
			}
		}

		$atemp = abs($w[$i]) + abs($rv1[$i]);
		if($atemp > $anorm){
			$anorm = $atemp;
		}
	}

	for($i = $n; $i > 0; $i--){
		if($i < $n){
			if($g != 0.0){
				for($j = $l; $j <= $n; $j++){
					$v[$j][$i] = $u[$i][$j]/$u[$i][$l]/$g;
				}
				for($j = $l; $j <= $n; $j++){
					$s = 0.0;
					for($k = $l; $k <= $n; $k++){
						$s += $u[$i][$k] * $v[$k][$j];
					}
					for($k = $l; $k <= $n; $k++){
						$v[$k][$j] += $s * $v[$k][$i];
					}
				}
			}
			for($j = $l ; $j <= $n; $j++){
				$v[$i][$j] = 0.0;
				$v[$j][$i] = 0.0;
			}	
		}
		$v[$i][$i] = 1.0;
		$g = $rv1[$i];
		$l = $i;
	}

	$istart = $m;
	if($n < $m){
		$istart = $n;
	}
	for($i = $istart; $i > 0; $i--){
		$l = $i + 1;
		$g = $w[$i];
		for($j = $l; $j <= $n; $j++){
			$u[$i][$j] = 0.0;
		}

		if($g != 0.0){
			$g = 1.0/$g;
			for($j = $l; $j <= $n; $j++){
				$s = 0.0;
				for($k = $l; $k <= $m; $k++){
					$s += $u[$k][$i] * $u[$k][$j];
				}
				$f = ($s/$u[$i][$i])* $g;
				for($k = $i; $k <= $m; $k++){
					$u[$k][$j] += $f * $u[$k][$i];
				}
			}
			for($j = $i; $j <= $m; $j++){
				$u[$j][$i] *= $g;
			}
		}else{
			for($j = $i; $j <= $m; $j++){
				$u[$j][$i] = 0.0;
			}
		}
		$u[$i][$i]++;
	}

	OUTER2:
	for($k = $n; $k > 0; $k--){
		for($its = 0; $its < 30; $its++){
			$do_int = 0;
			OUTER:
			for($l = $k; $l > 0; $l--){
				$nm = $l -1;
				if((abs($rv1[$l]) + $anorm) == $anorm){
					last OUTER;
				}
				if((abs($w[$nm]) + $anorm) == $anorm){
					$do_int = 1;
					last OUTER;
				}
			}
			if($do_int == 1){
				$c = 0.0;
				$s = 1.0;
				for($i = $l; $i <= $k; $i++){
					$f = $s * $rv1[$i];
					$rv1[i] = $c * $rv1[$i];
					if((abs($f) + $anorm) != $anorm){
						$g = $w[$i];
						$h = pythag($f, $g);
						$w[$i] = $h;
						$h = 1.0/$h;
						$c = $g * $h;
						$s = -1.0 * $f * $h;
						for($j = 1; $j <= $m; $j++){
							$y = $u[$j][$nm];
							$z = $u[$j][$i];
							$u[$j][$nm] = ($y * $c) + ($z * $s);
							$u[$j][$i]  = -1.0 * ($y * $s) + ($z * $c);
						}
					}
				}
			}

			$z = $w[$k];
			if($l == $k ){
				if($z < 0.0) {
					$w[$k] = -1.0 * $z;
					for($j = 1; $j <= $n; $j++){
						$v[$j][$k] *= -1.0;
					}
				}
				next OUTER2;
			}else{
				if($its == 29){
					print "No convergence in 30 iterations\n";
					exit 1;
				}
				$x = $w[$l];
				$nm = $k -1;
				$y = $w[$nm];
				$g = $rv1[$nm];
				$h = $rv1[$k];
				$f = (($y - $z)*($y + $z) + ($g - $h)*($g + $h))/(2.0 * $h * $y);
				$g = pythag($f, 1.0);

				$ss = $f/abs($f);
				$gx = $ss * $g;

				$f = (($x - $z)*($x + $z) + $h * (($y/($f + $gx)) - $h))/$x;

				$c = 1.0; 
				$s = 1.0;
				for($j = $l; $j <= $nm; $j++){
					$i = $j +1;
					$g = $rv1[$i];
					$y = $w[$i];
					$h = $s * $g;
					$g = $c * $g;
					$z = pythag($f, $h);
					$rv1[$j] = $z;
					$c = $f/$z;
					$s = $h/$z;
					$f = ($x * $c) + ($g * $s);
					$g = -1.0 * ($x * $s) + ($g * $c);
					$h = $y * $s;
					$y = $y * $c;
					for($jj = 1; $jj <= $n ; $jj++){
						$x = $v[$jj][$j];
						$z = $v[$jj][$i];
						$v[$jj][$j] = ($x * $c) + ($z * $s);
						$v[$jj][$i] = -1.0 * ($x * $s) + ($z * $c);
					}
					$z = pythag($f, $h);
					$w[$j] = $z;
					if($z != 0.0){
						$z = 1.0/$z;
						$c = $f * $z;
						$s = $h * $z;
					}
					$f = ($c * $g) + ($s * $y);
					$x = -1.0 * ($s * $g) + ($c * $y);
					for($jj = 1; $jj <= $m; $jj++){
						$y = $u[$jj][$j];
						$z = $u[$jj][$i];
						$u[$jj][$j] = ($y * $c) + ($z * $s);
						$u[$jj][$i] = -1.0 * ($y * $s) + ($z * $c);
					}
				}
				$rv1[$l] = 0.0;
				$rv1[$k] = $f;
				$w[$k] = $x;
			}
		}
	}
}	
	
########################################################################
### pythag: compute sqrt(x**2 + y**2) without overflow               ###
########################################################################

sub pythag{
	my($a, $b);
	($a,$b) = @_;

	$absa = abs($a);
	$absb = abs($b);
	if($absa == 0){
		$result = $absb;
	}elsif($absb == 0){
		$result = $absa;
	}elsif($absa > $absb) {
		$div    = $absb/$absa;
		$result = $absa * sqrt(1.0 + $div * $div);
	}elsif($absb > $absa){
		$div    = $absa/$absb;
		$result = $absb * sqrt(1.0 + $div * $div);
	}
	return $result;
}
	
########################################################################
### funcs: linear polymonical fuction                                ###
########################################################################

sub funcs {
	my($inp, $pwr, $kf, $temp);
	($inp, $pwr) = @_;
	$afunc[1] = 1.0;
	for($kf = 2; $kf <= $pwr; $kf++){
		$afunc[$kf] = $afunc[$kf-1] * $inp;
	}
}

########################################################################
### funcs2 :Legendre polynomial function                            ####
########################################################################

sub funcs2 {
#
#---- this one is not used in this script
#
	my($inp, $pwr, $j, $f1, $f2, $d, $twox);
	($inp, $pwr) = @_;
	$afunc[1] = 1.0;
	$afunc[2] = $inp;
	if($pwr > 2){
		$twox = 2.0 * $inp;
		$f2   = $inp;
		$d    = 1.0;
		for($j = 3; $j <= $pwr; $j++){
			$f1 = $d;
			$f2 += $twox;
			$d++;
			$afunc[$j] = ($f2 * $afunc[$j-1] - $f1 * $afunc[$j-2])/$d;
		}
	}
}
	
########################################################################
### digit_clean: shorten number for printing                         ###
########################################################################

sub digit_clean{
	($number) = @_;
	if($number =~ /e/i){
		@atemp = split(/e/i, $number);
		@btemp = split(//, $atemp[0]);
		if($btemp[0] =~ /\-/ || $btemp[0] =~ /\+/){
			if($btemp[6] > 4){
				$btemp[5]++;
			}
			$digit = "$btemp[1]$btemp[2]$btemp[3]$btemp[4]$btemp[5]";
			if($btemp[0] eq '-'){
				$adjusted = "$btemp[0]$digit".'e'."$atemp[1]";
			}else{
				$adjusted = "$digit".'e'."$atemp[1]";
			}
		}else{
			if($btemp[5] > 4){
				$btemp[4]++;
			}
			$digit = "$btemp[0]$btemp[1]$btemp[2]$btemp[3]$btemp[4]";
			$adjusted = "$digit".'e'."$atemp[1]";
		}
	}elsif($number =~ /\./){
		@atemp = split(/\./, $number);
		@btemp = split(//, $atemp[1]);
		if($btemp[3] > 4){
			$btemp[2]++;
		}
		$adjusted = "$atemp[0]".'.'."$btemp[0]$btemp[1]$btemp[2]";
	}else{
		$adjusted = $number;
	}
	return $adjusted;
}


######################################################################
### pol_val: compute a value for polinomial fit for  give coeffs   ###
######################################################################

sub pol_val{
	my ($x, $dim, $i, $j);
	($dim, $x) = @_;
	funcs($x, $dim);
	$out = $a[0];
	for($i = 1; $i <= $dim; $i++){
		$out += $a[$i] * $afunc[$i +1];
	}
	return $out;
}

####################################################################
### robust_fit: linear fit for data with medfit robust fit metho  ##
####################################################################

sub robust_fit{

        @temp = sort{$a<=>$b} @xrdata;
        $xtmin = $temp[0];
	$xtmax = $temp[$rdata_cnt -2];
	
        @temp = sort{$a<=>$b} @yrdata;
        $ytmin = $temp[0];
	$ytmax = $temp[$rdata_cnt -2];
	
        $n_cnt = 0;
        @xtrim = ();
        @ytrim = ();
#
#--- robust fit works better if the intercept is close to the
#--- middle of the data cluster. In this case, we just need to
#--- worry about time direction.
#
	OUTER:
        for($m = 0; $m < $rdata_cnt; $m++){
                $xt = $xrdata[$m] - $xtmin - 0.5;
                push(@xtrim, $xt);
                push(@ytrim, $yrdata[$m]);
                $n_cnt++;
        }
        @xrbin = @xtrim;
        @yrbin = @ytrim;
        $total = $n_cnt;
        medfit();

        $alpha +=  $beta * (-1.0 *  ($xtmin + 0.5));
#        $alpha +=  $beta * (-1.0 *  ($xmin + 0.5));
        $int   = sprintf "%2.4f",$alpha;
        $slope = sprintf "%2.4f",$beta;
}


####################################################################
### medfit: robust filt routine                                  ###
####################################################################

sub medfit{

#########################################################################
#                                                                       #
#       fit a straight line according to robust fit                     #
#       Numerical Recipes (FORTRAN version) p.544                       #
#                                                                       #
#       Input:          @xbin   independent variable                    #
#                       @ybin   dependent variable                      #
#                       total   # of data points                        #
#                                                                       #
#       Output:         alpha:  intercept                               #
#                       beta:   slope                                   #
#                                                                       #
#       sub:            rofunc evaluate SUM( x * sgn(y- a - b * x)      #
#                       sign   FORTRAN/C sign function                  #
#                                                                       #
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
                $xt[$j] = $xrbin[$j];
                $yt[$j] = $yrbin[$j];
                $sx  += $xrbin[$j];
                $sy  += $yrbin[$j];
                $sxy += $xrbin[$j] * $yrbin[$j];
                $sxx += $xrbin[$j] * $xrbin[$j];
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
                $diff   = $yrbin[$j] - ($aa + $bb * $xrbin[$j]);
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
                $arr[$j] = $yrbin[$j] - $b_in * $xrbin[$j];
        }
        @arr = sort{$a<=>$b} @arr;
        $aa = 0.5 * ($arr[$nml] + $arr[$nmh]);
        $sum = 0.0;
        $abdev = 0.0;
        for($j = 0; $j < $total; $j++){
                $d = $yrbin[$j] - ($b_in * $xrbin[$j] + $aa);
                $abdev += abs($d);
                $sum += $xrbin[$j] * sign(1.0, $d);
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

