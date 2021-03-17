PRO HIST_TEPHIN,eph
;PRO HIST_TEPHIN
; IDL Version 5.3 (sunos sparc)
; Journal File for mta@colossus
; Working directory: /data/mta/Script/Deriv
; Date: Tue Jan 21 14:45:07 2003
 
zero=266.6
int=5
top=335

up_yel=322.15
up_red=332.15
set_plot,'Z'
device, set_resolution=[512,420]
!p.multi=[0,1,1,0,0]
eph=mrdfits('ephtv.fits',1)
eph=eph(sort(eph.time))
loadct,39
grn_color=150
yel_color=190
red_color=250

;eph=mrdfits('ephtv.fits',1)

yr_str=['1999-01-01T00:00:00', $
        '2000-01-01T00:00:00', $
        '2001-01-01T00:00:00', $
        '2002-01-01T00:00:00', $
        '2003-01-01T00:00:00', $
        '2004-01-01T00:00:00', $
        '2005-01-01T00:00:00', $
        '2006-01-01T00:00:00', $
        '2007-01-01T00:00:00', $
        '2008-01-01T00:00:00', $
        '2009-01-01T00:00:00', $
        '2010-01-01T00:00:00', $
        '2011-01-01T00:00:00', $
        '1999-01-01T00:00:00']
yr_end=['2000-01-01T00:00:00', $
        '2001-01-01T00:00:00', $
        '2002-01-01T00:00:00', $
        '2003-01-01T00:00:00', $
        '2004-01-01T00:00:00', $
        '2005-01-01T00:00:00', $
        '2006-01-01T00:00:00', $
        '2007-01-01T00:00:00', $
        '2008-01-01T00:00:00', $
        '2009-01-01T00:00:00', $
        '2010-01-01T00:00:00', $
        '2011-01-01T00:00:00', $
        '2012-01-01T00:00:00', $
        '2050-01-01T00:00:00']
title=[' 1999',' 2000',' 2001',' 2002',' 2003',' 2004',' 2005',' 2006',' 2007',' 2008',' 2009',' 2010',' 2011',' 1999-2012']

for iplot=0,n_elements(title)-1 do begin
  if (iplot eq n_elements(title)-1) then begin
    device, set_resolution=[512,400] ; resize for total plot
    !p.multi=[0,1,1,0,0]
  endif ; if (iplot eq n_elements(title)-1) then begin
  y=where(eph.time lt cxtime(yr_end(iplot),'cal','sec') and $
          eph.time ge cxtime(yr_str(iplot),'cal','sec'))
  hist=time_hist(eph(y).time,eph(y).tephin_avg, $
                 binsize=int,min=zero,max_int=15000)
  ;yel_bin=up_red-up_yel
  yel_bin=int
  yel=time_hist(eph(y).time,eph(y).tephin_avg, $
                binsize=yel_bin,min=up_yel,max_int=15000)
  maxv=max(eph(y).tephin_avg)
  ;red_bin=maxv-up_red
  red_bin=int
  red=time_hist(eph(y).time,eph(y).tephin_avg, $
                binsize=red_bin,min=up_red,max_int=15000)
  tot=total(hist)
  tot_days=tot/86400.0
  hist=hist/tot*100.0
  yel=yel/tot*100.0
  red=red/tot*100.0

  xarr=float(indgen(n_elements(hist)+2))*int+int/2+zero-int
  yarr=float(indgen(n_elements(yel)+2))*int+int/2+up_yel-int
  rarr=float(indgen(n_elements(red)+2))*int+int/2+up_red-int
  print, yarr, yel  ; debug
  print, rarr, red  ; debug
  ytop=max(hist)*1.1
  xtop=xarr(n_elements(xarr)-2)+int/2 ; right edge of bins
  plot,xarr, $
    [0,hist,0],psym=10,xrange=[zero,top],xstyle=1,ystyle=1, $
    yrange=[0,ytop],ytitle="% time", yticks=2, $
    xtitle="TEPHIN (K)", xticks=3, xtickv=[270,290,310,330], $
    charsize=2.0, xticklen=-0.015, max_value=up_yel, $
    title=strcompress(title[iplot]+" "+string(fix(tot_days))+" days")
  for i=1,n_elements(xarr)-2 do begin
    polyfill, $
     [xarr(i)-int/2,xarr(i)-int/2,xarr(i)+int/2,xarr(i)+int/2], $
     [0,hist(i-1),hist(i-1),0], color=grn_color
     ;/line_fill,orientation=45
    oplot, [xarr(i)-int,xarr(i),xarr(i)+int],[0,hist(i-1),0],$
     psym=10
  endfor
  for i=1,n_elements(yarr)-2 do begin
    polyfill, $
     [yarr(i)-int/2,yarr(i)-int/2,yarr(i)+int/2,yarr(i)+int/2], $
     [0,yel(i-1),yel(i-1),0], color=yel_color
     ;/line_fill,orientation=45
    oplot, [yarr(i)-int,yarr(i),yarr(i)+int],[0,yel(i-1),0],$
     psym=10
  endfor
  for i=1,n_elements(rarr)-2 do begin
    polyfill, $
     [rarr(i)-int/2,rarr(i)-int/2,rarr(i)+int/2,rarr(i)+int/2], $
     [0,red(i-1),red(i-1),0], color=red_color
     ;/line_fill,orientation=45
    oplot, [rarr(i)-int,rarr(i),rarr(i)+int],[0,red(i-1),0],$
     psym=10
  endfor
  if (iplot le n_elements(title)-2) then begin
    write_gif,'hist_tephin_'+strcompress(title(iplot),/remove_all)+'.gif',tvrd()
  endif ; if (iplot eq 4) then begin
endfor ; for iplot=0,n_elements(title) do begin

write_gif,'hist_tephin.gif',tvrd()

end
