#!/usr/bin/perl 

$file = $ARGV[0];
open(FH, $file);
while(<FH>){
    chomp $_;
    @atemp = split(/\s+/, $_);
    print "$atemp[0]\t";
    for($i = 1; $i < 5; $i++){
        $j =  2 * $i;
        print "$atemp[$j]\t";
    }
    print "\n";
}
close(FH);

