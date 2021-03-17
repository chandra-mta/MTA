#!/usr/bin/perl 

$in_fits = $ARGV[0];
chomp $in_fits;
@atemp = split(/_/, $in_fits);
$acisid = $atemp[0];

$input = `ls /data/mta/Script/ACIS/SIB/Correct_excess/Reg_files/$acisid*_source_coord`;
@atemp = split(/\s+/, $input);
$coords = `cat $atemp[0]`;
chomp $coords;
@btemp  = split(/:/, $coords);
$skyx   = $btemp[0];
$skyy   = $btemp[1];

$input      = `ls /data/mta/Script/ACIS/SIB/Correct_excess/Reg_files/$acisid*_block_src.reg`;
@block_list = split(/\s+/, $input);
@ccd_list   = ();
$ccd_cnt    = 0;
foreach $ent (@block_list){
	@atemp = split(/ccd/, $ent);
	@btemp = split(/_/,   $atemp[1]);
	push(@ccd_list, $btemp[0]);
	$ccd_cnt++;
}

$line = "$in_fits".'[exclude sky=circle('."$skyx,$skyy".', 200)]';
system("dmcopy \"$line\" outfile=source_removed.fits");


$o_fits = $in_fits;
if($o_fits =~ /gz/){
	$o_fits =~ s/\.gz//;
}

@file_list = ();
foreach $ccd (@ccd_list){
	$out  = $o_fits;
	$app  = '_ccd'."$ccd".'.fits';
	$out  =~ s/\.fits/$app/;

#	$line = "$in_fits".'[ccd_id='."$ccd".']';
	$line = 'source_removed.fits[ccd_id='."$ccd".']';
	system("dmcopy \"$line\" outfile=$out");
	push(@file_list, $out);
}

system("rm source_removed.fits");

for($j = 0; $j < $ccd_cnt; $j++){
	$fits  = $file_list[$j];

	open(FH, "$block_list[$j]");
	@exclude = ();
	$e_cnt   = 0;
	while(<FH>){
		chomp $_;
		@atemp = split(/\,/, $_);
		$atemp[2] *= 3;
		$atemp[3] *= 3;
		$line = "$atemp[0],$atemp[1],$atemp[2],$atemp[3],$atemp[4]";
		push(@exclude, $line);
		$e_cnt++;
	}
	close(FH);
		
	$out_name = $fits;
	if($out_name =~ /gz/){
			$out_name =~ s/\.gz//;
	}
	$out_name =~ s/\.fits/_cleaned\.fits/;

	if($e_cnt > 0){
		$cnt   = 0;
		$chk   = 0;
		$round = 0;
		$line = '';
		OUTER1:
		while($cnt < $e_cnt){
			OUTER2:
			for($i = $cnt; $i < $cnt + 6; $i++){
				if($i >= $e_cnt){
					$chk++;
					last OUTER2;
				}
				if($line eq ''){
					$line = $exclude[$i];
				}else{
					$line = "$line".'+'."$exclude[$i]";
				}
			}
			$cnt += 6;
			if($round == 0){
				$eline = "$fits".'[exclude sky='."$line".']';
				system("dmcopy \"$eline\" outfile=out.fits");
				$round++;
			}else{
				system("mv out.fits temp.fits");
				$eline = 'temp.fits[exclude sky='."$line".']';
				system("dmcopy \"$eline\" outfile=out.fits");
			}
		
			if($chk > 0){
				last OUTER1;
			}else{
				$line = '';
			}
		}
		system("rm temp.fits");
		system("mv out.fits $out_name");
	}else{
		system("cp $fits $out_name");
	}
}
