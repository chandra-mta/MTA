FUNCTION LIST_VALUES, inarray
; given an inarray (floating point, sorted) will return
;  an array containing inarray's unique values

nelms = n_elements(inarray)
midarray = fltarr(1)
count = 0

for i = 1, nelms-1 do begin
  if (inarray(i) ne inarray(i-1)) then begin
    midarray = [midarray, inarray(i-1)]
    count = count + 1
  endif
endfor

if (nelms eq 0) then begin
  outarray = 99999
endif else if ((nelms eq 1) or (n_elements(midarray) lt 2)) then begin
  outarray = inarray
endif else begin
  outarray = [midarray(1:count), inarray(i-1)]
endelse

return, outarray
end
