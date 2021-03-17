#!/home/ascds/DS.release/ots/bin/perl
use CGI qw/:standard :netscape /;

#########################################################################################################
#                                                                                                       #
#       mta_script_list.cgi:    create a list of MTA managed scripts                                    #
#                                                                                                       #
#           author: t. isobe (tisobe@cfa.harvard.edu)                                                   #
#                                                                                                       #
#           last updated:   Sep 30, 2014                                                                #
#                                                                                                       #
#########################################################################################################

#
#--- setting a couple of parameters
#

$thtml = 'https://cxc.cfa.harvard.edu/mta_days/mta_script_list';
$flev  = '/data/mta/www/mta_script_list';
#
#--- read each user's html pages and directories
#
$input = `ls -d /data/mta/www/mta_script_list/Scott/*`;
@sdata = split(/\n+/, $input);

$input = `ls -d  /data/mta/www/mta_script_list/Brad/*`;
@bdata = split(/\n+/, $input);

$input = `ls -d  /data/mta/www/mta_script_list/Takashi/*`;
@tdata = split(/\n+/, $input);

#
#-- print header part of the page 
#

print header;

print "<html> ";

print "<head> ";
print "<link rel='stylesheet' type='text/css' href='https://cxc.cfa.harvard.edu/mta_days/mta_script_list/house_keeping/style_sheet.css' /> ";
print "<style> ";
print "    td{padding:5px} ";
print "    th{padding:5px text-align:center} ";
print "    span{padding-left:10px} ";
print "</style> ";

print "<title>MTA Group Managed Software/Script List</title> ";

print "<script  src='https://cxc.cfa.harvard.edu/mta_days/mta_script_list/house_keeping/j_module.js'> </script> ";

print "</head> ";

#
#-- main part starts here
#

print "<body> ";

print "<h2 style='background-color:bluecolor:#FAEBD7margin-right:40px'> ";
print "<u>MTA Group Managed  Sofware/Script List</u> ";
print "</h2> ";
print "<div style='padding-bottom:20px'> ";
print "</div> ";

#-------------------------------------------------------------------------------------------------------#
#--                            Scott Section Starts                                                   --#
#-------------------------------------------------------------------------------------------------------#

print "<h3>Software/Scripts Managed by <a href='mailto:swolk\@cfa.harvard.edu'>Scott Wolk</a></h3> ";

$uname = 'Scott';
@indata = @sdata;
print_link();


print "<div style='padding-top:20px'> ";
print "</div> ";
print "<hr /> ";
print "<div style='padding-top:20px'> ";
print "</div> ";


#-------------------------------------------------------------------------------------------------------#
#--                             Brad Section Starts                                                   --#
#-------------------------------------------------------------------------------------------------------#

print "<h3>Software/Scripts Managed by <a href='mailto:brad\@cfa.harvard.edu'>Brad Spitzbart</a></h3> ";


$uname = 'Brad';
@indata = @bdata;
print_link();


print "<div style='padding-top:20px'> ";
print "</div> ";
print "<hr /> ";
print "<div style='padding-top:20px'> ";
print "</div> ";


#-------------------------------------------------------------------------------------------------------#
#--                            Takashi Section Starts                                                 --#
#-------------------------------------------------------------------------------------------------------#


print "<h3>Software/Scripts Managed by <a href='mailto:isobe\@cfa.harvard.edu'>Takashi Isobe</a></h3> ";


$uname = 'Takashi';
@indata = @tdata;
print_link();



print "<div style='padding-top:20px'> ";
print "</div> ";
print "<hr /> ";


#
#--- closing part
#

print "<p> ";
print "If you have questions about this page, email to <a href='mailto:tisobe\@cfa.harvard.edu'>tisobe\@cfa.harvard.edu</a> ";
print "</p> ";

print "</body> ";
print "</html> ";



#----------------------------------------------------------------------------------------------
#-- print_link: separate html pages to top and sub directories and print the links          ---
#----------------------------------------------------------------------------------------------

sub print_link{

    @html_list = ();                    #--- save the top level html page names
    $cnt       = 0;                     #--- counter to check whether any top level html pages exist
    @dir_name  = ();                    #--- save the sub directory names

    foreach  $ent (@indata){
#
#--- top level html pages
#
        @atemp = split(/$uname\//, $ent);
        if($ent =~ /.html/){
            push(@html_list, $atemp[1]);
            $cnt++;
        }else{
#
#--- create holders for sub directory html pages
#
            if(!(-f $ent) && !(-l $ent)){
                $dir   = $atemp[1];
                if($dir !~ /^Temp/){
                    $dir   =~ s/\///g;
                    @{$dir} = ();
                    push(@dir_name,$dir);
                }
            }
        }
    }
#
#--- printing top level html page links
#
    if($cnt > 0){
        print "<ul>";
        foreach $ent (@html_list){
            if($ent =~ /_template/){                        #--- ignoure template page
                next;
            }
            $shtml = "$thtml/$uname/$ent";                  #--- web address
            $efile = "$flev/$uname/$ent";                   #--- physical location

            print_link_sub($shtml, $efile);
        }
        print "</ul>";
    }
#
#--- get sub level html pages
#
    foreach  $dir (@dir_name){
        $test = `ls $flev/$uname/$dir/*`;                   #--- testing the directory has html pages
        if($test =~ /.html/){
            @atemp = split(/\n+/, $test);
            foreach $ent (@atemp){
                @btemp = split(/$dir\//, $ent);
                push(@{$dir}, $btemp[1]);
            }
        }    
    }
#
#--- print sub level html page links
#
    foreach $dir (@dir_name){
#
#--- create the title of the sub directory entries
#
        $name  = $dir;
        $name  =~ s/_/ /g;
        $dname = "$uname/$dir";
#
#--- check the directory actually has any entries
#
        $cnt = 0;
        foreach(@{$dir}){
            $cnt++;
        }
        if($cnt > 0){
            print "<h3>$name</h3>";
            print "<ul>";
            foreach $ent (@{$dir}){
                $shtml = "$thtml/$uname/$dir/$ent";
                $efile = "$flev/$uname/$dir/$ent";

                print_link_sub($shtml, $efile);
            }
            print "</ul>";
        }
    }
}

#----------------------------------------------------------------------------------------------
#-- print out each html link                                                                ---
#----------------------------------------------------------------------------------------------

sub print_link_sub{
#
#   input: shtml    --- a full html address of the page
#          efile    --- a full physical address of the file
#

    my($shtml, $efile) = @_;
#
#--- find the title of the html page; it assumes that of between <title> tags
#
    open(FH, $efile);

    @data = ();
    while(<FH>){
        chomp $_;
        push(@data, $_);
    }
    close(FH);

    foreach $line (@data){
        if ($line =~ /<title>/){
            @atemp = split(/<title>/, $line);
            @btemp = split(/<\\title>/, $atemp[1]);
            $title = $btemp[0];
            last; 
        }
    }

    print "<li><a href='$shtml'>$title</a>\n";

    $mtime = localtime((stat $efile)[9]);
    @temp  = split(/\s+/, $mtime);
    $mtime = "$temp[1] $temp[2], $temp[4]";

    print "<span style='padding-left:20px;font-size:90%'>(Last Update: $mtime)</span></li>\n";
}
