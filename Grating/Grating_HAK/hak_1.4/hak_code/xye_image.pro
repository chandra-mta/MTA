PRO xye_image, X, Y, E, GIF_FILE = gif_file, ONELEVEL=onelevel, $
		LOG_E_COLORS=log_e_colors, $
		XBINSIZE=xbinsize, YBINSIZE=ybinsize, $
		MARX_DIR = marx_dir, $
		ACIS_TRW_ID = acis_trw_id
;+
; PRO xye_image, X, Y, E, GIF_FILE = gif_file, ONELEVEL=onelevel, $
;		LOG_E_COLORS=log_e_colors, $
;		XBINSIZE=xbinsize, YBINSIZE=ybinsize, $
;		MARX_DIR = marx_dir, $
;		ACIS_TRW_ID = acis_trw_id
;
; Procedure to convert, display, write-to-file event data
; into an energy-color-coded image.  Builds on Dave H's pioneering
; work!
;
; INPUTS:
;    X [np] X values (nominally in mm)
;    Y [np] Y values (nominally in mm)
;    E [np] E values (in keV)
;
; OPTIONAL INPUTS:
;    /LOG_E_COLORS if set then the energy-->color mapping is fixed
;                 independant of the data (red to blue is 0.1 to 10 keV).
;                 Real data (if not selected on energy) will probably
;                 cover the full range always and not need this.
;    ONELEVEL = 0.0 - 1.0  sets the intensity of a one-count pixel
;                 Default of 0.6 is good for (my) monitor, for printer
;                 output (e.g. when writing .gif file to later print)
;                 better to use 0.2 or so...
;
;    GIF_FILE = 'filename' writes gif image to this file
;
;    XBINSIZE = 6.*0.024   sets image bin size, same units as X
;    YBINSIZE = 6.*0.024   sets image bin size, same units as Y
;
;    MARX_DIR = 'directory' if set, the X,Y, and E will be taken
;                           from the marx ypos.dat, zpos.dat, and
;                           energy.dat
;    ACIS_TRW_ID = 'H-HAS-EA-8.003' trw id: this is used to 
;                  restore the ACIS XRCF L1 save file from dd's
;                  cache of them in /spectra/d6/ACIS_anal/ .
;                  To add others, run dd's ~dd/idl/xrcf/psu_view !
;
; OPTIONAL OUTPUTS:
;    if the MARX_DIR or ACIS_TRW_ID is used then these are output:
;      X [np] X values (in mm) = marx ypos.dat   OR mm w.r.t. aim pt
;      Y [np] X values (in mm) = marx zpos.dat   OR mm w.r.t. aim pt
;      E [np] E values (in keV)= marx energy.dat OR keV
;
; PROCEDURES required (all from dph!):
;                 ~dd/idl/marx/mk_color_image.pro
;               ~dd/idl/useful/make_image.pro
;               ~dd/idl/useful/wgif.pro
;
;
; EXAMPLES with CHANDRA Data
;
; 1) After running obs_anal with /EXPORT perform some selections
;    to get desired events and make the energy-color-coded image:
;
;  sel = where(oa_Etouse GT 0.3 AND oa_Etouse LT 10.0 AND $
;	ABS(oa_AY - oa_aveAY) LT 300.0 AND $
;	ABS(oa_AX - oa_aveAX) GT 2.0)   ; get rid of bright 
;                                        ; (not piled-up) zero order core
;  Xtouse = oa_AX(sel)
;  Ytouse = oa_AY(sel)
;  Etouse = oa_Etouse(sel)
;
;  set_plot,'X'
;  xye_image, xtouse, ytouse, etouse, $
;	xbin=6.0, ybin=6.0, gif_file='Obs_out/Obs457_image.gif', ONE=0.4
;
;
; 2) From evt1a (or evt1) file directly:
;
;  fits_file = '/nfs/atum/d2/hetgs/obsid_1318/' + $
;	'acisf1318_000N001_g02346EsS4_evt1a.fits'
;  l1a = mrdfits(fits_file, 1)
;
;  sel = where(l1a.ENERGY GT 500.0 AND l1a.ENERGY LT 2500.0)
;  Xtouse = l1a(sel).TDETX
;  Ytouse = l1a(sel).TDETY
;  Etouse = l1a(sel).ENERGY/1000.0
;
;  set_plot,'X'
;  xye_image, xtouse, ytouse, etouse, $
;	xbin=12.0, ybin=12.0, gif_file='Capella/Obs1318_TDETimage.gif', $
; 	ONE=0.1
;
; - - - - - - - - - - - - -
; REVISIONS
;   1/8/98 (dd)
;  11/11/99 dd Added Chandra examples
;     ---------------------------------------------------
;-

; MARX input?
if KEYWORD_SET(MARX_DIR) then begin
  X = read_marx_file(marx_dir+'/ypos.dat')
  Y = read_marx_file(marx_dir+'/zpos.dat')
  ; Use the energy (cheating)
  E = read_marx_file(marx_dir+'/energy.dat')
  ; Would have used PHA BUT then need to convert
  ; PHA --> energy based on a calibration for each chip
  ; PI would be the preferred quantity to use... but that is
  ; Level 1 and not in the MARX output...
  ; PHA = read_marx_file(marx_dir+'/pha.dat')
  ; ; Convert PHA to E:
  ; E = 0.00429 * PHA  ; keV/PHA of MARX ?
end

; ACIS TRW ID ?
if KEYWORD_SET(ACIS_TRW_ID) then begin
  restore, '/nfs/spectra/d6/ACIS_anal/'+acis_trw_id+'_l1.idlsav'
  ; select standard grade set
  sel = WHERE((l1.GRADE EQ 0 or l1.GRADE EQ 2 or l1.GRADE EQ 3 $
		or l1.GRADE EQ 4 or l1.GRADE EQ 6) and $
		l1.energy LT 12.0)
  X = l1(sel).detx 
  Y = l1(sel).dety
  E = l1(sel).energy 
end

; Default bin sizes
; Assuming X,Y in mm set the bins so that ACIS-S will be about
; 1000 bins long
if n_elements(XBINSIZE) EQ 0 then xbinsize = 6.*0.024
if n_elements(YBINSIZE) EQ 0 then ybinsize = 6.*0.024

; The KEYWORD ONELEVEL is used to set the intensity of image bins
; that have a single count.
if KEYWORD_SET(ONELEVEL) then begin
  use_level = onelevel
end else begin
  use_level = 0.6
end

if KEYWORD_SET(LOG_E_COLORS) then begin
  mk_color_image, X, Y, [xbinsize, ybinsize], E, $
	image, xax, yax, rgb_table, ONELEVEL = use_level, /LOG_E_COLORS
end else begin
  mk_color_image, X, Y, [xbinsize, ybinsize], E, $
	image, xax, yax, rgb_table, ONELEVEL = use_level
end

iwindow = 2  ; appears in upper left of screen

window, iwindow, XSIZE=n_elements(xax), YSIZE=n_elements(yax) 
tvlct, rgb_table
tv, image

if KEYWORD_SET(GIF_FILE) then begin
  wgif, iwindow, gif_file
end

RETURN
END
