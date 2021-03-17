PRO DTREND, infile, SIG=sig, WSMOOTH=wsmooth, KEYS=keys, PLOTX=plotx
; make trending and derivative plots
; input:
;     infile - file returned by dataseeker
;     sig - filter out any data more than sig sigma from mean (default 3)
;     wsmooth - smoothing factor (number of days to smooth over)

; directory for web output
outdir="/data/mta/www/mta_deriv"

if (NOT keyword_set(sig)) then sig=3
if (NOT keyword_set(wsmooth)) then wsmooth = 0
; convert to seconds
wsmooth = wsmooth * 86400.0

nticks=6

; this is stupid right now, but limit number of points (dsmooth is slow)
n_lim=3000

; plotting stuff
!p.multi = [0,1,2,0,0]
loadct, 39
white = 255
bgrd = 0
red = 230
yellow = 190
blue = 100
green = 150
purple = 50
orange = 215
if (keyword_set(plotx)) then begin
  set_plot, 'X'
endif else begin
  set_plot, 'Z'
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
nstart=rstrpos(infile, "/")+1
nstop=rstrpos(infile,".")
if (nstop lt nstart) then nstop = nstart+20
rootname=strmid(infile,nstart,nstop-nstart)
get_lun, sunit ; file unit for stat ouput
if (NOT keyword_set(keys)) then begin
  ; we'll only do averages for now
  keys=tnames(where(strpos(tnames,'_AVG') ge 0)) 
  openw, sunit, strcompress(outdir+"/"+rootname+".html", /remove_all)
endif else begin
  ;openw, sunit, strcompress(infile+".stat1", /remove_all)
  openw, sunit, strcompress(outdir+"/"+rootname+"A.html", /remove_all)
endelse

; setup html file
printf, sunit, '<HTML>'
printf, sunit, '<HEAD>'
printf, sunit, '     <TITLE>'+strupcase(rootname)+'_AVG Trends</TITLE>'
printf, sunit, '</HEAD>'
printf, sunit, '<BODY TEXT="#DDDDDD" BGCOLOR="#000000"'+ $
               'LINK="#FF0000" VLINK="#FFFF22" ALINK="#7500FF">'
printf, sunit, '<h1><center>'+strupcase(rootname)+'   Trends</center></h1>'
printf, sunit, '<br><hr><br>'

printf, sunit, '<table width=100% border=0>'
printf, sunit, '<tr>'
printf, sunit, '<td align=left>Start date: '
printf, sunit, strtrim(cxtime(min(data.time),'sec','cal'),2)
printf, sunit, 'DOM '
printf, sunit, strtrim(string(fix(cxtime(min(data.time),'sec','met'))),2)
printf, sunit, '</td>'
printf, sunit, '<td align=right>End date: '
printf, sunit, strtrim(cxtime(max(data.time),'sec','cal'),2)
printf, sunit, 'DOM '
printf, sunit, strtrim(string(fix(cxtime(max(data.time),'sec','met'))),2)
printf, sunit, '</td>'
printf, sunit, '</tr>'
printf, sunit, '</table>'

printf, sunit, '<br><hr><br>'
printf, sunit, '<center>'
printf, sunit, '<table border=1 cellpadding=3>'
printf, sunit, '<tr>'
printf, sunit, '<tr><td>MSID<td> MEAN<td> RMS<td> DELTA (/year)'+ $
               '<td> DELTA_DERIV (/year/year)<td> UNITS<td>DESCRIPTION</tr>'

; keep a copy, but do this a better way
;  (some data is removed with NaN's, so go back to orginal data for each pass)
data_org = data

for i = 0, n_elements(keys)-1 do begin
  data = data_org
  print, "Working ", keys(i)
  k = where(tnames eq strupcase(keys(i)),n)
  j = k(0)
  x = where(strpos(string(data.(j)), 'NaN') eq -1)
  data = data(x) ; this is a hack, fix it later
  if (n ne 1) then print, keys(i)+" no good."
  m = moment(data.(j))
  ;print, "mean: ", m ;debug
  b = where(abs(data.(j) - m(0)) le sqrt(m(1))*sig,num)
  if (num lt 3) then b=indgen(n_elements(data))
  ;print, "B ", b ;debug
  n_el = n_elements(b)
  dfit = linfit(data(b).time,data(b).(j))
  plot, data(b).time, data(b).(j), psym=3, ystyle=1, $
        title=keys(i), xtitle='Time (DOY)', ytitle='Units', $
        xrange=[xmin,xmax], $
        charsize = 1.0, charthick =1, color = white, background = bgrd, $
        xticks=nticks-1, xtickv = doyticks, xminor=10, $
        xtickformat='s2doy_axis_labels'
  oplot, data.time, data.time*dfit(1)+dfit(0), color=green
  ycon = convert_coord([0],[0], /device, /to_data)
  label_year, xmin, xmax, ycon(1), csize=1.2

  if (n_el gt n_lim) then begin
    ; dsmooth does not handle many points quickly, so do some presmoothing
    scale=n_el/n_lim
    b = b(where(b*scale lt n_el))*scale
  endif
  if (wsmooth gt 0) then begin
    dv = dsmooth(data(b).time, data(b).(j), fit=df, w=wsmooth)
  endif else begin
    dv = dsmooth(data(b).time, data(b).(j), fit=df)
  endelse
  oplot, data(b).time, df, color=blue
  ddfit = linfit(data(b).time, dv*31536000)
  plot, data(b).time, dv*86400, ystyle=1, $
        title=strcompress("dy/dx "+keys(i)", $
              ;" delta units/day/day="+string(format='(e10.3)',ddfit(1))), $
        xtitle='Time (DOY)', ytitle='Units/Day', $
        xrange=[xmin,xmax], $
        charsize = 1.0, charthick =1, color = white, background = bgrd, $
        xticks=nticks-1, xtickv = doyticks, xminor=10, $
        xtickformat='s2doy_axis_labels'
  oplot, data(b).time, ddfit(1)*data(b).time+ddfit(0), color=green
  ycon = convert_coord([0],[0], /device, /to_data)
  label_year, xmin, xmax, ycon(1), csize=1.2
  write_gif, strcompress(outdir+"/"+ $
                         strlowcase(keys(i))+'.gif', /remove_all), tvrd()
  printf, sunit, '<tr><td><a href="'+strlowcase(keys(i))+'.gif">'+ $
                  keys(i)+'</a>'+ $
                  '<td>'+string(format='(e10.3)',m(0))+ $
                  '<td>'+string(format='(e10.3)',sqrt(m(1)))+ $
                  '<td>'+string(format='(e10.3)',dfit(1)*31536000)+ $
                  '<td>'+string(format='(e10.3)',ddfit(1))+ $
                  '<td>&#160'+ $
                  '<td>&#160'+ $
                  '</tr>'
endfor ;for j = 1, n_elements(keys)-1 do begin

; close html file
printf, sunit, '</table>'
printf, sunit, '</center>'
printf, sunit, '</body></html>'
close, sunit

end
