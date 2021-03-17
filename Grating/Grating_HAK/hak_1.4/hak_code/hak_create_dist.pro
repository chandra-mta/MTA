PRO hak_create_dist, dist_dir
;+
; PRO hak_create_dist, dist_dir
;
; This procedure creates a stand-alone distribution of
; the "HETG Analysis Kit" IDL s/w in the directory dist_dir.
; The contents include two sub directories:
;          o hak_code/
;          o hak_data/
;     and the files:
;          o hak_start.pro
;          o README.txt
;
; The HAK distribution created is a subset of "ddidl" software
; which is useful for inspecting flight grating observations and,
; additionally, in going from a MARX FITS file to ISIS-compatible
; histogram files.  For futher details see the web pages:
;   http://space.mit.edu/HETG/HAK
;   http://space.mit.edu/HETG/flight
;
; hak_create_dist.pro is contained in the HETG Calibration
; Software, specifically, it is located in the directory:
;   $CALDBaxafcal/hetg/software/ddidl/marx .
;
; SUMMARY of OPERATION
; hak_create_dist does the following:
;
;   - create the specified directory containing the sub-directories:
;          o hak_code
;          o hak_data
;     and the files:
;          o hak_start.pro
;          o README.txt
;   - copy all needed ddidl routines from 'hetg/software/ddidl to 
;     hak_code
;   - copy all needed data files from $CALDBaxafcal to hak_data
;   - create hak_start.pro in the distribution directory
;   - create README.txt in the distribution directory
;
; For HTML help file manually run, e.g., 
;  IDL> mk_html_help, '/nfs/wiwaxia/d4/ASC/src/hak_1.3/hak_code', $
;	'hak_doc.html'
; and edit hak_doc.html for better readability...
;
; ----------------------------------------------------------------
; Revision history:
; 1999-05-23 dd  Initial creation to provide a stand-alone
;                version of obs_anal.pro to CXC MTA group.
; 1999-05-30 dd  Forgot xgef_beep routine!
; 1999-07-02 dd  Added hist_list_lines and strpad routines
; 1999-07-06 dd  Add foc_do_it_all.pro and friends...
; 1999-08-07 dd  Add oa_common, mc_ file, marx_timing_sim
; 1999-09-17 dd  Change the tdet correction file into hak_data
; 1999-10-01 dd  Additions for HAK 1.3 release
; ----------------------------------------------------------------
;-

; Create the specified directory containing the sub-directories:
;          o hak_code
;          o hak_data
SPAWN, 'mkdir '+dist_dir
SPAWN, 'mkdir '+dist_dir+'/hak_code'
SPAWN, 'chmod a+rw '+dist_dir+'/hak_code/*'
SPAWN, 'mkdir '+dist_dir+'/hak_data'
SPAWN, 'chmod a+rw '+dist_dir+'/hak_data/*'

; ----------------------------------------------------------------
; Copy all needed ddidl routines from 'hetg/software/ddidl to 
;     hak_code
code_dir = dist_dir+'/hak_code'

; Copy the routines needed from their ddidl locations to the hak_code
; directory:

sub_dir = 'marx'
; Routines in the "marx" sub dir (include this one!):
routines = ['obs_anal', 'hak_create_dist', 'foc_do_it_all', $
		'foc_common', 'foc_show_params', 'foc_gather', $
		'foc_plot', 'oa_common', 'marx_timing_sim', $
		'hak_write_isis', 'sol_plot', 'chip_gap_solve', $
		'meas_line_angle', 'chip_of_dispx', $
		'xye_image', 'mk_color_image', 'chip_frames']
for ir=0, n_elements(routines)-1 do begin
  SPAWN, 'cp '+!DDIDL+'/'+sub_dir+'/'+routines(ir)+'.pro '+code_dir+'/'
end

sub_dir = 'xgef_test'
; Routines in the "xgef_test" sub dir:
routines = ['xgef_beep']
for ir=0, n_elements(routines)-1 do begin
  SPAWN, 'cp '+!DDIDL+'/'+sub_dir+'/'+routines(ir)+'.pro '+code_dir+'/'
end

sub_dir = 'useful'
; Routines in the "useful" sub dir:
routines = ['dd_load_ct', 'log_hist', 'lin_hist', $
	 'interpol_sort', 'df_common', 'df_fit', 'curvefit_dd', $
	 'gauss1', 'lgauss', 'approx_equal', $
	 'rdb_read', 'rdb_write', 'rdb_param', $
	 'hist_lines', 'acf_herman', 'plot_errors', $
	 'hist_list_lines', 'strpad', $
	 'rpf_add_param', 'rpf_create', 'rpf_delete_param', $
	 'rpf_get_value', 'rpf_list', 'rpf_put_value', $
	 'pre_print_portrait', 'pre_print_landscape', $
	 'pre_print_sqr', 'post_print', 'plot_creator_label', $
	 'make_image', 'wgif', 'poiss_f']
for ir=0, n_elements(routines)-1 do begin
  SPAWN, 'cp '+!DDIDL+'/'+sub_dir+'/'+routines(ir)+'.pro '+code_dir+'/'
end
; and a text file...
  SPAWN, 'cp '+!DDIDL+'/'+sub_dir+'/rpf_description.txt '+code_dir+'/'

; no restrictions
SPAWN, 'chmod a+rw '+dist_dir+'/hak_code/*'


; ----------------------------------------------------------------
; Copy all needed data files from $CALDBaxafcal to hak_data
; The files are removed from any heirarchy and are "flat" in
; hak_data.
data_dir = dist_dir+'/hak_data'

; Data used by obs_anal.pro:
; A set of effective areas for various instrument 
; combinations (cira AO-1 - hey close enough for now!):
tbl_dir = !DDHETGCAL+'/fcp/Tbl_AO1'
template = 'EA*.rdb'
SPAWN, 'cp '+tbl_dir+'/' + template + ' ' + data_dir+'/'

; File of TDET correction values:
; !DDACISCAL+'/cip/acisD1999-07-23tdetoffN0002.rdb'
cipsdir = !DDACISCAL+'/cip'
template= 'acisD1999-07-23tdetoffN0002.rdb'
SPAWN, 'cp '+cipsdir+'/' + template + ' ' + data_dir+'/'

; Data used by hist_lines.pro:
; Conservative and optimistic Resolving Power
; estimates for the grating spectrometers,
; aka "E/dE vs E".  These values assume a point source,
; on-axis, nominal aspect performance, etc.
cipsdir = !DDHETGCAL+'/cip'
template='/hetg'+'*'+'D1996-11-01res_*N0002.rdb'
SPAWN, 'cp '+cipsdir+'/' + template + ' ' + data_dir+'/'

cipsdir = !DDLETGCAL+'/cip'
template='/letgD1996-11-01res_*N0002.rdb'
SPAWN, 'cp '+cipsdir+'/' + template + ' ' + data_dir+'/'

; no restrictions
SPAWN, 'chmod a+rw '+dist_dir+'/hak_data/*'

; ----------------------------------------------------------------
; Create hak_start.pro in the distribution directory
; Fun with s/w making s/w!
;
OPENW, su, dist_dir + '/hak_start.pro', /GET_LUN
printf, su, '; IDL startup file for the HETG Analysis Kit (HAK) software'
printf, su, '; Created by hak_create_dist.pro at '+!DDLOCATION+' on '+SYSTIME()
printf, su, '; Created in: '+dist_dir
printf, su, '; --------------------------------------------------'
; What's it got to do?
;  o set the !DDVERDATE value to the current time
printf, su, "DEFSYSV, '!DDVERDATE', '" + SYSTIME() + "'"
;  o set !DDLOCATION to 'HAK Stand-alone'
;    This value will signal HAK-compliant code to bypass the
;    usual data path to the CALDB area and instead use the 
;    value of the system variable !DDHAKDATA as the full
;    above-file path to the data files.
printf, su, "DEFSYSV, '!DDLOCATION', 'HAK Stand-alone'"
;  o IDL and astrolib to path
printf, su, "DEFSYSV, '!DIR', EXISTS = ie"
printf, su, "; *** Edit the following path to the ASTROLIB directory: ***"
printf, su, "DEFSYSV, '!DDASTRO', !DIR+'/lib_astro/pro'"
;  o define and set the value of the !DDHAKDATA and !DDHAKCODE system variables
printf, su, "; *** Edit the following path to the hak_code directory: ***"
printf, su, "DEFSYSV, '!DDHAKCODE', '"+code_dir+"'"
printf, su, "; *** Edit the following path to the hak_data directory: ***"
printf, su, "DEFSYSV, '!DDHAKDATA', '"+data_dir+"'"

printf, su, "print, '' "
printf, su, "print, ' - - - - - - - - - - - - - - - - - - - - ' "
printf, su, "print, '       HETG Analysis Kit Software' "
printf, su, "print, '  created on: ' + !DDVERDATE "
printf, su, "print, ' - - - - - - - - - - - - - - - - - - - - ' "
printf, su, "print, '      http://space.mit.edu/HETG/HAK' "
printf, su, "print, ' - - - - - - - - - - - - - - - - - - - - ' "
printf, su, "print, '' "

;  o add hak_code to path
printf, su, "; Add the HAK code to beginning of the path:"
printf, su, "!path = !DDHAKCODE+':' + !path "
printf, su, "print, ' HAK code dir : ' + !DDHAKCODE"
printf, su, "print, ' Ref data dir : ' + !DDHAKDATA"
printf, su, "print, '' "
printf, su, "print, ' To list the routines available:' "
printf, su, "print, '   hak> $ls '+ !DDHAKCODE"
printf, su, "print, ' To get information on a routine, e.g.:' "
printf, su, "print, '   hak> doc_library, ''obs_anal'' ' "
printf, su, "print, '' "
printf, su, "print, ' - - - - - - - - - - - - - - - - - - - - ' "

;  o setup astrolib at end of the path
printf, su, "; Add the astrolibrary to the end of the path: "
printf, su, "full_astro = EXPAND_PATH('+'+!DDASTRO) "
printf, su, "!path=!path+':' + full_astro "
printf, su, "ASTROLIB"

;  o prompt, hc, oa_common, and foc_common
printf, su, "; set the prompt and foc_common and we're done..."
printf, su, "print, '' "
printf, su, "DEFSYSV, '!DDHC', " + STRING(!DDHC)
printf, su, "!prompt = 'hak> ' "
printf, su, "@oa_common ' "
printf, su, "@foc_common ' "

; and close it up...
close, su
free_lun, su

; ----------------------------------------------------------------
; Copy the README.txt file to the distribution directory
SPAWN, 'cp '+!DDIDL+'/marx/hak_read_me.txt '+dist_dir+'/README.txt'

RETURN
END
