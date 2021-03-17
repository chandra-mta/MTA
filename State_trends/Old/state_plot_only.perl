#!/usr/bin/perl
use PGPLOT;

#########################################################################################
#											#
#	state_plot_only.perl: create plots for a given year				#
#			    and trends key data.					#
#											#
#		 author: t. isobe (tisobe@cfa.harvard.edu)				#
#											#
#		last update Feb 04, 2013						#
#											#
#########################################################################################


##############################################################
#
#--- setting directories
#
$dir_list = '/data/mta/Script/OBT/ACIS/house_keeping/dir_list';

open(FH, $dir_list);
while(<FH>){
    chomp $_;
    @atemp = split(/\s+/, $_);
    ${$atemp[0]} = $atemp[1];
}   
close(FH);
##############################################################

$diryear = $ARGV[0];
chomp $diryear;

#
#---- plottting preparation starting here
#


$file = "$web_dir/$diryear/sim_data_summary$diryear";
open(FH, "$file");

$count = 0;
while(<FH>) {
	chomp $_;
	if($count > 1) {
		push(@temp_list, $_);
	}
	$count++;
}
close(FH);


#
#--- read a header file to get msids
#

$list  = `cat $data_dir/sim_header`;
@title =  split(/\s+/, $list);

#
#--- now accumulate data
#

$acc_tsc   = 0.0;
$acc_fa    = 0.0;
$entry_no  = 0;
@time_line = ();
@TSCPOS    = ();
@FAPOS     = ();
@CORADMEN  = ();
@COBSRQID  = ();
@CCSDSTMF  = ();
@ACC_TSC   = ();
@ACC_FA    = ();
@HRLSB     = ();
@liLSA     = ();
@LRLSBD    = ();
@M28IRAX   = ();
@M28IRBX   = ();
@M5IRAX    = ();
@M5IRBX    = ();

OUTER:
foreach $line (@temp_list) {
	if($line =~ /TIME/i){
		next OUTER;
	}elsif($line eq ''){
		next OUTER;
	}

	@atemp = split(/\t+/, $line);
	@btemp = split(/:/,   $atemp[0]);

	if($btemp[0] =~/\d/) {
		$year  = $btemp[0];
		$day   = $btemp[1];
		$hour  = $btemp[2];
		$min   = $btemp[3]; 
		@ctemp = split(/\t/,$btemp[4]);
		$sec   = $ctemp[0];
		$aday  = $day + (($sec/3600.0 + $min/60.0) + $hour)/24.0;

        	if ($year == 1999) {
                 	$dom = $day - 202;
        	}elsif($year >= 2000){
                	$dom = $day + 163 + 365*($year - 2000);
                	if($year > 2000) {
                        	$dom++;
                	}
                	if($year > 2004) {
                        	$dom++;
                	}
                	if($year > 2008) {
                        	$dom++;
                	}
                	if($year > 2012) {
                        	$dom++;
                	}
                	if($year > 2016) {
                        	$dom++;
                	}
                	if($year > 2020) {
                        	$dom++;
                	}
        	}

                $time = $dom;

#
#---  here we create cummulative form of tscpos and fapos
#

		$acc_tsc = $acc_tsc + abs($atemp[1]);
		$acc_fa  = $acc_fa  + abs($atemp[2]);

		push(@time_line, $time);
		push(@TSCPOS,    $atemp[1]);
		push(@FAPOS,     $atemp[2]);

#
#--- changing enab/disa/to 1 and 0
#

		$atemp[3] =~ s/^\s+//g;
		if($atemp[3] eq 'ENAB'){
			$value = 1;
		}else{
			$value = 0;
		}

		push(@CORADMEN, $value);
		push(@COBSRQID, $atemp[4]);
		
		@ctemp = split(/FMT/,$atemp[5]);
		push(@CCSDSTMF, $ctemp[1]);

		push(@ACC_TSC, $acc_tsc);
		push(@ACC_FA,  $acc_fa);

		$atemp[6] = ~s/^\s+//g;
		if($atemp[6] eq "INSR") {
			$value = 1;
		}else{
			$value = 0;
		}
		push(@HILSA, $value);

		$atemp[7] =~ s/^\s+//g;
		if($atemp[7] eq "INSR") {
			$value = 1;
		}else{
			$value = 0;
		}
		push(@HRLSB, $value);

		$atemp[8] =~ s/^\s+//g;
		if($atemp[8] eq "INSR") {
			$value = 1;
		}else{
			$value = 0;
		}
		push(@liLSA, $value);

		$atemp[9] =~ s/^\s+//g;
		if($atemp[9] eq "INSR") {
			$value = 1;
		}else{
			$value = 0;
		}
		push(@LRLSBD, $value);

		$atemp[10] =~ s/^\s+//g;
		if($atemp[10] eq "ENAB") {
			$value = 1;
		}else{
			$value = 0;
		}
		push(@M28IRAX, $value);

		$atemp[11] =~ s/^\s+//g;
		if($atemp[11] eq "ENAB") {
			$value = 1;
		}else{
			$value = 0;
		}
		push(@M28IRBX, $value);

		$atemp[12] =~ s/^\s+//g;
		if($atemp[12] eq "ENAB") {
			$value = 1;
		}else{
			$value = 0;
		}
		push(@M5IRAX, $value);

		$atemp[13] =~ s/^\s+//g;
		if($atemp[13] eq "ENAB") {
			$value = 1;
		}else{
			$value = 0;
		}
		push(@M5IRBX, $value);
		
		$entry_no++;
	}
}

$count  = 0;
@x_data = ();
@y_data = ();

foreach $x (@time_line) {
	$count++;
	$xint = int($x);
	$xfac = $x - $xint;
	@xt   = split(//,$xfac);
	$xb   = "$xint"."$xt[1]"."$xt[2]"."$xt[3]"."$xt[4]"."$xt[5]";
	push(@x_data, $xb);
}

$mcnt       = 0;
$scnt       = 0;
$s_TSCPOS   = 0;
$s_FAPOS    = 0;
$s_ACC_TSC  = 0;
$s_ACC_FA   = 0;
$s_CORADMEN = 0;
$s_COBSRQID = 0;
$s_CCSDSTMF = 0;
$s_HILSA    = 0;
$s_HRLSB    = 0;
$s_liLSA    = 0;
$s_LRLSBD   = 0;
$s_M28IRAX  = 0;
$s_M28IRBX  = 0;
$s_M5IRAX   = 0;
$s_M5IRBX   = 0;

$xbin[0]         = $x_data[0];
$TSCPOS_bin[0]   = $TSCPOS[0];
$FAPOS_bin[0]    = $FAPOS[0];
$ACC_TSC_bin[0]  = $ACC_TSC[0];
$ACC_FA_bin[0]   = $ACC_FA[0];
$CORADMEN_bin[0] = $CORADMEN[0];
$COBSRQID_bin[0] = $COBSRQID[0];
$CCSDSTMF_bin[0] = $CCSDSTMF[0];
$HILSA_bin[0]    = $HILSA[0];
$HILSB_bin[0]    = $HILSB[0];
$liLSA_bin[0]    = $liLSA[0];
$LRLSBD_bin[0]   = $LRLSBD[0];
$M28IRAX_bin[0]  = $M28IRAX[0];
$M28IRBX_bin[0]  = $M28IRBX[0];
$M5IRAX_bin[0]   = $M5IRAX[0];
$M5IRBX_bin[0]   = $M5IRBX[0];

for($i = 1; $i < $count; $i++) {
	 unless($x_data[$i] == $xbin[$mcnt]) {
		if($scnt < 1) {
			$TSCPOS_bin[$mcnt]   = 0; 
			$FAPOS_bin[$mcnt]    = 0; 
			$ACC_TSC_bin[$mcnt]  = 0; 
			$ACC_FA_bin[$mcnt]   = 0; 
			$CORADMEN_bin[$mcnt] = 0;
			$COBSRQID_bin[$mcnt] = 0;
			$CCSDSTMF_bin[$mcnt] = 0;
			$HILSA_bin[$mcnt]    = 0;
			$HILSB_bin[$mcnt]    = 0;
			$liLSA_bin[$mcnt]    = 0;
			$LRLSBD_bin[$mcnt]   = 0;
			$M28IRAX_bin[$mcnt]  = 0;
			$M28IRBX_bin[$mcnt]  = 0;
			$M5IRAX_bin[$mcnt]   = 0;
			$M5IRBX_bin[$mcnt]   = 0;

		}else {
			$TSCPOS_bin[$mcnt]   = $s_TSCPOS/$scnt; 
			$FAPOS_bin[$mcnt]    = $s_FAPOS/$scnt; 
			$ACC_TSC_bin[$mcnt]  = $s_ACC_TSC/$scnt; 
			$ACC_FA_bin[$mcnt]   = $s_ACC_FA/$scnt; 
			$CORADMEN_bin[$mcnt] = $s_CORADMEN/$scnt; 

			make_it_int($CORADMEN_bin[$mcnt]);

			$CORADMEN_bin[$mcnt] = $ivalue;
			$COBSRQID_bin[$mcnt] = $s_COBSRQID/$scnt; 

			make_it_int($COBSRQID_bin[$mcnt]);

			$COBSRQID_bin[$mcnt] = $ivalue;
			$CCSDSTMF_bin[$mcnt] = $s_CCSDSTMF/$scnt; 

			make_it_int($CCSDSTMF_bin[$mcnt]);

			$CCSDSTMF_bin[$mcnt] = $ivalue;
			$HILSA_bin[$mcnt]    = $s_HILSA/$scnt;

			make_it_int($HILSA_bin[$mcnt]);

			$HILSA_bin[$mcnt] = $ivalue;
			$HILSB_bin[$mcnt]    = $s_HILSB/$scnt;

			make_it_int($HILSB_bin[$mcnt]);

			$HILSB_bin[$mcnt] = $ivalue;
			$liLSA_bin[$mcnt]    = $s_liLSA/$scnt;

			make_it_int($liLSA_bin[$mcnt]);

			$liLSA_bin[$mcnt] = $ivalue;
			$LRLSBD_bin[$mcnt]   = $s_LRLSBD/$scnt;

			make_it_int($LRLSBD_bin[$mcnt]);

			$LRLSBD_bin[$mcnt] = $ivalue;
			$M28IRAX_bin[$mcnt]  = $s_M28IRAX/$scnt;

			make_it_int($M28IRAX_bin[$mcnt]);

			$M28IRAX_bin[$mcnt] = $ivalue;
			$M28IRBX_bin[$mcnt]  = $s_M28IRBX/$scnt;

			make_it_int($M28IRBX_bin[$mcnt]);

			$M28IRBX_bin[$mcnt] = $ivalue;
			$M5IRAX_bin[$mcnt]   = $s_M5IRAX/$scnt;

			make_it_int($M5IRAX_bin[$mcnt]);

			$M5IRAX_bin[$mcnt] = $ivalue;
			$M5IRBX_bin[$mcnt]   = $s_M5IRBX/$scnt;

			make_it_int($M5IRBX_bin[$mcnt]);

			$M5IRBX_bin[$mcnt] = $ivalue;
		}
		$scnt = 1;
		$mcnt++;
		$xbin[$mcnt] = $x_data[$i];
		$s_TSCPOS    = $TSCPOS[$i];
		$s_FAPOS     = $FAPOS[$i];
		$s_ACC_TSC   = $ACC_TSC[$i];
		$s_ACC_FA    = $ACC_FA[$i];
		$s_CORADMEN  = $CORADMEN[$i];
		$s_COBSRQID  = $COBSRQID[$i];
		$s_CCSDSTMF  = $CCSDSTMF[$i];
		$s_HILSA     = $HILSA[$i];
		$s_HRLSB     = $HRLSB[$i];
		$s_liLSA     = $liLSA[$i];
		$s_LRLSBD    = $LRLSBD[$i];
		$s_M28IRAX   = $M28IRAX[$i];
		$s_M28IRBX   = $M28IRBX[$i];
		$s_M5IRAX    = $M5IRAX[$i];
		$s_M5IRBX    = $M5IRBX[$i];
	}else{
		$s_TSCPOS    = $s_TSCPOS + $TSCPOS[$i];
		$s_FAPOS     = $s_FAPOS + $FAPOS[$i];
		$s_ACC_TSC   = $s_ACC_TSC + $ACC_TSC[$i];
		$s_ACC_FA    = $s_ACC_FA + $ACC_FA[$i];
		$s_CORADMEN  = $s_CORADMEN + $CORADMEN[$i];
		$s_COBSRQID  = $s_COBSRQID + $COBSRQID[$i];
		$s_CCSDSTMF  = $s_CCSDSTMF + $CCSDSTMF[$i];
		$s_HILSA     = $s_HILSA + $HILSA[$i];
		$s_HRLSB     = $s_HRLSB + $HRLSB[$i];
		$s_liLSA     = $s_liLSA + $liLSA[$i];
		$s_LRLSBD    = $s_LRLSBD + $LRLSBD[$i];
		$s_M28IRAX   = $s_M28IRAX + $M28IRAX[$i];
		$s_M28IRBX   = $s_M28IRBX + $M28IRBX[$i];
		$s_M5IRAX    = $s_M5IRAX + $M5IRAX[$i];
		$s_M5IRBX    = $s_M5IRBX + $M5IRBX[$i];
		$scnt++;
	}
}
$count_save = $count;
$count      = $mcnt;		

#
#--- setting plot min max
#

@xtemp = sort{ $a<=> $b } @xbin;
$xmin  = 0;

while($xmin == 0) {
        $xmin = shift(@xtemp);
}
$xmax = pop(@xtemp);
		
$xt_axis = "Time (DOM)";
$yskip   = 0;

#
#--- SIM
#

pgbegin(0, "/ps",1,1);
pgsubp(1,2);
pgsch(2);
pgslw(2);
	$data_file = '3FAPOS';
	$yt_axis   = '3FAPOS (step)';
	$xt_axis   = 'Time (DOM)';
	$title     = 'SEA FA POSITION';
	@ybin      = @FAPOS_bin;

	y_min_max();

	plot_fig();

	$data_file = '3TSCPOS';
	$yt_axis   = '3TSCPOS (step)';
	$xt_axis   = 'Time (DOM)';
	$title     = 'SEA TSC POSITION';
	@ybin      = @TSCPOS_bin;

	y_min_max();

	plot_fig();

pgclos();
        system("mv pgplot.ps $web_dir/$diryear/sim_file.ps");

#
#--- TSCPOS
#

pgbegin(0, "/ps",1,1);
pgsubp(1,5);
pgsch(3);
pgslw(2);

$xstart = $xmin + 0.01;
$yskip  = 1;

	$data_file = '3TSCPOS';
	$yt_axis   = '3TSCPOS (step)';
	$xt_axis   = 'Time (DOM)';
	$title     = 'SEA TSC POSITION: 9.28e4~9.30e4';
	@ybin      = @TSCPOS_bin;
	$ymin      = 9.28e4;
	$ymax      = 9.30e4;
	$xt_axis   = '';
        pgpage;

        pgswin($xmin, $xmax, $ymin, $ymax);
        pgbox('BCT', 0.0, 0, 'BCNTV',0.0,  0);
	pgslw(4);
        pgpt(1, $xbin[0], $ybin[0], -1);
        for($i = 1; $i < $count; $i++) {
                pgpt(1,$xbin[$i], $ybin[$i], -1);
        }
	pgslw(2);
	pglabel("", "", "$title");
        pgtext($xstart, 9.298e4, 'SEA TSC POSITION: 9.28e4~9.30e4');
	
	$title   = 'SEA TSC POSITION:7.40e4~7.60e4';
	$ymin    = 7.40e4;
	$ymax    = 7.60e4;
	$xt_axis = '';
        pgpage;

        pgswin($xmin, $xmax ,$ymin, $ymax);
        pgbox('BCT', 0.0, 0, 'BCNTV',0.0,  0);
	pgslw(4);
        pgpt(1,$xbin[0], $ybin[0],-1);
        for($i = 1; $i < $count; $i++) {
                pgpt(1, $xbin[$i], $ybin[$i], -1);
        }
	pgslw(2);
        pgtext($xstart, 7.575e4, 'SEA TSC POSITION: 7.40e4~7.60e4');
	
	$title   = 'SEA TSC POSITION:2.30e4~2.40e4';
	$ymin    = 2.3e4;
	$ymax    = 2.4e4;
	$xt_axis = '';
        pgpage;

        pgswin($xmin, $xmax, $ymin, $ymax);
        pgbox('BCT', 0.0, 0, 'BCNTV', 0.0,  0);
	pgslw(4);
        pgpt(1, $xbin[0], $ybin[0], -1);
        for($i = 1; $i < $count; $i++) {
                pgpt(1, $xbin[$i], $ybin[$i], -1);
        }
	pgslw(2);
        pgtext($xstart, 2.385e4, 'SEA TSC POSITION: 2.30e4~2.40e4');
	
	$title   = 'SEA TSC POSITION:-5.0e4~-5.1e4';
	$ymin    = -5.1e4;
	$ymax    = -5.0e4;
	$xt_axis = '';
        pgpage;

        pgswin($xmin, $xmax, $ymin, $ymax);
        pgbox('BCT', 0.0, 0, 'BCNTV', 0.0,  0);
	pgslw(4);
        pgpt(1, $xbin[0], $ybin[0], -1);
        for($i = 1; $i < $count; $i++) {
                pgpt(1, $xbin[$i], $ybin[$i], -1);
        }
	pgslw(2);
        pgtext($xstart, -5.01e4, 'SEA TSC POSITION: -5.0e4~-5.1e4');
	
	$title   = 'SEA TSC POSITION:-1.00e5~-0.99e5';
	$ymin    = -1.0e5;
	$ymax    = -9.9e4;
	$xt_axis = 'Time (DOM)';
        pgpage;

        pgswin($xmin, $xmax, $ymin, $ymax);
        pgbox('BCNT', 0.0, 0, 'BCNTV',0.0,  0);
	pgslw(4);
        pgpt(1, $xbin[0], $ybin[0], -1);
        for($i = 1; $i < $count; $i++) {
                pgpt(1, $xbin[$i], $ybin[$i], -1);
        }
	pgslw(2);
        pglabel("$xt_axis","","");
        pgtext($xstart, -9.915e4,'SEA TSC POSITION: -1.00e5~-0.99e5');
	
pgclos();
system("mv pgplot.ps $web_dir/$diryear/tscpos.ps");

#
#--- FAPOS
#

pgbegin(0, "/ps",1,1);
pgsubp(1,5);
pgsch(3);
pgslw(2);
	$data_file = '3FAPOS';
	$yt_axis   = '3FAPOS (step)';
	$xt_axis   = 'Time (DOM)';
	$title     = 'SEA FA POSITION:1.71e2~1.73e2';
	@ybin      = @FAPOS_bin;
	$ymin      = 1.71e2;
	$ymax      = 1.73e2;
	$xt_axis   = '';
        pgpage;

        pgswin($xmin, $xmax, $ymin, $ymax);
        pgbox('BCT', 0.0, 0, 'BCNTV',0.0,  0);
	pgslw(4);
        pgpt(1, $xbin[0], $ybin[0], -1);

        for($i = 1; $i < $count; $i++) {
                pgpt(1,$xbin[$i], $ybin[$i], -1);
        }
	pgslw(2);
        pglabel("", "", "$title");
        pgtext($xstart, 1.728e2, 'SEA FA POSITION: 1.71e2~1.73e2');
	
	$title = 'SEA FA POSITION:-1.60e2~-1.58e2';
	$ymin  = -1.60e2;
	$ymax  = -1.58e2;
	$xt_axis = '';
        pgpage;

        pgswin($xmin, $xmax, $ymin, $ymax);
        pgbox('BCT', 0.0, 0, 'BCNTV',0.0,  0);
	pgslw(4);
        pgpt(1, $xbin[0], $ybin[0], -1);
        for($i = 1; $i < $count; $i++) {
                pgpt(1, $xbin[$i], $ybin[$i], -1);
        }
	pgslw(2);
        pgtext($xstart, -1.582e2, 'SEA FA POSITION: -1.60e2~-1.58e2');
	
	$title   = 'SEA FA POSITION:-4.68e2~-4.66e2';
	$ymin    = -4.68e2;
	$ymax    = -4.66e2;
	$xt_axis = '';
        pgpage;

        pgswin($xmin, $xmax, $ymin, $ymax);
        pgbox('BCT', 0.0, 0, 'BCNTV', 0.0,  0);
	pgslw(4);
        pgpt(1, $xbin[0], $ybin[0], -1);
        for($i = 1; $i < $count; $i++) {
                pgpt(1,$xbin[$i], $ybin[$i], -1);
        }
	pgslw(2);
        pgtext($xstart, -4.662e2, 'SEA FA POSITION: -4.68e2~-4.66e2');
	
	$title   = 'SEA FA POSITION:-5.95e2~-5.93e2';
	$ymin    = -5.95e2;
	$ymax    = -5.93e2;
	$xt_axis = '';
        pgpage;

        pgswin($xmin, $xmax, $ymin, $ymax);
        pgbox('BCT', 0.0, 0, 'BCNTV',0.0,  0);
	pgslw(4);
        pgpt(1, $xbin[0], $ybin[0], -1);
        for($i = 1; $i < $count; $i++) {
                pgpt(1, $xbin[$i], $ybin[$i], -1);
        }
	pgslw(2);
        pgtext($xstart, -5.932e2, 'SEA FA POSITION: -5.95e2~-5.93e2');
	
	$title   = 'SEA FA POSITION:-9.00e2~-8.98e2';
	$ymin    = -9.00e2;
	$ymax    = -8.98e2;
	$xt_axis = 'Time (DOM)';
        pgpage;

        pgswin($xmin, $xmax, $ymin, $ymax);
        pgbox('BCNT', 0.0, 0, 'BCNTV',0.0,  0);
	pgslw(4);
        pgpt(1, $xbin[0], $ybin[0], -1);
        for($i = 1; $i < $count; $i++) {
                pgpt(1, $xbin[$i], $ybin[$i], -1);
        }
	pgslw(2);
        pglabel("xt_axis", "", "");
        pgtext($xstart, -8.982e2, 'SEA FA POSITION: -9.00e2~-8.98e2');
	
pgclos();
system("mv pgplot.ps $web_dir/$diryear/fapos.ps");

$yskip = 0;

#
#--- State
#

pgbegin(0, "/ps",1,1);
pgsubp(1,2);
pgsch(2);
pgslw(2);

        $data_file = 'CCSDSTMF';
        $yt_axis   = 'CCSDSTMF';
        $xt_axis   = 'Time (DOM)';
        $title     = 'TELEMETRY FORMAT ID';
        @ybin      = @CCSDSTMF_bin;
	$ymin      = -1;
	$ymax      = 6;
        plot_fig();

        $data_file = 'COBSRQID';
        $yt_axis   = 'COBSRQID';
        $xt_axis   = 'Time (DOM)';
        $title     = 'LAST COMMAND OBSERVATION ID';
        @ybin      = @COBSRQID_bin;
	$ymin      = -10000;
	$ymax      = 70000;
        plot_fig();

        $data_file = 'CORADMEN';
        $yt_axis   = 'CORADMEN';
        $xt_axis   = 'Time (DOM)';
        $title     = 'RAD MON PROCESS STATE';
        @ybin      = @CORADMEN_bin;
	$ymin      = -1.0;
	$ymax      = 2.0;
        plot_fig();


pgclos();
system("mv pgplot.ps $web_dir/$diryear/state_file.ps");

#
#--- RAD MON 
#

pgbegin(0, "/ps",1,1);
pgsubp(1,2);
pgsch(2);
pgslw(2);

        $data_file = 'CORADMEN';
        $yt_axis   = 'CORADMEN';
        $xt_axis   = 'Time (DOM)';
        $title     = 'RAD MON PROCESS STATE';
        @ybin      = @CORADMEN_bin;
	$ymin      = -1.0;
	$ymax      = 2.0;
        plot_fig();


pgclos();
system("mv pgplot.ps $web_dir/$diryear/rad_mon.ps");

#
#--- Grating
#

pgbegin(0, "/ps",1,1);
pgsubp(1,4);
pgsch(2);
pgslw(2);

        $data_file = 'HILSA';
        $yt_axis   = '4HILSA';
        $xt_axis   = 'Time (DOM)';
        $title     = 'MCE A: HETG liMIT SWITCH 2A MONITOR (INSERTED)';
        @ybin      = @HILSA_bin;
	$ymin      = -1.0;
	$ymax      =  2.0;
        plot_fig();

        $data_file = 'HILSB';
        $yt_axis   = '4HILSB';
        $xt_axis   = 'Time (DOM)';
        $title     = 'MCE B: HETG liMIT SWITCH 2A MONITOR (INSERTED)';
        @ybin      = @HILSB_bin;
	$ymin      = -1.0;
	$ymax      =  2.0;
        plot_fig();

        $data_file = 'liLSA';
        $yt_axis   = '4liLSA';
        $xt_axis   = 'Time (DOM)';
        $title     = 'MCE A: LETG liMIT SWITCH 2A MONITOR (INSERTED)';
        @ybin      = @liLSA_bin;
	$ymin      = -1.0;
	$ymax      =  2.0;
        plot_fig();

        $data_file = 'LRLSBD';
        $yt_axis   = '4LRLSBD';
        $xt_axis   = 'Time (DOM)';
        $title     = 'MCE B: LETG liMIT SWITCH 1A MONITOR (RETRACTED)';
        @ybin      = @LRLSBD_bin;
	$ymin      = -1.0;
	$ymax      =  2.0;
        plot_fig();

        $data_file = 'M28IRAX';
        $yt_axis   = '4M28IRAX';
        $xt_axis   = 'Time (DOM)';
        $title     = 'MCE A: +28 VOLT CONV INH RELAY MON';
        @ybin      = @M28IRAX_bin;
	$ymin      = -1.0;
	$ymax      =  2.0;
        plot_fig();

        $data_file = 'M28IRBX';
        $yt_axis   = '4M28IRBX';
        $xt_axis   = 'Time (DOM)';
        $title     = 'MCE B: +28 VOLT CONV INH RELAY MON';
        @ybin      = @M28IRBX_bin;
	$ymin      = -1.0;
	$ymax      =  2.0;
        plot_fig();

        $data_file = 'M5IRAX';
        $yt_axis   = '4M5IRAX';
        $xt_axis   = 'Time (DOM)';
        $title     = 'MCE A: +5 VOLT CONV INH RELAY MONITOR';
        @ybin      = @M5IRAX_bin;
	$ymin      = -1.0;
	$ymax      =  2.0;
        plot_fig();

        $data_file = 'M5IRBX';
        $yt_axis   = '4M5IRBX';
        $xt_axis   = 'Time (DOM)';
        $title     = 'MCE B: +5 VOLT CONV INH RELAY MONITOR';
        @ybin      = @M5IRBX_bin;
	$ymin      = -1.0;
	$ymax      =  2.0;
        plot_fig();

pgclos();
system("mv pgplot.ps $web_dir/$diryear/grating_file.ps");

#
#--- printing html page.
#

print_html_page();


######################################################
### y_min_max: find min and max of y axis          ###
######################################################

sub y_min_max {
        if($yskip == 0) {
                @ytemp = sort { $a<=> $b }  @ybin;
                $ymin = shift(@ytemp);
                if($ymin == 0.0) {
                        $ymin = -1.0}
                else{
                        if($ymin < 0.0) {
                                $ymin = $ymin*1.05;
                        }else{
                                $ymin = $ymin*0.95;
                        }
                }
                $ymax = pop(@ytemp);
                if($ymax == 0.0) {
                        $ymax = 1.0
                }else{
                        if($ymax < 0.0) {
                                $ymax = $ymax*0.95;
                        }else{
                                $ymax = $ymax*1.05;
                        }
                }
	}
}

######################################################
### plot_fig: plotting scattered plots             ###
######################################################

sub plot_fig {

        pgenv($xmin, $xmax,$ymin, $ymax,0,0);
	$xstart  = $xmin + 0.01*($xmax - $xmin);
	$xstart2 = $xmin + 0.2*($xmax - $xmin);

	if($data_file eq 'HILSA' || $data_file eq 'HILSB' 
		|| $data_file eq 'liLSA' || $data_file eq 'liLSB'){
		pgtext($xstart,  1.5, '0: RETR');
		pgtext($xstart2, 1.5, '1: INSR');
	}

	if($data_file eq 'LRLSBD' || $data_file eq 'M28IRAX'
		|| $data_file eq 'M28IRBX' || $data_file eq  'M5IRAX'
		|| $data_file eq 'CORADMEN') {
		$xstart= $xmin + 0.01;
		pgtext($xstart,  1.5, '0: DISA');
		pgtext($xstart2, 1.5, '1: ENAB');
	}


	pgslw(4);
        pgpt(1,$xbin[0], $ybin[0],-1);
        for($i = 1; $i < $count; $i++) {
                pgpt(1, $xbin[$i], $ybin[$i], -1);
        }
	pgslw(2);
        pglabel("$xt_axis", "$yt_axis", "$title");
}


######################################################
### make_it_int: make number to interger           ###
######################################################

sub make_it_int {
        ($ivalue) = @_;
        $int_part = int ($ivalue);
        $diff     = $ivalue - $int_part;

        if($diff < 0.5) {
                $add = 0.0;
        }else{
                $add = 1.0;
        }

        $ivalue = $int_part + $add;
}


######################################################
### rm_dupl: removing duplicated lines             ###
######################################################

sub rm_dupl {
        system('df -k . > zspace');
        open(INR, "./zspace");
        while(<INR>){
                chomp $_;
                if($_ =~ /\%/){
                        @atemp = split(/\s+/, $_);
                        @btemp = split(/\%/, $atemp[4]);
                        if($btemp[0] > 98){
                                open(FILE, ">.zwarning");
                                print FILE "Please check: /data/mta/www/mta_states/SIM/";
                                print FILE "$year/mta_sim_data_summary$year\n\n";
                                print FILE "Due to a disk space, the data was not updated\n";
                                close(FILE);

                                system("cat zwarning| mailx -s \"Subject:  SIM summary problem detected !!\n \" -r isobe\@head.cfa.harvard.edu  isobe\@head.cfa.harvard.edu ");
                                system("rm zwarning");
                        }else{

        			open(FH,  "./temp_data_summary");
        			open(OUT, ">sim_data_summary");
        			$count = 0;
				OUTER:
        			while(<FH>) {
                			chomp $_;
					@stemp = split(/:/, $_);
					if($stemp[0] < $diryear){
						next OUTER;
					}
                			if($count == 0) {
                        			$line = $_;
                        			print OUT "$_\n";
                        			$count++;
                			}else{
                        			unless($_ eq $line) {
                                			$line = $_;
                                			print OUT "$_\n";
                        			}else{
                                			$line = $_;
                        			}
                			}
        			}
        			close(FH);
        			close(OUT);
			}
		}
	}
	close(INR);
	system("rm ./zspace");
}

######################################################
### print_html_page: print html pages              ###
######################################################

sub print_html_page {

($usec, $umin, $uhour, $umday, $umon, $uyear, $uwday, $uyday, $uisdst)= localtime(time);

if($uyear < 1900) {
        $uyear = 1900 + $uyear;
}
$month = $umon + 1;

if ($uyear == 1999) {
        $dom = $uyday - 202;

}elsif($uyear >= 2000){
        $dom = $uyday + 163 + 365*($uyear - 2000);
        if($uyear > 2000) {
                $dom++;
        }
        if($uyear > 2004) {
                $dom++;
        }
        if($uyear > 2008) {
                $dom++;
        }
        if($uyear > 2012) {
                $dom++;
        }
        if($uyear > 2016) {
                $dom++;
        }
        if($uyear > 2020) {
                $dom++;
        }
}

#
#--- a top SIM html page
#

open(OUT, ">$web_dir/../sim.html");

print OUT "<!DOCTYPE html>\n";
print OUT "<html>\n";
print OUT "<head>\n";
print OUT '<title> Abridged Summary of State Changes </title>';
print OUT "<meta http-equiv='Content-Type' content='text/html; charset=utf-8' />\n";
print OUT "<style  type='text/css'>\n";
print OUT "table{text-align:center;margin-left:auto;margin-right:auto;border-style:solid;border-spacing:8px;border-width:2px;border-collapse:separate}\n";
print OUT "a:link {color:#00CCFF;}\n";
print OUT "a:visited {color:#B6FFFF;}\n";
print OUT "</style>\n";
print OUT "</head>\n";

print OUT "<body style='color:#FFFFFF;background-color:#000000'>\n";
print OUT "\n";
print OUT "\n";
print OUT '<h1 style="text-align:center">Abridged Summary of State Changes</h1>';
print OUT "\n";
print OUT '<h1 style="text-align:center" >Updated ';
print OUT "$uyear-$month-$umday  ";
print OUT "\n";
print OUT "<br />";
print OUT "DAY OF YEAR: $uyday ";
print OUT "\n";
print OUT "<br />";
print OUT "DAY OF MISSION: $dom ";
print OUT '</h1>';
print OUT "\n";
print OUT '<div style="padding-top:10px;padding-bottom:10px">';
print OUT '<hr />';
print OUT "\n";
print OUT "</div>\n";
print OUT '<ul>';
print OUT "\n";

for($hyear = 1999; $hyear <  $diryear+1; $hyear++){
        $htmname = 'year'."$hyear".'.html';
        print OUT '<li><a href="./ACIS/',"$htmname",'">Abridged Summary for Year ';
        print OUT "$hyear",'</a></li>',"\n";
}

print OUT '</ul>';
print OUT "\n";
print OUT '<div style="padding-top:10px;padding-bottom:10px">';
print OUT '<hr />';
print OUT "</div>\n";
print OUT '<a href="http://asc.harvard.edu/mta_days/mta_trends/trends.html">Link to MTA Trend Page</a>';
print OUT "</body>\n";
print OUT "</html>\n";
close(OUT);

#
#--- a html page for $diryear
#

$htmname = "$web_dir".'/year'."$diryear".'.html';
open(OUT,">$htmname");

print OUT "<!DOCTYPE html>\n";
print OUT "<html>\n";
print OUT "<head>\n";
print OUT "<title> Comprehensive Summary </title>\n";
print OUT "<meta http-equiv='Content-Type' content='text/html; charset=utf-8' />\n";
print OUT "<style  type='text/css'>\n";
print OUT "table{text-align:center;margin-left:auto;margin-right:auto;border-style:solid;border-spacing:8px;border-width:2px;border-collapse:separate}\n";
print OUT "a:link {color:#00CCFF;}\n";
print OUT "a:visited {color:B6FFFF;}\n";
print OUT "</style>\n";
print OUT "</head>\n";
print OUT '<body style="color:#FFFFFF;background-color:#000000">';

print OUT "\n";
print OUT '<title> Abridged Summary </title>';
print OUT "\n";
print OUT '<h1 style="text-align:center">Abridged Summary of State Changes</h1>';

print OUT "<div style='padding-top:10px;padding-bottom:10px'>\n";
print OUT '<hr />';
print OUT "\n";
print OUT "</div>\n";
print OUT "<p>\n";
print OUT 'Please select one of the following reports:';
print OUT "\n";
print OUT "</p>\n";
print OUT '';
print OUT "\n";
print OUT '  <ul>';
print OUT "\n";
print OUT '    <li><a href="./',"$diryear",'/sim_file.ps">SIM Positions</a></li>';
print OUT "\n";
print OUT '<li Type=square><a href="./',"$diryear",'/fapos.ps">SEA FA Position; Details</a></li>';
print OUT "\n";
print OUT '<li Type=square><a href="./',"$diryear",'/tscpos.ps"> SEA TSC POSITION; Details</a></li>';
print OUT "\n";
print OUT '    <li Type=disk><a href="./',"$diryear",'/grating_file.ps">Grating Status</a></li>';
print OUT "\n";
print OUT '    <li Type=disk><a href="./',"$diryear",'/state_file.ps">Other Status</a></li>';
print OUT "\n";
print OUT "</ul>\n";
$sim_name = 'sim_data_summary'."$dirname";
print OUT "<div style='padding-top:10px;padding-bottom:10px'>\n";
print OUT '<ul> <li Type=disk><a href="http://asc.harvard.edu/mta_days/mta_temp/ACIS/',"$diryear",'/'."$sim_name\">".'ASCII Data</a></li></ul>';
print OUT "\n";
print OUT "</div>\n";

print OUT "</body>\n";
print OUT "</html>\n";


close(OUT);
}
