#!/usr/bin/perl

#---------------------------------------------------------------------------
#
# prepare prep.perl output for input into mk_fp_avg.pro
#  (change date format)
#
#---------------------------------------------------------------------------

$year    = $ARGV[2];
$outfile = $ARGV[1];
$infile  = $ARGV[0];

open(FH, "$infile");
open(OUT,">$outfile");

#$year    =`date +%Y`;

while ($line=<FH>) {
    chomp $line;
    @input = split(" ",$line);
    @doy   = split(":",$input[1]);

    if ($#doy != 1) {next;} # something is wrong with the format, skip line

    $sec   = ($year - 1998) * 365 * 86400.00 + (($doy[0] - 1) * 86400.00) + $doy[1];
    $leap  = 2000;

    while ($year > $leap) {
        $sec += 86400.0;
        $leap = $leap + 4;
    }
    printf OUT "$sec";

    for ($i=2; $i<=$#input; $i++) {
        printf OUT "\t$input[$i]";
    }
    printf OUT "\n";
}
close(FH);
close(OUT);
