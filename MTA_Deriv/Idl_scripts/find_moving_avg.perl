#!/usr/bin/perl

#########################################################################################
#											#
#	find_moving_avg.perl: fit a moving average, a n-th degree polynomial,	 	#
#				  and an envelope to a given data (x, y)		#
#											#
#	USAGE:										#
#		perl find_moving_avg.perl <file name> <a period> <degree> <out file>	#
#					<option: -nodrop/-nodrop2/-nodrop3>		#
#											#
#		example 1: perl find_moving_avg.perl input_data 10 4 out_data		#
#				(if you want to drop outlayers)				#
#		example 2: perl find_moving_avg.perl input_data 10 4 out_data -nodrop	#
#				(if you want to use all the data to fit the line)	#
#											#
#	INPUT:										#
#		file name:	input data file name in (indepedent depedent) format	#
#				the x and y are separated by a space			#
#		a period:	a period for a moving average				#
#					take this so that each period has enough 	#
#					data points. if you take the period wider	#
#					the moving average get more smoother		#
#		degree:		a degree of polynomial fitting (<= 5 are probably safe)	#
#					if they are not enough data points, take lower	#
#					degree. otherwise, it may not give a good fit	#
#		out file	a name of output file name				#
#											#
#	OUTPUT:										#
#		out file	date (or indep. val) a date of the middle of the period	#
#				mvavg		     a moving average			#
#				sigma		     a standard deviation of the mvavg	#
#				bottom		     a polynomial fitted bottom envelop #
#				middle		     a polynomial fitted middle envelop	#
#				top		     a polynomial fitted top envelop	#
#				std_fit		     a polynomial fit for std		#
#				min_sv		     data used to compute bottom envlope#
#				max_sv		     data used to compute top envlope	#
#											#
#	Sub:										#
#		svdfit, svbksb, svdcmp, pythag, funcs, pol_val, robust_fit		#
#											#
#	Note:										#
#		To drop outlyers, this script uses two methods to exclude outlyers	#
#			* outside of 3 sigma from a straight fitted line to the data	#
#			  are dropped							#
#			* 0.5% of the lowest and 0.5% highest data are dropped		#
#		If you do not want to drop the data, then use the option		#
#			-nodrop:  both mechanisms are not used				#
#			-nodrop1: only 3 sigma method is used				#
#			-nodrop2: only 0.5% of both end will be dropped			#
#		If there is no option, it will use both to exclude outlyers		# 
#											#
#	author: t. isobe (tisobe@cfa.harvard.edu)					#
#											#
#	last update: 01/30/2008								#
#											#
#########################################################################################

my ($file, $arange, $nterm, @input, $incnt, $i, $avg, $std, $max, $min, $tot);
my ($dcnt, $npts, $nterms, $m, $yest, $xscale, $yscale, $dchk);
my ($outfile, $nodrop, $xsum, $ysum, $xs, $ys);
my (@input, @mvavg, @sigma, @max_sv, @min_sv, @time, @mdata, @x_pt, @y_pt);
my (@x_in, @y_in, @sorted_input);

$file   = $ARGV[0];		#---- input data file name
$arange = $ARGV[1];		#---- moving average period
$nterms = $ARGV[2];		#---- degree of polynomial fitting
$outfile= $ARGV[3];		#---- output file name
$nodrop = $ARGV[4];		#---- if this one is entired, all data will be used

chomp $file;
chomp $arange;
chomp $nterm;
chomp $outfile;
chomp $nodrop;
#
#-- small help for someone does not know...
#
if($file =~ /-h/i || $file eq ''){
	print 'USAGE:',"\n";
	print '        perl find_moving_avg.perl <file name> <a period> <degree> <out file> ',"\n";
	print '                                <option: -nodrop/-nodrop2/-nodrop3> ',"\n";           
	exit 1;
}

$dchk = 0;
if($nodrop     =~ /nodrop1/i){
	$dchk  = 1;
}elsif($nodrop =~ /nodrop2/i){
	$dchk  = 2;
}elsif($nodrop =~ /nodrop/i) {
	$dchk  = 3;
}

#
#--- read the data 
#
open(FH, "$file");
@input =();
$incnt = 0;
while(<FH>){
	chomp $_;
	push(@input, $_);
	$incnt++;
}
close(FH);
#
#--- sort the data, the smallest to the largest on date
#

@sorted_input = sort{$a<=>$b} @input;

@x_in = ();
@y_in = ();
$xsum = 0;
$ysum = 0;
foreach $line (@sorted_input){
	if($line =~ /\:/){
		@atemp = split(/\:/, $line);
	}elsif($line =~ /\,/){
		@atemp = split(/\,/, $line);
	}elsif($line =~ /\;/){
		@atemp = split(/\;/, $line);
	}elsif($line =~ /\//){
		@atemp = split(/\//, $line);
	}elsif($line =~ /\t/){
		@atemp = split(/\t+/, $line);
	}else{
		@atemp = split(/\s+/, $line);
	}
	push(@x_in, $atemp[0]);
	push(@y_in, $atemp[1]);
	$xsum += $atemp[0];
	$ysum += $atemp[1];
}
#
#--- to get the best polynomial fit, scale the data close to "1"
#
$xscale = abs($xsum/$incnt);
$yscale = abs($ysum/$incnt);
@x_tp   = ();
@y_tp   = ();
for($k = 0; $k < $incnt; $k++){
	$xs = $x_in[$k]/$xscale;
	push(@x_tp, $xs);
	$ys = $y_in[$k]/$yscale;
	push(@y_tp, $ys);
}
#
#--- a period also needs to be scaled.
#
$arange /= $xscale;

#
#--- a fit a straight line with robust method, then find how much deviations
#--- around the line. this informaiton will be use to drop extreme outlyers (>3 sigma)
#
@xdata    = @x_tp;
@ydata    = @y_tp;
$data_cnt = $incnt;

robust_fit();			#---  robust_fit method

for($i = 0; $i < $incnt; $i++){
	$diff = $y_tp[$i] -($int + $slope * $x_tp[$i]);
	$sum  += $diff;
	$sum2 += $diff * $diff;
}
$avg = $sum/$incnt;
$std = sqrt(abs($sum2/$incnt - $avg * $avg));

#
#--- set 3 sigma for the limit and drop outlyers
#

$olim  = 3.0 * $std;

#
#--- find out the top and bottom 0.5% values. this will be used to drop extreme outlayers
#
@ytemp  = sort{$a<=>$b} @y_tp;
$nlim   = int (0.005 * $incnt);
if($nlim < 1){
	$nlim = 1;
}
$ylower = $ytemp[$nlim];
$unlim  = $incnt - $nlim;
$yupper = $ytemp[$unlim];

@time  = ();
@mdata = ();
$dcnt  = ();
OUTER:
for($m = 0; $m < $incnt; $m++){

#
#---- check whether the data is in 3 sigma from a straight line fitted on the data
#
	if(($dchk == 0) || ($dchk == 1)){
		$diff = $y_tp[$m] -($int + $slope * $x_tp[$m]);
		if(abs($diff) > $olim){
			next OUTER;
		}
	}
#
#--- check whether the data point is in 0.5% of either lowest or highest data range
#
	if(($dchk == 0) || ($dchk == 2)){
		if($y_tp[$m] < $ylower || $y_tp[$m] > $yupper){
			next OUTER;
		}
	}

	push(@time,  $x_tp[$m]);
	push(@mdata, $y_tp[$m]);
	$dcnt++;
}

#
#--- find moving average
#

@date   = ();
@mvavg  = ();
@sigma  = ();
@max_sv = ();
@min_sv = ();
$tot    = 0;

$start = $time[0];
$end   = $start + $arange;
$sum   = 0;
$sum2  = 0;
$max   = -1.e+5;
$min   = 1.e+5;
$mcnt  = 0;
OUTER:
for($i = 0; $i < $dcnt; $i++){
	if($time[$i] >= $start && $time[$i] < $end){
		$sum  += $mdata[$i];
		$sum2 += $mdata[$i] * $mdata[$i];
		if($mdata[$i] > $max){
			$max = $mdata[$i];
		}
		if($mdata[$i] < $min){
			$min = $mdata[$i];
		}
		$mcnt++;
	}elsif($time[$i] <= $start){
		next OUTER;
	}elsif($time[$i] >=  $end){
		if($mcnt <= 0){
			$start = $end;
			$end   = $start + $arange;
			$sum  = 0;
			$sum2 = 0;
			$max  = -1.e+5;
			$min  = 1.e+5;
			$mcnt = 0;
			next OUTER;
		}

		$avg = $sum/$mcnt;
		$std = sqrt(abs($sum2/$mcnt - $avg * $avg));
		push(@mvavg,  $avg);
		push(@sigma,  $std);
		push(@max_sv, $max);
		push(@min_sv, $min);
		$mtime = 0.5 * ($start + $end);
		push(@date,   $mtime);
		$tot++;

		$start = $end;
		$end   = $start + $arange;
		$sum  = 0;
		$sum2 = 0;
		$max  = -1.e+5;
		$min  = 1.e+5;
		$mcnt = 0;
	}
}

if ($mcnt) { # add last partial bin
	$avg = $sum/$mcnt;
	$std = sqrt(abs($sum2/$mcnt - $avg * $avg));
	push(@mvavg,  $avg);
	push(@sigma,  $std);
	push(@max_sv, $max);
	push(@min_sv, $min);
	$mtime = 0.5 * ($start + $time[$i-1]);  # account for smaller bin 
	push(@date,   $mtime);
	$tot++;
}

#
#--- set a couple of parameters
#

$mode   = 0;
$npts   = $tot;
@bottom = ();
@middle = ();
@top    = ();
@std_fit= ();

#
#---- n-th degree polynomial fitting: bottom envelope
#

@x_in   = @date;
@y_in   = @min_sv;
svdfit($npts, $nterms);

for($m = 0; $m < $tot; $m++){
	$yest = pol_val($nterms, $date[$m]);
	push(@bottom, $yest);
}

#
#---- n-th degree polynomial fitting: top envelope
#

@x_in   = @date;
@y_in   = @max_sv;
svdfit($npts, $nterms);

for($m = 0; $m < $tot; $m++){
	$yest = pol_val($nterms, $date[$m]);
	push(@top, $yest);
}

#
#---- n-th degree polynomial fitting:  moving average
#

@x_in   = @date;
@y_in   = @mvavg;
svdfit($npts, $nterms);

for($m = 0; $m < $tot; $m++){
	$yest = pol_val($nterms, $date[$m]);
	push(@middle, $yest);
}
#
#---- n-th degree polynomila fitting: standard deviation
#

@x_in   = @date;
@y_in   = @sigma;
svdfit($npts, $nterms);

for($m = 0; $m < $tot; $m++){
	$yest = pol_val($nterms, $date[$m]);
	push(@std_fit, $yest);
}
#--- print out the final data
#
open(OUT, ">$outfile");
for($i = 0; $i < $tot; $i++){
#
#--- scale back all the data before printing them out
#
	$date[$i]    *= $xscale;
	$mvavg[$i]   *= $yscale;
	$sigma[$i]   *= $yscale;
	$bottom[$i]  *= $yscale;
	$middle[$i]  *= $yscale;
	$top[$i]     *= $yscale;
	$std_fit[$i] *= $yscale;
	$min_sv[$i]  *= $yscale;
	$max_sv[$i]  *= $yscale;

	print OUT "$date[$i]\t";
	print OUT "$mvavg[$i]\t";
	print OUT "$sigma[$i]\t";
	print OUT "$bottom[$i]\t";
	print OUT "$middle[$i]\t";
	print OUT "$top[$i]\t";
	print OUT "$std_fit[$i]\t";
	print OUT "$min_sv[$i]\t";
	print OUT "$max_sv[$i]\n";
}
close(FH);

########################################################################
###svdfit: polinomial line fit routine                               ###
########################################################################

######################################################################
#       Input:  @x_in: independent variable list
#               @y_in: dependent variable list
#               @sigmay: error in dependent variable
#               $npts: number of data points
#               $mode: mode of the data set mode = 0 is fine.
#               $nterms: polinomial dimention
#               input takes: svdfit($npts, $nterms);
#
#       Output: $a[$i]: coefficient of $i-th degree
#               $chisq: chi sq of the fit
#
#       Sub:    svbksb, svdcmp, pythag, funcs
#               where fun could be different (see at the bottom)
#
#       also see pol_val at the end of this file
#
######################################################################

sub svdfit{
#
#----- this code was taken from Numerical Recipes. the original is FORTRAN
#

        $tol = 1.e-5;

        my($ndata, $ma, @x, @y, @sig, @w, $i, $j, $tmp, $ma, $wmax, $sum, $diff);

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
        svdcmp($ndata, $ma);            ###### this also need $u[$i][$j] and $b[$i]
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

        svbksb($ndata, $ma);            ###### this also needs b, u, v, w. output is a[$j]
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
                for($jj = 1; $jj <= $n; $jj++){
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


######################################################################
### pol_val: compute a value for polinomial fit for  give coeffs   ###
######################################################################

sub pol_val{
###############################################################
#       Input: $a[$i]: polinomial parameters of i-th degree
#               $dim:  demension of the fit
#               $x:    dependent variable
#       Output: $out:  the value at $x
###############################################################
        my ($x, $dim, $i, $j, $out);
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
	@xldat = ();
	@yldat = ();
	for($n = 0; $n < $data_cnt; $n++){
		$xldat[$n] = $xdata[$n] - $xavg;
		$yldat[$n] = $ydata[$n] - $yavg;
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
#	Input:		@xldat	independent variable			#
#			@yldat	dependent variable			#
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
		$xt[$j] = $xldat[$j];
		$yt[$j] = $yldat[$j];
		$sx  += $xldat[$j];
		$sy  += $yldat[$j];
		$sxy += $xldat[$j] * $yldat[$j];
		$sxx += $xldat[$j] * $xldat[$j];
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
		$diff   = $yldat[$j] - ($aa + $bb * $xldat[$j]);
		$chisq += $diff * $diff;
	}
	$sigb = sqrt(abs($chisq/$del));
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
		$arr[$j] = $yldat[$j] - $b_in * $xldat[$j];
	}
	@arr = sort{$a<=>$b} @arr;
	$aa = 0.5 * ($arr[$nml] + $arr[$nmh]);
	$sum = 0.0;
	$abdev = 0.0;
	for($j = 0; $j < $total; $j++){
		$d = $yldat[$j] - ($b_in * $xldat[$j] + $aa);
		$abdev += abs($d);
		$sum += $xldat[$j] * sign(1.0, $d);
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
