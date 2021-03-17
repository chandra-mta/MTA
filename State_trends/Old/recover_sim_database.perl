#!/usr/bin/perl
use PGPLOT;

#########################################################################################
#											#
#	recover_sim_database.perl: this extract state sim data for a given data period	#
#		e.g. 01/01/12,00:00:00 01/02/12,00:00:00				#
#											#
#		 author: t. isobe (tisobe@cfa.harvard.edu)				#
#											#
#		last update Jan 30, 2013						#
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


$dare = `cat /data/mta/MTA/data/.dare`;
chomp $dare;
$hakama = `cat /data/mta/MTA/data/.hakama`;
chomp $hakama;

##############################################################

$list = `ls `;
if($list =~ /Temp_comp/){
}else{
        system("mkdir ./Temp_comp");
}


#
#--- remove the past system log
#

system("rm ./systemlog");

$tstart = $ARGV[0];
$tstop  = $ARGV[1];
chomp $tstart;
chomp $tsop;

open(OUT, ">./command");
print OUT "operation=browse\n";
print OUT "dataset = flight\n";
print OUT "detector = telem\n";
print OUT "level = raw\n";
print OUT "tstart = $tstart\n";
print OUT "tstop  = $tstop\n";
print OUT "go\n";
close(OUT);

system("echo $hakama | arc4gl -U$dare -Sarcocc -i./command > zout");
system("rm ./command");

open(FH, "./zout");
@list = ();
OUTER:
while(<FH>){
        if($_ !~ /Dump_EM/){
                next OUTER;
        }elsif($_ =~ /sto.log/){
                next OUTER;
        }
        chomp $_;
        @atemp = split(/\s+/, $_);
        push(@list, $atemp[0]);
}
close(FH);
system("rm zout");

foreach $ent (@list){
        print "$ent\n";

        open(OUT, ">./Temp_comp/command");
        print OUT "operation=retrieve\n";
        print OUT "dataset = flight\n";
        print OUT "detector = telem\n";
        print OUT "level = raw\n";
        print OUT "filename=$ent\n";
        print OUT "go\n";
        close(OUT);

        system("cd ./Temp_comp; echo $hakama | arc4gl -U$dare -Sarcocc -i./command ");
        system("rm ./Temp_comp/*log.gz ./Temp_comp/command");

        extract_data($ent);
	system("rm acissimpos_*");
}


##################################################################################################################################
##################################################################################################################################
##################################################################################################################################

sub extract_data{


	($name) = @_;
#
#--- gzip a dump data and extract data we need for the plots
#
	$data = "./Temp_comp/$name".".gz";
	system("gzip -dc $data| $bin_dir/acorn -nCO $data_dir/simpos_acis2.scr -T -o");

	system("cat acissimpos* > alldata");

#
#--- remove headers
#

	system("sed -f $data_dir/sim_sedscript1 alldata > alldata_cleaned");

	system("sort alldata_cleaned > alldata_cleaned_sorted");
	
	system("nawk -F\"\\t\" -f $data_dir/sim_nawkscript alldata_cleaned_sorted       > alldata_cleaned_sorted_timed");
	
	system("cat alldata_cleaned_sorted_timed >> sim_data_summary");

	system("rm alldata*");
	system("rm ./Temp_comp/*");
}



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
