FUNCTION TSCPOS, startpar, endpar, TREND = trend
;
; input data file is '/data/mta/www/mta_sim/Scripts/sim_data.out'
;
;  -can supply startpar and endpar in format yyyy:doy
;    to run subset of data
;  -keyword trend runs trending analysis as well

exit_status = [1,1]
;
;--- set maximum allowable move time in seconds
;
tlimit   = 500
;
;--- set minimum time instrument must stay in position
;---  to be considered "settled"
;
staytime = 1500
;
;--- constants
;
sperdy   = 86400

set_plot, 'Z'

get_lun, iunit
get_lun, ounit
get_lun, lunit
get_lun, hunit
;
;--- array of detector names, used for plot titles etc.
;
detectors = ['','ACIS-I','ACIS-S','HRC-I','HRC-S']
;
;--- detector SIM position ranges
;
drange      = fltarr (4, 2)

drange(0,0) =   89000
drange(0,1) =   94103
;drange(1,0) =  74420
drange(1,0) =   71420
drange(1,1) =   76820
drange(2,0) =  -51705
drange(2,1) =  -49305
drange(3,0) = -100800
drange(3,1) =  -98400
;
; ************************** read data *************************
;--- get data, leave off header
;
spawn, 'tail -n +5 /data/mta/www/mta_sim/Scripts/sim_data.out > xtmpsimdata'
;
;--- figure num lines input
;
xnum   = strarr(1)
spawn, 'wc -l xtmpsimdata', xnum 
xxnum  = fltarr(2)
xxnum  = strsplit(xnum(0),' ', /extract)
numobs = long(xxnum(0))

openr, iunit, 'xtmpsimdata'

array  = strarr(numobs)
readf, iunit, array
  
free_lun, iunit
spawn, 'rm -f xtmpsimdata'

tsc   = fltarr(numobs)
fa    = fltarr(numobs)
mpwm  = fltarr(numobs)
times = fltarr(numobs)
timed = strarr(numobs)
inst  = intarr(numobs)
;
;--- set starting and ending dates of interest
;
if (n_params(startpar) eq 0) then begin
  startpar = string('1998:0')
  endpar   = string(strmid(systime(), 20, 4) + ':366')
endif

if (n_params(endpar) eq 1) then $
  endpar = string(strmid(systime(), 20, 4) + ':366')

ttmp      = fltarr(2)
ttmp      = strsplit(startpar,':', /extract)
startpars = float(((ttmp(0) - 1998) * 31536000) + (ttmp(1) * 86400))

ttmp      = fltarr(2)
ttmp      = strsplit(endpar,':', /extract)
endpars   = float(((ttmp(0) - 1998) * 31536000) + (ttmp(1) * 86400))
;    
;---  collect TIME, 3TSCPOS, 3FAPOS
;
j = 0L

print,"numobs",numobs

for i = 0L, numobs-1 do begin
  tmp  = strarr(4)
  tmp  = strsplit(array(i), '	', /extract)
  ttmp = fltarr(5)
  ttmp = strsplit(tmp(0),':', /extract)
;
;--- time in seconds since 1998:00:00:00
;
  ttimes = float(((ttmp(0) - 1998) * 31536000) $
                  + ((ttmp(1)+1) * 86400) + (double(ttmp(2)) * 3600) $
                  + (ttmp(3) * 60) + ttmp(4))

  if ((ttimes ge startpars) and (ttimes le endpars)) then begin
    times(j) = ttimes
    tsc(j)   = float(tmp(1))
    fa(j)    = float(tmp(2))

    if (fa(j) eq 9999) then fa(j)=fa(j-1)

    mpwm(j)  = float(tmp(3))
    timed(j) = tmp(0)

    case 1 of
      (tsc(j) gt drange(0,0)) and (tsc(j) lt drange(0,1)): inst(j) = 1
      (tsc(j) gt drange(1,0)) and (tsc(j) lt drange(1,1)): inst(j) = 2
      (tsc(j) gt drange(2,0)) and (tsc(j) lt drange(2,1)): inst(j) = 3
      (tsc(j) gt drange(3,0)) and (tsc(j) lt drange(3,1)): inst(j) = 4
    else: inst(j) = 0
    endcase
    j = j + 1
  endif
endfor 

if (j eq 0) then begin
;
;--- no files to close now, but add them here if that changes
;
  stop, 'No observations found between ', startpar, ' and ', endpar
endif


if (j gt 0) then numobs = j
;
;--- filter detector identifications 
;
inst = filterinst(tsc, inst)        ;---- filterinst.pro

;
; **************** plots of all data ****************************
;
bkgcolor = 0
white    = 255
psymbol  = 1
nticks   = 5
chsize   = 1

device, set_resolution = [600, 400]
xmin = min(times)
xmax = max(times)
xr   = xmax - xmin
xmin = xmin - (xr * 0.1)
xmax = xmax + (xr * 0.1)

doyticks = pick_doy_ticks(xmin, xmax - 43200, num = nticks)
;
;--- plotting tsc
;
plot, times, tsc, psym = 3, yrange = [-110000, 101000], $
      xrange = [xmin,xmax], $
      xtitle = 'time (DOY)', ytitle = 'SIM Position', title = '3TSCPOS', $
      ystyle = 1, xstyle = 1, background = bkgclr, color = white, $
      xticks = nticks-1, xtickv = doyticks, xminor = 10, $
      xtickformat = 's2doy_axis_labels', charsize=chsize

ycon = convert_coord([0],[0], /device, /to_data)
label_year, xmin, xmax, ycon(1), csize=1

write_gif, '3tscpos.gif', tvrd()
;
;---  make a position plot for each detector
;
for i = 1, 4 do begin
  plot, times(where(inst eq i)), tsc(where(inst eq i)), $
        psym   = psymbol, title = detectors(i), $
        xrange = [xmin,xmax], $
        yrange = [drange(i-1,0), drange(i-1,1)], $
        xtitle = 'time (DOY)', ytitle = 'SIM Position', $
        ystyle = 1, xstyle = 1, background = bkgclr, color = white, $
        xticks = nticks-1, xtickv = doyticks, xminor=10, $
        xtickformat='s2doy_axis_labels', charsize=chsize

  ycon = convert_coord([0],[0], /device, /to_data)
  label_year, xmin, xmax, ycon(1), csize=1
  savefile = 'inst .gif'
  strput, savefile, strmid(i, 7, 1), 4

  write_gif, savefile, tvrd()
endfor
;
;--- plot fa
;
plot, times, fa, psym = 3, $
      xrange = [xmin,xmax], $
      xtitle = 'time (DOY)', ytitle = 'FA Position', title = '3FAPOS', $
      ystyle = 1, xstyle = 1, background = bkgclr, color = white, $
      xticks = nticks-1, xtickv = doyticks, xminor = 10, $
      xtickformat='s2doy_axis_labels', charsize=chsize

ycon = convert_coord([0],[0], /device, /to_data)
label_year, xmin, xmax, ycon(1), csize=1
write_gif, '3fapos.gif', tvrd()
;
;--- plot max pulse width modulation
;
plot, times(where(mpwm lt 99)), mpwm(where(mpwm lt 99)), psym = psymbol, $
      xrange = [xmin,xmax], $
      xtitle = 'time (DOY)', ytitle = '3MRMMXMV', title = '3MRMMXMV', $
      ystyle = 1, xstyle = 1, background = bkgclr, color = white, $
      xticks = nticks-1, xtickv = doyticks, xminor = 10, $
      xtickformat='s2doy_axis_labels', charsize=chsize

ycon = convert_coord([0],[0], /device, /to_data)
label_year, xmin, xmax, ycon(1), csize=1

write_gif, '3mrmmxmv.gif', tvrd()
 
plot, tsc(where(mpwm lt 99)), mpwm(where(mpwm lt 99)), psym = 2, $
      ;xrange = [0 , tdom(numobs-1) + xscale], $
      xticks = 4, $
      xtitle = '3TSCPOS', ytitle = '3MRMMXMV', title = '3MRMMXMV', $
      ystyle = 1, xstyle = 1, background = 255, color = 0, $
      charsize = 2, charthick =2

write_gif, '3mrmmxmv2.gif', tvrd()

plot, inst(where(mpwm lt 99)), mpwm(where(mpwm lt 99)), psym = 2, $
      ;xrange = [0 , tdom(numobs-1) + xscale], $
      xticks = 4, $
      xtitle = 'INST', ytitle = '3MRMMXMV', title = '3MRMMXMV', $
      ystyle = 1, xstyle = 1, background = 255, color = 0, $
      charsize = 2, charthick =2

write_gif, '3mrmmxmv3.gif', tvrd()

;
;**************** plot past 24 hours *************************
;
currtime  = max(times)
b         = where(times gt currtime - sperdy)
xmin1     = min(times(b))
xmax1     = currtime
xr1       = xmax1-xmin1
xmin1     = xmin1-(xr1*0.1)
xmax1     = xmax1+(xr1*0.1)
;doyticks1 = pick_doy_ticks(xmin1,xmax1-43200,num=nticks)

plot, times(b), $
      tsc(b), $
      xrange=[xmin1,xmax1], $
      yrange = [-110000, 101000], $
      xtitle = 'time (DOY)', ytitle = 'SIM Position', title = '3TSCPOS', $
      ystyle = 1, xstyle = 1, background = bkgclr, color = white, $
;      xticks = nticks-1, xtickv = doyticks1, xminor = 10, $
      xticks = nticks-1,  xminor = 10, $
      xtickformat='s2doy_axis_labels', charsize=chsize

ycon = convert_coord([0],[0], /device, /to_data)
label_year, xmin1, xmax1, ycon(1), csize=1

write_gif, '3tscpos_day.gif', tvrd()

plot, times(b), $
      fa(b), $
      xrange=[xmin1,xmax1], $
      xtitle = 'time (DOY)', ytitle = 'FA Position', title = '3FAPOS', $
      ystyle = 1, xstyle = 1, background = bkgclr, color = white, $
;      xticks = nticks-1, xtickv = doyticks1, xminor = 10, $
      xticks = nticks-1,  xminor = 10, $
      xtickformat='s2doy_axis_labels', charsize=chsize

ycon = convert_coord([0],[0], /device, /to_data)
label_year, xmin1, xmax1, ycon(1), csize=1

write_gif, '3fapos_day.gif', tvrd()

plot, times(where((mpwm lt 99) and (times gt currtime - sperdy))), $
      mpwm(where((mpwm lt 99) and (times gt currtime - sperdy))), $
      psym   = psymbol, $
      xrange = [xmin1,xmax1], $
      xtitle = 'time (DOY)', ytitle = '3MRMMXMV', title = '3MRMMXMV', $
      ystyle = 1, xstyle = 1, background = bkgclr, color = white, $
;      xticks = nticks-1, xtickv = doyticks1, xminor = 10, $
      xticks = nticks-1, xminor = 10, $
      xtickformat='s2doy_axis_labels', charsize=chsize

ycon = convert_coord([0],[0], /device, /to_data)
label_year, xmin1, xmax1, ycon(1), csize=1

write_gif, '3mrmmxmv_day.gif', tvrd()

;
;***************** plot past 7 days ***************************
;
b         = where(times gt currtime - sperdy*7)
xmin7     = min(times(b))
xmax7     = currtime
xr7       = xmax7-xmin7
xmin7     = xmin7-(xr7*0.1)
xmax7     = xmax7+(xr7*0.1)
doyticks7 = pick_doy_ticks(xmin7,xmax7-43200,num=nticks)

plot, times(b), $
      tsc(b), $
      yrange = [-110000, 101000], $
      xrange = [xmin7,xmax7], $
      xtitle = 'time (DOY)', ytitle = 'SIM Position', title = '3TSCPOS', $
      ystyle = 1, xstyle = 1, background = bkgclr, color = white, $
      xticks = nticks-1, xtickv = doyticks7, xminor = 10, $
      xtickformat='s2doy_axis_labels', charsize=chsize

ycon = convert_coord([0],[0], /device, /to_data)
label_year, xmin7, xmax7, ycon(1), csize=1

write_gif, '3tscpos_week.gif', tvrd()
;
;
;
plot, times(b), $
      fa(b), $
      xrange = [xmin7,xmax7], $
      xtitle = 'time (DOY)', ytitle = 'FA Position', title = '3FAPOS', $
      ystyle = 1, xstyle = 1, background = bkgclr, color = white, $
      xticks = nticks-1, xtickv = doyticks7, xminor = 10, $
      xtickformat='s2doy_axis_labels', charsize=chsize

ycon = convert_coord([0],[0], /device, /to_data)
label_year, xmin7, xmax7, ycon(1), csize=1

write_gif, '3fapos_week.gif', tvrd()
;
;
;
plot, times(where((mpwm lt 99) and (times gt currtime - sperdy*7))), $
      mpwm(where((mpwm lt 99) and (times gt currtime - sperdy*7))), $
      psym   = psymbol, $
      xrange = [xmin7,xmax7], $
      xtitle = 'time (DOY)', ytitle = '3MRMMXMV', title = '3MRMMXMV', $
      ystyle = 1, xstyle = 1, background = bkgclr, color = white, $
      xticks = nticks-1, xtickv = doyticks7, xminor = 10, $
      xtickformat='s2doy_axis_labels', charsize=chsize

ycon = convert_coord([0],[0], /device, /to_data)
label_year, xmin7, xmax7, ycon(1), csize=1
write_gif, '3mrmmxmv_week.gif', tvrd()

;
;******* determine TSC movement time **********
;
a = {mv, startd: 0, stopd: 0, startt: 0.0, stopt: 0.0, $
         startp: 0.0, stopp: 0.0}

transtab = replicate({mv}, numobs/3)
j        = 0
k        = 0L
moving   = 0

openw, lunit, 'log'

for i = 1L, numobs-1 do begin
  printf, lunit, i

  if (inst(i) eq 0) then begin
    printf, lunit, "started loop"
;
;---  we're just starting a move, if moving eq 1, we're already moving
;
    if (moving eq 0) then begin
      printf, lunit, "moving = 0"

      tstart = times(i)
      pstart = tsc(i-1)
      p0     = tsc(i)  ; new 07/17/01 BS
      istart = inst(i-1)
    endif
;
;--- must be in transit
;
    while (inst(i) eq 0 and (i lt (numobs-1))) do begin
      printf, lunit, "inst = 0 i = ", i
      i = i + 1
    endwhile

    k       = i
    tmpend  = times(k)
    tmpinst = inst(k)

    printf, lunit, "tmpend = ", timed(k)
;
;---  found a detector, will SIM stay there?
;
    while ((k lt (numobs-1)) and (inst(k) eq tmpinst)) do begin
 
      printf, lunit, "will SIM stay?  inst = ", inst(k)
      k = k + 1
    endwhile
;
;---  SIM has settled on instrument
;
    if ((times(k-1) - tmpend) ge staytime) then begin
      moving = 0
      tend   = times(i)
      p1     = tsc(i-1)
      pend   = tsc(i)
      iend   = inst(i)
;     
;--- this is an experiment to interpolate times from 32-s frames
;
      printf, lunit, "settled inst = ", iend, " time= ", $
                  timed(i), " pos= ", pend, " i= ", k
      i = k - 1
      if ((istart ne iend) and ((tend - tstart) lt tlimit)) then begin
        printf, lunit, "write transtab"
        transtab(j) = {mv, startd: istart, stopd: iend, $
                           startt: tstart, stopt: tend, $
                           startp: pstart, stopp: pend}
        printf, lunit, format='(2(I1, " "), 2(E16.9, " "), 2(F, " "))',$
             istart, iend, tstart, tend, pstart, pend
        j = j + 1
      endif
    endif
;
;---  just passing through, keep going
;
    if ((times(k-1) - tmpend) lt 600) then begin
      printf, lunit, "passing through "
      moving = 1
    endif
  endif
  printf, lunit, "end loop i= ", i, " k= ", k
endfor

free_lun, lunit
transtab = transtab(0:j-1)
spawn, 'mv log log1'

;
;******************* Trending ***********************************
;

if (keyword_set(trend)) then begin
  tsc_mv_trend, transtab, tsc, fa, times        ;--- tsc_mv_trend.pro

  cmp_as_planned, times, tsc, fa, 'al'          ;--- cmp_as_planned.pro
  exit_status(1) = 0
endif
;
;--- backstop compare daily and weekly 
;
cmp_as_planned, times(where(times gt currtime - 86400)), $
              tsc(where(times gt currtime - 86400)), $
              fa(where(times gt currtime - 86400)), 'dy'

cmp_as_planned, times(where(times gt currtime - 86400*7)), $
              tsc(where(times gt currtime - 86400*7)), $
              fa(where(times gt currtime - 86400*7)), 'wk'
;
;--- give some output 
;
openw,  ounit, 'tscpos.out'
printf, ounit, timed(0), ' to ', timed(numobs-1)
printf, ounit, '  Start     Stop     #obs   Time/Step     Ave. Time     Std dev'

b       = {summ, startd: '', stopd: '', nobs: 0, tperstep: 0.0, avet: 0.0, sdev: 0.0}
summary = replicate({summ}, 12)

m = 0
get_lun, vunit
openw, vunit, 'tpos.out'

for i = 1, 4 do begin
  for j = 1, 4 do begin

    if (i ne j) then begin
      b = where(transtab.startd eq i and transtab.stopd eq j, count)

      if (count gt 0) then begin
        tdiffplot = fltarr(1)
        pdiffplot = fltarr(1)
        timeplot = fltarr(1)

        for k = 0, count-1 do begin
          tdiffplot = [tdiffplot, transtab(b(k)).stopt - transtab(b(k)).startt]
          pdiffplot = [pdiffplot, $
                       abs(transtab(b(k)).stopp - transtab(b(k)).startp)]
          timeplot = [timeplot, transtab(b(k)).startt]
        endfor
;
;--- remove first, dummy array element
;
        tdiffplot = tdiffplot(1:*)
        pdiffplot = pdiffplot(1:*)
        timeplot  = timeplot(1:*)
        tvals     = list_values(tdiffplot)

        for k = 0, n_elements(tvals)-1 do begin
          c = where(tdiffplot eq tvals(k))

          for l = 1, n_elements(c) do begin
            printf, vunit, tdiffplot(c(l-1)), $
                    transtab(b(c(l-1))).startp, transtab(b(c(l-1))).stopp, $
                    transtab(b(c(l-1))).startt
          endfor
        endfor
;
;---  summarize
;
        summary(m).startd   = detectors(i)
        summary(m).stopd    = detectors(j)
        summary(m).nobs     = count

        tprstp              = mymean(tdiffplot/pdiffplot)
        summary(m).tperstep = tprstp(0)

        mean                = mymean(tdiffplot)
        summary(m).avet     = mean(0)
        summary(m).sdev     = sqrt(mean(1))

        printf, ounit, summary(m)
        m = m + 1
;
;--- plot 
;
        plottitle = 'From        to       '
        strput, plottitle, detectors(j), 15
        strput, plottitle, detectors(i), 5
        device, set_resolution = [410,290]

        plot,   timeplot, tdiffplot, psym = psymbol, $
              xtitle = 'time (DOY)', $
              ytitle = 'transit time (s)', title = plottitle, $
              xrange = [xmin,xmax], $
              yrange = [10, 350], $
              ystyle = 1, xstyle = 1, background = bkgclr, color = white, $
              xticks = nticks-1, xtickv = doyticks, xminor = 10, $
              xtickformat='s2doy_axis_labels', charsize=chsize

        ycon = convert_coord([0],[0], /device, /to_data)
        label_year, xmin, xmax, ycon(1), csize=1

        savefile = 'tsc  a.gif'
        strput, savefile, strmid(j, 7, 1), 4
        strput, savefile, strmid(i, 7, 1), 3

        write_gif, savefile, tvrd()
; 
;--- adjustable scale
;
        device, set_resolution = [600,400]
        plot, timeplot, tdiffplot, psym = psymbol, $
              xtitle = 'time (DOY)', $
              ytitle = 'transit time (s)', title = plottitle, $
              xrange = [xmin,xmax], $
              yrange = [mean(0)-(3*sqrt(mean(1))), $
                        mean(0)+(3*sqrt(mean(1)))], $
              ystyle = 1, xstyle = 1, background = bkgclr, color = white, $
              xticks = nticks-1, xtickv = doyticks, xminor = 10, $
              xtickformat='s2doy_axis_labels', charsize=chsize

        ycon = convert_coord([0],[0], /device, /to_data)
        label_year, xmin, xmax, ycon(1), csize=1
        strput, savefile, 'b', 5

        write_gif, savefile, tvrd()
      endif

    endif
  endfor
endfor

free_lun, ounit
free_lun, vunit

mkwebsum, summary, timed, m-1, tsc, fa, mpwm(where(mpwm lt 99))     ;--- mkwebsum.pro
;
; ******************** give some weekly output **************************
;
summary = replicate({summ}, 12)
temp    = transtab(where(transtab.startt gt 0))
weekt   = temp(n_elements(temp)-1).startt - 86400 * 7
xmin    = (weekt - 48815999) /86400
xmax    = (temp(n_elements(temp)-1).startt - 48815999) / 86400

print, weekt, ' ', temp(n_elements(temp) - 1).startt
weekstab = transtab(where(transtab.startt gt weekt))

openw,  ounit, 'tscposwk.out'
printf, ounit, 'Past week ending ', timed(numobs-1)
printf, ounit, '  Start     Stop     #obs   Time/Step     Ave. Time     Std dev'

m = 0
get_lun, vunit
openw,   vunit, 'tposwk.out'

for i = 1, 4 do begin
  for j = 1, 4 do begin

    if (i ne j) then begin
      b = where(weekstab.startd eq i and weekstab.stopd eq j, count)

      summary(m).startd = detectors(i)
      summary(m).stopd  = detectors(j)
      summary(m).nobs   = count

      if (count gt 0) then begin
        tdiffplot = fltarr(1)
        pdiffplot = fltarr(1)
        timeplot  = fltarr(1)

        for k = 0, count-1 do begin
          tdiffplot = [tdiffplot, weekstab(b(k)).stopt - weekstab(b(k)).startt]
          pdiffplot = [pdiffplot, $
                       abs(weekstab(b(k)).stopp - weekstab(b(k)).startp)]
          timeplot  = [timeplot, weekstab(b(k)).startt]
        endfor
;
;---  remove first, dummy array element
;
        tdiffplot = tdiffplot(1:*)
        pdiffplot = pdiffplot(1:*)
        timeplot  = timeplot(1:*)
        tvals     = list_values(tdiffplot)

        for k = 0, n_elements(tvals)-1 do begin
          c = where(tdiffplot eq tvals(k))

          for l = 1, n_elements(c) do begin
            printf, vunit, tdiffplot(c(l-1)), $
                    weekstab(b(c(l-1))).startp, weekstab(b(c(l-1))).stopp
          endfor
        endfor
;
;---- summarize
;
        tprstp              = mymean(tdiffplot/pdiffplot)
        summary(m).tperstep = tprstp(0)
        mean                = mymean(tdiffplot)
        summary(m).avet     = mean(0)
        summary(m).sdev     = sqrt(mean(1))

        printf, ounit, summary(m)
;
;---- plot
;
        timeplot = (timeplot-48815999) / 86400

        plottitle = 'From        to       '
        strput, plottitle, detectors(j), 15
        strput, plottitle, detectors(i), 5
        plot,   timeplot, tdiffplot, psym = psymbol, $
              xtitle = 'time (DOM)', $
              ytitle = 'transit time (s)', title = plottitle, $
              xrange = [xmin,xmax], $
              yrange = [10, 350], $
              ystyle = 1, xstyle = 1, background = bkgclr, color = white
;              xticks = nticks-1, xtickv = doyticks, xminor = 10, $
;              xtickformat='s2doy_axis_labels', charsize=chsize

        ycon = convert_coord([0],[0], /device, /to_data)
        label_year, xmin, xmax, ycon(1), csize=1
        xyouts, 1.0, 0.0, systime(), alignment = 1, color = 0, /normal

        savefile = 'tsc  aw.gif'

        strput, savefile, strmid(j, 7, 1), 4
        strput, savefile, strmid(i, 7, 1), 3

        write_gif, savefile, tvrd()
;  
;--- adjustable scale
;
        plot, timeplot, tdiffplot, psym = psymbol, $
              xtitle = 'time (DOM)', $
              ytitle = 'transit time (s)', title = plottitle, $
              yrange = [mean(0)-(3*sqrt(mean(1))), $
                        mean(0)+(3*sqrt(mean(1)))], $
              xrange = [xmin,xmax], $
              ystyle = 1, xstyle = 1, background = bkgclr, color = white
;              xticks = nticks-1, xtickv = doyticks, xminor = 10, $
;              xtickformat='s2doy_axis_labels', charsize=chsize

        ycon = convert_coord([0],[0], /device, /to_data)
        label_year, xmin, xmax, ycon(1), csize=1

        strput, savefile, 'b', 5

        write_gif, savefile, tvrd()
      endif

    m = m + 1
    endif
  endfor
endfor
free_lun, ounit
free_lun, vunit

mkweeksum, summary, m-1, timed
;
; ********************************************************************
;

exit_status(0) = 0
return, exit_status
end
