PRO log_hist, values, bin_ratio, bin_values_out, bin_counts_out
;+
; PRO log_hist, values, bin_ratio, bin_values_out, bin_counts_out
;
; Use log spaced bins to form a histogram; the bin_values_out
; are correctly calculated bin centers.
;     --------------------------------------------------------
; 1/26/98 dd
; 4/26/99 dd Change INDGEN to LINDGEN to handle more than 32 k bins...
;     --------------------------------------------------------
;-

; For example: (using ACIS XRCF Al-K data file)
;
; ddIDL> restore, '/nfs/spectra/d6/ACIS_anal/H-HAS-PI-1.001_l1.idlsav'
; ddIDL> log_hist, l1.energy, 1.1, es, counts
; ddIDL> plot_oi, es, counts, PSYM=10
; (now use only GRADE 0 events!)
; ddIDL> sel = where(l1.grade ne 7)
; ddIDL> log_hist, l1(sel).energy, 1.1, es, counts
; ddIDL> plot_oi, es, counts, PSYM=10
;

; Catch negative values
pvs = where(values GT 0.0)
if n_elements(pvs) NE n_elements(values) then begin
  print, 'log_hist:  Found negative/zero values!  Ignoring them.' 
end
lvs = ALOG(values(pvs))

; The bin_ratio is the ratio of bin i+1 to bin i centers
; e.g., 1.1
lbinsize = ABS(ALOG(bin_ratio))

bin_counts_out = HISTOGRAM(lvs, BINSIZE=lbinsize, OMAX=lmax, OMIN=lmin)

; Calculate the log centers of the bins
nbins = n_elements(bin_counts_out)
lbins = lmin + (0.5+LINDGEN(nbins))*(lmax-lmin)/FLOAT(nbins)

bin_values_out = EXP(lbins)

RETURN
END
