PRO rpf_list, rpf, HEADER=rpf_header, FILE_OUT=file_out, SILENT=silent
;+
; PRO rpf_list, rpf, HEADER=rpf_header, FILE_OUT=file_out, SILENT=silent
;
; This procedure lists to screen and/or file the contents of
; an rpf structure optionally preceeded by the header lines.
;
; For more information see:  <this_directory>/rpf_description.txt
;     -------------------------------------------------
; 7/3/99 dd
;     -------------------------------------------------
;-

; Make a string for each parameter's value
; depending on string or scalar type...
val_strings = STRARR(n_elements(rpf))
type_strings = STRARR(n_elements(rpf))
for ip=0, n_elements(rpf)-1 do begin
  if rpf(ip).DataType EQ 'StringValue' then begin
    val_strings(ip) = '"'+rpf(ip).StringValue+'"'
    type_strings(ip) = 'S'
  end else begin
    val_strings(ip) = STRCOMPRESS(STRING(rpf(ip).ScalarValue) + $
		 '  +/- '+ STRING(rpf(ip).Error) + '  ' + $
		rpf(ip).Unit)
    type_strings(ip) = 'N'
  end
end

name_width = MAX(strlen(rpf.Name))+2
desc_width = MAX(strlen(rpf.Description))+2
val_width = MAX(strlen(val_strings))+2

if NOT(KEYWORD_SET(SILENT)) then begin
  print, ''
  if n_elements(rpf_header) GT 0 then begin
    for ih=0,n_elements(rpf_header)-1 do begin
      print, ' '+rpf_header(ih)
    end
  end

  for ip=0, n_elements(rpf)-1 do begin
    print, ' '+type_strings(ip) + '   ' + $
	STRPAD(rpf(ip).Name,name_width, /RIGHT)+ ' : ' + $
	STRPAD(val_strings(ip),val_width)+ '  ' + $
	STRPAD(rpf(ip).Description,desc_width)
  end
  print, ''
end

if n_elements(FILE_OUT) GT 0 then begin
  OPENW, out_unit, file_out, /GET_LUN
  printf, out_unit, ''
  if n_elements(rpf_header) GT 0 then begin
    for ih=0,n_elements(rpf_header)-1 do begin
      printf, out_unit, ' '+rpf_header(ih)
    end
  end

  for ip=0, n_elements(rpf)-1 do begin
    printf, out_unit, ' '+type_strings(ip) + '   ' + $
	STRPAD(rpf(ip).Name,name_width, /RIGHT)+ ' : ' + $
	STRPAD(val_strings(ip),val_width)+ '  ' + $
	STRPAD(rpf(ip).Description,desc_width)
  end
  printf, out_unit, ''

  CLOSE, out_unit
  FREE_LUN, out_unit
end

RETURN
END
