PRO DTREND, infile, SIG=sig, WSMOOTH=wsmooth, PLOTX=plotx
; make trending and derivative plots
; input:
;     infile - file returned by dataseeker
;     sig - filter out any data more than sig sigma from mean (default 3)
;     wsmooth - smoothing factor (number of days to smooth over)
; v1.3
; 12.Mar 2002 BDS - add limit checking, indications
; v1.4
; 21.Mar 2002 BDS - just a few minor, mostly cosmetic improvements
; v1.5
; 28.Mar 2002 BDS - added dtrend_read for customized processing

; directory for web output
outdir="/data/mta/www/mta_deriv"
;outdir="/data/mta/www/mta_deriv/TEST"
ifile=outdir+"/index.html"

; limit number of points plotted
;  (and number of points dsmooth uses, it's slow)
n_lim=5000
; other things user can set
nticks=6

; constants
speryr=31536000.0

nstart=rstrpos(infile, "/")+1
nstop=rstrpos(infile,".")
if (nstop lt nstart) then nstop = nstart+20
rootname=strmid(infile,nstart,nstop-nstart)
htmlout=strcompress(outdir+"/"+rootname+".html", /remove_all)
htmltmp=outdir+"/tmp.html"

if (NOT keyword_set(sig)) then sig=3
if (NOT keyword_set(wsmooth)) then wsmooth = 0

; plotting stuff
!p.multi = [0,1,2,0,0]
xwidth=720
yheight=550

; colors
loadct, 39
white = 255
bgrd = 0
red = 230
yellow = 190
blue = 100
green = 150
purple = 50
orange = 215
hred = "#FF0000"
hyellow = "#FFFF00"
hgreen = "#33FF33"
hblue = "#33CCFF"
hwhite = "#FFFFFF"

if (keyword_set(plotx)) then begin
  set_plot, 'X'
  window, 0, xsize=xwidth, ysize=yheight,retain=2
endif else begin
  set_plot, 'Z'
  device, set_resolution = [xwidth, yheight]
endelse

data_in=mrdfits(infile,1) ; this is an extra read, just to get dates
                       ;  is there another way?
xmin = min(data_in.time)
xmax = max(data_in.time)
print, "Start ", cxtime(xmin, 'sec','cal'), " DOM ", cxtime(xmin,'sec','met')
print, "End ", cxtime(xmax, 'sec','cal'), " DOM ", cxtime(xmax,'sec','met')
xmin = xmin - (xmax-xmin)*0.1
xmax = xmax + (xmax-xmin)*0.1
doyticks = pick_doy_ticks(xmin,xmax-43200,num=nticks)

; setup html file
get_lun, sunit ; file unit for stat ouput
openw, sunit, htmltmp
printf, sunit, '<HTML>'
printf, sunit, '<HEAD>'
printf, sunit, '     <TITLE>'+strupcase(rootname)+'_AVG Trends</TITLE>'
printf, sunit, '</HEAD>'
printf, sunit, '<BODY TEXT="#DDDDDD" BGCOLOR="#000000"'+ $
               'LINK="#00CCFF" VLINK="#EEEEEE" ALINK="#7500FF">'
printf, sunit, '<h1><center>'+strupcase(rootname)+'   Trends</center></h1>'
printf, sunit, '<br><hr><br>'

; this part is terribly confusing
;  you need both kinds of quotes, so have to switch back and forth
printf, sunit, ''
printf, sunit, '<script language="JavaScript">'
printf, sunit, '  function WindowOpener(imgname) {'
printf, sunit, '    msgWindow = open("","displayname",'+ $
               '"toolbar=no,directories=no,menubar=no,'+ $
               'location=no,scrollbars=no,status=no,'+ $
               'width=720,height=570,resize=no");'
printf, sunit, '    msgWindow.document.clear();'
printf, sunit, '    msgWindow.document.write("<HTML><TITLE>Trend plot:   "'+ $
               '+imgname+"</TITLE>");'
printf, sunit, '    msgWindow.document.write("<BODY BGCOLOR='+"'black'"+'>");'
printf, sunit, '    msgWindow.document.write("<IMG SRC='+"'"+'"'+ $
               '+imgname+'+ $
               '"'+"'"+' BORDER=0><P></BODY></HTML>");'
printf, sunit, '    msgWindow.focus();'
printf, sunit, '  }'
printf, sunit, '</script>'
printf, sunit, ''

printf, sunit, '<table width=100% border=0>'
printf, sunit, '<tr>'
printf, sunit, '<td align=center colspan=2>Last updated: '
update = systime(1) - speryr*21 - 7*(speryr+86400)
printf, sunit, strtrim(cxtime(update,'sec','cal'),2)
printf, sunit, 'DOM '
printf, sunit, strtrim(string(fix(cxtime(update,'sec','met'))),2)
printf, sunit, '</td></tr>'
printf, sunit, '<td align=left>Data start: '
printf, sunit, strtrim(cxtime(min(data_in.time),'sec','cal'),2)
printf, sunit, 'DOM '
printf, sunit, strtrim(string(fix(cxtime(min(data_in.time),'sec','met'))),2)
printf, sunit, '</td>'
printf, sunit, '<td align=right>Data end: '
printf, sunit, strtrim(cxtime(max(data_in.time),'sec','cal'),2)
printf, sunit, 'DOM '
printf, sunit, strtrim(string(fix(cxtime(max(data_in.time),'sec','met'))),2)
printf, sunit, '</td>'
printf, sunit, '</tr>'
printf, sunit, '</table>'

printf, sunit, '<br><hr><br>'
printf, sunit, '<center>'
printf, sunit, '<table border=1 cellpadding=3>'

rmark = 0 ; counter for red violation
ymark = 0 ; counter for yellow violation
;data=mrdfits(infile, 1)
loop=1
loop_end=1
while (loop le loop_end) do begin ; this is the loop to do several
                                  ; passes through the data, if neccessary
tab_lab=""    ;initialize
groot="A" ;start all gif files with A, unless dtrend_read instructs otherwise
wsm=wsmooth  ;initialize
log_scale=0 ;initialize
setlog=0
symbol=3
data=dtrend_read(infile,data_in,loop,loop_out=loop_end, $
                 label=tab_lab,smooth=wsm,log_scale=setlog, gifroot=groot, $
                 symb=symbol)
xmin = min(data.time)
xmax = max(data.time)
xmin = xmin - (xmax-xmin)*0.1
xmax = xmax + (xmax-xmin)*0.1
doyticks = pick_doy_ticks(xmin,xmax-43200,num=nticks)
;debug print, loop,loop_end,tag_names(data) ; debug

printf, sunit, '<tr align=center><td colspan=7>'+tab_lab+'</tr>
printf, sunit, '<tr align=center><td>MSID<td> MEAN<td> RMS'+ $
               '<td> DELTA/YR<td> DELTA/YR/YR'+ $
               '<td> UNITS<td>DESCRIPTION</tr>'

tnames=tag_names(data)
keys=tnames(where(strpos(tnames,'_AVG') ge 0))

for i = 0, n_elements(keys)-1 do begin

  ; rework name for labelling
  if (strpos(keys(i),"X") eq 0) then s=1 else s=0
  if (rstrpos(keys(i),"_AVG") gt s) then len = rstrpos(keys(i),"_AVG")-s
  msid = strmid(keys(i), s, len)

  print, "Working ", keys(i)
  ;debug print, keys ; degub
  k = where(tnames eq strupcase(keys(i)),n)
  if (n ne 1) then print, keys(i)+" no good."
  j = k(0)
  x = where(strpos(string(data.(j)), 'NaN') eq -1)
  xtime = data(x).time
  xdata = data(x).(j)
  m = moment(xdata)
  b = where(abs(xdata - m(0)) le sqrt(m(1))*sig,n_el)
  if (n_el lt 3) then b=indgen(n_elements(xdata))
  xtime = xtime(b)
  xdata = xdata(b)
  m = moment(xdata) ; refigure mean
  n_el = n_elements(xdata)
  dfit = [m(0),0]
  if (m(1) gt 0) then dfit = linfit(xtime,xdata)
  if (n_el gt n_lim) then begin
    ;xfact = fix(n_el/n_lim)
    ;xtime = rebin(xtime, n_el/xfact)
    ;xdata = rebin(xdata, n_el/xfact)
    xtime = congrid(xtime, n_lim)
    xdata = congrid(xdata, n_lim)
  endif
  ;print, "  using # elements: ", n_elements(xdata) ; debug
    
  ; get limit info
  lim = limits(msid,describe=des,unit=units)
  if (des eq "") then des = msid
  r = max(xdata)-min(xdata)
  if (r gt 0) then begin
    ymin = min(xdata)-0.10*r
    ymax = max(xdata)+0.10*r
  endif else begin
    ymin = min(xdata)-0.10
    ymax = max(xdata)+0.10
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
  plot, xtime, xdata, psym=symbol, ystyle=1, symsize=ssize, $
        title=des, xtitle='UT (DOY)', ytitle=msid+" ("+units+")", $
        xrange=[xmin,xmax], yrange=[ymin,ymax], ylog=setlog, $
        charsize = 1.0, charthick =1, color = white, background = bgrd, $
        xticks=nticks-1, xtickv = doyticks, xminor=10, $
        xtickformat='s2doy_axis_labels'
  line = xtime*dfit(1)+dfit(0)
  if (setlog eq 1 and lognum ge 1) then begin ; reset 0's
    xdata=xdata_org
    ymin=ymin_org
  endif
  if (lim(0) ne -999) then begin
    y = where(xdata ge lim(1) or xdata le lim(0), ynum)
    r = where(xdata ge lim(3) or xdata le lim(2), rnum)
    if (ynum gt 0) then oplot, xtime(y), xdata(y), $
                               psym=symbol, color=yellow, symsize=ssize
    if (rnum gt 0) then oplot, xtime(r), xdata(r), $
                               psym=symbol, color=red, symsize=ssize
    g = where(line ge lim(0) and line le lim(1), gnum)
    y = where(line ge lim(1) or line le lim(0), ynum)
    r = where(line ge lim(3) or line le lim(2), rnum)
    if (gnum gt 0) then oplot, xtime(g), line(g), color=green
    if (ynum gt 0) then oplot, xtime(y), line(y), color=yellow
    if (rnum gt 0) then oplot, xtime(r), line(r), color=red
  endif else begin
    oplot, xtime, line, color=blue
  endelse ; if (lim(0) ne -1) then begin

  if (wsmooth gt 0) then begin
    ; convert to seconds
    ws = wsm * 86400.0
    dv = dsmooth(xtime, xdata, fit=df, w=ws)
  endif else begin
    dv = dsmooth(xtime, xdata, fit=df)
  endelse

  ; get rid of too-tiny garbage
  mac = machar()
  zero = where(abs(dv) lt mac.epsneg, num)
  if (num gt 0) then dv(zero) = 0.0

  oplot, xtime, df, color=blue
  dm=moment(dv)
  b = where(abs(dv - dm(0)) le sqrt(dm(1))*sig,n_el)
  if (n_el lt 3) then b=indgen(n_elements(dv))
  ddfit = linfit(xtime(b), dv(b))
  r = max(dv*speryr)-min(dv*speryr)
  if (r gt 0) then begin
    ymin = min(dv*speryr)-0.10*r
    ymax = max(dv*speryr)+0.10*r
  endif else begin
    ymin = min(dv*speryr)-0.10
    ymax = max(dv*speryr)+0.10
  endelse
  plot, xtime, dv*speryr, ystyle=1, psym=symbol, symsize=ssize, $
        title=strcompress("dy/dx "+msid), $
              ;" delta units/day/day="+string(format='(e10.3)',ddfit(1))), $
        xtitle='UT (DOY)', ytitle=units+'/Year', $
        xrange=[xmin,xmax], yrange=[ymin,ymax], $
        charsize = 1.0, charthick =1, color = white, background = bgrd, $
        xticks=nticks-1, xtickv = doyticks, xminor=10, $
        xtickformat='s2doy_axis_labels'
  line = (ddfit(1)*xtime+ddfit(0))*speryr
  oplot, xtime, line, color=blue
  ycon = convert_coord([0],[0], /device, /to_data)
  label_year, xmin, xmax, ycon(1), csize=1.2
  giffile=strcompress(strlowcase(keys(i))+groot+ $
                         '.gif', /remove_all)
  write_gif, outdir+"/"+giffile, tvrd()
 
; make html outfile
  if (units eq "") then units = "&#160"
  mean_color = hwhite
  rms_color = hwhite
  d_color = hwhite
  dd_color = hwhite
  u_color = hwhite
  rms = sqrt(m(1))
  ; flag if derivatives project busted limited within tlim seconds
  ; (in terms of fraction of plotted range)
  tlim = 180*86400 ; look 6 months into future
  last = max(xtime)+tlim
  if (lim(0) ne -999) then begin  ; color code based on limits
    if (m(0) le lim(0) or m(0) ge lim(1)) then mean_color=hyellow
    if (m(0) le lim(2) or m(0) ge lim(3)) then mean_color=hred
    if (m(0)-rms le lim(0) or m(0)+rms ge lim(1)) then rms_color=hyellow
    if (m(0)-rms le lim(2) or m(0)+rms ge lim(3)) then rms_color=hred
    test = dfit(1)*last+dfit(0)
    if (test ge lim(1) or test le lim(0)) then d_color = hyellow
    if (test ge lim(3) or test le lim(2)) then d_color = hred
    ; second deriv test
    test = (ddfit(1)*last+ddfit(0))*tlim + m(0)
    if (test ge lim(1) or test le lim(0)) then dd_color = hyellow
    if (test ge lim(3) or test le lim(2)) then dd_color = hred
  endif else begin
    u_color = hblue ; mark units as not having op limits
    ;test = abs(dfit(1)*last+dfit(0) - m(0))/m(0)
    ;test = abs(dfit(1)*last+dfit(0) - m(0))/rms
    test = abs(dfit(1)*tlim)/rms
    if (rms gt 0.0 and test ge 2) then d_color = hyellow
    if (rms gt 0.0 and test ge 3) then d_color = hred
    ; second deriv test
    ;test = abs(ddfit(1)*tlim*tlim)/rms
    test = (ddfit(1)*last+ddfit(0))*tlim/rms
    ;print, (ddfit(1)*last+ddfit(0)) ; debug
    if (rms gt 0.0 and test ge 2) then dd_color = hyellow
    if (rms gt 0.0 and test ge 3) then dd_color = hred
  endelse; if (lim(0) ne -1) then begin  ; color code based on limits

  printf, sunit, '<tr><td><a href="javascript:WindowOpener('+ $
                 "'"+giffile+"')"+'">'+ $
                  msid+'</a></td>'
  printf, sunit, '<td><font color="'+mean_color+'">'+ $
                  string(format='(e10.3)',m(0))+'</font></td>'
  printf, sunit, '<td><font color="'+rms_color+'">'+ $
                  string(format='(e10.3)',sqrt(m(1)))+'</font></td>'
  printf, sunit, '<td><font color="'+d_color+'">'+ $
                  string(format='(e10.3)',dfit(1)*speryr)+'</font></td>'
  printf, sunit, '<td><font color="'+dd_color+'">'+ $
                  string(format='(e10.3)',ddfit(1)*speryr*speryr)+'</font></td>'
  printf, sunit, '<td><font color="'+u_color+'">'+ $
                  units+'</font></td>'
  printf, sunit, '<td>'+des+'</td></tr>'

  ; check to see if we should indicate violations on index page
  if (mean_color eq hyellow or rms_color eq hyellow or $
      d_color eq hyellow or dd_color eq hyellow) then $
    ymark = ymark+1
  if (mean_color eq hred or rms_color eq hred or $
      d_color eq hred or dd_color eq hred) then $
    rmark = rmark+1
endfor ;for j = 1, n_elements(keys)-1 do begin

loop = loop + 1
endwhile ; while (loop le loop_end) do begin
; close html file
printf, sunit, '</table>'
printf, sunit, '</center>'
printf, sunit, '</body></html>'
close, sunit
spawn, "mv "+htmltmp+" "+htmlout

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

free_lun, iunit

get_lun, ounit
openw, ounit, ifile

data_sec = 0 ; have not found update section yet

for i = 0, numlns-1 do begin
  if (strpos(array(i), '<!-- start last updated -->') ge 0) then begin
    data_sec = 1
    xmin = min(data.time)
    xmax = max(data.time)
    printf, ounit, '<!-- start last updated -->'
    printf, ounit, '<table width=100% border=0>'
    printf, ounit, '<tr>'
    printf, ounit, '<td align=center colspan=2>Last updated: '
    ;printf, ounit, systime()+'  ('+rootname+')'
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
    if (strpos(array(i), rootname+".html") ge 0) then begin
      lstart=strpos(array(i),"<li")
      if (ymark gt 0 and rmark le 0) then $
        printf, ounit, '<font color="'+hyellow+'">'+strmid(array(i),lstart,100)
      if (rmark gt 0) then $
        printf, ounit, '<font color="'+hred+'">'+strmid(array(i),lstart,100)
      if (ymark le 0 and rmark le 0) then $
        printf, ounit, '<font color="'+hwhite+'">'+strmid(array(i),lstart,100)
    endif else begin  ; if (strpos(array(i), htmlout) ge 0) then begin
      printf, ounit, array(i)
    endelse  ; if (strpos(array(i), htmlout) ge 0) then begin
  endif ; copy old file
endfor

free_lun, ounit  

retall
end
