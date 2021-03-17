#!/soft/ascds/DS.release/ots/bin/perl

use DBI;
use DBD::Sybase;

#########################################################################################
#											#
#	mk_img_html.perl: this script creates html page showing pspc images of given	#
#			  acis observation list (acis_obs)				#
#											#
#		author: t. isobe (tisobe@cfa.harvard.edu)				#
#											#
#		last update: Apr 23, 2010						#
#											#
#########################################################################################

open(FH, "acis_obs");		#--- list of the observation. the obsid is in the first col
@list = ();
@name = ();
while(<FH>){
	chomp $_;
	@atemp = split(/\s+/, $_);
	push(@list, $atemp[0]);
	push(@name, $atemp[1]);
}
close(FH);

$pass_dir = '/proj/web-icxc/cgi-bin/obs_ss/.Pass_dir/';
$mp_http      = 'http://asc.harvard.edu/'; 

open(OUT, ">target_image.html");

print OUT "<html>\n";
print OUT "<body>\n";

$i = 0;
foreach $obsid(@list){
	
	read_databases();

        $ros_http  = "$mp_http/targets/"."$seq_nbr".'/'."$seq_nbr".'.'."$obsid".'.pspc.gif';

	print OUT  "<h2>$obsid\t $seq_nbr\t$name[$i]</h2>";
        print OUT  "<img src=\"$ros_http\" height='600' width='600'>";
#	print OUT  "<a href = $ros_http  target='blank'><img align=middle src=\"$mp_http/targets/webgifs/ros.gif\"></a>";

	print OUT  "<br><br>\n";
	$i++;
}
print OUT "</html>\n";
close(OUT);


################################################################################
### sub read_databases: read out values from databases                       ###
################################################################################

sub read_databases{

#------------------------------------------------
#-------  database username, password, and server
#------------------------------------------------

        $db_user = "browser";
        $server  = "ocatsqlsrv";

#       $db_user="browser";
#       $server="sqlbeta";

        $db_passwd =`cat $pass_dir/.targpass`;
        chop $db_passwd;

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
                obsid,targid,seq_nbr,targname,obj_flag,object,si_mode,photometry_flag,
                vmagnitude,ra,dec,est_cnt_rate,forder_cnt_rate,y_det_offset,z_det_offset,
                raster_scan,dither_flag,approved_exposure_time,pre_min_lead,pre_max_lead,
                pre_id,seg_max_num,aca_mode,phase_constraint_flag,ocat_propid,acisid,
                hrcid,grating,instrument,rem_exp_time,soe_st_sched_date,type,lts_lt_plan,
                mpcat_star_fidlight_file,status,data_rights,tooid,description,
                total_fld_cnt_rate, extended_src,uninterrupt, multitelescope,observatories,
                tooid, constr_in_remarks, group_id, obs_ao_str, roll_flag, window_flag, spwindow_flag
        from target where obsid=$obsid));
        $sqlh1->execute();
        @targetdata = $sqlh1->fetchrow_array;
        $sqlh1->finish;

#--------------------------------------------------------------------------
#------- fill values from target table
#------- doing this the long way so I can see what I'm doing and make sure
#------- everything is accounted for
#--------------------------------------------------------------------------

        $targid                         = $targetdata[1];
        $seq_nbr                        = $targetdata[2];
        $targname                       = $targetdata[3];
        $obj_flag                       = $targetdata[4];
        $object                         = $targetdata[5];
        $si_mode                        = $targetdata[6];
        $photometry_flag                = $targetdata[7];
        $vmagnitude                     = $targetdata[8];
        $ra                             = $targetdata[9];
        $dec                            = $targetdata[10];
        $est_cnt_rate                   = $targetdata[11];
        $forder_cnt_rate                = $targetdata[12];
        $y_det_offset                   = $targetdata[13];
        $z_det_offset                   = $targetdata[14];
        $raster_scan                    = $targetdata[15];
        $dither_flag                    = $targetdata[16];
        $approved_exposure_time         = $targetdata[17];
        $pre_min_lead                   = $targetdata[18];
        $pre_max_lead                   = $targetdata[19];
        $pre_id                         = $targetdata[20];
        $seg_max_num                    = $targetdata[21];
        $aca_mode                       = $targetdata[22];
        $phase_constraint_flag          = $targetdata[23];
        $proposal_id                    = $targetdata[24];
        $acisid                         = $targetdata[25];
        $hrcid                          = $targetdata[26];
        $grating                        = $targetdata[27];
        $instrument                     = $targetdata[28];
        $rem_exp_time                   = $targetdata[29];
        $soe_st_sched_date              = $targetdata[30];
        $type                           = $targetdata[31];
        $lts_lt_plan                    = $targetdata[32];
        $mpcat_star_fidlight_file       = $targetdata[33];
        $status                         = $targetdata[34];
        $data_rights                    = $targetdata[35];
        $tooid                          = $targetdata[36];
        $description                    = $targetdata[37];
        $total_fld_cnt_rate             = $targetdata[38];
        $extended_src                   = $targetdata[39];
        $uninterrupt                    = $targetdata[40];
        $multitelescope                 = $targetdata[41];
        $observatories                  = $targetdata[42];
        $tooid                          = $targetdata[43];
        $constr_in_remarks              = $targetdata[44];
        $group_id                       = $targetdata[45];
        $obs_ao_str                     = $targetdata[46];
        $roll_flag                      = $targetdata[47];
        $window_flag                    = $targetdata[48];
        $spwindow                       = $targetdata[49];

        $dbh1->disconnect();


        $targid                 =~ s/\s+//g;
        $seq_nbr                =~ s/\s+//g;

}
