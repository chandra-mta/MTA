PRO foc_show_params
;+
; PRO foc_show_params
;
; List the parameter values in the foc_common.
;    --------------------------------------
; 8/12/99 dd Changes for new parameters...
;    --------------------------------------
;-

@foc_common

print, '   PARAMETERS in foc_common (available at command line):'
print, ''
print, ' foc_project_title = '+foc_project_title
print, ''
print, ' foc_grating = '+foc_grating
print, ' foc_detector = '+foc_detector
print, ''
print, 'OBSANAL:'
print, ''
print, ' Focus names, values, obs_anal, rollaxay, sel, and FITS files:'
for ia=0,n_elements(foc_focs)-1 do begin
  print, '  '+foc_names(ia) + ' : ' + STRING(foc_focs(ia)) + $
	' mm,   ' + foc_oas(ia)+ '  ' + $
	STRCOMPRESS(foc_rollaxays(ia)) + '  ' + $
	STRCOMPRESS(foc_oa_sel(ia)) + '  ' + foc_fits(ia)
end
print, ''
print, ' foc_oa_coords = '+foc_oa_coords
print, ' foc_oa_aspect [0|1] = '+STRING(foc_oa_aspect,FORMAT='(I2)')
print, ''
print, ' foc_obs_dir = '+foc_obs_dir
print, ''
print, 'GATHER:'
print, ''
print, ' foc_results_dir = '+foc_results_dir
print, ' foc_gather_file = '+foc_gather_file
gath_str = ''
for ig=0,n_elements(foc_gather_sel)-1 do gath_str = gath_str + $
	STRCOMPRESS(foc_gather_sel(ig))
print, ' foc_gather_sel = '+ gath_str
print, ' foc_gather_source = '+ foc_gather_source
print, ' foc_gather_meth = '+ foc_gather_meth
print, ''
print, ' gfr ("jeff-er") n_elements = ' + STRING(n_elements(gfr))
print, ''
print, 'ANALYZE:'
print, ''
print, ' foc_L1a [0,1] = '+STRCOMPRESS(foc_L1a)
print, ' foc_lwe (keV) = '
print, foc_lwe
print, ''

RETURN
END
