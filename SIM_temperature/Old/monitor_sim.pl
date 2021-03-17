#!/usr/bin/perl

$init         = 0;
$tscpos       = 0;
$tscneg       = 0;
$fapos        = 0;
$faneg        = 0;
$tmoves       = 0;
$fmoves       = 0;
$deltsc       = 0;
$delfa        = 0;
$ntsc         = 0;
$nfa          = 0;

$tsc_test     = 9;
$fa_test      = 9;

$n_tt_sum     = 0;
$n_fa_sum     = 0;
$sumsq_tt_err = 0.0;
$rms_tt_err   = 0.0;
$sumsq_fa_err = 0.0;
$rms_fa_err   = 0.0;

@simt   = (23336, 92905, 75620, -50505, -99612);
@tscloc = ("SAFE", "ACIS-I", "ACIS-S", "HRC-I", "HRC-S");
@simf   = (-595, -505, -536, -468, -716, -991, -1048, -545, -455, -486, -418, -666, -941, -998);
@faloc  = ("INIT1", "INIT2", "ACIS-I", "ACIS-S", "HRC-I", "HRC-S", "HRC-S", "INIT1+", "INIT2+", 
           "ACIS-I+", "ACIS-S+", "HRC-I+", "HRC-S+", "HRC-S+");

system("date");

$out_dir        = '/data/mta/Script/SIM/Data/';

$ttab_file      = "$out_dir/sim_ttabs.out";
$sum_file       = "$out_dir/sim_summary.out";
$tsc_file       = "$out_dir/tsc_pos.out";
$fa_file        = "$out_dir/fa_pos.out";
$err_file       = "$out_dir/errors.lis";
$plot_file      = "$out_dir/plotfile.out";
$thist_file     = "$out_dir/tsc_histogram.out";
$lim_file       = "$out_dir/limits.txt";
$tsc_temps_file = "$out_dir/tsc_temps.txt";
$tsc_temps2     = "$out_dir/tsc_temps2.txt";

open(TTABS,">$ttab_file")          || die "Cannot open TTAB output file";
open(TFILE,">$tsc_file")           || die "Cannot open TFILE output file";
open(FFILE,">$fa_file")            || die "Cannot open FFILE output file";
open(EFILE,">$err_file")           || die "Cannot open EFILE output file";
open(PFILE,">$plot_file")          || die "Cannot open PFILE output file";
open(THFILE,">$thist_file")        || die "Cannot open HFILE output file";
open(LFILE,">$lim_file")           || die "Cannot open limits violations output file";
open(TSCTEMPF,">>$tsc_temps_file") || die "Cannot open tsc temps output file";
open(TSC2,">>$tsc_temps2")         || die "Cannot open tsc temps2 output file";


printf PFILE "%20s %10s %10s %10s %6s %10s %6s %6s %6s %10s %6s %6s %10s %10s\n", " DATE", " DAYS", " MET",
    " METYR", "TMOVES", "TSTEPS", "NTSC", "TSCRMS", "FMOVES", "FSTEPS", " NFA", " FARMS", " TSCPOS", " FAPOS";
	   
for ($i = 0; $i < 4000; $i++) {
    $daily_tsc_moves[$i] = 0;
    $dates_vs_met[$i]    = "XXXXXX";
}
$imet_max = 0;
$input = `ls ./TL/*tmp`;
@list  = split(/\n+/, $input);
@dlist = ();
foreach $ent (@list){
    open(FH, $ent);
    while(<FH>){
        chomp $_;
        push(@dlist, $_);
    }
    close(FH);
}

$k  = 0;
$mm = 6;
printf "Initialization\n", $i;
for ($i = 0; $i <= $mm; $i++) {
    $chk = 0;
    while($chk == 0){
        @fields = split(/\s*?\t\s*/,$dlist[$k]);
        $k++;

        next if ($fields[0] eq "N");
        next if ($fields[0] eq "TIME");
        next if ($fields[0] eq "");
        $chk = 1
    }

    $date_string = $fields[0];
    $dd[$i]      = $date_string;
    unshift(@fields,"N");  # VCDU not in TL files BDS    
    $tsc[$i]     = $fields[8];
    $tscmove[$i] = $fields[7];
    $fa[$i]      = $fields[10];
    $famove[$i]  = $fields[9];
    $maxpwm[$i]  = $fields[11];
    $tabaxis[$i] = $fields[15];
    $tabno[$i]   = $fields[16];
    $tabpos[$i]  = $fields[17];
    $motoc[$i]   = $fields[12];
    $stall[$i]   = $fields[13];
    $tflexa[$i]  = $fields[18];
    $tflexb[$i]  = $fields[19];
    $tflexc[$i]  = $fields[20];
    $ttscmot[$i] = $fields[21];
    $tfamot[$i]  = $fields[22];
    $tseaps[$i]  = $fields[23];
    $trail[$i]   = $fields[24];
    $tseabox[$i] = $fields[25];
    $trpm[$i]    = 0.0;
    $frpm[$i]    = 0.0;
    $tstate[$i]  = "STOP";
    $fstate[$i]  = "STOP";

    get_date();

    find_locs();
}

$lasttsc     = $tsc[$mm];
$lastfa      = $fa[$mm];
$lasttabaxis = $tabaxis[$mm];
$lasttabno   = $tabno[$mm];
$lasttabpos  = $tabpos[$mm];
$tscsum      = 0.0;
$tsctot      = 0.0;
$fasum       = 0.0;
$fatot       = 0.0;
$last_tsctot = 0.0;
$last_tscsum = 0.0;
$last_tmoves = 0.0;
$last_fatot  = 0.0;
$last_fasum  = 0.0;
$last_fmoves = 0.0;

$init        = 1;

$isize = scalar @dlist;
$i     = $mm;

for($m = $k+1;$m < $isize; $m++){

  @fields = split(/\s*?\t\s*/,$dlist[$m]);
  $t      = $fields[0];

  if ( ($t ne "TIME") && ($t ne "N") && ($t ne "")) {

	for ($i = 1; $i <= $mm; $i++) {
	    $dd[$i-1]      = $dd[$i];
	    $tsc[$i-1]     = $tsc[$i];
	    $tscmove[$i-1] = $tscmove[$i];
	    $fa[$i-1]      = $fa[$i];
	    $famove[$i-1]  = $famove[$i];
	    $maxpwm[$i-1]  = $maxpwm[$i];
	    $tabaxis[$i-1] = $tabaxis[$i];
	    $tabno[$i-1]   = $tabno[$i];
	    $tabpos[$i-1]  = $tabpos[$i];
	    $motoc[$i-1]   = $motoc[$i];
	    $stall[$i-1]   = $stall[$i];
	    $tflexa[$i-1]  = $tflexa[$i];
	    $tflexb[$i-1]  = $tflexb[$i];
	    $tflexc[$i-1]  = $tflexc[$i];
	    $ttscmot[$i-1] = $ttscmot[$i];
	    $tfamot[$i-1]  = $tfamot[$i];
	    $tseaps[$i-1]  = $tseaps[$i];
	    $trail[$i-1]   = $trail[$i];
	    $tseabox[$i-1] = $tseabox[$i];
	    $trpm[$i-1]    = $trpm[$i];
	    $frpm[$i-1]    = $frpm[$i];
	    $tloc[$i-1]    = $tloc[$i];
	    $floc[$i-1]    = $floc[$i];
	    $tdays[$i-1]   = $tdays[$i];
	    $tsec[$i-1]    = $tsec[$i];
	    $tstate[$i-1]  = $tstate[$i];
	    $fstate[$i-1]  = $fstate[$i];
	    $tsc_err[$i-1] = $tsc_err[$i];
	    $fa_err[$i-1]  = $fa_err[$i];
	}

	$i           = $mm;
	$date_string = $fields[0];
	$dd[$i]      = $date_string;

    unshift(@fields,"N");  # VCDU not in TL files BDS    

	$tsc[$i]     = $fields[8];
	$tscmove[$i] = $fields[7];
	$famove[$i]  = $fields[9];
	$fa[$i]      = $fields[10];
	$maxpwm[$i]  = $fields[11];
	$motoc[$i]   = $fields[12];
	$stall[$i]   = $fields[13];
	$tabaxis[$i] = $fields[15];
	$tabno[$i]   = $fields[16];
	$tabpos[$i]  = $fields[17];
	$tflexa[$i]  = $fields[18];
	$tflexb[$i]  = $fields[19];
	$tflexc[$i]  = $fields[20];
	$ttscmot[$i] = $fields[21];
	$tfamot[$i]  = $fields[22];
	$tseaps[$i]  = $fields[23];
	$trail[$i]   = $fields[24];
	$tseabox[$i] = $fields[25];
	$bus_volts   = $fields[31];

	get_date();

	$terror  = "FALSE";
	$del_sec = ($tsec[$i] - $tsec[$i-1]);

	if ( ($del_sec > 33.0) || ($del_sec < 32.0) ) { 
	    $terror = "TRUE";
	    printf EFILE "%20s  TIME SKIP ERROR - %20s %12.3f %12.3f %12.1f\n", 
	                  $dd[$i], $dd[$i-1], $tsec[$i], $tsec[$i-1], $del_sec;
	}

	$trpm[$i] = (60.0/32.8)*($tsc[$i] - $tsc[$i-1])/18.0;

	if ( ($terror eq "FALSE") && ( abs($trpm[$i]) > 3200.0) ) {
	    printf EFILE "%20s  TSC RPM ERROR   - %10d %10d %10d\n", 
                      $dd[$i], $tsc[$i], $tsc[$i-1], $trpm[$i];
	    $tsc[$i]  = $lasttsc;
	    $trpm[$i] = 0.0;
	}


	$frpm[$i] = (60.0/32.8)*($fa[$i] - $fa[$i-1])/18.0;

	if ( ($terror eq "FALSE") && ( abs($frpm[$i]) > 1200.0) ) {
	    printf EFILE "%20s   FA RPM ERROR   - %10d %10d\n", 
                        $dd[$i], $fa[$i], $frpm[$i];

	    $fa[$i]   = $lastfa;
	    $frpm[$i] = 0.0;
	}


	if ($tsc[$i-1] != $tsc[$i]) {
        $tstate[$i] = "MOVE";
        if ( $tsc[$i] > $tsc[$i-1]) {
            $tscpos = $tscpos + ($tsc[$i] - $lasttsc);
            $tscsum = $tscsum + ($tsc[$i] - $lasttsc);
            $tsctot = $tsctot + ($tsc[$i] - $lasttsc);
        } else {
            $tscneg = $tscneg - ($tsc[$i] - $lasttsc);
            $tscsum = $tscsum + ($tsc[$i] - $lasttsc);
            $tsctot = $tsctot - ($tsc[$i] - $lasttsc);
        }
    } else {
           $tstate[$i] = "STOP";
    }

	if ($fa[$i-1] != $fa[$i] ) { 
        $fstate[$i] = "MOVE";
        if ( $fa[$i] > $lastfa) {
            $fapos = $fapos + ($fa[$i] - $lastfa);
	        $fasum = $fasum + ($fa[$i] - $lastfa);
	        $fatot = $fatot + ($fa[$i] - $lastfa);
	    } else {
	        $faneg = $faneg - ($fa[$i] - $lastfa);
	        $fasum = $fasum + ($fa[$i] - $lastfa);
	        $fatot = $fatot - ($fa[$i] - $lastfa);
	    }
    } else {
	    $fstate[$i] = "STOP";
	}

	if ( ($fstate[$i-1] eq "STOP") && ($fstate[$i] eq "MOVE") ) {
	    $fmoves++;
	}
	
	find_locs();

	$ptab = 0;
	if ($tabaxis[$i-1] ne $tabaxis[$i] ) {
	    $ptab = 1;
	}
	if ($tabno[$i-1] != $tabno[$i] ) {
	    $ptab = 1;
	}
	if ($tabpos[$i-1] != $tabpos[$i] ) {
	    $ptab = 1;
	}


	if ( ($tstate[$i-1] eq "STOP") && ($tstate[$i] eq "MOVE") ) {
	    $start_tsc = $tsc[$i-1];
	    print "\nStart TT move\n";
	    printf TFILE "\n";
	    printf TFILE "%20s %8s %6s %6s %6s %3s %7s %4s %4s %4s %10s %10s %4s %3s %3s %6s %5s %2s %6s %6s\n",
	    "DATE", "TSCPOS", "STATE", "MFLAG", "RPM", "PWM", " LOCN", "ERR", "   N", " RMS", "TOTSTP", "DELSTP", 
	    "MVES", "OVC", "STL", "TMOT", "AXIS", "NO", "TABPOS", "TRAIL";
	    printf TFILE "%20s %8d %6s %6s %6d %3d %7s %4d %4s %4s %10d %10d %4d %3d %3d %6.1f\n",
	    $dd[$i-1], $tsc[$i-1], $tstate[$i-1], $tscmove[$i-1], $trpm[$i-1], $maxpwm[$i-1], $tloc[$i-1], 
	    $tsc_err[$i-1], "    ", "    ", $last_tsctot, $last_tscsum, $last_tmoves, $motoc[$i-1], 
        $stall[$i-1], $ttscmot[$i-1];

	    $temp_tsc_start = $ttscmot[$i];
	    $max_tsc_pwm    = $maxpwm[$i];
	    $tsc_pos_start  = $tsc[$i-1];

	    $met            = $tdays[$i-1]-204.5;
	    $metyr          = $met/365.0;

	    printf TSC2 "%20s %10.4f %10.4f %6.1f\n", $dd[$i-1], $met, $metyr, $ttscmot[$i-1];
	}

	if ($tstate[$i] eq "MOVE") {
	    print "Continue TT move\n";
	    printf TFILE "%20s %8d %6s %6s %6d %3d %7s %4d %4s %4s %10d %10d %4d %3d %3d %6.1f", 
	    $dd[$i], $tsc[$i], $tstate[$i], $tscmove[$i], $trpm[$i], $maxpwm[$i], $tloc[$i], 
	    $tsc_err[$i], "    ", "    ", $tsctot, $tscsum, $tmoves, $motoc[$i], $stall[$i], $ttscmot[$i];

	    if ( ($ptab > 0) && ($tabaxis[$i] eq "TSC" ) ) {
		    printf TFILE "%6s %2d %6d %6.1f\n", $tabaxis[$i], $tabno[$i], $tabpos[$i], $trail[$i];
	    } else {
		    printf TFILE "\n";
	    }

	    if ($motoc[$i] > 0) {
		    printf LFILE "%20s %8d\n", $dd[$i], $motoc[$i];
	    }

	    if ($maxpwm[$i-1] > $max_tsc_pwm ) {
		    $max_tsc_pwm = $maxpwm[$i];
	    }
	}

	if ( ($tstate[$i-1] eq "MOVE") && ($tstate[$i] eq "STOP") ) {

	    if ( $tsc_err[$i] < 999 ) {
		    $n_tt_sum     = $n_tt_sum + 1;
		    $sumsq_tt_err = $sumsq_tt_err + $tsc_err[$i]**2;
		    $rms_tt_err   = sqrt($sumsq_tt_err/$n_tt_sum);
	    }
	    $stop_tsc      = $tsc[$i];
	    $tsc_move_size = $stop_tsc - $start_tsc;
	    printf "Stop TT move N tot: %6d RMS Err: %6.2f Size: %10d\n", 
                    $n_tt_sum, $rms_tt_err, $tsc_move_size;

	    $met                 = $tdays[$i]-204.5;
	    $imet                = int($met);
	    $dates_vs_met[$imet] = $dd[$i];

	    if ($imet > $imet_max) {
		    $imet_max = int(1+$imet);
	    }
	    $metyr = $met/365.0;
	    
	    if ($maxpwm[$i-1] > $max_tsc_pwm ) {
		    $max_tsc_pwm = $maxpwm[$i];
	    }
	    
	    $tsc_pos_end     = $tsc[$i];
	    $tsc_steps_moved = abs($tsc_pos_end - $tsc_pos_start);

	    if ($tsc_steps_moved > 0 ) {

		    $tmoves++;

		    $daily_tsc_moves[$imet]++;
		    printf "Add TSC Move: %20s %5d\n", $dd[$i], $daily_tsc_moves[$imet];
    
		    printf TFILE "%20sD%8d %6s %6s %6d %3d %7s %4d %4d %4.1f %10d %10d %4d %3d %3d %6.1f\n", 
		                    $dd[$i], $tsc[$i], $tstate[$i], $tscmove[$i], $trpm[$i], $maxpwm[$i], $tloc[$i], 
		                    $tsc_err[$i], $n_tt_sum, $rms_tt_err, $tsctot, $tscsum, $tmoves, $motoc[$i], 
                            $stall[$i], $ttscmot[$i];
    
		    printf THFILE"%20s %10d %10d %10d\n", $dd[$i], $start_tsc, $stop_tsc, $tsc_move_size;
    
		    printf TSC2 "%20s %10.4f %10.4f %6.1f\n", $dd[$i], $met, $metyr, $ttscmot[$i];
    
		    printf TSCTEMPF "%20s %10.4f %6.1f %6.1f %6d %8d %4d %4d %6.1f\n", 
                            $dd[$i], $metyr, $temp_tsc_start, $ttscmot[$i], $max_tsc_pwm, 
                            $tsc_steps_moved, $motoc[$i], $stall[$i], $bus_volts;
    
    
		    printf "TSC MOVE Complete:  %20s %6.1f %6d\n", $dd[$i], $temp_tsc_start, $max_tsc_pwm;
    
		    printf PFILE "%20s %10.4f %10.4f %10.4f %6d %10d %6d %6.1f %6d %10d %6d %6.1f %10d %10d\n", 
		                    $dd[$i], $tdays[$i], $met, $metyr, $tmoves, $tsctot, $n_tt_sum, 
                            $rms_tt_err, $fmoves, $fatot, $n_fa_sum, $rms_fa_err, $tsc[$i], $fa[$i];

	    }
	}


	if ( ($fstate[$i-1] eq "STOP") && ($fstate[$i] eq "MOVE") ) {
	    print "\nStart FA move\n";
	    printf FFILE "\n";
	    printf FFILE "%20s %8s %6s %6s %6s %3s %7s %4s %4s %4s %10s %10s %4s %3s %3s %6s %5s %2s %6s %6s\n",
	    "DATE", "TSCPOS", "STATE", "MFLAG", "RPM", "PWM", " LOCN", "ERR", "   N", " RMS", "TOTSTP", "DELSTP", 
	    "MVES", "OVC", "STL", "TMOT", "AXIS", "NO", "TABPOS", "TRAIL";
	    printf FFILE "%20s %8d %6s %6s %6d %3d %7s %4d %4s %4s %10d %10d %4d %3d %3d %6.1f\n", 
	                    $dd[$i-1], $fa[$i-1], $fstate[$i-1], $famove[$i-1], $frpm[$i-1], $maxpwm[$i-1], 
                        $floc[$i-1], $fa_err[$i-1], "    ", "    ", $last_fatot, $last_fasum, 
                        $last_fmoves, $motoc[$i-1], $stall[$i-1], $tfamot[$i-1];
	}

	if ($fstate[$i] eq "MOVE") {
	    print "Continue FA move\n";
	    printf FFILE "%20s %8d %6s %6s %6d %3d %7s %4d %4s %4s %10d %10d %4d %3d %3d %6.1f", 
	    $dd[$i], $fa[$i], $fstate[$i], $famove[$i], $frpm[$i], $maxpwm[$i], $floc[$i], 
	    $fa_err[$i], "    ", "    ", $fatot, $fasum, $fmoves, $motoc[$i], $stall[$i], $tfamot[$i];

	    if ( ($ptab > 0) && ($tabaxis[$i] eq "FA" ) ) {
		    printf FFILE "%6s %2d %6d %6.1f\n", $tabaxis[$i], $tabno[$i], $tabpos[$i], $trail[$i];
	    } else {
		    printf FFILE "\n";
	    }
	}

	if ( ($fstate[$i-1] eq "MOVE") && ($fstate[$i] eq "STOP") ) {
	    if ( $fa_err[$i] < 999 ) {
		    $n_fa_sum = $n_fa_sum + 1;
		    $sumsq_fa_err = $sumsq_fa_err + $fa_err[$i]**2;
		    $rms_fa_err = sqrt($sumsq_fa_err/$n_fa_sum);
	    }
	    printf "Stop FA move N tot: %6d RMS Err: %6.2f\n", $n_fa_sum, $rms_fa_err;
	    printf FFILE "%20s %8d %6s %6s %6d %3d %7s %4d %4d %4.1f %10d %10d %4d %3d %3d %6.1f\n", 
	            $dd[$i], $fa[$i], $fstate[$i], $famove[$i], $frpm[$i], $maxpwm[$i], $floc[$i], 
	            $fa_err[$i], $n_fa_sum, $rms_fa_err, $fatot, $fasum, $fmoves, $motoc[$i], 
                $stall[$i], $tfamot[$i];

	    $met = $tdays[$i] - 204.5;
	    $metyr = $met/365.0;
	    printf PFILE "%20s %10.4f %10.4f %10.4f %6d %10d %6d %6.1f %6d %10d %6d %6.1f %10d %10d\n", 
	                $dd[$i], $tdays[$i], $met, $metyr, $tmoves, $tsctot, $n_tt_sum, $rms_tt_err, 
                    $fmoves, $fatot, $n_fa_sum, $rms_fa_err, $tsc[$i], $fa[$i];
	}

	if ($ptab > 0) {
	    if ( $tabaxis[$i] eq "TSC" ) {
		    printf TTABS "%20s %6s %2d %6d %6.1f\n", $dd[$i], $tabaxis[$i], $tabno[$i], $tabpos[$i], $trail[$i];
	    } else {
#		    printf FTABS "%20s %6s %2d %6d %6.1f\n", $dd[$i], $tabaxis[$i], $tabno[$i], $tabpos[$i], $trail[$i];
	    }
	}

	$last_tscsum = $tscsum;
	$last_tsctot = $tsctot;
	$last_fasum  = $fasum;
	$last_fatot  = $fatot;
	$last_tmoves = $tmoves;
	$last_fmoves = $fmoves;
	$lasttsc     = $tsc[$i];
	$lastfa      = $fa[$i];
	$lasttabaxis = $tabaxis[$i];
	$lasttabno   = $tabno[$i];
	$lasttabpos  = $tabpos[$i];

  }                 #---- closing of if ( ($t ne "TIME") && ($t ne "N") && ($t ne "")) {
  $init = 1;
}                   #---- closing of while loop

close(TFILE);
close(FFILE);
close(EFILE);
close(PFILE);
close(THFILE);
close(LFILE);
close(TSCTEMPF);
close(TSC2);

if ($ntsc < 1) {
    $ntsc = 1;
}
if ($nfa < 1) {
    $nfa = 1;
}

$tscerr = $deltsc/$ntsc;
$faerr = $delfa/$nfa;

open(SUMFILE,">$sum_file") || die "Cannot open summary file";
printf SUMFILE "%24s %16d\n", "Total FA moves:      ", $fmoves;
printf SUMFILE "%24s %16d\n", "Total TT moves:      ", $tmoves;
printf SUMFILE "%24s %16d\n", "Sum of Pos TSC Steps:", $tscpos;
printf SUMFILE "%24s %16d\n", "Sum of Neg TSC Steps:", $tscneg;
printf SUMFILE "%24s %16d\n", "Sum of Pos  FA Steps:", $fapos;
printf SUMFILE "%24s %16d\n", "Sum of Pos  FA Steps:", $faneg;
printf SUMFILE "%24s  %16.2f\n", "Avg Error in TSC Position: ", $tscerr;
printf SUMFILE "%24s  %16.2f\n", "Avg Error in  FA Position: ", $faerr;

close(SUMFILE);

##***************************************************************************
sub get_date {
##***************************************************************************

    $gmt_yr   = substr($date_string,0,4);
    $gmt_day  = substr($date_string,4,3);
    $gmt_hr   = substr($date_string,8,2);
    $gmt_min  = substr($date_string,10,2);
    $gmt_sec  = substr($date_string,12,2);
    $gmt_msec = substr($date_string,14,3);

    $tddd  = ($gmt_day + $gmt_hr/24.0 +$gmt_min/(1440.0) + $gmt_sec/86400.0 + $gmt_msec/(86400000));
    $tddd += 365.0*($gmt_yr-1999)+int(($gmt_yr-1996)/4.0);

    $tdays[$i] = $tddd;
    $tsec[$i]  = (86400.0*$gmt_day + 3600.0*$gmt_hr + 60.0*$gmt_min + $gmt_sec + $gmt_msec/1000.0);
    
}

##***************************************************************************
sub get_acorn_date {  # acorn date format is a little different than greta
##***************************************************************************

    @dstring1 = split(" ",$date_string);
    $time     = "";

    for ($di = 2; $di <= $#dstring1; $di++) {
        $time .= $dstring1[$di];
    }

    @dstring2 = split(":",$time);
    $gmt_yr   = $dstring1[0];
    $gmt_day  = $dstring1[1];
    $gmt_hr   = $dstring2[0];
    $gmt_min  = $dstring2[1];
    $gmt_sec  = $dstring2[2];
    $gmt_msec = 0;

    if ($gmt_yr < 1900) { $gmt_yr += 1900;}

    $tddd = ($gmt_day + $gmt_hr/24.0 +$gmt_min/(1440.0) + $gmt_sec/86400.0);

    if ($gmt_yr == 2000) {
	    $tddd = $tddd + 365.0;
    } 

    if ($gmt_yr == 2001) {
	    $tddd = $tddd + 365.0 + 366.0;
    }     

    if ($gmt_yr == 2002) {
	    $tddd = $tddd + 365.0 + 366.0 + 365.0;
    }     

    $tdays[$i] = $tddd;
    $tsec[$i]  = (86400.0*$gmt_day + 3600.0*$gmt_hr + 60.0*$gmt_min + $gmt_sec + $gmt_msec/1000.0);
}


##***************************************************************************
sub find_locs {
##***************************************************************************
    
    $tloc[$i]    = "----";
    $floc[$i]    = "----";
    $tsc_err[$i] = 999;
    $fa_err[$i]  = 999;
    $nnt         = @simt;

    for ($j = 0; $j < $nnt; $j++) {
	    if ($tscmove[$i] eq "STOP") {
	        $dtsc = abs($tsc[$i]-$simt[$j]);

	        if ($dtsc < $tsc_test) {
		        $tsc_err[$i] = ($tsc[$i] - $simt[$j]);
		        $deltsc      = $deltsc + $dtsc;
		        $ntsc        = $ntsc + 1;
		        $tloc[$i]    = $tscloc[$j];
	        }
	    }
    }
	
    $nnf = @simf;
    for ($j = 0; $j < $nnf; $j++) {
	    if ($famove[$i] eq "STOP" ) {
	        $dfa = abs($fa[$i]-$simf[$j]);

	        if ($dfa < $fa_test) {
		        $fa_err[$i] = ($fa[$i] - $simf[$j]);
		        $delfa      = $delfa + $dfa;
		        $nfa        = $nfa + 1;
		        $floc[$i]   = $faloc[$j];
	        }
	    }
    }
}

##***************************************************************************
sub aform2dform {  
#   convert acorn date yyyy doy hh:mm:ss to greta yyyydoy.hhmmss
##***************************************************************************

  my @yrdoy = split(' ', $_[0]);
  my $year  = $yrdoy[0] + 1900;

  if ($year < 1900) {$year += 1900;}

  my $doy        = "00".$yrdoy[1];
  my $whats_left = "";

  for ($i = 2; $i <= $#yrdoy; $i++) {
        $whats_left = $whats_left.$yrdoy[$i];
  }

  my @hrminsec = split(':', $whats_left);
  my $hour     = "0".$hrminsec[0];
  my $min      = "0".$hrminsec[1];
  my $sec      = $hrminsec[2];
  $_           = substr($sec, 0, index($sec, "\."));
  $count = tr/0-9//;

  if ($count eq 1) {$sec = "0".$sec;}

  $sec =~ s/\.//;

  my $dec = sprintf "%4s%3s\.%2s%2s%s", $year,substr($doy, -3, 3), substr($hour,
 -2, 2), substr($min, -2, 2), $sec;

  return $dec;
}
