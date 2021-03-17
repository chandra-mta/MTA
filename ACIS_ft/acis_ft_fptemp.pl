#!/usr/bin/env /usr/local/bin/perl

#################################################################################
#                                       										#
#	acis_focal_fptemp.pl: Peter Ford's perl script which reads focal temp	    #
#			      data from telemetered data			                        #
#				(pgf@space.mit.edu)				                                #
#										                                        #
#		/opt/local/bin/gzip -dc $ent 					                        #
#			|$bin_data/Acis_focal/getnrt -O $* 			                        #
#			| $bin_dir/acis_focal_fptemp.pl				                        #
#										                                        #
#										                                        #
#	noted by t. isobe							                                #
#										                                        #
#################################################################################

while (read(STDIN, $buf, 8) == 8) {
    @buf = unpack('V2', $buf);
    die "$file: bad sync\n" unless $buf[0] == 0x736f4166;
    local($len, $type) = (&bit(32, 10), &bit(42, 6));
    read(STDIN, $buf, ($len-2)*4, 8) == ($len-2)*4 || die "$file: $!\n";

    if ($type == 62) {

        @buf  = unpack('V*', $buf);
        $date = sprintf("%9d %03d:%d.%03d%03d",
            (&bit(96, 32) << 7) + &bit(128, 16),
            &bit(149,11), (&bit(144, 5) << 12) | &bit(164, 12),
            (&bit(160, 4) << 6) | &bit(186, 6), &bit(176, 10));

    } elsif ($type == 11) {

        local($temp11, $temp12, $len, $off);
        @buf = unpack('V*', $buf);
        $len = &bit(32, 10)*32-192;
        for ($off = 160; $off <= $len; $off += 32) {

            if (&bit($off, 8) >= 10) {

                local($query, $val) = (&bit(8+$off,8), &bit(16+$off, 16));
                $temp12 = &temp($val) if $query == 15;
                $temp11 = &temp($val) if $query == 16;
            }
        }
        printf "%s %6.2f %6.2f\n", $date, $temp11, $temp12;
    }
}

exit(0);

#
#--------------------------------------------------------------------------
#
sub temp {
    local($t) = (shift()-2048)/1.255;
    return -246.3 + 0.1863*$t + 1.415e-5*$t*$t - 1.885e-9*$t*$t*$t;
}
#
#--------------------------------------------------------------------------
#
sub bit {
    local($off, $len) = @_;
    local($bit, $n, $exp, $i) = $off & 31;
    if ($bit + $len > 32) {
        $n = $buf[$off >> 5] >> $bit;
        $n &= 0x7fffffff >> ($bit - 1) if $bit;
        $exp = 32 - $bit;
        $off += $exp;
        $len -= $exp;
        $bit = 0;
    }
    $i = $buf[$off >> 5] >> $bit;
    $i &= 0x7fffffff >> (31 - $len) if $len < 32;
    $n += $i << $exp;
    return $n;
}
