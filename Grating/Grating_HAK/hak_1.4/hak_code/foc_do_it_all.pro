PRO foc_do_it_all, OBSANAL=obsanal, GATHER=gather, $
	ANALYZE=analyze
;+
; PRO foc_do_it_all, OBSANAL=obsanal, GATHER=gather, $
;	ANALYZE=analyze
;
; This file:
;   o documents all the analysis steps for
;     analysis of the HETG OAC focus tests.
;   o contains the parameters for a specific analysis.
;     (A local copy of this file is edited and saved
;      for reference.)
;   o carries out the analysis steps.
;
; The KEYWORDS select the major
; processing steps for execution
;
;
; USAGE = Procedure for Focus Analysis:
;         ----------------------------
;
; [] Have unix-like system with the following:
;      . HAK distribution
;      . IDL with ASTROLIB
;      . text editor (e.g., emacs)
;      . HTML browser
;      . disk space for files created...
;
; [] Verify where the HAK distribution is located
;    ("hak_dist"), e.g.,
;      MIT     : /nfs/wiwaxia/d4/ASC/src/hak_N.N
;      SAO/60  : /data/aus1/caldb/local/axaf/cal/hetg/software/hak_N.N
;      MTA/Ops :
;      TARA    :
;      ACIS/GSE:
;      HRC/GSE :
;      web     : http://space.mit.edu/HETG/HAK
;
; [] cd to some "analysis directory" where IDL can be run.
;
; [] Copy to the analysis directory the HAK startup file:
;     o hak_start.pro      (in hak_dist/ )
;
; [] Start IDL/HAK:
;     unix[17] idl
;       (IDL starts up )
;     IDL> @hak_start
;       (HAK starts up )
;     hak>
;
; [] Also copy foc_do_it_all.pro and optionally obs_anal.pro
;    to the analysis directory,
;     o foc_do_it_all.pro        (in hak_dist/hak_code/ )
;     o obs_anal.pro [optional]  (in hak_dist/hak_code/ )
;
;    This can be done from the hak prompt as:
;     hak> SPAWN, 'cp '+!DDHAKCODE+ '/foc_do_it_all.pro .'
;
; [] FYI, Documentation on the various hak routines can be
;    obtained using the IDL doc_library command, e.g.:
;     hak> doc_library, 'obs_anal'
;
; [] Edit the parameters in foc_do_it_all.pro as appropriate
;    and as indicated by the comments in foc_do_it_all.pro.
;     hak> $emacs foc_do_it_all.pro &
;
; [] After editing, compile foc_do_it_all:
;     hak> .run foc_do_it_all
;
; Execute the processing in several processing steps.
;
; [] First, run obs_anal on the FITS files...
;     hak> foc_do_it_all, /OBSANAL
;
; [] Look at the obs_anal output plots, etc. using
;    the html browser.  The files to check can be
;    found by doing "ls -l1 *summary.html" in the
;    obs_anal output directory (foc_do_it_all lists
;    these 'summary.html files also.)
;
; [] Create a "gathered FWHM results" file from all the line lists...
;     hak> foc_do_it_all, /GATHER
;
; [] Create a set of analysis plots, etc.
;    Lines for focus analysis plots may be taken from
;    foc_lwe array.
;     hak> foc_do_it_all, /ANALYZE
;
;    Or make focus plots for a desired "part" (MEGm, HEGp, etc)
;    and line energy:
;     hak> foc_plot, 'MEGm', foc_lwe(0), /ACF
;
;  --------------------------------------------------
; Revision notes
; 7/4-7/99 dd Initial version for 7/6/99 meeting, 
;             and 7/9/99 HAK 1.0 release.
; 8/11/99 dd added foc_project_title and foc_L1a to common;
; 8/12/99 dd write gfr out after anal;
; 8/31/99 dd Add foc_sky_roll to common to be passed to obs_anal:ROLLAXAY
;  -------------------------------------
;-

; Keep a ton of good stuff in common!
@foc_common

; Fill up the common values...

; -------------------------------------
; INPUT PARAMETERS, DIRECTORIES, etc.
; -------------------------------------
; The various parameters are described and set
; below.  Note that commented out versions of the
; lines are included as a "template".

; PROJECT NAME
; This name will be prefixed to plots to identify the foc analysis
;
; foc_project_title = 'OAC Capella Simulation(dd)'
;
foc_project_title = 'OAC Capella Focus (1099+)'

; GRATING, DETECTOR
; Set the grating and detector corresponding to the
; FITS files - these values are directly passed to
; obs_anal.
;
; foc_grating = 'HETG'      ; 'HETG' or 'LETG'
; foc_detector = 'ACIS-S'   ; 'ACIS-S', 'HRC-S', 'ACIS-S' or 'HRC-I'
;
foc_grating = 'HETG'
foc_detector = 'ACIS-S'

; COORDINATES, and ASPECT
; ACIS: The coordinates used can be 'TDET' or 'DET'.
; HRC: use 'DET'.
; 
; foc_oa_coords = 'TDET'  ; 'TDET','DET','Sky' coords for obs_anal to use
; foc_oa_aspect = 1       ; 0 = no auto-aspect solution in obs_anal
;                        ; 1 = do auto-aspect solution in obs_anal
;
foc_oa_coords = 'Sky'
foc_oa_aspect = 0

; FOCUS OFFSETS
; These are the commanded offsets coresponding to the exposures;
; the three HETG ones are:
;
; foc_focs = [0.0, -0.2, 0.2]  ; mm
;
foc_focs = [0.0, -0.2, 0.2]

; OBS_ANAL OUTPUT PREFIX NAMES FOR THESE FILES
; These names can stay the same even as the
; FITS files may have varied names.  Further
; processing will use products with these names
; as prefix instead of the FITS file names.
;
; foc_names = ['fz','fm','fp']
;
foc_names = ['fz','fm','fp']

; LEVEL ~1 FITS FILES
; The Level 1ish files to be analyzed are pointed to
; here.  Absolute paths are given so that the
; files may be anywhere.  Note that they could
; be put in the foc_results_dir if desired for 
; completeness.
;
; Set to dd's MARX simulations files at MIT
; foc_fits = '/nfs/spectra/d0/MARX' + '/' + $
;		['O-HAS-Capella-3.001/i0/Capella-3.001.fits', $
;		'O-HAS-Capella-3.003/i0/Capella-3.003.fits', $
;		'O-HAS-Capella-3.002/i0/Capella-3.002.fits']
;
foc_fits = '/nfs/spectra/d0/MARX' + '/' + $
		['O-HAS-Capella-3.001/i0/Capella-3.001.fits', $
		'O-HAS-Capella-3.003/i0/Capella-3.003.fits', $
		'O-HAS-Capella-3.002/i0/Capella-3.002.fits']

; CUSTOM OBS_ANL 
; Each FITS file may need to have its own obs_anal.pro
; procedure(s) to tune things like time range analyzed,
; selection criteria, zero-order determination, etc.
; An array gives the names of these procedures.
; To make a custom obs_anal, the obs_anal.pro in the
; analysis directory can copied to obs_anal_<customname>.pro
; and the "PRO obs_anal" in the first line of the
; new file changed to "PRO obs_anal_<customname>".
; After editing the file, type:
;  hak> .run obs_anal_<customname>
; to see that it compiles.
;
; The foc_rollaxays values are angles in degrees to be
; passed to the obs_anal ROLLAXAY keyword to rotate the
; chosen coordinate about the zero-order before doing
; grating processing.  This allows Sky coordinates to be
; used: the ROLLAXAY value should be -1.0*<average ROLL in sol file>.
; See sol_plot.pro also.
;
; If a file is not yet available or has already been 
; analyzed its (re-)analysis can be skipped
; by setting its foc_oa_sel to 0 instead of 1.
;
; foc_oas = ['obs_anal','obs_anal','obs_anal']
; foc_rollaxays = [0.0,0.0,0.0]
; foc_oa_sel = [1,1,1]
;
foc_oas = ['obs_anal','obs_anal','obs_anal']
foc_rollaxays = [0.0,0.0,0.0]
foc_oa_sel = [1,1,1]

; OBS_ANAL OUTPUT DIRECTORY
; This is the output directory for all the junk created
; by obs_anal.pro...
;
; foc_obs_dir = '/nfs/spectra/d0/OAC/obs_990704'
;
foc_obs_dir = '/nfs/spectra/d0/OAC/obs_990704'

; FOCUS ANALYSIS RESULTS DIRECTORY
; This directory is the repository for the 
; results of the focus test analysis.
; * The user must create it.
; Several directories may be created, e.g., as new
; data sets arrive or as new processing parameters
; are tried.
;
; foc_results_dir = '/nfs/spectra/d0/OAC/foc_990704'
;
foc_results_dir = '/nfs/spectra/d0/OAC/foc_990704'

; GATHER FILE
; The results of the various observations analyses
; will be collected into this rdb file.  The foc_gather_sel
; can be used to select a subset of the results...
;
; foc_gather_file = 'fwhm_results.rdb'
; foc_gather_sel = [1,1,1]   ; 1 = include, 0 = don't include
;
foc_gather_file = 'fwhm_results.rdb'
foc_gather_sel = [1,1,1]   ; 1 = include, 0 = don't include

; OTHER GATHER PARAMETERS
; -- generally do not need to be modified --
; The gather source refers to the level 1.5 source number
; and is expected to be 'S1' for OAC HETG observations.
;
;foc_gather_source = 'S1'
;
foc_gather_source = 'S1'
 
; The gather method is a combination of aspect selected
; ('a') and the COORDS used ('TDET', 'DET').  Default
; is to set it based on foc_oa_coords and foc_oa_aspect:
; selected above
; if foc_oa_aspect EQ 1 then begin
;   foc_gather_meth = 'a'+foc_oa_coords
; end else begin
;   foc_gather_meth = foc_oa_coords
; end
;
if foc_oa_aspect EQ 1 then begin
  foc_gather_meth = 'a'+foc_oa_coords
end else begin
  foc_gather_meth = foc_oa_coords
end

; "GFR" STRUCTURE
; The gathered FWHM results are put into
; the structure "gfr" ("jeff-er") available in foc_common
; and at the command line.
; This structure can therefore be used by, e.g., foc_plot
; for input.  It can be explicitly filled from the foc_gather_file:
;  gfr = rdb_read(foc_results_dir+'/'+foc_gather_file)

; LINES WE EXPECT
; Energies for key lines expected... 
; ("lwe" = "lines we expect")
;
; foc_lwe = [0.653, 0.826, 1.022, 1.351, 1.472]
;
foc_lwe = [0.6536, 0.8258, 1.0217, 1.3520, 1.4724, 1.8638]

; foc_plot GLOBAL PARAMETERS
; Use the L1a or obs_anal-created dispersed event energies
;
; foc_L1a = 0
;
foc_L1a = 0

; -------------------------------------
;  END of SETTING PARAMETERS
; -------------------------------------


; -------------------------------------
; Summarize the parameters
; -------------------------------------

print, ''
print, '       foc_do_it_all, '+SYSTIME()

print, ' . . . . . . . . . . . . . . . . . . . . . . . . . . .'

foc_show_params

print, ' . . . . . . . . . . . . . . . . . . . . . . . . . . .'

; -------------------------------------
; END of parameter summary
; -------------------------------------


; -------------------------------------
; ANALYZE the FITS FILES
; -------------------------------------
; Run obs_anal on the FITS files
if KEYWORD_SET(OBSANAL) then begin
  print, ' /OBSANAL :'
  print, ''

  ; If things aren't too crazy we can loop over the 
  ; desired files.
  for ia = 0, n_elements(foc_oas)-1 do begin
    if foc_oa_sel(ia) EQ 1 then begin


      CALL_PROCEDURE, foc_oas(ia), foc_fits(ia), $
	DETECTOR=foc_detector, GRATING=foc_grating, $
	COORDS=foc_oa_coords, ASPECT=foc_oa_aspect, $
	CD_WIDTH=5.0, $
	/LINE_ANAL, $
	/ZB, /SILENT, $
	OUT_DIR=foc_obs_dir, OUTPUT_PREFIX=foc_names(ia)

    end
  end

end else begin
  print, ' No /OBSANAL : No (additional) analysis carried out.'
end
print, ''
; Show what analysis result files are available
; so they can be viewed with a browser...
html_files = FINDFILE(foc_obs_dir+'/*_summary.html',COUNT=nfound)
if nfound GE 1 then begin
  print, ' Files that can be viewed with HTML browser:'
  for ih=0,nfound-1 do begin
    print, '   ' + html_files(ih)
  end
end
print, ' . . . . . . . . . . . . . . . . . . . . . . . . . . .'
; -------------------------------------
; END of OBSANAL
; -------------------------------------


; -------------------------------------
; GATHER the various linelist rdb files 
; -------------------------------------
if KEYWORD_SET(GATHER) then begin

  print, ' /GATHER :'

  foc_gather


end else begin
  print, " No /GATHER : No (additional) gathering of line results."
end

print, ' . . . . . . . . . . . . . . . . . . . . . . . . . . .'
; -------------------------------------
; END of GATHER
; -------------------------------------


; -------------------------------------
; ANALYZE AND PLOT RESULTS
; -------------------------------------
if KEYWORD_SET(ANALYZE) then begin

  print, ' /ANALYZE :'

  ; differentiate the plot file name...
  if foc_L1a EQ 0 then L1a_str = '' else L1a_str = '_L1a'

  ; Read in the gathered FWHM results file
  gfr = rdb_read(foc_results_dir+'/'+foc_gather_file, /SILENT, $
		HEADER=gfr_header)

  !p.multi = 0  ; one plot pane

  ; - - - - - - Show the bright lines in the spectra - - - - -
  if foc_grating NE 'NONE' then begin

    ; Create a .ps file
    pre_print_landscape

    ; Sort the lines in energy order
    esort = SORT(gfr.energy)
    ; and print out all the energies
    print, gfr(esort).energy
    ; Where are the bright lines?
    plot_oo,  gfr(esort).energy, gfr(esort).roi_counts, PSYM=-4, $
	XRANGE=[0.5,2.0], XSTYLE=1, $
	TITLE = foc_project_title + ': ROI Counts vs Energy, All lines', $
	XTITLE = 'Energy (keV)', YTITLE='ROI counts'

    for il=0,n_elements(foc_lwe)-1 do begin
      oplot, foc_lwe(il)*[1., 1.], [1.0,1.E12], LINESTYLE=2
    end

    plot_creator_label, 'foc_do_it_all.pro'
    ; finish the plot
    device, /close
    set_plot, 'X'
    !p.multi = 0
    ; and save the idl.ps file to the results dir:
    SPAWN, 'cp idl.ps '+ foc_results_dir + '/roi_counts_vs_e.ps'
  end


  ; - - - - - - - - The good stuff - - - - 
  ; Make the focus plots...

  ; Zero-order (or No grating)

  ; setup .ps output, one plot in top-half of page
  pre_print_sqr
  !p.multi = 0

  ; This makes the plot
  foc_plot, 'Zero,Core'
  foc_plot, 'Zero,Strk', oplot=1

  plot_creator_label, 'foc_do_it_all.pro'
  ; finish the plot
  device, /close
  set_plot, 'X'
  !p.multi = 0
  ; and save the idl.ps file to the results dir:
  SPAWN, 'cp idl.ps '+ foc_results_dir + '/zero_order_focus'+L1a_str+'.ps'

  ; Diffracted orders
  if foc_grating NE 'NONE' then begin

    ; setup .ps output, one plot in top-half of page
    pre_print_sqr
    !p.multi = 0

    if foc_grating EQ 'HETG' then begin
      foc_plot, 'MEGm', foc_lwe(0)
      foc_plot, 'MEGm', foc_lwe(1), oplot=1
      foc_plot, 'MEGm', foc_lwe(2), oplot=2
      foc_plot, 'MEGm', foc_lwe(3), oplot=3
      foc_plot, 'MEGm', foc_lwe(4), oplot=4

      foc_plot, 'MEGp', foc_lwe(0)
      foc_plot, 'MEGp', foc_lwe(1), oplot=1
      foc_plot, 'MEGp', foc_lwe(2), oplot=2
      foc_plot, 'MEGp', foc_lwe(3), oplot=3
      foc_plot, 'MEGp', foc_lwe(4), oplot=4

      foc_plot, 'HEGm', foc_lwe(1)
      foc_plot, 'HEGm', foc_lwe(2), oplot=1
      foc_plot, 'HEGm', foc_lwe(3), oplot=2
      foc_plot, 'HEGm', foc_lwe(4), oplot=3
      foc_plot, 'HEGm', foc_lwe(5), oplot=4

      foc_plot, 'HEGp', foc_lwe(1)
      foc_plot, 'HEGp', foc_lwe(2), oplot=1
      foc_plot, 'HEGp', foc_lwe(3), oplot=2
      foc_plot, 'HEGp', foc_lwe(4), oplot=3
      foc_plot, 'HEGp', foc_lwe(5), oplot=4

    end else begin
      ; Place holder for LETG plots:
      foc_plot, 'LEGm', foc_lwe(0)
      foc_plot, 'LEGp', foc_lwe(0), oplot=1
      foc_plot, 'LEGm', foc_lwe(1), oplot=2
      foc_plot, 'LEGp', foc_lwe(1), oplot=3
    end

    plot_creator_label, 'foc_do_it_all.pro'
    ; finish the file
    device, /close
    set_plot, 'X'
    !p.multi = 0
    ; and save the idl.ps file to the results dir:
    SPAWN, 'cp idl.ps '+ foc_results_dir + '/diffracted_focus'+L1a_str+'.ps'

  end

  ; - - - - - - - - Example of using gfr structure - - - - 
  ; An example of working with the gfr structure directly
  ; in this case to compare FWHM error and ACF error -
  ; (value/value_err)^2 should be roughly the number of counts
  ; if the error is root-N ...
  ; These lines could be executed here (remove the double
  ; comments (";;") or typed at the hak> command line.
;;  !p.multi = [0,1,2]
;;  plot_oo, gfr.roi_counts, (gfr.acf/gfr.acf_err)^2, PSYM=4, $
;;	XRANGE=[1.E1, 1.E5], YRANGE=[1.E1, 1.E5]  
;;  plot_oo, gfr.roi_counts, (gfr.fwhm/gfr.fwhm_err)^2, PSYM=4, $
;;	XRANGE=[1.E1, 1.E5], YRANGE=[1.E1, 1.E5]
;;  !p.multi = 0

  ; - - - - - - - - Save the gfr to disk - - - - 
  ; The analysis modifies the dx_min and dx_min_err values in gfr
  ; so save it now:
  rdb_write, foc_results_dir+'/'+foc_gather_file,  gfr, $
	HEADER=gfr_header, /SILENT

end else begin
  print, " No /ANALYZE : Didn't create output plots."
end
print, ' . . . . . . . . . . . . . . . . . . . . . . . . . . .'
; -------------------------------------
; END of ANALYZE AND PLOT RESULTS
; -------------------------------------


RETURN
END
