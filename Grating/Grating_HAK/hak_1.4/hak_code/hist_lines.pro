PRO hist_lines, hist_file, OUT_DIR=out_dir, $
	MOUSE=mouse, $
	OUTPUT_PREFIX=output_prefix, $
	SILENT=silent, ZBUFFER=zbuffer, $
        RES1KEV = res1kev
;+
; PRO hist_lines, hist_file, OUT_DIR=out_dir, $
;	MOUSE=mouse, $
;	OUTPUT_PREFIX=output_prefix, $
;	SILENT=silent, ZBUFFER=zbuffer
;       RES1KEV = res1kev;
;
; hist_lines.pro reads in an rdb histogram file and:
;   - finds "lines" in it
;   - shows and measures the FWHM of the lines (Gaussian fit)
;   - plots measured E/dE points along with expected flight
;     predictions.
;
; KEYWORDS:
;  OUT_DIR     - specifies directory where products are placed, default is
;                 present directory ( = '.'), trailing / not needed.
;  /MOUSE - user interactive, requires clicking to proceed to next plot
;  OUTPUT_PREFIX - returns the prefix for the files TO the calling routine
;  /ZBUFFER   - use set_plot, 'Z', so physical output device is not needed,
;               e.g., for batch or non-xterm (telnet) operation.
;  /SILENT    - suppress output to screen
;  RES1KEV    - returns an estimate of the resolving power at 1 keV
;               based on the average of lines in the 0.5 to 2.0 keV
;               range.  Of course if the source lines are broad this
;               will also be low.
;       ------------------------------------------------
; 2/1/99 dd
; 1999-02-09 dd Add .txt output file
; 1999-02-12 dd asthetic changes...
; 1999-02-20 dd out_dir and zbuffer added...
; 1999-03-08 dd try for more robust low-count fitting?!?
; 1999-03-31 dd Add fwhm and fwhm_err to output, add Herman's ACF too.
; 1999-05-23 dd Add SILENT keyword
; 1999-07-02 dd Create rdb format output file, added listing routine
;               hist_list_lines for text output, cleaned up plot...
; 1999-07-26 dd Added [ ]'s to plot_oo call to handle single E/dE point
; 1999-07-30 dd added nfound to unaccounted= ...
; 1999-08-07 dd added RES1KEV returned value
; 1999-08-09 dd more checking of WHERE()'s...
;       ------------------------------------------------
;-
; Common for fitting routines
@df_common

if NOT(KEYWORD_SET(OUT_DIR)) then out_dir = '.'

; Save the original device and plot values (thanks Jim!)
Orig_device = !d.name
Orig_plot = !p      ; save it all?
if KEYWORD_SET(ZBUFFER) then set_plot, 'Z' else set_plot, 'X'

iwind = 0
if KEYWORD_SET(ZBUFFER) then begin
  device, set_resolution=[700,700]
end else begin
  window, iwind, xsi=700, ysi=700
end

dd_load_ct, /OTHER
clr_org = 40
clr_grn = 125

; Read in the hist file:
hist_in = rdb_read(hist_file,/SILENT)

; Get the grating type
grat_str = 'meg'
if STRPOS(hist_file,'HEG') GE 0 then grat_str = 'heg'
if STRPOS(hist_file,'LEG') GE 0 then grat_str = 'leg'

; prefix for output .gif plots, etc.
; Get the last component of the filename and remove hist.rdb :
if 1 EQ 1 then begin
  pieces = STR_SEP(hist_file,'/')
  ; get the last piece...
  last_str = pieces(n_elements(pieces)-1)
  ; remove hist.rdb
  where_hist = STRPOS(STRUPCASE(last_str),'_HIST.RDB')
  if where_hist GT 0 then begin
    ; Use everything upto the HIST.RDB
    output_prefix = STRMID(last_str, 0, where_hist)
  end else begin
    ; OK, can't find hist.rdb, use it as is...
    output_prefix = last_str
  end
end

; set bins and counts arrays for histogram to analyze
bins = hist_in.bin
counts = hist_in.count
errs = hist_in.err

; Parameters
ge_min = 0.4 ; keV
if grat_str EQ 'heg' then ge_min = 0.6
if grat_str EQ 'leg' then ge_min = 0.06
ge_max = 7.0 ; keV
if grat_str EQ 'heg' then ge_max = 10.0
if grat_str EQ 'leg' then ge_max = 5.0

min_counts_at_peak = 10 ; counts

; This is the size to either side of a peak that is
; associated with the peak
feature_half_width = 24  ; bins

; Maximum number of feature to list...
max_n_feats = 45 ; enough is enough

; Number of panes to use for spectrum plot
npanes = 4

hc = 12.3985

flag_frac = 0.001 ; dE/E fraction to flag E_peak NE E_fit


if NOT(KEYWORD_SET(SILENT)) then begin
  print, ' - - - - - - - - - - Make List of Bright Lines - - - - - - - - - - - -'
  print, ''
end

maxbin = n_elements(bins)-1

; Keep track of which bins have been "extracted"
accounted = INTARR(n_elements(bins))

; Find the first feature:
nfeats = 0
fpeak = where(counts EQ MAX(counts),nfound)
these_counts = counts(fpeak(0))
nfeats = nfeats + 1
feat_peak_bins = [fpeak(0)]
low_bin = (feat_peak_bins(nfeats-1)-feature_half_width) > 0
high_bin = (feat_peak_bins(nfeats-1)+feature_half_width) < maxbin
accounted(low_bin:high_bin)=1

; Find the next one, if there is a next one
unaccounted = where(accounted EQ 0, nfound)
if nfound GE 1 then begin
  maxunaccounted = MAX(counts(unaccounted))
  fpeak = where(counts EQ maxunaccounted AND (accounted EQ 0),nfound)
  these_counts = counts(fpeak(0))

  ; Now loop until the "features" have less than min_counts_at_peak
  ; in their peak channel
  while these_counts GE min_counts_at_peak AND nfeats LT max_n_feats do begin
    ; save this peak/region
    nfeats = nfeats + 1
    feat_peak_bins = [feat_peak_bins,fpeak(0)]
    low_bin = (feat_peak_bins(nfeats-1)-feature_half_width) > 0
    high_bin = (feat_peak_bins(nfeats-1)+feature_half_width) < maxbin
    accounted(low_bin:high_bin)=1
    ; Find the next one
    unaccounted = where(accounted EQ 0, nfound)
    if nfound GT 0 then begin
      maxunaccounted = MAX(counts(unaccounted))
      fpeak = where(counts EQ maxunaccounted AND (accounted EQ 0),nfound)
      if nfound GT 0 then begin
        these_counts = counts(fpeak(0))
      end else begin
        these_counts = -1
      end
    end else begin
      these_counts = -1
    end
  end
end

; Sort these by energy
sorte = SORT(bins(feat_peak_bins))
feat_peak_bins = feat_peak_bins(sorte)

; Show what we've done...
; Plot the spectrum stretched out
!p.multi=[0,1,npanes]
for ip=0,npanes-1 do begin
  pmin = ge_min * (ge_max/ge_min)^((0.+ip)/npanes)
  pmax = ge_min * (ge_max/ge_min)^((1.+ip)/npanes)
  if ip EQ 0 then begin
    plot_io, bins, counts, PSYM=10, $
	XSTYLE=1, XRANGE=[pmin,pmax], $
	YSTYLE=1, YRANGE=[0.5,2.*MAX(counts)], $
	TITLE='Spectrum from '+output_prefix, $
	XTITLE='Energy (keV)', YTITLE='Counts/bin', $
	CHARSIZE=1.71
  end else begin
    plot_io, bins, counts, PSYM=10, $
	XSTYLE=1, XRANGE=[pmin,pmax], $
	YSTYLE=1, YRANGE=[0.5,2.*MAX(counts)], $
	XTITLE='Energy (keV)', YTITLE='Counts/bin', $
	CHARSIZE=1.71
  end
  oplot, [pmin,pmax], min_counts_at_peak*[1.,1.], LINESTYLE=1
  oplot, bins(feat_peak_bins), counts(feat_peak_bins), $
	SYMSIZE=1.6, THICK=1.5, PSYM=4, COLOR=clr_grn
end

; Finish the .gif output
if NOT(KEYWORD_SET(ZBUFFER)) then wshow,iwind,iconic=0
image = tvrd()
tvlct, red, green, blue, /GET
write_gif, out_dir+'/'+output_prefix+'_specpanes.gif', image, red, green, blue


if KEYWORD_SET(MOUSE) then begin
; List to screen the selected peaks while plot is up...
  print, ' Selected '+STRCOMPRESS(nfeats)+' peaks.'
  print, ''
  print, 'index    Energy  Wavelength  Peak_counts'
  for ip=0,nfeats-1 do begin
    print, STRING(ip, FORMAT='(I4)')+'   '+$
  	STRING(bins(feat_peak_bins(ip)),FORMAT='(F8.4)')+ $
  	STRING(hc/bins(feat_peak_bins(ip)),FORMAT='(F10.3)')+ $
  	'     '+STRING(counts(feat_peak_bins(ip)),FORMAT='(I6)')
  end
  print, ''
  print, '    !!! Click Mouse anywhere to Continue !!!'
  print, ''
  cursor, x, y, 3
end

; Now zoom in on each line
;  - plot the line region
;  - measure the E/dE w/Gaussian fit
;  - oplot the fit
;  - save measured Epeak and E/dE values

meas_peaks = FLTARR(nfeats)
meas_peakerrs = FLTARR(nfeats)
roi_counts = FLTARR(nfeats)
meas_fwhms = FLTARR(nfeats)
meas_fwhmerrs = FLTARR(nfeats)
meas_acfs = FLTARR(nfeats)
meas_acferrs = FLTARR(nfeats)

; Setup for enough plots...
ncols = FIX(SQRT(FLOAT(nfeats)))+1
nrows = ncols - 1
if nrows*ncols LT nfeats then nrows = ncols
!p.multi = [0,ncols,nrows]

for ip=0,nfeats-1 do begin
  peak_bin = feat_peak_bins(ip)
  peak_e = bins(peak_bin)
  bin_low = (peak_bin - feature_half_width) > 0
  bin_high = (peak_bin + feature_half_width) < maxbin
  roi_counts(ip) = TOTAL(counts(bin_low:bin_high))

  ; Fit the data with a gaussian...
  ; Guess fit parameters [height, center, gauss_sigma, continuum]
  ; guess a sigma which corresponds to FWHM ~ 1/5 of total span:
  guess_sigma = 0.2* (bins(bin_high) - bins(bin_low)) / 2.35
  a_inout = [max(counts(bin_low:bin_high)), peak_e, guess_sigma, $
		1.0]
  ; flat continuum
  df_continuum = 0.*bins(bin_low:bin_high) + 1.0
  df_fit, 1, bins(bin_low:bin_high), counts(bin_low:bin_high), a_inout, $
		(errs(bin_low:bin_high) > 2), sig, yfit

  ; Save fitting results
  meas_peaks(ip) = a_inout(1)
  meas_peakerrs(ip) = sig(1)
  meas_fwhms(ip) = a_inout(2)*2.35
  meas_fwhmerrs(ip) = sig(2)*2.35

  ; Herman's ACF:
  acf_array = FLOAT(counts(bin_low:bin_high))
  acf_herman, acf_array, acf_val, acf_err
  meas_acfs(ip) = acf_val
  meas_acferrs(ip) = acf_err

  ; Plot the data
  plot, bins(bin_low:bin_high), counts(bin_low:bin_high), PSYM=10, $
	XSTYLE=1, $
	YSTYLE=1, YRANGE=[0.,1.1*counts(peak_bin)], $
	TITLE = STRING(bins(peak_bin),FORMAT='(F8.4)')+' keV', $
	CHARSIZE=1.4
  ; add the fit
  oplot, bins(bin_low:bin_high), yfit, COLOR=clr_org
end

; Finish the .gif output
if NOT(KEYWORD_SET(ZBUFFER)) then wshow,iwind,iconic=0
image = tvrd()
tvlct, red, green, blue, /GET
write_gif, out_dir+'/'+output_prefix+'_linefits.gif', image, red, green, blue

; Line list output to an rdb file:
rdb_file = out_dir+'/'+output_prefix+'_linelist.rdb'
; and text file:
txt_file = out_dir+'/'+output_prefix+'_linelist.txt'

; Create the header
rdb_header = ['# hist_lines.pro output, '+SYSTIME()]
rdb_header = [rdb_header, '# filename:	'+rdb_file]
rdb_header = [rdb_header, '# histogram_file:	'+hist_file]
rdb_header = [rdb_header, '# grating:	'+STRUPCASE(grat_str)]
rdb_header = [rdb_header, '# e_explored_min:	'+STRCOMPRESS(ge_min)]
rdb_header = [rdb_header, '# e_explored_max:	'+STRCOMPRESS(ge_max)]
rdb_header = [rdb_header, '# n_peaks_found:	'+STRCOMPRESS(nfeats)]
rdb_header = [rdb_header, '# ']
; print this to screen if desired
if NOT(KEYWORD_SET(SILENT)) then begin
  for ih=0,n_elements(rdb_header)-1 do print, rdb_header(ih)
end

; Include column notes...
rdb_header = [rdb_header, '# Column defintion notes:']
rdb_header = [rdb_header, '#  peak_bin_energy']
rdb_header = [rdb_header, '#  peak_bin_count']
rdb_header = [rdb_header, '#  peak_flag        = 1 if peak and fit energies '+ $
		'differ by more than '+ $
		STRING(100.0*flag_frac,FORMAT='(F7.3)')+'% )']	
rdb_header = [rdb_header, '#  energy']
rdb_header = [rdb_header, '#  energy_err']
rdb_header = [rdb_header, '#  fwhm']
rdb_header = [rdb_header, '#  fwhm_err']
rdb_header = [rdb_header, '#  ede']
rdb_header = [rdb_header, '#  roi_counts']
rdb_header = [rdb_header, '#  acf']
rdb_header = [rdb_header, '#  acf_err']
rdb_header = [rdb_header, '# ']

; Setup the structure
one_row = {peak_bin_energy:0.0, peak_bin_count:0, peak_flag:0, $
		energy:0.0, energy_err:0.0, $
		fwhm:0.0, fwhm_err:0.0, $
		ede:0.0, roi_counts:0.0, $
		acf:0.0, acf_err:0.0}


struct = REPLICATE(one_row, nfeats)

; Fill the values
for ip=0,nfeats-1 do begin
  struct(ip).peak_bin_energy = bins(feat_peak_bins(ip))
  struct(ip).peak_bin_count = counts(feat_peak_bins(ip))

  struct(ip).energy = meas_peaks(ip)
  struct(ip).energy_err = meas_peakerrs(ip)
		
  struct(ip).fwhm = meas_fwhms(ip)
  struct(ip).fwhm_err = meas_fwhmerrs(ip)
		
  struct(ip).ede = meas_peaks(ip)/meas_fwhms(ip)
  struct(ip).roi_counts = roi_counts(ip)
		
  struct(ip).acf = meas_acfs(ip)
  struct(ip).acf_err = meas_acferrs(ip)

  ; Flag suspicious peaks
  struct(ip).peak_flag = 0
  ; If the fit peak is far from the peak bin (includes case where fit
  ; peak is NaN.)
  if NOT(approx_equal(bins( feat_peak_bins(ip)), meas_peaks(ip), $
	flag_frac )) then struct(ip).peak_flag = 1
end

; list the values to the screen if desired and
; to a text file in any case
if NOT(KEYWORD_SET(SILENT)) then begin
  hist_list_lines, struct, FILE=txt_file
end else begin
  hist_list_lines, struct, FILE=txt_file, /SILENT
end

; and write out the file
rdb_write, rdb_file, struct, HEADER = rdb_header, /SILENT

if KEYWORD_SET(MOUSE) then begin
  print, '    !!! Click Mouse anywhere to Continue !!!'
  print, ''
  cursor, x, y, 3
end

; Make an E/dE vs E plot
!p.multi = 0

plot_oo, [struct.energy], [struct.ede], PSYM=4, $
	XRANGE=[ge_min, ge_max], XSTYLE=1, $
	YRANGE=[50.0,4000.0], YSTYLE=1, $
	TITLE = 'Resolving Power Measurments and Expectations', $
	XTITLE = 'Energy (keV)', YTITLE='Resolving Power = E/dE_FWHM'

; mark the more significant ones
sel = where(struct.fwhm_err/struct.fwhm LT 0.1, nfound)
if nfound GE 1 then begin
  oplot, [struct(sel).energy], [struct(sel).ede], PSYM=2
end

; and add error bars to reasonably significant ones
sel = where(struct.fwhm_err/struct.fwhm LT 0.2, nfound)
res1keV = 0.0  ; default if no significant lines
if nfound GE 1 then begin
  plot_errors, struct(sel).energy, struct(sel).energy, struct(sel).energy, $
		struct(sel).energy/(struct(sel).fwhm + struct(sel).fwhm_err), $
		struct(sel).energy/(struct(sel).fwhm - struct(sel).fwhm_err)
  ; Also use these measurements in the range 0.5 to 2.0 keV
  ; to estimate the 1 keV resolving power
  sigones = struct(sel)
  inrange = where(sigones.energy GT 0.5 AND sigones.energy LT 2.0, nin)
  if nin GE 1 then begin
    res1keV = TOTAL(sigones(inrange).energy * sigones(inrange).ede ) / $
		n_elements(inrange)
  end
end

; and overplot the conservative/optimistic E/dE expectations for
; this grating type
if grat_str NE 'leg' then begin
  if STRPOS(!DDLOCATION, 'HAK') LT 0 then begin
    ; CALDB location of the files
    cipsdir = !DDHETGCAL+'/cip'
  end else begin
    ; HAK Stand-alone location of the files
    cipsdir = !DDHAKDATA
  end
  res_opt = rdb_read(cipsdir+'/hetg'+grat_str+'D1996-11-01res_optN0002.rdb', $
	/SILENT)
  res_con = rdb_read(cipsdir+'/hetg'+grat_str+'D1996-11-01res_conN0002.rdb', $
	/SILENT)
end else begin
  if STRPOS(!DDLOCATION, 'HAK') LT 0 then begin
    ; CALDB location of the files
    cipsdir = !DDLETGCAL+'/cip'
  end else begin
    ; HAK Stand-alone location of the files
    cipsdir = !DDHAKDATA
  end
  res_opt = rdb_read(cipsdir+'/letgD1996-11-01res_optN0002.rdb', /SILENT)
  res_con = rdb_read(cipsdir+'/letgD1996-11-01res_conN0002.rdb', /SILENT)
end

oplot, res_opt.energies, res_opt.respower, LINESTYLE=2
oplot, res_con.energies, res_con.respower, LINESTYLE=1

; Finish the .gif output
if NOT(KEYWORD_SET(ZBUFFER)) then wshow,iwind,iconic=0
image = tvrd()
tvlct, red, green, blue, /GET
write_gif, out_dir+'/'+output_prefix+'_eoverde.gif', image, red, green, blue


; Reset the device and plot parameters...
set_plot, Orig_device
!p = Orig_plot      ; restore it all?

RETURN
END
