PRO TSC_MV_TREND, transtab, tscarr, faarr, timearr
 
get_lun, inunit

xnum     = strarr(1)
;
;--- a file "months" must be made before running this (use: mkmonth_list.py)
;--- it has a format of Feb15 5673 5701
;
spawn, 'wc -l /data/mta_www/mta_sim/Scripts/SIM_move/Outputs/months', xnum

xxnum    = fltarr(2)
xxnum    = strsplit(xnum(0),' ', /extract)
numtimes = xxnum(0)

timelist = strarr(numtimes)

openr,    inunit, '/data/mta_www/mta_sim/Scripts/SIM_move/Outputs/months'
readf,    inunit, timelist
free_lun, inunit

name   = strarr(numtimes)
start  = fltarr(numtimes)
stop   = fltarr(numtimes)

for i = 0, numtimes-1 do begin
  tmp = strarr(3)
  tmp = strsplit(timelist(i), ' ', /extract)
  name(i)  = tmp(0)
  start(i) = float(tmp(1))
  stop(i)  = float(tmp(2))
endfor
;
;--- how many moves in transtab
;
;--------- full range ---------------------
;
;--- tsc
;
tscmvtab = simmoves(timearr, tscarr)        ;--- siimmoves.pro

bkgcolor = 0
white    = 255
psymbol  = 1
nticks   = 9
chsize   = 1

device, set_resolution = [1200,400]

xmin = min(tscmvtab.startt)
xmax = max(tscmvtab.startt)
xr   = xmax-xmin
xmin = xmin-(xr*0.1)
xmax = xmax+(xr*0.1)

doyticks = pick_doy_ticks(xmin,xmax-43200,num=nticks)

plot, tscmvtab.startt, where(tscmvtab.startt) + 1, $
      xtitle      = 'time (DOY)', $
      xrange      = [xmin,xmax], $
      ytitle      = '# Moves', $
      yrange      = [0, n_elements(tscmvtab)*1.05], $
      title       = 'SIM Cumulative Moves', $
      ystyle      = 1, xstyle = 1, background = bkgclr, color = white, $
      xticks      = nticks-1, xtickv = doyticks, xminor=10, $
      xtickformat = 's2doy_axis_labels', charsize=chsize

ycon = convert_coord([0],[0], /device, /to_data)
label_year, xmin, xmax, ycon(1), csize=1

write_gif, 'trend_tmove.gif', tvrd()
;
;--- fa
;
famvtab = simmoves(timearr, faarr)

plot, famvtab.startt, where(famvtab.startt) + 1, $
      xtitle      = 'time (DOY)', $
      xrange      = [xmin,xmax], $
      ytitle      = '# Moves', $
      yrange      = [0, n_elements(famvtab)*1.05], $
      title       = 'SIM Cumulative Moves', $
      ystyle      = 1, xstyle = 1, background = bkgclr, color = white, $
      xticks      = nticks-1, xtickv = doyticks, xminor=10, $
      xtickformat = 's2doy_axis_labels', charsize=chsize

ycon = convert_coord([0],[0], /device, /to_data)
label_year, xmin, xmax, ycon(1), csize=1

write_gif, 'trend_fmove.gif', tvrd()

;
; Cumulative distance
; 11/08 BS Use tsc and times array instead of transtab
;  transtab does not have every step
;
;--- tsc
;
tdist    = fltarr(n_elements(tscarr))
tdist(0) = 0

for i = 1L, n_elements(tscarr)-1 do begin
  tdist(i) = tdist(i-1) + (abs(tscarr(i) - tscarr(i-1)))
endfor

plot, timearr, tdist, $
      xtitle      = 'time (DOY)', $
      xrange      = [xmin,xmax], $
      ytitle      = 'total distance (steps)', $
      yrange      = [0, max(tdist)*1.05], $
      title       = 'SIM Cumulative Distance Travelled', $
      ystyle      = 1, xstyle = 1, background = bkgclr, color = white, $
      xticks      = nticks-1, xtickv = doyticks, xminor=10, $
      xtickformat = 's2doy_axis_labels', charsize=chsize

ycon = convert_coord([0],[0], /device, /to_data)
label_year, xmin, xmax, ycon(1), csize=1

write_gif, 'trend_tdist.gif', tvrd()
;
;--- fa
;
fdist    = fltarr(n_elements(faarr))
fdist(0) = 0

for i = 1L, n_elements(faarr)-1 do begin
  fdist(i) = fdist(i-1) + (abs(faarr(i) - faarr(i-1)))
endfor

plot, timearr, fdist, $
      xtitle      = 'time (DOY)', $
      xrange      = [xmin,xmax], $
      ytitle      = 'total distance (steps)', $
      yrange      = [0, max(fdist)*1.05], $
      title       = 'SIM Focus Cumulative Distance Travelled', $
      ystyle      = 1, xstyle = 1, background = bkgclr, color = white, $
      xticks      = nticks-1, xtickv = doyticks, xminor=10, $
      xtickformat = 's2doy_axis_labels', charsize=chsize

ycon = convert_coord([0],[0], /device, /to_data)
label_year, xmin, xmax, ycon(1), csize=1

write_gif, 'trend_fdist.gif', tvrd()
;
;---  monthly trends -------
;
device, set_resolution = [600,400]

ave      = fltarr(numtimes)
nummoves = fltarr(numtimes)

for i = 0, numtimes - 1 do begin
  b = where((sdom(transtab.startt) ge start(i)) and $
            (sdom(transtab.startt) lt stop(i)))

  if (b(0) ge 0) then begin
    tstart      = transtab(b).startt
    tstop       = transtab(b).stopt
    pstart      = transtab(b).startp
    pstop       = transtab(b).stopp
    tperstep    = (tstop - tstart) / (abs(pstop - pstart))
    mn          = mymean(tperstep)
    ave(i)      = mn(0)
    nummoves(i) = n_elements(b)
  endif
endfor  

ave      = ave(where(ave gt 0))
sstart   = start
sstop    = stop
start    = start(where(ave gt 0))
stop     = stop(where(ave gt 0))
nummoves = nummoves(where(nummoves gt 0))

;;print, 'Month averages: ', ave                      ;---- debug
;;print, 'Month # moves: ', nummoves                  ;---- debug

mid     = (start + stop)/2
fit     = svdfit(mid, ave, 2)
fitline = fit(0) + fit(1)*mid

;;print, 'fit coeff: ', fit                           ;---- debug

mid_plot=cxtime(mid,'met','sec')

plot, mid_plot, ave, psym = psymbol, $
      xtitle      = 'time (DOY)', $
      xrange      = [xmin,xmax], $
      ytitle      = 'seconds/step', $
      yrange      = [0, 0.002], $
      title       = 'SIM Monthly Move Rate', $
      ystyle      = 1, xstyle = 1, background = bkgclr, color = white, $
      xticks      = nticks-1, xtickv = doyticks, xminor=10, $
      xtickformat = 's2doy_axis_labels', charsize=chsize

ycon = convert_coord([0],[0], /device, /to_data)
label_year, xmin, xmax, ycon(1), csize=1

oplot, mid_plot, fitline, color = white

xyouts, max(transtab.stopt)/2, 0.0001, $
        'slope '+string(fit(1))+' s/step/day', $
        color = white, /data

write_gif, 'trend_month1.gif', tvrd()
;
;--- monthly trends (without ACIS-I to ACIS-S moves
;
ave      = fltarr(numtimes)
nummoves = fltarr(numtimes)
start    = sstart
stop     = sstop

for i = 0L, numtimes - 1 do begin
  b = where((sdom(transtab.startt) ge start(i)) and $
            (sdom(transtab.startt) lt stop(i)))
  if (b(0) ge 0) then begin
    tstart = transtab(b).startt
    tstop  = transtab(b).stopt
    pstart = transtab(b).startp
    pstop  = transtab(b).stopp
;
;--- filter out short moves
;--- ie. eliminate ACIS-I to ACIS-S and vice versa
;
    longm = where((pstop - pstart) gt 40000)

;;    print, longm                                    ;---- debug
    lsum = 0
    lcnt = 0

    for k = 0, n_elements(longm)-1 do begin
;    tperstep    = (tstop(longm) - tstart(longm)) / (abs(pstop(longm) - pstart(longm)))
        element  = longm[k]
        if(element > 0) then begin
            diff = abs(pstop(element) - pstart(element))
            if (diff > 0) then begin
                lsum    += (tstop(element) - tstart(element)) / (abs(pstop(element) - pstart(element)))
                lcnt    += 1
            endif
        endif
    endfor
;;    mn          = mymean(tperstep)
;;    ave(i)      = mn(0)
    ave(i)      = 0
    if(lcnt > 0) then ave(i)      = lsum/lcnt
    nummoves(i) = n_elements(b)
  endif
endfor  

ave      = ave(where(ave gt 0))
start    = start(where(ave gt 0))
stop     = stop(where(ave gt 0))
nummoves = nummoves(where(nummoves gt 0))

;;print, 'Month averages: ', ave                      ;---- debug
;;print, 'Month # moves: ', nummoves                  ;---- debug

mid     = (start + stop)/2
fit     = svdfit(mid, ave, 2)
fitline = fit(0) + fit(1)*mid

;;print, 'fit coeff: ', fit                           ;---- debug

mid_plot=cxtime(mid,'met','sec')
plot, mid_plot, ave, psym = psymbol, $
      xtitle      = 'time (DOY)', $
      xrange      = [xmin,xmax], $
      ytitle      = 'seconds/step', $
      yrange      = [0, 0.002], $
      title       = 'SIM Monthly Move Rate *', $
      ystyle      = 1, xstyle = 1, background = bkgclr, color = white, $
      xticks      = nticks-1, xtickv = doyticks, xminor=10, $
      xtickformat = 's2doy_axis_labels', charsize=chsize

ycon = convert_coord([0],[0], /device, /to_data)
label_year, xmin, xmax, ycon(1), csize=1

oplot, mid_plot, fitline, color=white

xyouts, xmin + (xmax-xmin)*0.1, 0.0004, $
        '* moves between ACIS-I and ACIS-S not included, times too short', $
        alignment = 0, color = white, /data
xyouts, max(transtab.stopt)/2, 0.0001, $
        'slope '+string(fit(1))+' s/step/day', $
        color = white, /data

write_gif, 'trend_month2.gif', tvrd()
;
;--- instrument moves trends
;
detectors = ['', 'ACIS-I', 'ACIS-S', 'HRC-I', 'HRC-S']

for i = 1, 4 do begin
  for j = 1, 4 do begin
    if (i ne j) then begin
      b = where(transtab.startd eq i and transtab.stopd eq j, count)

      if (count gt 0) then begin
        tdiffplot = fltarr(1)
        pdiffplot = fltarr(1)
        timeplot  = fltarr(1)

        for k = 0, count-1 do begin
          tdiffplot = [tdiffplot, transtab(b(k)).stopt - transtab(b(k)).startt]
          pdiffplot = [pdiffplot, $
                       abs(transtab(b(k)).stopp - transtab(b(k)).startp)]
          timeplot  = [timeplot, transtab(b(k)).startt]
        endfor
;
;---  remove first, dummy array element
;
        tdiffplot = tdiffplot(1:*)
        pdiffplot = pdiffplot(1:*)
        timeplot  = timeplot(1:*)
        mean = moment(tdiffplot/pdiffplot)

;;        print, mean                         ;--- debug

        b        = where(abs(tdiffplot/pdiffplot - mean(0)) lt 3*sqrt(mean(1)))
        rateplot = tdiffplot(b)/pdiffplot(b)
;        
;--- smooth by bins of sbin
;
        sbin  = 3
        tplot = fltarr(1)
        trate = fltarr(1)
        for m = 0, n_elements(timeplot(b))-sbin do begin
          tmptime = 0
          tmprate = 0

          for n = 0, sbin-1 do begin
            tmptime = tmptime + timeplot(b(m+n))
            tmprate = tmprate + (rateplot(m+n))
          endfor

          tplot = [tplot, tmptime/sbin]
          trate = [trate, tmprate/sbin]
        endfor

        tplot = tplot(1:*)
        trate = trate(1:*)
        fit   = linfit(tplot, trate)

        plottitle = 'From        to       '
        strput, plottitle, detectors(j), 15
        strput, plottitle, detectors(i), 5
        
        plot, tplot,trate, psym = psymbol, $
              xtitle      = 'time (DOY)', $
              xrange      = [xmin,xmax], $
              ytitle      = 'seconds/step', title = plottitle, $
              yrange      = [0, 0.0020], $
              ystyle      = 1, xstyle = 1, background = bkgclr, color = white, $
              xticks      = nticks-1, xtickv = doyticks, xminor=10, $
              xtickformat = 's2doy_axis_labels', charsize=chsize, $
              /nodata

        ycon = convert_coord([0],[0], /device, /to_data)
        label_year, xmin, xmax, ycon(1), csize=1
        
        oplot, tplot, trate, psym=psymbol, color=white
        oplot, tplot, fit(0)+tplot*fit(1), color=white
        
        xyouts, xmax/2, 0.0001, $
                'slope '+string(fit(1)*86400)+' s/step/day', $
                color=white, /data
        savefile = 'trend  a.gif'
        strput, savefile, strmid(j, 7, 1), 6
        strput, savefile, strmid(i, 7, 1), 5

        write_gif, savefile, tvrd()
;
;
;
        xhist = histogram(tdiffplot/pdiffplot, binsize = 0.00005)
        plot, xhist, $
              psym       = 10, $
              xtitle     = 'seconds/step', xticks = 4, $
              xrange     = [0, 12], $
              ytitle     = 'frequency', title = plottitle, $
              yrange     = [0, max(xhist)*1.05], $
              xstyle     = 1, ystyle = 1, $
              background = bkgclr, color = white, $
              charsize   = 1.2, charthick = 2
        
        savefile = 'trend  hist.gif'
        strput, savefile, strmid(j, 7, 1), 6
        strput, savefile, strmid(i, 7, 1), 5

        write_gif, savefile, tvrd()

      endif
    endif
  endfor
endfor
;
;--- plot TSC move rate
;
time_list = fltarr(1)
terr_list = fltarr(1)
step_list = fltarr(1)
pos_diff  = abs(transtab.stopp - transtab.startp)
pos_list  = list_values(pos_diff(sort(pos_diff)))

;;print, "step sizes: ", pos_list  ;--- debug

for i = 0 , n_elements(pos_list)-1 do begin
  b = where(pos_diff eq pos_list(i))

  if (n_elements(b) gt 1 ) then begin
    time_val = moment(transtab(b).stopt - transtab(b).startt)
  endif else begin
    time_val = [(transtab(b).stopt-transtab(b).startt), 0]
  endelse

  time_list = [time_list, time_val(0)]
  terr_list = [terr_list, sqrt(time_val(1))]
  step_list = [step_list, pos_list(i)]
endfor

c       = where(time_list gt 32)
fit     = svdfit(step_list(c), time_list(c), 2)
fitline = fit(0) + fit(1)*step_list[1:*]

;;print, "Fit: ", fit(0), fit(1)  ;--- debug

plot, step_list[1:*], time_list[1:*], psym=1, $
      yrange   = [0, max(time_list)*1.1], $
      ytitle   = "Time (s)", xtitle="N steps", $
      title    = "Average TSC Move Times", $
      ystyle   = 1, xstyle = 1, background = bkgclr, color = white, $
      xticks   = nticks-1, xminor=10, $
      charsize = chsize

oplot, step_list[1:*], fitline
oplot, step_list[1:*], step_list[1:*]/700+30, linestyle=1

write_gif, 'trend_trate.gif', tvrd()

end
