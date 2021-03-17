#!/usr/bin/perl 

$dir = $ARGV[0];

foreach $elm ('al', 'mn', 'ti'){
    for($ccd = 0; $ccd < 10; $ccd++){
        $file = "$dir/$elm".'_ccd'."$ccd";
        if($dir =~ /Det/){
            if($ccd == 5){
                next;
            }elsif($ccd == 7){
                next;
            }
        }

        open(FH, $file);
        $sum0 = 0;
        $sum1 = 0;
        $sum2 = 0;
        $sum3 = 0;
        $tot  = 0;
        while(<FH>){
            chomp $_;
            @atemp = split(/\s+/, $_);
            @btemp = split(/-/, $atemp[0]);
            if($btemp[0] > 2012){
                last;
            }
            @ctemp = split(/\+\-/, $atemp[1]);
            if($ctemp[0] > 0){
                $sum0 += $ctemp[0];
            }
            @ctemp = split(/\+\-/, $atemp[2]);
            if($ctemp[0] > 0){
                $sum1 += $ctemp[0];
            }
            @ctemp = split(/\+\-/, $atemp[3]);
            if($ctemp[0] > 0){
                $sum2 += $ctemp[0];
            }
            @ctemp = split(/\+\-/, $atemp[4]);
            if($ctemp[0] > 0){
                $sum3 += $ctemp[0];
            }
            $tot++;
        }
        close(FH);
        $sum0 /= $tot;
        $sum1 /= $tot;
        $sum2 /= $tot;
        $sum3 /= $tot;

        printf "%4.3f\t%4.3f\t%4.3f\t%4.3f\n", $sum0, $sum1, $sum2, $sum3;
    }
    print "\n\n";
}


