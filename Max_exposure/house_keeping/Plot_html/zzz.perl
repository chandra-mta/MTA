#!/usr/bin/perl 

$input = `ls *_*.html`;
@list  = split(/\s+/, $input);

foreach $ent (@list){
	$line = `cat $ent`;
	$line =~ s/png/gif/g;
	open(OUT, ">$ent");
	print OUT "$line";
}

