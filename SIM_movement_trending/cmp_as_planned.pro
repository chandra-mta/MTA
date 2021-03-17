PRO CMP_AS_PLANNED, times, tspos, fapos, name
;

;
;--- set maximum time moves can take (seconds)
;
maxmvtime  = 1200
;
;--- set allowable lag time for moves
;
minmvtime  = 600
;
;--- set maximum position difference to be considered 'found' (steps)
;
maxposdiff = 800
;
;--- set minimum time in one position to be 'settled' (seconds)
;
minstay    = 500
;
;------ read pred_state.rdb --------
;
;---  figure num lines input
;
xnum   = strarr(1)
spawn, 'wc -l /home/mta/Chex/pred_state.rdb', xnum
xxnum  = fltarr(2)
xxnum  = strsplit(xnum(0),' ', /extract)
numobs = float(xxnum(0))

get_lun,  transunit
openr,    transunit, '/home/mta/Chex/pred_state.rdb'

array = strarr(numobs)

readf,    transunit, array
free_lun, transunit
;
;--- read simtrans data
;
btimes    = fltarr(numobs)
bpos      = fltarr(numobs)
fpos      = fltarr(numobs)
btimes(0) = 0
bpos(0)   = 0
fpos(0)   = 0
bprev     = 0
fprev     = 0
;
;--- pred_state.rdb starts the most recent date
;--- so reverse the data order
;
for k = 1L, numobs-2 do begin
  i = numobs - k
;
;--- parse simtrans
;
  tmp  = strarr(9)
  tmp  = strsplit(array(i),  /extract)
  xtmp = strarr(5)
  xtmp = strsplit(tmp(0),   ':', /extract)
;
;--- time in seconds since 1998:00:00:00
;
  btimes(i) = float((double((xtmp(0)) - 1998) * 31536000) $
                  + (double(xtmp(1)) * 86400) + (double(xtmp(2)) * 3600) $
                  + (double(xtmp(3)) * 60) + double(xtmp(4)))
;
;--- expected position
;--- if the value is undef or NONE, replace with the previous value
;
  if(tmp(2) eq 'undef' || tmp(2) eq 'NONE') then tmp(2) = bprev
  if(tmp(3) eq 'undef' || tmp(3) eq 'NONE') then tmp(3) = fprev

  bpos(i) = float(tmp(2))
  fpos(i) = float(tmp(3))
  bprev   = tmp(2)
  fprev   = tmp(3)
endfor
;
;--------  TSC/FA POS comparison --------
;
datasize  = n_elements(tspos)
tsposdiff = fltarr(datasize)
faposdiff = fltarr(datasize)
;
;--- backstop (bpos btimes) index
;
j = 0L
jcnt = n_elements(btimes)
get_lun, ounit
get_lun, ounit2
openw,   ounit,  'cmp_as_planned_ts.out'
openw,   ounit2, 'cmp_as_planned_fa.out'

for i = 0L, datasize-1 do begin

  if(times(i) < btimes(0)) then begin
    tsposdiff(i) = 0
    faposdiff(i) = 0
  endif else begin 
    while (times(i) ge btimes(j)) do begin
        if(j lt jcnt-1) then begin          ;--- added to avoid over-run 3/23/15 (ti)
            j = j + 1
        endif else begin
            break
        endelse
    endwhile

    if (times(i) - btimes(j-1) ge minmvtime) then begin
        tsposdiff(i) = tspos(i) - bpos(j-1)
        faposdiff(i) = fapos(i) - fpos(j-1)
    endif
    
    if (times(i) - btimes(j-1) lt minmvtime) then begin
        tsposdiff(i) = 0
        faposdiff(i) = 0
    endif

  endelse

  if (abs(tsposdiff(i)) gt 10) then printf, ounit,  i, ' ', $
      sdom(times(i)), ' ',  sdom(btimes(j-1)), ' ', $
      sdom(btimes(j)), ' ', tspos(i), ' ', bpos(j-1)

  if (abs(faposdiff(i)) gt 10) then printf, ounit2, i, ' ', $
      sdom(times(i)), ' ',  sdom(btimes(j-1)), ' ', $
      sdom(btimes(j)), ' ', fapos(i), ' ', fpos(j-1)
endfor

free_lun, ounit
free_lun, ounit2
 
spawn, "cat cmp_as_planned_ts.out cmp_as_planned_fa.out > cmp_as_planned.out"

;
;--- TSCPOS plot ------------
;
bkgcolor = 0
white    = 255
psymbol  = 1
nticks   = 5
chsize   = 1

device, set_resolution = [600,400]

xmin = min(times)
xmax = max(times)
xr   = xmax-xmin
xmin = xmin-(xr*0.1)
xmax = xmax+(xr*0.1)

;doyticks = pick_doy_ticks(xmin,xmax-43200,num=nticks)

plot, times, tsposdiff, psym = psymbol, $
      xtitle = 'Time (DOY)', $
      ytitle = 'Actual - Expected (steps)', $
      yrange = [min(tsposdiff) - 1, max(tsposdiff) + 1], $
      xrange = [xmin,xmax], $
      title  = 'SIM Position Actual - Expected', $
      ystyle = 1, xstyle = 1, background = bkgclr, color = white, $
      xticks=nticks-1, xtickv = doyticks, xminor=10, $
      xtickformat='s2doy_axis_labels', charsize=chsize

ycon = convert_coord([0],[0], /device, /to_data)
label_year, xmin, xmax, ycon(1), csize=1

savefile = 'tscposdiff_  .gif'
strput, savefile, name, 11

write_gif, savefile, tvrd()
;
;----  FAPOS plot -----------------
;
 
plot, times, faposdiff, psym = psymbol, $
      xtitle = 'Time (DOY)', $
      ytitle = 'Actual - Expected (steps)', $
      yrange = [min(faposdiff) - 1, max(faposdiff) + 1], $
      title  = 'SIM Focus Actual - Expected', $
      ystyle = 1, xstyle = 1, background = bkgclr, color = white, $
      xticks = nticks-1, xtickv = doyticks, xminor=10, $
      xtickformat='s2doy_axis_labels', charsize=chsize

ycon = convert_coord([0],[0], /device, /to_data)
label_year, xmin, xmax, ycon(1), csize=1

savefile = 'faposdiff_  .gif'
strput, savefile, name, 10

write_gif, savefile, tvrd()

end
