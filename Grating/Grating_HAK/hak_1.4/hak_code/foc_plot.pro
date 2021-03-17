PRO foc_plot, part_sel, energy_sel, ACF=acf, L1a = l1a, $
	OPLOT = n_oplot, DX_MIN = dx_min, DX_MIN_ERR = dx_min_err, $
	VERBOSE=verbose, XRANGE=xrange, YRANGE=yrange
;+
; PRO foc_plot, part_sel, energy_sel, ACF=acf, L1a = l1a, $
;	OPLOT = n_oplot, DX_MIN = dx_min, DX_MIN_ERR = dx_min_err, $
;	VERBOSE=verbose, XRANGE=xrange, YRANGE=yrange
;
; Plot FWHM vs defocus value and fit the values to
; a simple model of the dependence, see:
;
;   http://space.mit.edu/HETG/flight/oac.html#defocus
;
;    --------------------------------------------------
; 7/5/99 dd Initial version
; 7/7/99 dd Add dx_min return on command line
; 8/10/99 dd add meth_sel to plot label;
; 8/11/99 dd add foc_project_title; set L1a based on 
;       foc_L1a; fill gfr.dx_min;
; 8/12/99 dd foc_streak not needed?
; 8/14/99 dd Add "verbose" keyword to show more to screen and plot;
;            change selection method to loop over the defocus
;            values and for each do a where() on all criteria with a
;            broad energy acceptance (e.g., 0.02*energy) and keep the ONE
;            entry with the largest peak_bin_count: this will prevent
;            accepting "little energy neighbors" and reduce losing lines
;            if the energy is off a bit.
; 8/20/99 dd Add XRANGE,YRANGE; 
; 8/22/99 dd "1/ACF" or "FWHM" in labels,
;    --------------------------------------------------
;-

@foc_common

; Out of the "gathered FWHM results" structure, gfr in common,
; select a set of lines based on some criteria.
; The gfr tags are:
; NAME FOCUS SPEC_PART GRAT_CODE ORDER PROC_METH SOURCE
; ENERGY PEAK_BIN_COUNT ROI_COUNTS FWHM FWHM_ERR ACF ACF_ERR
; (DX_MIN DX_MIN_ERR)

; Select SPEC_PART, PROC_METH, SOURCE, ENERGY and
; then analyze FWHM (or ACF) vs FOCUS for the selection.

struct_defn = {name:'', focus:0.0, spec_part:'', $
		grat_code:0, order:0, $
		proc_meth:'', source:'', $
		peak_bin_count:0.0, $
		energy:0.0, roi_counts:0.0, $
		fwhm:0.0, fwhm_err:0.0, $
		acf:0.0, acf_err:0.0, $
		dx_min:0.0, dx_min_err:0.0}

; Defaults...
if n_elements(part_sel) EQ 0 then part_sel = 'Zero,Core'
if n_elements(n_oplot) EQ 0 then n_oplot = 0
if n_elements(XRANGE) EQ 0 then begin
  xrange = [-0.6, 0.6]  ; default for HETG focus test
end
if n_elements(YRANGE) EQ 0 then begin
  yrange = [0.7, 3.5]  ; default for HETG focus test, FWHM ratio
end
; overplot symbols
plt_syms = [6,2,5,7,1,4,6]

meth_sel = foc_gather_meth
if n_elements(L1a) EQ 0 then L1a = foc_L1a
if KEYWORD_SET(L1a) then meth_sel = 'L1a'

if STRPOS(part_sel,'Zero') GE 0 then begin
  sel = where( (STRPOS(gfr.SPEC_PART, part_sel) GE 0) AND $
	gfr.PROC_METH EQ meth_sel AND $
	gfr.SOURCE EQ foc_gather_source, nfound)
end else begin
  ; Loop over the focus offsets
  nsel = 0
  savesel = [0]
  for iff=0, n_elements(foc_focs)-1 do begin
    this_sel = where( (STRPOS(gfr.SPEC_PART, part_sel) GE 0) AND $
	gfr.PROC_METH EQ meth_sel AND $
	gfr.SOURCE EQ foc_gather_source AND $
	approx_equal(gfr.ENERGY, energy_sel,0.02*energy_sel) AND $
	approx_equal(gfr.focus, foc_focs(iff), 0.01), nfound )
    if nfound GE 1 then begin
      ; find the largest peak_bin_count value
      pbcsort = SORT(-1.0*gfr(this_sel).peak_bin_count)
      pbcsel = this_sel(pbcsort(0))
      ; add it to the list
      savesel = [savesel, [pbcsel]]
      nsel = nsel + 1
    end
  end
  ; OK, fill "sel" from savesel:
  if nsel GT 0 then begin
    nfound = nsel
    sel = savesel(1:nsel)
  end else begin
    nfound = 0
    sel = -1
  end
end

if KEYWORD_SET(VERBOSE) then begin
  print, ''
  print, ' Number matching the criteria = '+STRING(nfound)
  for im=0,nfound-1 do print, gfr(sel(im))
end

if nfound LE 1 then begin
  print, '* foc_plot: Less than 2 points: No plotting carried out :(
  print, '  part_sel = '+part_sel
  if n_elements(energy_sel) GT 0 then begin
    print, '  energy_sel = '+STRCOMPRESS(energy_sel)
  end
  print, ''
  RETURN
end

if KEYWORD_SET(ACF) then begin
  fwhm_vals = 1.0/gfr(sel).acf
  fwhm_errs = fwhm_vals - 1.0/(gfr(sel).acf + gfr(sel).acf_err)
  fwhm_name = '1/ACF'
end else begin
  fwhm_vals = gfr(sel).fwhm
  fwhm_errs = gfr(sel).fwhm_err
  fwhm_name = 'FWHM'
end

dx_vals = gfr(sel).focus

charsize = 1.0

; X-array to plot the fit curve
nfine = 100
fxvs = (xrange(1)-xrange(0))*indgen(nfine+1)/FLOAT(nfine) + xrange(0)

plot_title = foc_project_title+': Focus Plot'

; Show the values
if n_oplot EQ 0 then begin
  plot, dx_vals, (fwhm_vals/MIN(fwhm_vals))^2, PSYM=plt_syms(n_oplot), $
	SYMSIZE = 1.4, $
	TITLE = plot_title, charsize = charsize, $
	XTITLE = 'Commanded Defocus (mm)', $
	YTITLE = '[ '+fwhm_name+'(dx) / MIN('+fwhm_name+') ]^2', $
	XRANGE=xrange, XSTYLE=1, $
	YRANGE=yrange, YSTYLE=1
end else begin
  oplot, dx_vals, (fwhm_vals/MIN(fwhm_vals))^2, PSYM=plt_syms(n_oplot), $
	SYMSIZE = 1.4
end

; and errors...
error_bar_offset = 0.0 
err_dx_vals = dx_vals + error_bar_offset
plot_errors, err_dx_vals-0.005, err_dx_vals, err_dx_vals+0.005, $
	((fwhm_vals+fwhm_errs)/MIN(fwhm_vals))^2, $
	((fwhm_vals-fwhm_errs)/MIN(fwhm_vals))^2

if nfound LE 2 then begin
  print, '* foc_plot: Only 2 points: No fitting carried out :(
  print, '  part_sel = '+part_sel
  if n_elements(energy_sel) GT 0 then begin
    print, '  energy_sel = '+STRCOMPRESS(energy_sel)
  end
  print, ''
  RETURN
end

; Do a fit to the values
result = POLY_FIT(dx_vals, (fwhm_vals/MIN(fwhm_vals))^2, 2, Yfit)

dx_min = -1.0*result(1)/(2.*result(2))
oplot, fxvs, 0.+ result(0) + result(1)*fxvs + result(2)*fxvs^2, $
	LINESTYLE=2, THICK=2.0

; Now estimate the error by resampling the data points, and
; fitting...  Plot the resampled curves too.
nresamp = 100
ntrysmax = 500
dx_mins = FLTARR(nresamp)
ave_curve = 0.0 * fxvs
ire = 0
itrys = 0
; Only accept fits which have positive x^2 term!
while (ire LT (nresamp-1)) AND (itrys LT ntrysmax) do begin
  re_vals = fwhm_vals
  re_errs = fwhm_errs
  ;
  re_vals = re_vals + re_errs*RANDOMN(SEED, n_elements(re_vals)) 
  result = POLY_FIT(dx_vals, (re_vals/MIN(re_vals))^2, 2, Yfit)
  if result(2) GT 0.0 then begin
    re_min = -1.0*result(1)/(2.*result(2))
    curve = 0.+ result(0) + result(1)*fxvs + result(2)*fxvs^2
    ; if VERBOSE then show the resampled curves
    if KEYWORD_SET(VERBOSE) then begin
      oplot, fxvs, curve, LINESTYLE=1
    end
    ave_curve = ave_curve + curve
    dx_mins(ire) = re_min
    ire = ire + 1
  end
  itrys = itrys + 1
end
if itrys EQ ntrysmax then begin
  print, '* foc_plot: reached ntrysmax and no pos-curvature solutions !?!'
  print, '  part_sel = '+part_sel+',  energy_sel = '+STRCOMPRESS(energy_sel)
  print, ''
  RETURN
end
dx_mins = dx_mins(0:ire-1)
nresamp = n_elements(dx_mins)
ave_curve = ave_curve/FLOAT(nresamp)
oplot, fxvs, ave_curve, THICK=2.0

; Get rid of the outliers
dx_mins = dx_mins(SORT(dx_mins))
dx_mins = dx_mins(nresamp/20:(19*nresamp)/20)
nresamp = n_elements(dx_mins)

dx_min_ave = TOTAL(dx_mins)/FLOAT(nresamp)
dx_min_err = SQRT(TOTAL((dx_mins - dx_min_ave)^2)/FLOAT(nresamp-1))

if KEYWORD_SET(VERBOSE) then begin
  print, ''
  print, '      Dx_Min  = ', dx_min
  print, ' Resample:'
  print, '     Min Ave  = ', dx_min_ave
  print, '       Error  = ', dx_min_err
  print, ''
  print, ' Measured values = ', fwhm_vals
  print, ' Commanded focus = ', dx_vals
  print, ' Ratio^2 at Min Ave = ', MIN(ave_curve)
  print, ' '+fwhm_name+' at Min Ave = ', SQRT(MIN(ave_curve))*MIN(fwhm_vals)
  print, '    ---------------------------------------- '
end

; Put the dx_min_ave and dx_min_err values into the gather FWHM results array
for is=0,n_elements(sel)-1 do begin
  gfr(sel(is)).dx_min = dx_min_ave
  gfr(sel(is)).dx_min_err = dx_min_err
end

; Add a label

yloc = TOTAL([0.1,0.9]*yrange)
yspace = 0.12
xloc = TOTAL([0.8,0.2]*xrange)

if STRPOS(part_sel, 'Zero') GE 0 then begin
  label_part = part_sel + ' ['+meth_sel+']'
end else begin
  label_part = part_sel + ' at '+STRING(energy_sel,FORMAT='(F7.4)') + $
	' keV ['+meth_sel+']'
end

oplot, [xloc,xloc+0.07], [yloc,yloc]-yspace*n_oplot, $
	PSYM=-1*plt_syms(n_oplot), SYMSIZE = 1.4
xyouts, xloc+0.1, yloc-(0.02 + yspace*n_oplot), ' ' + $
	'dx_min_ave ='+STRCOMPRESS(STRING(dx_min_ave,FORMAT='(F8.3)'))+ $
	' +/-'+STRCOMPRESS(STRING(dx_min_err,FORMAT='(F8.3)'))+ $
	' mm,  '+label_part, $
	CHARSIZE = charsize

RETURN
END






