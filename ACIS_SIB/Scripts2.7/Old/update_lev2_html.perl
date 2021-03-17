#!/user/bin/perl
use PGPLOT;

#########################################################################################
#											#
#	"update_lev2_html.perl: update html page for Lev2 SIB Plots 		 	#
#											#
#	Author: T. Isobe (tisobe@cfa.harvard.edu)					#
#	Last Update: Mar 28, 2013							#
#											#
#########################################################################################


#######################################
#
#---- setting directories
#
$bin_dir  = '/data/mta/MTA/bin/';
$data_dir = '/data/mta/MTA/data/';
$web_dir  = '/data/mta/www/mta_sib/';

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
conv_no_ch_month();		# change month format to e.g. 1 to Jan

$amonth = $month;
if($amonth < 10){
	$amonth = '0'."$amonth";
}

print_main();	

print_img_html();	

print_long_html();

print_past_year_html();


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
	
	$start += $acc_date;
	$start --;
	$start *= 86400;
	$end   += $acc_date;
	$end   *= 86400;
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
        if($tyear == 2000 || $tyear == 2004 || $tyear == 2008 || $tyear == 2012){
                if($tmonth > 2){
                        $dom++;
                }
        }

        $dom = $dom + $acc_date + $tday - 202;
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
	
###################################################################
### print_main: create sib main html page                       ###
###################################################################

sub print_main{

	open(OUT, ">$web_dir/sib_main_lev2.html");
	print OUT '<html>',"\n";
	print OUT '<head><title>SIB'," $cmonth $uyear",'</title></head>',"\n";
	print OUT '<body TEXT="#000000" BGCOLOR="#FFFFFF">',"\n";
	print OUT '<center>',"\n";
	print OUT '<h2>MTA Science Instrument Background Report: ACIS';
	print OUT " $cmonth $uyear",'(Level 2 Data) </h2>',"\n";

	find_today_dom();
	$hyday++;               # hyday starts from day 0 in localtime(time) function

	print OUT '<H3>Updated  on: ';
	print OUT "$hyear-$month-$hmday  / ";
	print OUT "DAY OF YEAR: $hyday  / ";
	print OUT "DAY OF MISSION: $dom ";
	print OUT '</H3>';


	$year_begin = 1999;
	$month_begin = 9;
	$diff = $uyear - $year_begin;
	@year_list =();
	@month_list = ();
	$icnt = 0;
	for($j = 0; $j <= $diff; $j++){
		if($j == 0){
			for($km = $month_begin; $km <= 12; $km++){
				if($km< 10){
                                        @atemp = split(//, $km);
                                        if(@atemp[0] != 0){
                                                $km = '0'."$km";
                                        }
				}
				push(@year_list, $year_begin);
				push(@month_list, $km);
				$icnt++;
			}
		}elsif($j == $diff){
			for($km = 1; $km <= $month; $km++){
				if($km < 10){
                                        @atemp = split(//, $km);
                                        if(@atemp[0] != 0){
                                                $km = '0'."$km";
                                        }
				}
				$dir_year = $year_begin + $j;
				push(@year_list, $dir_year);
				push(@month_list, $km);
				$icnt++;
			}
		}else{
			for($km = 1; $km <= 12; $km++){
				if($km < 10){
                                        @atemp = split(//, $km);
                                        if(@atemp[0] != 0){
                                                $km = '0'."$km";
                                        }
				}
				$dir_year = $year_begin + $j;
				push(@year_list, $dir_year);
				push(@month_list, $km);
				$icnt++;
			}
		}
	}

	print OUT '<img src ="./Lev2/Plots/Plot_long/long_total_data_ccd6.gif" width=80%>',"\n";
	print OUT '<br>',"\n";

	print OUT '<img src ="./Lev2/Plots/comb_plot.gif" width=85% >',"\n";
	print OUT '<br>',"\n";

	print OUT '</center><P>',"\n";
	print OUT 'This page shows scientific instrument background data based on Acis observations, ',"\n";
	print OUT 'based on Level 2 data. ',"\n";
	print OUT 'A source region file is generated using get_srcregions and then the input',"\n";
	print OUT 'event file is filtered using the regions in that file to remove the sources.',"\n";
	print OUT 'Details on these tools can be using ahelp.',"\n";
	print OUT '</P><P>',"\n";
	print OUT 'The plot above is data of the background photon count rates of the entire energy range',"\n";
	print OUT 'of ccd6 from Sept 1999 to this week.',"\n";
	print OUT '</P><P>',"\n";
	print OUT 'If you select a ccd from the table below, it brings up seven plots of that month.',"\n";
	print OUT 'The top plot is for the entire energy range. Smaller plots are for super soft, soft,',"\n";
	print OUT 'moderate, hard, very hard, and beyond 10 KeV.',"\n";
        print OUT '</P><P>',"\n";
        print OUT 'Before computing SIB, most extended sources, such as clusters of galaxies, ',"\n";
        print OUT ' were removed manually to avoid confusion. All point sources were removed ',"\n";
        print OUT 'automatically by scripts.',"\n";
        print OUT '(NOTE: extended sources were currently removed only for 2003, and 2004.)',"\n";
        print OUT '</P><P>',"\n";
        print OUT 'The fitted line for the entire period is 4th order polynomials, and it is extended ',"\n";
        print OUT 'to two years beyond the current time to show a possible SIB level in future.',"\n";
        print OUT 'For all others, the fitted line is a linear, and for one year plots, the line ',"\n";
        print OUT 'is extended 6 months beyond the current date.',"\n";
        print OUT '</P><P>',"\n";
	print OUT '</P><P>',"\n";
	print OUT 'If you are interested in checking the scientific instrument background ',"\n";
	print OUT 'computed with Level 1 data set, please to go to ',"\n";
	print OUT "<a href='https://cxc.cfa.harvard.edu/mta_days/mta_sib/sib_main.html'>";
	print OUT 'level 1 SIB page</a>.',"\n";
	print OUT '</P><P>',"\n";
	print OUT '</P><center>';
	print OUT "\n";

	print OUT '<br><br>',"\n";
	print OUT '<table border = 1 cellspacing = 1 cellpadding = 3>',"\n";
	print OUT '<tr><th>Name   </th><th>Low (keV)</th><th>Hight(KeV)</th><th>Description            </th></tr>',"\n";
	print OUT '<tr><th>SSoft  </th><td> 0.00    </td><td>  0.50    </td><td>Super soft photons     </td></tr>',"\n";
	print OUT '<tr><th>Soft   </th><td> 0.50    </td><td>  1.00    </td><td>Soft photons           </td></tr>',"\n";
	print OUT '<tr><th>Med    </th><td> 1.00    </td><td>  3.00    </td><td>Moderate energy photons</td></tr>',"\n";
	print OUT '<tr><th>Hard   </th><td> 3.00    </td><td>  5.00    </td><td>Hard Photons           </td></tr>',"\n";
	print OUT '<tr><th>Harder </th><td> 5.00    </td><td> 10.00    </td><td>Very Hard photons      </td></tr>',"\n";
	print OUT '<tr><th>Hardest</th><td>10.00    </td><td> &#160    </td><td>Beyond 10 keV          </td></tr>',"\n";
	print OUT '</table>',"\n";
	print OUT '<br><br>',"\n";


	print OUT '<table border = 1 cellspacing = 1 cellpadding = 5>',"\n";

        print OUT '<tr>';
        print OUT '<th>',"Entire Period",'</th>';

        print OUT '<td><a href = "',"./Lev2/Plots/Plot_long",'/long_ccd0.html">CCD0</a></td>',"\n";
        print OUT '<td><a href = "',"./Lev2/Plots/Plot_long",'/long_ccd1.html">CCD1</a></td>',"\n";
        print OUT '<td><a href = "',"./Lev2/Plots/Plot_long",'/long_ccd2.html">CCD2</a></td>',"\n";
        print OUT '<td><a href = "',"./Lev2/Plots/Plot_long",'/long_ccd3.html">CCD3</a></td>',"\n";
        print OUT '<td><a href = "',"./Lev2/Plots/Plot_long",'/long_ccd4.html">CCD4</a></td>',"\n";
        print OUT '<td><a href = "',"./Lev2/Plots/Plot_long",'/long_ccd5.html">CCD5</a></td>',"\n";
        print OUT '<td><a href = "',"./Lev2/Plots/Plot_long",'/long_ccd6.html">CCD6</a></td>',"\n";
        print OUT '<td><a href = "',"./Lev2/Plots/Plot_long",'/long_ccd7.html">CCD7</a></td>',"\n";
        print OUT '<td><a href = "',"./Lev2/Plots/Plot_long",'/long_ccd8.html">CCD8</a></td>',"\n";
        print OUT '<td><a href = "',"./Lev2/Plots/Plot_long",'/long_ccd9.html">CCD9</a></td>',"\n";
        print OUT '</tr>';

        print OUT '<tr>';
        print OUT '<th>',"Past One Year",'</th>';

        print OUT '<td><a href = "',"./Lev2/Plots/Plot_past_year",'/long_ccd0.html">CCD0</a></td>',"\n";
        print OUT '<td><a href = "',"./Lev2/Plots/Plot_past_year",'/long_ccd1.html">CCD1</a></td>',"\n";
        print OUT '<td><a href = "',"./Lev2/Plots/Plot_past_year",'/long_ccd2.html">CCD2</a></td>',"\n";
        print OUT '<td><a href = "',"./Lev2/Plots/Plot_past_year",'/long_ccd3.html">CCD3</a></td>',"\n";
        print OUT '<td><a href = "',"./Lev2/Plots/Plot_past_year",'/long_ccd4.html">CCD4</a></td>',"\n";
        print OUT '<td><a href = "',"./Lev2/Plots/Plot_past_year",'/long_ccd5.html">CCD5</a></td>',"\n";
        print OUT '<td><a href = "',"./Lev2/Plots/Plot_past_year",'/long_ccd6.html">CCD6</a></td>',"\n";
        print OUT '<td><a href = "',"./Lev2/Plots/Plot_past_year",'/long_ccd7.html">CCD7</a></td>',"\n";
        print OUT '<td><a href = "',"./Lev2/Plots/Plot_past_year",'/long_ccd8.html">CCD8</a></td>',"\n";
        print OUT '<td><a href = "',"./Lev2/Plots/Plot_past_year",'/long_ccd9.html">CCD9</a></td>',"\n";
        print OUT '</tr>';

#
#----- Plot every month for this year
#

        OUTER:
        for($i = $icnt -1; $i > -1; $i--){
                if($year_list[$i] != $year_list[$icnt-1]){
                        last OUTER;
                }
                $out_dir = './Lev2/Plots/Plots_'."$year_list[$icnt-1]"."_$month_list[$i]";

                $temp_month = $month_list[$i];
                conv_no_ch_month();

                print OUT '<tr>';
                print OUT '<th>',"$cmonth $year_list[$i]",'</th>';

                print OUT '<td><a href = "',"$out_dir",'/ccd0.html">CCD0</a></td>',"\n";
                print OUT '<td><a href = "',"$out_dir",'/ccd1.html">CCD1</a></td>',"\n";
                print OUT '<td><a href = "',"$out_dir",'/ccd2.html">CCD2</a></td>',"\n";
                print OUT '<td><a href = "',"$out_dir",'/ccd3.html">CCD3</a></td>',"\n";
                print OUT '<td><a href = "',"$out_dir",'/ccd4.html">CCD4</a></td>',"\n";
                print OUT '<td><a href = "',"$out_dir",'/ccd5.html">CCD5</a></td>',"\n";
                print OUT '<td><a href = "',"$out_dir",'/ccd6.html">CCD6</a></td>',"\n";
                print OUT '<td><a href = "',"$out_dir",'/ccd7.html">CCD7</a></td>',"\n";
                print OUT '<td><a href = "',"$out_dir",'/ccd8.html">CCD8</a></td>',"\n";
                print OUT '<td><a href = "',"$out_dir",'/ccd9.html">CCD9</a></td>',"\n";
                print OUT '</tr>';

        }
#
#----- Plot only a year long plot for the all previous years
#
####	$y_last = $year_list[$icnt -2] -1;
	$y_last = $year_list[$icnt -2];
#        for($i = $y_last; $i >= $year_list[0] ; $i--){
#        for($i = $y_last; $i > 1999 ; $i--){
	$start_year = $uyear -1;
        for($i = $start_year; $i > 1999 ; $i--){
                $out_dir = './Lev2/Plots/Plot_year_'."$i";

                print OUT '<tr>';
                print OUT '<th>',"$i",'</th>';

                print OUT '<td><a href = "',"$out_dir",'/long_ccd0.html">CCD0</a></td>',"\n";
                print OUT '<td><a href = "',"$out_dir",'/long_ccd1.html">CCD1</a></td>',"\n";
                print OUT '<td><a href = "',"$out_dir",'/long_ccd2.html">CCD2</a></td>',"\n";
                print OUT '<td><a href = "',"$out_dir",'/long_ccd3.html">CCD3</a></td>',"\n";
                print OUT '<td><a href = "',"$out_dir",'/long_ccd4.html">CCD4</a></td>',"\n";
                print OUT '<td><a href = "',"$out_dir",'/long_ccd5.html">CCD5</a></td>',"\n";
                print OUT '<td><a href = "',"$out_dir",'/long_ccd6.html">CCD6</a></td>',"\n";
                print OUT '<td><a href = "',"$out_dir",'/long_ccd7.html">CCD7</a></td>',"\n";
                print OUT '<td><a href = "',"$out_dir",'/long_ccd8.html">CCD8</a></td>',"\n";
                print OUT '<td><a href = "',"$out_dir",'/long_ccd9.html">CCD9</a></td>',"\n";
                print OUT '</tr>';
        }



	print OUT '</table>',"\n";
	close(OUT);
}

###################################################################
### print_img_html: create a html page for ecah ccd             ###
###################################################################

sub print_img_html{

	for($iccd = 0; $iccd < 10; $iccd++){
		$file = 'ccd'."$iccd".'.html';
		open(OUT, ">$web_dir/Lev2/Plots/$this_month/$file"),"\n";

		print OUT '<html>',"\n";
		print OUT '<head><title>CCD',"$iccd",' plot</title></head>',"\n";
		print OUT '<body TEXT="#000000" BGCOLOR="#FFFFFF">',"\n";
		print OUT '<h2>CCD ',"$iccd",' SIB </h2>',"\n";
		print OUT '<center>',"\n";
		print OUT '<img src ="./total_data_ccd',"$iccd",'.gif", width = 80% >',"\n";
		print OUT "\n","\n";
		print OUT '<hr>',"\n";
		print OUT '<img src ="./indep_plot_ccd',"$iccd",'.gif", width = 100% height = 100%>',"\n";
		print OUT '</center>',"\n";
		print OUT '<body>',"\n";
		print OUT '</html>',"\n";
	}
	close(OUT);
}


###################################################################
### print_long_html: print a html page for long term plots      ###
###################################################################

sub print_long_html{

        for($iccd = 0; $iccd < 10; $iccd++){
                $file = 'long_ccd'."$iccd".'.html';
                open(OUT, ">$web_dir/Lev2/Plots/Plot_long/$file"),"\n";

                print OUT '<html>',"\n";
                print OUT '<head><title>CCD',"$iccd",' plot</title></head>',"\n";
                print OUT '<body TEXT="#000000" BGCOLOR="#FFFFFF">',"\n";
                print OUT '<h2>CCD ',"$iccd",' SIB </h2>',"\n";
                print OUT '<center>',"\n";
                print OUT '<img src ="./long_total_data_ccd',"$iccd",'.gif", width=80%>',"\n";
                print OUT '\n',"\n";
                print OUT '<hr>',"\n";
                print OUT '<img src ="./long_indep_plot_ccd',"$iccd",'.gif", width = 100% height = 100%>',"\n";
                print OUT '</center>',"\n";
                print OUT '<body>',"\n";
                print OUT '</html>',"\n";
        }
        close(OUT);
}

#######################################################################
### print_past_year_html: print a html page for past yearplots      ###
#######################################################################

sub print_past_year_html{

        for($iccd = 0; $iccd < 10; $iccd++){
                $file = 'long_ccd'."$iccd".'.html';
                open(OUT, ">$web_dir/Lev2/Plots/Plot_past_year/$file"),"\n";

                print OUT '<html>',"\n";
                print OUT '<head><title>CCD',"$iccd",' plot</title></head>',"\n";
                print OUT '<body TEXT="#000000" BGCOLOR="#FFFFFF">',"\n";
                print OUT '<h2>CCD ',"$iccd",' SIB </h2>',"\n";
                print OUT '<center>',"\n";
                print OUT '<img src ="./long_total_data_ccd',"$iccd",'.gif", width=80%>',"\n";
                print OUT '\n',"\n";
                print OUT '<hr>',"\n";
                print OUT '<img src ="./long_indep_plot_ccd',"$iccd",'.gif", width = 100% height = 100%>',"\n";
                print OUT '</center>',"\n";
                print OUT '<body>',"\n";
                print OUT '</html>',"\n";
        }
        close(OUT);
}

################################################################
### today_dom: find today dom                               ####
################################################################

sub find_today_dom{

        ($hsec, $hmin, $hhour, $hmday, $hmon, $hyear, $hwday, $hyday, $hisdst)= localtime(time);

        if($hyear < 1900) {
                $hyear = 1900 + $hyear;
        }
        $month = $hmon + 1;
        #$hyday++;

        if ($hyear == 1999) {
                $dom = $hyday - 202 + 1;
        }elsif($hyear >= 2000){
                $dom = $hyday + 163 + 1 + 365*($hyear - 2000);
                if($hyear > 2000) {
                        $dom++;
                }
                if($hyear > 2004) {
                        $dom++;
                }
                if($hyear > 2008) {
                        $dom++;
                }
                if($hyear > 2012) {
                        $dom++;
                }
        }
}
