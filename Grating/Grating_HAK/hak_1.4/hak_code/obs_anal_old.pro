PRO obs_anal, filename, $
	OUTPUT_PREFIX=output_prefix, OUT_DIR=out_dir, $
        COORDS_NAME = coords_name, TDET_SELECT = tdet_select, $
	ROLLAXAY = rollaxay, $
	CENTER_FIT = center_fit, CENTER_STREAK = center_streak, $
        CC_MODE_FLAG = cc_mode_flag, $
	MOUSE=mouse, $
	OVERRIDE_ZERO=override_zero, OVERR_WIDTH=overr_width, $
	ASPECT=aspect, BUT_DONT_APPLY=but_dont_apply, $
	LINE_ANALYSIS=line_analysis, $
	CD_WIDTH=cd_width, CD_OFFSET=cd_offset, $
	GRATING=grating, LETG=letg, $
	DETECTOR=detector, FLIPY=flipy, $
	GAIN_FACTORS=gain_factors, $
        ORDER_SEL_ACCURACY=order_sel_accuracy, $
        SCREEN24 = screen24, ZBUFFER=zbuffer, $
	SILENT=silent, $
	XRCF_ROWLAND=xrcf_rowland, $
	STREAK_MARX=streak_marx, EXPORT=export

;
; - - - - - - - - - Documentation - - - - - - - - - - - - - - -
;+
; PRO obs_anal, filename [, ... many KEYWORDS ... ]
;
; PURPOSE:    
;
;  Procedure to analyze the L1 or L1.5 FITS file from a grating observation
;  Prototype MTA, etc. algorithms..., create informative plots, etc.
;
; ARGUMENTS:
;
;  filename - full file specification to a FITS event file
;
; KEYWORDS:
;
;  OUTPUT_PREFIX - if present, this character string is used as
;                  the prefix name for all output products; if not
;                  specified it is set to the last part of the filename
;                  with .fit or .FITS removed (if present.) 
;  OUT_DIR       - specifies directory where products are placed, default is
;                  present directory ( = '.'), trailing / not needed.
;  COORDS_NAME   - takes on the values: 'TDET', 'DET', or 'Sky'.
;                  If provided on input it selects which X,Y coordinates to
;                  use from the file.
;                  If not supplied, it is set based on detector:
;                  TDET for ACIS, DET for HRC
;  /TDET_SELECT  - if set then COORDS_NAME is set to 'TDET'
;  ROLLAXAY      - the X and Y coords are rotated by this value (degrees)
;                  about the X,Y zero-order location -- only applies
;                  when the analysis method is 'Sky' (i.e., does not
;                  apply to the comparison X,Y plots and analysis.)
;                  Positive roll of 90 degrees takes the AX axis
;                  into the AY axis.
; CENTER_FIT,
; CENTER_STREAK  - Adjust the AX coordinate so that the center of the 
;                  zero-order fit (or streak fit) is at aveAX in order to
;                  symmetrize plus/minus line locations.
;  /CC_MODE_FLAG - set to signal that data are in CC mode.  In addition, if
;                  TDETY has a constant value CC mode is assumed (e.g., this
;                  was the case for some XRCF data sets.)
;  /MOUSE - stops after each plot and waits for a mouse click...  Uses user
;                guidance for zero-order location, but s/w has the final word.
;  /OVERRIDE_ZERO - if set, the s/w stops for mouse input of the zero-order
;                location and the final location used is from the mouse input.
;                (Normally a final average is performed in the zero-order
;                 region to set the location.)
;  /OVERR_WIDTH - The measured width of the zo is used to set grating
;                    PHA bin size - this keyword overrides this with the
;                    given value (in um).
;  /ASPECT - create an aspect solution from the zero-order X, Y vs time 
;  /BUT_DONT_APPLY - If this keyword is set the aspect solution that is
;                    calculated will NOT be applied to the coordinates.
;  /LINE_ANALYSIS - grating energy histograms will be analysed for
;                  lines and E/dE values if this keyword is set.
;  CD_WIDTH  - Acceptance full-width in the cross-dispersion direction, in mm.
;              Default value is 2.0 mm.  Note, however that events are
;              also required to be in the correct quadrant to separate
;              HEG and MEG.
;  CD_OFFSET - Offset of the extraction region in cross-dispersion, in mm.
;              Default value is 0.0 mm.
;  GRATING  - set to 'HETG', 'LETG' or 'NONE', default is 'HETG'
;  /LETG    - short way to set GRATING='LETG' is with /LETG
;  DETECTOR - set to 'ACIS-S','ACIS-I','HRC-I', or 'HRC-S', default is ACIS-S
;  GAIN_FACTORS - array of factors to multiply the ACIS ENERGY values by;
;                 array has values for the 10 chips in order: [i0,i1,...s0,s1,...,s5]
;  ORDER_SEL_ACCURACY - Set the order selection width; ACIS energy can be
;                       from (1-this) to (1+this) of the grating Energy.
;                       Default is wide = 0.5 .
;  /FLIPY   - changes the sign of the y-axis, e.g., HRC DETY to get 
;             HEG/MEG in correct quadrants...
;  /SCREEN24 - causes the displayed colors to look OK on a 24bit monitor
;             (and/but messes up the 8 bit gif output!)
;  /ZBUFFER  - use set_plot, 'Z', so physical output device is not needed,
;              e.g., for batch or non-xterm (telnet) operation.
;  /SILENT   - suppresses the print outs to screen
;  /XRCF_ROWLAND - use the XRCF value of the Rowland Diameter
;  /STREAK_MARX - used ONLY when the input FITS file is from a MARX 
;                 simulation to add ACIS time quantization and frame
;                 transfer streaking.
;  /EXPORT   - causes the oa_common variables to be filled when
;              obs_anal is finished, this gives access to the obs_anal
;              internal variables for further custom processing.
;
; COMMON:
;          oa_common.pro defines variables to be available at the
;          command line after obs_anal is run.
;           ----------------------------------------------
;-
; Revisions:
; 1999/01/22 - 02/05 dd Initial hacking to prototype the HETG Analysis Kit
;                       (HAK) code algorithms and plots...
; 1999/02/06 - 02/12 dd Create HTML output, use .gif plots and color...
;                       Try to clean up the humongeous and kludgy (HAK) code.
;                       Nope, it's still a mess!
; 1999/02/13 -       dd Add ISIS output format for histograms
; 1999/02/16 -       dd tweaking, experimenting w/TDETX for HRC-S, etc.  Add fcp/Tbl_AO1.
; 1999/02/18 -       dd Change HRC DETX,DETY pixel size to agree with ICD
; 1999/02/20 -       dd Add keywords for Z buffer and output directory
; 1999/02/22 -       dd Add KEYWORD COORDS_NAME, and associated logic...
; 1999/02/25 -       dd Write HTML output to a temp file and later copy to HTML out file;
;                       this allows the "proc_method" value to be known and the
;                       html output file to have proc_method as part of the filename...
; 1999/02/25 -       dd Look into the aspect solution a bit... add apodization
; 1999/02/26 -       dd add Etouse array...
; 1999/03/05 - 03/08 dd clean things up..., add TDET_SELECT, adapt for CC mode,
;                       add XRCF_ROWLAND, keep "low" frequ.s in aspect sol'n.
; 1999/03/30 -       dd Add cross-dispersion selection criteria and
;                       parameters (cd-width, etc.)
;                       Set ge_bin_ratio to 1 part in 10000 for line
;                       analysis...
; 1999/04/03 -       dd reduce LETG binning to avoid >32K channels,
;                       check for 4-element STATUS (due to 32X format!?)
;                       For now skip it, use/convert it in future...
; 1999/04/14 -       dd Added CC_MODE_FLAG to tell s/w the data are CC mode.
;                       (It still auto-detects cc mode if TDETYs are all
;                        the same.)
; 1999/05/10 -       dd Properly handles ACIS STATUS for the "16x" format
;                       where STATUS appears as a two-byte array.
; 1999/05/22,23 -    dd Modified based on chat w/Jim and Scott:
;                       doc_library used, remove TEST_CASE keyword and code,
;                       added BUT_DONT_APPLY, added SILENT keyword, check
;                       for no order selection events, etc.
; 1999/05/24,25a     dd HEG plus and minus were mislabeled in 4 spectra
;                       plot..., set zo_fwhm_pixels from gaussian fit,
;                       Part plot HEG,LEG labels corrected
; 1999/05/28a        dd Clean up the plot's font sizes, clipping, xrange;
;                       HRC PHA low set to 1.0.
; 1999/05/28b        dd Looking for 2 pixel offset in zero order... use
;                       median for final zero-order determination; use
;                       "50% median" in aspect solution, plot X,Y - ave.
; 1999/05/28c        dd Default COORDS is 'DET'; clip energy_colors at 242;
; 1999/05/30b        dd clip energy_colors at 251+3; use "ave median" for
;                       zero-order centroid
; 1999/06/15         dd Change zero-order finding median-average to use
;                       90% of the events (instead of 50%); charsize adjusted;
; 1999/06/23         dd Catch events with ENERGY=Inf, etc.; change aspect
;                       bin time to 60 seconds; change COORDS_NAME defaults
;                       (if not supplied) to be TDET for ACIS, DET for HRC.
; 1999/06/29         dd Catch case of no events in aspect solution time
;                       region - pass whatever events are present to finish
;                       plots...
; 1999/07/02         dd Add % in ACIS grades to output, add .rdb link for
;                       hist_lines output.
; 1999/07/06         dd Add 'summary.rdb output file of parameters (includes
;                       zero_order_fwhm) and ACF for zero-order, etc.
;                       for HAK release.
; 1999/07/09         dd Add other rpf output parameters...
; 1999/07/26,27      dd add a 'summary.txt output as listing of 'summary.html;
;                       change ACF "unit" in rpf; rpf output changes:
;                         - add filename, detector, grating
;                         - add file_events
;                         - add x_coord_name, y_coord_name
;                         - add zo_det_events, zo_live_rate
;                         - add zo_det_fwtenthm, zo_det_fwhm
;                         - add aspect_bin_time, aspect_bin_rate
;                       skip aspect if bin_rate is less than 3 events/bin ave.
;                       skip all grating activities if less than 200 zero-order
;                          events are available, go to level 1.5 check.
;                       do not show X,Y plots if X,Y have no range,
;                          e.g., all 0's
;                       added comments to do a GRACEFUL RETURN IF NO TDETX
;                         is found in the FITS file extensions but not
;                         implemented because it relies on EXTENDs being
;                         correctly set in each header...
; 1999/08/01         dd Remove blurring of the DET coordinates: CXC level 1
;                       products have DET already randomized - good!
;                       Add STREAK_MARX KEYWORD for adding timing effects
;                       to MARX simulations (NOT FOR FLIGHT DATA!!!)
; 1999/08/03         dd Bin ACIS spectra in 14.6 eV bins (a la PI);
;                       make X-Y plot more square if "I" array used;
;                       CD_WIDTH default to 5.0 mm; make streak-event
;                       spatial plots; zo isis-format PHA out;
; 1999/08/04         dd Move all ARD parameters up front;
; 1999/08/06         dd Use Herman's tdetx corrections file to correct
;                       the TDET values.
; 1999/08/07         dd check for enough streak counts; add Grade %'s
;                       to screen print; scale spect compare to max of all;
;                       add oa_common; add res1kev values to rpf out;
; 1999/08/08         dd add ISIS keywords; add EXPORT for oa_common;
; 1999/08/09         dd skip grating processing if zero-order FWHM is large.
; 1999/08/22         dd Add ROLLAXAY keyword; reduce selected energy range;
;                       zo_exam_size larger;
; 1999/08/28         dd [after HETG first light!]; filter out X,Y GT 1.E5;
;                       special enery range for zero-order searching;
;                       zo FWHM manual set note fixed;
; 1999/08/31         dd analyzing Capella data: CD_WIDTH default to 2.0 mm;
;                       add guess_center to gauss fitting; zero-order
;                       search restricted to 0.7-2.0 keV;
; 1999/09/08         dd zero-order spectral added; fft_thresh to 0.1;
;                       add CENTER_FIT, CENTER_STREAK; add fit locations
;                       to output rpf; change LIVETIME to EXPOSURE for isis;
; 1999/09/09         dd fix colors >= 3;
; 1999/09/10         dd new angles;
; 1999/09/15         dd change order plot Y axis to ACIS/Grating ratio;
; 1999/09/17         dd Add the HEG,MEG,LEG zero-order offset values; add
;                       the new tdet offsets file;
; 1999/09/20,21,22   dd Add GAIN_FACTORS keyword to approx correct ACIS gains;
;                       add nom chip labels to order plots, etc.; improve
;                       the angle plots; add toolow_f_defn for auto-aspect;
; 1999/09/27         dd Default CD_WIDTH to 0.5 mm;
; 1999/10/08         dd Set heg and meg zo_offsets to 0.0.
; 1999/10/28         dd Add ORDER_SEL_ACCURACY keyword.
; 1999/10/29         dd Don't blur Sky-Y in CC mode analysis,
;                        e.g.: if cc_mode AND (COORDS_NAME ne 'Sky') then ...
; 1999/11/01         dd Little changes for HAK 1.3 release.
; 1999/11/11         dd Add ACIS EXPNO checking section...; zo sel 0.7-6.0keV
; 1999/12/28         dd Add pileup plots of grating spectra;
;                       fft_thresh back to 0.01 for use with MARX sims.
; 2000/01/04         dd Add ISIS format output of zeroth order and streak
;                       1d histograms.
; 2000/02/02         dd Changed tg_src_id to tg_srcid in hak_write_isis calls
; 2000/05/01,,2      dd Slight adjustments of HETG gap energies (on order
;                       sel plot);  using "0.0mm" values from POG table.
;                       Limit zosel to the CD_WIDTH value in cross-disp for
;                       histograms and output rdb zo files; output average
;                       CHIPX, CHIPY zo values if available; ignore HEG
;                       below 0.8keV in y-axis range for comparison plot.
;      ----------------------------------------------

; Common for returning arrays,etc. for command line use
; (hak_start does a "@oa_common")
@oa_common

; Common for the fitting routines...
@df_common

; - - - - - - - - - - - - - - - - - - - - - - - - - - -
; Constants and ARD Parameters
hc = !DDHC
sig_per_fwhm = 2.35

; Focal length for pixel size conversion (1/plate_scale):
; (from $CALDBaxafcal/hrma/cip/hrmaD1996-11-01basicN0003.rdb)
hrc_pix_foc_leng = 10061.62 ; mm
acis_pix_foc_leng =  10061.62 ; mm

; Angular sizes of DET and Sky pixels
; (e-mail from Jonathan, 8/6/99)
hrc_pix_ang_size =  0.13175 ; arc sec, DET and Sky Coords
acis_pix_ang_size = 0.49190 ; arc sec, DET and Sky Coords

; Physical size of detector pixels
; (HRC $CALDBaxafcal/hrc/cip/hrcD1996-11-01basicNnext.rdb, will be N0002)
; ($CALDBaxafcal/acis/cip/acisD1996-11-01basicN0001.rdb)
hrc_pixel_size = 0.0064294 ; mm
acis_pixel_size = 0.0240000 ; mm

; Grating dispersion angles, periods, and spacings
; (Angles defined w.r.t. observatory axes at the moment.)
; (HETG ref:$CALDBaxafcal/hetg/cip/hetgD1996-11-01periodN0002.rdb)
; (LETG ref:$CALDBaxafcal/letg/cip/letgD1996-11-01periodN0002.rdb)
ang_meg = 4.725  ; degrees
ang_heg = -5.235 ; degrees
ang_leg = 0.016 ; degrees
;
p_meg = 4001.41
p_heg = 2000.81
p_leg = 9912.16
;
heg_zo_offset =  0.0 ; 0.36   ; pixels
meg_zo_offset =  0.0 ; -0.08  ; pixels
leg_zo_offset = 0.0
;
; expected flight Rowland spacing:
; (NOTE: MARX 2.22 has 8634.0 in marx.par, a 156, 196 ppm difference;
;  In MARX use 8632.48 for both and error is +/- 19 ppm.)
; For a single, average value, use 8632.48
hetg_rs_flight = 8632.65 ; mm
letg_rs_flight = 8632.31 ; mm
; at XRCF:
hetg_rs_xrcf = 8782.80 ; mm "based on XRCF data"
; for reference: hetg_rs_xrcf = 8788.65 ; mm, TRW value
letg_rs_xrcf = 8788.76 ; mm, TRW value, agrees w/data

; Bin size of ACIS PI bins
pi_energy_bin_spacing = 0.0146 ; keV

; - - - - - - - - - - - - - - - - - - - - - - - - - - -


; Print these lines even if SILENT...
print, ''
print, ' - - - obs_anal.pro - - - - - - - - - - '+SYSTIME()+' - - - '

; - - - - OK, check out the filename... - - - - - - - - -
; It's the only required argument, if not present help 'em out...
if n_elements(filename) EQ 0 then begin
  print, ''
  print, ' *** No filename supplied ! ***'
  print, ''
  doc_library, 'obs_anal'
  print, ' - - - - - - - - - - - - - - - - - - - - '+SYSTIME()+' - -'
  print, ''
  RETURN
end

; - - - - Default values for OUTPUT_PREFIX and OUT_DIR - - - - - - - 
if n_elements(OUTPUT_PREFIX) EQ 0 then begin
  pieces = STR_SEP(filename,'/')
  ; get the last piece...
  last_str = pieces(n_elements(pieces)-1)
  ; remove .fits or .FITS or even .FitsIsSoHardToRead !
  where_fits = STRPOS(STRUPCASE(last_str),'.FITS')
  if where_fits GT 0 then begin
    ; Use everything upto the .FITS:
    output_prefix = STRMID(last_str, 0, where_fits)
  end else begin
    ; OK, no FITS, use it as is...
    output_prefix = last_str
  end
end
if n_elements(OUT_DIR) EQ 0 then begin
  out_dir = '.'
end


; - - - - - - - KEYWORD defaults, etc. - - - - - - -

; Default DETECTOR logic
; Default value:
if n_elements(DETECTOR) EQ 0 then DETECTOR='ACIS-S'
; convert input to upper case
DETECTOR = STRUPCASE(DETECTOR)
; Check user input detector value...
allowed_detectors = ['ACIS-S', 'ACIS-I', 'HRC-S', 'HRC-I']
if TOTAL(DETECTOR EQ allowed_detectors) EQ 0 then begin
  print, ''
  print, ' *** DETECTOR not valid (ACIS-S, ACIS-I, HRC-S, HRC-I) ***'
  print, '     DETECTOR set to: ACIS-S'
  print, ''
  DETECTOR = 'ACIS-S'
end

; COORDS_NAME and TDET logic...
if KEYWORD_SET(TDET_SELECT) then COORDS_NAME = 'TDET'
if n_elements(coords_name) EQ 0 then begin
  ; Defaults different for ACIS and HRC:
  if STRPOS(DETECTOR, 'ACIS') GE 0 then begin
    ; ACIS default
    coords_name = 'TDET'
  end else begin
    ; HRC default
    coords_name = 'DET'
  end
end else begin
  ; user supplied a valid value?
  ; convert it to upper case
  coords_name = STRUPCASE(coords_name)
  allowed_coords = ['DET','TDET','SKY']
  if TOTAL(coords_name EQ allowed_coords) EQ 0 then begin
    print, ''
    print, ' *** COORDS_NAME not valid (DET, TDET, Sky, or Not supplied) ***'
    print, '     COORDS_NAME set to: Not supplied on input'
    print, ''
    coords_name = 'Not supplied on input'
  end
  ; for asthetics change 'SKY' to 'Sky' :
  if coords_name EQ 'SKY' then coords_name='Sky'
end

; Default CD_ parameters
if n_elements(cd_width) EQ 0 then cd_width = 0.5 ; mm
if n_elements(cd_offset) EQ 0 then cd_offset = 0.0 ; mm

; Default grating logic...
; /LETG takes precedence
if KEYWORD_SET(LETG) then begin
  GRATING='LETG'
end
; Default if GRATING is not supplied:
if n_elements(GRATING) EQ 0 then GRATING='HETG'
; finally, if the user provided a value for GRATING
; make sure it's OK:
GRATING = STRUPCASE(GRATING)
; Check user input grating value...
allowed_gratings = ['NONE','HETG','LETG']
if TOTAL(GRATING EQ allowed_gratings) EQ 0 then begin
  print, ''
  print, ' *** GRATING not valid (NONE, HETG, LETG) ***'
  print, '     GRATING set to: NONE'
  print, ''
  GRATING = 'NONE'
end

; Default ORDER_SEL_ACCURACY
if n_elements(ORDER_SEL_ACCURACY) EQ 0 then ORDER_SEL_ACCURACY = 0.5

; Check consistancy of ZBUFFER and MOUSE, SCREEN24
if KEYWORD_SET(ZBUFFER) then begin
  if KEYWORD_SET(MOUSE) OR KEYWORD_SET(OVERRIDE_ZERO) then begin
    print, ''
    print, ' *** MOUSE and OVERRIDE_ZERO not available with ZBUFFER! ***'
    print, '     Setting them to 0 '
    print, ''
    MOUSE=0
    OVERRIDE_ZERO=0
  end
  if KEYWORD_SET(SCREEN24) then begin
    print, ''
    print, ' *** SCREEN24 not useful with ZBUFFER! ***'
    print, '     SCREEN24 set to 0 '
    print, ''
    SCREEN24=0
  end
end


; - - - - - - - create a temporary output file for now - - - - - - -
OPENW, out_unit, out_dir+'/temp_summary.html', /GET
; and an output parameters structure
rpf_create, rpf, HEADER=rpf_header

; - - - - - - - - Start output... - - - - - - - - - - -
; Summarize what the inputs are... (except for action-creating
; keywords ...)

printf, out_unit, SYSTIME()+' : obs_anal.pro started'
printf, out_unit, "</PRE>"
printf, out_unit, '<HR>'
printf, out_unit, '<H3>Inputs</H3>'
printf, out_unit, "<PRE>"
printf, out_unit, ""

  ; Keep the filename print out even if SILENT
  print, ' Filename        = '+filename
if NOT(KEYWORD_SET(SILENT)) then begin
  print, ' Output_prefix   = '+output_prefix
  print, ' Output dir.     = '+out_dir
  print, ' Grating         = '+grating
  if grating NE 'NONE' then begin
    print, '   cd_width      = '+STRCOMPRESS(cd_width)+' mm'
    print, '   cd_offset     = '+STRCOMPRESS(cd_offset)+' mm'
  end
  print, ' Detector        = '+detector
  print, '   Spatial coord = '+coords_name
end
printf, out_unit, ' Filename        = '+filename
printf, out_unit, ' Output_prefix   = '+output_prefix
printf, out_unit, ' Output dir.     = '+out_dir
printf, out_unit, ' Grating         = '+grating
if grating NE 'NONE' then begin
  printf, out_unit, '   cd_width      = '+STRCOMPRESS(cd_width)+' mm'
  printf, out_unit, '   cd_offset     = '+STRCOMPRESS(cd_offset)+' mm'
end
printf, out_unit, ' Detector        = '+detector
printf, out_unit, '   Spatial coord = '+coords_name

; screen output
if NOT(KEYWORD_SET(SILENT)) then begin
  ; Indicate if the FLIPY is set
  if KEYWORD_SET(FLIPY) then begin
    print, '   * FLIPY IS set!'
  end else begin
    print, '   (FLIPY is not set)'
  end
  if n_elements(ROLLAXAY) GT 0 then begin
    print, '   * ROLLAXAY = '+STRING(rollaxay)
  end else begin
    print, '   (no ROLLAXAY value)'
  end
  if KEYWORD_SET(CC_MODE_FLAG) then begin
    print, ' CC_MODE_FLAG keyword set'
  end
  if KEYWORD_SET(MOUSE) then begin
    print, ' MOUSE keyword set'
  end
  if KEYWORD_SET(OVERRIDE_ZERO) then begin
    print, ' OVERRIDE_ZERO keyword set'
  end
  if n_elements(OVERR_WIDTH) GT 0 then begin
    print, ' OVERR_WIDTH = '+STRING(overr_width)+' um'
  end
  if KEYWORD_SET(ASPECT) then begin
    print, ' ASPECT keyword set'
    if KEYWORD_SET(BUT_DONT_APPLY) then begin
      print, '   (will not be applied)'
    end
  end
  if KEYWORD_SET(XRCF_ROWLAND) then begin
    print, ' XRCF_ROWLAND keyword set'
  end
  if KEYWORD_SET(LINE_ANALYSIS) then begin
    print, ' LINE_ANALYSIS keyword set'
  end
  print, ''
end

; Write to html file:
; Indicate if the FLIPY is set
if KEYWORD_SET(FLIPY) then begin
  printf, out_unit, '   * FLIPY IS set!'
end else begin
  printf, out_unit, '   (FLIPY is not set)'
end
if n_elements(ROLLAXAY) GT 0 then begin
  printf, out_unit, '   * ROLLAXAY = '+STRING(rollaxay)
end else begin
  printf, out_unit, '   (no ROLLAXAY value)'
end
if KEYWORD_SET(CC_MODE_FLAG) then begin
  printf, out_unit, ' CC_MODE_FLAG keyword set'
end
if KEYWORD_SET(MOUSE) then begin
  printf, out_unit, ' MOUSE keyword set'
end
if KEYWORD_SET(OVERRIDE_ZERO) then begin
  printf, out_unit, ' OVERRIDE_ZERO keyword set'
end
if n_elements(OVERR_WIDTH) GT 0 then begin
  printf, out_unit, ' OVERR_WIDTH = '+STRING(overr_width)+' um'
end
if KEYWORD_SET(ASPECT) then begin
  printf, out_unit, ' ASPECT keyword set'
  if KEYWORD_SET(BUT_DONT_APPLY) then begin
    printf, out_unit, '   (will not be applied)'
  end
end
if KEYWORD_SET(XRCF_ROWLAND) then begin
  printf, out_unit, ' XRCF_ROWLAND keyword set'
end
if KEYWORD_SET(LINE_ANALYSIS) then begin
  printf, out_unit, ' LINE_ANALYSIS keyword set'
end
printf, out_unit, ''

; NOTE: since this is one big huge hunk of code, there are a ton
; of parameters, arrays, etc that are created during execution.
; Sprinkled though the code are these reminders/summaries of
; what (useful) parameters are available at this stage of
; processing.
; .......................................
;    - Data and Parameters available at this stage:
; filename, output_prefix, theKEYWORDS, out_unit, iwind, clr_*, color24_values
; .......................................

if NOT(KEYWORD_SET(SILENT)) then begin
  print, ' - - - - - - - - - - - - Getting Data ... - - - - - - - - - '
  print, ''
  print, ' Source of data: '+filename
  print, ''
end
printf, out_unit, '</PRE>'
printf, out_unit, '<HR>'
printf,out_unit, '<H3>Getting Data ...</H3>'
printf,out_unit, '<PRE>'
printf,out_unit, ''
printf,out_unit, ' Source of data: '+filename
printf,out_unit, ''
; Read in the file...
if NOT(KEYWORD_SET(SILENT)) then begin
  print, ' Reading FITS file: '+filename
  print, ''
end
printf,out_unit, ' Reading FITS file: '+filename
printf,out_unit, ''
; Always an Empty primary
iext=0
dummy = mrdfits(filename, iext)
; Look for the first extension with TDETX in it...
; (needed because other extensions are possible too, e.g.,
;  the GTI(?) extension with START and STOP values)
;
; GRACEFUL RETURN IF NO TDETX:
; Want to add graceful return if no extension with TDETX
; is found... could do:
;  before the loop:
;    another = 1
;  in the loop:
;    evts = mrdfits(filename, iext, fit_header)
;    another = fxpar(fit_header, 'EXTEND')
;  then change the while to:
;    while NOT(found_it) AND (another EQ 1) do begin
;  finally, have an "if NOT(found_it) then begin ..."
;  block to print message and return...
;  ---> I have not implemented this because there is a
;  chance that EXTEND may not be correctly set!
;
found_it = 0 GT 0
while NOT(found_it) do begin
  iext = iext+1
  evts = mrdfits(filename, iext)
  evts_tags = tag_names(evts)
  found_it = TOTAL(evts_tags EQ 'TDETX') GT 0
end

; Filter out X,Y events GT 10^5
if TOTAL(evts_tags EQ 'X') GT 0 then begin
  nottoobig = where(ABS(evts.X) LT 1.E5 AND ABS(evts.Y) LT 1.E5, nfound)
  evts = evts(nottoobig)  
end

;-----------------------------------------------
; Add ACIS effects to MARX 2.22 simulations
;
; To simulate the quantized ACIS time resolution and
; ACIS streak events modify the TIME, CHIPY, TDETY,
; and DETY coordinates... ONLY fully valid for ACIS-S!
; (will provide correct TIME and CHIPY for ACIS-I
;  but the orientation of the I chips is not 
;  included... so all streaks are in (T)DETY direction)
if KEYWORD_SET(STREAK_MARX) then begin
  if DETECTOR EQ 'ACIS-S' then begin
    marx_timing_sim, evts
  end
  if DETECTOR EQ 'ACIS-I' then begin
    marx_timing_sim, evts, /ACISIARRAY
  end
  if NOT(KEYWORD_SET(SILENT)) then begin
    print, '* STREAK_MARX keyword: called marx_timing_sim'
    print, ''
  end
  printf, out_unit, '* STREAK_MARX keyword: called marx_timing_sim'
  printf,out_unit, ''
end
;-----------------------------------------------

;
; What could/do we have:
;
;     L1 Columns
;
; Timing related:
;  EXPNO TIME
;
; Event Location:
;   (aspect correction is first included in Y X)
;  Y X DETY DETX TDETY TDETX CHIPY CHIPX CCDNODE CCD_ID
;
; Event PHA, Energy, etc. properties
;  STATUS FLTGRADE GRADE ENERGY PI PHA
;
;     L1.5 Columns
;
;  TG_SMAP TG_PART TG_SRCID TG_MLAM TG_LAM TG_M TG_D TG_R GDPY GDPX
;

; Check to make sure there are some events here...
if n_elements(evts) LT 100 then begin
  print, ''
  print, " *** I can't do anything with "+ $
	STRCOMPRESS(n_elements(evts)) + ' events! ***'
  print, ''
  print, ' - - - - - - - - - - - - - - - - - - - - '+SYSTIME()+' - -'
  print, ''
  RETURN
end


if NOT(KEYWORD_SET(SILENT)) then begin
  print, ' Tag names are:'
  print, evts_tags
  print, ''
end
printf,out_unit, ' Tag names are:'
printf,out_unit, evts_tags
printf,out_unit, ''

; Check on ENERGY and TIME here...
; Setup arrays for each of these with "converted" values for
; uniformity, e.g., energy in keV.
Etouse = FLTARR(n_elements(evts))

; Put ENERGY into keV
energy_unit = 'n/a'
; Logic to decide if we have valid energy available to use...
; If the tag is there and if it is non-constant then assume
; it is valid... for now!  Might have to add an "ENERGY_SUCKS"
; keyword to tell s/w to ignore it...

; Check for the TAG:
got_energy = (TOTAL(evts_tags EQ 'ENERGY') GE 1)

; OK, it's there, is it any good?  Catch NaNs also...
if got_energy then begin
  got_energy = NOT(MIN(evts.ENERGY) EQ MAX(evts.ENERGY)) AND $
	NOT( TOTAL(evts.ENERGY NE evts.ENERGY) GE 1 )
  ; If we now don't have valid energy let'em know!
  if NOT(got_energy) then begin
    print, '* ENERGY column is present but invalid.'
    print, '  (a constant value, or contains NaN)
    printf, out_unit, '* ENERGY column is present but invalid.'
    printf, out_unit, '  (a constant value, or contains NaN)
  end
end else begin
  print, '* No ENERGY available.' 
  printf, out_unit, '* No ENERGY available.' 
end

; If valid energy is present, convert it to keV
if got_energy then begin
  ; Fill the array
  Etouse = evts.ENERGY
  ; If the energy value is Inf set it to 0.0 for now
  inf_e = where(Etouse GT 1.E12, nfound)
  if nfound GE 1 then begin
    Etouse(inf_e) = 0.0    
  end
  if MAX(Etouse) GT 1000.0 then begin
    if NOT(KEYWORD_SET(SILENT)) then begin
      print, '* Looks like ENERGY is in eV, converting to keV'
    end
    printf, out_unit, '* Looks like ENERGY is in eV, converting to keV'
    Etouse = Etouse/1000.0
  end else begin
    if NOT(KEYWORD_SET(SILENT)) then begin
      print, ' Looks like ENERGY is in keV'
    end
    printf, out_unit, ' Looks like ENERGY is in keV'
  end
  energy_unit = 'keV'
  ; Set small, zero, and negative energy events to 0.01 keV
  low_e = where(Etouse LT 0.01, nfound)
  if nfound GE 1 then begin
    Etouse(low_e) = 0.010
  end
  ; Correct the ENERGIES if GAIN_FACTORS is present
  if n_elements(gain_factors) EQ 10 then begin
    if NOT(KEYWORD_SET(SILENT)) then begin
      print, ' '
      print, '* Correcting ENERGY with GAIN_FACTORS:'
      print, gain_factors
      print, ' '
    end

    printf, out_unit, '* Correcting ENERGY with GAIN_FACTORS:'
    printf, out_unit, gain_factors
    printf, out_unit, ' '
    for iccd=0, 9 do begin
      this_ccd = where(evts.CCD_ID EQ iccd, nfound)
      if nfound GT 0 then Etouse(this_ccd) = Etouse(this_ccd) * gain_factors(iccd)
    end
  end
end

if TOTAL(evts_tags EQ 'TIME') GE 1 then begin
  ; Create the time since first event... ("Floating Time")
  if NOT(KEYWORD_SET(SILENT)) then begin
    print, ' Creating ftime from TIME'
  end
  printf, out_unit, ' Creating ftime from TIME'
  abs_start_time = MIN(evts.TIME)
  ftime = DOUBLE(evts.TIME - abs_start_time)
  interval_duration = MAX(ftime)
  time_unit = 'second'
end else begin
  if NOT(KEYWORD_SET(SILENT)) then begin
    print, ' No TIME information, use event number as TIME'
  end
  printf, out_unit, ' No TIME information, use event number as TIME'
  ftime = DOUBLE(LINDGEN(n_elements(evts)))
  abs_start_time = 0.0
  interval_duration = MAX(ftime)
  time_unit = 'event'
end
live_interval = interval_duration

; And report the most basic info...
if NOT(KEYWORD_SET(SILENT)) then begin
  print, ''
  print, ' Total Events = '+STRCOMPRESS(n_elements(evts))
  print, ' Start time = '+STRCOMPRESS(abs_start_time)+' '+time_unit+'s'
  print, ' Interval duration = '+STRCOMPRESS(interval_duration)+' '+time_unit+'s'
  print, ' Ave Event Rate = '+STRCOMPRESS(FLOAT(n_elements(evts))/ $
			interval_duration)+' events/'+time_unit
  print, ''
end
printf, out_unit, ''
printf, out_unit, ' Total Events = '+STRCOMPRESS(n_elements(evts))
printf, out_unit, ' Start time = '+ $
	STRCOMPRESS(abs_start_time)+' '+time_unit+'s'
printf, out_unit, ' Interval duration = '+ $
	STRCOMPRESS(interval_duration)+' '+time_unit+'s'
printf, out_unit, ' Ave Event Rate = '+ $
	STRCOMPRESS(FLOAT(n_elements(evts))/ $
		interval_duration)+' events/'+time_unit
printf, out_unit, ''
; - - - - - end of FITS input - - - - - 

rpf_add_param, rpf, 'filename', filename
rpf_add_param, rpf, 'detector', detector
rpf_add_param, rpf, 'grating', grating

rpf_add_param, rpf, 'file_events', n_elements(evts)

rpf_add_param, rpf, 'abs_start_time', abs_start_time, $
	UNIT = time_unit
rpf_add_param, rpf, 'interval_duration', interval_duration, $
	UNIT = time_unit
rpf_add_param, rpf, 'ave_event_rate', FLOAT(n_elements(evts)) / $
	interval_duration, ERROR = SQRT(FLOAT(n_elements(evts))) / $
	interval_duration, UNIT = 'event/'+time_unit

; .......................................
;    - Data and Parameters available at this stage:
; filename, output_prefix, theKEYWORDS, out_unit, iwind, clr_*, color24_values
; evts, evts_tags, energy_unit,
; abs_start_time, interval_duration, ftime, time_unit
; .......................................


; - - - - - - - - Coordinates and Pixel size - - - - - - - - 
if NOT(KEYWORD_SET(SILENT)) then begin
  print, ' - - - - - - - - - - - - Coordinates and Pixel Size... - - - - - - - '
  print, ''
end
printf, out_unit, "</PRE>"
printf, out_unit, '<HR>'
printf, out_unit, '<H3>Coordinates and Pixel Size...</H3>'
printf, out_unit, "<PRE>"
printf, out_unit, ""

; Check for ACIS-S CC mode where TDETY is a constant value
; This will not work for ACIS-I ?  

if (DETECTOR EQ 'ACIS-S') then begin
  if KEYWORD_SET(CC_MODE_FLAG) then begin
    if NOT(KEYWORD_SET(SILENT)) then begin
      print, '* CC_MODE_FLAG set: setting TDETYs to 511.'    
    end
    printf, out_unit, '* CC_MODE_FLAG set: setting TDETYs to 511.'    
    evts.TDETY = 511
  end
  if (MIN(evts.TDETY) EQ MAX(evts.TDETY)) then begin
    cc_mode = (1 EQ 1) 
    if NOT(KEYWORD_SET(SILENT)) then begin
      print, '* Looks like ACIS-S CC mode data'
    end
    printf, out_unit, '* Looks like ACIS-S CC mode data'
  end else begin
    if NOT(KEYWORD_SET(SILENT)) then begin
      print, ' (Not CC mode data)'
    end
    printf, out_unit, ' (Not CC mode data)'
    cc_mode = (1 EQ 0)
  end
end else cc_mode = (1 EQ 0)

; Set the value of COORDS_NAME if it was not supplied
if STRPOS(coords_name, 'Not') GE 0 then begin
  ; Check for the Sky coord.s, X,Y :
  if (TOTAL(evts_tags EQ 'X') GE 1) then begin
    coords_name = 'Sky'
  end else begin
    if (TOTAL(evts_tags EQ 'DETX') GE 1) then begin
      coords_name = 'DET'
    end else begin
      coords_name = 'TDET'  ; assuming these are always available...
    end
  end
end else begin
  ; OK, the user specified a desired coordinates to use
  ; Verify that the desired coordinates are in the tags - if not demote them...
  ; Asked for Sky but not there
  if ( (coords_name EQ 'Sky') AND NOT(TOTAL(evts_tags EQ 'X') GE 1) )then begin
    coords_name = 'DET'
    if NOT(KEYWORD_SET(SILENT)) then begin
      print, '* Sky coordinates (X,Y) not available - try DET'
    end
    printf, out_unit, '* Sky coordinates (X,Y) not available - try DET'
  end
  ; Asked for DET but not there
  if ( (coords_name EQ 'DET') AND NOT(TOTAL(evts_tags EQ 'DETX') GE 1) )then begin
    if NOT(KEYWORD_SET(SILENT)) then begin
      print, '* DET coordinates not available - using TDET'
    end
    printf, out_unit, '* DET coordinates not available - using TDET'
    coords_name = 'TDET'
  end
end

; Set the "processing method" to indicate how the spatial coordinates
; for grating dispersion are arrived at... (for L1.5 will use 'L1.5').
; Use this in the .gif output filenames.
if KEYWORD_SET(ASPECT) AND NOT(KEYWORD_SET(BUT_DONT_APPLY)) then begin
  proc_method = 'a'+coords_name
end else begin
  proc_method = coords_name 
end
save_proc_method = proc_method

; write the value of this to the output rdb file
rpf_add_param, rpf, 'proc_method', proc_method

; For plot labeling define the basic axis names... to be modified
; in the following to indicate sign flipping, bluring, etc.
x_name = coords_name+'X'
y_name = coords_name+'Y'

; Based on the COORDS selection, create and fill the arrays Xtouse Ytouse and
; set the pixel size and axis names.
; The DETX, DETY and SkyX, SkyY pixels are defined in angular units, so the
; conversion to mm requires the angular size of a pixel and
; a focal length:
;    pix_ang_size = 0.132   ; arc sec
;    pix_foc_leng = 10065.5 ; mm
;    pixel_size = pix_foc_leng * !DTOR*pix_ang_size/3600.
;
; NOTE that the DetY nominally gets a -1 to keep same orientation
; as TDET and Sky systems...
CASE coords_name OF
  'Sky': begin
    ; No bluring applied here: sky coords should be aspect corrected, etc.
    ; and in real, non-quantized, values
    Xtouse = FLOAT(evts.X)
    Ytouse = FLOAT(evts.Y)
    if STRPOS(DETECTOR,'HRC') GE 0 then begin
      pix_ang_size = hrc_pix_ang_size
      pix_foc_leng = hrc_pix_foc_leng
      pixel_size = pix_foc_leng * !DTOR*pix_ang_size/3600.
    end else begin
      pix_ang_size = acis_pix_ang_size
      pix_foc_leng = acis_pix_foc_leng
      pixel_size = pix_foc_leng * !DTOR*pix_ang_size/3600.
    end
  end
  'DET': begin
    Xtouse = FLOAT(evts.DETX)
    Ytouse = -1.0*FLOAT(evts.DETY)
    ; No need to blur: level 1 has DET blurred already - 8/1/99 dd
    ; blur by +/- 0.5 pixel to avoid aliassing with binning...
    ; Xtouse = FLOAT(Xtouse) + (randomu(SEED,n_elements(evts))-0.5)
    ; Ytouse = FLOAT(Ytouse) + (randomu(SEED,n_elements(evts))-0.5)
    ; x_name = x_name + 'b'
    ; y_name = y_name + 'b'
    if STRPOS(DETECTOR,'HRC') GE 0 then begin
      pix_ang_size = hrc_pix_ang_size
      pix_foc_leng = hrc_pix_foc_leng
      pixel_size = pix_foc_leng * !DTOR*pix_ang_size/3600.
    end else begin
      pix_ang_size = acis_pix_ang_size
      pix_foc_leng = acis_pix_foc_leng
      pixel_size = pix_foc_leng * !DTOR*pix_ang_size/3600.
    end
  end
  'TDET': begin
    Xtouse = FLOAT(evts.TDETX)
    Ytouse = FLOAT(evts.TDETY)
    ; These coordinates are still quantized to a pixel, so
    ; blur by +/- 0.5 pixel to avoid aliassing with binning...
    Xtouse = FLOAT(Xtouse) + (randomu(SEED,n_elements(evts))-0.5)
    Ytouse = FLOAT(Ytouse) + (randomu(SEED,n_elements(evts))-0.5)
    x_name = x_name + 'b'
    y_name = y_name + 'b'
    if STRPOS(DETECTOR,'HRC') GE 0 then begin
      pixel_size = hrc_pixel_size
    end else begin
      pixel_size = acis_pixel_size
    end
    ; If it is ACIS-S and CCD_ID is present then correct
    ; for the TDETX offsets...
    if (DETECTOR EQ 'ACIS-S') AND $
		(TOTAL(evts_tags EQ 'CCD_ID') GE 1) then begin
      ; Read in the TDETX offsets
      if STRPOS(!DDLOCATION, 'HAK') LT 0 then begin 
        ; CALDB location of the file
        tdet_offset_file = !DDACISCAL+'/cip/acisD1999-07-23tdetoffN0002.rdb'
      end else begin
        ; HAK Stand-alone location of the file
        tdet_offset_file = !DDHAKDATA+'/acisD1999-07-23tdetoffN0002.rdb'
      end
      tdo = rdb_read(tdet_offset_file, /SILENT)
      ; Go through the S-array CCDs and correct them
      for ic = 4, 9 do begin
        tdoname = 'tdetx_offset_id'+STRING(ic,FORMAT='(I1)')
        rpf_get_value, tdo, tdoname, tdovalue
        ; find events from this CCD
        tdosel = where(evts.CCD_ID EQ ic, ntdo)
        if ntdo GE 1 then begin
          Xtouse(tdosel) = Xtouse(tdosel) + tdovalue
        end
      end
      ; and add a "c" to indicate corrected:
      x_name = x_name + 'c'
    end
  end
  ELSE: begin
    ; Can't arrive here... [Don't bet on it!]
  end
ENDCASE

; Now some Y-madness: CC and FLIPY
; add prefixes to y_name
if cc_mode AND (COORDS_NAME ne 'Sky') then begin
  ; The Y value is meaningless so
  ; assign the yaxis a +/-4 pixel blur
  Ytouse = Ytouse + $
	4.0 * 2.*(randomu(SEED,n_elements(Ytouse))-0.5)
  if NOT(KEYWORD_SET(SILENT)) then begin
    print, '* CC mode: blur '+y_name+' by +/- 4 pixels'
  end
  printf, out_unit, '* CC mode: blur '+y_name+' by +/- 4 pixels'
  y_name = 'cc'+y_name
end else begin
  ; The FLIPY is here for HRC but it will work for other detectors too...
  ; Add a sign to the Y name: 
  if KEYWORD_SET(FLIPY) then begin
    if NOT(KEYWORD_SET(SILENT)) then begin
      print, '* Changing the sign of '+y_name
    end
    printf, out_unit, '* Changing the sign of '+y_name
    Ytouse = -1.0 * Ytouse
    ; YFLIP: TDET and Sky get -, DET gets +
    if coords_name EQ 'DET' then begin
      y_name = '+'+y_name
    end else begin
      y_name = '-'+y_name
    end
  end else begin
    ; No flip: TDET and Sky get no prefix, DET gets -
    if coords_name EQ 'DET' then begin
      y_name = '-'+y_name
    end else begin
      ; y_name = y_name
    end
  end
end

; Report the Coords results...
if NOT(KEYWORD_SET(SILENT)) then begin
  print, ''
  print, ' Spatial coordinates are : '+ x_name +', '+ y_name
  print, ' pixel size  = '+STRING(1.E3*pixel_size,FORMAT='(F7.4)')+' microns'
  print, ' Processing method = '+proc_method
  print, ''
end

printf, out_unit, ''
printf, out_unit, ' Spatial coordinates are : '+ x_name +', '+ y_name
printf, out_unit, ' pixel size  = '+STRING(1.E3*pixel_size,FORMAT='(F7.4)')+' microns'
printf, out_unit, ' Processing method = '+proc_method
printf, out_unit, ''


; - - - - - - - - - - - Setup HTML output - - - - - - - - 
; OK that we have proc_method we can open the output HTML file
; and write out the lines that have been stored up...
; - - - - - - - - HTML output file - - - - - - - - -
;
; Close the temporary file
CLOSE, out_unit
; and open the real file...
OPENW, out_unit, out_dir+'/'+output_prefix+'_'+proc_method+'_summary.html', /GET
; Create corresponding rpf output file names:
rpf_file_name = out_dir+'/'+output_prefix+'_'+proc_method+'_summary.rdb'
rpf_list_name = out_dir+'/'+output_prefix+'_'+proc_method+'_summary.txt'

; Setup HTML header etc.
printf, out_unit, '<HTML>'
printf, out_unit, '<HEAD>'
printf, out_unit, '  <TITLE>'+output_prefix+'</TITLE>'
printf, out_unit, '</HEAD>
printf, out_unit, '
printf, out_unit, '<BODY TEXT="#000000"  BGCOLOR="#FFFFFF" '
printf, out_unit, 'LINK="#0000FF" VLINK="#FF00FF" ALINK="#FF00FF">'
printf, out_unit, ''
printf, out_unit, '  <H2 align="center">'+output_prefix+'_'+proc_method+'</H2>'
printf, out_unit, ''
; Keep it simple, default to <PRE> format...
printf, out_unit, '<PRE>'
;
; Now add the temporary info to the output file
OPENR, temp_unit, out_dir+'/temp_summary.html', /GET
while NOT(EOF(temp_unit)) do begin
  line_in = ''
  readf, temp_unit, line_in
  printf, out_unit, line_in
end
CLOSE, temp_unit
FREE_LUN, temp_unit
SPAWN, 'rm ' + out_dir + '/temp_summary.html'

; - - - - - - - - - - - Setup plot output - - - - - - - - 
; Plot to .gif
; Setup a window...
;
; Save the original device and plot values (thanks Jim!)
Orig_device = !d.name
Orig_plot = !p      ; save it all?
;
if KEYWORD_SET(ZBUFFER) then begin
  set_plot, 'Z' 
end else begin
  set_plot, 'X'
  zbuffer = 0  ; can pass it to other routines...
end

; Output window
iwind = 0
if KEYWORD_SET(ZBUFFER) then begin
  device, set_resolution=[700,700]
end else begin
  window, iwind, xsi=700, ysi=700
end

; Hang in there with me on this - I'm new to 24bit color!
; See if it is 24 bit color...
color24bit = !d.n_colors EQ 16777216

; Color table for PHA-->color coding
; 0=black, 1=white, 2=darkbackground, 3-255 = red to blue
  dd_load_ct, RED=red_ct, GREEN=green_ct, BLUE=blue_ct, /OTHER

; Set colors: if it is 8 bit then the colors are 
; 0 to 255 according to the table above; if it is
; 24 bit then the "color" is the 24bit RGB combination
; in that case the 0-255 color table value is converted
; to 24 bit color:
color24_values = red_ct + 256L * (green_ct + 256L * blue_ct)

;
; Color is used here for two purposes:
;  1) delineate different curves on plots
;  2) color-code photons by their energy
;
; Set some curve colors based on 8 bit, then convert
; to 24 bit values if needed.
clr_back = 0  ; black  
clr_wht = 1  ; white
clr_red = 3
clr_org = 40
clr_yel = 85
clr_grn = 125
clr_blu = 250
;
if color24bit AND KEYWORD_SET(SCREEN24) then begin
  print, ' Using 24 bit colors for display...'
  print, ''
  ic = clr_back
  clr_back = color24_values(ic)
  ic = clr_wht
  clr_wht = color24_values(ic)
  ic = clr_red
  clr_red = color24_values(ic)
  ic = clr_org
  clr_org = color24_values(ic)
  ic = clr_yel
  clr_yel = color24_values(ic)
  ic = clr_grn
  clr_grn = color24_values(ic)
  ic = clr_blu
  clr_blu = color24_values(ic)
end
;
; NOTE: The SCREEN24 KEYWORD will caluse 24 bit colors to show on the screen as
; correct colors BUT the write_gif will NOT be correct -
; So, use /SCREEN24 for viewing at terminal, rerun without /SCREEN24 to
; get valid .gif files...
;

; .......................................
;    - Data and Parameters available at this stage:
; filename, output_prefix, theKEYWORDS, out_unit, iwind, clr_*, color24_values
; evts, evts_tags, energy_unit, interval_duration, ftime, time_unit
; cc_mode, pixel_size, Xtouse, x_name, Ytouse, y_name, proc_method
; .......................................

; - - - - - - - Selection Criteria for Nominally Valid Events - - - -
; Report the effects of each selection...
; Parameters:
; Fractional time range to use:
ft_frac_min = 0.0  ; 0.0 default, for MC-3.001: 0.460 (4ks) 
ft_frac_max = 1.0  ; 1.0 default,               0.578 (5ks) 
; Energies to use:
max_sel_energy = 10.0 ; keV
min_sel_energy = 0.2  ; keV
max_zo_energy = 6.0 ; keV
min_zo_energy = 0.7  ; keV
; Energies for color coding (red to blue)
max_clr_energy = 7.0 ; keV
min_clr_energy = 0.4  ; keV
; Bin size for ENERGY histograms
; Was log binning:
; e_bin_ratio = 1.02  ; En+1/En
; now follow the PI binning: 14.6 eV/bin
e_bin_ratio = pi_energy_bin_spacing  ; En+1 - En
; PHA region for selection
min_sel_pha = 1.0  ; for HRC only
max_sel_pha = 250.0  ; for HRC only
; PHA range for plotting and color coding (not for selection)
min_clr_pha = 0
if STRPOS(DETECTOR,'ACIS') GE 0 then begin
  max_clr_pha = 2500
end else begin
  max_clr_pha = 256
end
; For HRC-I: Select ACIS-like cross-dispersion width for 
; consideration...
hrci_yreg = 4000.0  ; hrc pixels ~ 1024 ACIS pixels
;

if NOT(KEYWORD_SET(SILENT)) then begin
  print, ' - - - - - - - - - - - - Showing and Selecting Events... - - - - - - - '
  print, ''
end
printf, out_unit, "</PRE>"
printf, out_unit, '<HR>'
printf, out_unit, '<H3>Showing and Selecting Events...</H3>'
printf, out_unit, "<PRE>"
printf, out_unit, ""

; First...
; Show all events in Xtouse, Ytouse
; and a histogram of ENERGY (or PHA) if available

if GRATING EQ 'NONE' AND STRPOS(DETECTOR, '-I') GE 0 then begin
  ; larger X-Y area
  !p.multi = [0,1,2]
  triplot_charsize = 1.0
end else begin
  !p.multi = [0,1,3]
  triplot_charsize = 1.81
end

; ENERGY or PHA available?
if (got_energy) OR $
	(TOTAL(evts_tags EQ 'PHA') GE 1) then begin
  ; OK, we have something - make more plots
  ; Prefer to use energy if it is present
  if got_energy then begin
    ; Log energy color coding...
    ; energy_colors = 3+FIX(252.* $
    ;	(ALOG(Etouse) - ALOG(min_clr_energy))/ $
    ;		(ALOG(max_clr_energy) - ALOG((min_clr_energy > 0.06))) )
    ; Prefer..
    ; Linear coding...
    energy_colors = 3+ ( FIX( (251.* $
	(Etouse - min_clr_energy)/ $
		(max_clr_energy - min_clr_energy) ) < 251.   ) > 0)
  end else begin
    ; PHA available...
    energy_colors = 3+ ( FIX( (251.* $
	(evts.PHA - min_clr_pha)/ $
		(max_clr_pha - min_clr_pha) ) < 251.) > 0)
  end
  if color24bit AND KEYWORD_SET(SCREEN24) then begin
    ; convert the colors to 24 bit...
    energy_colors = color24_values(energy_colors)
  end
end else begin
  ; No ENERGY or PHA to provide color coding...
  energy_colors = clr_grn
end

plot, Xtouse, Ytouse, PSYM=3, $
	XSTYLE=1, YSTYLE=1, $
	BACK = clr_back, COLOR = clr_wht, /NODATA, $
        TITLE='X-Y Plot of ALL Events', $
        XTITLE=x_name+' (pixels)', $
        YTITLE=y_name+' (pixels)', $
	CHARSIZE=triplot_charsize
plots, Xtouse, Ytouse, PSYM=3, COLOR=energy_colors, NOCLIP=0

if GRATING EQ 'NONE' AND STRPOS(DETECTOR, '-I') GE 0 then begin
  ; setup for rest of plots on page
  !p.multi = [2,1,4]
  triplot_charsize = 1.81
end

; ENERGY plots if available
if got_energy then begin
  plot_io, Xtouse, Etouse, PSYM=3, $
	XSTYLE=1, YSTYLE=1, YRANGE=[min_sel_energy,max_sel_energy], $
	BACK=clr_back, COLOR=clr_wht, /NODATA, $
        TITLE='X-E Plot of ALL Events', $
        XTITLE=x_name+' (pixels)', $
        YTITLE='Detector Energy ('+energy_unit+')', $
	CHARSIZE=triplot_charsize
  plots, Xtouse, Etouse, $
	PSYM=3, COLOR=energy_colors, NOCLIP=0
  lin_hist, Etouse, e_bin_ratio, bines, bincounts
  use_em = where(bines GT min_sel_energy AND $
			bines LT max_sel_energy)
  plot_oo, bines, bincounts, PSYM=10, $
	XRANGE=[min_sel_energy,max_sel_energy], XSTYLE=1, $
	YRANGE=[(0.5*MIN(bincounts(use_em))) > 0.5, $
		2.0*MAX(bincounts(use_em))], YSTYLE=1, $
	BACK=clr_back, COLOR=clr_wht, $
        TITLE='Detector Pulse Height Distribution of ALL Events', $
        XTITLE='Detector Energy ('+energy_unit+')', $
        YTITLE='Counts/bin', $
	CHARSIZE=triplot_charsize
end else begin
  ; PHA plots if available and ENERGY isn't
  if (TOTAL(evts_tags EQ 'PHA')) GE 1 then begin
    plot, Xtouse, evts.PHA, PSYM=3, $
	XSTYLE=1, YRANGE=[0.,MAX(evts.PHA)], YSTYLE=1, $
	BACK=clr_back, COLOR=clr_wht, /NODATA, $
        TITLE='X-PHA Plot of ALL Events', $
        XTITLE=x_name+' (pixels)', $
        YTITLE='Detector PHA', $
	CHARSIZE=triplot_charsize
    plots, Xtouse, evts.PHA, $
	PSYM=3, COLOR=energy_colors, NOCLIP=0
    lin_hist, evts.PHA, 1.0, bines, bincounts
    plot, bines, bincounts, PSYM=10, $
	XSTYLE=1, XRANGE=[0.,MAX(evts.PHA)], $
	YSTYLE=1, $
	BACK=clr_back, COLOR=clr_wht, $
        TITLE='Detector Pulse Height Distribution of ALL Events', $
        XTITLE='Detector PHA', $
        YTITLE='Counts/bin', $
	CHARSIZE=triplot_charsize
  end
end
nevts = n_elements(evts)

; Finish the .gif output
if NOT(KEYWORD_SET(ZBUFFER)) then wshow,iwind,iconic=0
image = tvrd()
tvlct, red, green, blue, /GET
gif_out = output_prefix+'_'+proc_method+'_showALL.gif'
write_gif, out_dir+'/'+gif_out, image, red, green, blue

; Add .gif link
printf, out_unit, "</PRE>"
printf, out_unit, "<UL>"
printf, out_unit, '<LI><B><A href="'+gif_out+'">'+'Plots of ALL Events'+'</A></B>'
printf, out_unit, "</UL>"
printf, out_unit, "<PRE>"

if KEYWORD_SET(MOUSE) then begin
  print, '    !!! Click Mouse anywhere to Continue !!!'
  print, ''
  cursor, x, y, 3
end

; Now perform selections in sequence...

; TIME
keep = where(ftime GE ft_frac_min*interval_duration AND $
		ftime LE ft_frac_max*interval_duration, nfound)
if nfound GT 0 then begin
  if NOT(KEYWORD_SET(SILENT)) then begin
    print, ' Keeping TIME-in-range events, '+ $
		STRCOMPRESS((100.0*nfound)/nevts)+' %'
    print, '  (from '+STRCOMPRESS(ft_frac_min*interval_duration)+$
		' to '+STRCOMPRESS(ft_frac_max*interval_duration)+')'
  end
  printf, out_unit, ' Keeping TIME-in-range events, '+ $
		STRCOMPRESS((100.0*nfound)/nevts)+' %'
  printf, out_unit, '  (from '+STRCOMPRESS(ft_frac_min*interval_duration)+$
		' to '+STRCOMPRESS(ft_frac_max*interval_duration)+')'
  evts = evts(keep)
  fstart_time = MIN(ftime(keep))
  ftime = ftime(keep) - fstart_time
  interval_duration = MAX(ftime)
  live_interval = interval_duration
  abs_start_time = abs_start_time + fstart_time
  Etouse = Etouse(keep)
  Xtouse = Xtouse(keep)
  Ytouse = Ytouse(keep)
  nevts = n_elements(evts)
  if NOT(KEYWORD_SET(SILENT)) then begin
    print, ' Start time = '+STRCOMPRESS(abs_start_time)+ $
		' '+time_unit+'s'
    print, ' Interval duration = '+STRCOMPRESS(interval_duration)+ $
		' '+time_unit+'s'
  end
  printf, out_unit, ' Start time = '+STRCOMPRESS(abs_start_time)+ $
		' '+time_unit+'s'
  printf, out_unit, ' Interval duration = '+STRCOMPRESS(interval_duration)+ $
		' '+time_unit+'s'
end else begin
  if NOT(KEYWORD_SET(SILENT)) then begin
    print, '* There were no TIME-in-range events, keep them all.'
  end
  printf, out_unit, '* There were no TIME-in-range events, keep them all.'
end

; HRC Spatial
; Limit HRC to ~ACIS width region in Y for grating observations...
if (STRPOS(DETECTOR,'HRC') GE 0) AND (GRATING NE 'NONE') then begin
  aveY = TOTAL(FLOAT(Ytouse))/n_elements(evts)
  yoffset = Ytouse - aveY
  keep = where( ABS(yoffset) LT hrci_yreg/2.0, nfound) 
  if nfound GT 0 then begin
    if NOT(KEYWORD_SET(SILENT)) then begin
      print, ' HRC: Keeping central stripe Y events, '+ $
		STRCOMPRESS((100.0*nfound)/nevts)+' %'
    end
    printf, out_unit, ' HRC: Keeping central stripe Y events, '+ $
		STRCOMPRESS((100.0*nfound)/nevts)+' %'
    evts = evts(keep)
    ftime = ftime(keep)
    Etouse = Etouse(keep)
    Xtouse = Xtouse(keep)
    Ytouse = Ytouse(keep)
    nevts = n_elements(evts)
  end else begin
    if NOT(KEYWORD_SET(SILENT)) then begin
      print, '* There were no HRC events in the central stripe region,' + $
		' keep them all.'
    end
    printf, out_unit, '* There were no HRC-I events in the central stripe region,' + $
		' keep them all.'
  end
end


; STATUS/QUALCODE
if STRPOS(DETECTOR,'HRC') GE 0 then begin
  ; HRC STATUS...
  if TOTAL(evts_tags EQ 'STATUS') GE 1 then begin
    ; Well status is present...  is it a single value or an array of 4 ?
    stat_size = SIZE(evts(0).STATUS)
    ; Proceed here if it is not an array
    if stat_size(0) EQ 0 then begin
      keep = where( (evts.STATUS AND '3FFF00'xL) EQ 0, nfound) 
      if nfound GT 0 then begin
        if NOT(KEYWORD_SET(SILENT)) then begin
          print, ' Keeping "(STATUS AND 3FFF00xL) EQ 0" events, '+ $
		STRCOMPRESS((100.0*nfound)/nevts)+' %'
        end
        printf, out_unit, ' Keeping "(STATUS AND 3FFF00xL) EQ 0" events, '+ $
		STRCOMPRESS((100.0*nfound)/nevts)+' %'
        evts = evts(keep)
        ftime = ftime(keep)
        Etouse = Etouse(keep)
        Xtouse = Xtouse(keep)
        Ytouse = Ytouse(keep)
        nevts = n_elements(evts)
      end else begin
        if NOT(KEYWORD_SET(SILENT)) then begin
          print, '* There were no "(STATUS AND 3FFF00xL) EQ 0" events,' + $
		' keep them all.'
        end
        printf, out_unit, '* There were no "(STATUS AND 3FFF00xL) EQ 0" events,' + $
		' keep them all.'
      end
    end else begin
      if NOT(KEYWORD_SET(SILENT)) then begin
        print, '* STATUS is present but is an array of bytes - Not implemented'
      end
      printf, out_unit, '* STATUS is present but is an array of bytes - Not implemented'
    end
  end else begin
    if NOT(KEYWORD_SET(SILENT)) then begin
      print, ' No STATUS selection'
    end
    printf, out_unit, ' No STATUS selection'
  end
end else begin
  ; ACIS STATUS...
  if TOTAL(evts_tags EQ 'STATUS') GE 1 then begin
    ; Well status is present...  is it a single value or an array of 2 ?
    stat_size = SIZE(evts(0).STATUS)
    ; Proceed here if it is single value or a two element array ("16x")
    if stat_size(0) EQ 0 OR $
		(stat_size(0) EQ 1 AND stat_size(1) EQ 2) then begin
      if stat_size(0) EQ 0 then begin
        keep = where(evts.STATUS EQ 0, nfound)
      end else begin
        keep = where(evts.STATUS(0) EQ 0 AND $
			evts.STATUS(1) EQ 0, nfound)
      end
      if nfound GT 0 then begin
        if NOT(KEYWORD_SET(SILENT)) then begin
          print, ' Keeping STATUS=0 events, '+ $
		STRCOMPRESS((100.0*nfound)/nevts)+' %'
        end
        printf, out_unit, ' Keeping STATUS=0 events, '+ $
		STRCOMPRESS((100.0*nfound)/nevts)+' %'
        evts = evts(keep)
        ftime = ftime(keep)
        Etouse = Etouse(keep)
        Xtouse = Xtouse(keep)
        Ytouse = Ytouse(keep)
        nevts = n_elements(evts)
      end else begin
        if NOT(KEYWORD_SET(SILENT)) then begin
          print, '* There were no STATUS=0 events, keep them all.'
        end
        printf, out_unit, '* There were no STATUS=0 events, keep them all.'
      end
    end else begin
      if NOT(KEYWORD_SET(SILENT)) then begin
        print, '* STATUS is present but unexpected format - Not implemented'
      end
      printf, out_unit, $
	'* STATUS is present but unexpected format - Not implemented'
    end
  end else begin
    if NOT(KEYWORD_SET(SILENT)) then begin
      print, ' No STATUS selection'
    end
    printf, out_unit, ' No STATUS selection'
  end
end


if TOTAL(evts_tags EQ 'QUALCODE') GE 1 then begin
  keep = where(evts.QUALCODE EQ 0, nfound)
  if nfound GT 0 then begin
    if NOT(KEYWORD_SET(SILENT)) then begin
      print, ' Keeping QUALCODE=0 events, '+ $
		STRCOMPRESS((100.0*nfound)/nevts)+' %'
    end
    printf, out_unit, ' Keeping QUALCODE=0 events, '+ $
		STRCOMPRESS((100.0*nfound)/nevts)+' %'
    evts = evts(keep)
    ftime = ftime(keep)
    Etouse = Etouse(keep)
    Xtouse = Xtouse(keep)
    Ytouse = Ytouse(keep)
    nevts = n_elements(evts)
  end else begin
    if NOT(KEYWORD_SET(SILENT)) then begin
      print, '* There were no QUALCODE=0 events, keep them all.'
    end
    printf, out_unit, '* There were no QUALCODE=0 events, keep them all.'
  end
end else begin
  if NOT(KEYWORD_SET(SILENT)) then begin
    print, ' No QUALCODE selection'
  end
  printf, out_unit, ' No QUALCODE selection'
end

; Make a nominal selection on GRADE (= 0,2,3,4,6)
if TOTAL(evts_tags EQ 'GRADE') GE 1 then begin
  ; print, the grade distribution
  if NOT(KEYWORD_SET(SILENT)) then begin
    print, ' GRADE distribution:'
  end
  printf, out_unit, ' GRADE distribution:'
  grade_hist = histogram(evts.grade)
  totevts = FLOAT(n_elements(evts))
  for ig=0,n_elements(grade_hist)-1 do begin
    if NOT(KEYWORD_SET(SILENT)) then begin
      print, '  '+STRING(ig,FORMAT='(I3)')+' : ' + $
		STRING(grade_hist(ig),FORMAT='(I8)') + ',  ' + $
		STRING(100.0*FLOAT(grade_hist(ig))/totevts,FORMAT='(F7.2)') + ' %'
    end
    printf, out_unit, '  '+STRING(ig,FORMAT='(I3)')+' : ' + $
		STRING(grade_hist(ig),FORMAT='(I8)') + ',  ' + $
		STRING(100.0*FLOAT(grade_hist(ig))/totevts,FORMAT='(F7.2)') + ' %'
  end
  keep = where( (evts.GRADE EQ 0 OR evts.GRADE EQ 2 OR $
		 evts.GRADE EQ 3 OR evts.GRADE EQ 4 OR $
		evts.GRADE EQ 6), nfound)
  if nfound GT 0 then begin
    if NOT(KEYWORD_SET(SILENT)) then begin
      print, ' Keeping GRADE = 0,2,3,4,6 events, '+ $
		STRCOMPRESS((100.0*nfound)/nevts)+' %'
    end
    printf, out_unit, ' Keeping GRADE = 0,2,3,4,6 events, '+ $
		STRCOMPRESS((100.0*nfound)/nevts)+' %'
    evts = evts(keep)
    ftime = ftime(keep)
    Etouse = Etouse(keep)
    Xtouse = Xtouse(keep)
    Ytouse = Ytouse(keep)
    nevts = n_elements(evts)
  end else begin
    if NOT(KEYWORD_SET(SILENT)) then begin
      print, '* There were no GRADE = 0,2,3,4,6 events, keep them all.'
    end
    printf, out_unit, '* There were no GRADE = 0,2,3,4,6 events, keep them all.'
  end
end else begin
  if NOT(KEYWORD_SET(SILENT)) then begin
    print, ' No GRADE selection'
  end
  printf, out_unit, ' No GRADE selection'
end

; Make a nominal selection on ENERGY
if got_energy then begin
  keep = where( Etouse GT min_sel_energy AND $
		Etouse LT max_sel_energy, nfound)
  if nfound GT 0 then begin
    if NOT(KEYWORD_SET(SILENT)) then begin
      print, ' Keeping ENERGY selected events, '+ $
		STRCOMPRESS((100.0*nfound)/nevts)+' %'
      print, '  (from '+STRCOMPRESS(min_sel_energy)+$
		' to '+STRCOMPRESS(max_sel_energy)+' keV)'
    end
    printf, out_unit, ' Keeping ENERGY selected events, '+ $
		STRCOMPRESS((100.0*nfound)/nevts)+' %'
    printf, out_unit, '  (from '+STRCOMPRESS(min_sel_energy)+$
		' to '+STRCOMPRESS(max_sel_energy)+' keV)'
    evts = evts(keep)
    ftime = ftime(keep)
    Etouse = Etouse(keep)
    Xtouse = Xtouse(keep)
    Ytouse = Ytouse(keep)
    nevts = n_elements(evts)
  end else begin
    if NOT(KEYWORD_SET(SILENT)) then begin
      print, '* There were no acceptable ENERGY events, keep them all.'
      print, '  (Candidates range: ', MIN(Etouse), ' to ', MAX(Etouse), '; )'
      print, '  (none in range '+STRCOMPRESS(min_sel_energy)+$
		' to '+STRCOMPRESS(max_sel_energy)+' keV)'
    end
    printf, out_unit, '* There were no acceptable ENERGY events, keep them all.'
    printf, out_unit, '  (Candidates range: ', MIN(Etouse), ' to ', $
			MAX(Etouse), '; )'
    printf, out_unit, '  (none in range '+STRCOMPRESS(min_sel_energy)+$
		' to '+STRCOMPRESS(max_sel_energy)+' keV)'
  end
end else begin
  if NOT(KEYWORD_SET(SILENT)) then begin
    print, ' No ENERGY selection'
  end
  printf, out_unit, ' No ENERGY selection'
end

; For HRC, make a nominal selection on PHA
if (STRPOS(DETECTOR,'HRC') GE 0) AND (TOTAL(evts_tags EQ 'PHA') GE 1) then begin
  keep = where( evts.PHA GT min_sel_pha AND $
		evts.PHA LT max_sel_pha, nfound)
  if nfound GT 0 then begin
    if NOT(KEYWORD_SET(SILENT)) then begin
      print, ' Keeping HRC PHA selected events, '+ $
		STRCOMPRESS((100.0*nfound)/nevts)+' %'
      print, '  (from '+STRCOMPRESS(min_sel_pha)+$
		' to '+STRCOMPRESS(max_sel_pha)+' )'
    end
    printf, out_unit, ' Keeping HRC PHA selected events, '+ $
		STRCOMPRESS((100.0*nfound)/nevts)+' %'
    printf, out_unit, '  (from '+STRCOMPRESS(min_sel_pha)+$
		' to '+STRCOMPRESS(max_sel_pha)+' )'
    evts = evts(keep)
    ftime = ftime(keep)
    Etouse = Etouse(keep)
    Xtouse = Xtouse(keep)
    Ytouse = Ytouse(keep)
    nevts = n_elements(evts)
  end else begin
    if NOT(KEYWORD_SET(SILENT)) then begin
      print, ' No HRC PHAs in range(?), keep them all.'
    end
    printf, out_unit, ' No HRC PHAs in range(?), keep them all.'
  end
end else begin
  if (STRPOS(DETECTOR,'HRC') GE 0) then begin
    if NOT(KEYWORD_SET(SILENT)) then begin
      print, ' HRC PHA selection not performed'
    end
    printf, out_unit, ' HRC PHA selection not performed'
  end
end

if NOT(KEYWORD_SET(SILENT)) then print, ''
printf, out_unit, ''

; All done selecting, make new energy_color array:
; ENERGY or PHA available?
if (got_energy) OR $
	(TOTAL(evts_tags EQ 'PHA') GE 1) then begin
  ; Prefer to use energy if it is present
  if got_energy then begin
    ; Log energy color coding...
    ; energy_colors = 3+FIX(252.* $
    ;	(ALOG(Etouse) - ALOG(min_clr_energy))/ $
    ;		(ALOG(max_clr_energy) - ALOG((min_clr_energy > 0.06))) )
    ; Prefer..
    ; Linear coding...
    energy_colors = 3+ ( FIX( (251.* $
	(Etouse - min_clr_energy)/ $
		(max_clr_energy - min_clr_energy) ) < 251.) > 0)
  end else begin
    ; PHA available...
    energy_colors = 3+ ( FIX( (251.* $
	(evts.PHA - min_clr_pha)/ $
		(max_clr_pha - min_clr_pha) ) < 251.) > 0)
  end
  if color24bit AND KEYWORD_SET(SCREEN24) then begin
    ; convert the colors to 24 bit...
    energy_colors = color24_values(energy_colors)
  end
end else begin
  ; No ENERGY or PHA to provide color coding...
  energy_colors = clr_grn
end

if GRATING EQ 'NONE' AND STRPOS(DETECTOR, '-I') GE 0 then begin
  !p.multi = [0,1,2]
  triplot_charsize = 1.0
end else begin
  !p.multi = [0,1,3]
  triplot_charsize = 1.81
end

plot, Xtouse, Ytouse, PSYM=3, $
	XSTYLE=1, YSTYLE=1, $
	BACK=clr_back, COLOR=clr_wht, /NODATA, $
        TITLE='X-Y Plot of Selected Events', $
        XTITLE=x_name+' (pixels)', $
        YTITLE=y_name+' (pixels)', $
	CHARSIZE=triplot_charsize
plots, Xtouse, Ytouse, PSYM=3, COLOR=energy_colors, NOCLIP=0

if GRATING EQ 'NONE' AND STRPOS(DETECTOR, '-I') GE 0 then begin
  ; setup for rest of plots on page
  !p.multi = [2,1,4]
  triplot_charsize = 1.81
end

if got_energy then begin
  plot_io, Xtouse, Etouse, PSYM=3, $
	XSTYLE=1, YSTYLE=1, YRANGE=[min_sel_energy,max_sel_energy], $
	BACK=clr_back, COLOR=clr_wht, /NODATA, $
        TITLE='X-E Plot of Selected Events', $
        XTITLE=x_name+' (pixels)', $
        YTITLE='Detector Energy ('+energy_unit+')', $
	CHARSIZE=triplot_charsize
  plots, Xtouse, Etouse, PSYM=3, COLOR=energy_colors, NOCLIP=0
  lin_hist, Etouse, e_bin_ratio, bines, bincounts
  plot_oo, bines, bincounts, PSYM=10, $
	XRANGE=[min_sel_energy,max_sel_energy], XSTYLE=1, $
	YRANGE=[(0.5*MIN(bincounts)) > 0.5, 2.0*MAX(bincounts)], YSTYLE=1, $
	BACK=clr_back, COLOR=clr_wht, $
        TITLE='Detector Pulse Height Distribution of Selected Events', $
        XTITLE='Detector Energy ('+energy_unit+')', $
        YTITLE='Counts/bin', $
	CHARSIZE=triplot_charsize
  if NOT(KEYWORD_SET(SILENT)) then begin
    print, 'Linear  binning from '+STRCOMPRESS(min_sel_energy)+ $
		' to '+STRCOMPRESS(max_sel_energy)+' keV'
    print, ' dE of one bin width = '+STRCOMPRESS(e_bin_ratio)+' keV'
    print, ''
  end
  printf, out_unit, 'Linear  binning from '+STRCOMPRESS(min_sel_energy)+ $
		' to '+STRCOMPRESS(max_sel_energy)+' keV'
  printf, out_unit, ' dE of one bin width = '+STRCOMPRESS(e_bin_ratio)+' keV'
  printf, out_unit, ''
end else begin
  ; PHA plots if available and ENERGY isn't
  if (TOTAL(evts_tags EQ 'PHA')) GE 1 then begin
    plot, Xtouse, evts.PHA, PSYM=3, $
	XSTYLE=1, YRANGE=[0.,MAX(evts.PHA)], YSTYLE=1, $
	BACK=clr_back, COLOR=clr_wht, /NODATA, $
        TITLE='X-PHA Plot of Selected Events', $
        XTITLE=x_name+' (pixels)', $
        YTITLE='Detector PHA', $
	CHARSIZE=triplot_charsize
    plots, Xtouse, evts.PHA, $
	PSYM=3, COLOR=energy_colors, NOCLIP=0
    lin_hist, evts.PHA, 1.0, bines, bincounts
    plot, bines, bincounts, PSYM=10, $
	XSTYLE=1, XRANGE=[0.,MAX(evts.PHA)], $
	YSTYLE=1, $
	BACK=clr_back, COLOR=clr_wht, $
        TITLE='Detector Pulse Height Distribution of Selected Events', $
        XTITLE='Detector PHA', $
        YTITLE='Counts/bin', $
	CHARSIZE=triplot_charsize
  end
end


; Finish the .gif output
if NOT(KEYWORD_SET(ZBUFFER)) then wshow,iwind,iconic=0
image = tvrd()
tvlct, red, green, blue, /GET
gif_out = output_prefix+'_'+proc_method+'_showselect.gif'
write_gif, out_dir+'/'+gif_out, image, red, green, blue

; Add .gif link
printf, out_unit, "</PRE>"
printf, out_unit, "<UL>"
printf, out_unit, '<LI><B><A href="'+gif_out+'">'+'Plots of Selected Events'+'</A></B>'
printf, out_unit, "</UL>"
printf, out_unit, "<PRE>"

if KEYWORD_SET(MOUSE) then begin
  print, '    !!! Click Mouse anywhere to Continue !!!'
  print, ''
  cursor, x, y, 3
end

; - - - - - end of event selection - - - -

; .......................................
;    - Data and Parameters available at this stage:
; filename, output_prefix, theKEYWORDS, out_unit, iwind, clr_*, color24_values
; evts, evts_tags, energy_unit, interval_duration, ftime, time_unit
; cc_mode, pixel_size, Xtouse, x_name, Ytouse, y_name, proc_method
; ft_frac_min, ft_frac_max, max_sel_energy, min_sel_energy, e_bin_ratio, 
;   min_clr_energy, max_clr_energy, min_clr_pha, max_clr_pah, energy_colors
; .......................................


; - - - - - - - - - - ACIS EXPNO Analysis - - - - - - - - - - -
; Only do this if ACIS is the detector and EXPNO tag is available
if (STRPOS(DETECTOR,'ACIS') GE 0)  AND $
	(TOTAL(evts_tags EQ 'EXPNO') GE 1) then begin
; .....
  ; Parameters:
  ;  none
  printf, out_unit, "</PRE>"
  printf, out_unit, '<HR>'
  printf, out_unit, '<H3>ACIS EXPNO Analysis...</H3>'
  printf, out_unit, "<PRE>"
  printf, out_unit, ""

  ; Find min, max, and number of expnos for pileup plot later:
  expno = evts.expno
  expno_min_all = MIN(expno)  
  expno_max_all = MAX(expno)  
  expno_num_all = FLOAT(n_elements(uniq(expno,SORT(expno))))

  printf, out_unit, ' Min, Max, Unique EXPNOs: '+STRING(expno_min_all)+', '+ $
		STRING(expno_max_all)+', '+ $
		STRING(expno_num_all)
  printf, out_unit, ''

  if NOT(KEYWORD_SET(SILENT)) then begin
    print, ' - - - - - - - - - - - - ACIS EXPNO Analysis... - - - - - - - - - '
    print, ''
    print, ' Min, Max, Unique EXPNOs: '+STRING(expno_min_all)+', '+ $
		STRING(expno_max_all)+', '+ $
		STRING(expno_num_all)
    print, ''
    print, '       Exposures and Events per Chip (w/selections)'
    print, ''
    print, '           MIN(EXPNO)  MAX(EXPNO)   TotalEvents   TotalExps  ' + $
	' PoissExps *      Ratio'
    print, ''
  end

  printf, out_unit, '       Exposures and Events per Chip (w/selections)'
  printf, out_unit, ''
  printf, out_unit, '           MIN(EXPNO)  MAX(EXPNO)   TotalEvents   TotalExps  ' + $
	' PoissExps *      Ratio'
  printf, out_unit, ''

  ; Make Baganoff expno plots
  !p.multi=[0,2,6]
  hexplot_charsize = 1.50

  ; go through the CCDs...
  for iccd=0,9 do begin
    strccdno = STRING(iccd,FORMAT='(I1)')
    sN = where(evts.ccd_id EQ iccd, nfound)
    if nfound GT 0 then begin
      expno = evts(sN).expno
      uexp = expno(uniq(expno,SORT(expno)))
      ; event rate over all frames
      evts_per_frame = FLOAT(nfound)/FLOAT(MAX(uexp)-MIN(uexp))
      ; poisson distribution for this rate (just 0 rate)
      poiss_dist = poiss_f(evts_per_frame, 0)
      expected_frames = (1.0 - poiss_dist(0))*FLOAT(MAX(uexp)-MIN(uexp))
      expno_ratio = FLOAT(n_elements(uexp))/expected_frames
      if NOT(KEYWORD_SET(SILENT)) then begin
        print, ' CCD '+strccdno+ $
		' : ',MIN(uexp), MAX(uexp), nfound, n_elements(uexp), $
	expected_frames, expno_ratio
    end
      printf, out_unit, ' CCD '+strccdno+ $
		' : '+STRING(MIN(uexp)) + STRING(MAX(uexp)) + $
		STRING(nfound) + STRING(n_elements(uexp)) + $
		STRING(expected_frames) + STRING(expno_ratio)
      ; save ratio of frames to the output .rdb file
      rpf_add_param, rpf, 'expnos_ratio_'+strccdno, expno_ratio

      lin_hist, uexp, 10.0, bins, counts
      plot, bins, counts, PSYM=4, YRANGE=[-1.0,11.0],YSTYLE=1, $
	TITLE='CCD '+STRING(iccd,FORMAT='(I1)') + $
		', ratio = '+STRING(expno_ratio), $
	BACK=clr_back, COLOR=clr_wht, $
	XTITLE='EXPNO value', YTITLE='N-out-of-10', $
	CHARSIZE=hexplot_charsize

      lin_hist, expno, 10.0, evtbins, evtcounts
      plot, evtbins, evtcounts, PSYM=4, $
	TITLE='CCD '+STRING(iccd,FORMAT='(I1)') + $
		', Ave event rate = '+ $
		STRING(Float(nfound)/n_elements(uexp), FORMAT='(F8.3)') + $
		' / frame', $
	BACK=clr_back, COLOR=clr_wht, $
	XTITLE='EXPNO value', YTITLE='Events-per-10-EXPNOs', $
	CHARSIZE=hexplot_charsize

    end else begin
      if NOT(KEYWORD_SET(SILENT)) then begin
        print, ' CCD '+STRING(iccd,FORMAT='(I1)')+ ' : '
      end
      printf, out_unit, ' CCD '+STRING(iccd,FORMAT='(I1)')+ ' : '
      rpf_add_param, rpf, 'expnos_ratio_'+strccdno, 0
    end
  end

  if NOT(KEYWORD_SET(SILENT)) then begin
    print, ''
    print, '    * Expected number of exposures with one or more'
    print, '      detected events, assuming no telemetry-limit-dropped'
    print, '      exposures for this CCD.'
    print, ''
  end
  printf, out_unit, ''
  printf, out_unit, '    * Expected number of exposures with one or more'
  printf, out_unit, '      detected events, assuming no telemetry-limit-dropped'
  printf, out_unit, '      exposures for this CCD.'
  printf, out_unit, ''

  ; Finish the .gif output
  if NOT(KEYWORD_SET(ZBUFFER)) then wshow,iwind,iconic=0
  image = tvrd()
  tvlct, red, green, blue, /GET
  gif_out = output_prefix+'_'+proc_method+'_expnos.gif'
  write_gif, out_dir+'/'+gif_out, image, red, green, blue

  ; Add .gif link
  printf, out_unit, "</PRE>"
  printf, out_unit, "<UL>"
  printf, out_unit, '<LI><B><A href="'+gif_out+'">'+ $
	'ACIS EXPNOS Plots'+'</A></B>'
  printf, out_unit, "</UL>"
  printf, out_unit, "<PRE>"

  if KEYWORD_SET(MOUSE) then begin
    print, '    !!! Click Mouse anywhere to Continue !!!'
    print, ''
    cursor, x, y, 3
  end
;.....
end ; of if ACIS do this
; - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

; - - - - - - - - - - Timing Analysis - - - - - - - - - - -
; Parameters:
tbinsize = 0.1  ; seconds
tgapsize = 15.0 ; seconds
printf, out_unit, "</PRE>"
printf, out_unit, '<HR>'
printf, out_unit, '<H3>Timing Analysis...</H3>'
printf, out_unit, "<PRE>"
printf, out_unit, ""

if NOT(KEYWORD_SET(SILENT)) then begin
  print, ' - - - - - - - - - - - - Timing Analysis... - - - - - - - - - '
  print, ''
  print, ' Total Events = '+STRCOMPRESS(n_elements(evts))
  print, ' Start time = '+STRCOMPRESS(abs_start_time)+' '+time_unit+'s'
  print, ' Interval duration = '+STRCOMPRESS(interval_duration)+' '+time_unit+'s'
  print, ' Ave Event Rate = '+STRCOMPRESS(FLOAT(n_elements(evts))/ $
			interval_duration)+' events/'+time_unit
  print, ''
end

printf, out_unit, ' Selected Events = '+STRCOMPRESS(n_elements(evts))
printf, out_unit, ' Start time = '+STRCOMPRESS(abs_start_time)+' '+time_unit+'s'
printf, out_unit, ' Interval duration = '+STRCOMPRESS(interval_duration)+' '+time_unit+'s'
printf, out_unit, ' Ave Event Rate = '+STRCOMPRESS(FLOAT(n_elements(evts))/ $
			interval_duration)+' events/'+time_unit
printf, out_unit, ''

; Create the time-between-events...
; The events do not need to be in time-sorted order
; so sort them for this
tsort = SORT(ftime)
sftime = ftime(tsort)
delta_ts = sftime(1:*)-sftime(0:n_elements(ftime)-2)

; Find, report and "clip" any large gaps...
large_gaps = where(delta_ts GT tgapsize, nfound)
tot_gap_time = 0.0
if nfound GT 0 then begin
  tot_gap_time = TOTAL(delta_ts(large_gaps))
  live_interval = interval_duration-tot_gap_time

  if NOT(KEYWORD_SET(SILENT)) then begin
    print, '* Found '+STRCOMPRESS(nfound)+' big ( > '+STRCOMPRESS(tgapsize)+ $
		' s) gaps, totalling '+ $
		STRCOMPRESS(tot_gap_time)+' '+time_unit+'s'
    print, ''
    print, ' Live Interval = '+STRCOMPRESS(live_interval)+ $
		' '+time_unit+'s'
    print, ' Revised Event Rate = '+STRCOMPRESS(FLOAT(n_elements(evts))/ $
			(live_interval) )+' events/'+time_unit
  end

  printf, out_unit, '* Found '+STRCOMPRESS(nfound)+' big ( > '+STRCOMPRESS(tgapsize)+ $
		' s) gaps, totalling '+ $
		STRCOMPRESS(tot_gap_time)+' '+time_unit+'s'
  printf, out_unit, ''
  printf, out_unit, ' Live Interval = '+STRCOMPRESS(live_interval)+ $
		' '+time_unit+'s'
  printf, out_unit, ' Revised Event Rate = '+STRCOMPRESS(FLOAT(n_elements(evts))/ $
			(live_interval) )+' events/'+time_unit

  ; "Clip" the large gaps for this plotting purpose
  delta_ts(large_gaps) = tgapsize
end else begin
  if NOT(KEYWORD_SET(SILENT)) then begin
    print, ' Found no big ( > '+STRCOMPRESS(tgapsize)+ $
		' s) gaps in event data.'
  end
  printf, out_unit, ' Found no big ( > '+STRCOMPRESS(tgapsize)+ $
		' s) gaps in event data.'
end

; save these to the output .rdb file
rpf_add_param, rpf, 'live_interval', live_interval, $
	UNIT = time_unit
rpf_add_param, rpf, 'live_event_rate', FLOAT(n_elements(evts)) / $
	live_interval, ERROR = SQRT(FLOAT(n_elements(evts))) / $
	live_interval, UNIT = 'event/'+time_unit

  if NOT(KEYWORD_SET(SILENT)) then print, ''
printf, out_unit, ''

; Make some timing plots
!p.multi=[0,1,4]
quadplot_charsize = 1.81

; PLOT Xtouse vs ftime
plot, ftime, Xtouse, PSYM=3, $
	XSTYLE=1, YSTYLE=1, $
	BACK=clr_back, COLOR=clr_wht, /NODATA, $
        TITLE='t-X Plot of Selected Events', $
        XTITLE='Time ('+time_unit+'s)', $
        YTITLE=x_name+' (pixels)', $
	CHARSIZE=quadplot_charsize
plots, ftime, Xtouse, PSYM=3, COLOR=energy_colors, NOCLIP=0

; PLOT Ytouse vs ftime (for ACIS-S can see dropped chips...)
plot, ftime, Ytouse, PSYM=3, $
	XSTYLE=1, YSTYLE=1, $
	BACK=clr_back, COLOR=clr_wht, /NODATA, $
        TITLE='t-Y Plot of Selected Events', $
        XTITLE='Time ('+time_unit+'s)', $
        YTITLE=y_name+' (pixels)', $
	CHARSIZE=quadplot_charsize
plots, ftime, Ytouse, PSYM=3, COLOR=energy_colors, NOCLIP=0

if got_energy then begin
  ; PLOT ENERGY vs ftime
  plot_io, ftime, Etouse, PSYM=3, $
	XSTYLE=1, YSTYLE=1, YRANGE=[min_sel_energy,max_sel_energy], $
	BACK=clr_back, COLOR=clr_wht, /NODATA, $
        TITLE='t-E Plot of Selected Events', $
        XTITLE='Time ('+time_unit+'s)', $
        YTITLE='Detector Energy ('+energy_unit+')', $
	CHARSIZE=quadplot_charsize
  plots, ftime, Etouse, PSYM=3, COLOR=energy_colors, NOCLIP=0
end else begin
  if TOTAL(evts_tags EQ 'PHA') GE 1 then begin
    plot, ftime, evts.PHA, PSYM=3, $
	XSTYLE=1, YRANGE=[0.,MAX(evts.PHA)], YSTYLE=1, $
	BACK=clr_back, COLOR=clr_wht, /NODATA, $
        TITLE='t-PHA Plot of Selected Events', $
        XTITLE='Time ('+time_unit+'s)', $
        YTITLE='Detector PHA ', $
	CHARSIZE=quadplot_charsize
    plots, ftime, evts.PHA, PSYM=3, COLOR=energy_colors, NOCLIP=0
  end
end

; PLOT the event-to-event time distribution
lin_hist, delta_ts, tbinsize, tbins, tcounts
plot_io, tbins, tcounts, PSYM=10, YRANGE=[0.5,2.0*MAX(tcounts)],YSTYLE=1, $
	TITLE='Arrival Time Distribution of Selected Events', $
	XTITLE= 't_N+1 - t_N ('+time_unit+'s)', $
	YTITLE= 'Number of occurances', CHARSIZE=quadplot_charsize
oplot, tbins, tcounts, PSYM=4

; Finish the .gif output
if NOT(KEYWORD_SET(ZBUFFER)) then wshow,iwind,iconic=0
image = tvrd()
tvlct, red, green, blue, /GET
gif_out = output_prefix+'_'+proc_method+'_timing.gif'
write_gif, out_dir+'/'+gif_out, image, red, green, blue

; Add .gif link
printf, out_unit, "</PRE>"
printf, out_unit, "<UL>"
printf, out_unit, '<LI><B><A href="'+gif_out+'">'+'Timing Plots'+'</A></B>'
printf, out_unit, "</UL>"
printf, out_unit, "<PRE>"

if KEYWORD_SET(MOUSE) then begin
  print, '    !!! Click Mouse anywhere to Continue !!!'
  print, ''
  cursor, x, y, 3
end
; - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

; .......................................
; Data and Parameters available at this stage:
;  filename, grating, evts, evts_tags, 
;  max_sel_energy, min_sel_energy, e_bin_ratio, 
;  ftime, tsort, delta_ts, tbinsize, tgapsize, interval_duration
; .......................................

; - - - - - - - - Zero-order Determination - - - - - - - - - - - 
; Find time-average location of zero-order in the selected coords
; Use all events...
; Parameters:
;  See max_zo_energy, min_zo_energy above.
;  Zero-order region of 250 pixels
;    = +/- 3 mm, i.e. from S2-S3 gap to nominal aim point
;    = +/- 1 arc min, less than dither pattern...
zoregsize = 6.0 / pixel_size

if NOT(KEYWORD_SET(SILENT)) then begin
  print, ' - - - - - - - - - - - - Determine Zero-order... - - - - - - -'
  print, ''
end
printf, out_unit, "</PRE>"
printf, out_unit, '<HR>'
printf, out_unit, '<H3>Determine Zero-order...</H3>'
printf, out_unit, "<PRE>"
printf, out_unit, ""


!p.multi = [0,1,2]

; Select by energy if available
if got_energy then begin
  sel = where(Etouse GT min_zo_energy AND Etouse LT max_zo_energy)
  efmt = '(F5.2)'
  if NOT(KEYWORD_SET(SILENT)) then begin
    print, ' Zero-order search uses energies: '+ $
	STRING(min_zo_energy,FORMAT=efmt)+ $
	' to '+STRING(max_zo_energy,FORMAT=efmt)+' keV.'
    print, ''
  end
  printf, out_unit, ' Zero-order search uses energies: '+ $
	STRING(min_zo_energy,FORMAT=efmt)+ $
	' to '+STRING(max_zo_energy,FORMAT=efmt)+' keV.'
  printf, out_unit, ''
end else begin
  sel = lindgen(n_elements(evts))
end

; Plot the events ...
plot, Xtouse(sel), Ytouse(sel), PSYM=3, $
	XSTYLE=1, YSTYLE=1, $
	BACK=clr_back, COLOR=clr_wht, /NODATA, $
        TITLE='X-Y Plot of Selected Events', $
        XTITLE=x_name+' (pixels)', $
        YTITLE=y_name+' (pixels)', $
	CHARSIZE=1.11
plots, Xtouse(sel), Ytouse(sel), PSYM=3, COLOR=energy_colors(sel), NOCLIP=0

; Compute the Average Xtouse and Ytouse
nevts = n_elements(evts(sel))
aveXtouse = TOTAL(Xtouse(sel))/FLOAT(nevts)
aveYtouse = TOTAL(Ytouse(sel))/FLOAT(nevts)
if NOT(KEYWORD_SET(SILENT)) then begin
print, ' Average '+x_name+','+y_name+' gives x,y = ' + $
	STRCOMPRESS(aveXtouse)+', '+STRCOMPRESS(aveYtouse)
end
printf, out_unit, ' Average '+x_name+','+y_name+' gives x,y = ' + $
	STRCOMPRESS(aveXtouse)+', '+STRCOMPRESS(aveYtouse)

; Show the current Zero-order location
; and have operator improve the guess...
oplot, [aveXtouse], [aveYtouse], PSYM=6
if KEYWORD_SET(MOUSE) OR KEYWORD_SET(OVERRIDE_ZERO) then begin
  ; this is the first time the operator is needed to think about
  ; the click, so give 'em a beep !
  xgef_beep
  xyouts, aveXtouse, aveYtouse, '  Click Near Zero-order'
  print, ''
  print, '    !!! Click Mouse ON ZERO-ORDER to Continue !!!'
  print, ''
  cursor, x, y, 3
  print, ' Mouse clicked at x,y = '+STRCOMPRESS(x)+', '+STRCOMPRESS(y)
  printf, out_unit, ' Mouse clicked at x,y = '+STRCOMPRESS(x)+', '+STRCOMPRESS(y)
  oplot, [x],[y],PSYM=2
  aveXtouse = x
  aveYtouse = y
end

; Zoom-in on a square region around this location
; at six-times the desired zero-order region size
!p.multi=[2,2,2]

; Improve the average by using only these events and iterating...
if got_energy then begin
  sel = where( ABS(Xtouse-aveXtouse) LT 0.5*6.0*zoregsize AND $
		ABS(Ytouse-aveYtouse) LT 0.5*6.0*zoregsize AND $
		(Etouse GT min_zo_energy AND Etouse LT max_zo_energy) )
end else begin
  sel = where( ABS(Xtouse-aveXtouse) LT 0.5*6.0*zoregsize AND $
		ABS(Ytouse-aveYtouse) LT 0.5*6.0*zoregsize )
end

plot, Xtouse(sel), Ytouse(sel), PSYM=3, $
	XRANGE=aveXtouse+ 6.*zoregsize*[-0.5,0.5], XSTYLE=1, $
	YRANGE=aveYtouse+ 6.*zoregsize*[-0.5,0.5], YSTYLE=1, $
	BACK=clr_back, COLOR=clr_wht, /NODATA, $
        TITLE='Zero-order Region (x6)', $
        XTITLE=x_name+' (pixels)', $
        YTITLE=y_name+' (pixels)', $
	CHARSIZE=1.11
plots, Xtouse(sel), Ytouse(sel), PSYM=3, COLOR=energy_colors(sel), NOCLIP=0

aveXtouse = TOTAL(Xtouse(sel))/FLOAT(n_elements(sel))
aveYtouse = TOTAL(Ytouse(sel))/FLOAT(n_elements(sel))
if NOT(KEYWORD_SET(SILENT)) then begin
  print, ' Average '+x_name+','+y_name+' gives x,y = ' + $
	STRCOMPRESS(aveXtouse)+', '+STRCOMPRESS(aveYtouse)
end
printf, out_unit, ' Average '+x_name+','+y_name+' gives x,y = ' + $
	STRCOMPRESS(aveXtouse)+', '+STRCOMPRESS(aveYtouse)

; Have operator improve the guess...
oplot, [aveXtouse], [aveYtouse], PSYM=6
if KEYWORD_SET(MOUSE) OR KEYWORD_SET(OVERRIDE_ZERO) then begin
  xyouts, aveXtouse, aveYtouse, '  Click Near Zero-order'
  print, ''
  print, '    !!! Click Mouse ON ZERO-ORDER to Continue !!!'
  print, ''
  cursor, x, y, 3
  print, ' Mouse clicked at x,y = '+STRCOMPRESS(x)+', '+STRCOMPRESS(y)
  printf, out_unit, ' Mouse clicked at x,y = '+STRCOMPRESS(x)+', '+STRCOMPRESS(y)
  oplot, [x],[y],PSYM=2
  aveXtouse = x
  aveYtouse = y
end

; Next-to-final zero-order computation at 2X region size
if got_energy then begin
  sel = where( ABS(Xtouse-aveXtouse) LT zoregsize AND $
		ABS(Ytouse-aveYtouse) LT zoregsize AND $
		(Etouse GT min_zo_energy AND Etouse LT max_zo_energy) )
end else begin
  sel = where( ABS(Xtouse-aveXtouse) LT zoregsize AND $
		ABS(Ytouse-aveYtouse) LT zoregsize )
end
aveXtouse = TOTAL(Xtouse(sel))/FLOAT(n_elements(sel))
aveYtouse = TOTAL(Ytouse(sel))/FLOAT(n_elements(sel))

; and show the events and zero-order approx location
plot, Xtouse(sel), Ytouse(sel), PSYM=3, $
	XRANGE=aveXtouse+ 2.0*zoregsize*[-0.5,0.5], XSTYLE=1, $
	YRANGE=aveYtouse+ 2.0*zoregsize*[-0.5,0.5], YSTYLE=1, $
	BACK=clr_back, COLOR=clr_wht, /NODATA, $
        TITLE='Zero-order Region (x2)', $
        XTITLE=x_name+' (pixels)', $
        YTITLE=y_name+' (pixels)', $
	CHARSIZE=1.11
plots, Xtouse(sel), Ytouse(sel), PSYM=3, COLOR=energy_colors(sel), $
	NOCLIP=0

if NOT(KEYWORD_SET(SILENT)) then begin
  print, ' Average '+x_name+','+y_name+' gives x,y = ' + $
	STRCOMPRESS(aveXtouse)+', '+STRCOMPRESS(aveYtouse)
  print, ''
end
printf, out_unit, ' Average '+x_name+','+y_name+' gives x,y = ' + $
	STRCOMPRESS(aveXtouse)+', '+STRCOMPRESS(aveYtouse)
printf, out_unit, ''

; Final selection and Calculation of the Zero-order region
if got_energy then begin
  zosel = where( ABS(Xtouse-aveXtouse) LT 0.5*zoregsize AND $
		ABS(Ytouse-aveYtouse) LT 0.5*zoregsize AND $
		(Etouse GT min_zo_energy AND Etouse LT max_zo_energy) ,nfound)
end else begin
  zosel = where( ABS(Xtouse-aveXtouse) LT 0.5*zoregsize AND $
		ABS(Ytouse-aveYtouse) LT 0.5*zoregsize, nfound)
end
; Instead of average...
;aveXtouse = TOTAL(Xtouse(zosel))/FLOAT(n_elements(zosel))
;aveYtouse = TOTAL(Ytouse(zosel))/FLOAT(n_elements(zosel))
; try the median...
;sxzo = zosel(SORT(Xtouse(zosel)))
;aveXtouse = Xtouse(sxzo(n_elements(sxzo)/2))
;syzo = zosel(SORT(Ytouse(zosel)))
;aveYtouse = Ytouse(syzo(n_elements(syzo)/2))
;
; and finally use an average of the median (m_medave-2)/m_medave of events,
; e.g., m_medave = 4  --> average 1/4 to 3/4 = 50% of events
;       m_medave = 20 --> average 1/20 to 19/20 = 90% of events
m_medave = 20   ; average 90% of events, cuts out 5% on each side
selsort = zosel(SORT(Xtouse(zosel)))
selmed = selsort( (nfound/m_medave) : (((m_medave-1)*nfound)/m_medave) )
aveXtouse = TOTAL(Xtouse(selmed))/FLOAT(n_elements(selmed))
selsort = zosel(SORT(Ytouse(zosel)))
selmed = selsort( (nfound/m_medave) : (((m_medave-1)*nfound)/m_medave) )
aveYtouse = TOTAL(Ytouse(selmed))/FLOAT(n_elements(selmed))

; Now select all the zero-order events in the region 
; if the energy has been selected on up until now (to reduce background)
if got_energy then begin
  zosel = where( ABS(Xtouse-aveXtouse) LT 0.5*zoregsize AND $
		ABS(Ytouse-aveYtouse) LT 0.5*zoregsize, nfound)
end

; plot cross-hairs at this location
oplot, zoregsize*[-0.5,0.5]+aveXtouse, [1.,1.]+aveYtouse
oplot, [1.,1.]+aveXtouse, zoregsize*[-0.5,0.5]+aveYtouse

; Not so fast!  User wants the last word...
if KEYWORD_SET(OVERRIDE_ZERO) then begin
  xyouts, aveXtouse, aveYtouse, '  *** Click on THE Zero-order ***'
  print, ''
  print, '    !!! *** Click Mouse on THE ZERO-ORDER to Continue !!!'
  print, ''
  cursor, x, y, 3
  print, ' Mouse clicked at x,y = '+STRCOMPRESS(x)+', '+STRCOMPRESS(y)
  printf, out_unit, ' Mouse clicked at x,y = '+STRCOMPRESS(x)+', '+STRCOMPRESS(y)
  oplot, [x],[y],PSYM=2
  aveXtouse = x
  aveYtouse = y
  ; and define the zero-order region w.r.t. these
  zosel = where( ABS(Xtouse-aveXtouse) LT 0.5*zoregsize AND $
		ABS(Ytouse-aveYtouse) LT 0.5*zoregsize  )
end

if NOT(KEYWORD_SET(SILENT)) then begin
  print, '                    ==> MTA Monitor Task 5.2 <=='
  print, ''
  print, ' Zero-order Location '+x_name+','+y_name+' ave-median = '+ $
	STRCOMPRESS(aveXtouse)+', '+STRCOMPRESS(aveYtouse)
  print, ''
end

printf, out_unit, '</PRE>'
printf, out_unit, '<P align="center"><FONT COLOR="#00D000" SIZE=+1>'
printf, out_unit, ' ==> MTA Monitor Task 5.2 <== '
printf, out_unit, '</FONT></P>'
printf, out_unit, '<PRE>'

printf, out_unit, ' Zero-order Location '+x_name+','+y_name+' ave-median = '+ $
	STRCOMPRESS(aveXtouse)+', '+STRCOMPRESS(aveYtouse)
printf, out_unit, ''

; Output zero-order events and rate
rpf_add_param, rpf, 'zo_det_events', n_elements(zosel), $
	ERROR = 0.0, UNIT=''
rpf_add_param, rpf, 'zo_live_rate', FLOAT(n_elements(zosel)) / $
	live_interval, ERROR = SQRT(FLOAT(n_elements(zosel))) / $
	live_interval, UNIT = 'event/'+time_unit

; Output the names of the coordinates
rpf_add_param, rpf, 'x_coord_name', x_name
rpf_add_param, rpf, 'y_coord_name', y_name

; Output the zero-order location to the parameter file
rpf_add_param, rpf, 'zo_loc_x', aveXtouse, $
	ERROR = 0.0, UNIT='pixel'
rpf_add_param, rpf, 'zo_loc_y', aveYtouse, $
	ERROR = 0.0, UNIT='pixel'

; Finish the .gif output
if NOT(KEYWORD_SET(ZBUFFER)) then wshow,iwind,iconic=0
image = tvrd()
tvlct, red, green, blue, /GET
gif_out = output_prefix+'_'+proc_method+'_zerofind.gif'
write_gif, out_dir+'/'+gif_out, image, red, green, blue

; Add .gif link
printf, out_unit, "</PRE>"
printf, out_unit, "<UL>"
printf, out_unit, '<LI><B><A href="'+gif_out+'">'+ $
	'Finding Zero-order Plots'+'</A></B>'
printf, out_unit, "</UL>"
printf, out_unit, "<PRE>"

if KEYWORD_SET(MOUSE) then begin
  print, '    !!! Click Mouse anywhere to Continue !!!'
  print, ''
  cursor, x, y, 3
end

; Show close-up of the region...
!p.multi=[0,2,2]


printf, out_unit, ' Events in Zero-order Region = '+ $
	STRCOMPRESS(n_elements(zosel))
printf, out_unit, ' Ave. Event Rate in Zero-order Region = '+ $
	STRCOMPRESS(n_elements(zosel)/interval_duration)+ $
	' events/'+time_unit+'s'
printf, out_unit, ''

if NOT(KEYWORD_SET(SILENT)) then begin
  print, ' Events in Zero-order Region = '+ $
	STRCOMPRESS(n_elements(zosel))
  print, ' Event Rate in Zero-order Region = '+ $
	STRCOMPRESS(n_elements(zosel)/interval_duration)+ $
	' events/'+time_unit+'s'
  print, ''
end

; Plot the zero-order region
plot, Xtouse(zosel) - aveXtouse, $
	Ytouse(zosel) - aveYtouse, PSYM=3, $
	XRANGE= zoregsize*[-0.5,0.5], XSTYLE=1, $
	YRANGE= zoregsize*[-0.5,0.5], YSTYLE=1, $
	BACK=clr_back, COLOR=clr_wht, /NODATA, $
        TITLE='Zero-order Region', $
        XTITLE=x_name+' - '+STRING(aveXtouse,FORMAT='(F9.1)'), $
        YTITLE=y_name+' - '+STRING(aveYtouse,FORMAT='(F9.1)'), $
	CHARSIZE=1.09
plots, Xtouse(zosel) - aveXtouse, Ytouse(zosel) - aveYtouse, PSYM=3, $
	COLOR=energy_colors(zosel), NOCLIP=0

; plot cross-hairs at the z-o location
oplot, zoregsize*[-0.5,0.5], [1.,1.]
oplot, [1.,1.], zoregsize*[-0.5,0.5]
; Calculate the r-rms of these events
rs = SQRT((Xtouse(zosel)-aveXtouse)^2 + (Ytouse(zosel)-aveYtouse)^2)
rrms = SQRT(TOTAL(rs*rs)/FLOAT(n_elements(zosel)))

if NOT(KEYWORD_SET(SILENT)) then begin
  print, ' '+x_name+','+y_name+' RMS Radius = '+STRCOMPRESS(rrms)+' pixels'
end
printf, out_unit, ' '+x_name+','+y_name+' RMS Radius = '+ $
	STRCOMPRESS(rrms)+' pixels'

; Plot the Dispersion axis profile ~ LRF
lin_hist, Xtouse(zosel) - aveXtouse, 1.0, xbins, xcounts
plot, xbins, xcounts, PSYM=10, $
        TITLE='Zero-order '+x_name+' Profile (~ LRF)', $
        XTITLE=x_name+' - '+STRING(aveXtouse,FORMAT='(F9.1)'), $
        YTITLE='Counts/bin', $
	XRANGE= zoregsize*[-0.5,0.5], XSTYLE=1, $
	CHARSIZE=1.09
above10 = where(xcounts GE 0.10*MAX(xcounts), nabove10)
above50 = where(xcounts GE 0.50*MAX(xcounts), nabove50)

rpf_add_param, rpf, 'zo_det_fwtenthm', nabove10, $
	ERROR = 0.0, UNIT='pixel'
rpf_add_param, rpf, 'zo_det_fwhm', nabove50, $
	ERROR = 0.0, UNIT='pixel'

if NOT(KEYWORD_SET(SILENT)) then begin
  print, ' Number of '+x_name+' LRF pixels GT 10% of peak = '+ $
	STRCOMPRESS(nabove10)
  print, ' Number of '+x_name+' LRF pixels GT 50% of peak = '+ $
	STRCOMPRESS(nabove50)
end
printf, out_unit, ' Number of '+x_name+' LRF pixels GT 10% of peak = '+ $
	STRCOMPRESS(nabove10)
printf, out_unit, ' Number of '+x_name+' LRF pixels GT 50% of peak = '+ $
	STRCOMPRESS(nabove50)

; Plot the zero-order events vs time
plot, ftime(zosel), Xtouse(zosel) - aveXtouse, PSYM=3, $
	XSTYLE=1, YSTYLE=1, $
	BACK=clr_back, COLOR=clr_wht, /NODATA, $
        TITLE='t-X Plot for Zero-order Events', $
        XTITLE='Time ('+time_unit+'s)', $
        YTITLE=x_name+' - '+STRING(aveXtouse,FORMAT='(F9.1)'), $
	CHARSIZE=1.09
plots, ftime(zosel), Xtouse(zosel) - aveXtouse, PSYM=3, $
	COLOR=energy_colors(zosel), NOCLIP=0

plot, ftime(zosel), Ytouse(zosel) - aveYtouse, PSYM=3, $
	XSTYLE=1, YSTYLE=1, $
	BACK=clr_back, COLOR=clr_wht, /NODATA, $
        TITLE='t-Y Plot for Zero-order Events', $
        XTITLE='Time ('+time_unit+'s)', $
        YTITLE=y_name+' - '+STRING(aveYtouse,FORMAT='(F9.1)'), $
	CHARSIZE=1.09
plots, ftime(zosel), Ytouse(zosel) - aveYtouse, PSYM=3, $
	COLOR=energy_colors(zosel), NOCLIP=0

if NOT(KEYWORD_SET(SILENT)) then print, ''
printf, out_unit, ''

; Finish the .gif output
if NOT(KEYWORD_SET(ZBUFFER)) then wshow,iwind,iconic=0
image = tvrd()
tvlct, red, green, blue, /GET
gif_out = output_prefix+'_'+proc_method+'_zerospatial.gif'
write_gif, out_dir+'/'+gif_out, image, red, green, blue

; Add .gif link
printf, out_unit, "</PRE>"
printf, out_unit, "<UL>"
printf, out_unit, '<LI><B><A href="'+gif_out+'">'+'Zero-order Region Plots'+'</A></B>'
printf, out_unit, "</UL>"
printf, out_unit, "<PRE>"

if KEYWORD_SET(MOUSE) then begin
  print, '    !!! Click Mouse anywhere to Continue !!!'
  print, ''
  cursor, x, y, 3
end

; end of zero-order determine/examine
; - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

; .......................................
; Data and Parameters available at this stage:
;  filename, grating, evts, evts_tags, 
;  max_sel_energy, min_sel_energy, e_bin_ratio, 
;  ftime, tsort, delta_ts, tbinsize, tgapsize, interval_duration
;  zoregsize, zosel, aveXtouse, aveYtouse, xyshowtoo
; .......................................


; Aspect and Zero-order Examination Parameters:
; size of region to zoom in on for plots...
zo_exam_size = (6.0*0.050)/pixel_size  ; +/- 6 arc seconds
; number of sub-pixel bins to use
zo_exam_subbins = 10.0
; if there are too few streak counts the bins may be made fewer...
strk_exam_subbins = 5.0

; - - - - - - - - Aspect determination - - - - - -
; 
; Do some things that we'd do if no aspect is
; performed... this allows ASPECT to bail if
; counts-per-bin is too low...
;
; Define AX and AY in anycase, to be used in further analysis...
AX = Xtouse
AY = Ytouse
ax_name = x_name
ay_name = y_name
aveAX = aveXtouse
aveAY = aveYtouse

if KEYWORD_SET(ASPECT) then begin
  ; Parameters
  time_bin_size = 60.0  ; seconds
  aspect_min_rate = 3.0 ; events per bin time

  ; Have a 1/6th total time apodization region at beginning and end
  ; of the time series - thus 2/3 of the points will have valid solution
  apod_region_time = interval_duration/6.0  ; set to 0 for no apodization

  fft_thresh = 0.01 ; fraction of peak to include in smooth output

  low_f_defn = 0.33 ; define "low" frequencies as some fraction of
                    ; the Nyquist frequency
  toolow_f_defn = 0.03 ; define "too low" frequencies

  if NOT(KEYWORD_SET(SILENT)) then begin
    print, ' - - - - - - - - - - - - Creating Aspect Solution... - - - - - - '
    print, ''
  end
  printf, out_unit, "</PRE>"
  printf, out_unit, '<HR>'
  printf, out_unit, '<H3>Creating Aspect Solution...</H3>'
  printf, out_unit, "<PRE>"
  printf, out_unit, ""

  ; Create the average Xtouse and Ytouse values of events
  ; in each time bin...
  ; Could use Dave's reverse indices but do it brute force...
  ; Number of whole bins
  nbins = LONG( interval_duration/time_bin_size )
  binaveX = FLTARR(nbins)
  binaveY = binaveX
  binT = binaveX
  binApod = binaveX  ; array for apodization function
  binnave = INTARR(nbins)
  if NOT(KEYWORD_SET(SILENT)) then begin
    print, ' Aspect solution from '+x_name+','+y_name+' data...'
    print, ' Calculating '+x_name+','+y_name+' averages every '+ $
		STRCOMPRESS(time_bin_size)+' '+time_unit+'s.'
    print, ' Apodizing during the first and last '+ $
		STRCOMPRESS(apod_region_time)+' '+time_unit+'s of data.'
    print, ' Requires '+STRCOMPRESS(nbins)+' bins ...'
  end
  printf, out_unit, ' Aspect solution from '+x_name+','+y_name+' data...'
  printf, out_unit, ' Calculating '+x_name+','+y_name+' averages every '+ $
		STRCOMPRESS(time_bin_size)+' '+time_unit+'s.'
  printf, out_unit, ' Apodizing during the first and last '+ $
		STRCOMPRESS(apod_region_time)+' '+time_unit+'s of data.'
  printf, out_unit, ' Requires '+STRCOMPRESS(nbins)+' bins ...'

  ; ASPECT: GO or NO-GO ?
  ; Write out some aspect parameters and do some
  ; checking to make sure doing ASPECT is OK...
  ; if it is not OK (low counts per bin), then
  ; skip aspect correction...

  ; output aspect parameters of interest
  rpf_add_param, rpf, 'aspect_bin_time', time_bin_size, $
	UNIT = time_unit
  aspect_bin_rate = time_bin_size* FLOAT(n_elements(zosel))/interval_duration
  rpf_add_param, rpf, 'aspect_bin_rate', aspect_bin_rate, $
	UNIT = 'event/bin'
  if aspect_bin_rate LT aspect_min_rate then begin
    ; Let folks know what happened (silent or not!)
    printf, out_unit, "* aspect bin rate too low - skip aspect solution."
    print, "* aspect_bin_rate too low - skip aspect solution."
    GOTO, ASPECT_BAIL
  end

  ; Remove the average values from the Xtouse and Ytouse
  Xtouse = Xtouse - aveXtouse
  Ytouse = Ytouse - aveYtouse

  ; Go through the time bins and fill things in
  ; Use a plot to show how it's going!
  !p.multi = [0,1,5]
  plot, [0.,0.],[0., 100.0], PSYM=-3, $
	XRANGE=[0., 100.0], XSTYLE=1, $
	YRANGE=[-1.,1.], YSTYLE=1, $
        XTITLE='% Complete', $
        TITLE='Aspect Solution Progress Monitor', $
	CHARSIZE = 2.0
  for ib=0,nbins-1 do begin 
    oplot, [100.0*FLOAT(ib)/nbins],[0.0], PSYM=4
    ; this time bin...
    tb = FLOAT(ib)*time_bin_size
    te = FLOAT(ib+1)*time_bin_size
    binT(ib) = (tb+te)/2.0
    binT(ib) = (tb+te)/2.0
    ; find the zero-order events in this time region
    sel = where( ABS(Xtouse) LT 0.5*zoregsize AND $
		ABS(Ytouse) LT 0.5*zoregsize AND $
		ftime GT tb AND ftime LE te, nfound )
    ; found any?
    if nfound GE 1 then begin
      binnave(ib) = nfound
      ; Different ways to calculate the "average" location at this time:
      ; Arithmetic average ...
      ;;binaveX(ib) = TOTAL(Xtouse(sel))/FLOAT(nfound)
      ;;binaveY(ib) = TOTAL(Ytouse(sel))/FLOAT(nfound)
      ; Average of some median fraction of events:
      ; average of the median (m_medave-2)/m_medave of events,
      ; e.g., m_medave = 4  --> average 1/4 to 3/4 = 50% of events
      ;       m_medave = 20 --> average 1/20 to 19/20 = 90% of events
      m_medave = 4   ; average 50% of events, cuts out 25% on each side
      selsort = sel(SORT(Xtouse(sel)))
      selmed = selsort( (nfound/m_medave) : (((m_medave-1)*nfound)/m_medave) )
      binaveX(ib) = TOTAL(Xtouse(selmed))/FLOAT(n_elements(selmed))
      selsort = sel(SORT(Ytouse(sel)))
      selmed = selsort( (nfound/m_medave) : (((m_medave-1)*nfound)/m_medave) )
      binaveY(ib) = TOTAL(Ytouse(selmed))/FLOAT(n_elements(selmed))
    end else begin
      ; if no events were found in the interval
      ; use 0 (relative to average) - this could be made
      ; smarter (use previous value, extrapolate, etc.)
      ; but hopefully this case will be infrequent!
      binaveX(ib) = 0.0
      binaveY(ib) = 0.0
      binnave(ib) = nfound
    end
    ; Evaluate the apodization function
    binApod(ib) = 1.0 ; default
    if binT(ib) LT apod_region_time then begin
      binApod(ib) = 0.5*(1.0 - COS(!PI*binT(ib)/apod_region_time))
    end
    if binT(ib) GT (interval_duration - apod_region_time) then begin
      binApod(ib) = 0.5*(1.0 - COS(!PI*(interval_duration-binT(ib))/apod_region_time))
    end
  end

  if NOT(KEYWORD_SET(SILENT)) then begin
    print, ' Min / Max number of events per time bin = '+ $
	STRCOMPRESS(MIN(binnave)) + ' / '+STRCOMPRESS(MAX(binnave))
  end
  printf, out_unit, ' Min / Max number of events per time bin = '+ $
	STRCOMPRESS(MIN(binnave)) + ' / '+STRCOMPRESS(MAX(binnave))

  ; Apodize the time series and 
  ; Take the transform of the average locations...
  fftx = FFT(binaveX*binApod)
  ffty = FFT(binaveY*binApod)

  ; Now just keep the "significant" FFT components
  ; to reconstruct the smoothed aspect for each axis...
  ; To reduce noise due to non-concentrated events
  ; (e.g. background, LETG cross-dispersion events, etc.)
  ; keep only the "low" (but not "too low") frequencies
  frequs = INDGEN(nbins)
  low_frequ = ( ( (frequs LT low_f_defn*0.5*n_elements(fftx)) AND $
		(frequs GT toolow_f_defn*0.5*n_elements(fftx))) OR $
		( (frequs GT (1.0-low_f_defn*0.5)*n_elements(fftx)) AND $
		(frequs LT (1.0-toolow_f_defn*0.5)*n_elements(fftx))) )
  sigx = where( (ABS(fftx) GT fft_thresh*MAX(ABS(fftx(1:*))) ) AND $ 
	low_frequ)
  sigy = where( (ABS(ffty) GT fft_thresh*MAX(ABS(ffty(1:*))) ) AND $
	low_frequ)

  fftxsm = 0.0*fftx
  fftxsm(sigx) = fftx(sigx)
  fftysm = 0.0*ffty
  fftysm(sigy) = ffty(sigy)

  ; Do the reverse transformations... and keep the real part...
  smaveX = FLOAT(FFT(fftxsm, /INVERSE))
  smaveY = FLOAT(FFT(fftysm, /INVERSE))

  if NOT(KEYWORD_SET(SILENT)) then  print, ''
  printf, out_unit, ''

  !p.multi = [0,1,5]

  ; PLOT "Light curve", events per time bin
  plot, binT, binnave, PSYM=10, $
	XSTYLE=1, YRANGE=[0.,1.1*MAX(binnave)],YSTYLE=1, $
        TITLE='Light Curve: Events per Time Interval', $
        XTITLE='Time ('+time_unit+'s)', $
        YTITLE='Counts/bin', $
	CHARSIZE=1.51

  ; Plot the "measured" aspect motion and the smooth fit
  plot, binT, binaveX*binApod, PSYM=-4, $
	XSTYLE=1, YSTYLE=1, $
        TITLE='Average Zero-order '+x_name+' vs t; aspect solution overplotted', $
        XTITLE='Time ('+time_unit+'s)', $
        YTITLE='Ave '+x_name+' (pixels)', $
	CHARSIZE=1.51
  oplot, binT, smaveX, THICK=2, COLOR=clr_grn
  ; Indicate the apodization regions
  if apod_region_time GT 0.0 then begin
    oplot, apod_region_time*[1.,1.], [MIN(binaveX), MAX(binaveX)], $
		LINESTYLE=2, COLOR=clr_grn
    oplot, interval_duration-apod_region_time*[1.,1.], $
	[MIN(binaveX), MAX(binaveX)], $
		LINESTYLE=2, COLOR=clr_grn
  end
  plot_io, ABS(fftx(0:nbins/2)), PSYM=-1, $
	XSTYLE=1, YSTYLE=1, $
        TITLE='FFT of Ave '+x_name+'; selected frequ.s indicated', $
        XTITLE='Frequency Bin (0 to f_Nyquist)', $
        YTITLE='FFT Amplitude', $
	CHARSIZE=1.51
  oplot, ABS(fftxsm(0:nbins/2)), PSYM=6, COLOR=clr_grn

  plot, binT, binaveY*binApod, PSYM=-4, $
	XSTYLE=1, YSTYLE=1, $
        TITLE='Average Zero-order '+y_name+' vs t; aspect solution overplotted', $
        XTITLE='Time ('+time_unit+'s)', $
        YTITLE='Ave '+y_name+' (pixels)', $
	CHARSIZE=1.51
  oplot, binT, smaveY, THICK=2, COLOR=clr_grn
  ; Indicate the apodization regions
  if apod_region_time GT 0.0 then begin
    oplot, apod_region_time*[1.,1.], [MIN(binaveY), MAX(binaveY)], $
		LINESTYLE=2, COLOR=clr_grn
    oplot, interval_duration-apod_region_time*[1.,1.], $
	[MIN(binaveY), MAX(binaveY)], $
		LINESTYLE=2, COLOR=clr_grn
  end
  plot_io, ABS(ffty(0:nbins/2)), PSYM=-1, $
	XSTYLE=1, YSTYLE=1, $
        TITLE='FFT of Ave '+y_name+'; selected frequ.s indicated', $
        XTITLE='Frequency Bin (0 to f_Nyquist)', $
        YTITLE='FFT Amplitude', $
	CHARSIZE=1.51

  oplot, ABS(fftysm(0:nbins/2)), PSYM=6, COLOR=clr_grn

  ; Finish the .gif output
  if NOT(KEYWORD_SET(ZBUFFER)) then wshow,iwind,iconic=0
  image = tvrd()
  tvlct, red, green, blue, /GET
  gif_out = output_prefix+'_'+proc_method+'_aspectsolve.gif'
  write_gif, out_dir+'/'+gif_out, image, red, green, blue

  ; Add .gif link
  printf, out_unit, "</PRE>"
  printf, out_unit, "<UL>"
  printf, out_unit, '<LI><B><A href="'+gif_out+'">'+'Aspect Solution'+'</A></B>'
  printf, out_unit, "</UL>"
  printf, out_unit, "<PRE>"

  ; Make the aspect corrected values:
  ; binT is the aspect time and smaveX and smaveY are
  ; the locations of zero-order at that time... so
  ; use ftime for each event to interpolate zero-order
  ; for that event at that time...
  if NOT(KEYWORD_SET(SILENT)) then begin
    print, ''
    print, ' Making aspect corrected coordinates, AX,AY ...'
  end
  printf, out_unit, ''
  printf, out_unit, ' Making aspect corrected coordinates, AX,AY ...'

  ; Subtract the aspect solution
  AX = Xtouse - INTERPOL_SORT(smaveX, binT, ftime,/SILENT)
  AY = Ytouse - INTERPOL_SORT(smaveY, binT, ftime,/SILENT)
  ax_name = 'a'+x_name
  ay_name = 'a'+y_name
  ; and add back the average values to AX, AY and Xtouse, Ytouse
  Xtouse = Xtouse + aveXtouse
  Ytouse = Ytouse + aveYtouse
  AX = AX + aveXtouse
  AY = AY + aveYtouse
  aveAX = TOTAL(AX(zosel))/FLOAT(n_elements(zosel))
  aveAY = TOTAL(AY(zosel))/FLOAT(n_elements(zosel))

  if NOT(KEYWORD_SET(SILENT)) then print, ''
  printf, out_unit, ''

  if KEYWORD_SET(MOUSE) then begin
    print, '    !!! Click Mouse anywhere to Continue !!!'
    print, ''
    cursor, x, y, 3
  end

  ; - - - - - - - - ASPECT Spatial Examination - - - - - - - - - - 
  ; Now we compare Xtouse,Ytouse to AX, AY

  !p.multi = [0,2,4]

  if NOT(KEYWORD_SET(SILENT)) then begin
    print, ' Before aspect correction:'
    print, ''
  end
  printf, out_unit, ' Before aspect correction:'
  printf, out_unit, ''

  ; Zero-order Region and uncorrected corrds
  plot, Xtouse(zosel), Ytouse(zosel), PSYM=3, $
	XRANGE=aveXtouse+ zoregsize*[-0.5,0.5], XSTYLE=1, $
	YRANGE=aveYtouse+ zoregsize*[-0.5,0.5], YSTYLE=1, $
	BACK=clr_back, COLOR=clr_wht, /NODATA, $
        TITLE='Zero-order Region', $
        XTITLE=x_name+' (pixels)', $
        YTITLE=y_name+' (pixels)', $
	CHARSIZE=1.51
  plots, Xtouse(zosel), Ytouse(zosel), $
		PSYM=3, COLOR=energy_colors(zosel), NOCLIP=0

  ; plot cross-hairs at the z-o location
  oplot, zoregsize*[-0.5,0.5]+aveXtouse, [1.,1.]+aveYtouse
  oplot, [1.,1.]+aveXtouse, zoregsize*[-0.5,0.5]+aveYtouse
  ; Calculate the r-rms of these events
  rs = SQRT((Xtouse(zosel)-aveXtouse)^2 + (Ytouse(zosel)-aveYtouse)^2)
  rrms = SQRT(TOTAL(rs*rs)/FLOAT(n_elements(zosel)))
  if NOT(KEYWORD_SET(SILENT)) then begin
    print, ' '+x_name+','+y_name+' RMS Radius = '+STRCOMPRESS(rrms)+' pixels'
  end
  printf, out_unit, ' '+x_name+','+y_name+' RMS Radius = '+ $
	STRCOMPRESS(rrms)+' pixels'

  ; Plot the Dispersion (Xtouse) LRF
  lin_hist, Xtouse(zosel), 1.0, xbins, xcounts
  plot, xbins, xcounts, PSYM=10, $
        TITLE='Zero-order '+x_name+' Profile (~ LRF)', $
        XTITLE=x_name+' (pixels)', $
        YTITLE='Counts/bin', $
	CHARSIZE=1.51

  above10 = where(xcounts GE 0.1*MAX(xcounts), nabove10)

  if NOT(KEYWORD_SET(SILENT)) then begin
    print, ' Number of '+x_name+' LRF width at 10% of peak = '+ $
	STRCOMPRESS(nabove10)
  end
  printf, out_unit, ' Number of '+x_name+' LRF width at 10% of peak = '+ $
	STRCOMPRESS(nabove10)

  ; Plot the events vs time
  plot, ftime(zosel), Xtouse(zosel), PSYM=3, $
	XSTYLE=1, YSTYLE=1, $
	BACK=clr_back, COLOR=clr_wht, /NODATA, $
        TITLE='t-X Plot for Zero-order Events', $
        XTITLE='Time ('+time_unit+'s)', $
        YTITLE=x_name+' (pixels)', $
	CHARSIZE=1.51
  plots, ftime(zosel), Xtouse(zosel), $
		PSYM=3, COLOR=energy_colors(zosel), NOCLIP=0

  plot, ftime(zosel), Ytouse(zosel), PSYM=3, $
	XSTYLE=1, YSTYLE=1, $
	BACK=clr_back, COLOR=clr_wht, /NODATA, $
        TITLE='t-Y Plot for Zero-order Events', $
        XTITLE='Time ('+time_unit+'s)', $
        YTITLE=y_name+' (pixels)', $
	CHARSIZE=1.51
  plots, ftime(zosel), Ytouse(zosel), $
		PSYM=3, COLOR=energy_colors(zosel), NOCLIP=0

  ; Show the AX,AY value for these events
  plot, AX(zosel), AY(zosel), PSYM=3, $
	XSTYLE=1, XRANGE = aveAX + zo_exam_size*[-1.,1.], $
	YSTYLE=1, YRANGE = aveAY + zo_exam_size*[-1.,1.], $
	BACK=clr_back, COLOR=clr_wht, /NODATA, $
        TITLE='Aspect X, Aspect Y: Zero-order Region', $
        XTITLE=ax_name+' (pixels)', $
        YTITLE=ay_name+' (pixels)', $
	CHARSIZE=1.51
  plots, AX(zosel), AY(zosel), $
		PSYM=3, COLOR=energy_colors(zosel), NOCLIP=0

  if NOT(KEYWORD_SET(SILENT)) then begin
    print, ''
    print, ' Aspect correction yields (including apodized events):'
    print, ''
  end
  printf, out_unit, ''
  printf, out_unit, ' Aspect correction yields (including apodized events):'
  printf, out_unit, ''

  ; Calculate the r-rms of these events
  axyrs = SQRT((AX(zosel)-aveAX)^2 + (AY(zosel)-aveAY)^2)
  raxyrms = SQRT(TOTAL(axyrs*axyrs)/FLOAT(n_elements(zosel)))
  if NOT(KEYWORD_SET(SILENT)) then begin
    print, ' AX,AY RMS Radius = '+STRCOMPRESS(raxyrms)+' pixels'
  end
  printf, out_unit, ' AX,AY RMS Radius = '+STRCOMPRESS(raxyrms)+' pixels'

  ; Plot the Dispersion axis (AX) LRF
  ; bin size is 1./zo_exam_subbins
  lin_hist, AX(zosel) - aveAX, 1.0/zo_exam_subbins, axxbins, axxcounts

  plot, axxbins, axxcounts, PSYM=10, $
        TITLE='Zero-order Aspect X Profile (~ LRF)', $
        XTITLE=ax_name+' (pixels, bin = '+ $
		STRING(1.0/zo_exam_subbins, FORMAT='(F5.3)')+' pixel)', $
	XRANGE=zo_exam_size*[-1.,1.], XSTYLE=1, $
        YTITLE='Counts/bin', $
	CHARSIZE=1.51
  axabove10 = where(axxcounts GE 0.10*MAX(axxcounts), naxabove10)

  if NOT(KEYWORD_SET(SILENT)) then begin
    print, ' Width of AX LRF at 10% of peak = '+ $
		STRING(naxabove10/zo_exam_subbins,FORMAT='(F6.1)')+ ' pixels'
  end
  printf, out_unit, ' Width of AX LRF at 10% of peak = '+ $
		STRING(naxabove10/zo_exam_subbins,FORMAT='(F6.1)')+ ' pixels'


  ; Plot the events vs time
  plot, ftime(zosel), AX(zosel) - aveAX, PSYM=3, $
	XSTYLE=1, YSTYLE=1, YRANGE=zo_exam_size*[-1.,1.], $
	BACK=clr_back, COLOR=clr_wht, /NODATA, $
        TITLE='t - Aspect X Plot for Zero-order Events', $
        XTITLE='Time ('+time_unit+'s)', $
        YTITLE=ax_name+' - '+STRING(aveAX,FORMAT='(F9.1)'), $
	CHARSIZE=1.51
  plots, ftime(zosel), AX(zosel) - aveAX, $
		PSYM=3, COLOR=energy_colors(zosel), NOCLIP=0
  ; Indicate the apodization regions
  if apod_region_time GT 0.0 then begin
    oplot, apod_region_time*[1.,1.], zo_exam_size*[-1.,1.], $
		LINESTYLE=2, COLOR=clr_grn
    oplot, interval_duration-apod_region_time*[1.,1.], $
	zo_exam_size*[-1.,1.], LINESTYLE=2, COLOR=clr_grn
  end

  plot, ftime(zosel), AY(zosel) - aveAY, PSYM=3, $
	XSTYLE=1, YSTYLE=1, YRANGE=zo_exam_size*[-1.,1.], $
	BACK=clr_back, COLOR=clr_wht, /NODATA, $
        TITLE='t - Aspect Y Plot for Zero-order Events', $
        XTITLE='Time ('+time_unit+'s)', $
        YTITLE=ay_name+' - '+STRING(aveAY,FORMAT='(F9.1)'), $
	CHARSIZE=1.51
  plots, ftime(zosel), AY(zosel) - aveAY, $
		PSYM=3, COLOR=energy_colors(zosel), NOCLIP=0
  ; Indicate the apodization regions
  if apod_region_time GT 0.0 then begin
    oplot, apod_region_time*[1.,1.], zo_exam_size*[-1.,1.], $
		LINESTYLE=2, COLOR=clr_grn
    oplot, interval_duration-apod_region_time*[1.,1.], $
	zo_exam_size*[-1.,1.], LINESTYLE=2, COLOR=clr_grn
  end

  if NOT(KEYWORD_SET(SILENT)) then print, ''
  printf, out_unit, ''

  ; Finish the .gif output
  if NOT(KEYWORD_SET(ZBUFFER)) then wshow,iwind,iconic=0
  image = tvrd()
  tvlct, red, green, blue, /GET
  gif_out = output_prefix+'_'+proc_method+'_aspectspatial.gif'
  write_gif, out_dir+'/'+gif_out, image, red, green, blue

  ; Add .gif link
  printf, out_unit, "</PRE>"
  printf, out_unit, "<UL>"
  printf, out_unit, '<LI><B><A href="'+gif_out+'">'+ $
	'Zero-order Aspect Corrected'+'</A></B>'
  printf, out_unit, "</UL>"
  printf, out_unit, "<PRE>"

  if KEYWORD_SET(MOUSE) then begin
    print, '    !!! Click Mouse anywhere to Continue !!!'
    print, ''
    cursor, x, y, 3
  end
  ; end of ASPECT zero-order examination
  ; - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

  if NOT(KEYWORD_SET(BUT_DONT_APPLY)) then begin
    ; Select only the events in the un-apodized time range to pass on
    ; for futher analysis
    ; - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    keep = where(ftime GT apod_region_time AND $
		ftime LT (interval_duration - apod_region_time) , nkeep)
    ; if there are no events in the time region then pass them
    ; all on !?!
    if nkeep LE 0 then begin
      keep = LINDGEN(n_elements(ftime))
      ; Let folks know what happened (silent or not!)
      printf, out_unit, "* No valid events in auto-aspect time region?! Pass them all."
      print, "* No valid events in auto-aspect time region?! Pass them all."
    end
    evts = evts(keep)
    nevts = n_elements(evts)
    ftime = ftime(keep) - MIN(ftime(keep))
    interval_duration = MAX(ftime)
    ; assume that aspect solution is done in a time region lacking
    ; large gaps (solution would have problems I imagine!) so that:
    live_interval = interval_duration  ; is a good estimate
    ftime_start = MIN(ftime(keep))
    abs_start_time = abs_start_time + ftime_start
    Etouse = Etouse(keep)
    energy_colors = energy_colors(keep)
    Xtouse = Xtouse(keep)
    Ytouse = Ytouse(keep)
    AX = AX(keep)
    AY = AY(keep)
    ; and redefine zosel using the previous average X,Y values
    ; applied to AX, AY
    zosel = where( ABS(AX-aveXtouse) LT 0.5*zoregsize AND $
		ABS(AY-aveYtouse) LT 0.5*zoregsize  )
    aveAX = TOTAL(AX(zosel))/FLOAT(n_elements(zosel))
    aveAY = TOTAL(AY(zosel))/FLOAT(n_elements(zosel))
  end else begin
    ; OK, don't apply the aspect solution after all...
    ; Define AX and AY in anycase, to be used in further analysis...
    AX = Xtouse
    AY = Ytouse
    ax_name = x_name
    ay_name = y_name
    aveAX = aveXtouse
    aveAY = aveYtouse
  end
end
ASPECT_BAIL: dummy_statement = 0.0
; end of ASPECT
; - - - - - - - - - - - - - - - - - - - - - - - - -


if NOT(KEYWORD_SET(SILENT)) then begin
  print, ' - - - - - - - - Detailed Examine Zero-order Spatial... - - - - - - -'
  print, ''
end
printf, out_unit, "</PRE>"
printf, out_unit, '<HR>'
printf, out_unit, '<H3>Detailed Examine Zero-order Spatial...</H3>'
printf, out_unit, "<PRE>"
printf, out_unit, ""

; ROLL IT ?
; Roll the AX, AY coordinates if ROLLAXAY is present.
; Positive roll of 90 degrees takes the ACIS TDETX axis
; into the ACIS TDETY axis (i.e., about "TDETZ".)
;
if n_elements(ROLLAXAY) GT 0 then begin
  roll_str = STRCOMPRESS(STRING(rollaxay,FORMAT='(F10.3)'),/REMOVE)
  if NOT(KEYWORD_SET(SILENT)) then begin
    print, '* Rolling the AX,AY coordinates by ' + roll_str + ' degrees.'
    print, ""
  end
  printf, out_unit, '* Rolling the AX,AY coordinates by ' + $
	roll_str + ' degrees.'
  printf, out_unit, ""
  ; rolled values
  sinr = SIN(!DTOR*rollaxay)
  cosr = COS(!DTOR*rollaxay)
  AXr = cosr*(AX-aveAX) - sinr*(AY-aveAY) + aveAX
  AYr = sinr*(AX-aveAX) + cosr*(AY-aveAY) + aveAY
  AX = AXr
  AY = AYr
  ; new names
  ax_name = ax_name+','+roll_str+'deg.'
  ay_name = ay_name+','+roll_str+'deg.'
end else begin
  rollaxay = 0.0
end
; record the roll value

rpf_add_param, rpf, 'roll_axay', rollaxay, UNIT='degrees'


; Summarize the event status here because Aspect correction can remove
; a bunch (33%) of events...

if NOT(KEYWORD_SET(SILENT)) then begin
  print, ' Total Events = '+STRCOMPRESS(n_elements(evts))
  print, ' Start time = '+STRCOMPRESS(abs_start_time)+' '+time_unit+'s'
  print, ' Interval duration = '+STRCOMPRESS(interval_duration)+' '+time_unit+'s'
  print, ' Ave Event Rate = '+STRCOMPRESS(FLOAT(n_elements(evts))/ $
			interval_duration)+' events/'+time_unit
  print, ''
  ; Also, the "AX,AY" coords are going to be used for grating spectra
  print, ' The spatial coordinates to be used for grating spectra are:'
  print, '   AX, AY  =  '+ax_name+', '+ay_name
  print, ''

end
printf, out_unit, ' Total Events = '+STRCOMPRESS(n_elements(evts))
printf, out_unit, ' Start time = '+STRCOMPRESS(abs_start_time)+ $
	' '+time_unit+'s'
printf, out_unit, ' Interval duration = '+STRCOMPRESS(interval_duration)+ $
	' '+time_unit+'s'
printf, out_unit, ' Ave Event Rate = '+STRCOMPRESS(FLOAT(n_elements(evts))/ $
			interval_duration)+' events/'+time_unit
printf, out_unit, ''
printf, out_unit, ' The spatial coordinates to be used for grating spectra are:'
printf, out_unit, '   AX, AY  =  '+ax_name+', '+ay_name
printf, out_unit, ''


; - - - - - - Detailed AX AY - - - -

; Restrict the zo events in the cross-disp direction:
n_full_cd = n_elements(zosel)
zosel = where( ABS(AX-aveAX) LT 0.5*zoregsize AND $
		ABS(AY-aveAY) LT 0.5*(zoregsize < (cd_width/pixel_size))  )
n_restricted_cd = n_elements(zosel)

; Calculate the average CHIPX, CHIPY of zero-order ...
if (TOTAL(evts_tags EQ 'CHIPX') GE 1) then begin
  zo_chip_x = TOTAL(evts(zosel).CHIPX)/FLOAT(n_elements(zosel))
  zo_chip_y = TOTAL(evts(zosel).CHIPY)/FLOAT(n_elements(zosel))

  rpf_add_param, rpf, 'zo_chip_x',  zo_chip_x, UNIT='pixel'
  rpf_add_param, rpf, 'zo_chip_y',  zo_chip_y, UNIT='pixel'

  ; Report this info
  if NOT(KEYWORD_SET(SILENT)) then begin
    print, ' Zero-order Average CHIPX, CHIPY = ' + $
	STRING(zo_chip_x,FORMAT='(F7.1)') + ', ' + STRING(zo_chip_y,FORMAT='(F7.1)')
    print, ''
  end
  printf, out_unit, ' Zero-order Average CHIPX, CHIPY = ' + $
	STRING(zo_chip_x,FORMAT='(F7.1)') + ', ' + STRING(zo_chip_y,FORMAT='(F7.1)')
  printf, out_unit, ''
end

; Calculate the r-rms of these events
axyrs = SQRT((AX(zosel)-aveAX)^2 + (AY(zosel)-aveAY)^2)
raxyrms = SQRT(TOTAL(axyrs*axyrs)/FLOAT(n_elements(zosel)))
if NOT(KEYWORD_SET(SILENT)) then begin
  print, ' AX,AY RMS Radius = '+STRCOMPRESS(raxyrms)+' pixels'
end
printf, out_unit, ' AX,AY RMS Radius = '+STRCOMPRESS(raxyrms)+' pixels'

rpf_add_param, rpf, 'det_rms_radius',  raxyrms, $
	UNIT='pixel'


; Create the 1-D projection along nominal dispersion axis
lin_hist, AX(zosel) - aveAX, 1.0/zo_exam_subbins, axxbins, axxcounts
; save this histogram for output later
zo_axxbins = axxbins
zo_axxcounts = axxcounts

; Measure and report LRF widths
axabove10 = where(axxcounts GE 0.10*MAX(axxcounts), naxabove10)
axabove50 = where(axxcounts GE 0.50*MAX(axxcounts), naxabove50)

; Save a guess for the zero-order FWHM in pixels:
zo_fwhm_pixels = FLOAT(naxabove50)/FLOAT(zo_exam_subbins)

if NOT(KEYWORD_SET(SILENT)) then begin
  print, ' Width of AX LRF at 10% of peak = '+ $
		STRING((1000.0*pixel_size*naxabove10)/zo_exam_subbins, $
		FORMAT='(F7.1)')+ ' microns'
  print, ' Width of AX LRF at 50% of peak = '+ $
		STRING((1000.0*pixel_size*naxabove50)/zo_exam_subbins, $
		FORMAT='(F7.1)')+ ' microns'
end
printf, out_unit, ' Width of AX LRF at 10% of peak = '+ $
		STRING((1000.0*pixel_size*naxabove10)/zo_exam_subbins, $
		FORMAT='(F7.1)')+ ' microns'
printf, out_unit, ' Width of AX LRF at 50% of peak = '+ $
		STRING((1000.0*pixel_size*naxabove50)/zo_exam_subbins, $
		FORMAT='(F7.1)')+ ' microns'

; Fit the data with a gaussian...
; Guess fit parameters [height, center, gauss_sigma, continuum]
; guess a sigma which corresponds to naxabove50
guess_sigma = zo_fwhm_pixels / sig_per_fwhm  ; pixels
guess_center = TOTAL(FLOAT(axxbins(axabove50)))/n_elements(axabove50)
a_inout = [max(axxcounts), guess_center, guess_sigma, 1.0]
; flat continuum
df_continuum = 0.*axxbins + 1.0
df_fit, 1, axxbins, axxcounts, a_inout, $
		(SQRT(axxcounts) > 2), sig, yfit
if NOT(KEYWORD_SET(SILENT)) then begin
  print, ' Gaussian center = '+STRING(a_inout(1))+' pixels'
  print, ' Gaussian fit FWHM = '+STRING(1.E3*pixel_size*a_inout(2)*sig_per_fwhm, $
		FORMAT='(F7.1)')+ ' microns'
  print, '        FWHM error = '+STRING(1.E3*pixel_size*sig(2)*sig_per_fwhm, $
		FORMAT='(F7.1)')+ ' microns'
end
printf, out_unit, ' Gaussian center = '+STRING(a_inout(1))+' pixels'
printf, out_unit, ' Gaussian fit FWHM = '+STRING(1.E3*pixel_size*a_inout(2)*sig_per_fwhm, $
		FORMAT='(F7.1)')+ ' microns'
printf, out_unit, '        FWHM error = '+STRING(1.E3*pixel_size*sig(2)*sig_per_fwhm, $
		FORMAT='(F7.1)')+ ' microns'

; Save the zero-order FWHM in pixels from the fit:
zo_fwhm_pixels = a_inout(2)*sig_per_fwhm
; and the fit location offset
zo_fit_offset = a_inout(1)

; Save the fit location to the structure:
rpf_add_param, rpf, 'zo_loc_fit', a_inout(1), $
	ERROR = sig(1), UNIT='pixel'
; Save the zero-order fwhm value, in microns, to the structure:
rpf_add_param, rpf, 'zo_fwhm_fit', 1000.0*pixel_size*zo_fwhm_pixels, $
	ERROR = 1.E3*pixel_size*sig(2)*sig_per_fwhm, UNIT='micron'

; and the ACF !?!
acf_herman, axxcounts, acf_val, acf_err
rpf_add_param, rpf, 'zo_acf', acf_val, $
	ERROR = acf_err, UNIT='fraction in pixel/'+ $
		STRCOMPRESS(FIX(zo_exam_subbins),/REMOVE)

; along with the number of zo counts
rpf_add_param, rpf, 'zo_detail_events', n_elements(zosel), $
	ERROR = 0.0, UNIT=''
; and the zo rate
rpf_add_param, rpf, 'zo_detail_rate', FLOAT(n_elements(zosel)) / $
	interval_duration, ERROR = SQRT(FLOAT(n_elements(zosel))) / $
	interval_duration, UNIT = 'event/'+time_unit

; If OVERRIDE_ZERO was requested then perhaps the zero-order size
; is also not accurate - ask the user to confirm or replace the
; measured FWHM above
if KEYWORD_SET(OVERRIDE_ZERO) then begin
  print, ''
  print, '     !!!  Zero-order measured FWHM is '+ $
	STRCOMPRESS(1000.0*pixel_size*zo_fwhm_pixels)+' microns.'
  print, '          This value will set the grating spectra bin size.'
  print, ''
  quest_out = '          Do you want to enter a manual value (y/n): ' 
  change_fwhm=''
  if n_elements(OVERR_WIDTH) GT 0 then begin
    change_fwhm='y'
  end else begin
    READ, change_fwhm, PROMPT = quest_out
  end
  if STRPOS(STRUPCASE(change_fwhm), 'Y') GE 0 then begin
    quest_out = '          Enter zero-order FWHM in microns: ' 
    new_fwhm=50.0 ; microns
    if n_elements(OVERR_WIDTH) GT 0 then begin
      new_fwhm = overr_width
    end else begin
      READ, new_fwhm, PROMPT = quest_out
    end
    zo_fwhm_pixels = new_fwhm/(1000.0*pixel_size)
    print, ''
    print, '* Zero-order FWHM manually set to: '+ $
	STRCOMPRESS(1000.0*pixel_size*zo_fwhm_pixels)+' microns.'
    print, ''
    printf, out_unit, ''
    printf, out_unit, '* Zero-order FWHM manually set to: '+ $
	STRCOMPRESS(1000.0*pixel_size*zo_fwhm_pixels)+' microns.'
    printf, out_unit, ''
  end
end else begin
  ; Handle case of no override zero BUT there is override width:
  if n_elements(OVERR_WIDTH) GT 0 then begin
    zo_fwhm_pixels = overr_width/(1000.0*pixel_size)
    if NOT(KEYWORD_SET(SILENT)) then begin
      print, ''
      print, '* Zero-order FWHM manually set to: '+ $
	STRCOMPRESS(1000.0*pixel_size*zo_fwhm_pixels)+' microns.'
      print, ''
    end    
    printf, out_unit, ''
    printf, out_unit, '* Zero-order FWHM manually set to: '+ $
	STRCOMPRESS(1000.0*pixel_size*zo_fwhm_pixels)+' microns.'
    printf, out_unit, ''
  end
end

; Ideally we have a point source with FWHM under 50 microns (2 ACIS
; pixels...) but incase it if extended or aspect correction is not
; good, increase the examination size to make a useful plot...
; Keep doubling the zero-order examination size in order to get
; the "axabove50" to be less than 1/3 of 2times exam_size:
; (zo_exam_size is in pixels)
zo_detail_size = zo_exam_size
while (2./3.)*zo_detail_size LT zo_fwhm_pixels do begin
  zo_detail_size = 2.*zo_detail_size
end

!p.multi=[0,2,2]

; Show the AX,AY value for these events
plot, AX(zosel) - aveAX, AY(zosel) - aveAY, PSYM=3, $
	XSTYLE=1, XRANGE = zo_detail_size*[-1.,1.], $
	YSTYLE=1, YRANGE = zo_detail_size*[-1.,1.], $
	BACK=clr_back, COLOR=clr_wht, /NODATA, $
        TITLE='Aspect X, Aspect Y: Zero-order Region', $
        XTITLE=ax_name+' - '+STRING(aveAX,FORMAT='(F9.1)'), $
        YTITLE=ay_name+' - '+STRING(aveAY,FORMAT='(F9.1)'), $
	CHARSIZE=1.090
plots, AX(zosel) - aveAX, AY(zosel) - aveAY, $
		PSYM=3, COLOR=energy_colors(zosel), NOCLIP=0

; Plot the Dispersion axis (AX) LRF
plot, axxbins, axxcounts, PSYM=10, $
        TITLE='Zero-order Aspect X Profile (~ LRF)', $
        XTITLE=ax_name+' (pixels, bin = '+ $
		STRING(1.0/zo_exam_subbins, FORMAT='(F5.3)')+' pixel)', $
	XRANGE=zo_detail_size*[-1.,1.], XSTYLE=1, $
        YTITLE='Counts/bin', $
	CHARSIZE=1.090
; Plot the gaussian fit
oplot, axxbins, yfit, COLOR=clr_grn

; Plot the events vs time
plot, ftime(zosel), AX(zosel) - aveAX, PSYM=3, $
	XSTYLE=1, YSTYLE=1, YRANGE=zo_detail_size*[-1.,1.], $
	BACK=clr_back, COLOR=clr_wht, /NODATA, $
        TITLE='t - Aspect X Plot for Zero-order Events', $
        XTITLE='Time ('+time_unit+'s)', $
        YTITLE=ax_name+' - '+STRING(aveAX,FORMAT='(F9.1)'), $
	CHARSIZE=1.090
plots, ftime(zosel), AX(zosel) - aveAX, $
		PSYM=3, COLOR=energy_colors(zosel), NOCLIP=0

plot, ftime(zosel), AY(zosel) - aveAY, PSYM=3, $
	XSTYLE=1, YSTYLE=1, YRANGE=zo_detail_size*[-1.,1.], $
	BACK=clr_back, COLOR=clr_wht, /NODATA, $
        TITLE='t - Aspect Y Plot for Zero-order Events', $
        XTITLE='Time ('+time_unit+'s)', $
        YTITLE=ay_name+' - '+STRING(aveAY,FORMAT='(F9.1)'), $
	CHARSIZE=1.090
plots, ftime(zosel), AY(zosel) - aveAY, $
		PSYM=3, COLOR=energy_colors(zosel), NOCLIP=0

; Finish the .gif output
if NOT(KEYWORD_SET(ZBUFFER)) then wshow,iwind,iconic=0
image = tvrd()
tvlct, red, green, blue, /GET
gif_out = output_prefix+'_'+proc_method+'_detailedzero.gif'
write_gif, out_dir+'/'+gif_out, image, red, green, blue

; Add .gif link
printf, out_unit, "</PRE>"
printf, out_unit, "<UL>"
printf, out_unit, '<LI><B><A href="'+gif_out+'">'+ $
	'Zero-order Examination Plots'+'</A></B>'
printf, out_unit, "</UL>"
printf, out_unit, "<PRE>"

if KEYWORD_SET(MOUSE) then begin
  print, ''
  print, '    !!! Click Mouse anywhere to Continue !!!'
  print, ''
  cursor, x, y, 3
end

; - - - - - - Compare AX, AY  to X,Y if available... - - - -
; and if COORDS_NAME is not Sky !
xyshowtoo = (TOTAL(evts_tags EQ 'X') GT 0) AND NOT(coords_name EQ 'Sky')

; Make sure the X and Y have a range as well (i.e., not all 0's)
if xyshowtoo then begin
  xyshowtoo = NOT( (MIN(evts.X) EQ MAX(evts.X)) OR $
	(MIN(evts.Y) EQ MAX(evts.Y)) )
end

if xyshowtoo then begin
  !p.multi = [0,2,2]
  if NOT(KEYWORD_SET(SILENT)) then begin
    print, ''
    print, ' Sky X,Y (Level 1) Coordinates are present... showing them too.'
    print, ''
  end
  printf, out_unit, ''
  printf, out_unit, ' Sky X,Y (Level 1) Coordinates are present... showing them too.'
  printf, out_unit, ''
  ; Show the X,Y value for these events
  aveX = TOTAL(evts(zosel).X)/FLOAT(n_elements(zosel))
  aveY = TOTAL(evts(zosel).Y)/FLOAT(n_elements(zosel))
  plot, evts(zosel).X - aveX, evts(zosel).Y - aveY, PSYM=3, $
	XSTYLE=1, XRANGE = zo_detail_size*[-1.,1.], $
	YSTYLE=1, YRANGE = zo_detail_size*[-1.,1.], $
	BACK=clr_back, COLOR=clr_wht, /NODATA, $
        TITLE='Sky X, Sky Y (Level 1) : Zero-order Region', $
        XTITLE='L1 Sky X - '+STRING(aveX,FORMAT='(F9.1)'), $
        YTITLE='L1 Sky Y - '+STRING(aveY,FORMAT='(F9.1)'), $
	CHARSIZE=1.090
  plots, evts(zosel).X - aveX, evts(zosel).Y - aveY, PSYM=3, $
	COLOR=energy_colors(zosel), NOCLIP=0

  ; Calculate the r-rms of these events
  xyrs = SQRT((evts(zosel).X-aveX)^2 + (evts(zosel).Y-aveY)^2)
  rxyrms = SQRT(TOTAL(xyrs*xyrs)/FLOAT(n_elements(zosel)))
  if NOT(KEYWORD_SET(SILENT)) then begin
    print, ' X,Y RMS Radius = '+STRCOMPRESS(rxyrms)+' pixels'
  end
  printf, out_unit, ' X,Y RMS Radius = '+STRCOMPRESS(rxyrms)+' pixels'

  rpf_add_param, rpf, 'xy_rms_radius',  rxyrms, $
	UNIT='pixel'

  ; Plot the Dispersion axis (X) LRF
  lin_hist, evts(zosel).X - aveX, 1.0/zo_exam_subbins, xxbins, xxcounts
  plot, xxbins, xxcounts, PSYM=10, $
        TITLE='Zero-order Sky X Profile (~ LRF)', $
        XTITLE='Sky X (pixels, bin = '+ $
		STRING(1.0/zo_exam_subbins, FORMAT='(F5.3)')+' pixels)', $
	XRANGE=zo_detail_size*[-1.,1.], XSTYLE=1, $
        YTITLE='Counts/bin', $
	CHARSIZE=1.090

  xabove10 = where(xxcounts GE 0.10*MAX(xxcounts), nxabove10)
  xabove50 = where(xxcounts GE 0.50*MAX(xxcounts), nxabove50)
  if NOT(KEYWORD_SET(SILENT)) then begin
    print, ' Width of LRF at 10% of peak = '+ $
		STRING((1000.0*pixel_size*nxabove10)/zo_exam_subbins, $
		FORMAT='(F7.1)')+ ' microns'
    print, ' Width of LRF at 50% of peak = '+ $
		STRING((1000.0*pixel_size*nxabove50)/zo_exam_subbins, $
		FORMAT='(F7.1)')+ ' microns'
  end
  printf, out_unit, ' Width of LRF at 10% of peak = '+ $
		STRING((1000.0*pixel_size*nxabove10)/zo_exam_subbins, $
		FORMAT='(F7.1)')+ ' microns'
  printf, out_unit, ' Width of LRF at 50% of peak = '+ $
		STRING((1000.0*pixel_size*nxabove50)/zo_exam_subbins, $
		FORMAT='(F7.1)')+ ' microns'

  ; Fit the data with a gaussian...
  ; Guess fit parameters [height, center, gauss_sigma, continuum]
  ; guess a sigma which corresponds to naxabove50
  guess_sigma = zo_fwhm_pixels / sig_per_fwhm  ; pixels
  guess_center = TOTAL(FLOAT(xxbins(xabove50)))/n_elements(xabove50)
  a_inout = [max(xxcounts), guess_center, guess_sigma, 1.0]
  ; flat continuum
  df_continuum = 0.*xxbins + 1.0
  df_fit, 1, xxbins, xxcounts, a_inout, $
		(SQRT(xxcounts) > 2), sig, yfit

  oplot, xxbins, yfit, COLOR=clr_grn

  if NOT(KEYWORD_SET(SILENT)) then begin
    print, ' Gaussian center = '+STRING(a_inout(1))+' pixels'
    print, ' Gaussian fit FWHM = '+STRING(1.E3*pixel_size*a_inout(2)*sig_per_fwhm, $
		FORMAT='(F7.1)')+ ' microns'
    print, '        FWHM error = '+STRING(1.E3*pixel_size*sig(2)*sig_per_fwhm, $
		FORMAT='(F7.1)')+ ' microns'
  end
  printf, out_unit, ' Gaussian center = '+STRING(a_inout(1))+' pixels'
  printf, out_unit, ' Gaussian fit FWHM = '+STRING(1.E3*pixel_size*a_inout(2)*sig_per_fwhm, $
		FORMAT='(F7.1)')+ ' microns'
  printf, out_unit, '        FWHM error = '+STRING(1.E3*pixel_size*sig(2)*sig_per_fwhm, $
		FORMAT='(F7.1)')+ ' microns'

; Save the fit location to the structure:
rpf_add_param, rpf, 'zo_xy_loc_fit', a_inout(1), $
	ERROR = sig(1), UNIT='pixel'
; Save the XY zero-order fwhm value, in microns, to the structure:
rpf_add_param, rpf, 'zo_xy_fwhm_fit', 1.E3*pixel_size*a_inout(2)*sig_per_fwhm, $
	ERROR = 1.E3*pixel_size*sig(2)*sig_per_fwhm, UNIT='micron'

; and the ACF !?!
acf_herman, xxcounts, acf_val, acf_err
rpf_add_param, rpf, 'zo_xy_acf', acf_val, $
	ERROR = acf_err, UNIT='fraction in pixel/'+ $
		STRCOMPRESS(FIX(zo_exam_subbins),/REMOVE)


  ; Plot the events vs time
  plot, ftime(zosel), evts(zosel).X - aveX, PSYM=3, $
	YRANGE = zo_detail_size*[-1.,1.], XSTYLE=1, YSTYLE=1, $
	BACK=clr_back, COLOR=clr_wht, /NODATA, $
        TITLE='t - Sky X Plot for Zero-order Events', $
        XTITLE='Time ('+time_unit+'s)', $
        YTITLE='Sky X - '+STRING(aveX,FORMAT='(F9.1)'), $
	CHARSIZE=1.090
  plots, ftime(zosel), evts(zosel).X - aveX, PSYM=3, $
	COLOR=energy_colors(zosel), NOCLIP=0

  plot, ftime(zosel), evts(zosel).Y - aveY, PSYM=3, $
	XSTYLE=1, YSTYLE=1, YRANGE=zo_detail_size*[-1.,1.0], $
	BACK=clr_back, COLOR=clr_wht, /NODATA, $
        TITLE='t - Sky Y Plot for Zero-order Events', $
        XTITLE='Time ('+time_unit+'s)', $
        YTITLE='Sky Y - '+STRING(aveY,FORMAT='(F9.1)'), $
	CHARSIZE=1.090
  plots, ftime(zosel), evts(zosel).Y - aveY, PSYM=3, $
	COLOR=energy_colors(zosel), NOCLIP=0

  ; Finish the .gif output
  if NOT(KEYWORD_SET(ZBUFFER)) then wshow,iwind,iconic=0
  image = tvrd()
  tvlct, red, green, blue, /GET
  gif_out = output_prefix+'_'+proc_method+'_skyxyzero.gif'
  write_gif, out_dir+'/'+gif_out, image, red, green, blue

  ; Add .gif link
  printf, out_unit, "</PRE>"
  printf, out_unit, "<UL>"
  printf, out_unit, '<LI><B><A href="'+gif_out+'">'+ $
	'Sky X,Y Plots for Comparison'+'</A></B>'
  printf, out_unit, "</UL>"
  printf, out_unit, "<PRE>"

  if KEYWORD_SET(MOUSE) then begin
    print, ''
    print, '    !!! Click Mouse anywhere to Continue !!!'
    print, ''
    cursor, x, y, 3
  end
if NOT(KEYWORD_SET(SILENT)) then print, ''
  printf, out_unit, ''
end else begin
  ; any message 
  if (TOTAL(evts_tags EQ 'X') EQ 0) then begin
    if NOT(KEYWORD_SET(SILENT)) then begin
      print, ''
      print, ' ( No X,Y coord.s to compare this to. )'
      print, ''
    end
    printf, out_unit, ''
    printf, out_unit, ' ( No X,Y coord.s to compare this to. )'
    printf, out_unit, ''
  end
end


; - - - - - - Streak events !!! - - - -
; Parameter: how many streak events needed to do this?
n_strk_needed = 50  ; events

; only if ACIS and not CC mode:
if STRPOS(DETECTOR, 'ACIS') GE 0 AND NOT(cc_mode) then begin

; Find the streak events
strk_name = 'Skip_it'
if STRPOS(DETECTOR,'-S') GE 0 then begin
  ; ACIS-S has streak in Y
  strksel = where( ABS(AX-aveAX) LT 0.5*zoregsize AND $
		ABS(AY-aveAY) GT 0.5*zoregsize, nstrk  )
  if nstrk GE n_strk_needed then begin
    cross_strk = AX(strksel) - AveAX
    strk_name = ax_name
  end
end else begin
  ; ACIS-I has streak in X
  strksel = where( ABS(AX-aveAX) GT 0.5*zoregsize AND $
		ABS(AY-aveAY) LT 0.5*zoregsize, nstrk  )
  if nstrk GE n_strk_needed then begin
    cross_strk = AY(strksel) - aveAY
    strk_name = ay_name
  end
end
; another if ...
if strk_name NE 'Skip_it' then begin
; . . . . . . . . . .

; Create the 1-D projection along the cross-streak axis
lin_hist, cross_strk, 1.0/strk_exam_subbins, axxbins, axxcounts

; Measure and report LRF widths
axabove10 = where(axxcounts GE 0.10*MAX(axxcounts), naxabove10)
axabove50 = where(axxcounts GE 0.50*MAX(axxcounts), naxabove50)

; Save a guess for the zero-order FWHM in pixels:
strk_fwhm_pixels = FLOAT(naxabove50)/FLOAT(strk_exam_subbins)

if NOT(KEYWORD_SET(SILENT)) then begin
  print, ' Width of Streak LRF at 10% of peak = '+ $
		STRING((1000.0*pixel_size*naxabove10)/strk_exam_subbins, $
		FORMAT='(F7.1)')+ ' microns'
  print, ' Width of Streak LRF at 50% of peak = '+ $
		STRING((1000.0*pixel_size*naxabove50)/strk_exam_subbins, $
		FORMAT='(F7.1)')+ ' microns'
end
printf, out_unit, ' Width of Streak LRF at 10% of peak = '+ $
		STRING((1000.0*pixel_size*naxabove10)/strk_exam_subbins, $
		FORMAT='(F7.1)')+ ' microns'
printf, out_unit, ' Width of Streak LRF at 50% of peak = '+ $
		STRING((1000.0*pixel_size*naxabove50)/strk_exam_subbins, $
		FORMAT='(F7.1)')+ ' microns'

; Fit the data with a gaussian...
; Guess fit parameters [height, center, gauss_sigma, continuum]
; guess a sigma which corresponds to naxabove50
guess_sigma = strk_fwhm_pixels / sig_per_fwhm  ; pixels
guess_center = TOTAL(FLOAT(axxbins(axabove50)))/n_elements(axabove50)
a_inout = [max(axxcounts), guess_center, guess_sigma, 1.0]
; flat continuum
df_continuum = 0.*axxbins + 1.0
df_fit, 1, axxbins, axxcounts, a_inout, $
		(SQRT(axxcounts) > 2), sig, yfit
if NOT(KEYWORD_SET(SILENT)) then begin
  print, ' Gaussian center = '+STRING(a_inout(1))+' pixels'
  print, ' Gaussian fit FWHM = '+STRING(1.E3*pixel_size*a_inout(2)*sig_per_fwhm, $
		FORMAT='(F7.1)')+ ' microns'
  print, '        FWHM error = '+STRING(1.E3*pixel_size*sig(2)*sig_per_fwhm, $
		FORMAT='(F7.1)')+ ' microns'
end
printf, out_unit, ' Gaussian center = '+STRING(a_inout(1))+' pixels'
printf, out_unit, ' Gaussian fit FWHM = '+STRING(1.E3*pixel_size*a_inout(2)*sig_per_fwhm, $
		FORMAT='(F7.1)')+ ' microns'
printf, out_unit, '        FWHM error = '+STRING(1.E3*pixel_size*sig(2)*sig_per_fwhm, $
		FORMAT='(F7.1)')+ ' microns'

; Save the zero-order FWHM in pixels from the fit:
strk_fwhm_pixels = a_inout(2)*sig_per_fwhm
; and the fit location offset
strk_fit_offset = a_inout(1)

; Save the fit location to the structure:
rpf_add_param, rpf, 'strk_loc_fit', a_inout(1), $
	ERROR = sig(1), UNIT='pixel'
; Save the zero-order fwhm value, in microns, to the structure:
rpf_add_param, rpf, 'strk_fwhm_fit', 1000.0*pixel_size*strk_fwhm_pixels, $
	ERROR = 1.E3*pixel_size*sig(2)*sig_per_fwhm, UNIT='micron'

; and the ACF !?!
acf_herman, axxcounts, acf_val, acf_err
rpf_add_param, rpf, 'strk_acf', acf_val, $
	ERROR = acf_err, UNIT='fraction in pixel/'+ $
		STRCOMPRESS(FIX(strk_exam_subbins),/REMOVE)

; along with the number of Streak counts
rpf_add_param, rpf, 'strk_events', n_elements(strksel), $
	ERROR = 0.0, UNIT=''
; and the Streak rate
rpf_add_param, rpf, 'strk_rate', FLOAT(n_elements(strksel)) / $
	interval_duration, ERROR = SQRT(FLOAT(n_elements(strksel))) / $
	interval_duration, UNIT = 'event/'+time_unit

; Ideally we have a point source with FWHM under 50 microns (2 ACIS
; pixels...) but incase it if extended or aspect correction is not
; good, increase the examination size to make a useful plot...
; Keep doubling the zero-order examination size in order to get
; the "axabove50" to be less than 1/3 of 2times exam_size:
; (zo_exam_size is in pixels)
zo_detail_size = zo_exam_size
while (2./3.)*zo_detail_size LT strk_fwhm_pixels do begin
  zo_detail_size = 2.*zo_detail_size
end

!p.multi=[0,2,2]

; Show the AX,AY value for these events
plot, AX(strksel) - aveAX, AY(strksel) - aveAY, PSYM=3, $
	BACK=clr_back, COLOR=clr_wht, /NODATA, $
        TITLE='Aspect X, Aspect Y: Zero-order Streak', $
        XTITLE=ax_name+' - '+STRING(aveAX,FORMAT='(F9.1)'), $
        YTITLE=ay_name+' - '+STRING(aveAY,FORMAT='(F9.1)'), $
	CHARSIZE=1.090
plots, AX(strksel) - aveAX, AY(strksel) - aveAY, $
		PSYM=3, COLOR=energy_colors(strksel), NOCLIP=0

; Plot the cross-streak LRF
plot, axxbins, axxcounts, PSYM=10, $
        TITLE='Zero-order Cross-streak Profile', $
        XTITLE=strk_name+' (pixels, bin = '+ $
		STRING(1.0/strk_exam_subbins, FORMAT='(F5.3)')+' pixel)', $
	XRANGE=zo_detail_size*[-1.,1.], XSTYLE=1, $
        YTITLE='Counts/bin', $
	CHARSIZE=1.090
; Plot the gaussian fit
oplot, axxbins, yfit, COLOR=clr_grn

; Plot the events vs time
vert_range = [MIN(AX(strksel) - aveAX),MAX(AX(strksel) - aveAX)]
if DETECTOR EQ 'ACIS-S' then vert_range = zo_detail_size*[-1.,1.]
plot, ftime(strksel), AX(strksel) - aveAX, PSYM=3, $
	BACK=clr_back, COLOR=clr_wht, /NODATA, $
        TITLE='t - Aspect X Plot for Zero-order Streak', $
        XTITLE='Time ('+time_unit+'s)', $
        YTITLE=ax_name+' - '+STRING(aveAX,FORMAT='(F9.1)'), $
	YRANGE=vert_range, YSTYLE=1, $
	CHARSIZE=1.090
plots, ftime(strksel), AX(strksel) - aveAX, $
		PSYM=3, COLOR=energy_colors(strksel), NOCLIP=0

vert_range = [MIN(AY(strksel) - aveAY),MAX(AY(strksel) - aveAY)]
if DETECTOR EQ 'ACIS-I' then vert_range = zo_detail_size*[-1.,1.]
plot, ftime(strksel), AY(strksel) - aveAY, PSYM=3, $
	BACK=clr_back, COLOR=clr_wht, /NODATA, $
        TITLE='t - Aspect Y Plot for Zero-order Streak', $
        XTITLE='Time ('+time_unit+'s)', $
        YTITLE=ay_name+' - '+STRING(aveAY,FORMAT='(F9.1)'), $
	YRANGE=vert_range, YSTYLE=1, $
	CHARSIZE=1.090
plots, ftime(strksel), AY(strksel) - aveAY, $
		PSYM=3, COLOR=energy_colors(strksel), NOCLIP=0

; Finish the .gif output
if NOT(KEYWORD_SET(ZBUFFER)) then wshow,iwind,iconic=0
image = tvrd()
tvlct, red, green, blue, /GET
gif_out = output_prefix+'_'+proc_method+'_streakzero.gif'
write_gif, out_dir+'/'+gif_out, image, red, green, blue

; Add .gif link
printf, out_unit, "</PRE>"
printf, out_unit, "<UL>"
printf, out_unit, '<LI><B><A href="'+gif_out+'">'+ $
	'Zero-order Streak Plots'+'</A></B>'
printf, out_unit, "</UL>"
printf, out_unit, "<PRE>"

if KEYWORD_SET(MOUSE) then begin
  print, ''
  print, '    !!! Click Mouse anywhere to Continue !!!'
  print, ''
  cursor, x, y, 3
end

;
; Output the zero-order and streak LRFs to isis format
; Streak arrays are: axxbins, axxcounts
;

; Offset the values if requested...
if KEYWORD_SET(CENTER_STREAK) then begin
  if n_elements(strk_fit_offset) GT 0 then begin
    axxbins = axxbins - strk_fit_offset
  end
end
if KEYWORD_SET(CENTER_FIT) then begin
  if n_elements(zo_fit_offset) GT 0 then begin
    axxbins = axxbins - zo_fit_offset
  end
end

; Offset the zero of axxbins to 100.0 and keep 
; only resulting bins in 1 to 199 (pixels) range.
axxbins = axxbins + 100.0
sel = where(axxbins GT 1.0 AND axxbins LT 199.0)
axxbins = axxbins(sel)
axxcounts = axxcounts(sel)

; Write out the ISIS format file
isis_file = output_prefix+'_'+proc_method+'_'+'strk_1d'+'_isis.dat' 

if NOT(KEYWORD_SET(SILENT)) then begin
  print, ''
  print, ' Creating ISIS format: '+isis_file+' ...'
end
printf, out_unit, ''
printf, out_unit, ' Creating ISIS format: <B><A href="'+isis_file+'">'+ $
	isis_file+'</A></B> ...'

bin_size = axxbins(1)-axxbins(0)
hak_write_isis, out_dir+'/'+isis_file, $
	axxbins - bin_size/2.0, axxbins + bin_size/2.0, $
	axxcounts, SQRT(axxcounts), $
	DATAFROM='obs_anal.pro', $
	OBJECT=OUTPUT_PREFIX, $
	INSTRUMENT=DETECTOR, GRATING=GRATING, EXPOSURE=interval_duration, $
	TG_M=0, TG_PART=0, TG_SRCID=1, XUNIT='Angstrom'

; . . . . . . . . . .
end ; of nstrk test
end ; of streak section

;
; Prepare to output the Zero-order LRF to isis format
; arrays are: zo_axxbins, zo_axxcounts
;

; Offset the values if requested...
if KEYWORD_SET(CENTER_STREAK) then begin
  if n_elements(strk_fit_offset) GT 0 then begin
    zo_axxbins = zo_axxbins - strk_fit_offset
  end
end
if KEYWORD_SET(CENTER_FIT) then begin
  if n_elements(zo_fit_offset) GT 0 then begin
    zo_axxbins = zo_axxbins - zo_fit_offset
  end
end

; Offset the zero of zo_axxbins to 100.0 and keep 
; only resulting bins in 1 to 199 (pixels) range.
zo_axxbins = zo_axxbins + 100.0
sel = where(zo_axxbins GT 1.0 AND zo_axxbins LT 199.0)
zo_axxbins = zo_axxbins(sel)
zo_axxcounts = zo_axxcounts(sel)

; Write out the ISIS format file
isis_file = output_prefix+'_'+proc_method+'_'+'zo_1d'+'_isis.dat' 

if NOT(KEYWORD_SET(SILENT)) then begin
  print, ''
  print, ' Creating ISIS format: '+isis_file+' ...'
end
printf, out_unit, ''
printf, out_unit, ' Creating ISIS format: <B><A href="'+isis_file+'">'+ $
	isis_file+'</A></B> ...'

bin_size = zo_axxbins(1)-zo_axxbins(0)
hak_write_isis, out_dir+'/'+isis_file, $
	zo_axxbins - bin_size/2.0, zo_axxbins + bin_size/2.0, $
	zo_axxcounts, SQRT(zo_axxcounts), $
	DATAFROM='obs_anal.pro', $
	OBJECT=OUTPUT_PREFIX, $
	INSTRUMENT=DETECTOR, GRATING=GRATING, EXPOSURE=interval_duration, $
	TG_M=0, TG_PART=0, TG_SRCID=1, XUNIT='Angstrom'
;
; Done with isis histogram output


; Adjust the average AX value by the fit-measured offsets
; if requested...
if KEYWORD_SET(CENTER_FIT) then begin
  if NOT(KEYWORD_SET(SILENT)) then begin
    print, ''
    print, '* Zero-order fit used to offset aveAX'
    print, ''
  end
  printf, out_unit, ''
  printf, out_unit, '* Zero-order fit used to offset aveAX'
  printf, out_unit, ''
  aveAX = aveAX + zo_fit_offset
end
if KEYWORD_SET(CENTER_STREAK) then begin
  if n_elements(strk_fit_offset) GT 0 then begin
    if NOT(KEYWORD_SET(SILENT)) then begin    print, ''
      print, ''
      print, '* Streak fit used to offset aveAX'
      print, ''
    end
    printf, out_unit, ''
    printf, out_unit, '* Streak fit used to offset aveAX'
    printf, out_unit, ''
    aveAX = aveAX + strk_fit_offset
  end else begin
    print, '* Streak fit not available - cannot CENTER_STREAK'
    print, ''
    printf, out_unit, '* Streak fit not available - cannot CENTER_STREAK'
    printf, out_unit, ''
  end
end

; Output the final zero-order AX,AY location
rpf_add_param, rpf, 'zo_loc_ax', aveAX, $
	ERROR = 0.0, UNIT='pixel'
rpf_add_param, rpf, 'zo_loc_ay', aveAY, $
	ERROR = 0.0, UNIT='pixel'

; end of Zero-order Spatial
; - - - - - - - - - - - - - - - - - - - - - - - - -


if NOT(KEYWORD_SET(SILENT)) then begin
  print, ' - - - - - - - - Detailed Examine Zero-order Spectral... - - - - - - -'
  print, ''
end
printf, out_unit, "</PRE>"
printf, out_unit, '<HR>'
printf, out_unit, '<H3>Detailed Examine Zero-order Spectral...</H3>'
printf, out_unit, "<PRE>"
printf, out_unit, ""

; Last thing to do with zero-order is
; output an isis-format PHA of the zero-order energy values
if got_energy then begin

  tg_part_str = 'Zero'

  ; Bin in nominal energy PI size bins
  lin_hist, Etouse(zosel), e_bin_ratio, bines, bincounts
  ; the bines are bin centers in keV ...
  ; convert to wavelength and have the binlams be the lower-lambda bin
  ; edge values
  binlams = hc/(bines + e_bin_ratio/2.0)
  binsort = SORT(binlams)
  binlams = binlams(binsort)
  bincounts = bincounts(binsort)

  ; Write out the ISIS format file
  isis_file = output_prefix+'_'+proc_method+'_'+tg_part_str+'_isis.dat' 

  if NOT(KEYWORD_SET(SILENT)) then begin
    print, ' Creating ISIS format: '+isis_file+' ...'
  end
  printf, out_unit, ' Creating ISIS format: <B><A href="'+isis_file+'">'+isis_file+'</A></B> ...'

  nbins = n_elements(binlams)

  hak_write_isis, out_dir+'/'+isis_file, $
	binlams(0:nbins-2), binlams(1:nbins-1), $
	bincounts(0:nbins-2), SQRT(bincounts(0:nbins-2)), $
	DATAFROM='obs_anal.pro', $
	OBJECT=OUTPUT_PREFIX, $
	INSTRUMENT=DETECTOR, GRATING=GRATING, EXPOSURE=interval_duration, $
	TG_M=0, TG_PART=0, TG_SRCID=1, XUNIT='Angstrom'

end


; end of detailed zero-order determine/examine
; - - - - - - - - - - - - - - - - - - - - - - - - - - - - -


; - - - - - End of processing if there is no grating! - - - -
if GRATING EQ 'NONE' then begin
  if NOT(KEYWORD_SET(SILENT)) then begin
    print, ''
    print, " GRATING = 'NONE' - end of processing."
  end
  printf, out_unit, ''
  printf, out_unit, " GRATING = 'NONE' - end of processing."
  ; OK, here's what we've been waiting for - one per program! 
  GOTO, ALL_FINISHED
end else begin
  ; and if there is a grating but a few zero-order counts
  ; then skip all the grating stuff here and go to level 1.5 check...
  if n_elements(zosel) LE 200 then begin
    ; Let folks know what happened (silent or not!)
    printf, out_unit, "* too few zero-order events, skip grating processing."
    print, "* too few zero-order events, skip grating processing."
    GOTO, Level_1a_check
  end
  ; if the zero-order FWHM is large skip over internal grating
  ; processing too:
  if zo_fwhm_pixels * pixel_size GT 2.00 then begin
    ; Let folks know what happened (silent or not!)
    printf, out_unit, "* Zero-order too wide, skip grating processing."
    print, "* Zero-order too wide, skip grating processing."
    GOTO, Level_1a_check
  end
end

; - - - - - - - - - - - - - - - - - - - - - - - - - - - - -


; .......................................
; Data and Parameters available at this stage:
;  filename, grating, evts, evts_tags, 
;  max_sel_energy, min_sel_energy, e_bin_ratio, 
;  ftime, tsort, delta_ts, tbinsize, tgapsize, interval_duration
;  zoregsize, zosel, aveXtouse, aveYtouse, xyshowtoo,
;  ASPECT: time_bin_size, fft_thresh, binT, binaveX, binaveY, binnave,
;          smaveX, smaveY, AX, AY, aveAX, aveAY
; .......................................

; - - - - - - - - - - ANGLES - - - - - - - 
; This section forms selections of the events by sign and grating.
; Angles in detector space can then be measured for the selected
; events.  Note that for CC mode events are assigned to HEG and
; MEG - hopefully ENERGY will be present to separate them.
;

if NOT(KEYWORD_SET(SILENT)) then begin
  print, ' - - - - - - - - - - - - Measure Grating Angle(s)... - - - - - - '
  print, ''
  print, '                    ==> MTA Monitor Task 5.5 <=='
  print, ''
end
printf, out_unit, "</PRE>"
printf, out_unit, '<HR>'
printf, out_unit, '<H3>Measure Grating Angle(s)...</H3>'
printf, out_unit, '<P align="center"><FONT COLOR="#00D000" SIZE=+1>'
printf, out_unit, ' ==> MTA Monitor Task 5.5 <== '
printf, out_unit, '</FONT></P>'
printf, out_unit, '<PRE>'

if NOT(KEYWORD_SET(SILENT)) then begin
  print, ' Selecting events in the grating parts...'
  print, '   cd_width = '+STRCOMPRESS(cd_width)+' mm'
  print, '   cd_offset = '+STRCOMPRESS(cd_offset)+' mm'
  print, ''
end
printf, out_unit, ' Selecting events in the grating parts...'
printf, out_unit, '   cd_width = '+STRCOMPRESS(cd_width)+' mm'
printf, out_unit, '   cd_offset = '+STRCOMPRESS(cd_offset)+' mm'
printf, out_unit, ''

; Go through the Quadrants...
if GRATING EQ 'LETG' then begin
  ; setup three plots
  !p.multi=[0,1,3]
  ; set quadrants
  iqstart = 6
  iqstop = 8
end else begin
  ; set quadrants
  iqstart = 0
  iqstop = 5
  ; setup six plots
  !p.multi=[0,2,3]
end

qnames = ['HEG_minus', 'MEG_plus', 'MEG_minus', 'HEG_plus', $
		'HEG_all', 'MEG_all', $
		'LEG_minus', 'LEG_plus', 'LEG_all']

; Known/expected flight angles
q_flight_angles = [ang_heg, ang_meg, ang_meg, ang_heg, $
		ang_heg, ang_meg, ang_leg, ang_leg, ang_leg]

; array for measured angles
qangles = FLTARR(9)

for iq=iqstart,iqstop do begin
  ; Select the events in the given spectrum based on being in the
  ; correct quadrant and within the cross-dispersion width

  ; Calculate the Y value on the dispersion axis for all the events
  ; This is in pixel units, the cd parameters are in mm, however.
  Yaxis = aveAY + (cd_offset/pixel_size) + $
		(AX - aveAX)*TAN(q_flight_angles(iq)*!DTOR)
  CASE iq OF
    0: begin
         if cc_mode then begin
           sel = where(AX LT aveAX - zoregsize/2.0)
         end else begin
           sel = where(AX LT aveAX - zoregsize/2.0 AND $
		(AY GT (aveAY+(cd_offset/pixel_size))) AND $
		ABS(AY - Yaxis ) LT (0.5*cd_width/pixel_size) )
         end
         hegmsel = sel
       end
    1: begin
         if cc_mode then begin
           sel = where(AX GT aveAX + zoregsize/2.0)
         end else begin
           sel = where(AX GT aveAX + zoregsize/2.0 AND $
		(AY GT (aveAY+(cd_offset/pixel_size))) AND $
		ABS(AY - Yaxis ) LT (0.5*cd_width/pixel_size) )
         end
         megpsel = sel
       end
    2: begin
         if cc_mode then begin
           sel = where(AX LT aveAX - zoregsize/2.0)
         end else begin
           sel = where(AX LT aveAX - zoregsize/2.0 AND $
		(AY LT (aveAY+(cd_offset/pixel_size))) AND $
		ABS(AY - Yaxis ) LT (0.5*cd_width/pixel_size) )
         end
         megmsel = sel
       end
    3: begin
         if cc_mode then begin
           sel = where(AX GT aveAX + zoregsize/2.0)
         end else begin
           sel = where(AX GT aveAX + zoregsize/2.0 AND $
		(AY LT (aveAY+(cd_offset/pixel_size))) AND $
		ABS(AY - Yaxis ) LT (0.5*cd_width/pixel_size) )
         end
         hegpsel = sel
       end
    4: begin
         sel = [hegmsel,hegpsel]
         hegallsel = sel
       end
    5: begin
         sel = [megmsel,megpsel]
         megallsel = sel
       end
    6: begin
         if cc_mode then begin
           sel = where(AX LT aveAX - zoregsize/2.0)
         end else begin
           sel = where(AX LT aveAX - zoregsize/2.0 AND $
		ABS(AY - Yaxis ) LT (0.5*cd_width/pixel_size) )
         end
         legmsel = sel
       end
    7: begin
         if cc_mode then begin
           sel = where(AX GT aveAX + zoregsize/2.0)
         end else begin
           sel = where(AX GT aveAX + zoregsize/2.0 AND $
		ABS(AY - Yaxis ) LT (0.5*cd_width/pixel_size) )
         end
         legpsel = sel
       end
    8: begin
         sel = [legmsel,legpsel]
         legallsel = sel
       end
  ELSE: begin
        end
  ENDCASE

  if NOT(cc_mode) then begin
    ; Select the Quadrant Events
    ; Use AX, and AY
    qxs = AX(sel)
    qys = AY(sel)
    ; and keep the ecpected Yaxis values
    Yaxis = Yaxis(sel)
    ; Find two representative points
    xminpt = where(MIN(qxs) EQ qxs)
    xminpt = xminpt(0)
    xmaxpt = where(MAX(qxs) EQ qxs)
    xmaxpt = xmaxpt(0)

    plot, qxs, qys - Yaxis, PSYM=3, $
	XRANGE=[qxs(xminpt), qxs(xmaxpt)], XSTYLE=1, $
	YRANGE=[MIN(qys - Yaxis), MAX(qys-Yaxis)], YSTYLE=1, $
	BACK=clr_back, COLOR=clr_wht, /NODATA, $
	TITLE = 'Measuring Angle for '+qnames(iq)+' Events', $
        XTITLE=ax_name+' (pixels)', $
        YTITLE=ay_name+' - Y_axis(X) (pixels)', $
	CHARSIZE=1.51
    plots, qxs, qys - Yaxis, PSYM=3, COLOR=energy_colors(sel), NOCLIP=0

    ; Try to fit these...!?!
    fit_result = linfit(qxs, qys)
    oplot, [qxs(xminpt), qxs(xmaxpt)], $
	fit_result(0)+fit_result(1)*[qxs(xminpt), qxs(xmaxpt)] - $
		[Yaxis(xminpt), Yaxis(xmaxpt)], $
		COLOR=clr_blu

    ; Report the slope
    slope = fit_result(1)
    angle = ATAN(slope)/!DTOR
    qangles(iq) = angle
    if NOT(KEYWORD_SET(SILENT)) then begin
      print, ' '+qnames(iq)+' number of events = '+ $
		STRCOMPRESS(n_elements(qxs))
      print, ' '+qnames(iq)+' slope is '+ $
	STRCOMPRESS(slope)+', --> '+ $
	STRCOMPRESS(angle)+' degrees on detector'
    end
    printf, out_unit, ' '+qnames(iq)+' number of events = '+ $
		STRCOMPRESS(n_elements(qxs))
    printf, out_unit, ' '+qnames(iq)+' slope is '+ $
	STRCOMPRESS(slope)+', --> '+ $
	STRCOMPRESS(angle)+' degrees on detector'

    ; Put the number of events and angle into the output parameter file
    rpf_add_param, rpf, STRLOWCASE(qnames(iq)+'_events'), $
	n_elements(qxs), ERROR = 0.0, UNIT=''
    rpf_add_param, rpf, STRLOWCASE(qnames(iq)+'_angle'), $
	angle, ERROR = 0.0, UNIT='degree'

  end
end

if cc_mode then begin
  if NOT(KEYWORD_SET(SILENT)) then begin
    print, ''
    print, " CC mode data: can't measure the angles."
    print, ''
  end
  printf, out_unit, ''
  printf, out_unit, " CC mode data: can't measure the angles."
  printf, out_unit, ''
end else begin
  if NOT(KEYWORD_SET(SILENT)) then print, ''
  printf, out_unit, ''

  ; Finish the .gif output
  if NOT(KEYWORD_SET(ZBUFFER)) then wshow,iwind,iconic=0
  image = tvrd()
  tvlct, red, green, blue, /GET
  gif_out = output_prefix+'_'+proc_method+'_angles.gif'
  write_gif, out_dir+'/'+gif_out, image, red, green, blue

  ; Add .gif link
  printf, out_unit, "</PRE>"
  printf, out_unit, "<UL>"
  printf, out_unit, '<LI><B><A href="'+gif_out+'">'+ $
	'Grating Angle Analysis Plots'+'</A></B>'
  printf, out_unit, "</UL>"
  printf, out_unit, "<PRE>"

  if KEYWORD_SET(MOUSE) then begin
    print, '    !!! Click Mouse anywhere to Continue !!!'
    print, ''
    cursor, x, y, 3
  end
end

; end of selection and angles
; - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

; .......................................
; Data and Parameters available at this stage:
;  filename, grating, evts, evts_tags, max_sel_energy, min_sel_energy, e_bin_ratio, 
;  ftime, tsort, delta_ts, tbinsize, tgapsize, interval_duration
;  zoregsize, zosel, aveXtouse, aveYtouse,
;  ASPECT: time_bin_size, fft_thresh, binT, binaveX, binaveY, binnave,
;          smaveX, smaveY, AX, AY, aveAX, aveAY
;  qnames, qangles, [heg|meg][m|p|all]sel
; .......................................

; - - - - - - - - - - Crude Dispersed Spectra w/Pileup Estimate - - - - - - - 
;
; Histograms of the selections are made along the AX direction
; and convolved with a 3 pixel box-car summer, [1.,1.,1.],
; to evalutate the amount of pileup present in the spectra.

; Parameters:
; Rowland spacings
if KEYWORD_SET(XRCF_ROWLAND) then begin
  if GRATING EQ 'HETG' then begin
    hetg_rs = hetg_rs_xrcf
  end else begin
    hetg_rs = letg_rs_xrcf
  end
end else begin
  if GRATING EQ 'HETG' then begin
    hetg_rs = hetg_rs_flight
  end else begin
    hetg_rs = letg_rs_flight
  end
end

ge_min = 0.4 ; keV
; Go a bit lower if LETG and ACIS:
if GRATING EQ 'LETG' AND (STRPOS(DETECTOR,'ACIS') GE 0) then ge_min=0.20
; Go even lower if LETG and HRC:
if GRATING EQ 'LETG' AND (STRPOS(DETECTOR,'HRC') GE 0) then ge_min=0.05
ge_max = 10.0 ; keV

; Define order-selection bands in PHA-grating_energy space
; Open up to 0.50 because spatial selection separates HEG and MEG;
; higher orders are at higher energy and the 1.50 should filter them...
; order_sel_accuracy = 0.50  ; PHA can be from 0.50 to 1.5 of grating E

; Bin size: E_n+1/E_n at 1 keV:
; This has E/dE = 10000. at 1 keV, useful for HEG and MEG point
; sources with narrow lines
ge_bin_ratio = 1.0001
; If the zero-order FWHM is larger than 50 microns FWHM, then
; increase this bin size:
ge_bin_ratio = ge_bin_ratio ^ ( FIX(zo_fwhm_pixels*pixel_size/0.05) > 1)
if GRATING EQ 'LETG' then ge_bin_ratio = ge_bin_ratio^6  ; 6x coarser

if NOT(KEYWORD_SET(SILENT)) then begin
  print, ' - - - - - - - - - - - - Crude Dispersed Spectra w/Pileup Estimate... - - - - - - '
  print, ''
end
printf, out_unit, "</PRE>"
printf, out_unit, '<HR>'
printf, out_unit, '<H3>Crude Dispersed Spectra w/Pileup Estimate...</H3>'
printf, out_unit, "<PRE>"
printf, out_unit, ""

if NOT(KEYWORD_SET(SILENT)) then begin
  print, ''
  print, ' Rowland spacing used is '+ $
	STRING(hetg_rs,FORMAT='(F8.2)')+' mm'
  print, ''
end

printf, out_unit, ''
printf, out_unit, ' Rowland spacing used is '+ $
	STRING(hetg_rs,FORMAT='(F8.2)')+' mm'
printf, out_unit, ''

; For LETG use the meg arrays and calculations by setting
;  megm=legm, and p_meg = p_leg ...
; Provide a string to flag this:
megleg = 'meg'
if GRATING EQ 'LETG' then begin
  p_meg = p_leg
  megpsel = legpsel
  megmsel = legmsel
  megleg = 'leg'
  meg_zo_offset = leg_zo_offset
end

if NOT(KEYWORD_SET(SILENT)) then begin
  print, ' MEG Zero-order offset: ', meg_zo_offset, ' pixels'
end
printf, out_unit, ' MEG Zero-order offset: ', meg_zo_offset, ' pixels'

; Dispersion distance using AX, AY
d_megp = pixel_size*SQRT( (AX(megpsel) - (aveAX+meg_zo_offset))^2 + $
	(AY(megpsel) - (aveAY+cd_offset/pixel_size))^2)
d_megm = pixel_size*SQRT( (AX(megmsel) - (aveAX+meg_zo_offset))^2 + $
	(AY(megmsel) - (aveAY+cd_offset/pixel_size))^2)
if GRATING EQ 'HETG' then begin
  if NOT(KEYWORD_SET(SILENT)) then begin
    print, ' HEG Zero-order offset: ', heg_zo_offset, ' pixels'
  end
  printf, out_unit, ' HEG Zero-order offset: ', heg_zo_offset, ' pixels'
  d_hegp = pixel_size*SQRT( (AX(hegpsel) - (aveAX+heg_zo_offset))^2 + $
	(AY(hegpsel) - (aveAY+cd_offset/pixel_size))^2)
  d_hegm = pixel_size*SQRT( (AX(hegmsel) - (aveAX+heg_zo_offset))^2 + $
	(AY(hegmsel) - (aveAY+cd_offset/pixel_size))^2)
end
print, ''
printf, out_unit, ''

; Modify these distances if it is CC mode data with the HETG
if cc_mode and (GRATING EQ 'HETG') then begin
  d_megp = d_megp / COS(ang_meg*!DTOR)
  d_megm = d_megm / COS(ang_meg*!DTOR)
  d_hegp = d_hegp / COS(ang_heg*!DTOR)
  d_hegm = d_hegm / COS(ang_heg*!DTOR)
end

; Simple diffraction equation for 1st order
e_megp = hc/(p_meg*d_megp/hetg_rs)
e_megm = hc/(p_meg*d_megm/hetg_rs)
if GRATING EQ 'HETG' then begin
  e_hegp = hc/(p_heg*d_hegp/hetg_rs)
  e_hegm = hc/(p_heg*d_hegm/hetg_rs)
end

; Select events whose diffracted energy matches PHA energy
; if ENERGY is available AND it is not HRC!
if (got_energy) AND $
	NOT(STRPOS(DETECTOR,'HRC') GE 0) then begin
  if NOT(KEYWORD_SET(SILENT)) then begin
    print, ' Use ACIS ENERGY for Order selection...'
  end
  printf, out_unit, ' Use ACIS ENERGY for Order selection...'
  ; Create plots here to show order selection...
  !p.multi = [0,1,2]  ; leg/meg +/-
  if GRATING EQ 'HETG' then !p.multi = [0,1,4]

  ; Will overplot the selection criteria lines - make up the data points
  order_plt_es = 12.0*(indgen(101)/100.0) ; 0-12 keV

  ; Set the order range to plot
  order_plt_range = [0.0, 2.5]

  m1_megm = where(approx_equal(Etouse(megmsel)/e_megm,1.0, $
	order_sel_accuracy), nfound)
  ; Catch no events here, e.g. due to MEG-HEG arm flip?!?
  if nfound EQ 0 then begin
    print, ' * No events agree with MEG -1 order selection;'
    print, '   HETG arms may be interchanged or ACIS energy invalid.'
    print, '   Keeping all candidate events anyway.'
    printf, out_unit, ' * No events agree with MEG -1 order selection;'
    printf, out_unit, '   HETG arms may be interchanged or ACIS energy invalid.'
    printf, out_unit, '   Keeping all candidate events anyway.'
    m1_megm = LINDGEN(n_elements(megmsel))
  end
  plot_oi, e_megm(m1_megm), Etouse(megmsel(m1_megm))/e_megm(m1_megm), PSYM=3, $
	XSTYLE=1, XRANGE=[ge_min, ge_max], $
	YSTYLE=1, YRANGE=order_plt_range, $
	BACK=clr_back, COLOR=clr_wht, /NODATA, $
	TITLE = 'Grating-E - ACIS-E : Order Selection Plots', $
	XTITLE=STRUPCASE(megleg)+'-minus Energy (keV)', $
	YTITLE='ACIS Energy / Grating Energy', $
	CHARSIZE=1.51
  oplot, order_plt_es, COLOR=clr_blu, $
	(1.0+order_sel_accuracy)+0.0*order_plt_es, LINESTYLE=2
  oplot, order_plt_es, COLOR=clr_blu, $
	(1.0)+0.0*order_plt_es
  oplot, order_plt_es, COLOR=clr_blu, $
	(1.0-order_sel_accuracy)+0.0*order_plt_es, LINESTYLE=2
  ;plots, e_megm(m1_megm), Etouse(megmsel(m1_megm))/e_megm(m1_megm), PSYM=3, $
  ;	COLOR=energy_colors(megmsel(m1_megm)), NOCLIP=0
  plots, e_megm, Etouse(megmsel)/e_megm, PSYM=3, $
	COLOR=energy_colors(megmsel), NOCLIP=0
  if GRATING EQ 'HETG' AND DETECTOR EQ 'ACIS-S' then begin
    ; show and label gaps and chips
    ; MEG minus
    gap_es = [0.473, 0.852, 4.26]
    for ig=0,n_elements(gap_es)-1 do begin
      oplot, gap_es(ig)*[1.0,1.0], order_plt_range, COLOR=clr_blu, LINESTYLE=1
    end
    xyouts, 0.42, TOTAL(order_plt_range*[0.2,0.8]), 'S0'
    xyouts, 0.60, TOTAL(order_plt_range*[0.2,0.8]), 'S1'
    xyouts, 1.4, TOTAL(order_plt_range*[0.2,0.8]), 'S2'
    xyouts, 5.5, TOTAL(order_plt_range*[0.2,0.8]), 'S3'
  end

  m1_megp = where(approx_equal(Etouse(megpsel)/e_megp,1.0, $
	order_sel_accuracy), nfound)
  ; Catch no events here, e.g. due to MEG-HEG arm flip?!?
  if nfound EQ 0 then begin
    print, ' * No events agree with MEG +1 order selection;'
    print, '   HETG arms may be interchanged or ACIS energy invalid.'
    print, '   Keeping all candidate events anyway.'
    printf, out_unit, ' * No events agree with MEG +1 order selection;'
    printf, out_unit, '   HETG arms may be interchanged or ACIS energy invalid.'
    printf, out_unit, '   Keeping all candidate events anyway.'
    m1_megp = LINDGEN(n_elements(megpsel))
  end
  if n_elements(gain_factors) EQ 10 then begin
    gain_fact_title = 'Gain factors (S0-S5): '
    for iccd=4,9 do gain_fact_title = gain_fact_title + $
	STRING(gain_factors(iccd),FORMAT='(F6.2)')
  end else begin
    gain_fact_title = '(No additional gain correction applied to ENERGY)'
  end
  plot_oi, e_megp(m1_megp), Etouse(megpsel(m1_megp))/e_megp(m1_megp), PSYM=3, $
	XSTYLE=1, XRANGE=[ge_min, ge_max], $
	YSTYLE=1, YRANGE=order_plt_range, $
	BACK=clr_back, COLOR=clr_wht, /NODATA, $
	TITLE=gain_fact_title, $
	XTITLE=STRUPCASE(megleg)+'-plus Energy (keV)', $
	YTITLE='ACIS Energy / Grating Energy', $
	CHARSIZE=1.51
  oplot, order_plt_es, COLOR=clr_blu, $
	(1.0+order_sel_accuracy)+0.0*order_plt_es, LINESTYLE=2
  oplot, order_plt_es, COLOR=clr_blu, $
	(1.0)+0.0*order_plt_es
  oplot, order_plt_es, COLOR=clr_blu, $
	(1.0-order_sel_accuracy)+0.0*order_plt_es, LINESTYLE=2
  ;plots, e_megp(m1_megp), Etouse(megpsel(m1_megp))/e_megp(m1_megp), PSYM=3, $
  ;	COLOR=energy_colors(megpsel(m1_megp)), NOCLIP=0
  plots, e_megp, Etouse(megpsel)/e_megp, PSYM=3, $
	COLOR=energy_colors(megpsel), NOCLIP=0
  if GRATING EQ 'HETG' AND DETECTOR EQ 'ACIS-S' then begin
    ; show and label gaps and chips
    ; MEG plus
    gap_es = [0.609, 1.421]
    for ig=0,n_elements(gap_es)-1 do begin
      oplot, gap_es(ig)*[1.0,1.0], order_plt_range, COLOR=clr_blu, LINESTYLE=1
    end
    xyouts, 0.47, TOTAL(order_plt_range*[0.2,0.8]), 'S5'
    xyouts, 0.85, TOTAL(order_plt_range*[0.2,0.8]), 'S4'
    xyouts, 2.9, TOTAL(order_plt_range*[0.2,0.8]), 'S3'
  end

  if NOT(KEYWORD_SET(SILENT)) then begin
    print, ' '+STRUPCASE(megleg)+' minus order selection keeps '+ $
	STRCOMPRESS((100.0*n_elements(m1_megm))/n_elements(megmsel))+' %'+$
	',  '+STRCOMPRESS(n_elements(m1_megm))+' events'

    print, ' '+STRUPCASE(megleg)+' plus  order selection keeps '+ $
	STRCOMPRESS((100.0*n_elements(m1_megp))/n_elements(megpsel))+' %'+$
	',  '+STRCOMPRESS(n_elements(m1_megp))+' events'
  end
  printf, out_unit, ' '+STRUPCASE(megleg)+' minus order selection keeps '+ $
	STRCOMPRESS((100.0*n_elements(m1_megm))/n_elements(megmsel))+' %'+$
	',  '+STRCOMPRESS(n_elements(m1_megm))+' events'

  printf, out_unit, ' '+STRUPCASE(megleg)+' plus  order selection keeps '+ $
	STRCOMPRESS((100.0*n_elements(m1_megp))/n_elements(megpsel))+' %'+$
	',  '+STRCOMPRESS(n_elements(m1_megp))+' events'

  if GRATING EQ 'HETG' then begin

    m1_hegm = where(approx_equal(Etouse(hegmsel)/e_hegm,1.0, $
	order_sel_accuracy), nfound)
    ; Catch no events here, e.g. due to MEG-HEG arm flip?!?
    if nfound EQ 0 then begin
      print, ' * No events agree with HEG -1 order selection;'
      print, '   HETG arms may be interchanged or ACIS energy invalid.'
      print, '   Keeping all candidate events anyway.'
      printf, out_unit, ' * No events agree with HEG -1 order selection;'
      printf, out_unit, '   HETG arms may be interchanged or ACIS energy invalid.'
      printf, out_unit, '   Keeping all candidate events anyway.'
      m1_hegm = LINDGEN(n_elements(hegmsel))
    end
    plot_oi, e_hegm(m1_hegm), Etouse(hegmsel(m1_hegm))/e_hegm(m1_hegm), $
	PSYM=3, $
	XSTYLE=1, XRANGE=[ge_min, ge_max], $
	YSTYLE=1, YRANGE=order_plt_range, $
	BACK=clr_back, COLOR=clr_wht, /NODATA, $
	XTITLE='HEG-minus Energy (keV)', $
	YTITLE='ACIS Energy / Grating Energy', $
	CHARSIZE=1.51
    oplot, order_plt_es, COLOR=clr_blu, $
	(1.0+order_sel_accuracy)+0.0*order_plt_es, LINESTYLE=2
    oplot, order_plt_es, COLOR=clr_blu, $
	(1.0)+0.0*order_plt_es
    oplot, order_plt_es, COLOR=clr_blu, $
	(1.0-order_sel_accuracy)+0.0*order_plt_es, LINESTYLE=2
    ;plots, e_hegm(m1_hegm), Etouse(hegmsel(m1_hegm))/e_hegm(m1_hegm), PSYM=3, $
    ;	COLOR=energy_colors(hegmsel(m1_hegm)), NOCLIP=0
    plots, e_hegm, Etouse(hegmsel)/e_hegm, PSYM=3, $
	COLOR=energy_colors(hegmsel), NOCLIP=0
    if GRATING EQ 'HETG' AND DETECTOR EQ 'ACIS-S' then begin
      ; show and label gaps and chips
      ; HEG minus
      gap_es = [0.657, 0.946, 1.702]
      for ig=0,n_elements(gap_es)-1 do begin
        oplot, gap_es(ig)*[1.0,1.0], order_plt_range, COLOR=clr_blu, LINESTYLE=1
      end
      xyouts, 0.63, TOTAL(order_plt_range*[0.2,0.8]), 'S0'
      xyouts, 1.25, TOTAL(order_plt_range*[0.2,0.8]), 'S1'
      xyouts, 3.1, TOTAL(order_plt_range*[0.2,0.8]), 'S2'
    end
    m1_hegp = where(approx_equal(Etouse(hegpsel)/e_hegp,1.0, $
	order_sel_accuracy), nfound)
    ; Catch no events here, e.g. due to MEG-HEG arm flip?!?
    if nfound EQ 0 then begin
      print, ' * No events agree with HEG +1 order selection;'
      print, '   HETG arms may be interchanged or ACIS energy invalid.'
      print, '   Keeping all candidate events anyway.'
      printf, out_unit, ' * No events agree with HEG +1 order selection;'
      printf, out_unit, '   HETG arms may be interchanged or ACIS energy invalid.'
      printf, out_unit, '   Keeping all candidate events anyway.'
      m1_hegp = LINDGEN(n_elements(hegmsel))
    end
    plot_oi, e_hegp(m1_hegp), Etouse(hegpsel(m1_hegp))/e_hegp(m1_hegp), $
	PSYM=3, $
	XSTYLE=1, XRANGE=[ge_min, ge_max], $
	YSTYLE=1, YRANGE=order_plt_range, $
	BACK=clr_back, COLOR=clr_wht, /NODATA, $
	XTITLE='HEG-plus Energy (keV)', $
	YTITLE='ACIS Energy / Grating Energy', $
	CHARSIZE=1.51
    oplot, order_plt_es, COLOR=clr_blu, $
	(1.0+order_sel_accuracy)+0.0*order_plt_es, LINESTYLE=2
    oplot, order_plt_es, COLOR=clr_blu, $
	(1.0)+0.0*order_plt_es
    oplot, order_plt_es, COLOR=clr_blu, $
	(1.0-order_sel_accuracy)+0.0*order_plt_es, LINESTYLE=2
    ;plots, e_hegp(m1_hegp), Etouse(hegpsel(m1_hegp))/e_hegp(m1_hegp), PSYM=3, $
    ;	COLOR=energy_colors(hegpsel(m1_hegp)), NOCLIP=0
    plots, e_hegp, Etouse(hegpsel)/e_hegp, PSYM=3, $
	COLOR=energy_colors(hegpsel), NOCLIP=0
    if GRATING EQ 'HETG' AND DETECTOR EQ 'ACIS-S' then begin
      ; show and label gaps and chips
      ; HEG plus
      gap_es = [0.777, 1.216, 2.840]
      for ig=0,n_elements(gap_es)-1 do begin
        oplot, gap_es(ig)*[1.0,1.0], order_plt_range, COLOR=clr_blu, LINESTYLE=1
      end
      xyouts, 0.65, TOTAL(order_plt_range*[0.2,0.8]), 'S5'
      xyouts, 1.5, TOTAL(order_plt_range*[0.2,0.8]), 'S4'
      xyouts, 4.3, TOTAL(order_plt_range*[0.2,0.8]), 'S3'
    end

    if NOT(KEYWORD_SET(SILENT)) then begin
      print, ' HEG minus order selection keeps '+ $
	STRCOMPRESS((100.0*n_elements(m1_hegm))/n_elements(hegmsel))+' %'+$
	',  '+STRCOMPRESS(n_elements(m1_hegm))+' events'

      print, ' HEG plus  order selection keeps '+ $
	STRCOMPRESS((100.0*n_elements(m1_hegp))/n_elements(hegpsel))+' %'+$
	',  '+STRCOMPRESS(n_elements(m1_hegp))+' events'
    end
    printf, out_unit, ' HEG minus order selection keeps '+ $
	STRCOMPRESS((100.0*n_elements(m1_hegm))/n_elements(hegmsel))+' %'+$
	',  '+STRCOMPRESS(n_elements(m1_hegm))+' events'

    printf, out_unit, ' HEG plus  order selection keeps '+ $
	STRCOMPRESS((100.0*n_elements(m1_hegp))/n_elements(hegpsel))+' %'+$
	',  '+STRCOMPRESS(n_elements(m1_hegp))+' events'

  end
  if NOT(KEYWORD_SET(SILENT)) then print, ''
  printf, out_unit, ''

  ; Finish the .gif output
  if NOT(KEYWORD_SET(ZBUFFER)) then wshow,iwind,iconic=0
  image = tvrd()
  tvlct, red, green, blue, /GET
  gif_out = output_prefix+'_'+proc_method+'_orderselect.gif'
  write_gif, out_dir+'/'+gif_out, image, red, green, blue

  ; Add .gif link
  printf, out_unit, "</PRE>"
  printf, out_unit, "<UL>"
  printf, out_unit, '<LI><B><A href="'+gif_out+'">'+ $
	'Order Selection Plots'+'</A></B>'
  printf, out_unit, "</UL>"
  printf, out_unit, "<PRE>"

  if KEYWORD_SET(MOUSE) then begin
    print, '    !!! Click Mouse anywhere to Continue !!!'
    print, ''
    cursor, x, y, 3
  end

  em1_megp = e_megp(m1_megp)
  em1_megm = e_megm(m1_megm)
  if GRATING EQ 'HETG' then begin
    em1_hegp = e_hegp(m1_hegp)
    em1_hegm = e_hegm(m1_hegm)
  end
end else begin
  ; No ENERGY, just keep em all...
  em1_megp = e_megp
  em1_megm = e_megm
  if GRATING EQ 'HETG' then begin
    em1_hegp = e_hegp
    em1_hegm = e_hegm
  end
  if NOT(KEYWORD_SET(SILENT)) then begin
    print, ' ACIS ENERGY not available: keeping all orders'
    print, ''
  end
  printf, out_unit, ' ACIS ENERGY not available: keeping all orders'
  printf, out_unit, ''
end

;
; Pileup plots for ACIS readout
;
if STRPOS(DETECTOR, 'ACIS') GE 0 then begin
  ; Do the plots in the order of the Order Selection Plots
  ; just created: MEGm, MEGp, HEGm, HEGp
  ; Keep !p.multi the same

  if NOT(KEYWORD_SET(SILENT)) then begin
    print, ''
    print, ' Estimating pileup level in dispersed spectra...'
  end
  printf, out_unit, ''
  printf, out_unit, ' Estimating pileup level in dispersed spectra...'

  ; Sum over three pixels
  kernel = [1.,1.,1.]

  lin_hist, AX(megmsel), 1.0, megmbins, megmcounts
  bin3counts = CONVOL(megmcounts, kernel)
  if NOT(KEYWORD_SET(SILENT)) then begin
    print, STRUPCASE(megleg)+'-minus Max rate: ' + $
	STRING(MAX(bin3counts)/expno_num_all) + ' per frame'
  end
  printf, out_unit, STRUPCASE(megleg)+'-minus Max rate: ' + $
	STRING(MAX(bin3counts)/expno_num_all) + ' per frame'
  plot_io, megmbins, bin3counts, PSYM=10, $
	XSTYLE=1, /NODATA, $
	YSTYLE=1, YRANGE=[1.0,10.0*expno_num_all], $
	BACK=clr_back, COLOR=clr_wht, $
	TITLE = 'Pileup Plots (dashed line = 0.1/frame)', $
	XTITLE=STRUPCASE(megleg)+'-minus '+ax_name+' (pixels)', $
	YTITLE='Counts (3-pixel-sum)', $
	CHARSIZE=1.51
  oplot, [0.,10000.], [1.,1.]*expno_num_all, COLOR=clr_red
  oplot, [0.,10000.], [1.,1.]*0.1*expno_num_all, LINESTYLE=2, COLOR=clr_red
  oplot, [0.,10000.], [1.,1.]*0.01*expno_num_all, LINESTYLE=1, COLOR=clr_red
  oplot, megmbins, bin3counts, PSYM=10, COLOR=clr_yel

  lin_hist, AX(megpsel), 1.0, megpbins, megpcounts
  bin3counts = CONVOL(megpcounts, kernel)
  if NOT(KEYWORD_SET(SILENT)) then begin
    print, STRUPCASE(megleg)+'-plus Max rate: ' + $
	STRING(MAX(bin3counts)/expno_num_all) + ' per frame'
  end
  printf, out_unit, STRUPCASE(megleg)+'-plus Max rate: ' + $
	STRING(MAX(bin3counts)/expno_num_all) + ' per frame'
  plot_io, megpbins, bin3counts, PSYM=10, $
	XSTYLE=1, /NODATA, $
	YSTYLE=1, YRANGE=[1.0,10.0*expno_num_all], $
	BACK=clr_back, COLOR=clr_wht, $
	XTITLE=STRUPCASE(megleg)+'-plus '+ax_name+' (pixels)', $
	YTITLE='Counts (3-pixel-sum)', $
	CHARSIZE=1.51
  oplot, [0.,10000.], [1.,1.]*expno_num_all, COLOR=clr_red
  oplot, [0.,10000.], [1.,1.]*0.1*expno_num_all, LINESTYLE=2, COLOR=clr_red
  oplot, [0.,10000.], [1.,1.]*0.01*expno_num_all, LINESTYLE=1, COLOR=clr_red
  oplot, megpbins, bin3counts, PSYM=10, COLOR=clr_yel

  if GRATING EQ 'HETG' then begin
  ; - - -
  lin_hist, AX(hegmsel), 1.0, hegmbins, hegmcounts
  bin3counts = CONVOL(hegmcounts, kernel)
  if NOT(KEYWORD_SET(SILENT)) then begin
    print, 'HEG'+'-minus Max rate: ' + $
	STRING(MAX(bin3counts)/expno_num_all) + ' per frame'
  end
  printf, out_unit, 'HEG'+'-minus Max rate: ' + $
	STRING(MAX(bin3counts)/expno_num_all) + ' per frame'
  plot_io, hegmbins, bin3counts, PSYM=10, $
	XSTYLE=1, /NODATA, $
	YSTYLE=1, YRANGE=[1.0,10.0*expno_num_all], $
	BACK=clr_back, COLOR=clr_wht, $
	TITLE = 'Pileup Rate Plots', $
	XTITLE='HEG'+'-minus '+ax_name+' (pixels)', $
	YTITLE='Counts (3-pixel-sum)', $
	CHARSIZE=1.51
  oplot, [0.,10000.], [1.,1.]*expno_num_all, COLOR=clr_red
  oplot, [0.,10000.], [1.,1.]*0.1*expno_num_all, LINESTYLE=2, COLOR=clr_red
  oplot, [0.,10000.], [1.,1.]*0.01*expno_num_all, LINESTYLE=1, COLOR=clr_red
  oplot, hegmbins, bin3counts, PSYM=10, COLOR=clr_blu

  lin_hist, AX(hegpsel), 1.0, hegpbins, hegpcounts
  bin3counts = CONVOL(hegpcounts, kernel)
  if NOT(KEYWORD_SET(SILENT)) then begin
    print, 'HEG'+'-plus Max rate: ' + $
	STRING(MAX(bin3counts)/expno_num_all) + ' per frame'
  end
  printf, out_unit, 'HEG'+'-plus Max rate: ' + $
	STRING(MAX(bin3counts)/expno_num_all) + ' per frame'
  plot_io, hegpbins, bin3counts, PSYM=10, $
	XSTYLE=1, /NODATA, $
	YSTYLE=1, YRANGE=[1.0,10.0*expno_num_all], $
	BACK=clr_back, COLOR=clr_wht, $
	XTITLE='HEG'+'-plus '+ax_name+' (pixels)', $
	YTITLE='Counts (3-pixel-sum)', $
	CHARSIZE=1.51
  oplot, [0.,10000.], [1.,1.]*expno_num_all, COLOR=clr_red
  oplot, [0.,10000.], [1.,1.]*0.1*expno_num_all, LINESTYLE=2, COLOR=clr_red
  oplot, [0.,10000.], [1.,1.]*0.01*expno_num_all, LINESTYLE=1, COLOR=clr_red
  oplot, hegpbins, bin3counts, PSYM=10, COLOR=clr_blu
  ; - - -
  end

  ; Finish the .gif output
  if NOT(KEYWORD_SET(ZBUFFER)) then wshow,iwind,iconic=0
  image = tvrd()
  tvlct, red, green, blue, /GET
  gif_out = output_prefix+'_'+proc_method+'_pileup.gif'
  write_gif, out_dir+'/'+gif_out, image, red, green, blue

  ; Add .gif link
  printf, out_unit, "</PRE>"
  printf, out_unit, "<UL>"
  printf, out_unit, '<LI><B><A href="'+gif_out+'">'+ $
	'Pileup Plots'+'</A></B>'
  printf, out_unit, "</UL>"
  printf, out_unit, "<PRE>"

  if KEYWORD_SET(MOUSE) then begin
    print, '    !!! Click Mouse anywhere to Continue !!!'
    print, ''
    cursor, x, y, 3
  end

  if NOT(KEYWORD_SET(SILENT)) then print, ''
  printf, out_unit, ''
end


if NOT(KEYWORD_SET(SILENT)) then begin
  print, ' Constant d-Lambda binning from '+STRCOMPRESS(ge_min)+ $
	' to '+STRCOMPRESS(ge_max)+' keV'
  print, ''
  print, ' E/dE of one bin width at 1 keV = '+STRCOMPRESS(1./(ge_bin_ratio-1.0))
  print, ''
end
printf, out_unit, ' Constant d-Lambda binning from '+STRCOMPRESS(ge_min)+' to '+STRCOMPRESS(ge_max)+$
		' keV'
printf, out_unit, ''
printf, out_unit, ' E/dE of one bin width at 1 keV = '+STRCOMPRESS(1./(ge_bin_ratio-1.0))
printf, out_unit, ''

; Here is the grating binning...
; Going to be dragged kicking and screaming into wavelength land
; by instrument (blur ~ constant in lambda) and ISIS very soon...
; These histograms are created here for plotting purposes, they are
; written out to rdb and ISIS data files later in code.

; Do a binning in Lambda with E/dE at 1 keV (= hc A) of :
;    1.0/(ge_bin_ratio -1.0) :
lin_hist, hc/em1_megp, (hc)*(ge_bin_ratio-1.0), mpbins, mpcounts
mpbins = hc/mpbins
binsort = SORT(mpbins)
mpbins = mpbins(binsort)
mpcounts = mpcounts(binsort)

lin_hist, hc/em1_megm, (hc)*(ge_bin_ratio-1.0), mmbins, mmcounts
mmbins = hc/mmbins
binsort = SORT(mmbins)
mmbins = mmbins(binsort)
mmcounts = mmcounts(binsort)


if GRATING EQ 'HETG' then begin
  lin_hist, hc/em1_hegp, (hc)*(ge_bin_ratio-1.0), hpbins, hpcounts
  hpbins = hc/hpbins
  binsort = SORT(hpbins)
  hpbins = hpbins(binsort)
  hpcounts = hpcounts(binsort)

  lin_hist, hc/em1_hegm, (hc)*(ge_bin_ratio-1.0), hmbins, hmcounts
  hmbins = hc/hmbins
  binsort = SORT(hmbins)
  hmbins = hmbins(binsort)
  hmcounts = hmcounts(binsort)
end

if GRATING EQ 'LETG' then begin
  !p.multi=[0,1,2]
  plot_oo, mmbins, mmcounts, PSYM=10, $
	XSTYLE=1, XRANGE=[ge_min, ge_max], $
	YSTYLE=1, YRANGE=[0.5, 2.0*MAX(mmcounts)], $
	BACK=clr_back, COLOR=clr_wht, /NODATA, $
        TITLE='LETG Spectra', $
	XTITLE='LEG-minus Energy (keV)', $
	YTITLE='Counts/bin', $
	CHARSIZE=1.51
  oplot, mmbins, mmcounts, PSYM=10, COLOR=clr_yel
  plot_oo, mpbins, mpcounts, PSYM=10, $
	XSTYLE=1, XRANGE=[ge_min, ge_max], $
	YSTYLE=1, YRANGE=[0.5, 2.0*MAX(mmcounts)], $
	BACK=clr_back, COLOR=clr_wht, /NODATA, $
	XTITLE='LEG-plus Energy (keV)', $
	YTITLE='Counts/bin', $
	CHARSIZE=1.51
  oplot, mpbins, mpcounts, PSYM=10, COLOR=clr_yel
end else begin
  !p.multi=[0,1,4]
  plot_oo, mmbins, mmcounts, PSYM=10, $
	XSTYLE=1, XRANGE=[ge_min, ge_max], $
	YSTYLE=1, YRANGE=[0.5, 2.0*MAX(mmcounts)], $
	BACK=clr_back, COLOR=clr_wht, /NODATA, $
        TITLE='HETG Spectra', $
	XTITLE='MEG-minus Energy (keV)', $
	YTITLE='Counts/bin', $
	CHARSIZE=1.51
  oplot, mmbins, mmcounts, PSYM=10, COLOR=clr_yel
  plot_oo, mpbins, mpcounts, PSYM=10, $
	XSTYLE=1, XRANGE=[ge_min, ge_max], $
	YSTYLE=1, YRANGE=[0.5, 2.0*MAX(mmcounts)], $
	BACK=clr_back, COLOR=clr_wht, /NODATA, $
	XTITLE='MEG-plus Energy (keV)', $
	YTITLE='Counts/bin', $
	CHARSIZE=1.51
  oplot, mpbins, mpcounts, PSYM=10, COLOR=clr_yel
  plot_oo, hmbins, hmcounts, PSYM=10, $
  	XSTYLE=1, XRANGE=[ge_min, ge_max], $
	YSTYLE=1, YRANGE=[0.5, 2.0*MAX(mmcounts)], $
	BACK=clr_back, COLOR=clr_wht, /NODATA, $
	XTITLE='HEG-minus Energy (keV)', $
	YTITLE='Counts/bin', $
	CHARSIZE=1.51
  oplot, hmbins, hmcounts, PSYM=10, COLOR=clr_blu
  plot_oo, hpbins, hpcounts, PSYM=10, $
	XSTYLE=1, XRANGE=[ge_min, ge_max], $
	YSTYLE=1, YRANGE=[0.5, 2.0*MAX(mmcounts)], $
	BACK=clr_back, COLOR=clr_wht, /NODATA, $
	XTITLE='HEG-plus Energy (keV)', $
	YTITLE='Counts/bin', $
	CHARSIZE=1.51
  oplot, hpbins, hpcounts, PSYM=10, COLOR=clr_blu
end

; Finish the .gif output
if NOT(KEYWORD_SET(ZBUFFER)) then wshow,iwind,iconic=0
image = tvrd()
tvlct, red, green, blue, /GET
gif_out = output_prefix+'_'+proc_method+'_gspectra.gif'
write_gif, out_dir+'/'+gif_out, image, red, green, blue

; Add .gif link
printf, out_unit, "</PRE>"
printf, out_unit, "<UL>"
printf, out_unit, '<LI><B><A href="'+gif_out+'">'+$
	'Grating Spectra Plots'+'</A></B>'
printf, out_unit, "</UL>"
printf, out_unit, "<PRE>"

if KEYWORD_SET(MOUSE) then begin
  print, '    !!! Click Mouse anywhere to Continue !!!'
  print, ''
  cursor, x, y, 3
end
; end of crude disp spectra...
; - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

; .......................................
; Data and Parameters available at this stage:
;  filename, grating, evts, evts_tags,
;  max_sel_energy, min_sel_energy, e_bin_ratio, 
;  ftime, tsort, delta_ts, tbinsize, tgapsize, interval_duration
;  zoregsize, zosel, aveXtouse, aveYtouse,
;  ASPECT: time_bin_size, fft_thresh, binT, binaveX, binaveY, binnave,
;          smaveX, smaveY, AX, AY, aveAX, aveAY
;  qnames, qangles, [heg|meg][m|p|all]sel
;  pixel_size, hetg_rs, p_meg, p_heg, hc, ge_min, ge_max, ge_bin_ratio
;  megleg, em1_[heg|meg][p|m], [h|m][m|p]bins, [h|m][m|p]counts
; .......................................


; - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
; Check Zero-order spectra (if available) with dispersed spectra
;   Parameters:
; smoothing kernel to apply to ACIS and Grating spectra...
; A rectangular kernel is applied three times to produce
; a parabolic line response, FWHM of this is ~1.23 times the
; kernel length.

compare_EdE = 40.0  ; want to smooth the spectra to this level
                    ; to blur grating and ACIS spectra to similar level.
; The grating spectra are binned to ge_bin_ratio - how many of these
; bins is compare_EdE? :
compare_bins = ALOG(1. + 1./compare_EdE)/ALOG(ge_bin_ratio)
; empirical factor to convert kernel length to effective FWHM:
len2fwhm = 1.23
; needed k_len is then
k_len = FIX(compare_bins/len2fwhm > 3) ; keep 3 bins at least

if NOT(KEYWORD_SET(SILENT)) then begin
  print, ' - - - - - - - - - - - - Compare Zero-order and Dispersed spectra - - - - - - '
  print, ''
  print, '                    ==> MTA Monitor Task 5.7 <=='
  print, ''
end
printf, out_unit, "</PRE>"
printf, out_unit, '<HR>'
printf, out_unit, '<H3>Compare Zero-order and Dispersed Spectra...</H3>'
printf, out_unit, '<P align="center"><FONT COLOR="#00D000" SIZE=+1>'
printf, out_unit, ' ==> MTA Monitor Task 5.7 <== '
printf, out_unit, '</FONT></P>'
printf, out_unit, '<PRE>'

; Get the predicted effective areas for:
;  HETG/LETG zero-order
;  MEG/LEG combined 1st orders
;  HEG combined 1st orders
; "AO-1" versions of these are in:
if STRPOS(!DDLOCATION, 'HAK') LT 0 then begin 
  ; CALDB location of the files
  tbl_dir = !DDHETGCAL+'/fcp/Tbl_AO1'
end else begin
  ; HAK Stand-alone location of the files
  tbl_dir = !DDHAKDATA
end
; and file names are:
if STRPOS(DETECTOR,'HRC') GE 0 then begin
  if STRPOS(DETECTOR,'-S') GE 0 then begin
    hetg0file = 'EA_'+GRATING+'0-HS.rdb'
    meg1file = 'EA_MEG1-HS.rdb'
    heg1file = 'EA_HEG1-HS.rdb'
    leg1file = 'EA_LETG1-HS.rdb'
  end else begin
    hetg0file = 'EA_'+GRATING+'0-HI.rdb'
    meg1file = 'EA_MEG1-HI.rdb'
    heg1file = 'EA_HEG1-HI.rdb'
    leg1file = 'EA_LETG1-HI.rdb'
  end
end else begin
  hetg0file = 'EA_'+GRATING+'0-AS.rdb'
  meg1file = 'EA_MEG1-AS.rdb'
  heg1file = 'EA_HEG1-AS.rdb'
  leg1file = 'EA_LETG1-AS.rdb'
end

if GRATING EQ 'LETG' then meg1file = leg1file
; TAGs are energy and aeff
;
eahetg0 = rdb_read(tbl_dir+'/'+hetg0file,/SILENT)
eameg1 = rdb_read(tbl_dir+'/'+meg1file,/SILENT)
if GRATING EQ 'HETG' then begin
  eaheg1 = rdb_read(tbl_dir+'/'+heg1file,/SILENT)
end

; Create the spectra
; The counts/(s bin) is converted to photons/cm^2 s bin
zoeavail = (got_energy) AND $
	NOT(STRPOS(DETECTOR,'HRC') GE 0)

if zoeavail then begin
  log_hist, Etouse(zosel), ge_bin_ratio, zobins, zocounts
end
log_hist, [em1_megp,em1_megm], ge_bin_ratio, megbins, megcounts
if GRATING EQ 'HETG' then begin
  log_hist, [em1_hegp,em1_hegm], ge_bin_ratio, hegbins, hegcounts
end
if zoeavail then begin
  zoarea = INTERPOL_SORT(eahetg0.aeff, eahetg0.energy, zobins,/SILENT)
  zospect = (zocounts/interval_duration)/(zoarea > 0.01)
end
megarea = INTERPOL_SORT(eameg1.aeff, eameg1.energy, megbins,/SILENT)
megspect = (megcounts/interval_duration)/(megarea > 0.01)
if GRATING EQ 'HETG' then begin
  hegarea = INTERPOL_SORT(eaheg1.aeff, eaheg1.energy, hegbins,/SILENT)
  hegspect = (hegcounts/interval_duration)/(hegarea > 0.01)
end

k_fwhm = k_len*len2fwhm
k_ede = 1.0/((ge_bin_ratio^k_fwhm)-1.0)

if NOT(KEYWORD_SET(SILENT)) then begin
  print, ' Smoothing the spectra to E/dE ~ '+STRCOMPRESS(k_ede)
  print, ''
end
printf, out_unit, ' Smoothing the spectra by E/dE ~ '+STRCOMPRESS(k_ede)
printf, out_unit, ''

; Convolve with rectangle function three times (make parabola LRF)
kernel = (1.0+FLTARR(k_len))/FLOAT(k_len)
if zoeavail then begin
  czospect = CONVOL(zospect, kernel)
  czospect = CONVOL(czospect, kernel)
  czospect = CONVOL(czospect, kernel)
end
cmegspect = CONVOL(megspect, kernel)
cmegspect = CONVOL(cmegspect, kernel)
cmegspect = CONVOL(cmegspect, kernel)
if GRATING EQ 'HETG' then begin
  chegspect = CONVOL(hegspect, kernel)
  chegspect = CONVOL(chegspect, kernel)
  chegspect = CONVOL(chegspect, kernel)
end
 
nplots = 4
if GRATING EQ 'LETG' then nplots = nplots-1
if NOT(zoeavail) then nplots = nplots-1
!p.multi=[0,1,nplots]

; Use the same Y range for the spectra: MAX from all of them
allspectvis = [1.E-20]
megvis = where(megbins GT ge_min AND megbins LT ge_max, nmegvis)
if nmegvis GE 1 then begin
  allspectvis = [allspectvis, cmegspect(megvis)]
end
if zoeavail then begin
  zovis = where(zobins GT ge_min AND zobins LT ge_max, nzovis)
  if nzovis GE 1 then begin
    allspectvis = [allspectvis, czospect(zovis)]
  end
end
if GRATING EQ 'HETG' then begin
  ; Don't include E < 0.8 keV (a few counts at 0.65 Oxygen can be huge!)
  hegvis = where(hegbins GT (ge_min > 0.80) AND hegbins LT ge_max, nhegvis)
  if nhegvis GE 1 then begin
    allspectvis = [allspectvis, chegspect(hegvis)]
  end
end
max_spec_range = 4.0*MAX(allspectvis)

spec_range = max_spec_range*[1.E-3,1.0]
if zoeavail then begin
  plot_oo, zobins, czospect, PSYM=10, $
	XSTYLE=1, XRANGE=[ge_min, ge_max], $
	YSTYLE=1, YRANGE= spec_range, $
	BACK=clr_back, COLOR=clr_wht, /NODATA, $
	TITLE='ACIS Zero-order Spectrum: Raw and Smoothed', $
	XTITLE='Energy (keV)', $
	YTITLE='Photons / cm^2 s bin', $
	CHARSIZE = 1.51
; The counts/(s bin) is converted to photons/cm^2 s bin
  oplot, zobins, czospect, PSYM=10, COLOR=clr_org
  oplot, zobins, zospect, LINESTYLE=1, COLOR=clr_org
end

plot_oo, megbins, cmegspect, PSYM=10, $
	XSTYLE=1, XRANGE=[ge_min, ge_max], $
	YSTYLE=1, YRANGE= spec_range, $
	BACK=clr_back, COLOR=clr_wht, /NODATA, $
	TITLE=STRUPCASE(megleg)+' Spectrum: Raw and Smoothed', $
	XTITLE='Energy (keV)', $
	YTITLE='Photons / cm^2 s bin', $
	CHARSIZE = 1.51
oplot, megbins, cmegspect, PSYM=10, COLOR=clr_yel
oplot, megbins, megspect, LINESTYLE=1, COLOR=clr_yel
if GRATING EQ 'HETG' then begin
  plot_oo, hegbins, chegspect, PSYM=10, $
	XSTYLE=1, XRANGE=[ge_min, ge_max], $
	YSTYLE=1, YRANGE= spec_range, $
	BACK=clr_back, COLOR=clr_wht, /NODATA, $
	TITLE='HEG Spectrum: Raw and Smoothed', $
	XTITLE='Energy (keV)', $
	YTITLE='Photons / cm^2 s bin', $
	CHARSIZE = 1.51
  oplot, hegbins, chegspect, PSYM=10, COLOR=clr_blu
  oplot, hegbins, hegspect, LINESTYLE=1, COLOR=clr_blu
end

; Put all of them together
if zoeavail then begin
  plot_oo, zobins, czospect, PSYM=10, $
	XSTYLE=1, XRANGE=[ge_min, ge_max], $
	YSTYLE=1, YRANGE= spec_range, $
	BACK=clr_back, COLOR=clr_wht, /NODATA, $
	TITLE='All Smoothed Spectra for Comparison', $
	XTITLE='Energy (keV)', $
	YTITLE='Photons / cm^2 s bin', $
	CHARSIZE = 1.51
  oplot, zobins, czospect, PSYM=10, COLOR=clr_org
  oplot, megbins, cmegspect, LINESTYLE=2, COLOR=clr_yel
end else begin
  plot_oo, megbins, cmegspect, PSYM=10, $
	XSTYLE=1, XRANGE=[ge_min, ge_max], $
	YSTYLE=1, YRANGE= spec_range, LINESTYLE=2, $
	BACK=clr_back, COLOR=clr_wht, /NODATA, $
	TITLE='All Smoothed Spectra for Comparison', $
	XTITLE='Energy (keV)', $
	YTITLE='Photons / cm^2 s bin', $
	CHARSIZE = 1.51
  oplot, megbins, cmegspect, PSYM=10, LINESTYLE=2, COLOR=clr_yel
end
if GRATING EQ 'HETG' then begin
  oplot, hegbins, chegspect, LINESTYLE=1, COLOR=clr_blu
end

; Finish the .gif output
if NOT(KEYWORD_SET(ZBUFFER)) then wshow,iwind,iconic=0
image = tvrd()
tvlct, red, green, blue, /GET
gif_out = output_prefix+'_'+proc_method+'_gcompare.gif'
write_gif, out_dir+'/'+gif_out, image, red, green, blue

; Add .gif link
printf, out_unit, "</PRE>"
printf, out_unit, "<UL>"
printf, out_unit, '<LI><B><A href="'+gif_out+'">'+ $
	'Plots to Compare the Spectra'+'</A></B>'
printf, out_unit, "</UL>"
printf, out_unit, "<PRE>"

if KEYWORD_SET(MOUSE) then begin
  print, '    !!! Click Mouse anywhere to Continue !!!'
  print, ''
  cursor, x, y, 3
end
; end of zero-order spectra comparison
; - - - - - - - - - - - - - - - - - - - - - - - - - - - - -


; - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
; Check BI - FI ratio etc. (S1 vs S4,S5)


; - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
; Check as-measured E/dE vs E for bright lines
; Do this by writing out histograms from this analysis
; and from L1.5 analysis if available.  Then call
; procedure to do the analysis...
if NOT(KEYWORD_SET(SILENT)) then begin
  print, ' - - - - - - - - - Outputing Histograms of Spectra - - - - - -'
  print, ''
end
printf, out_unit, "</PRE>"
printf, out_unit, '<HR>'
printf, out_unit, '<H3>Outputing Histograms of Spectra...</H3>'
printf, out_unit, "<PRE>"
printf, out_unit, ""

if KEYWORD_SET(LINE_ANALYSIS) then begin
  if NOT(KEYWORD_SET(SILENT)) then begin
    print, ''
    print, '                    ==> MTA Monitor Task 5.4 <=='
    print, ''
  end
  printf, out_unit, '</PRE>'
  printf, out_unit, '<P align="center"><FONT COLOR="#00D000" SIZE=+1>'
  printf, out_unit, ' ==> MTA Monitor Task 5.4 <== '
  printf, out_unit, '</FONT></P>'
  printf, out_unit, '<PRE>'
end

; Define available dispersed spectra:
if GRATING EQ 'HETG' then begin
  if zoeavail then begin
    tg_part_strs = ['MEGm1','MEGp1','HEGm1','HEGp1']
    tg_parts = [2,2,1,1]
    tg_ms = [-1,1,-1,1]
  end else begin
    tg_part_strs = ['MEGmAll','MEGpAll','HEGmAll','HEGpAll']
    tg_parts = [2,2,1,1]
    tg_ms = [-1,1,-1,1]
  end
end
if GRATING EQ 'LETG' then begin
  if zoeavail then begin
    tg_part_strs = ['LEGm1','LEGp1']
    tg_parts = [3,3]
    tg_ms = [-1,1]
  end else begin
    tg_part_strs = ['LEGmAll','LEGpAll']
    tg_parts = [3,3]
    tg_ms = [-1,1]
  end
end

; Loop through the available histograms (spectra):
for is=0,n_elements(tg_part_strs)-1 do begin
  tg_part_str = tg_part_strs(is)
  tg_part = tg_parts(is)
  tg_m = tg_ms(is)

  ; set bins and counts for the histogram to write out
  CASE tg_part_str OF
    'MEGm1': begin
      bins = mmbins
      counts = mmcounts
    end
    'MEGp1': begin
      bins = mpbins
      counts = mpcounts
    end
    'HEGm1': begin
      bins = hmbins
      counts = hmcounts
    end
    'HEGp1': begin
      bins = hpbins
      counts = hpcounts
    end
    'MEGmAll': begin
      bins = mmbins
      counts = mmcounts
    end
    'MEGpAll': begin
      bins = mpbins
      counts = mpcounts
    end
    'HEGmAll': begin
      bins = hmbins
      counts = hmcounts
    end
    'HEGpAll': begin
      bins = hpbins
      counts = hpcounts
    end
    'LEGm1': begin
      bins = mmbins
      counts = mmcounts
    end
    'LEGp1': begin
      bins = mpbins
      counts = mpcounts
    end
    'LEGmAll': begin
      bins = mmbins
      counts = mmcounts
    end
    'LEGpAll': begin
      bins = mpbins
      counts = mpcounts
    end
  ELSE:    ; skip it
  ENDCASE


  ; Write the histogram file

  ; START - - - - - - hist_write_template.pro - - - - -
  ; Include and modify the following code to output data
  ; to an rdb histogram file
  ;
  ; column names
  hist_struct = {bin: 0.0, count:0.0, err:0.0}
  hist = REPLICATE(hist_struct, n_elements(bins))
  ;
  ; fill the strucuture from desired arrays...
  hist.bin = bins
  hist.count = counts
  hist.err = SQRT(FLOAT(counts))
  ;
  ; create header information
  ; each line is an element in the string array
  ; each line should start with a "#"
  ; optional parameters have the format:
  ; "# param_name[:][TAB]value_string"
  ;
  ; customize for application...
  your_header=['# created by obs_anal.pro, '+SYSTIME(),$
	'# event_filename:	'+filename, $
	'# grating:	'+grating, $
	'# detector:	'+detector, $
	'# tg_part_str:	'+tg_part_str, $
	'# processing:	'+proc_method ]
  ;
  ; parameters that hist routines might use:
  hist_header=['# for histogram routines use:', $
	'# title:	'+filename+': '+tg_part_str+' ('+ $
			proc_method+')', $
	'# bin_axis:	Energy', $
	'# bin_unit:	keV' ]
  header = [your_header, hist_header]
  ;
  ; and write it out to desired file
  hist_file = output_prefix+'_'+ $
	proc_method+'_'+tg_part_str+'_hist.rdb' 
  if NOT(KEYWORD_SET(SILENT)) then begin
    print, ' Creating '+hist_file+' ...'
  end
  printf, out_unit, ' Creating <B><A href="'+hist_file+'">'+hist_file+'</A></B> ...'
  ; prepend the output directory...
  hist_file = out_dir+'/'+hist_file
  rdb_write, hist_file, hist, HEAD = header, /SILENT
  ; END - - - - - - hist_write_template.pro - - - - -

  ; Write out the ISIS format file
  isis_file = output_prefix+'_'+proc_method+'_'+tg_part_str+'_isis.dat' 

  ; Convert back to wavelength histogram
  ; (arg!  "Energy -- going once, going twice, ...")
  lambins = hc/bins
  sortlam = SORT(lambins)
  lambins = lambins(sortlam)
  lamcounts = counts(sortlam)
  ; these histograms were linear in lambda, so dlambda is:
  dlam2 = (lambins(1) - lambins(0))/2.0  
  if NOT(KEYWORD_SET(SILENT)) then begin
    print, ' Creating ISIS format: '+isis_file+' ...'
  end
  printf, out_unit, ' Creating ISIS format: <B><A href="'+isis_file+'">'+isis_file+'</A></B> ...'

  hak_write_isis, out_dir+'/'+isis_file, $
	lambins-dlam2, lambins+dlam2, $
	lamcounts, SQRT(lamcounts), $
	DATAFROM='obs_anal.pro', $
	OBJECT=OUTPUT_PREFIX, $
	INSTRUMENT=DETECTOR, GRATING=GRATING, EXPOSURE=interval_duration, $
	TG_M=tg_m, TG_PART=tg_part, $
	TG_SRCID=1, XUNIT='Angstrom'

;***;  OPENW, isis_unit, out_dir+'/'+isis_file, /GET
;;  printf, isis_unit, n_elements(lambins)
;;  for ib=0,n_elements(lambins)-1 do begin
;;    printf, isis_unit, lambins(ib)-dlam2, lambins(ib)+dlam2, $
;;	lamcounts(ib), SQRT(lamcounts(ib))
;;  end
;;  close, isis_unit
;;  free_lun, isis_unit

  if KEYWORD_SET(LINE_ANALYSIS) then begin

    if KEYWORD_SET(MOUSE) then begin
      hist_lines, hist_file, /MOUSE, $
	OUTPUT_PREFIX=hist_prefix, OUT_DIR = out_dir, ZBUFFER=zbuffer, $
	RES1KEV = res1kev
    end else begin
      if KEYWORD_SET(SILENT) then begin
        hist_lines, hist_file, /SILENT, $
		OUTPUT_PREFIX=hist_prefix, OUT_DIR = out_dir, ZBUFFER=zbuffer, $
		RES1KEV = res1kev
      end else begin
        hist_lines, hist_file, $
		OUTPUT_PREFIX=hist_prefix, OUT_DIR = out_dir, ZBUFFER=zbuffer, $
		RES1KEV = res1kev
      end
    end

    ; save the resolving power average value
    rpf_add_param, rpf, tg_part_str+'_Res1keV', res1kev

    ; Make links to the output files
    ; hist_lines produces files named hist_prefix + :
    ; _specpanes.gif 
    ; _linefits.gif
    ; _eoverde.gif
    ; _linelist.txt and .rdb
    ; Build links for these...

    printf, out_unit, '</PRE>'
    printf, out_unit, '<TABLE BORDER=1>'
    printf, out_unit, '<TR>'
    this_file = hist_prefix + '_specpanes.gif'
    printf, out_unit, '<TD><B><A href="'+this_file+'"> Spectrum </A></B>'
    this_file = hist_prefix + '_linefits.gif'
    printf, out_unit, '<TD><B><A href="'+this_file+'"> Line Fits </A></B>'
    this_file = hist_prefix + '_eoverde.gif'
    printf, out_unit, '<TD><B><A href="'+this_file+'"> E/dE vs E </A></B>'
    this_file = hist_prefix + '_linelist.txt'
    printf, out_unit, '<TD><B>Line list <A href="'+this_file+'">.txt</A>'
    this_file = hist_prefix + '_linelist.rdb'
    printf, out_unit, ' or <A href="'+this_file+'">.rdb</A></B>'
    printf, out_unit, '</TABLE>'
    printf, out_unit, '<PRE>'
  end

if NOT(KEYWORD_SET(SILENT)) then print,''
printf, out_unit,''
end ; of loop over spectra to write out...
; - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

if KEYWORD_SET(MOUSE) then begin
  print, '    !!! Click Mouse anywhere to Continue !!!'
  print, ''
  cursor, x, y, 3
end

; - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
; Level 1.5 summary (numbers of events in sources, parts, )
; TG_SRCID, TG_PART
;
Level_1a_check: dummy_statement = 0.0

if NOT(KEYWORD_SET(SILENT)) then begin
  print, ' - - - - - - - - - Check Level 1.5 Columns... - - - - - -'
  print, ''
end
printf, out_unit, "</PRE>"
printf, out_unit, '<HR>'
printf, out_unit, '<H3>Check Level 1.5 Columns...</H3>'
printf, out_unit, "<PRE>"
printf, out_unit, ""

; List all evts tags that have tg_ in them:
l1p5tags = where(STRPOS(evts_tags,'TG_') GE 0, nfound)

if nfound EQ 0 then begin
  if NOT(KEYWORD_SET(SILENT)) then begin
    print, ' No Level 1.5 columns found in the file.'
    print, ''
  end
  printf, out_unit, ' No Level 1.5 columns found in the file.'
  printf, out_unit, ''
end else begin
  if NOT(KEYWORD_SET(SILENT)) then begin
    print, ' Found Level 1.5 columns: '
    print, '     '+evts_tags(l1p5tags)
    print, ''
  end
  printf, out_unit, ' Found Level 1.5 columns: '
  printf, out_unit, '     '+evts_tags(l1p5tags)
  printf, out_unit, ''

  if TOTAL(evts_tags EQ 'TG_SRCID') GT 0 then begin
    maxsrcid = MAX(evts(where(evts.tg_srcid LT 99)).tg_srcid)
    if NOT(KEYWORD_SET(SILENT)) then begin
      print, ' TG_SRCID: MAX value (<99) is: '+STRCOMPRESS(maxsrcid)
      print, ''
    end
    printf, out_unit, ' TG_SRCID: MAX value (<99) is: '+STRCOMPRESS(maxsrcid)
    printf, out_unit, ''
  end
  if TOTAL(evts_tags EQ 'TG_M') GT 0 then begin
    maxtgord = MAX(evts(where(evts.tg_m LT 99)).tg_m)
    if NOT(KEYWORD_SET(SILENT)) then begin
      print, ' TG_M: MAX value (<99) is: '+STRCOMPRESS(maxtgord)
      print, ' TG_M: MIN value is: '+STRCOMPRESS(MIN(evts.TG_M))
      print, ''
    end
    printf, out_unit, ' TG_M: MAX value (<99) is: '+STRCOMPRESS(maxtgord)
    printf, out_unit, ' TG_M: MIN value is: '+STRCOMPRESS(MIN(evts.TG_M))
    printf, out_unit, ''
  end
  if TOTAL(evts_tags EQ 'TG_PART') GT 0 then begin
    ; Make a table of the number of events in each Source-Part
    ; Plot the events in TG_R, TG_D while we're here...
    if GRATING EQ 'LETG' then begin
      nspectra = 1 ; one spectra for each source
    end else begin
      nspectra = 2 ; heg, meg spectra for each source
    end
    bkgnd = where(evts.TG_PART EQ 99, nbkgnd)
    if NOT(KEYWORD_SET(SILENT)) then begin
      print, ' Events in different Source-Parts:'
      print, ''
      print, '   Source      Zero-order     HEG     MEG     LEG'
      print, '  - - - - - - - - - - - - - - - - - - - - - - - - - -'
      print, '   Backgnd    '+STRING(nbkgnd, FORMAT='(I8)')
      print, '  . . . . . . . . . . . . . . . . . . . . . . . . .'
    end
    printf, out_unit, ' Events in different Source-Parts:'
    printf, out_unit, ''
    printf, out_unit, '   Source      Zero-order     HEG     MEG     LEG'
    printf, out_unit, '  - - - - - - - - - - - - - - - - - - - - - - - - - -'
    printf, out_unit, '   Backgnd    '+STRING(nbkgnd, FORMAT='(I8)')
    printf, out_unit, '  . . . . . . . . . . . . . . . . . . . . . . . . .'
    for is=1,maxsrcid do begin
      if is GT 1 then begin
        if NOT(KEYWORD_SET(SILENT)) then begin
          print, '  . . . . . . . . . . . . . . . . . . . . . . . . .'
        end
        printf, out_unit, '  . . . . . . . . . . . . . . . . . . . . . . . . .'
      end
      ; and plot TG_D vs hc/TG_LAM in ge_min to ge_max range also!
      !p.multi = [0,1,2*nspectra]
      found = where(evts.tg_srcid EQ is AND evts.tg_part EQ 0, nzopart)

      found = where(evts.tg_srcid EQ is AND evts.tg_part EQ 2, nmegpart)
      if nmegpart GT 0 then begin
        plot, evts(found).TG_R, evts(found).TG_D, PSYM=3, $
		XSTYLE=1, YSTYLE=1, $
		BACK=clr_back, COLOR=clr_wht, /NODATA, $
		TITLE = 'TG_R - TG_D Plot for MEG Part of Source '+$
			STRCOMPRESS(is,/REMOVE_ALL), $
		XTITLE = 'TG_R (degrees)', YTITLE='TG_D (degrees)', $
		CHARSIZE=1.71
        plots, evts(found).TG_R, evts(found).TG_D, PSYM=3, $
		COLOR=energy_colors(found), NOCLIP=0
        plot_oi, hc/evts(found).TG_LAM, evts(found).TG_D, PSYM=3, $
		XSTYLE=1, YSTYLE=1, XRANGE=[ge_min,ge_max], $
		BACK=clr_back, COLOR=clr_wht, /NODATA, $
		TITLE = 'TG_Energy - TG_D Plot for MEG Part of Source '+$
			STRCOMPRESS(is,/REMOVE_ALL), $
		XTITLE = 'hc/TG_LAM (keV)', YTITLE='TG_D (degrees)', $
		CHARSIZE=1.71
        plots, hc/evts(found).TG_LAM, evts(found).TG_D, PSYM=3, $
		COLOR=energy_colors(found), NOCLIP=0
      end

      found = where(evts.tg_srcid EQ is AND evts.tg_part EQ 1, nhegpart)
      if nhegpart GT 0 then begin
        plot, evts(found).TG_R, evts(found).TG_D, PSYM=3, $
		XSTYLE=1, YSTYLE=1, $
		BACK=clr_back, COLOR=clr_wht, /NODATA, $
		TITLE = 'TG_R - TG_D Plot for HEG Part of Source '+$
			STRCOMPRESS(is,/REMOVE_ALL), $
		XTITLE = 'TG_R (degrees)', YTITLE='TG_D (degrees)', $
		CHARSIZE=1.71
        plots, evts(found).TG_R, evts(found).TG_D, PSYM=3, $
		COLOR=energy_colors(found), NOCLIP=0
        plot_oi, hc/evts(found).TG_LAM, evts(found).TG_D, PSYM=3, $
		XSTYLE=1, YSTYLE=1, XRANGE=[ge_min,ge_max], $
		BACK=clr_back, COLOR=clr_wht, /NODATA, $
		TITLE = 'TG_Energy - TG_D Plot for HEG Part of Source '+$
			STRCOMPRESS(is,/REMOVE_ALL), $
		XTITLE = 'hc/TG_LAM (keV)', YTITLE='TG_D (degrees)', $
		CHARSIZE=1.71
        plots, hc/evts(found).TG_LAM, evts(found).TG_D, PSYM=3, $
		COLOR=energy_colors(found), NOCLIP=0
      end

      found = where(evts.tg_srcid EQ is AND evts.tg_part EQ 3, nlegpart)
      if nlegpart GT 0 then begin
        plot, evts(found).TG_R, evts(found).TG_D, PSYM=3, $
		XSTYLE=1, YSTYLE=1, $
		BACK=clr_back, COLOR=clr_wht, /NODATA, $
		TITLE = 'TG_R - TG_D Plot for LEG Part of Source '+$
			STRCOMPRESS(is,/REMOVE_ALL), $
		XTITLE = 'TG_R (degrees)', YTITLE='TG_D (degrees)', $
		CHARSIZE=1.71
        plots, evts(found).TG_R, evts(found).TG_D, PSYM=3, $
		COLOR=energy_colors(found), NOCLIP=0
        plot_oi, hc/evts(found).TG_LAM, evts(found).TG_D, PSYM=3, $
		XSTYLE=1, YSTYLE=1, XRANGE=[ge_min,ge_max], $
		BACK=clr_back, COLOR=clr_wht, /NODATA, $
		TITLE = 'TG_Energy - TG_D Plot for LEG Part of Source '+$
			STRCOMPRESS(is,/REMOVE_ALL), $
		XTITLE = 'hc/TG_LAM (keV)', YTITLE='TG_D (degrees)', $
		CHARSIZE=1.71
        plots, hc/evts(found).TG_LAM, evts(found).TG_D, PSYM=3, $
		COLOR=energy_colors(found), NOCLIP=0
      end

      if NOT(KEYWORD_SET(SILENT)) then begin
        print, STRING(is,FORMAT='(I7)')+ '       '+ $
		STRING(nzopart, FORMAT='(I8)') + '    ' + $
		STRING(nhegpart, FORMAT='(I8)') + $
		STRING(nmegpart, FORMAT='(I8)') + $
		STRING(nlegpart, FORMAT='(I8)')
      end
      ; Finish the .gif output
      if NOT(KEYWORD_SET(ZBUFFER)) then wshow,iwind,iconic=0
      image = tvrd()
      tvlct, red, green, blue, /GET
      gif_out = output_prefix+'_'+proc_method+'_S'+STRCOMPRESS(is,/REMOVE_ALL)+'_tgrdlam.gif'
      write_gif, out_dir+'/'+gif_out, image, red, green, blue

      printf, out_unit, STRING(is,FORMAT='(I7)')+ '       '+ $
	STRING(nzopart, FORMAT='(I8)') + '    ' + $
	STRING(nhegpart, FORMAT='(I8)') + $
	STRING(nmegpart, FORMAT='(I8)') + $
	STRING(nlegpart, FORMAT='(I8)')

      ; add gif link (indent a bunch with DL)
      printf, out_unit, "</PRE>"
      printf, out_unit, "<DL><DT><DD><UL>"
      printf, out_unit, '<LI><B><A href="'+gif_out+'">'+'TG_R, TG_D, TG_LAM plots'+'</A></B>'
      printf, out_unit, "</UL></DL>"
      printf, out_unit, "<PRE>"


      ; Wait after each source spectra are displayed...
      if KEYWORD_SET(MOUSE) then begin
        print, '    !!! Click Mouse anywhere to Continue !!!'
        print, ''
        cursor, x, y, 3
      end

    end
    if NOT(KEYWORD_SET(SILENT)) then begin
      print, '  - - - - - - - - - - - - - - - - - - - - - - - - - -'
      print, ''
    end
    printf, out_unit, '  - - - - - - - - - - - - - - - - - - - - - - - - - -'
    printf, out_unit, ''
  end
  if NOT(KEYWORD_SET(SILENT)) then print, ''
  printf, out_unit, ''

end ; of checking for L1.5
;  end of Simple Level 1.5 stuff
; - - - - - - - - - - - - - - - - - - - - - - - - - - - - -


; - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
; Output Level 1.5 histograms
if NOT(KEYWORD_SET(SILENT)) then begin
  print, ' - - - - - - - - - Output Histogram files from L1.5 - - - - - -'
  print, ''
end
printf, out_unit, "</PRE>"
printf, out_unit, '<HR>'
printf, out_unit, '<H3>Output Histogram files from L1.5... </H3>'
printf, out_unit, "<PRE>"
printf, out_unit, ""

; L1.5 tags available?
l1p5tags = where(STRPOS(evts_tags,'TG_') GE 0, nfound)
if nfound EQ 0 then begin
  if NOT(KEYWORD_SET(SILENT)) then begin
    print, ' No Level 1.5 columns - cannot create L1.5 histograms.'
    print, ''
  end
  printf, out_unit, ' No Level 1.5 columns - cannot create L1.5 histograms.'
  printf, out_unit, ''
end else begin
  if KEYWORD_SET(LINE_ANALYSIS) then begin
    if NOT(KEYWORD_SET(SILENT)) then begin
      print, ''
      print, '                    ==> MTA Monitor Task 5.4 <=='
      print, ''
    end
    printf, out_unit, '</PRE>'
    printf, out_unit, '<P align="center"><FONT COLOR="#00D000" SIZE=+1>'
    printf, out_unit, ' ==> MTA Monitor Task 5.4 <== '
    printf, out_unit, '</FONT></P>'
    printf, out_unit, '<PRE>'
  end
  if NOT(KEYWORD_SET(SILENT)) then begin
    print, ' Level 1.5 columns - creating L1.5 histograms...'
    print, ''
  end
  printf, out_unit, ' Level 1.5 columns - creating L1.5 histograms...'
  printf, out_unit, ''
  ; Flag the processing...
  proc_method = 'L1.5'
  ; All orders are in TG_LAM...
  orders_used_str = 'All'
  ; unless ACIS is available for sorting
  if STRPOS(DETECTOR,'ACIS') GE 0 then orders_used_str = '1'

  ; Go through the sources
  maxsrcid = MAX(evts(where(evts.tg_srcid LT 99)).tg_srcid)
  for is=1,maxsrcid do begin
    if GRATING EQ 'HETG' then begin
      parts = [2,1]
      tg_part_strs = ['MEG','HEG']
      orders = [-1,1]
    end else begin
      parts = [3]
      tg_part_strs = ['LEG']
      orders = [-1,1]
    end
    ; Loop over the parts and orders
    for ip=0,n_elements(parts)-1 do begin
      this_part = parts(ip)
      for io=0,n_elements(orders)-1 do begin
        this_order = orders(io)
        ; make the tg_part_str for hist filename output...
        ord_str = 'p'
        if this_order EQ 0 then ord_str = 'z'
        if this_order LT 0 then ord_str = 'm'
        if this_order NE 0 then begin
          ord_str = ord_str + STRCOMPRESS(ABS(this_order),/REMOVE_ALL)
        end
        tg_part_str = tg_part_strs(ip)+ord_str
        ; Get the events for this source, part, order
        this_spo = where( (evts.tg_srcid EQ is) AND $
			(evts.tg_m EQ this_order) AND $
			(evts.tg_part EQ this_part), nfound)
        if NOT(KEYWORD_SET(SILENT)) then begin
          print, ' Source '+ STRCOMPRESS(is) + '  '+tg_part_str + $
		' : Number of events = '+ STRCOMPRESS(nfound)
        end
        printf, out_unit, ' Source '+ STRCOMPRESS(is) + '  '+tg_part_str + $
		' : Number of events = '+ STRCOMPRESS(nfound)

        ;; Make a histogram of the energies
        ;;log_hist, hc/evts(this_spo).tg_lam, ge_bin_ratio, bins, counts

        ; Do a binning in Lambda with E/dE at 1 keV (= hc A) of :
        ;    1.0/(ge_bin_ratio -1.0) :
        lin_hist, evts(this_spo).tg_lam, $
		(hc)*(ge_bin_ratio-1.0), bins, counts
        bins = hc/bins
        binsort = SORT(bins)
        bins = bins(binsort)
        counts = counts(binsort)

        ; Write out the histogram
        ; whoops - there goes the indenting due to cut/paste!

  ; START - - - - - - hist_write_template.pro - - - - -
  ; Include and modify the following code to output data
  ; to an rdb histogram file
  ;
  ; column names
  hist_struct = {bin: 0.0, count:0.0, err:0.0}
  hist = REPLICATE(hist_struct, n_elements(bins))
  ;
  ; fill the strucuture from desired arrays...
  hist.bin = bins
  hist.count = counts
  hist.err = SQRT(FLOAT(counts))
  ;
  ; create header information
  ; each line is an element in the string array
  ; each line should start with a "#"
  ; optional parameters have the format:
  ; "# param_name[:][TAB]value_string"
  ;
  ; customize for application...
  your_header=['# created by obs_anal.pro, '+SYSTIME(),$
	'# event_filename:	'+filename, $
	'# grating:	'+grating, $
	'# detector:	'+detector, $
	'# source:	'+STRCOMPRESS(is,/REMOVE_ALL), $
	'# tg_part_str:	'+tg_part_str, $
	'# processing:	'+proc_method ]
  ;
  ; parameters that hist routines might use:
  hist_header=['# for histogram routines use:', $
	'# title:	'+filename+': '+tg_part_str+' ('+ $
			proc_method+')', $
	'# bin_axis:	Energy', $
	'# bin_unit:	keV' ]
  header = [your_header, hist_header]
  ;
  ; and write it out to desired file
  hist_file = output_prefix+'_'+ $
	proc_method+'_'+'S'+STRCOMPRESS(is,/REMOVE_ALL)+ $
		tg_part_str+'_hist.rdb' 
  if NOT(KEYWORD_SET(SILENT)) then begin
    print, ' Creating '+hist_file+' ...'
  end
  printf, out_unit, ' Creating <B><A href="'+hist_file+'">'+hist_file+'</A></B> ...'
  ; prepend the output directory...
  hist_file = out_dir + '/' + hist_file
  rdb_write, hist_file, hist, HEAD = header, /SILENT
  ; END - - - - - - hist_write_template.pro - - - - -

  if KEYWORD_SET(LINE_ANALYSIS) then begin

    if KEYWORD_SET(MOUSE) then begin
      hist_lines, hist_file, /MOUSE, $
	OUTPUT_PREFIX=hist_prefix, OUT_DIR = out_dir, ZBUFFER=zbuffer, $
	RES1KEV = res1kev
    end else begin
      if KEYWORD_SET(SILENT) then begin
        hist_lines, hist_file, /SILENT, $
		OUTPUT_PREFIX=hist_prefix, OUT_DIR = out_dir, ZBUFFER=zbuffer, $
		RES1KEV = res1kev
      end else begin
        hist_lines, hist_file, $
		OUTPUT_PREFIX=hist_prefix, OUT_DIR = out_dir, ZBUFFER=zbuffer, $
		RES1KEV = res1kev
      end
    end

    ; save the resolving power average value
    rpf_add_param, rpf, 'L1a_'+tg_part_str+'_Res1keV', res1kev

    ; Make links to the output files
    ; hist_lines produces files named hist_prefix + :
    ; _specpanes.gif 
    ; _linefits.gif
    ; _eoverde.gif
    ; _linelist.txt
    ; Build links for these...

    printf, out_unit, '</PRE>'
    printf, out_unit, '<TABLE BORDER=1>'
    printf, out_unit, '<TR>'
    this_file = hist_prefix + '_specpanes.gif'
    printf, out_unit, '<TD><B><A href="'+this_file+'"> Spectrum </A></B>'
    this_file = hist_prefix + '_linefits.gif'
    printf, out_unit, '<TD><B><A href="'+this_file+'"> Line Fits </A></B>'
    this_file = hist_prefix + '_eoverde.gif'
    printf, out_unit, '<TD><B><A href="'+this_file+'"> E/dE vs E </A></B>'
    this_file = hist_prefix + '_linelist.txt'
    printf, out_unit, '<TD><B>Line list <A href="'+this_file+'">.txt</A>'
    this_file = hist_prefix + '_linelist.rdb'
    printf, out_unit, ' or <A href="'+this_file+'">.rdb</A></B>'
    printf, out_unit, '</TABLE>'
    printf, out_unit, '<PRE>'

  end else begin
    if NOT(KEYWORD_SET(SILENT)) then print, ''
    printf, out_unit, ''
  end
  ; finished writing histogram

      end ; loop over orders

    end ; loop over parts

  end ; loop over sources


end ; of Level 1.5 histogram output
; - - - - - - - - - - - - - - - - - - - - - - - - - - - - -


; - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
; Clean up and go home...
;
ALL_FINISHED: dummy_statement = 0.0

; Save the parameters to 'summary.rdb
rdb_write, rpf_file_name, rpf, HEADER=rpf_header, /SILENT
; and make a more human readable version:
rpf_list, rpf, HEADER=rpf_header, /SILENT, $
	FILE_OUT=rpf_list_name

printf, out_unit, "</PRE>"
printf, out_unit, '<HR>'
; add a link to summary.txt in the HTML file before the end:
printf, out_unit, '<B><A href="'+ $
	output_prefix+'_'+save_proc_method+'_summary.txt' + $
	'">Listing of _summary.rdb file</A></B> ...'
printf, out_unit, '<HR>'
printf, out_unit, "<PRE>"
printf, out_unit, SYSTIME()+ ' : obs_anal.pro finished'
printf, out_unit, "</PRE>"

; Close the html file
printf, out_unit, "</HTML>"
CLOSE, out_unit
FREE_LUN, out_unit

; Reset the device and plot parameters...
set_plot, Orig_device
!p = Orig_plot      ; restore it all?

; "Return" a bunch of variables to the oa_common for use at the
; command line - only if requested to save memory space...
if KEYWORD_SET(EXPORT) then begin
  oa_filename = filename
  oa_evts = evts
  oa_ftime = ftime
  oa_Xtouse = Xtouse
  oa_Ytouse = Ytouse
  oa_Etouse = Etouse
  oa_energy_colors = energy_colors
  oa_pixel_size = pixel_size
  oa_AX = AX
  oa_AY = AY
  if n_elements(zosel) GE 1 then begin
    oa_zosel = zosel
  end else zosel = -1
  if n_elements(strksel) GE 1 then begin
    oa_strksel = strksel
  end else strksel = -1
  oa_aveXtouse = aveXtouse
  oa_aveYtouse = aveYtouse
  oa_aveAX = aveAX
  oa_aveAY = aveAY
  if n_elements(hegmsel) GE 1 then begin
    oa_hegmsel = hegmsel
    oa_e_hegm = e_hegm
  end else strksel = -1
  if n_elements(megmsel) GE 1 then begin
    oa_megmsel = megmsel
    oa_e_megm = e_megm
  end else strksel = -1
  if n_elements(hegpsel) GE 1 then begin
    oa_hegpsel = hegpsel
    oa_e_hegp = e_hegp
  end else strksel = -1
  if n_elements(megpsel) GE 1 then begin
    oa_megpsel = megpsel
    oa_e_megp = e_megp
  end else strksel = -1
end

; Leave these two final prints to STOUT even if SILENT...
print, ' - - - - - - - - - - - - - - - - - - - - '+ $
	SYSTIME()+' - -'
print, ''

RETURN
END



