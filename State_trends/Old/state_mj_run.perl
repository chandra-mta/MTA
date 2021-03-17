#!/usr/bin/perl
use PGPLOT;					# pgplot package

###################################################################################
###										###
###			state_mj_run.perl					###
###	this script gets information from /dsops/GOT/input/.. dump data		###
###	and monitoring trend of key data.					###
###										###
###	Usage:		perl  run_mj_list.perl					###
###										###
###	Output:									###
###		postscript files for the trend plots				###
###										###
###	Author: Takashi Isobe (tisobe@cfa.harvad.edu)				###
###										###
###	Last Update: Apr 10, 2017						###
###										###
###################################################################################

#
#--- check whether this is a test case
#

$comp_test = $ARGV[0];
chomp $comp_test;

if($comp_test =~ /test/i){
	$input = `ls -d /data/mta/Script/OBT/*`;
	if($input =~ /Test_out/){
		system("rm -rf /data/mta/Script/OBT/Test_out/*");
		system("mkdir  /data/mta/Script/OBT/Test_out/house_keeping");
		system("cp     /data/mta/Script/OBT/MJ/house_keeping/Test_data/old_list /data/mta/Script/OBT/Test_out/house_keeping/.");
		system("cp     /data/mta/Script/OBT/MJ/house_keeping/Test_data/comprehensive_data_summary /data/mta/Script/OBT/Test_out/house_keeping/.");
		system("chmod 777 /data/mta/Script/OBT/Test_out/house_keeping/*");
	}else{
		system("mkdir  /data/mta/Script/OBT/Test_out");
		system("mkdir  /data/mta/Script/OBT/Test_out/house_keeping");
		system("cp     /data/mta/Script/OBT/MJ/house_keeping/Test_data/old_list /data/mta/Script/OBT/Test_out/house_keeping/.");
		system("cp     /data/mta/Script/OBT/MJ/house_keeping/Test_data/comprehensive_data_summary /data/mta/Script/OBT/Test_out/house_keeping/.");
		system("chmod 777 /data/mta/Script/OBT/Test_out/house_keeping/*");
	}
}

##############################################################
#
#--- setting directories
#
if($comp_test =~ /test/i){
	$dir_list = '/data/mta/Script/OBT/MJ/house_keeping/dir_list_test';
}else{
	$dir_list = '/data/mta/Script/OBT/MJ/house_keeping/dir_list';
}

open(FH, $dir_list);
while(<FH>){
    chomp $_;
    @atemp = split(/\s+/, $_);
    ${$atemp[0]} = $atemp[1];
}   
close(FH);
##############################################################

#
#--- remove the past system log
#

system("rm ./systemlog");


#
#--- find today's date
#

if($comp_test =~ /test/i){
	$diryear = 2013;
       	system("mkdir $web_dir/$diryear"); 
}else{
	($usec, $umin, $uhour, $umday, $umon, $uyear, $uwday, $uyday, $uisdst)= localtime(time);

	$diryear = 1900 + $uyear;
#
#---check whether we need a new directory or not
#---this happens only once a year on Jan 1.
#

	if($uyday ==  0) {
        	$last_year  = $diryear - 1;
        	$last_file  = "$web_dir"."/$last_year".'/comprehensive_data_summary'."$last_year";
        	system("cat $data_dir/mj_header $house_keeping/comprehensive_data_summary~ > $last_file");
	
        	system("rm $house_keeping/comprehensive_data_summary");
	
        	system("mkdir $web_dir/$diryear"); 
	}
}


#
#--- find which data file are already processed, and make a list of un-processed data
#

open(FH, "$house_keeping/old_list");
while(<FH>) {
	chomp $_;
	push(@old_list, $_);
}
close(FH);

if($comp_test =~ /test/i){
	system("ls -rt /data/mta/Script/OBT/MJ/house_keeping/Test_data/*Dump_EM*gz > new_list");
}else{
	system("ls -rt /dsops/GOT/input/*Dump_EM*gz > new_list");
}

@new_list = ();
open(FH,'./new_list');
while(<FH>) {
	chomp $_;
	push(@new_list, $_);
}
close(FH);

@data_list = ();
OUTER:
foreach $entry (@new_list) {
        foreach $comp (@old_list) {
                if($entry eq $comp) {
                        next OUTER;
                }
        }
        push(@data_list, $entry);
}

system("mv $house_keeping/old_list    $house_keeping/old_list~");
system("mv new_list                   $house_keeping/old_list");

@data_list = sort (@data_list);

#
#--- gzip a dump data and extract data we need for the plots
#
foreach $data (@data_list) {
#	system("gzip -dc $data| $bin_dir/acorn -nCO $data_dir/simpos_acis.scr -T -o");
	system("gzip -dc $data > ./temp_file");
	system("acorn -f ./temp_file  -nCO $data_dir/simpos_acis.scr -T -o");
	system("rm ./temp_file");
}

system('cat mjsimpos* > alldata');
open(FH, "./alldata");
open(OUT, ">./alldatatemp");
$i = 0;
OUTER:
while(<FH>){
        chomp $_;
        if($_ =~ /TIME/i && $i == 0){
                @atemp = split(/\s+/, $_);
                $total= 0;
                foreach(@atemp){
                        $total++;
                }
                $i = 1;
                print OUT "$_\n";
                next OUTER;
        }
                
        @atemp = split(/\s+/, $_);
        $cnt = 0;
        foreach(@atemp){
                $cnt++;
        }
        if($cnt == $total){
                print OUT "$_\n";
        }
}
close(OUT);
close(FH);


#
#--- remove headers
#

system("sed -f $data_dir/mj_sedscript1 alldatatemp > alldata_cleaned");

@data = ();
open(FH,'./alldata_cleaned');

while(<FH>){
        chomp $_;
        push(@data, $_);
}
close(FH);

@adata = sort @data;

open(OUT,">./alldata_cleaned_sorted");

foreach $ent (@adata){
        print OUT "$ent\n";;
}
close(OUT);

#
#--- change format
#

#system("nawk -F\"\\t\" -f $data_dir/mj_nawkscript alldata_cleaned_sorted > alldata_cleaned_sorted_timed");
system("gawk -F\"\\t\" -f $bin_dir/mj_nawkscript alldata_cleaned_sorted > alldata_cleaned_sorted_timed");

system("cat $house_keeping/comprehensive_data_summary alldata_cleaned_sorted_timed > ./data_summary");

#
#--- save alldata_cleaned_sorted_timed for focal plane computation
#

system("mv alldata_cleaned_sorted_timed todays_data");

system("rm alldata*");

open(FH,'./data_summary');
@data = ();

while(<FH>){
        chomp $_;
        push(@data, $_);
}
close(FH);

@adata = sort @data;

open(OUT,">./temp_data_summary");

foreach $ent (@adata){
        print OUT "$ent\n";;
}
close(OUT);

#
#-- clearning up the comprehensive_data_summary file
#

rm_dupl();			

#
#--- moidfy the data file for web page and save it
#

$comp_file = 'comprehensive_data_summary'."$diryear";
system("cat $data_dir/mj_header comprehensive_data_summary > $web_dir/$diryear/$comp_file");
system("rm data_summary temp_data_summary mjsimpos*tl");

#
#--- cp to  a pool area
#

if($comp_test !~ /test/i){
####    system("cp $web_dir/$diryear/$comp_file  /pool14/chandra/acis_diag_support/");
}

system("mv $house_keeping/comprehensive_data_summary $house_keeping/comprehensive_data_summary~");
system("mv comprehensive_data_summary                $house_keeping/comprehensive_data_summary");



#
#---- plottting preparation starting here
#



open(FH, "$house_keeping/comprehensive_data_summary");

$count = 0;
while(<FH>) {
	chomp $_;
	push(@temp_list, $_);
	$count++;
}
close(FH);

#
#--- remove duplicated lines
#

@data_list  = sort (@temp_list);

$count      = 0;
$line       = shift(@data_list);
@clean_list = ("$line");

foreach $comp (@data_list) {
	unless($comp eq $line) {
		push(@clean_list, $line);
	}
	$line = $comp;
}

#
#--- read a header file to get msids
#

$list  = `cat $data_dir/mj_header`;
@title =  split(/\s+/, $list);

#
#--- now accumulate data
#

@time_line = ();
@TSCPOS    = ();
@FAPOS     = ();
@CRAT      = ();
@CRBT      = ();
@ACC_TSC   = ();
@ACC_FA    = ();
@CCSDSTMF  = ();
@COBSRQID  = ();
@HPOSARO   = ();
@HPOSBRO   = ();
@LPOSARO   = ();
@LPOSBRO   = ();
@TSCPOS2   = ();
@FAPOS2    = ();
@acc_tsc   = (); 
@acc_fa    = (); 
@acc_nman  = (); 
@acc_npnt  = (); 
@acc_nsun  = (); 
@acc_pwrf  = (); 
@acc_pman  = (); 
@acc_stby  = (); 
$pvalue    = 1000;
$entry_no  = 0;
$null      = 0;

foreach $line (@clean_list) {
	@atemp = split(/\t+/, $line);
	@btemp = split(/:/,   $atemp[0]);

	if($btemp[0] =~/\d/) {			# looking for obs time
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

		$acc_tsc = $acc_tsc + abs($atemp[1]- $TSCPOS[$entry_no - 1]);
		$acc_fa  = $acc_fa  + abs($atemp[2] - $FAPOS[$entry_no - 1]);

		push(@time_line, $time);
		push(@TSCPOS,    $atemp[1]);
		push(@FAPOS,     $atemp[2]);
		push(@CRAT,      $atemp[3]);
		push(@CRBT,      $atemp[4]);
		push(@ACC_TSC,   $acc_tsc);
		push(@ACC_FA,    $acc_fa);

#
#--- changing enab/disa/to 1 and 0
#
		$atemp[5] =~ s/^\s+//g;

		if($atemp[5] eq "ENAB") {
			$value = 1;
		}else{
			$value = 0;
		}
		push(@CORADMEN, $value);

		$atemp[6] =~s/^\s+//g;
		if($atemp[6] eq "ENAB") {
			$value = 1;
		}else{
			$value = 0;
		}
		push(@CORADMIN, $value);
		
		@ctemp = split(/FMT/,$atemp[7]);
		push(@CCSDSTMF, $ctemp[1]);
		push(@COBSRQID, $atemp[8]);
		push(@HPOSARO,  $atemp[9]);
		push(@HPOSBRO,  $atemp[10]);
		push(@LPOSARO,  $atemp[11]);
		push(@LPOSBRO,  $atemp[12]);
		push(@TSCPOS2,  $atemp[13]);
		push(@FAPOS2,   $atemp[14]);

		$one_before = $entry_no - 1;
		$diff_time  = 365.25 * ($time - $time_line[$one_before]);

		$atemp[15] =~ s/^\s+//g;
		if($atemp[15] eq 'NMAN') {

			if($pvalue == 0) {
				push(@acc_nman, $diff_time);
			}
			$pvalue = 0;
			push(@acc_npnt, $null);
			push(@acc_nsun, $null);
			push(@acc_pwrf, $null);
			push(@acc_rman, $null);
			push(@acc_stby, $null);

		}elsif($atemp[15] eq 'NPNT') {

			if($pvalue == 1) {
				push(@acc_npnt, $diff_time);
			}
			$pvalue = 1;
			push(@acc_nman, $null);
			push(@acc_nsun, $null);
			push(@acc_pwrf, $null);
			push(@acc_rman, $null);
			push(@acc_stby, $null);

		}elsif($atemp[15] eq 'NSUN') {
			if($pvalue == 2) {
				push(@acc_nsun,  $diff_time);
			}
			$pvalue = 2;
			push(@acc_nman, $null);
			push(@acc_npnt, $null);
			push(@acc_pwrf, $null);
			push(@acc_rman, $null);
			push(@acc_stby, $null);

		}elsif($atemp[15] eq 'PWRF') {
			if($pvalue == 3) {
				push(@acc_pwrf, $diff_time);
			}
			$pvalue = 3;
			push(@acc_nman, $null);
			push(@acc_npnt, $null);
			push(@acc_nsun, $null);
			push(@acc_rman, $null);
			push(@acc_stby, $null);

		}elsif($atemp[15] eq 'RMAN') {
			if($pvalue == 4) {
				push(@acc_rman, $diff_time);
			}
			$pvalue = 4;
			push(@acc_nman, $null);
			push(@acc_npnt, $null);
			push(@acc_nsun, $null);
			push(@acc_pwrf, $null);
			push(@acc_stby, $null);

		}elsif($atemp[15] eq 'STBY') {
			if($pvalue == 5) {
				push(@acc_stby, $diff_time);
			}
			$pvalue = 5;
			push(@acc_nman, $null);
			push(@acc_npnt, $null);
			push(@acc_nsun, $null);
			push(@acc_pwrf, $null);
			push(@acc_rman, $null);

		}else {
			$pvalue  = -1;
			push(@acc_nman, $null);
			push(@acc_npnt, $null);
			push(@acc_nsun, $null);
			push(@acc_pwrf, $null);
			push(@acc_rman, $null);
			push(@acc_stby, $null);
		}
		push(@AOPCADMD, $pvalue);
		$entry_no++;
	}
}

@x_data = ();
@y_data = ();
$count  = 0;

foreach $x (@time_line) {
	$count++;
	$xint = int($x);
	$xfac = $x - $xint;
	@xt   = split(//, $xfac);
	$xb   = "$xint"."$xt[1]"."$xt[2]"."$xt[3]"."$xt[4]"."$xt[5]";
	push(@x_data, $xb);
}

$mcnt       = 0;
$scnt       = 0;
$s_TSCPOS   = 0;
$s_FAPOS    = 0;
$s_CRAT     = 0;
$s_CRBT     = 0;
$s_ACC_TSC  = 0;
$s_ACC_FA   = 0;
$s_CORADMEN = 0;
$s_CORADMIN = 0;
$s_CCSDSTMF = 0;
$s_COBSRQID = 0;
$s_HPOSARO  = 0;
$s_HPOSBRO  = 0;
$s_LPOSARO  = 0;
$s_LPOSBRO  = 0;
$s_TSCPOS2  = 0;
$s_FAPOS2   = 0;
$s_AOPCADMD = 0;
$s_ACC_NMAN = 0;
$s_ACC_NPNT = 0;
$s_ACC_NSUN = 0;
$s_ACC_PWRF = 0;
$s_ACC_PMAN = 0;
$s_ACC_STBY = 0;

$xbin[0]         = $x_data[0];
$TSCPOS_bin[0]   = $TSCPOS[0];
$FAPOS_bin[0]    = $FAPOS[0];
$CRAT_bin[0]     = $CRAT[0];
$CRBT_bin[0]     = $CRBT[0];
$ACC_TSC_bin[0]  = $ACC_TSC[0];
$ACC_FA_bin[0]   = $ACC_FA[0];
$CORADMEN_bin[0] = $CORADMEN[0];
$CORADMIN_bin[0] = $CORADMIN[0];
$CCSDSTMF_bin[0] = $CCSDSTMF[0];
$COBSRQID_bin[0] = $COBSRQID[0];
$HPOSARO_bin[0]  = $HPOSARO[0];
$HPOSBRO_bin[0]  = $HPOSBRO[0];
$LPOSARO_bin[0]  = $LPOSARO[0];
$LPOSBRO_bin[0]  = $LPOSBRO[0];
$TSCPOS2_bin[0]  = $TSCPOS2[0];
$FAPOS2_bin[0]   = $FAPOS2[0];
$AOPCADMD_bin[0] = $AOPCADMD[0];
$ACC_NMAN_bin[0] = $acc_nman[0];
$ACC_NPNT_bin[0] = $acc_npnt[0];
$ACC_NSUN_bin[0] = $acc_nsun[0];
$ACC_PWRF_bin[0] = $acc_pwrf[0];
$ACC_PMAN_bin[0] = $acc_pman[0];
$ACC_STBY_bin[0] = $acc_stby[0];

for($i = 1; $i < $count; $i++) {
	 unless($x_data[$i] == $xbin[$mcnt]) {
		if($scnt < 1) {
			$TSCPOS_bin[$mcnt]   = 0; 
			$FAPOS_bin[$mcnt]    = 0; 
			$CRAT_bin[$mcnt]     = 0; 
			$CRBT_bin[$mcnt]     = 0; 
			$ACC_TSC_bin[$mcnt]  = 0; 
			$ACC_FA_bin[$mcnt]   = 0; 
			$CORADMEN_bin[$mcnt] = 0; 
			$CORADMIN_bin[$mcnt] = 0; 
			$CCSDSTMF_bin[$mcnt] = 0; 
			$COBSRQID_bin[$mcnt] = 0; 
			$HPOSARO_bin[$mcnt]  = 0; 
			$HPOSBRO_bin[$mcnt]  = 0; 
			$LPOSARO_bin[$mcnt]  = 0; 
			$LPOSBRO_bin[$mcnt]  = 0; 
			$TSCPOS2_bin[$mcnt]  = 0; 
			$FAPOS2_bin[$mcnt]   = 0; 
			$AOPCADMD_bin[$mcnt] = 0;
			$ACC_NMAN_bin[$mcnt] = 0;
			$ACC_NPNT_bin[$mcnt] = 0;
			$ACC_NSUN_bin[$mcnt] = 0;
			$ACC_PWRF_bin[$mcnt] = 0;
			$ACC_PMAN_bin[$mcnt] = 0;
			$ACC_STBY_bin[$mcnt] = 0;
		}else {
			$TSCPOS_bin[$mcnt]   = $s_TSCPOS/$scnt; 
			$FAPOS_bin[$mcnt]    = $s_FAPOS/$scnt; 
			$CRAT_bin[$mcnt]     = $s_CRAT/$scnt; 
			$CRBT_bin[$mcnt]     = $s_CRBT/$scnt; 
			$ACC_TSC_bin[$mcnt]  = $s_ACC_TSC/$scnt; 
			$ACC_FA_bin[$mcnt]   = $s_ACC_FA/$scnt; 
			$CORADMEN_bin[$mcnt] = $s_CORADMEN/$scnt; 

			make_it_int($CORADMEN_bin[$mcnt]);

			$CORADMEN_bin[$mcnt] = $ivalue;
			$CORADMIN_bin[$mcnt] = $s_CORADMIN/$scnt; 

			make_it_int($CORADMIN_bin[$mcnt]);

			$CORADMIN_bin[$mcnt] = $ivalue;
			$CCSDSTMF_bin[$mcnt] = $s_CCSDSTMF/$scnt; 

			make_it_int($CCSDSTMF_bin[$mcnt]);

			$CCSDSTMF_bin[$mcnt] = $ivalue;
			$COBSRQID_bin[$mcnt] = $s_COBSRQID/$scnt; 
			$HPOSARO_bin[$mcnt]  = $s_HPOSARO/$scnt; 
			$HPOSBRO_bin[$mcnt]  = $s_HPOSBRO/$scnt; 
			$LPOSARO_bin[$mcnt]  = $s_LPOSARO/$scnt; 
			$LPOSBRO_bin[$mcnt]  = $s_LPOSBRO/$scnt; 
			$TSCPOS2_bin[$mcnt]  = $s_TSCPOS2/$scnt; 
			$FAPOS2_bin[$mcnt]   = $s_FAPOS2/$scnt;
			$AOPCADMD_bin[$mcnt] = $s_AOPCADMD/$scnt;

			make_it_int($AOPCADMD_bin[$mcnt]);

			$AOPCADMD_bin[$mcnt] = $ivalue;
			$ACC_NMAN_bin[$mcnt] = $s_ACC_NMAN;
			$ACC_NPNT_bin[$mcnt] = $s_ACC_NPNT;
			$ACC_NSUN_bin[$mcnt] = $s_ACC_NSUN;
			$ACC_PWRF_bin[$mcnt] = $s_ACC_PWRF;
			$ACC_PMAN_bin[$mcnt] = $s_ACC_PMAN;
			$ACC_STBY_bin[$mcnt] = $s_ACC_STBY;
		}
		$scnt = 1;
		$mcnt++;
		$xbin[$mcnt] = $x_data[$i];
		$s_TSCPOS    = $TSCPOS[$i];
		$s_FAPOS     = $FAPOS[$i];
		$s_CRAT      = $CRAT[$i];
		$s_CRBT      = $CRBT[$i];
		$s_ACC_TSC   = $ACC_TSC[$i];
		$s_ACC_FA    = $ACC_FA[$i];
		$s_CORADMEN  = $CORADMEN[$i];
		$s_CORADMIN  = $CORADMIN[$i];
		$s_CCSDSTMF  = $CCSDSTMF[$i];
		$s_COBSRQID  = $COBSRQID[$i];
		$s_HPOSARO   = $HPOSARO[$i];
		$s_HPOSBRO   = $HPOSBRO[$i];
		$s_LPOSARO   = $LPOSARO[$i];
		$s_LPOSBRO   = $LPOSBRO[$i];
		$s_TSCPOS2   = $TSCPOS2[$i];
		$s_FAPOS2    = $FAPOS2[$i];
		$s_AOPCADMD  = $AOPCADMD[$i];
		$s_ACC_NMAN  = $s_ACC_NMAN + $acc_nman[$i];
		$s_ACC_NPNT  = $s_ACC_NPNT + $acc_npnt[$i];
		$s_ACC_NSUN  = $s_ACC_NSUN + $acc_nsun[$i];
		$s_ACC_PWRF  = $s_ACC_PWRF + $acc_pwrf[$i];
		$s_ACC_PMAN  = $s_ACC_PMAN + $acc_pman[$i];
		$s_ACC_STBY  = $s_ACC_STBY + $acc_stby[$i];
	}else{
		$s_TSCPOS    = $s_TSCPOS + $TSCPOS[$i];
		$s_FAPOS     = $s_FAPOS + $FAPOS[$i];
		$s_CRAT      = $s_CRAT + $CRAT[$i];
		$s_CRBT      = $s_CRBT + $CRBT[$i];
		$s_ACC_TSC   = $s_ACC_TSC + $ACC_TSC[$i];
		$s_ACC_FA    = $s_ACC_FA + $ACC_FA[$i];
		$s_CORADMEN  = $s_CORADMEN + $CORADMEN[$i];
		$s_CORADMIN  = $s_CORADMIN + $CORADMIN[$i];
		$s_CCSDSTMF  = $s_CCSDSTMF + $CCSDSTMF[$i];
		$s_COBSRQID  = $s_COBSRQID + $COBSRQID[$i];
		$s_HPOSARO   = $s_HPOSARO + $HPOSARO[$i];
		$s_HPOSBRO   = $s_HPOSBRO + $HPOSBRO[$i];
		$s_LPOSARO   = $s_LPOSARO + $LPOSARO[$i];
		$s_LPOSBRO   = $s_LPOSBRO + $LPOSBRO[$i];
		$s_TSCPOS2   = $s_TSCPOS2 + $TSCPOS2[$i];
		$s_FAPOS2    = $s_FAPOS2 + $FAPOS2[$i];
		$s_AOPCADMD  = $s_AOPCADMD + $AOPCADMD[$i];
		$s_ACC_NMAN  = $s_ACC_NMAN + $acc_nman[$i];
		$s_ACC_NPNT  = $s_ACC_NPNT + $acc_npnt[$i];
		$s_ACC_NSUN  = $s_ACC_NSUN + $acc_nsun[$i];
		$s_ACC_PWRF  = $s_ACC_PWRF + $acc_pwrf[$i];
		$s_ACC_PMAN  = $s_ACC_PMAN + $acc_pman[$i];
		$s_ACC_STBY  = $s_ACC_STBY + $acc_stby[$i];
		$scnt++;
	}
}
$count_save = $count;
$count      = $mcnt;		

#
#--- setting plot min max
#

@xtemp      = sort{ $a<=> $b } @xbin;
$xmin       = 0;

while($xmin == 0) {
	$xmin = shift(@xtemp);
}

$xmax = pop(@xtemp);

$xt_axis = "Time (DOM)";
$yskip = 0;

#
#--- ACIS
#

pgbegin(0, "/ps",1,1);
pgsubp(1,2);
pgsch(2);
pgslw(2);
	$data_file = '1CRAT';
	$yt_axis   = '1CRAT (C)';
	$xt_axis   = 'Time (DOM)';
	$title     = 'COLD RADIATOR TEMP. A';
	@ybin      = @CRAT_bin;

	y_min_max();

	plot_fig();

	$data_file = '1CRBT';
	$yt_axis   = '1CRBT (C)';
	$xt_axis   = 'Time (DOM)';
	$title     = 'COLD RADIATOR TEMP. B';
	@ybin      = @CRBT_bin;

	y_min_max();

	plot_fig();

pgclos();
system("mv pgplot.ps $web_dir/$diryear/acis_file.ps");

#
#--- Grating
#

pgbegin(0, "/ps",1,1);
pgsubp(1,3);
pgsch(2);
pgslw(2);
	$data_file = '4HPOSARO';
	$yt_axis   = '4HPOSARO (deg)';
	$xt_axis   = '';
	$title     = 'HETG ROTATION ANGLE POSITION MONITOR A';
	@ybin      = @HPOSARO_bin;

	y_min_max();	

	plot_fig();

	$data_file = '4HPOSARO';
	$yt_axis   = '4HPOSARO (deg)';
	$xt_axis   = '';
	$title     = 'HETG ROTATION ANGLE POSITION MONITOR A: 60.0 ~ 85.0';

	$ymin      = 60.0;
	$ymax      = 87.0;

	plot_fig();

	$data_file = '4HPOSARO';
	$yt_axis   = '4HPOSARO (deg)';
	$xt_axis   = 'Time (DOM)';
	$title     = 'HETG ROTATION ANGLE POSITION MONITOR A: 5.0 ~ 10.0';

	$ymin      = 5.0;
	$ymax      = 10.0;

	plot_fig();

pgclos();
system("mv pgplot.ps $web_dir/$diryear/4hposaro.ps");

pgbegin(0, "/ps",1,1);
pgsubp(1,3);
pgsch(2);
pgslw(2);
	$data_file = '4HPOSBRO';
	$yt_axis   = '4HPOSBRO (deg)';
	$xt_axis   = '';
	$title     = 'HETG ROTATION ANGLE POSITION MONITOR B';
	@ybin      = @HPOSBRO_bin;

	y_min_max();	

	plot_fig();

	$data_file = '4HPOSBRO';
	$xt_axis   = '';
	$title     = 'HETG ROTATION ANGLE POSITION MONITOR B: 60.0 ~ 85.0';
	@y_bin     = @HPOSBRO_bin;

	$ymin      = 60.0;
	$ymax      = 87.0;

	plot_fig();

	$data_file = '4HPOSBRO';
	$yt_axis   = '4HPOSBRO (deg)';
	$xt_axis   = 'Time (DOM)';
	$title     = 'HETG ROTATION ANGLE POSITION MONITOR B: 5.0 ~ 10.0';

	$ymin      = 5.0;
	$ymax      = 10.0;

	plot_fig();

pgclos();
system("mv pgplot.ps $web_dir/$diryear/4hposbro.ps");


pgbegin(0, "/ps",1,1);
pgsubp(1,2);
pgsch(2);
pgslw(2);
	$data_file = '4LPOSARO';
	$yt_axis   = '4LPOSARO (deg)';
	$xt_axis   = 'Time (DOM)';
	$title     = 'LETG ROTATION ANGLE POSITION MONITOR A';
	@ybin      = @LPOSARO_bin;

	y_min_max();	

	plot_fig();

	$data_file = '4LPOSBRO';
	$yt_axis   = '4LPOSBRO (deg)';
	$xt_axis   = 'Time (DOM)';
	$title     = 'LETG ROTATION ANGLE POSITION MONITOR B';
	@ybinn     = @LPOSBRO_bin;

	y_min_max();

	plot_fig();

pgclos();
system("mv pgplot.ps $web_dir/$diryear/lteg_file.ps");

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

	$data_file = '7FAPOS';
	$yt_axis   = '7FAPOS (step)';
	$xt_axis   = 'Time (DOM)';
	$title     = 'SEA FA POSITION';
	@ybin      = @FAPOS2_bin;

	y_min_max();

	plot_fig();
	
	$data_file = 'TSCPOS2';
	$yt_axis   = '7TSCPOS (step)';
	$xt_axis   = 'Time (DOM)';
	$title     = 'SEA TSC POSITIOIN';
	@ybin      = @TSCPOS2_bin;

	y_min_max();

	plot_fig();

pgclos();
system("mv pgplot.ps $web_dir/$diryear/sim_file.ps");

pgbegin(0, "/ps",1,1);
pgsubp(1,2);
pgsch(2);
pgslw(2);
        $data_file = 'ACC_TSC';
        $yt_axis   = 'ACC_TSC (step)';
        $xt_axis   = 'Time (DOM)';
        $title     = 'INTEGRATED TSC POSITION';
        @ybin      = @ACC_TSC_bin;

        y_min_max();

        plot_fig();

        $data_file = 'ACC_FA';
        $yt_axis   = 'ACC_FA (step)';
        $xt_axis   = 'Time (DOM)';
        $title     = 'INTEGRATED FA POSITION';
        @ybin      = @ACC_FA_bin;

        y_min_max();

        plot_fig();

pgclos();
system("mv pgplot.ps $web_dir/$diryear/acc_sim_file.ps");

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

	$xt_axis = '';
        pgpage;
        pgswin($xmin, $xmax, $ymin, $ymax);
        pgbox('BCT', 0.0, 0, 'BCNTV',0.0,  0);
	pgslw(4);
        pgpt(1,$xbin[0], $ybin[0],-1);

        for($i = 1; $i < $count; $i++) {
                pgpt(1, $xbin[$i], $ybin[$i], -1);
        }

	pgslw(2);
        pglabel("","","$title");
        pgtext($xstart, 9.297e4, 'SEA TSC POSITION: 9.28e4~9.30e4');
	
	$title = 'SEA TSC POSITION:7.40e4~7.60e4';

	$ymin  = 7.40e4;
	$ymax  = 7.60e4;

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
        pgtext($xstart, 7.575e4, 'SEA TSC POSITION: 7.40e4~7.60e4');
	
	$title = 'SEA TSC POSITION:2.30e4~2.40e4';

	$ymin = 2.3e4;
	$ymax = 2.4e4;

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
	
	$title = 'SEA TSC POSITION:-5.0e4~-5.1e4';

	$ymin  = -5.1e4;
	$ymax  = -5.0e4;

	$xt_axis = '';
        pgpage;
        pgswin($xmin, $xmax, $ymin, $ymax);
        pgbox('BCT', 0.0, 0, 'BCNTV',0.0,  0);
	pgslw(4);
        pgpt(1,$xbin[0], $ybin[0],-1);

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
        pgbox('BCNT', 0.0, 0, 'BCNTV', 0.0,  0);
	pgslw(4);
        pgpt(1, $xbin[0], $ybin[0], -1);

        for($i = 1; $i < $count; $i++) {
                pgpt(1, $xbin[$i], $ybin[$i], -1);
        }

	pgslw(2);
        pglabel("$xt_axis", "", "");
        pgtext($xstart, -9.915e4, 'SEA TSC POSITION: -1.00e5~-0.99e5');
	
pgclos();
system("mv pgplot.ps $web_dir/$diryear/tscpos.ps");

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
                pgpt(1, $xbin[$i], $ybin[$i], -1);
        }

	pgslw(2);
        pglabel("", "", "$title");
        pgtext($xstart, 1.728e2, 'SEA FA POSITION: 1.71e2~1.73e2');
	
	$title = 'SEA FA POSITION:-1.60e2~-1.58e2';

	$ymin    = -1.60e2;
	$ymax    = -1.58e2;
	$xt_axis = '';

        pgpage;
        pgswin($xmin, $xmax, $ymin, $ymax);
        pgbox('BCT', 0.0, 0, 'BCNTV', 0.0,  0);
	pgslw(4);
        pgpt(1,$xbin[0], $ybin[0],-1);

        for($i = 1; $i < $count; $i++) {
                pgpt(1, $xbin[$i], $ybin[$i], -1);
        }

	pgslw(2);
        pgtext($xstart, -1.582e2, 'SEA FA POSITION: -1.60e2~-1.58e2');
	
	$title = 'SEA FA POSITION:-4.68e2~-4.66e2';

	$ymin    = -4.68e2;
	$ymax    = -4.66e2;
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
        pgtext($xstart, -4.662e2, 'SEA FA POSITION: -4.68e2~-4.66e2');

	$title   = 'SEA FA POSITION:-5.95e2~-5.93e2';
	$ymin    = -5.95e2;
	$ymax    = -5.93e2;
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

	$ymin      = 0;
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

        $data_file = 'CORADMIN';
        $yt_axis   = 'CORADMIN';
        $xt_axis   = 'Time (DOM)';
        $title     = 'RAD MON INIT PROCESS STATE';
        @ybin      = @CORADMIN_bin;

	$ymin      = -1.0;
	$ymax      = 2.0;

        plot_fig();

pgclos();
system("mv pgplot.ps $web_dir/$diryear/state_file.ps");

$yskip = 0;

#
#--- PCAD
#

pgbegin(0, "/ps",1,1);
pgsubp(1,2);
pgsch(2);
pgslw(2);

        $data_file = 'AOPCADMD';
        $yt_axis   = 'AOPCADMD';
        $xt_axis   = 'Time (DOM)';
        $title     = 'PCAD MODE';
        @ybin      = @AOPCADMD_bin;

	$ymin      = -1;
	$ymax      = 6;

        plot_fig();

pgclos();
system("mv pgplot.ps $web_dir/$diryear/pcad_file.ps");

pgbegin(0, "/ps",1,1);
pgsubp(1,2);
pgsch(2);
pgslw(2);

        $data_file = 'ACC_NMAN';
        $yt_axis   = 'INTEGRATED TIME (day)';
        $xt_axis   = 'Time (DOM)';
        $title     = 'INTEGRATED TIME FOR NMAN';
        @ybin      = @ACC_NMAN_bin;

	$ymin      = 0.0;
	@temp      = @ybin;
	$ymax      = pop(@temp);

	if($ymax eq 0.0) {
		$ymax = 1.0;
	}

        plot_fig();

        $data_file = 'ACC_NPNT';
        $yt_axis   = 'INTEGRATED TIME (day)';
        $xt_axis   = 'Time (DOM)';
        $title     = 'INTEGRATED TIME FOR NPNT';
        @ybin      = @ACC_NPNT_bin;

	$ymin      = 0.0;
	@temp      = @ybin;
	$ymax      = pop(@temp);

	if($ymax eq 0.0) {
		$ymax = 1.0;
	}

        plot_fig();

        $data_file = 'ACC_NSUN';
        $yt_axis   = 'INTEGRATED TIME (day)';
        $xt_axis   = 'Time (DOM)';
        $title     = 'INTEGRATED TIME FOR NSUN';
        @ybin      = @ACC_NSUN_bin;

	$ymin      = 0.0;
	@temp      = @ybin;
	$ymax      = pop(@temp);

	if($ymax eq 0.0) {
		$ymax = 1.0;
	}

        plot_fig();

        $data_file = 'ACC_PWRF';
        $yt_axis   = 'INTEGRATED TIME (day)';
        $xt_axis   = 'Time (DOM)';
        $title     = 'INTEGRATED TIME FOR PWRF';
        @ybin      = @ACC_PWRF_bin;

	$ymin      = 0.0;
	@temp      = @ybin;
	$ymax      = pop(@temp);

	if($ymax eq 0.0) {
		$ymax = 1.0;
	}

        plot_fig();

        $data_file = 'ACC_PMAN';
        $yt_axis   = 'INTEGRATED TIME (day)';
        $xt_axis   = 'Time (DOM)';
        $title     = 'INTEGRATED TIME FOR PMAN';
        @ybin      = @ACC_PMAN_bin;

	$ymin      = 0.0;
	@temp      = @ybin;
	$ymax      = pop(@temp);

	if($ymax eq 0.0) {
		$ymax = 1.0;
	}

        plot_fig();

        $data_file = 'ACC_STBY';
        $yt_axis   = 'INTEGRATED TIME (day)';
        $xt_axis   = 'Time (DOM)';
        $title     = 'INTEGRATED TIME FOR STBY';
        @ybin      = @ACC_STBY_bin;

	$ymin      = 0.0;
	@temp      = @ybin;
	$ymax      = pop(@temp);

	if($ymax eq 0.0) {
		$ymax = 1.0;
	}

        plot_fig();

pgclos();
system("mv pgplot.ps $web_dir/$diryear/acc_pcad_file.ps");
#
#---- create gif files
#
system(" /usr/local/bin/perl $bin_dir/mj_plots.perl $diryear");

#
#---  printing html page.
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
                                $ymin = $ymin*1.02;
                        }else{
                                $ymin = $ymin*0.98;
                        }
                }
                $ymax = pop(@ytemp);
                if($ymax == 0.0) {
                        $ymax = 1.02;
                }else{
                        if($ymax < 0.0) {
                                $ymax = $ymax*0.99;
                        }else{
                                $ymax = $ymax*1.02;
                        }
                }
	}
}

######################################################
### plot_fig: plotting  a given data               ###
######################################################

sub plot_fig {

        pgenv($xmin, $xmax,$ymin, $ymax,0,0);

        if($data_file eq 'AOPCADMD') {
                $xstart = $xmin + 0.01;
                pgtext($xstart, 5.00, '0: NMAN');
                pgtext($xstart, 4.50, '1: NPNT');
                pgtext($xstart, 4.00, '2: NSUN');
                pgtext($xstart, 3.50, '3: PWRF');
                pgtext($xstart, 3.00, '4: RMAN');
                pgtext($xstart, 2.50, '5: STBY');
        }

	pgslw(4);
        pgpt(1, $xbin[0], $ybin[0], -1);

        for($i = 1; $i < $count; $i++) {
                pgpt(1, $xbin[$i], $ybin[$i], -1);
        }
	pgslw(2);
        pglabel("$xt_axis", "$yt_axis", "$title");
}


######################################################
### make_it_int: make a value to interger          ###
######################################################

sub make_it_int {
	($ivalue) = @_;
	$int_part = int ($ivalue);
	$diff = $ivalue -$int_part;
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
				print FILE "Please check: /data/mta/www/mta_states/MJ/";
				print FILE "$year/mta_comprehensive_data_summary$year\n\n";
				print FILE "Due to a disk space, the data was not updated\n";
				close(FILE);

				system("cat zwarning| mailx -s \"Subject: MJ summary problem detected !!\n \" -r isobe\@head.cfa.harvard.edu  isobe\@head.cfa.harvard.edu ");
				system("rm zwarning");
			}else{

				open(FH, "./temp_data_summary");
				open(OUT,">comprehensive_data_summary");
				$count = 0;
				OUTER:
				while(<FH>) {
					chomp $_;
					@stemp = split(/:/, $_);
					if($stemp[0] !~ /$diryear/){
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
### print_html_page: printing html pages           ###
######################################################

sub print_html_page {

	($usec, $umin, $uhour, $umday, $umon, $uyear, $uwday, $uyday, $uisdst)= localtime(time);

	$uyday++;
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
#--- a top MJ html page
#

	open(OUT, ">$web_dir/../comprehensive.html");
	print OUT "<!DOCTYPE html>\n";
	print OUT "<html>\n";
    print OUT "<head>\n";
	print OUT "<title> Comprehensive Summary </title>\nr";
    print OUT "<meta http-equiv='Content-Type' content='text/html; charset=utf-8' />\n";
    print OUT "<style  type='text/css'>\n";
    print OUT "table{text-align:center;margin-left:auto;margin-right:auto;border-style:solid;border-spacing:8px;border-width:2px;border-collapse:separate}\n";
    print OUT "a:link {color:#00CCFF;}\n";
    print OUT "a:visited {color:#B6FFFF;}\n";
    print OUT "</style>\n";
    print OUT "</head>\n";
	
	print OUT '<body  style="color:#FFFFFF;background-color:#000000">';
	print OUT "\n";
	print OUT '<h1 style="text-align:center">Comprehensive Summary of State Changes</h1>';
	print OUT "\n";
	print OUT '<h1 style="text-align:center">Updated ';
	print OUT "$uyear-$month-$umday  ";
	print OUT "\n";
	print OUT "<br>";
	print OUT "DAY OF YEAR: $uyday ";
	print OUT "\n";
	print OUT "<br>";
	print OUT "DAY OF MISSION: $dom ";
	print OUT '</h1>';
	print OUT "\n";
	print OUT '<hr /> ';
    print OUT "<div style='padding-top:20px;padding-bottom:20px;'>\n";
	print OUT '  <ul>';
	print OUT "\n";
	
	for($hyear = 1999; $hyear <  $diryear+1; $hyear++){
		$htmname = 'year'."$hyear".'.html';
		print OUT '<li><a href="./MJ/',"$htmname",'">Comprihensive Summary for Year ';
		print OUT "$hyear",'</a></li>',"\n";
	}
	
	print OUT '</ul>';
	print OUT "\n";
    print OUT "</div>\n";
	print OUT '<hr />';
    print OUT "<p style='padding-top:10px;'>\n";
	print OUT '    <a href="http://asc.harvard.edu/mta_days/mta_trends/trends.html">Link to MTA Trend Page</a>';
	print OUT '</p>';
	print OUT "</body>\n";
	print OUT "</html>\n";
	
	close(OUT);

#
#--- a html page for $diryear
#

	$htmname = "$web_dir".'/year'."$diryear".'.html';
	open(OUT,">$htmname");

    $input = `cat $house_keeping/template_mj`;
    $input =~ s/#YEAR#/$diryear/g;

    print OUT"$input";

	close(OUT);
}
