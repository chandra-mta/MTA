#!/usr/bin/perl 

$pi = 3.141592;

$file = $ARGV[0];
open(FH, "$file");
$sum = ();
while(<FH>){
	chomp $_;
	@atemp = split(/\,/, $_);
	$area  = $pi * $atemp[3] * $atemp[3];
	$sum  += $area;
}
close(FH);

$total = 1021 * 1021;
$ratio = $sum/$total;

print "$ratio\n";
	
