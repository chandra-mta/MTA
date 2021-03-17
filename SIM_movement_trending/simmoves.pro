FUNCTION SIMMOVES, times, pos
; given arrays of times and positions, will return a structured array
;  of start time, stop time, start position, end position for each move
; ***************************************************************

; set maximum allowable move time in seconds
tlimit = 500
; set minimum time instrument must stay in position
;  to be considered "settled"
staytime = 1000

numobs = n_elements(times)
;determin TSC movement time
b = {mv2, startt: 0.0, stopt: 0.0, $
         startp: 0.0, stopp: 0.0}
movetab = replicate({mv2}, numobs/3)
j = 0
k = 0L
moving = 0
get_lun, lunit
openw, lunit, 'log'
for i = 1L, numobs-1 do begin
printf, lunit, i
  if (pos(i) ne pos(i-1)) then begin
    printf, lunit, "started loop"
    ;  we're just starting a move, if moving eq 1, we're already moving
    if (moving eq 0) then begin
      printf, lunit, "moving = 0"
      tstart = times(i)
      pstart = pos(i-1)
      p0 = pos(i)  ; new 07/17/01 BS
    endif
    ; must be in transit
    while (pos(i) ne pos(i-1) and (i lt (numobs-1))) do begin
      printf, lunit, "inst = 0 i = ", i
      i = i + 1
    endwhile
    k = i
    tmpend = times(k)
    ;tmpinst = inst(k)
    printf, lunit, "tmpend = ", times(k)
    ;  found a detector, will SIM stay there?
    while ((k lt (numobs-1)) and (pos(k) eq pos(k-1))) do begin
    ;while ((inst(k) ne 0) and (k lt (numobs-1))) do begin
      printf, lunit, "will SIM stay?  inst = ", pos(k)
      k = k + 1
    endwhile
    ;  SIM has settled on instrument
    if ((times(k-1) - tmpend) ge staytime) then begin
      moving = 0
      ;tend = times(i)
      tend = times(i-1)  ; new 07/17/01 BS
      p1 = pos(i-1)
      pend = pos(i)
      printf, lunit, " time= ", $
                  times(i), " pos= ", pend, " i= ", k
      i = k - 1
      ; this is an experiment to interpolate times from 32-s frames

      if (p1 ne p0) then begin
        tend = tend + ((tend-tstart)/abs(p1-p0)*abs(p1-pend))
        tstart = tstart - ((tend-tstart)/abs(p1-p0)*abs(p0-pstart))
      endif
      ;;;

      if ((pstart ne pend) and ((tend - tstart) lt tlimit)) then begin
        printf, lunit, "write trabstab"
        movetab(j) = {mv2, $
                           startt: tstart, stopt: tend, $
                           startp: pstart, stopp: pend}
        j = j + 1
      endif
    endif
    ;  just passing through, keep going
    if ((times(k-1) - tmpend) lt 600) then begin
      printf, lunit, "passing through "
      moving = 1
    endif
  endif
  printf, lunit, "end loop i= ", i, " k= ", k
endfor
free_lun, lunit
print, "found ", n_elements(where(movetab.startt gt 0)), " moves"
return, movetab(where(movetab.startt gt 0))
end
