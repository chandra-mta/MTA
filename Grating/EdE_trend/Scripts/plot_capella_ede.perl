#!/usr/bin/env /usr/local/bin/perl
use PGPLOT;

#########################################################################################################
#													#
#	plot_capella_ede.perl: plot EdE time evolution for a given data					#
#													#
#		author: t. isobe (tisobe@cfa.harvard.edu)						#
#													#
#		last update: May 27, 2015								#
#													#
#########################################################################################################

#$bin_dir = '/data/mta4/MTA/bin/';

#
# the data file must have the following data format
#
#obsid	 first line	 second line	 third line 	 fouth line 	 fifth line	 date			duration
#	  EdE	Error	 EdE	 Error	 EdE	 Error	 EdE	 Error	 EdE	 Error	
# -------------------------------------------------------------------------------------------------------------------------
#14240   209.3   4.5     126.3   5.2     268.3   7.8     214.1   12.6    130.8   8.8     2011-12-26T11:58:52     31498.3
#
# the name of the lines are give second input to fifth input. The last line is ignored.
#
#---- perl plot_capella_ede.perl acis_metg.dat  0.825 1.011 1.472 1.864
#---- perl plot_capella_ede.perl acis_hetg.dat  0.812 0.825 0.873 1.011
#---- perl plot_capella_ede.perl hrc_letg.dat   0.728 0.771 0.825 0.873

#
#--- save all data
#
$file   = $ARGV[0];		#---- data file name
$line1  = $ARGV[1];		#---- line names
$line2  = $ARGV[2];
$line3  = $ARGV[3];
$line4  = $ARGV[4];
$line5  = $ARGV[5];

#
#--- save all data points including 1999 data
#

@time1  = ();
@time2  = ();
@time3  = ();
@time4  = ();
@time5  = ();

@eline1 = ();
@eline2 = ();
@eline3 = ();
@eline4 = ();
@eline5 = ();

@error1 = ();
@error2 = ();
@error3 = ();
@error4 = ();
@error5 = ();

$cnt1  = 0;
$cnt2  = 0;
$cnt3  = 0;
$cnt4  = 0;
$cnt5  = 0;

#
#--- save data year > 1999
#

@timep1  = ();
@timep2  = ();
@timep3  = ();
@timep4  = ();
@timep5  = ();

@eline1p = ();
@eline2p = ();
@eline3p = ();
@eline4p = ();
@eline5p = ();

@error1p = ();
@error2p = ();
@error3p = ();
@error4p = ();
@error5p = ();

$cntp1 = 0;
$cntp2 = 0;
$cntp3 = 0;
$cntp4 = 0;
$cntp5 = 0;

#
#--- read the data
#

open(FH, "$file");
OUTER:
while(<FH>){
	chomp $_;
	@atemp = split(/\s+/, $_);
	$dom = ch_time_form_to_dom($atemp[11]);
#
#--- drop "na" entries
#
    if($atemp[1] != 'na'){
	    push(@time1,  $dom);
	    push(@eline1, $atemp[1]);
	    push(@error1, $atemp[2]);
        $cnt1++;
    }

    if($atemp[3] != 'na'){
	    push(@time2,  $dom);
	    push(@eline2, $atemp[3]);
	    push(@error2, $atemp[4]);
        $cnt2++;
    }

    if($atemp[5] != 'na'){
	    push(@time3,  $dom);
	    push(@eline3, $atemp[5]);
	    push(@error3, $atemp[6]);
        $cnt3++;
    }

    if($atemp[7] != 'na'){
	    push(@time4,  $dom);
	    push(@eline4, $atemp[7]);
	    push(@error4, $atemp[8]);
        $cnt4++;
    }

    if($atemp[9] != 'na'){
	    push(@time5,  $dom);
	    push(@eline5, $atemp[9]);
	    push(@error5, $atemp[10]);
        $cnt5++;
    }
	
#
#--- save data with year > 1999
#
	if($atemp[11] !~ /1999/){

		$dom = ch_time_form_to_dom($atemp[11]);
        if($atemp[1] != 'na'){
	        push(@time1p,  $dom);
	        push(@eline1p, $atemp[1]);
	        push(@error1p, $atemp[2]);
            $cnt1p++;
        }
    
        if($atemp[3] != 'na'){
	        push(@time2p,  $dom);
	        push(@eline2p, $atemp[3]);
	        push(@error2p, $atemp[4]);
            $cnt2p++;
        }
    
        if($atemp[5] != 'na'){
	        push(@time3p,  $dom);
	        push(@eline3p, $atemp[5]);
	        push(@error3p, $atemp[6]);
            $cnt3p++;
        }
    
        if($atemp[7] != 'na'){
	        push(@time4p,  $dom);
	        push(@eline4p, $atemp[7]);
	        push(@error4p, $atemp[8]);
            $cnt4p++;
        }
    
        if($atemp[9] != 'na'){
	        push(@time5p,  $dom);
	        push(@eline5p, $atemp[9]);
	        push(@error5p, $atemp[10]);
            $cnt5p++;
        }
	}
}
close(FH);

#
#---- plot start here
#

pgbegin(0, '"./pgplot.ps"/cps',1,1);
pgsubp(1, 1);
pgsch(1);
pgslw(4);

$tick = 0;			#--- plot option indicator

#
#--- set data point plotting  parameters
#

#
#--- find global min and max for the plotting area
#

@temp  = sort{$a<=>$b} @time1;
$xmin  = $temp[0];
$xmax  = $temp[$total-1];

@temp  = sort{$a<=>$b} @time2;
$xmint = $temp[0];
$xmaxt = $temp[$total-1];

if($xmint < $xmin){
    $xmin = $xmint;
}
if($xmaxt > $xmax){
    $xmax = $xmaxt;
}

@temp  = sort{$a<=>$b} @time3;
$xmint = $temp[0];
$xmaxt = $temp[$total-1];

if($xmint < $xmin){
    $xmin = $xmint;
}
if($xmaxt > $xmax){
    $xmax = $xmaxt;
}

@temp  = sort{$a<=>$b} @time4;
$xmint = $temp[0];
$xmaxt = $temp[$total-1];

if($xmint < $xmin){
    $xmin = $xmint;
}
if($xmaxt > $xmax){
    $xmax = $xmaxt;
}

@temp  = sort{$a<=>$b} @time5;
$xmint = $temp[0];
$xmaxt = $temp[$total-1];

if($xmint < $xmin){
    $xmin = $xmint;
}
if($xmaxt > $xmax){
    $xmax = $xmaxt;
}


$xdiff = $xmax - $xmin;
$xmin -= 0.1 * $xdiff;

if($xmin < 0){
	$xmin = 0;
}

$xmax += 0.1 * $xdiff;
$xdiff = $xmax - $xmin;
$xmid  = $xmin + 0.5 * $xdiff;
$xtxt  = $xmin + 0.1 * $xdiff;
$xbot  = $xmin - 0.07 * $xdiff;
		
#
#--- set data for line fitting (data with year > 1999)
#

pgsvp(0.1, 1.0, 0.77, 1.00);

@date = @time1;
$total= $cnt1;
@x    = @time1p;
$tot  = $cnt1p;
@data = @eline1;		#--- data point y
@err  = @error1;		#--- error of y

@y    = @eline1p;		#--- y for line fitting
@er   = @error1p;		#--- error for the line fitting

$energy = $line1;		#--- the name of the line

plot_data();			#--- plotting routine

pgsvp(0.1, 1.0, 0.53, 0.76);

@date = @time2;
$total= $cnt2;
@x    = @time2p;
$tot  = $cnt2p;
@data = @eline2;
@err  = @error2;

@y    = @eline2p;
@er   = @error2p;

$energy = $line2;

$tick = 1;			#--- it says to put y axis name on this panel

plot_data();
$tick = 0;

pgsvp(0.1, 1.0, 0.29, 0.52);

@date = @time3;
$total= $cnt3;
@x    = @time3p;
$tot  = $cnt3p;
@data = @eline3;
@err  = @error3;

@y    = @eline3p;
@er   = @error3p;

$energy = $line3;

plot_data();

pgsvp(0.1, 1.0, 0.05, 0.28);

@date = @time4;
$total= $cnt4;
@x    = @time4p;
$tot  = $cnt4p;
@data = @eline4;
@err  = @error4;

@y    = @eline4p;
@er   = @error4p;

$energy = $line4;

$tick = 2;			#--- it says to put date on x axis on this panel

plot_data();

pgptxt($xmid, $ybot, 0.0, 0.5, "Time (DOM)");

pgclos();

$out_plot = 'plot_lines.gif';

system("echo ''|gs -sDEVICE=ppmraw  -r256x256 -q -NOPAUSE -sOutputFile=-  ./pgplot.ps|pnmflip -r270 |ppmtogif > $out_plot");

system("rm -rf pgplot.ps");



##################################################################################
##################################################################################
##################################################################################

sub plot_data{

	@indata = @data;
	@yerr   = @err;
	@temp = sort{$a<=>$b} @indata;
	$ymin = $temp[0];
	$ymax = $temp[$total-1];
	$ydiff = $ymax - $ymin;
	$ymin -= 0.30 * $ydiff;

	if($ymin < 0){
        	$ymin = 0;
	}


	$ymax += 0.20 * $ydiff;
	$ydiff = $ymax - $ymin;
	$ytop  = $ymax - 0.1 * $ydiff;
	$ymid  = $ymin + 0.5 * $ydiff;
	$ybot  = $ymin - 0.2 * $ydiff;


	pgswin($xmin, $xmax, $ymin, $ymax);
	if($tick == 2){
		pgbox(ABCNST,0.0 , 0.0, ABCNSVT, 0.0, 0.0);
	}else{
		pgbox(ABCST,0.0 , 0.0, ABCNSVT, 0.0, 0.0);
	}

#
#---- plot two dim scattered diagram
#
	plot_fig();
	
#
#---- weighted linear least square fit
#
	@yerr   = @er;
	$ntot   = $tot;
	linfit();
	
	$yb = $s_int + $slope * $xmin;
	$yt = $s_int + $slope * $xmax;
	pgmove($xmin, $yb);
	pgsci(2);
	pgdraw($xmax, $yt);
	pgsci(1);
	
	$rslope = 1000 * $slope/365;
	$rslope = sprintf "%3.4f", $rslope;

	pgsci(3);
	pgptxt($xtxt, $ytop, 0.0, 0.0, "Line: $energy keV / Slope: $rslope (10**-3 EdE/year) ");
	pgsci(1);

##	pgptxt($xmid, $ybot, 0.0, 0.5, "Time (DOM)");

	if($tick == 1){
		pgptxt($xbot, $ymin, 90.0, 0.5, "E/dE");
	}
}


#########################################################################
### plot_fig: plotting scatttered diagram                             ###
#########################################################################

sub plot_fig{
        pgsch(2);
        for($j = 0; $j < $total; $j++){
                pgpt(1, $date[$j], $indata[$j], 3);
                $le = $indata[$j] - $yerr[$j];
                $lt = $indata[$j] + $yerr[$j];
                pgmove($date[$j], $le);
                pgdraw($date[$j], $lt);
        }
        pgsch(1);
}







###############################################################
###  ch_time_form_to_dom: changing time format  to dom   ######
###############################################################

sub ch_time_form_to_dom {

#############################################################################
#       Input: time: format is 2004-01-05T01:02:03 (from fits file header)
#                    called in:  ch_time_form_to_dom($time);
#
#       Output: acc_date: day of mission (less than a day added) returned
#
#       Sub:    conv_date_dom
#############################################################################

        my ($time, @atemp, $year, $month, $day);
        my ( @atemp, @btemp, $hr, $min, $sec, $hms, $acc_date);

        ($time) = @_;

        @atemp = split(/T/,$time);
        @btemp = split(/-/,$atemp[0]);

        $year  = $btemp[0];
        $month = $btemp[1];
        $day   = $btemp[2];

        $acc_date = conv_date_dom($year, $month, $day); #--- another format change

        @ctemp = split(/:/,$atemp[1]);
        $hr  = $ctemp[0]/24.0;
        $min = $ctemp[1]/1440.0;
        $sec = $ctemp[2]/86400.0;

        $hms = $hr + $min + $sec;

        $acc_date += $hms;
        return $acc_date;
}

###########################################################################
###      conv_date_dom: modify data/time format                       #####
###########################################################################

sub conv_date_dom {

#############################################################
#       Input:  $year: year in a format of 2004
#               $month: month in a formt of  5 or 05
#               $day:   day in a formant fo 5 05
#
#       Output: acc_date: day of mission returned
#############################################################

        my($year, $month, $day, $chk, $acc_date);

        ($year, $month, $day) = @_;

        $acc_date = ($year - 1999) * 365;

        if($year > 2000 ) {
                $acc_date++;
        }elsif($year >  2004 ) {
                $acc_date += 2;
        }elsif($year > 2008) {
                $acc_date += 3;
        }elsif($year > 2012) {
                $acc_date += 4;
        }elsif($year > 2016) {
                $acc_date += 5;
        }

        $acc_date += $day - 1;
        if ($month == 2) {
                $acc_date += 31;
        }elsif ($month == 3) {
                $chk = 4.0 * int(0.25 * $year);
                if($year == $chk) {
                        $acc_date += 59;
                }else{
                        $acc_date += 58;
                }
        }elsif ($month == 4) {
                $acc_date += 90;
        }elsif ($month == 5) {
                $acc_date += 120;
        }elsif ($month == 6) {
                $acc_date += 151;
        }elsif ($month == 7) {
                $acc_date += 181;
        }elsif ($month == 8) {
                $acc_date += 212;
        }elsif ($month == 9) {
                $acc_date += 243;
        }elsif ($month == 10) {
                $acc_date += 273;
        }elsif ($month == 11) {
                $acc_date += 304;
        }elsif ($month == 12) {
                $acc_date += 335;
        }
        $acc_date -= 202;
        return $acc_date;
}


###################################################################
### linfit: least sq. fitting  for a straight line with weight ####
###################################################################

sub linfit {

###########################################################
#  Input:       @x:       a list of independent variable
#               @y:       a list of dependent variable
#               @yerr:       a list of dependent variable errors
#               $ntot:      # of data points
#
#  Output:      $s_int:      intercept of the line
#               $slope:      slope of the line
#               $sigm_slope: the error on the slope
###########################################################

        my($sum, $sumx, $sumy, $symxy, $sumx2, $sumy2, $tot1);

        $sum   = 0;
        $sumx  = 0;
        $sumy  = 0;
        $sumxy = 0;
        $sumx2 = 0;
        $sumy2 = 0;

        for($fit_i = 0; $fit_i < $ntot; $fit_i++) {
                $sum   += $yerr[$fit_i];
                $sumx  += $yerr[$fit_i] * $x[$fit_i];
                $sumy  += $yerr[$fit_i] * $y[$fit_i];
                $sumx2 += $yerr[$fit_i] * $x[$fit_i] * $x[$fit_i];
                $sumy2 += $yerr[$fit_i] * $y[$fit_i] * $y[$fit_i];
                $sumxy += $yerr[$fit_i] * $x[$fit_i] * $y[$fit_i];
        }

        $delta = $sum * $sumx2 - $sumx * $sumx;
        $s_int = ($sumx2 * $sumy - $sumx * $sumxy)/$delta;
        $slope = ($sumxy * $sum  - $sumx * $sumy) /$delta;
        $pslope= sprintf "%3.4f", $slope;

        $tot1 = $ntot - 1;
        $variance = ($sumy2 + $s_int * $s_int * $sum + $slope * $slope * $sumx2
                        -2.0 *($s_int * $sumy + $slope * $sumxy
                        - $s_int * $slope * $sumx))/$tot1;
        $sigm_slope = sqrt($variance * $sum/$delta);
}

