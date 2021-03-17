#!/usr/local/bin/perl -w

#-------------------------------------------------------------------------------
#
# prefilter and format sim tracelogs for input into monitor_sim.pl
#
#--------------------------------------------------------------------------------

my $work_dir = "/data/mta/Script/SIM/Exc/";

my $tl_dir = "/data/mta/Script/SIM/Exc/TL/";  # repros

$lasttime=0;
foreach $file (<$tl_dir/*SIM*tl*>) {
    chomp $file;

    if ($file =~ /\.gz$/) {
        `/usr/bin/gunzip $file`;
        $file = substr($file, 0, $#file-2);
    }

    open TL, $file;
    open (OUT,">$file.tmp");

    my $hdr  = <TL>;
    my $line = <TL>;

    while (defined ($line = <TL>)) {
        $line =~ s/^\s+|\s+$//g;
        $date_string = substr($line, 0, index($line, "\t"));
        $tsec        = &convert_time($date_string);

        if ($tsec - $lasttime > 32.0) {
#
#--- convert to yyyydoy.hhmmss, assume given yy dd hh:mm:ss
#
            my $time  = aform2dform(substr($line, 0, index($line, "\t")));
            $line     = sprintf "%16.8f %s\n", $time, substr($line, index($line, "\t"));
            printf OUT $line;

            $lasttime = $tsec;
        } # if ($tsec - $lasttime > 32.0) {
    }
    close TL;
    close OUT;
}

#---------------------------------------------------------------------------
#---------------------------------------------------------------------------
#---------------------------------------------------------------------------

sub aform2dform_xx {
  
    my @yrdoy = split(' ', $_[0]);
print "yrdoy: @yrdoy\n";
#    my $year  = $yrdoy[0] + 1900;
    my $year  = $yrdoy[0];
    my $doy   = "00".$yrdoy[1];
    
#    my $whats_left;
#
#    for ($i = 2; $i <= $#yrdoy; $i++) {
#        $whats_left .= $yrdoy[$i];
#    }

#    my @hrminsec = split(':', $whats_left);
    my @hrminsec = split(/:/, $yrdoy[2]);
    my $hour     = "0".$hrminsec[0];
    my $min      = "0".$hrminsec[1];
    my $sec      = $hrminsec[2];

    $_ = substr($sec, 0, index($sec, "\."));

    $count = tr/0-9//;
    if ($count eq 1) {$sec = "0".$sec;}

    $sec =~ s/\.//;
    
    my $dec = sprintf "%4s%3s\.%2s%2s%s", 
            $year,substr($doy, -3, 3), substr($hour, -2, 2), substr($min, -2, 2), $sec;

    return $dec;
}


#---------------------------------------------------------------------------
#---------------------------------------------------------------------------
#---------------------------------------------------------------------------

sub aform2dform {
  
    my @line  = split(/:/, $_[0]);
    my @part1 = split(/\s+/, $line[0]);
    my $year  = $part1[0];
    my $doy   = "00".$part1[1];
    
    $part1[2] =~ s/\s+//g;
    my $hour     = "0".$part1[2];
    $line[1]  =~ s/\s+//g;
    my $min      = "0".$line[1];
    $line[2]  =~ s/\s+//g;
    my $sec      = $line[2];

    $_ = substr($sec, 0, index($sec, "\."));

    $count = tr/0-9//;
    if ($count eq 1) {$sec = "0".$sec;}

    $sec =~ s/\.//;

    my $dec = sprintf "%4s%3s\.%2s%2s%s", 
            $year,substr($doy, -3, 3), substr($hour, -2, 2), substr($min, -2, 2), $sec;

    return $dec;
}

#---------------------------------------------------------------------------
#---------------------------------------------------------------------------
#---------------------------------------------------------------------------

# this is obselete, but might be handy somewhere else
#sub aform2dec {
#  #print "working on $_[0]\n";
#  my @yrdoy = split(' ', $_[0]);
#  my $year = $yrdoy[0] + 1900;
#  my $doy  = $yrdoy[1];
#
#  my $whats_left;
#  for ($i = 2; $i <= $#yrdoy; $i++) {
#    $whats_left .= $yrdoy[$i];
#  }
#  my @hrminsec = split(':', $whats_left);
#  my $hour = $hrminsec[0];
#  my $min  = $hrminsec[1];
#  my $sec  = $hrminsec[2];
#
#  my $part = $hour/24.0 + $min/1440.0 + $sec/86400.0;
#  my $dec = $year*1000 + $doy + $part;
#  #print "$_[0] converted to $dec\n";
#  return $dec;
#}


#---------------------------------------------------------------------------
#---------------------------------------------------------------------------
#---------------------------------------------------------------------------

sub convert_time {
    my @yrday = split(' ', $_[0]);
    my $year = $yrday[0];
    my $day  = $yrday[1];

    my $hhmmss="";
    for ($i=2;$i<=$#yrday;$i++) {
      $hhmmss.=$yrday[$i];
    }
    my @hrminsec = split(':', $hhmmss);
    my $hour = $hrminsec[0];
    my $min  = $hrminsec[1];
    my $sec  = $hrminsec[2];

    my $totsecs = 0;
    $totsecs = $sec;
    $totsecs += $min  * 60;
    $totsecs += $hour * 3600;

    my $totdays = 0;
    $totdays = $day-1;

    if ($year < 1900) {
      if ($year >= 98) {
          $year = 1998 + ($year - 98);
      }
      else {
          $year = 2000 + $year;
      }
    } # if ($year < 1900) {

    # add days for past leap years
    if ($year > 2000)
    {
        # add one for y2k
        $totdays++;
        # Number of years since 2000. -1 for already counted current leap
        $years = $year - 2000 - 1;
        $leaps = int ($years / 4);
        $totdays += $leaps;
    }

    $totdays += ($year - 1998) * 365;

    $totsecs += $totdays * 86400;

    return $totsecs;
}
