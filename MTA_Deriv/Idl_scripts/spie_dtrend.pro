PRO SPIE_DTREND, infile, SIG=sig, WSMOOTH=wsmooth, PLOTX=plotx, $
            OUTDIR=outdir, FILT_IT=filt_it, XAX=xax, $
            AVG_ONLY=avg_only, QTR_ONLY=qtr_only, CCODE=ccode
; make trending and derivative plots
; input:
;     infile - file returned by dataseeker
;     sig - filter out any data more than sig sigma from mean (default 6)
;     wsmooth - smoothing factor (number of days to smooth over)
;     plotx - set_plot, 'X'
;     outdir - change default output directory (must already exist)
;     filt_it - a hack to filter by sig n times (used for grad only 
;                   now until I understand the data better)
;     xax - plot vs something other than time
;     avg_only - set to only run average plots, not daily min and max
;     qtr_only - set to only run quarterly plots, not avg, or daily min and max
;     ccode - column name to calibrate color scale
; v1.3
; 12.Mar 2002 BDS - add limit checking, indications
; v1.4
; 21.Mar 2002 BDS - just a few minor, mostly cosmetic improvements
; v1.5
; 28.Mar 2002 BDS - added dtrend_read for customized processing
; v1.6
; 19.Apr 2002 BDS - change html output routine with dtrend_html
; v2.0
; 25.Jun 2002 BDS - add xax to plot vs temp etc.
; v3.0
; 08.Jul 2002 BDS - add daily min and max plots
;                 - modify "TV screen" for netscape 6
; v3.1
; 28.Oct 2002 BDS - add quarterly trends
; v3.2
; 27.Nov 2002 BDS - add ccode
;                 - change congrid calls to new dsample, no, change back
; 30.Jan 2003 BDS - work on min/max comps
; 16.Apr 2003 BDS - move processing to rhodes 
; v3.4
; 09.Sep 2003 BDS - allow limit changes (different limits in different time
;                    intervals)

; directory for web output
if (not keyword_set(outdir)) then outdir="/data/mta4/www/DAILY/mta_deriv"
ifile=outdir+"/index.html"
;ifile=outdir+"/xindex.html"

; limit number of points plotted
;  (and number of points dsmooth uses, it's slow)
n_lim=2500
 
; constants
speryr=31536000.0
sperdy=86400.0
speryr_ref=31536000.0 ; speryr is hacked if xax, so use these 
sperdy_ref=86400.0    ;  if really mean secs per year/day


; other things user can set
nticks=8
pred_days=180 ; number of days to look ahead for predicted violations

; ******************************************************************
; initializations
html = strarr(1)
data_in = 0

nstart=rstrpos(infile, "/")+1
nstop=rstrpos(infile,".")
if (nstop lt nstart) then nstop = nstart+20
rootname=strmid(infile,nstart,nstop-nstart)
htmlfile=rootname+".html"
htmlout=strcompress(outdir+"/"+htmlfile, /remove_all)
htmltmp=outdir+"/tmp.html"

if (NOT keyword_set(xax)) then xax='TIME'
if (NOT keyword_set(sig)) then sig=6
if (NOT keyword_set(wsmooth)) then wsmooth = 0

; plotting stuff
xwidth=720
yheight=550

if (keyword_set(plotx)) then begin
  set_plot, 'X'
  window, 0, xsize=xwidth, ysize=yheight,retain=2
endif else begin
  set_plot, 'Z'
  device, set_resolution = [xwidth, yheight]
endelse

set_plot, 'ps'
device, filename='Spie_plot/xtrend.ps',xsize=10, ysize=7.6, $
         /encapsul,/color

; colors
loadct, 39
white = 255
white = 0
bgrd = 0
bgrd = 255
red = 230
;red = 14 ; alt - someday, I'll figure out why we lose colors sometimes
yellow = 190
;yellow = 11 ; alt
blue = 100
;blue = 6 ; alt
green = 150
;green = 9 ; alt
purple = 50
orange = 215
hred = "#FF0000"
hyellow = "#FFFF00"
hgreen = "#33FF33"
hblue = "#33CCFF"
hwhite = "#FFFFFF"

;data=mrdfits(infile, 1)

if (strlowcase(xax) eq 'time') then begin
  xaxtime=1
  xlim=[-999,-999,-999,-999]
  xunits='YR'
  ndaily=3
endif else begin
  xaxtime=0
  speryr=1 ; hack if we're not using time, yeah, but need correct
  sperdy=1 ;  values when writing index page (reset there for now)
  ndaily=3
endelse

nlstart = 0 ; which loop to start on
if (keyword_set(avg_only)) then ndaily=0
if (keyword_set(qtr_only)) then begin
  if (keyword_set(avg_only)) then begin
    print, "What do you want, AVERAGE ONLY or QUARTERLY ONLY?  Try again."
    exit
  endif ; if (keyword_set(avg_only)) then begin
  nlstart=3
endif ; if (keyword_set(qtr_only)) then begin
 
frame=["AVG","MAX","MIN","QTR"]
for n_if_time = nlstart, ndaily do begin ; loop to do daily min/max
;testfor n_if_time = 1, 3 do begin ; loop to do daily min/max

  html = strarr(1)
  rmark = 0 ; counter for red violation
  ymark = 0 ; counter for yellow violation

  loop=1
  loop_end=1
  while (loop le loop_end) do begin ; this is the loop to do several
                                    ; passes through the data, if neccessary
    print, strcompress(infile+string(frame(n_if_time))+" loop "+string(loop))
    tab_lab=""    ;initialize
    groot="A" ;start all gif files with A, unless dtrend_read instructs otherwise
    wsm=wsmooth  ;initialize
    log_scale=0 ;initialize
    setlog=0
    symbol=3
    data=dtrend_read(infile,data_in,loop,loop_out=loop_end, $
                     label=tab_lab,smooth=wsm,log_scale=setlog, gifroot=groot, $
                     symb=symbol)
    good=where(strpos(string(data.time),'NaN') eq -1)
    data=data(good)  ; there's so weird data out there, actually 
                     ; I think NaN's in time column come from bug in
                     ; tmp_save merge
    data_all=data  ; save a copy
    save_groot=groot
    save_tab_lab=tab_lab
    ;print,min(data.time),max(data.time) ;debugxxxx
    ;print,min(data.(1)),max(data.(1)) ;debugxxxx
    ;print,tag_names(data) ; debugxxx
  
    tnames=tag_names(data)
    keys=tnames(where(strpos(tnames,'_AVG') ge 0))
    
    xcol=min(where(strpos(strupcase(tnames),strupcase(xax)) ge 0))
    ccol=xcol ; initialize ccol
    if (xcol lt 0) then print, "xax column ", xax, " not found."
    if (keyword_set(ccode)) then begin
      ccol=min(where(strpos(strupcase(tnames),strupcase(ccode)) ge 0))
      if (ccol lt 0) then print, "ccode column ", ccode, " not found."
    endif ; if (keyword_set(ccode)) then begin
    
    ; rework name for labelling
    if (strpos(tnames(xcol),"X") eq 0) then s=1 else s=0
    if (rstrpos(tnames(xcol),"_AVG") gt s) then $
      len = rstrpos(tnames(xcol),"_AVG")-s $
    else len=20
    xmsid = strmid(tnames(xcol), s, len)

    if (n_if_time eq 3) then begin
      qtr=where(data.time ge max(data.time)-90*sperdy_ref)
      ;print,n_elements(data),max(data.time), sperdy_ref, qtr(0) ; debug qtr
      data=data(qtr)
      htmlfile=rootname+"_qtr.html"
      htmlout=strcompress(outdir+"/"+htmlfile, /remove_all)
      groot=save_groot+"qtr"
      tab_lab=save_tab_lab+" Previous Quarter"
      pred_days=30 ; only look 1 month forward
      ;data = data_all ; reset data
    endif ; if (n_if_time eq 3) then begin

    if (n_if_time eq 1) then begin
      htmlfile=rootname+"_max.html"
      htmlout=strcompress(outdir+"/"+htmlfile, /remove_all)
      groot=groot+"max"
      tab_lab=tab_lab+" Daily Maximums"
      data = data_all ; reset data
    endif ; if (n_if_time eq 1) then begin
    if (n_if_time eq 2) then begin
      htmlfile=rootname+"_min.html"
      htmlout=strcompress(outdir+"/"+htmlfile, /remove_all)
      groot=save_groot+"min"
      tab_lab=save_tab_lab+" Daily Minimums"
      data = data_all ; reset data
    endif ; if (n_if_time eq 2) then begin
      
    if (xaxtime ne 1) then begin
      xlim_struct = limits(xmsid,describe=xdes,unit=xunits)
      ;if (xlim_struct(0).yel_lo eq -999) then xlim=[-999]
      ;if (xlim_struct(0).yel_lo ne -999) then $
      ;  xlim=[xlim_struct(0).yel_lo, $
      ;        xlim_struct(0).yel_hi, $
      ;        xlim_struct(0).red_lo, $
      ;        xlim_struct(0).red_hi]
      ; ignore limits if not plotting versus time
      ;  (but still must call limits to set des and units
      ;lim=[-999] ; still need structure, set later
      xlim=[-999]
    endif ;if (xaxtime ne 1) then begin

    html = [html,'<tr align=center><td colspan=7>'+tab_lab+'</tr>']
    html = [html,'<tr align=center><td>MSID<td> MEAN<td> RMS'+ $
                   '<td> DELTA/'+strupcase(xunits)+ $
                   '<td> DELTA/'+strupcase(xunits)+'/'+strupcase(xunits)+ $
                   '<td> UNITS<td>DESCRIPTION</tr>']
    
    if (NOT keyword_set(filt_it)) then filt_it=1 ; filter once by default, more on request
    
    for i = 0, n_elements(keys)-1 do begin
    
      ; rework name for labelling
      if (strpos(keys(i),"X") eq 0) then s=1 else s=0
      if (rstrpos(keys(i),"_AVG") gt s) then len = rstrpos(keys(i),"_AVG")-s
      msid = strmid(keys(i), s, len)
    
      if (xmsid ne msid) then begin
        ;print, "Working ", keys(i)
        ;debug print, keys ; degub
        k = where(tnames eq strupcase(keys(i)),n)
        if (n ne 1) then print, keys(i)+" no good."
        j = k(0)
        ;x = where(strpos(string(data.(j)), 'NaN') eq -1)
        ; this is a little dangerous, but the old data (used for comp and grad
        ;             has -99 to mark bad/missing data
        x = where(strpos(string(data.(j)), 'NaN') eq -1 and data.(j) ne -99 $
            and strpos(string(data.(xcol)), 'NaN') eq -1 $
            and data.(xcol) ne -99, num)
        if (num gt 1) then begin
          xtime = data(x).(xcol)
          xtarr = data(x).time
          xdata = data(x).(j)
          xcolr = data(x).(ccol)
        endif else begin
          ;xtime = [xdmin,xdmax]
          xtime = [0,0,1,1]
          xtarr = [min(data.time),min(data.time),max(data.time),max(data.time)]
          xdata = [0,0,0,0]
          xcolr = [white,white,white,white]
        endelse
 
        ;xdmin = min(data.(xcol))
        ;xdmax = max(data.(xcol))
        xdmin = min(xtime)
        xdmax = max(xtime)
        xtmin = min(xtarr)
        xtmax = max(xtarr)
        xmin = xdmin - (xdmax-xdmin)*0.1
        if (xaxtime eq 1) then begin
          xmin=max([xmin,47174463])
          xmax = xdmax + pred_days*sperdy + (xdmax-xdmin)*0.1
          doyticks = pick_doy_ticks(xmin,xmax-43200,num=nticks)
          nticks=n_elements(doyticks)
        endif else begin
          xmax = xdmax + (xdmax-xdmin)*0.1
        endelse
        ;debug print, loop,loop_end,tag_names(data) ; debug
  
        ; figure out daily elements
        ;   how do I do this just once?  need xdata etc established
        ;                                to get indices right
        if (n_if_time eq 1 or n_if_time eq 2) then begin
          xndays = fix((xtmax-xtmin)/sperdy_ref)+5
          daily=lonarr(2,xndays) ; keep track of indices of daily start/stop
          dailytime=fltarr(xndays)
          idaily=0
          nel=n_elements(xtarr)
          for t = 1L, nel-1 do begin
            s = t-1 ; save start index
            start = xtarr(t-1)
            while (xtarr(t) lt start+sperdy_ref and t lt nel-2) do begin
              t=t+1
            endwhile
            daily(*,idaily)=[s,t-1]
            dailytime(idaily)=start+sperdy_ref/2.0
            idaily=idaily+1
          endfor ;for t = xdmin, xdmax, sperdy do begin
          daily = daily(*,0:idaily-1)
          dailytime=dailytime(0:idaily-1)
        endif ; if (xaxtime eq 1) then begin ; figure out daily elements
    
        tmpdata=fltarr(1) ; initialize
        tmptime=fltarr(1) ; initialize
        tmpcolr=fltarr(1) ; initialize
        if (n_if_time eq 1) then begin ;find daily maxes
          print, "Number of days: ", n_elements(daily(0,*)) ; debugme
          for k=0,n_elements(daily(0,*))-1 do begin
            tmp=xdata(daily(0,k):daily(1,k))
            mdat=fix(mymean(where(tmp eq max(tmp)))) ; choose middleish index
                                                 ; if more than one max value
            tmpdata=[tmpdata,tmp(mdat)]
            tmp=xtime(daily(0,k):daily(1,k))
            tmptime=[tmptime,tmp(mdat)]
            tmp=xcolr(daily(0,k):daily(1,k))
            tmpcolr=[tmpcolr,tmp(mdat)]
          endfor ; for k=0,n_elements(daily(0,*))-1 do begin
          xdata=tmpdata[1:*]
          xtime=tmptime[1:*]
          xcolr=tmpcolr[1:*]
          ;print, xdata ; debugdaily
          ;print, xtime ; debugdaily
        endif ; if (n_if_time eq 1) then begin ;find daily maxes
        if (n_if_time eq 2) then begin ;find daily mins
          for k=0,n_elements(daily(0,*))-1 do begin
            tmp=xdata(daily(0,k):daily(1,k))
            mdat=fix(mymean(where(tmp eq min(tmp)))) ; choose middleish index
                                                 ; if more than one max value
            tmpdata=[tmpdata,tmp(mdat)]
            tmp=xtime(daily(0,k):daily(1,k))
            tmptime=[tmptime,tmp(mdat)]
            tmp=xcolr(daily(0,k):daily(1,k))
            tmpcolr=[tmpcolr,tmp(mdat)]
          endfor ; for k=0,n_elements(daily(0,*))-1 do begin
          xdata=tmpdata[1:*]
          xtime=tmptime[1:*]
          xcolr=tmpcolr[1:*]
        endif ; if (n_if_time eq 1) then begin ;find daily mins
    
        ;print, n_elements(data), n_elements(x)  ; debugg
        for fit=1, filt_it do begin ; filter once by default, more on request
          m = moment(xdata)
          b = where(abs(xdata - m(0)) le sqrt(m(1))*sig,n_el)
          ;print, "sig filt", m(0), sqrt(m(1)), sig, $
          ;                    n_el, n_elements(xdata) ;debuggg
          if (n_el lt 3) then b=indgen(n_elements(xdata))
          xtime = xtime(b)
          xdata = xdata(b)
          xcolr = xcolr(b)
        endfor ;for fit=1, filt_it do begin
      
        m = moment(xdata) ; refigure mean
        rms = sqrt(m(1))
        n_el = n_elements(xdata)
        dfit = [m(0),0]
        if (m(1) gt 0) then dfit = linfit(xtime,xdata)
        if (n_el gt n_lim) then begin
          ;xfact = fix(n_el/n_lim)
          ;xtime = rebin(xtime, n_el/xfact)
          ;xdata = rebin(xdata, n_el/xfact)
          xtime = congrid(xtime, n_lim)
          xdata = congrid(xdata, n_lim)
          xcolr = congrid(xcolr, n_lim)
          ;b = intarr(n_lim)
          ;xtime = dsample(xtime, n_lim, minmax=xdata, idx=b)
          ;xdata = xdata(b)
          ;xcolr = xcolr(b)
        endif
        ;print, "  using # elements: ", n_elements(xdata) ; debug
          
        s=sort(xtime)
        xtime=xtime(s)
        xdata=xdata(s)
        xcolr=xcolr(s)

        if (keyword_set(ccode)) then begin
          cmap_range=200   ; cmap_range+cmap_zero le 255
          cmap_zero=50
          xcmin = min(xcolr)
          xcmax = max(xcolr)
          ccolor=fix((xcolr-xcmin)*cmap_range/(xcmax-xcmin))+cmap_zero
          crange=indgen(cmap_range)*(xcmax-xcmin)/cmap_range+xcmin
        endif else begin
          ccolor=replicate(white,n_elements(xdata))
        endelse ; if (keyword_set(ccode)) then begin

        ; get limit info
        lim = limits(msid,describe=des,unit=units)
        ; ignore limits if not plotting versus time
        ;  (but still must call limits to set des and units
        ;  and fake out time interval loop)
        if (xaxtime ne 1) then begin
          lim(0).tstart=min(xtime)-1
          lim(0).tstop=max(xtime)+1
          lim(0).yel_lo=-999
        endif ; if (xaxtime eq 1) then 
        if (des eq "") then des = msid
        r = abs(max(xdata)-min(xdata))
        if (r gt 0.10) then begin
          ymin = min(xdata)-0.10*r
          ymax = max(xdata)+0.10*r
        endif else begin
          ymin = min(xdata)-0.10*r
          ymax = max(xdata)+0.10*r
        endelse
        lognum=0
        if (setlog eq 1) then begin ; 0's don't work well on log plot
          b = where(xdata lt 0.01, lognum)
          if (lognum ge 1) then begin
            xdata_org=xdata
            xdata(b) = 0.01
            ymin_org = ymin
            ymin=0.009
          endif ; if (lognum ge 1) then begin
          if (ymin le 0) then begin
            xdata_org=xdata
            lognum=1
            ymin_org = ymin
            ymin=0.009
          endif ; if (ymin le 0) then begin
        endif ; if (setlog eq 1) then begin ; 0's don't work well on log plot
        ssize=1
        if (symbol ne 3) then ssize = 0.4
        if (keyword_set(ccode)) then begin
          !p.multi = [0,1,2,0,0]
          xrmarg=-30 ; right side of x axis 
                    ; (must be adjusted to fit color bar when ccode)
          ssize=0.2 && symbol=2
        endif else begin
          !p.multi = [0,1,2,0,0]
          xrmarg = 6
        endelse ; if (keyword_set(ccode)) then begin
        xlmarg=10
        minscale=min([abs(ymin),abs(ymax)])
        maxscale=max([abs(ymin),abs(ymax)])
        if ((minscale gt 0 and minscale lt 0.0001) or $
            (maxscale gt 10000)) then xlmarg=15 ; make more space for labels
        
        pcsize=0.8
        if (strlen(des) gt 54) then pcsize=1.0
        if (xaxtime eq 1) then begin
          plot, xtime, xdata, $
              psym=symbol, xstyle=1,ystyle=1, symsize=ssize, $
              ;title=des, xtitle='UT (DOY)', ytitle=msid+" ("+units+")", $
              title=des, xtitle='Time (DOY [UT])', ytitle=msid+" ("+units+")", $
              xrange=[xmin,xmax], yrange=[ymin,ymax], ylog=setlog, $
              charsize=pcsize,charthick=1,color=white,background=bgrd, $
              xticks=nticks-1, xtickv = doyticks, xminor=10, $
              xtickformat='s2doy_axis_labels', xmargin=[xlmarg,xrmarg]
              ;xtickformat='s2cal_axis_labels', xmargin=[xlmarg,xrmarg]
        endif ; if (xaxtime eq 1) then begin
        if (xaxtime eq 0) then begin
          if (xax eq "pt_suncent_ang") then begin
            xmin=40
            xmax=185
          endif
          if (xax eq "tephin") then begin
            xmin=265
            xmax=315
          endif
          if (strlen(des)+strlen(xdes) gt 54) then pcsize=0.8
          plot, xtime, xdata, $
              psym=symbol, xstyle=1,ystyle=1, symsize=ssize, $
              title=des+" vs "+xdes, xtitle= xmsid+" ("+xunits+")", $
              ytitle=msid+" ("+units+")", $
              xrange=[xmin,xmax], yrange=[ymin,ymax], ylog=setlog, $
              charsize = pcsize, charthick =1, $
              color = white, background = bgrd, xmargin=[xlmarg,xrmarg]
        endif ; if (xaxtime eq 0) then begin
        plots, xtime,xdata,color=ccolor,psym=symbol,symsize=ssize

        lim_done=0
        lim_struct=lim ; keep old lim,xtime,xdata variables
        xtime_all=xtime  ; so I don't have to rename all references
        xdata_all=xdata  ; and filters below
        xtime_dv=fltarr(1) ; save derive as we go
        xsave_dv=fltarr(1) ; to plt later
        for lim_loop=0,n_elements(lim_struct)-1 do begin ; start lim_loop
          ; set variables for this loop (limit time range)
          xtime=xtime_all
          xdata=xdata_all
          ;print,min(xtime),min(xtime) ;debugxxxx
          ;lstart=cxtime(lim_struct(lim_loop).tstart,'CAL','SEC')
          ;lstop=cxtime(lim_struct(lim_loop).tstop,'CAL','SEC')
          lstart=lim_struct(lim_loop).tstart
          lstop=lim_struct(lim_loop).tstop
          dates=where(xtime ge lstart and xtime lt lstop,dnum)
          ;print,"in lim_loop ",lstart,lstop,dnum ;debugdv
          if (dnum gt 0) then begin
            xtime=xtime(dates)
            xdata=xdata(dates)
            if (dnum gt 1) then m = moment(xdata) ; refigure mean
            dfit = [m(0),0]
            if (m(1) gt 0) then dfit = linfit(xtime,xdata)
            line = xtime*dfit(1)+dfit(0)
            if (setlog eq 1 and lognum ge 1) then begin ; reset 0's
              xdata=xdata_org
              ymin=ymin_org
            endif
            if (lim_struct(lim_loop).yel_lo eq -999) then lim=[-999]
            if (lim_struct(lim_loop).yel_lo ne -999) then $
              lim=[lim_struct(lim_loop).yel_lo, $
                     lim_struct(lim_loop).yel_hi, $
                     lim_struct(lim_loop).red_lo, $
                     lim_struct(lim_loop).red_hi]
  
            ;print,"lim_loop ",lim_loop    ; debug lim_loop
            ;print,lim,xlim  ; debug lim_loop
            if (lim(0) ne -999 and xlim(0) eq -999) then begin
              y = where((xdata ge lim(1) or xdata le lim(0)) and $
                        (xdata lt lim(3) and xdata gt lim(2)), ynum)
              r = where(xdata ge lim(3) or xdata le lim(2), rnum)
              if (ynum gt 0) then oplot, xtime(y), xdata(y), $
                                         psym=symbol, color=yellow, symsize=ssize
              if (rnum gt 0) then oplot, xtime(r), xdata(r), $
                                         psym=symbol, color=red, symsize=ssize
              g = where(line ge lim(0) and line le lim(1), gnum)
              y = where((line ge lim(1) or line le lim(0)) and $
                        (line lt lim(3) and line gt lim(2)), ynum)
              r = where(line ge lim(3) or line le lim(2), rnum)
              if (rnum gt 0) then oplot, xtime(r), line(r), color=red
              if (ynum gt 0) then oplot, xtime(y), line(y), color=yellow
              if (gnum gt 0) then oplot, xtime(g), line(g), color=green
              lim_done=1
            endif ;if (lim(0) ne -999 and xlim(0) eq -999) then begin
            if (lim(0) eq -999 and xlim(0) ne -999) then begin
              y = where((xtime ge xlim(1) or xtime le xlim(0)) and $
                        (xtime lt xlim(3) and xtime gt xlim(2)), ynum)
              r = where(xtime ge xlim(3) or xtime le xlim(2), rnum)
              if (ynum gt 0) then oplot, xtime(y), xdata(y), $
                                         psym=symbol, color=yellow, symsize=ssize
              if (rnum gt 0) then oplot, xtime(r), xdata(r), $
                                         psym=symbol, color=red, symsize=ssize
              lim_done=1
            endif ;if (lim(0) eq -999 and xlim(0) ne -999) then begin
            if (lim(0) ne -999 and xlim(0) ne -999) then begin
              y = where((xdata ge lim(1) or xdata le lim(0)) and $
                        (xdata lt lim(3) and xdata gt lim(2)) or $
                        (xtime ge xlim(1) or xtime le xlim(0)) and $
                        (xtime lt xlim(3) and xtime gt xlim(2)), ynum)
              r = where(xdata ge lim(3) or xdata le lim(2) or $
                       xtime ge xlim(3) or xtime le xlim(2), rnum)
              if (ynum gt 0) then oplot, xtime(y), xdata(y), $
                                         psym=symbol, color=yellow, symsize=ssize
              if (rnum gt 0) then oplot, xtime(r), xdata(r), $
                                         psym=symbol, color=red, symsize=ssize
              g = where(line ge lim(0) and line le lim(1), gnum)
              y = where((line ge lim(1) or line le lim(0)) and $
                        (line lt lim(3) and line gt lim(2)), ynum)
              r = where(line ge lim(3) or line le lim(2), rnum)
              if (rnum gt 0) then oplot, xtime(r), line(r), color=red
              if (ynum gt 0) then oplot, xtime(y), line(y), color=yellow
              if (gnum gt 0) then oplot, xtime(g), line(g), color=green
              lim_done=1
            endif ;if (lim(0) ne -999 and xlim(0) ne -999) then begin
            if (lim_done eq 0) then oplot, xtime, line, color=blue
        
            if (wsmooth gt 0) then begin
              ; convert to seconds
              ws = wsm * sperdy
              dv = dsmooth(xtime, xdata, fit=df, w=ws)
            endif else begin
              dv = dsmooth(xtime, xdata, fit=df)
            endelse
          
            ; get rid of too-tiny garbage
            ;mac = machar()
            ;zero = where(abs(dv) lt 0.01*(mac.epsneg), num)
            zero = where(abs(dv) lt 0.001*sqrt(m(1))/speryr, num)
            if (num gt 0) then dv(zero) = 0.0
            if (rms eq 0) then dv(0:*)=0.0
      
            oplot, xtime, df, color=blue
            xtime_dv=[xtime_dv,xtime]
            xsave_dv=[xsave_dv,dv] ; save for deriv plot
            ;print,"dv ",dv ;debugdv
          endif ; if (dnum gt 0) then begin
        endfor ; for lim_loop=0,n_elements(lim_struct)-1 do begin
        ; only do the rest for last, most recent lim_loop
        if (n_elements(dv) ge 2) then begin
          dm=moment(dv)
        endif else begin
          dv=[999,999]
          dm=[0,0,0,0,0]
        endelse
        b = where(abs(dv - dm(0)) le sqrt(dm(1))*sig,n_el)
        if (n_el lt 3) then b=indgen(n_elements(dv))
        ddfit = linfit(xtime(b), dv(b))
    
        tlim = pred_days*sperdy ; look pred_days into future
        ; oplot dfit and ddfit prediction
        if (xaxtime eq 1) then begin
          xtime_dv=xtime_dv(1:*) ; saved from above, don't need (and doesn't
          xsave_dv=xsave_dv(1:*) ; make sense if 
                                 ; not plotting against time
          last = max(xtime)+tlim
          lastval=dfit(1)*max(xtime)+dfit(0)
          tfit = float(indgen(100))/100.0*tlim
          ;dtest = (dfit(1)*tlim) + lastval
          ddtest = (ddfit(1)*tfit+dfit(1))*tfit + lastval
          ;oplot, [max(xtime),last],[lastval,dtest],linestyle=4
          if (lim(0) ne -999) then begin
            g = where(ddtest ge lim(0) and ddtest le lim(1), gnum)
            y = where((ddtest ge lim(1) or ddtest le lim(0)) and $
                      (ddtest lt lim(3) and ddtest gt lim(2)), ynum)
            r = where(ddtest ge lim(3) or ddtest le lim(2), rnum)
            if (rnum gt 0) then oplot, tfit(r)+max(xtime), ddtest(r), color=red, linestyle=3
            if (ynum gt 0) then oplot, tfit(y)+max(xtime), ddtest(y), color=yellow, linestyle=3
            if (gnum gt 0) then oplot, tfit(g)+max(xtime), ddtest(g), color=green, linestyle=3
          endif else begin
            oplot, tfit+max(xtime), ddtest, color=blue, linestyle=3
          endelse ; if (lim(0) ne -1) then begin
        endif ;if (xaxtime eq 1) then begin

        ; oplot envelope
        readcol,'Env_test/tavg_1pin1at_att_10deg_4.out',date,avg,std,bot,mid,top,spr
        ;readcol,'Env_test/tavg_1pin1at_1mo_6.out',date,avg,std,bot,mid,top,spr
        ;oplot,date,avg,color=blue-15
        oplot,date,bot,color=blue-15,thick=5
        oplot,date,top,color=blue-15,thick=5
        ;oplot,date,mid,color=blue-15

      
        ; color bar if ccode
        if (keyword_set(ccode)) then begin
          if (strupcase(ccode) eq 'TIME') then begin
            crange=cxtime(crange) 
            ynam='TIME (DOM)'
          endif else begin
            ynam=strupcase(ccode)
          endelse ; if (strupcase(ccode) eq 'TIME') then begin
          ;plot,0*indgen(256),crange,thick=10, $
          ;     ymargin=[-30,4],xmargin=[-1.0*xrmarg+25,6], $
          ;     xrange=[-1,1],xstyle=5,ystyle=9,xticks=1, $
          ;     charsize=0.7, ytitle=ynam
          ;plots,0*indgen(cmap_range),crange,$
          ;      color=indgen(cmap_range)+cmap_zero,thick=10 
        endif ; if (keyword_set(ccode)) then begin
      
        r = max(xsave_dv*speryr)-min(xsave_dv*speryr)
        if (r gt 0) then begin
          ymin = min(xsave_dv*speryr)-0.10*r
          ymax = max(xsave_dv*speryr)+0.10*r
        endif else begin
          ymin = min(xsave_dv*speryr)*0.90
          ymax = max(xsave_dv*speryr)*1.10
        endelse
        ;print, r, ymin, ymax ; debug
        if (xaxtime eq 1) then begin
          plot, xtime_dv, xsave_dv*speryr, $
              xstyle=1,ystyle=1, psym=symbol, symsize=ssize, $
              title=strcompress("dy/dx "+msid), $
              ;xtitle='UT (DOY)', ytitle=units+'/Year', $
              xtitle='Time (DOY [UT])', ytitle=units+'/Year', $
              xrange=[xmin,xmax], yrange=[ymin,ymax], $
              charsize=pcsize,charthick=1,color=white,background=bgrd, $
              xticks=nticks-1, xtickv = doyticks, xminor=10, $
              xtickformat='s2doy_axis_labels', xmargin=[xlmarg,xrmarg]
              ;xtickformat='s2cal_axis_labels', xmargin=[xlmarg,xrmarg]
          ycon = convert_coord([0],[0], /device, /to_data)
          label_year, xmin, xmax, ycon(1), csize=0.6
        endif
        if (xaxtime eq 0) then $
          plot, xtime, dv*speryr, $
              xstyle=1,ystyle=1, psym=symbol, symsize=ssize, $
              title=strcompress("dy/dx "+msid), $
              xtitle= xmsid+" ("+xunits+")", $
              ytitle=units+'/'+xunits, $
              xrange=[xmin,xmax], yrange=[ymin,ymax], $
              charsize = pcsize, charthick =1, $
              color = white, background = bgrd, xmargin=[xlmarg,xrmarg]
        plots, xtime,dv*speryr,color=ccolor,psym=symbol,symsize=ssize
        line = (ddfit(1)*xtime+ddfit(0))*speryr
        oplot, xtime, line, color=blue
        giffile=strcompress(strlowcase(keys(i))+groot+ $
                               '.gif', /remove_all)
        ;write_gif, "Spie_plot/"+giffile, tvrd()
        device, /close
       
      ; make html outfile
        if (units eq "") then units = "&#160"
        mean_color = hwhite
        rms_color = hwhite
        d_color = hwhite
        dd_color = hwhite
        u_color = hwhite
        ; flag if derivatives project busted limited within tlim seconds
        ; (in terms of fraction of plotted range)
        if (lim(0) ne -999) then begin  ; color code based on limits
          if (m(0) le lim(0) or m(0) ge lim(1)) then mean_color=hyellow
          if (m(0) le lim(2) or m(0) ge lim(3)) then mean_color=hred
          if (m(0)-rms le lim(0) or m(0)+rms ge lim(1)) then rms_color=hyellow
          if (m(0)-rms le lim(2) or m(0)+rms ge lim(3)) then rms_color=hred
          if (xaxtime eq 1) then begin
            test = dfit(1)*tlim+lastval
            if (test ge lim(1) or test le lim(0)) then d_color = hyellow
            if (test ge lim(3) or test le lim(2)) then d_color = hred
            ; second deriv test
            ;test = (ddfit(1)*last+ddfit(0))*tlim + m(0)
            test = (ddfit(1)*tlim+dfit(1))*tlim + lastval
            if (test ge lim(1) or test le lim(0)) then dd_color = hyellow
            if (test ge lim(3) or test le lim(2)) then dd_color = hred
          endif ; if (xaxtime eq 1) then begin
        endif else begin
          if (xaxtime eq 1) then begin
            u_color = hblue ; mark units as not having op limits
            ;test = abs(dfit(1)*last+dfit(0) - m(0))/m(0)
            ;test = abs(dfit(1)*last+dfit(0) - m(0))/rms
            test = abs(dfit(1)*tlim)/rms
            if (rms gt 0.0 and test ge 2) then d_color = hyellow
            if (rms gt 0.0 and test ge 3) then d_color = hred
            ; second deriv test
            ;test = abs(ddfit(1)*tlim*tlim)/rms
            ;test = (ddfit(1)*last+ddfit(0))*tlim/rms
            test = abs((ddfit(1)*tlim+dfit(1))*tlim)/rms
            ;print, (ddfit(1)*last+ddfit(0)) ; debug
            if (rms gt 0.0 and test ge 2) then dd_color = hyellow
            if (rms gt 0.0 and test ge 3) then dd_color = hred
          endif ; if (xaxtime eq 1) then begin
        endelse; if (lim(0) ne -1) then begin  ; color code based on limits
      
        html = [html,'<tr><td><a href="javascript:WindowOpener('+ $
                    "'"+giffile+"')"+'">'+ $
                     msid+'</a></td>']
        html = [html,'<td><font color="'+mean_color+'">'+ $
                     string(format='(e10.3)',m(0))+'</font></td>']
        html = [html,'<td><font color="'+rms_color+'">'+ $
                     string(format='(e10.3)',sqrt(m(1)))+'</font></td>']
        html = [html,'<td><font color="'+d_color+'">'+ $
                     string(format='(e10.3)',dfit(1)*speryr)+'</font></td>']
        html = [html,'<td><font color="'+dd_color+'">'+ $
                     string(format='(e10.3)',ddfit(1)*speryr*speryr)+'</font></td>']
        html = [html,'<td><font color="'+u_color+'">'+ $
                     units+'</font></td>']
        html = [html,'<td>'+des+'</td></tr>']
      
        ; check to see if we should indicate violations on index page
        if (mean_color eq hyellow or rms_color eq hyellow or $
            d_color eq hyellow or dd_color eq hyellow) then $
          ymark = ymark+1
        if (mean_color eq hred or rms_color eq hred or $
            d_color eq hred or dd_color eq hred) then $
          rmark = rmark+1
      endif ; if (xmsid ne msid) then begin
    endfor ;for j = 1, n_elements(keys)-1 do begin
    
    loop = loop + 1
  
  endwhile ; while (loop le loop_end) do begin
    
  ; write html output
  dtrend_html, min(data.time),max(data.time), html, htmlout, rootname
  
  ; update index file 
  ; figure num lines input
  xnum = strarr(1)
  spawn, 'wc -l '+ifile, xnum
  xxnum = fltarr(2)
  xxnum = strsplit(xnum(0),' ', /extract)
  numlns = long(xxnum(0))

  get_lun, iunit
  openr, iunit, ifile

  array = strarr(numlns)
  readf, iunit, array

  close, iunit
  free_lun, iunit

  get_lun, ounit
  openw, ounit, ifile

  data_sec = 0 ; have not found update section yet

  for i = 0, numlns-1 do begin
    if (strpos(array(i), '<!-- start last updated -->') ge 0) then begin
      data_sec = 1
      xmin = min(data_all.time)
      xmax = max(data_all.time)
      printf, ounit, '<!-- start last updated -->'
      printf, ounit, '<table width=100% border=0>'
      printf, ounit, '<tr>'
      printf, ounit, '<td align=center colspan=2>Last updated: '
      ;print, speryr_ref, sperdy_ref ; debug
      update = systime(1) - speryr_ref*21 - 7*(speryr_ref+sperdy_ref)
      ;print, systime(1), " ", update ; debug
      ;print, cxtime(systime(1),'sec','cal'), " ", cxtime(update,'sec','cal') ; debug
      printf, ounit, strtrim(cxtime(update,'sec','cal'),2)
      printf, ounit, 'DOM '
      printf, ounit, strtrim(string(fix(cxtime(update,'sec','met'))),2)
      printf, ounit, '  ('+rootname+')'
      printf, ounit, '</td></tr>'
      printf, ounit, '<td align=left>Data start: '
      printf, ounit, strtrim(cxtime(xmin,'sec','cal'),2)
      printf, ounit, 'DOM '
      printf, ounit, strtrim(string(fix(cxtime(xmin,'sec','met'))),2)
      printf, ounit, '</td>'
      printf, ounit, '<td align=right>Data end: '
      printf, ounit, strtrim(cxtime(xmax,'sec','cal'),2)
      printf, ounit, 'DOM '
      printf, ounit, strtrim(string(fix(cxtime(xmax,'sec','met'))),2)
      printf, ounit, '</td>'
      printf, ounit, '</tr>'
      printf, ounit, '</table>'
    endif ; <!-- start last updated -->
  
    if (strpos(array(i), '<!-- end last updated -->') ge 0) then begin
      data_sec = 0
    endif ; <!-- end last updated -->

    if (data_sec eq 0) then begin  ; not in data section, so copy old file
      if (strpos(array(i), htmlfile) ge 0) then begin
        lstart=strpos(array(i),"src")
        lend=strpos(array(i),"></a>")
        if (ymark gt 0 and rmark le 0) then $
          printf, ounit, strmid(array(i),0,lstart)+'src="yellow.gif"'+strmid(array(i),lend,200)
        if (rmark gt 0) then $
          printf, ounit, strmid(array(i),0,lstart)+'src="red.gif"'+strmid(array(i),lend,200)
        if (ymark le 0 and rmark le 0) then $
          printf, ounit, strmid(array(i),0,lstart)+'src="green.gif"'+strmid(array(i),lend,200)
      endif else begin  ; if (strpos(array(i), htmlout) ge 0) then begin
        printf, ounit, array(i)
      endelse  ; if (strpos(array(i), htmlout) ge 0) then begin
    endif ; copy old file

  ;oldif (data_sec eq 0) then begin  ; not in data section, so copy old file
    ;oldif (strpos(array(i), htmlfile) ge 0) then begin
      ;oldlstart=strpos(array(i),"<li")
      ;oldif (ymark gt 0 and rmark le 0) then $
        ;oldprintf, ounit, '<font color="'+hyellow+'">'+strmid(array(i),lstart,200)
      ;oldif (rmark gt 0) then $
        ;oldprintf, ounit, '<font color="'+hred+'">'+strmid(array(i),lstart,200)
      ;oldif (ymark le 0 and rmark le 0) then $
        ;oldprintf, ounit, '<font color="'+hwhite+'">'+strmid(array(i),lstart,200)
    ;oldendif else begin  ; if (strpos(array(i), htmlout) ge 0) then begin
      ;oldprintf, ounit, array(i)
    ;oldendelse  ; if (strpos(array(i), htmlout) ge 0) then begin
    ;oldendif ; copy old file

  endfor
  free_lun, ounit  
endfor ; for n_if_time = 0, nminmax, do begin ; loop to do daily min/max


retall
end
