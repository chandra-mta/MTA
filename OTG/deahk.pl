#! /bin/env perl

open (tfile,">deahk_temp.tmp");
open (efile,">deahk_elec.tmp");

while (read(STDIN, $buf, 8) == 8) {
  @buf = unpack('V2', $buf);
  die "$file: bad sync\n" unless $buf[0] == 0x736f4166;
  local($len, $type) = (&bit(32, 10), &bit(42, 6));
  read(STDIN, $buf, ($len-2)*4, 8) == ($len-2)*4 || die "$file: $!\n";
  if ($type == 62) {
    @buf = unpack('V*', $buf);
    $date = sprintf("%9d %03d:%d.%03d%03d",
      (&bit(96, 32) << 7) + &bit(128, 16),
      &bit(149,11), (&bit(144, 5) << 12) | &bit(164, 12),
      (&bit(160, 4) << 6) | &bit(186, 6), &bit(176, 10));
  } elsif ($type == 11) {
    local($temp11, $temp12, $len, $off);
    @buf = unpack('V*', $buf);
    $len = &bit(32, 10)*32-192;
    for ($off = 160; $off <= $len; $off += 32) {
    #for ($off = 160; $off <= 5000; $off += 32) { # hack
      if (&bit($off, 8) >= 10) {
        local($query, $val) = (&bit(8+$off,8), &bit(16+$off, 16));
        $bit00 = $val if $query == 00;

        $temp01 = &temp($val) if $query == 1;
        $temp02 = &temp($val) if $query == 2;
        $temp03 = &temp($val) if $query == 3;
        $temp04 = &temp($val) if $query == 4;
        $temp05 = &temp($val) if $query == 5;
        $temp06 = &temp($val) if $query == 6;
        $temp07 = &temp($val) if $query == 7;
        $temp08 = &temp($val) if $query == 8;
        $temp09 = &temp($val) if $query == 9;
        $temp10 = &temp($val) if $query == 10;
        $temp11 = &temp($val) if $query == 11;
        $temp12 = &temp($val) if $query == 12;
        $temp13 = &temp($val) if $query == 13;

        $temp15 = &fptemp($val) if $query == 15;
        $temp16 = &fptemp($val) if $query == 16;

        $volt17 = &dpag($val) if $query == 17;
        $volt18 = &dpa5($val) if $query == 18;
        $volt19 = &dpag($val) if $query == 19;
        $volt20 = &dpa5($val) if $query == 20;

        $volt25 = &raw1($val) if $query == 25;
        $volt26 = &raw1($val) if $query == 26;
        $volt27 = &raw2($val) if $query == 27;
        $volt28 = &raw2($val) if $query == 28;
        $volt29 = &raw2($val) if $query == 29;
        $volt30 = &raw2($val) if $query == 30;
        $mamp31 = &dpag($val) if $query == 31;
        $volt32 = &dpag($val) if $query == 32;
        $volt33 = &raw1($val) if $query == 33;
        $volt34 = &raw1($val) if $query == 34;
        $volt35 = &raw2($val) if $query == 35;
        $volt36 = &raw2($val) if $query == 36;
        $volt37 = &raw2($val) if $query == 37;
        $volt38 = &raw2($val) if $query == 38;
        $mamp39 = &dpag($val) if $query == 39;
        $volt40 = &dpag($val) if $query == 40;
      }
    }
    printf tfile "%s\t%.2f\t%.2f\t%.2f\t%.2f\t%.2f\t%.2f\t%.2f\t%.2f\t%.2f\t%.2f\t%.2f\t%.2f\t%.2f\t%.2f\t%.2f\n", $date, $temp01, $temp02, $temp03, $temp04, $temp05, $temp06, $temp07, $temp08, $temp09, $temp10, $temp11, $temp12, $temp13, $temp15, $temp16;
    printf efile "%s\t%.2f\t%.2f\t%.2f\t%.2f\t%.2f\t%.2f\t%.2f\t%.2f\t%.2f\t%.2f\t%.2f\t%.2f\t%.2f\t%.2f\t%.2f\t%.2f\t%.2f\t%.2f\t%.2f\t%.2f\n", $date, $volt17, $volt18, $volt19, $volt20, $volt25, $volt26, $volt27, $volt28, $volt29, $volt30, $mamp31, $volt32, $volt33, $volt34, $volt35, $volt36, $volt37, $volt38, $mamp39, $volt40;
  }
}

close tfile;
close efile;
exit(0);

sub temp {
  local($t) = (shift()-2048)*1.14;
  if ($t <= 10) {return "Short";}
  if ($t >= 2040) {return "Open";}
  $u = log(5230*$t/(2048-$t));
  return -273.16 + 1/(1.4733e-3 + 2.372e-4*$u + 1.074e-7*$u*$u*$u);
  #return shift();
}

sub fptemp {
  local($t) = (shift()-2048)/1.255;
  return -246.3 + 0.1863*$t + 1.415e-5*$t*$t - 1.885e-9*$t*$t*$t;
  #return shift();
}

sub dpag {
  local($t) = shift();
  return -2.5 + 0.00122*$t;
  #return shift();
}

sub dpa5 {
  local($t) = shift();
  return -20.83 + 0.01017*$t;
  #return shift();
}

sub raw1 {
  local($t) = shift();
  return -41.90 + 0.02044*$t;
  #return shift();
}

sub raw2 {
  local($t) = shift();
  return -20.83 + 0.01017*$t;
  #return shift();
}

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
