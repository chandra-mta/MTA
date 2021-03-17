PRO lin_hist, values, bin_size, bin_values_out, bin_counts_out
;+
; PRO lin_hist, values, bin_size, bin_values_out, bin_counts_out
;
; Use equally spaced bins to form a histogram; the bin_values_out
; are correctly the centers of the bins.
;    --------------------------------------------------------
; 4/24/98 dd
; 4/26/99 dd Change "INDGEN" to LINDGEN to handle more than 32K bins!
;    --------------------------------------------------------
;-

binsize = ABS(bin_size)

bin_counts_out = HISTOGRAM(values, BINSIZE=binsize, OMAX=lmax, OMIN=lmin)

; Calculate the centers of the bins
nbins = n_elements(bin_counts_out)
cbins = lmin + (0.5+LINDGEN(nbins))*(lmax-lmin)/FLOAT(nbins)

bin_values_out = cbins

RETURN
END
