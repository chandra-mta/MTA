#!/usr/bin/perl 

$input = `ls /data/mta/Script/ACIS/SIB/Correct_excess/Lev2/Outdir/lres/Save/*fits`;
@list  = split(/\n+/, $input);

$save = '/data/mta/Script/ACIS/SIB/Correct_excess/Lev1/Outdir/lres/Save/';
system("mkdir $save");
foreach $ent (@list){

    $ent =~ s/Lev2/Lev1/;
    $ent =~ s/Save//;
    $ent =~ s/N/\*N/;
    system("mv $ent $save");
}
