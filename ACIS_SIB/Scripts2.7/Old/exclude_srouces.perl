#!/usr/bin/perl 

#########################################################################################################
#													#
#	exclude_srouces.perl: remove the area around the main source and all point sources from data	#
#			      probably this is a good one to use evt2 files as it takes too much time	#
#			      run on evt1 file. The results save in Reg_files can be used to removed	#
#			      sources from evt 1 files. 						#
#													#
#		author: t. isobe (tisobe@cfa.harvard.edu)						#
#													#
#		last update: Jun 03, 2013								#
#													#
#########################################################################################################


#
#--- read a fits file name (should be in a zipped form).
#

$in_fits = $ARGV[0];

#
#--- extrad some information from header
#

system("dmlist $in_fits opt=head > zhead");

@ccd_list = ();

open(FH, "zhead");
while(<FH>){
	chomp $_;
#
#--- find out which ccds were used from bias file names
#
	if($_ =~ /bias file used/){
		@atemp = split(/CCD/, $_);
		$atemp[1] =~ s/\s+//g;
		push(@ccd_list, $atemp[1]);
	}
	if($_ =~ /SIM_X/){
		@atemp = split(/\s+/, $_);
		$sim_x = $atemp[2];
		$sim_x =~ s/\s+//g;
	}
	if($_ =~ /SIM_Y/){
		@atemp = split(/\s+/, $_);
		$sim_y = $atemp[2];
		$sim_y =~ s/\s+//g;
	}
	if($_ =~ /SIM_Z/){
		@atemp = split(/\s+/, $_);
		$sim_z = $atemp[2];
		$sim_z =~ s/\s+//g;
	}
	if($_ =~ /RA_NOM/){
		@atemp = split(/\s+/, $_);
		$ra_nom = $atemp[2];
		$ra_nom =~ s/\s+//g;
	}
	if($_ =~ /DEC_NOM/){
		@atemp = split(/\s+/, $_);
		$dec_nom = $atemp[2];
		$dec_nom =~ s/\s+//g;
	}
	if($_ =~ /ROLL_NOM/){
		@atemp = split(/\s+/, $_);
		$roll_nom = $atemp[2];
		$roll_nom =~ s/\s+//g;
	}
	if($_ =~ /RA_TARG/){
		@atemp = split(/\s+/, $_);
		$ra_targ = $atemp[2];
		$ra_targ =~ s/\s+//g;
	}
	if($_ =~ /DEC_TARG/){
		@atemp = split(/\s+/, $_);
		$dec_targ = $atemp[2];
		$dec_targ =~ s/\s+//g;
	}
}
close(FH);
system("rm zhead");

#
#--- guess a source center position on the sky coordinates from the information extracted from the header
#

system("dmcoords none none opt=cel ra=$ra_targ dec=$dec_targ sim='$sim_x $sim_y $sim_z' detector=acis celfmt=deg ra_nom=$ra_nom dec_nom=$dec_nom roll_nom=$roll_nom  ra_asp=\"\)ra_nom\" dec_asp=\"\)dec_nom\" verbose=1 > coord_out");

open(FH, 'coord_out');
OUTER:
while(<FH>){
	chomp $_;
	if($_ =~ /SKY/){
		@atemp = split(/\s+/, $_);
		$skyx  = $atemp[1];
		$skyy  = $atemp[2];
		last OUTER;
	}
}
close(FH);

system("rm coord_out");

#
#-- keep the record of the source position for the later use (e.g. used for evt1 processing);
#

$coord_file = $in_fits;
$coord_file =~ s/\.fits\.gz/_source_coord/;
open(OUT, ">$coord_file");
print OUT "$skyx:$skyy\n";
close(OUT);
system("mv *_source_coord Reg_files/");


@temp = sort{$a<=>$b}@ccd_list;
@ccd_list = @temp;

#
#-- remove the 200 pix radius area around the source
#

$line = "$in_fits".'[exclude sky=circle('."$skyx,$skyy".', 200)]';
system("dmcopy \"$line\" outfile=source_removed.fits");


$o_fits = $in_fits;
if($o_fits =~ /gz/){
	$o_fits =~ s/\.gz//;
}

#
#--- get a file size: will be used to measure the size of removed area later.
#--- assumption here is the x-ray hit ccd evenly, but of course it is not, 
#--- but this is the best guess we canget
#

foreach $ccd (@ccd_list){
	$line = "$in_fits".'[ccd_id='."$ccd".']';
	system("dmcopy \"$line\" outfile=test.fits clobber=yes");
	$input = `ls -l test.fits`;
	@line  = split(/\s+/, $input);
	if($line[4] =~ /\d/){
		%{size.$ccd} = (size =>["$line[4]"]);
	}else{
		%{size.$ccd} = (size =>["$line[3]"]);
	}
	system("rm test.fits");
}

#
#--- now separate observations to indivisual ccds
#

@file_list = ();
foreach $ccd (@ccd_list){
	$out  = $o_fits;
	$app  = '_ccd'."$ccd".'.fits';
	$out  =~ s/\.fits/$app/;

#	$line = "$in_fits".'[ccd_id='."$ccd".']';
	$line = 'source_removed.fits[ccd_id='."$ccd".']';
	system("dmcopy \"$line\" outfile=$out");
	push(@file_list, $out);
}

system("rm source_removed.fits");

#
#--- process each ccd
#

foreach $fits (@file_list){
	$reg_file = $fits;
	$reg_file =~ s/\.fits/_block_src\.reg/; 
#
#--- find point sources
#
	system("celldetect infile=$fits outfile=acisi_block_src.fits regfile=acisi_block_src.reg clobber=yes");

	open(FH, "acisi_block_src.reg");
	@exclude = ();
	$e_cnt   = 0;
	while(<FH>){
		chomp $_;
		@atemp = split(/\,/, $_);
#
#--- increase the area covered around the sources 3time to make sure leaks from a bright source is minimized
#
		$atemp[2] *= 3;
		$atemp[3] *= 3;
		$line = "$atemp[0],$atemp[1],$atemp[2],$atemp[3],$atemp[4]";
		push(@exclude, $line);
		$e_cnt++;
	}
	close(FH);
		
	$out_name = $fits;
	if($out_name =~ /gz/){
			$out_name =~ s/\.gz//;
	}
	$out_name =~ s/\.fits/_cleaned\.fits/;
#
#--- if we actually found point sources, remove them from the ccds
#
	if($e_cnt > 0){
		$cnt   = 0;
		$chk   = 0;
		$round = 0;
		$line = '';
#
#--- remove 6 sources at a time so that it won't tax memory too much
#
		OUTER1:
		while($cnt < $e_cnt){
			OUTER2:
			for($i = $cnt; $i < $cnt + 6; $i++){
				if($i >= $e_cnt){
					$chk++;
					last OUTER2;
				}
				if($line eq ''){
					$line = $exclude[$i];
				}else{
					$line = "$line".'+'."$exclude[$i]";
				}
			}
			$cnt += 6;
			if($round == 0){
				$eline = "$fits".'[exclude sky='."$line".']';
				system("dmcopy \"$eline\" outfile=out.fits");
				$round++;
			}else{
				system("mv out.fits temp.fits");
				$eline = 'temp.fits[exclude sky='."$line".']';
				system("dmcopy \"$eline\" outfile=out.fits");
			}
		
			if($chk > 0){
				last OUTER1;
			}else{
				$line = '';
			}
		}
		system("rm temp.fits");
		system("mv out.fits $out_name");
	}else{
		system("cp $fits $out_name");
	}

#
#--- find the size of cleaned up file size
#
	$input = `ls -l $out_name`;
	@line  = split(/\s+/, $input);
	$size  = $line[4];
	if($size !~ /\d/){
		$size = $line[3];
	}

	OUTER2:
	for($iccd = 0; $iccd < 10; $iccd++){
		$check = 'ccd'."$iccd";
		if($out_name =~ /$check/){
			$pccd = $iccd;
			last OUTER2;
		}
	}
#
#--- compute the ratio of the cleaned to the original file; 1 - ratio is the  potion that we removed
#--- from the original data
#
	$ratio = $size/${size.$pccd}{size}[0];
#
#--- record the ratio for later use
#
	open(OUT2, ">>Reg_files/ratio_table");
	print OUT2 "$reg_file: $ratio\n";
	close(OUT2);

	system("mv acisi_block_src.reg Reg_files/$reg_file");
#	system("mv acisi_block_src.reg $reg_file");
	system("rm acisi_block_src.fits");
}
