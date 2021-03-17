#!/usr/bin/perl

use List::Util qw[min max];

#################################################################################################
#                                                                                               #
#               average.pl --- one day resolution                                               #
#                                                                                               #
#               author: ????                                                                    #
#               maintained by:  t. isobe (tisobe@cfa.harvard.edu)                               #
#               last update: Oct 24, 2017                                                       #
#                                                                                               #
#################################################################################################

$verbose    = 0;
$infile;
$outfile;
$resolution = 86400.0;
$reftime    = 126228000-(300*12*24*2000); 
$step_size  = $resolution;

#
#--- Parse input arguments
#
&parse_args;

if ($verbose >= 2) {
    print "$0 args:\n";
    print "\tinfile:\t\t$infile\n";
    print "\toutfile:\t\t$outfile\n";
    print "\tresolution:\t\t$resolution\n";
    print "\tverbose:\t\t$verbose\n";
}  

my @datfiles;
my $datfile;
my $counter;

if ($infile =~ /^\@/) {
    $infile = substr($infile, 1);

    my @patharr = split("/", $infile);
    my $path = "";
    
    for ($ii = 0; $ii < $#patharr; $ii++) {
	    $path .= "/$patharr[$ii]";
    }

    open infile;
    
    $counter = 0;
    while($datfile = <infile>) {
	    chomp $datfile;
	    $datfiles[$counter++] = $path . $datfile;
    }
}
else {
    $datfiles[0] = $infile;
}

open OUTFILE, ">>$outfile";

my $in;
my @inline;
my @inarr;
my @totarr;
my @tmparr;
my $lasttime=0;
my $nelm = 0;

foreach $file (@datfiles) {
    open datfile, "$file" or die;
    
    $inline = <datfile>;
    chomp $in;
    
    @inline = split ("\t", $in);
#    
#--- remove whitespace line
#
    $preline = <datfile>;
    if (! $lasttime) { 
#
#--- start first line
#
      $inline = <datfile>;
      chomp $inline;
      @totarr = split ("\t", $inline);
      
      @tmparr = [0,@totarr];
      $lasttime=$totarr[0];
      $nelm = $nelm + 1;
    }
    
    while ($inline = <datfile>) {
	    chomp $inline;
	    @inarr = split ("\t", $inline);
    	
	    if ($inarr[0] - $lasttime <= $resolution) {
                for ($ii = 0; $ii <= $#inarr; $ii++) {
                    @totarr[$ii] = $totarr[$ii] + $inarr[$ii];
                    push(@tmparr, @inarr);
                }
                $nelm = $nelm + 1;
                next;
	    } else {
            if ($nelm gt 0) {
                $avg = $totarr[0]/$nelm;
                if ($avg lt $reftime) {
                    $avg=$reftime;
                }
                while ($avg >= $reftime+$step_size) {
                    $reftime=$reftime+$step_size;
                }
                if ($avg < $reftime) {next;}
                $tdiff=$avg - $reftime;
                if ($tdiff >= 0 && $tdiff < $step_size) {
                    #printf OUTFILE "%.8e\t%d",$reftime,$nelm;
                    printf OUTFILE "%.8e",$reftime;
                    $reftime=$reftime+$step_size;
     
                    @selected = ();
                    for ($ii = 1; $ii <= $#inarr; $ii++) {
                        $avg = $totarr[$ii]/$nelm;
                        $tot = 0;
                        for ($jj = $ii+1; $jj < $#tmparr; $jj += $#inarr+1) {
                            $tot = $tot + ($tmparr[$jj]-$avg)**2;
                            if($tmparr[$jj] > -100 && $tmparr[$jj] < 100){
                                push(@selected, $tmparr[$jj]);
                            }
                        }
                        $amed = median(@selected);
                        $amin = min(@selected);
                        $amax = max(@selected);
                        $sd   = sqrt($tot/$nelm);
                        printf OUTFILE "\t%.4f\t%.4f\t%.5f\t%.4f\t%.4f",$avg, $amed, $sd, $amin, $amax;
                    }
                    print OUTFILE "\n";
                } 
            } 
            $lasttime = $inarr[0];
            $nelm=0;
            @totarr = 0;
            @tmparr = 0;
            $avg=0;
	    }
	
    } 

    close datfile;
}

close OUTFILE;

#------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------

sub parse_args {
    my $infile_found     = 0;
    my $outfile_found    = 0;
    my $resolution_found = 0;

    
    for ($ii = 0; $ii <= $#ARGV; $ii++) {
	    if (!($ARGV[$ii] =~ /^-/)) {
	        next;
	    }

	    if ($ARGV[$ii] =~ /^-i/) {
	        $infile_found = 1;
	        if ($ARGV[$ii] =~ /^-i$/) {
		        $ii++;
		        $infile = $ARGV[$ii];	    
	        } else {
		        $infile = substr($ARGV[$ii], 2);
	        }	    
	    } 
    
	    if ($ARGV[$ii] =~ /^-o/) {
	        $outfile_found = 1;
	        if ($ARGV[$ii] =~ /^-o$/) {
		        $ii++;
		        $outfile = $ARGV[$ii];	    
	        } else {
		        $outfile = substr($ARGV[$ii], 2);
	        }
	    } 
        if ($ARGV[$ii] =~ /^-v/) {
            $verbose_found = 1;
            if ($ARGV[$ii] =~ /^-v$/) {
                $ii++;
                $verbose = $ARGV[$ii];
            } else {
                $verbose = substr($ARGV[$ii], 2);
            }

        } 

        if ($ARGV[$ii] =~ /^-r/) {
            $resolution_found = 1;
            if ($ARGV[$ii] =~ /^-r$/) {
                $ii++;
                $resolution = $ARGV[$ii];
            } else {
                $resolution = substr($ARGV[$ii], 2);
            }

        } 
        if ($ARGV[$ii] =~ /^-h/) {
            goto USAGE;
        } 
    } 

    if (!$infile_found || !$outfile_found) {
	    goto USAGE;
    }

    return;

  USAGE:
    print "Usage:\n\t$0 -i<infile> -o<outfile> [-r<resolution>] " .
	"[-v<verbose>]\n";
    exit (0);
}

#------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------

sub convert_time {
    my @yrday    = split(' ', $_[0]);
    my $year     = $yrday[0];
    my $day      = $yrday[1];
    
    my @hrminsec = split(':', ($yrday[2] . $yrday[3]));
    my $hour     = $hrminsec[0];
    my $min      = $hrminsec[1];
    my $sec      = $hrminsec[2];

    my $totsecs  = 0;
    $totsecs     = $sec;
    $totsecs    += $min  * 60;
    $totsecs    += $hour * 3600;

    my $totdays  = 0;
    my $totdays  = $day - 1;

    if ($year >= 98) {
	    $year = 1998 + ($year - 98);
    } else {
	    $year = 2000 + $year;
    }
#
#---- add days for past leap years
#
    if ($year > 2000) {
#
#--- add one for y2k
#
	    $totdays++;
#
#--- Number of years since 2000. -1 for already counted current leap
#
	    $years    = $year - 2000 - 1;
	    $leaps    = int ($years / 4);
	    $totdays += $leaps;
    }
    
    $totdays += ($year - 1998) * 365;

    $totsecs += $totdays * 86400;

    return $totsecs;
}

#------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------

sub quat_to_euler
{
    use Math::Trig;
    my @quat = @_;
    $RAD_PER_DEGREE = pi / 180.0;
    
    my $q1  = $quat[0];
    my $q2  = $quat[1];
    my $q3  = $quat[2];
    my $q4  = $quat[3];
    
    my $q12 = 2.0 * $q1 * $q1;
    my $q22 = 2.0 * $q2 * $q2;
    my $q32 = 2.0 * $q3 * $q3;
    
    my @T = (
	     [ 1.0 - $q22 - $q32, 2.0 * ($q1 * $q2 + $q3 * $q4), 2.0 * ($q3 * $q1 - $q2 * $q4) ],
	     [ 2.0 * ($q1 * $q2 - $q3 * $q4), 1.0 - $q32 - $q12,  2 * ($q2 * $q3 + $q4 * $q1) ],
	     [ 2.0 * ($q3 * $q1 + $q2 * $q4), 2.0 * ($q2 * $q3 - $q1 * $q4), 1.0 - $q12 - $q22 ]
	     );


    my %eci;

    $eci{ra}   = atan2($T[0][1], $T[0][0]);
    $eci{dec}  = atan2($T[0][2], sqrt($T[0][0] * $T[0][0] + $T[0][1] * $T[0][1]));
    $eci{roll} = atan2($T[2][0] * sin($eci{ra}) - $T[2][1] * cos($eci{ra}), -$T[1][0] * sin($eci{ra}) + $T[1][1] * cos($eci{ra}));
    

    $eci{ra}   /= $RAD_PER_DEGREE;
    $eci{dec}  /= $RAD_PER_DEGREE;
    $eci{roll} /= $RAD_PER_DEGREE;

    if ($eci{ra}   < 0.0)  {
	    $eci{ra} += 360.0;
    }
    if ($eci{roll} < -1e-13) {
        print hello;
	    $eci{roll} += 360.0;
    }
    if ($eci{dec}  < -90.0 || $eci{dec} > 90.0) {
	    print "Ugh dec $eci{dec}\n";
    }

    return (%eci);
}

#------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------

sub median
{
    my @vals = sort {$a <=> $b} @_;
    my $vlen = @vals;
    
    if($vlen%2) {
        return $vals[int($vlen/2)];
    
    } else {
        return ($vals[int($vlen/2)-1] + $vals[int($vlen/2)])/2;
    }
}

