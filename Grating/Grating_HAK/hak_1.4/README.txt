                                                    11/4/99 dd
        HETG Analysis Kit ("HAK") Software
        ----------------------------------

INTRODUCTION
------------ 
  This directory is a stand-alone distribution of
the "HETG Analysis Kit" (HAK) IDL routines.

  The contents of this directory are two sub-directories:

          o hak_code/
          o hak_data/

     and the files:

          o hak_start.pro
          o README.txt   (<-- this file)

  This distribution is a subset of HETG IDL software
which is useful for inspecting flight grating observations and,
additionally, in going from a MARX FITS file to ISIS-compatible
histogram files.  Additionally, the routine "foc_do_it_all.pro"
and other "foc_" routines supported the HETG first-light
focus set analysis.


SETUP
-----
  Edit the file hak_start.pro so that the following three
lines correctly describe the location of their directories,
for example:

   DEFSYSV, '!DDASTRO', !DIR+'/lib_astro/pro'

   DEFSYSV, '!DDHAKCODE', '/spectra/d0/hak_dist/hak_code'

   DEFSYSV, '!DDHAKDATA', '/spectra/d0/hak_dist/hak_data'

Note that the hak_code and hak_data directories may be
placed independently of each other.


USE
---
  Run IDL in any directory and at the IDL prompt type:

    IDL> @/path/to/hak_start.pro

or the hak_start.pro file may be copied to the current 
directory and simply invoked by typing:


    IDL> @hak_start

     - - - - - - - - - - - - - - - - - - - - 
           HETG Analysis Kit Software
      created on: Mon Jul 12 11:53:03 1999
     - - - - - - - - - - - - - - - - - - - - 
          http://space.mit.edu/HETG/HAK
     - - - - - - - - - - - - - - - - - - - - 

     HAK code dir : /nfs/spectra/d0/hak_dist/hak_code
     Ref data dir : /nfs/spectra/d0/hak_dist/hak_data

     To list the routines available:
       hak> $ls /nfs/spectra/d0/hak_dist/hak_code
     To get information on a routine, e.g.:
       hak> doc_library, 'obs_anal' 

     - - - - - - - - - - - - - - - - - - - - 
    % Compiled module: ASTROLIB.
    % ASTROLIB: Astronomy Library system variables have been added

    hak> 


The prompt is now "hak> " and you're ready to go.


EXAMPLES
--------

obs_anal:

  The current "release" contains the procedure "obs_anal.pro"
which creates a variety of plots and .html summary page from
a Chandra Level 1 or Level 1.5 FITS events file.
In addition it can be used on the files created by marx2fits.
Some examples of its use are given here.

1) obs_anal takes as argument the name of the FITS file
to be processed.  There are a variety of keywords which
describe the data and processing.  Documentation can
be displayed by typing obs_anal without a filename argument:

    hak> obs_anal

2) OK, so if my_obs.fits is the result of marx2fits of, say, an
HETG-ACIS-S simulation, it can be processed with the command:

    hak> obs_anal, 'my_obs.fits', DETECTOR='ACIS-S', $
    hak>   GRATING='HETG', OUT_DIR = '/mydisk/d0/Obs_out', $
    hak>   /ASPECT, /LINE_ANALYSIS, /STREAK_MARX

The file my_obs_aTDET_summary.html will be creatd in /mydisk/d0/Obs_out
and can be viewed with a web browser.  A variety of .gif files
are produced as well and are linked to the 'summary.html.
The files 'summary.rdb and 'summary.txt are also created
containing useful values in computer and human readable form.
Files of the form *_isis.dat are created and can be read
into ISIS.


foc_ routines:

  The routine "foc_do_it_all.pro" is both a procedure and a
routine to carry out focus set analyses, see foc_do_it_all.pro
for details.


FURTHER INFORMATION
-------------------
  Further examples, details, and updates to the HAK code are are
available at http://space.mit.edu/HETG/HAK.

Questions and comments may be directed to Dan Dewey, dd@space.mit.edu




