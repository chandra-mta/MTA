FUNCTION FLOAT_STRUCT, instruct, COLS=cols
;  this is kind of a hack to convert all structure elements to float
;  developed for comp and grad trending data,
;   where time column inputs as 2 bit integer.
; optional give arrray of column numbers to return
tnames=tag_names(instruct)
if (not keyword_set(cols)) then cols=indgen(n_elements(tnames))
mystruct = create_struct(tnames(cols(0)),0.0)
for i = 1, n_elements(cols)-1 do begin
  mystruct = create_struct(mystruct, tnames(cols(i)), 0.0)
endfor
outstruct=replicate(mystruct,n_elements(instruct))
for i = 0, n_elements(instruct)-1 do begin
  for j = 0, n_elements(cols)-1 do begin
    outstruct(i).(j)=instruct(i).(cols(j))
  endfor
endfor

return, outstruct
end
