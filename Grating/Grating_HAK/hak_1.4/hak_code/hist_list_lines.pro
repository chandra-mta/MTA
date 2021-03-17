PRO hist_list_lines, struct, SILENT=silent, FILE_OUT=file_out, $
	LAMBDA=lambda
;+
; PRO hist_list_lines, struct, SILENT=silent, FILE_OUT=file_out
;
; Make a nice text listing of the linelist structure.
; FILE_OUT can specify the full file spec for text output.
; SILENT supresses output to screen.
;   --------------------------------------------------
; 7/2/99 dd
;   --------------------------------------------------
;-

if KEYWORD_SET(LAMBDA) then begin
; -----
if NOT(KEYWORD_SET(SILENT)) then begin
  ; Print the headings
  print, ''
  print, ' |- - peak - -|  '+ $
	' | - - - fit - - - - - - |                ROI'
  print, '  Lambda  counts '+ $
	'  Lambda    FWHM,error(mA)' + $
	'      E/dE    counts      acf     acf_err'
  print, ' - - - - - - - - - - - - - - - - - - - - - - - - - - - - -' +$
	' - - - - - - - - - - - - -'
  ; and the lines
  for ip=0, n_elements(struct)-1 do begin
    flag_str = '   '
    if struct(ip).peak_flag EQ 1 then flag_str = ' * ' 
    print, ' '+STRPAD(struct(ip).peak_bin_lam,8,/COMP)+'  '+ $
	STRPAD(FIX(struct(ip).peak_bin_count),4,/COMP,/RIGHT)+'   '+ $
	STRPAD(struct(ip).lam, 8, /COMP) + flag_str + $
	STRPAD(STRING(1.E3 * struct(ip).fwhm,FORMAT='(F8.3)'), 8,/COMPRESS) + $
	STRPAD(STRING(1.E3 * struct(ip).fwhm_err,FORMAT='(F8.3)'), 8,/COMPRESS) + $
	STRPAD(STRING(struct(ip).ede, FORMAT='(F9.1)'), 9, /RIGHT) + $
	STRPAD(FIX(struct(ip).roi_counts), 8,/COMP,/RIGHT) + '    ' + $
	STRPAD(STRING(struct(ip).acf,FORMAT='(F10.6)'), 10,/COMPRESS) + $
	STRPAD(STRING(struct(ip).acf_err,FORMAT='(F10.6)'), 10,/COMPRESS)
  end
  print, ''
end


  ; Put it in a file if desired...
if n_elements(file_out) GT 0 then begin
  OPENW, out_unit, file_out, /GET
  ; copy from above with print --> printf, out_unit 
  printf, out_unit, ''
  printf, out_unit, ' |- - peak - -|  '+ $
	' | - - - fit - - - - - - |                ROI'
  printf, out_unit, '  Lambda  counts '+ $
	'  Lambda    FWHM,error(mA)' + $
	'      E/dE    counts      acf     acf_err'
  printf, out_unit, ' - - - - - - - - - - - - - - - - - - - - - - - - - - - - -' +$
	' - - - - - - - - - - - - -'
  for ip=0, n_elements(struct)-1 do begin
    flag_str = '   '
    if struct(ip).peak_flag EQ 1 then flag_str = ' * ' 
    printf, out_unit, ' '+STRPAD(struct(ip).peak_bin_lam,8,/COMP)+'  '+ $
	STRPAD(FIX(struct(ip).peak_bin_count),4,/COMP,/RIGHT)+'   '+ $
	STRPAD(struct(ip).lam, 8, /COMP) + flag_str + $
	STRPAD(STRING(1.E3 * struct(ip).fwhm,FORMAT='(F8.3)'), 8,/COMPRESS) + $
	STRPAD(STRING(1.E3 * struct(ip).fwhm_err,FORMAT='(F8.3)'), 8,/COMPRESS) + $
	STRPAD(STRING(struct(ip).ede, FORMAT='(F9.1)'), 9, /RIGHT) + $
	STRPAD(FIX(struct(ip).roi_counts), 8,/COMP,/RIGHT) + '    ' + $
	STRPAD(STRING(struct(ip).acf,FORMAT='(F10.6)'), 10,/COMPRESS) + $
	STRPAD(STRING(struct(ip).acf_err,FORMAT='(F10.6)'), 10,/COMPRESS)
  end
  printf, out_unit, ''
  ; end of copy/replace

  CLOSE, out_unit
  FREE_LUN, out_unit
end

end else begin
; -----
if NOT(KEYWORD_SET(SILENT)) then begin
  ; Print the headings
  print, ''
  print, ' |- - peak - -|  '+ $
	' | - - - fit - - - - - - |                ROI'
  print, '  Energy  counts '+ $
	'  Energy    FWHM,error(eV)' + $
	'      E/dE    counts      acf     acf_err'
  print, ' - - - - - - - - - - - - - - - - - - - - - - - - - - - - -' +$
	' - - - - - - - - - - - - -'
  ; and the lines
  for ip=0, n_elements(struct)-1 do begin
    flag_str = '   '
    if struct(ip).peak_flag EQ 1 then flag_str = ' * ' 
    print, ' '+STRPAD(struct(ip).peak_bin_energy,8,/COMP)+'  '+ $
	STRPAD(FIX(struct(ip).peak_bin_count),4,/COMP,/RIGHT)+'   '+ $
	STRPAD(struct(ip).energy, 8, /COMP) + flag_str + $
	STRPAD(STRING(1.E3 * struct(ip).fwhm,FORMAT='(F8.3)'), 8,/COMPRESS) + $
	STRPAD(STRING(1.E3 * struct(ip).fwhm_err,FORMAT='(F8.3)'), 8,/COMPRESS) + $
	STRPAD(STRING(struct(ip).ede, FORMAT='(F9.1)'), 9, /RIGHT) + $
	STRPAD(FIX(struct(ip).roi_counts), 8,/COMP,/RIGHT) + '    ' + $
	STRPAD(STRING(struct(ip).acf,FORMAT='(F10.6)'), 10,/COMPRESS) + $
	STRPAD(STRING(struct(ip).acf_err,FORMAT='(F10.6)'), 10,/COMPRESS)
  end
  print, ''
end


  ; Put it in a file if desired...
if n_elements(file_out) GT 0 then begin
  OPENW, out_unit, file_out, /GET
  ; copy from above with print --> printf, out_unit 
  printf, out_unit, ''
  printf, out_unit, ' |- - peak - -|  '+ $
	' | - - - fit - - - - - - |                ROI'
  printf, out_unit, '  Energy  counts '+ $
	'  Energy    FWHM,error(eV)' + $
	'      E/dE    counts      acf     acf_err'
  printf, out_unit, ' - - - - - - - - - - - - - - - - - - - - - - - - - - - - -' +$
	' - - - - - - - - - - - - -'
  for ip=0, n_elements(struct)-1 do begin
    flag_str = '   '
    if struct(ip).peak_flag EQ 1 then flag_str = ' * ' 
    printf, out_unit, ' '+STRPAD(struct(ip).peak_bin_energy,8,/COMP)+'  '+ $
	STRPAD(FIX(struct(ip).peak_bin_count),4,/COMP,/RIGHT)+'   '+ $
	STRPAD(struct(ip).energy, 8, /COMP) + flag_str + $
	STRPAD(STRING(1.E3 * struct(ip).fwhm,FORMAT='(F8.3)'), 8,/COMPRESS) + $
	STRPAD(STRING(1.E3 * struct(ip).fwhm_err,FORMAT='(F8.3)'), 8,/COMPRESS) + $
	STRPAD(STRING(struct(ip).ede, FORMAT='(F9.1)'), 9, /RIGHT) + $
	STRPAD(FIX(struct(ip).roi_counts), 8,/COMP,/RIGHT) + '    ' + $
	STRPAD(STRING(struct(ip).acf,FORMAT='(F10.6)'), 10,/COMPRESS) + $
	STRPAD(STRING(struct(ip).acf_err,FORMAT='(F10.6)'), 10,/COMPRESS)
  end
  printf, out_unit, ''
  ; end of copy/replace

  CLOSE, out_unit
  FREE_LUN, out_unit
end

;----
end

RETURN
END
