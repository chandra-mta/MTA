PRO HIST_TEPHIN,eph
;PRO HIST_TEPHIN
; IDL Version 5.3 (sunos sparc)
; Journal File for mta@colossus
; Working directory: /data/mta/Script/Deriv
; Date: Tue Jan 21 14:45:07 2003
 
zero=266.6
int=2.8
top=315

up_yel=300.2
up_red=303.0
window, 0, xsize=512, ysize=750
!p.multi=[0,1,4,0,0]
loadct,39
grn_color=150
yel_color=190
red_color=250

eph=mrdfits('ephtv.fits',1)

yr_str=['1999-01-01T00:00:00', $
        '2000-01-01T00:00:00', $
        '2001-01-01T00:00:00', $
        '2002-01-01T00:00:00', $
        '2003-01-01T00:00:00']
title=[' 1999',' 2000',' 2001',' 2002']

for iplot=0,n_elements(title)-1 do begin
  y=where(eph.time lt cxtime(yr_str(iplot+1),'cal','sec') and $
          eph.time ge cxtime(yr_str(iplot),'cal','sec'))
  hist=time_hist(eph(y).time,eph(y).tephin_avg, $
                 binsize=int,min=zero,max_int=2000)
  yel_bin=up_red-up_yel
  yel=time_hist(eph(y).time,eph(y).tephin_avg, $
                binsize=yel_bin,min=up_yel,max_int=2000)
  maxv=max(eph(y).tephin_avg)
  red_bin=maxv-up_red
  red=time_hist(eph(y).time,eph(y).tephin_avg, $
                binsize=red_bin,min=up_red,max_int=2000)
  tot=total(hist)
  tot_days=tot/86400.0
  hist=hist/tot*100.0
  yel=yel/tot*100.0
  red=red/tot*100.0

  xarr=float(indgen(n_elements(hist)+2))*int+int/2+zero-int
  ytop=max(hist)*1.1
  xtop=xarr(n_elements(xarr)-2)+int/2 ; right edge of bins
  plot,xarr, $
    [0,hist,0],psym=10,xrange=[zero,top],xstyle=1,ystyle=1, $
    yrange=[0,ytop],ytitle="% time",$
    xtitle="TEPHIN (K)", $
    charsize=2.0, xticklen=-0.015, $
    title=strcompress(title[iplot]+" "+string(fix(tot_days))+" days")
  polyfill,[up_yel,up_yel,up_red,up_red],[0,yel(0),yel(0),0], $
         color=yel_color
  polyfill,[up_red,up_red,xtop,xtop],[0,red(0),red(0),0], $
         color=red_color
  for i=1,n_elements(xarr)-2 do polyfill, $
    [xarr(i)-int/2,xarr(i)-int/2,xarr(i)+int/2,xarr(i)+int/2], $
    [0,hist(i-1),hist(i-1),0], color=grn_color, $
    /line_fill,orientation=45
  for i=1,n_elements(xarr)-2 do $
    oplot, [xarr(i)-int,xarr(i),xarr(i)+int],[0,hist(i-1),0],$
    psym=10
endfor ; for iplot=0,n_elements(title) do begin
write_gif,'hist_tephin_year.gif',tvrd()

window, 0, xsize=512, ysize=400
!p.multi=[0,1,1,0,0]
hist=time_hist(eph.time,eph.tephin_avg, $
               binsize=int,min=zero,max_int=2000)
yel_bin=up_red-up_yel
yel=time_hist(eph.time,eph.tephin_avg, $
              binsize=yel_bin,min=up_yel,max_int=2000)
maxv=max(eph.tephin_avg)
red_bin=maxv-up_red
red=time_hist(eph.time,eph.tephin_avg, $
                binsize=red_bin,min=up_red,max_int=2000)
tot=total(hist)
tot_days=tot/86400.0
hist=hist/tot*100.0
yel=yel/tot*100.0
red=red/tot*100.0

xarr=float(indgen(n_elements(hist)+2))*int+int/2+zero-int
ytop=max(hist)*1.1
xtop=xarr(n_elements(xarr)-2)+int/2 ; right edge of bins
plot,xarr, $
  [0,hist,0],psym=10,xrange=[zero,top],xstyle=1,ystyle=1, $
  yrange=[0,ytop],ytitle="% time",$
  xtitle="TEPHIN (K)", $
  charsize=2.0, xticklen=-0.015, $
  title=strcompress(" 1999-2002 "+string(fix(tot_days))+" days")
polyfill,[up_yel,up_yel,up_red,up_red],[0,yel(0),yel(0),0], $
         color=yel_color
polyfill,[up_red,up_red,xtop,xtop],[0,red(0),red(0),0], $
         color=red_color
for i=1,n_elements(xarr)-2 do polyfill, $
  [xarr(i)-int/2,xarr(i)-int/2,xarr(i)+int/2,xarr(i)+int/2], $
  [0,hist(i-1),hist(i-1),0], color=grn_color, $
  /line_fill,orientation=45
for i=1,n_elements(xarr)-2 do $
  oplot, [xarr(i)-int,xarr(i),xarr(i)+int],[0,hist(i-1),0],$
  psym=10
write_gif,'hist_tephin.gif',tvrd()

end
