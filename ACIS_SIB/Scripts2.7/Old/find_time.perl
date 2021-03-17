#!/usr/bin/perl

#########################################################################################
#											#
#	find_time.perl: create a list of time of observation from Input/acis*fits	#
#											#
#		author: t. isobe (tisobe@cfa.harvard.edu)				#
#											#
#		last update: Mar 27, 2007						#
#											#
#########################################################################################

$in_list = `ls Input/acis*fits`;
@list = split(/\s+/, $in_list);

@save = ();
OUTER:
foreach $ent (@list){
	system("dmlist $ent opt=head > zout");
	open(FH, "./zout");
	$tb_chk = 0;
	$te_chk = 0;
	while(<FH>){
		chomp $_;
		@atemp = split(/\s+/, $_);
		if($_ =~ /DATE-OBS/i){
			$start = $atemp[2];
		}elsif($_ =~ /DATE-END/i){
			$end   = $atemp[2];
		}elsif($_ =~ /TSTART/i){
			if($tb_chk == 0){
				$tstart = $atemp[2];
				$tstart2 = `axTime3 $tstart u s t d`;
				$tb_chk++;
			}
		}elsif($_ =~ /TSTOP/i){
			if($te_chk == 0){
				$tstop   = $atemp[2];
				$tstop2  = `axTime3 $tstop u s t d`;
				$te_chk++;
			}
		}
	}
	$ent =~s/Input\/acisf0//;
	@btemp = split(/N/, $ent);
	$obsid = $btemp[0];
	@ctemp = split(/\./, $tstart);
	@dtemp = split(/\./, $tstop);
	$line = "$ctemp[0]\t$dtemp[0]\t$tstart2\t$tstop2\t$obsid";
	push(@save, $line);
}
close(FH);

@sorted = sort{$a<=>$b} @save;
foreach $ent (@sorted){
	print "$ent\n";
}
