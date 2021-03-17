#!/soft/ascds/DS.release/ots/bin/perl

BEGIN
{
#    $ENV{SYBASE} = "/soft/SYBASE_OCS15.5";
    $ENV{SYBASE} = "/soft/SYBASE15.7";
    }


use DBI;
use DBD::Sybase;

#################################################################################################
#												#
#	sib_corr_find_observation.perl: create a list of observations done during the period 	#
#				given as arguments						#
#
#       ---- THIS IS A DS TEST VERSION ----
#												#
#		author: t. isobe (tisobe@cfa.harvard.edu)					#
#												#
#		last update: May 30, 2017							#
#												#
#################################################################################################

#
#--- get user and pasword
#

$dare   = `cat /data/mta/MTA/data/.dare`;
$hakama = `cat /data/mta/MTA/data/.hakama`;

chomp $dare;
chomp $hakama;

#
#----- format for input dates are: mm/dd/yy,hh:mm:ss, e.g., 10/20/04,00:00:00
#
$start = $ARGV[0];
$stop  = $ARGV[1];

chomp $start;
chomp $stop;

open(OUT, ">./input_line");             # input script for arc4gl
print OUT "operation=browse\n";
print OUT "dataset=flight\n";
print OUT "detector=acis\n";
print OUT "level=1\n";
print OUT "filetype=evt1\n";
print OUT "tstart=$start\n";
print OUT "tstop=$stop\n";
print OUT "go\n";
close(OUT);

#
#---- use arc4gl to get observations done during the period
#

system("echo $hakama |arc4gl -U$dare -Sarcocc -iinput_line > zout");

open(FH, './zout');
@obsid_list = ();
while(<FH>){
	chomp $_;
	if($_ =~ /evt1.fits/){
		@atemp = split(/_/, $_);
		@btemp = split(/f/, $atemp[0]);
		push(@obsid_list, $btemp[1]);
	}
}
close(FH);
system("rm zout");

#
#--- remove duplicated obsid
#

$first = shift(@obsid_list);
@new   = ($first);

OUTER:
foreach $ent (@obsid_list){
	foreach $comp (@new){
		if($ent =~ /$comp/){
			next OUTER;
		}
	}
	push(@new, $ent);
}

@obsid_list = @new;

#
#----- setting for sql database access
#

$db_user = "mtaops_internal_web";
$server  = "ocatsqlsrv";
#$server  = "sqlocc";
#$server  = "sqlxtest";

#$db_passwd =`cat /data/mta4/CUS/www/Usint/Pass_dir/.targpass`;
$db_passwd =`cat /data/mta4/CUS/www/Usint/Pass_dir/.targpass_internal`;
chomp $db_passwd;

@date_list = ();

OUTER:
foreach $obsid (@obsid_list){
	if($obsid > 50000){
		next OUTER;
	}
#--------------------------------------
#-------- open connection to sql server
#--------------------------------------

	my $db = "server=$server;database=axafocat";
	$dsn1  = "DBI:Sybase:$db";
	$dbh1  = DBI->connect($dsn1, $db_user, $db_passwd, { PrintError => 0, RaiseError => 1});

#------------------------------------------------------
#---------------  get stuff from target table, clean up
#------------------------------------------------------

	$sqlh1 = $dbh1->prepare(qq(select
        	obsid,targid,seq_nbr,targname,instrument,soe_st_sched_date,lts_lt_plan 
	from target  where obsid=$obsid));
	
	$sqlh1->execute();
	@targetdata = $sqlh1->fetchrow_array;
	$sqlh1->finish;
	
	$targid            = $targetdata[1];
	$seq_nbr           = $targetdata[2];
	$targname          = $targetdata[3];
	$instrument	   = $targetdata[4];
	$soe_st_sched_date = $targetdata[5];
	$lts_lt_plan       = $targetdata[6];
	
	$seq_nbr           =~ s/\s+//g;
	$targname          =~ s/\s+//g;
	$instrument        =~ s/\s+//g;
	$lts_lt_plan       =~ s/\s+//g;

	@atemp = split(//, $targname);
	$name = '';
	for($i = 0; $i < 14; $i++){
		if($atemp[$i] eq ''){
			$add_char = ' ';
		}else{
			$add_char = $atemp[$i];
		}
		$name = "$name"."$add_char"
	}

	convert_time_format();			#---- change date to sec from 1998.1.1
	
	$line = "$obsid\t$name\t$instrument\t$soe_st_sched_date\t$sec_date\t$targid\t$seq_nbr";
	%{data.$sec_date} = (line => ["$line"]);
	push(@date_list, $sec_date);
}

@date_list_sorted = sort{$a<=>$b} @date_list;

open(OUT, "> ./acis_obs");
foreach $sdate (@date_list_sorted){
	print OUT  "${data.$sdate}{line}[0]\n";
}
close(OUT);

###########################################################
### convert_time_format: change to sec from 1998.1.1    ###
###########################################################

sub convert_time_format{
	@atemp = split(/\s+/, $soe_st_sched_date);
	$month = $atemp[0];
	$day   = $atemp[1];
	$year  = $atemp[2];

	if($atemp[3] =~ /AM/){
		@btemp = split(/AM/, $atemp[3]);
		$time  = $btemp[0];
	}else{
		@btemp = split(/PM/, $atemp[3]);
		@ctemp = split(/:/,  $btemp[0]);
		$hour  = $ctemp[0] + 12;
		$time  = "$hour".":$ctemp[1]";
	}

	$time = "$time".":00";

	if($month =~ /Jan/i){
		$ydate = $day;
		$month = 1;
	}elsif($month =~ /Feb/i){
		$ydate = $day + 31;
		$month = 2;
	}elsif($month =~ /Mar/i){
		$ydate = $day + 59;
		$month = 3;
	}elsif($month =~ /Apr/i){
		$ydate = $day + 90;
		$month = 4;
	}elsif($month =~ /May/i){
		$ydate = $day + 120;
		$month = 5;
	}elsif($month =~ /Jun/i){
		$ydate = $day + 151;
		$month = 6;
	}elsif($month =~ /Jul/i){
		$ydate = $day + 181;
		$month = 7;
	}elsif($month =~ /Aug/i){
		$ydate = $day + 212;
		$month = 8;
	}elsif($month =~ /Sep/i){
		$ydate = $day + 243;
		$month = 9;
	}elsif($month =~ /Oct/i){
		$ydate = $day + 273;
		$month = 10;
	}elsif($month =~ /Nov/i){
		$ydate = $day + 304;
		$month = 11;
	}elsif($month =~ /Dec/i){
		$ydate = $day + 333;
		$month = 12;
	}

	$test = int($year/4) * 4;

	if($test = $year){
		if($month > 2){
			$ydate++;
		}
	}

	$ldate    = "$year".":$ydate".":$time";
	$sec_date = `axTime3 $ldate t d u s`;
	$sec_date = int ($sec_date);
}

