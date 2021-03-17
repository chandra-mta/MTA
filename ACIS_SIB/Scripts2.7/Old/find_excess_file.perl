#/usr/bin/perl 

#################################################################################################
#												#
#	find_excess_file.perl: find lre data which exceed the critia 				#
#												#
#		author: t. isobe (tisobe@cfa.harvard.edu)					#
#												#
#		last update: Feb 11, 2010							#
#												#
#################################################################################################

$input =`ls /data/mta/Script/ACIS/SIB/Correct_excess/Outdir/lres/mtaf*fits`;
@list  = split(/\s+/, $input);

system("mkdir /data/mta/Script/ACIS/SIB/Correct_excess/Outdir/lres/Save");

open(OUT, "> sib_avg");
open(OUT2, "> sib_avg_excess");
foreach $ent (@list){
	system("dmlist $ent opt=data > zout");
	open(FH, "zout");
        $sum_ssoft   = 0;
        $sum_soft    = 0;
        $sum_med     = 0;
        $sum_hard    = 0;
        $sum_harder  = 0;
        $sum_hardest = 0;
	$cnt = 0;
	while(<FH>){
		chomp $_;
		@atemp = split(/\s+/, $_);
                $sum_ssoft   += $atemp[7];
                $sum_soft    += $atemp[8];
                $sum_med     += $atemp[9];
                $sum_hard    += $atemp[10];
                $sum_harder  += $atemp[11];
                $sum_hardest += $atemp[12];
		$cnt++;
	}
	close(FH);
	system("rm zout");
        $avg_ssoft   = $sum_ssoft/$cnt;
        $avg_soft    = $sum_soft/$cnt;
        $avg_med     = $sum_med/$cnt;
        $avg_hard    = $sum_hard/$cnt;
        $avg_harder  = $sum_harder/$cnt;
        $avg_hardest = $sum_hardest/$cnt;

        $avg_ssoft   = sprintf "%6.2f", $avg_ssoft;
        $avg_soft    = sprintf "%6.2f", $avg_soft;
        $avg_med     = sprintf "%6.2f", $avg_med;
        $avg_hard    = sprintf "%6.2f", $avg_hard;
        $avg_harder  = sprintf "%6.2f", $avg_harder;
        $avg_hardest = sprintf "%6.2f", $avg_hardest;

        print OUT  "$ent: $avg_ssoft\t";
        print OUT  "$avg_soft\t";
        print OUT  "$avg_med\t";
        print OUT  "$avg_hard\t";
        print OUT  "$avg_harder\t";
        print OUT  "$avg_hardest\n";


	if($avg_soft > 500 || ($avg_med > 150 && $ent !~ /acis6/) || ($avg_med > 200 && $ent =~ /acis6/)){
        	print OUT2  "$ent: $avg_ssoft\t";
        	print OUT2  "$avg_soft\t";
        	print OUT2  "$avg_med\t";
        	print OUT2  "$avg_hard\t";
        	print OUT2  "$avg_harder\t";
        	print OUT2  "$avg_hardest\n";
		system("mv $ent /data/mta/Script/ACIS/SIB/Correct_excess/Outdir/lres/Save/");
	}
}
close(OUT);
close(OUT2);
