FUNCTION FILTERINST, tsc, inst
; this function returns a filtered instrument list
;  it eliminates observations that fall within the
;  detector ranges, but should not be counted
;  as having the detector in place

; nmin is the minimium number of observations at a particular
;  location to be considered 'in place'
nmin = 5

if (nmin lt 1) then nmin = 1

detectors = ['', 'ACIS-I', 'ACIS-S', 'HRC-I', 'HRC-S']

get_lun, funit
openw, funit, 'filter.out'

for i = 0, 4 do begin
  printf, funit, detectors(i)
  k = where(inst eq i)
  if (k(0) ne -1) then begin
    ipos1 = tsc(k)
    ipos = ipos1(sort(ipos1))
    lastj = 0
    m = n_elements(ipos) - 1
    for j = 1L, m do begin
      ; 3 cases (special consideration for last element)
  
      if ((ipos(j) ne ipos(j-1)) and (j ne m)) then begin
        if (j-lastj ge nmin) then begin
          printf, funit, ipos(j-1), j-lastj
        endif
        if (j-lastj lt nmin) then begin
          printf, funit, ipos(j-1), ' dropped'
          drop = where(tsc eq ipos(j-1))
          for k = 0, n_elements(drop)-1 do begin
            inst(drop(k)) = 0
          endfor
        endif
        lastj = j
      endif

      if ((ipos(j) ne ipos(j-1)) and (j eq m)) then begin
        if (j-lastj ge nmin) then begin
          printf, funit, ipos(j-1), j-lastj
        endif
        if (j-lastj lt nmin) then begin
          printf, funit, ipos(j-1), ' dropped'
          drop = where(tsc eq ipos(j-1))
          for k = 0, n_elements(drop)-1 do begin
            inst(drop(k)) = 0
          endfor
        endif
        if (1 ge nmin) then begin
          printf, funit, ipos(j), '       1'
        endif
        if (1 lt nmin) then begin
          printf, funit, ipos(j), ' dropped'
          drop = where(tsc eq ipos(j))
          for k = 0, n_elements(drop)-1 do begin
            inst(drop(k)) = 0
          endfor
        endif
      endif

      if ((ipos(j) eq ipos(j-1)) and (j eq m)) then begin
        if (j-lastj+1 ge nmin) then begin
          printf, funit, ipos(j), j-lastj+1
        endif
        if (j-lastj+1 lt nmin) then begin
          printf, funit, ipos(j), ' dropped'
          drop = where(tsc eq ipos(j))
          for k = 0, n_elements(drop)-1 do begin
            inst(drop(k)) = 0
          endfor
        endif
      endif
    endfor
  endif
endfor

close, funit
return, inst
end

