PRO DTREND, infile, SIG=sig, WSMOOTH=wsmooth, KEYS=keys, PLOTX=plotx, $
            APPEND=append, LABEL=label
; make trending and derivative plots
; input:
;     infile - file returned by dataseeker
;     sig - filter out any data more than sig sigma from mean (default 3)
;     wsmooth - smoothing factor (number of days to smooth over)
; v1.3
; 12.Mar 2002 BDS - add limit checking, indications
; v1.4
; 21.Mar 2002 BDS - just a few minor, mostly cosmetic improvements

; directory for web output
outdir="/data/mta/www/mta_deriv"
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

if (NOT keyword_set(sig)) then sig=3
if (NOT keyword_set(wsmooth)) then wsmooth = 0
; convert to seconds
wsmooth = wsmooth * 86400.0

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

data=mrdfits(infile, 1)
xmin = min(data.time)
xmax = max(data.time)
print, "Start ", cxtime(xmin, 'sec','cal'), " DOM ", cxtime(xmin,'sec','met')
print, "End ", cxtime(xmax, 'sec','cal'), " DOM ", cxtime(xmax,'sec','met')
xmin = xmin - (xmax-xmin)*0.1
xmax = xmax + (xmax-xmin)*0.1
doyticks = pick_doy_ticks(xmin,xmax-43200,num=nticks)

tnames=tag_names(data)
get_lun, sunit ; file unit for stat ouput
if (NOT keyword_set(keys)) then begin
  ; we'll only do averages for now
  keys=tnames(where(strpos(tnames,'_AVG') ge 0)) 
  openw, sunit, htmlout
endif else begin
  ;openw, sunit, strcompress(infile+".stat1", /remove_all)
  openw, sunit, htmlout
endelse

; setup html file
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
printf, sunit, strtrim(cxtime(min(data.time),'sec','cal'),2)
printf, sunit, 'DOM '
printf, sunit, strtrim(string(fix(cxtime(min(data.time),'sec','met'))),2)
printf, sunit, '</td>'
printf, sunit, '<td align=right>Data end: '
printf, sunit, strtrim(cxtime(max(data.time),'sec','cal'),2)
printf, sunit, 'DOM '
printf, sunit, strtrim(string(fix(cxtime(max(data.time),'sec','met'))),2)
printf, sunit, '</td>'
printf, sunit, '</tr>'
printf, sunit, '</table>'

printf, sunit, '<br><hr><br>'
printf, sunit, '<center>'
printf, sunit, '<table border=1 cellpadding=3>'
printf, sunit, '<tr align=center><td>MSID<td> MEAN<td> RMS'+ $
               '<td> DELTA/YR<td> DELTA/YR/YR'+ $
               '<td> UNITS<td>DESCRIPTION</tr>'

rmark = 0 ; counter for red violation
ymark = 0 ; counter for yellow violation
for i = 0, n_elements(keys)-1 do begin

  ; rework name for labelling
  if (strpos(keys(i),"X") eq 0) then s=1 else s=0
  if (rstrpos(keys(i),"_AVG") gt s) then len = rstrpos(keys(i),"_AVG")-s
  msid = strmid(keys(i), s, len)

  print, "Working ", keys(i)
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
  dfit = linfit(xtime,xdata)
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
  symbol=3
  if (n_elements(xdata) lt 200) then symbol=1
  plot, xtime, xdata, psym=symbol, ystyle=1, $
        title=des, xtitle='UT (DOY)', ytitle=msid+" ("+units+")", $
        xrange=[xmin,xmax], yrange=[ymin,ymax], $
        charsize = 1.0, charthick =1, color = white, background = bgrd, $
        xticks=nticks-1, xtickv = doyticks, xminor=10, $
        xtickformat='s2doy_axis_labels'
  line = xtime*dfit(1)+dfit(0)
  if (lim(0) ne -1) then begin
    y = where(xdata ge lim(1) or xdata le lim(0), ynum)
    r = where(xdata ge lim(3) or xdata le lim(2), rnum)
    if (ynum gt 0) then oplot, xtime(y), xdata(y), psym=symbol, color=yellow
    if (rnum gt 0) then oplot, xtime(r), xdata(r), psym=symbol, color=red
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
    dv = dsmooth(xtime, xdata, fit=df, w=wsmooth)
  endif else begin
    dv = dsmooth(xtime, xdata, fit=df)
  endelse

  ; get rid of too-tiny garbage
  mac = machar()
  zero = where(abs(dv) lt mac.epsneg, num)
  if (num gt 0) then dv(zero) = 0.0

  oplot, xtime, df, color=blue
  ddfit = linfit(xtime, dv)
  r = max(dv*speryr)-min(dv*speryr)
  if (r gt 0) then begin
    ymin = min(dv*speryr)-0.10*r
    ymax = max(dv*speryr)+0.10*r
  endif else begin
    ymin = min(dv*speryr)-0.10
    ymax = max(dv*speryr)+0.10
  endelse
  plot, xtime, dv*speryr, ystyle=1, $
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
  write_gif, strcompress(outdir+"/"+ $
                         strlowcase(keys(i))+'.gif', /remove_all), tvrd()
 
; make html outfile
  if (units eq "") then units = "&#160"
  mean_color = hwhite
  rms_color = hwhite
  d_color = hwhite
  dd_color = hwhite
  rms = sqrt(m(1))
  ; flag if derivatives project busted limited within tlim seconds
  ; (in terms of fraction of plotted range)
  tlim = 0.2*(max(xtime)-min(xtime))
  if (lim(0) ne -1) then begin  ; color code based on limits
    if (m(0) le lim(0) or m(0) ge lim(1)) then mean_color=hyellow
    if (m(0) le lim(2) or m(0) ge lim(3)) then mean_color=hred
    if (m(0)-rms le lim(0) or m(0)+rms ge lim(1)) then rms_color=hyellow
    if (m(0)-rms le lim(2) or m(0)+rms ge lim(3)) then rms_color=hred
    last = max(xtime)+tlim
    test = dfit(1)*last+dfit(0)
    if (test ge lim(1) or test le lim(0)) then d_color = hyellow
    if (test ge lim(3) or test le lim(2)) then d_color = hred
    ; second deriv test does not quite work yet
    ; dtest = ddfit(1)*last+ddfit(0)
    ; test = dtest*last+dfit(0)
    ; ;test = ddfit(1)/2*last*last+ddfit(0)*last+dfit(0)
    ; if (test ge lim(1) or test le lim(0)) then dd_color = hyellow
    ; if (test ge lim(3) or test le lim(2)) then dd_color = hred
  endif else begin
    last = max(xtime)+tlim
    test = abs(dfit(1)*last+dfit(0) - m(0))/m(0)
    if (test ge 0.10) then d_color = hyellow
    if (test ge 0.20) then d_color = hred
  endelse; if (lim(0) ne -1) then begin  ; color code based on limits

  printf, sunit, '<tr><td><a href="javascript:WindowOpener('+ $
                 "'"+strlowcase(keys(i))+".gif')"+'">'+ $
                  msid+'</a></td>'
  printf, sunit, '<td><font color="'+mean_color+'">'+ $
                  string(format='(e10.3)',m(0))+'</font></td>'
  printf, sunit, '<td><font color="'+rms_color+'">'+ $
                  string(format='(e10.3)',sqrt(m(1)))+'</font></td>'
  printf, sunit, '<td><font color="'+d_color+'">'+ $
                  string(format='(e10.3)',dfit(1)*speryr)+'</font></td>'
  printf, sunit, '<td><font color="'+dd_color+'">'+ $
                  string(format='(e10.3)',ddfit(1)*speryr*speryr)+'</font></td>'
  printf, sunit, '<td>'+units+'</td>'
  printf, sunit, '<td>'+des+'</td></tr>'

  ; check to see if we should indicate violations on index page
  if (mean_color eq hyellow or rms_color eq hyellow or $
      d_color eq hyellow or dd_color eq hyellow) then $
    ymark = ymark+1
  if (mean_color eq hred or rms_color eq hred or $
      d_color eq hred or dd_color eq hred) then $
    rmark = rmark+1
endfor ;for j = 1, n_elements(keys)-1 do begin

; close html file
printf, sunit, '</table>'
printf, sunit, '</center>'
printf, sunit, '</body></html>'
close, sunit

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
    printf, ounit, array(i)
    if (strpos(array(i), rootname+".html") ge 0) then begin
      if (ymark gt 0 and rmark le 0) then $
        printf, ounit, '<font color="'+hyellow+'"> ****</font>'
      if (rmark gt 0) then $
        printf, ounit, '<font color="'+hred+'"> ****</font>'
      if (strpos(array(i+1), "**" ) ge 0) then i = i+1
    endif ; if (strpos(array(i), htmlout) ge 0) then begin
  endif ; copy old file
endfor

free_lun, ounit  

end
