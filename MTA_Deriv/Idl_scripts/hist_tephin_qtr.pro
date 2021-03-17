PRO HIST_TEPHIN_QTR,eph
;PRO HIST_TEPHIN
; IDL Version 5.3 (sunos sparc)
; Journal File for mta@colossus
; Working directory: /data/mta/Script/Deriv
; Date: Tue Jan 21 14:45:07 2003

; make quarterly plot page
 
zero=266.6
int=5
top=335

up_yel=322.15
up_red=332.15
set_plot,'Z'
;device, set_resolution=[850,420]
device, set_resolution=[1050,420]
!p.multi=[0,4,1,0,0]
eph=mrdfits('ephtv.fits',1)
eph=eph(sort(eph.time))
loadct,39
grn_color=150
yel_color=190
red_color=250

plot,[0,1],[0,1],/nodata,ystyle=5,xstyle=5
xyouts,0.1,0.85,"SPRING"
xyouts,0.3,0.75,"Feb 15 - May 15"
xyouts,0.1,0.35,"FALL"
xyouts,0.3,0.25,"Aug 15 - Nov 15"
plot,[0,1],[0,1],/nodata,ystyle=5,xstyle=5
xyouts,0.1,0.85,"SUMMER"
xyouts,0.3,0.75,"May 15 - Aug 15"
xyouts,0.1,0.35,"WINTER"
xyouts,0.3,0.25,"Nov 15 - Feb 15"

;eph=mrdfits('ephtv.fits',1)

yr_str=['1999-08-15T00:00:00', $
        '1999-11-15T00:00:00', $
        '2000-02-15T00:00:00', $
        '2000-05-15T00:00:00', $
        '2000-08-15T00:00:00', $
        '2000-11-15T00:00:00', $
        '2001-02-15T00:00:00', $
        '2001-05-15T00:00:00', $
        '2001-08-15T00:00:00', $
        '2001-11-15T00:00:00', $
        '2002-02-15T00:00:00', $
        '2002-05-15T00:00:00', $
        '2002-08-15T00:00:00', $
        '2002-11-15T00:00:00', $
        '2003-02-15T00:00:00', $
        '2003-05-15T00:00:00', $
        '2003-08-15T00:00:00', $
        '2003-11-15T00:00:00', $
        '2004-02-15T00:00:00', $
        '2004-05-15T00:00:00', $
        '2004-08-15T00:00:00', $
        '2004-11-15T00:00:00', $
        '2005-02-15T00:00:00', $
        '2005-05-15T00:00:00', $
        '2005-08-15T00:00:00', $
        '2005-11-15T00:00:00', $
        '2006-02-15T00:00:00', $
        '2006-05-15T00:00:00', $
        '2006-08-15T00:00:00', $
        '2006-11-15T00:00:00', $
        '2007-02-15T00:00:00', $
        '2007-05-15T00:00:00', $
        '2007-08-15T00:00:00', $
        '2007-11-15T00:00:00', $
        '2008-02-15T00:00:00', $
        '2008-05-15T00:00:00', $
        '2008-08-15T00:00:00', $
        '2008-11-15T00:00:00', $
        '2009-02-15T00:00:00', $
        '2009-05-15T00:00:00', $
        '2009-08-15T00:00:00', $
        '2009-11-15T00:00:00', $
        '2010-02-15T00:00:00', $
        '2010-05-15T00:00:00', $
        '2010-08-15T00:00:00', $
        '2010-11-15T00:00:00', $
        '2011-02-15T00:00:00', $
        '2011-05-15T00:00:00']
yr_end=['1999-11-15T00:00:00', $
        '2000-02-15T00:00:00', $
        '2000-05-15T00:00:00', $
        '2000-08-15T00:00:00', $
        '2000-11-15T00:00:00', $
        '2001-02-15T00:00:00', $
        '2001-05-15T00:00:00', $
        '2001-08-15T00:00:00', $
        '2001-11-15T00:00:00', $
        '2002-02-15T00:00:00', $
        '2002-05-15T00:00:00', $
        '2002-08-15T00:00:00', $
        '2002-11-15T00:00:00', $
        '2003-02-15T00:00:00', $
        '2003-05-15T00:00:00', $
        '2003-08-15T00:00:00', $
        '2003-11-15T00:00:00', $
        '2004-02-15T00:00:00', $
        '2004-05-15T00:00:00', $
        '2004-08-15T00:00:00', $
        '2004-11-15T00:00:00', $
        '2005-02-15T00:00:00', $
        '2005-05-15T00:00:00', $
        '2005-08-15T00:00:00', $
        '2005-11-15T00:00:00', $
        '2006-02-15T00:00:00', $
        '2006-05-15T00:00:00', $
        '2006-08-15T00:00:00', $
        '2006-11-15T00:00:00', $
        '2007-02-15T00:00:00', $
        '2007-05-15T00:00:00', $
        '2007-08-15T00:00:00', $
        '2007-11-15T00:00:00', $
        '2008-02-15T00:00:00', $
        '2008-05-15T00:00:00', $
        '2008-08-15T00:00:00', $
        '2008-11-15T00:00:00', $
        '2009-02-15T00:00:00', $
        '2009-05-15T00:00:00', $
        '2009-08-15T00:00:00', $
        '2009-11-15T00:00:00', $
        '2010-02-15T00:00:00', $
        '2010-05-15T00:00:00', $
        '2010-08-15T00:00:00', $
        '2010-11-15T00:00:00', $
        '2011-02-15T00:00:00', $
        '2011-05-15T00:00:00', $
        '2011-08-15T00:00:00']
yr_label=['1999','2000','2001','2002','2003','2004','2005','2006','2007','2008','2009','2010','2011']
title=[' 1999 fall',' 1999 winter', $
       ' 2000 spring',' 2000 summer',' 2000 fall',' 2000 winter', $
       ' 2001 spring',' 2001 summer',' 2001 fall',' 2001 winter', $
       ' 2002 spring',' 2002 summer',' 2002 fall',' 2002 winter', $
       ' 2003 spring',' 2003 summer',' 2003 fall',' 2003 winter', $
       ' 2004 spring',' 2004 summer',' 2004 fall',' 2004 winter', $
       ' 2005 spring',' 2005 summer',' 2005 fall',' 2005 winter', $
       ' 2006 spring',' 2006 summer',' 2006 fall',' 2006 winter', $
       ' 2007 spring',' 2007 summer',' 2007 fall',' 2007 winter', $
       ' 2008 spring',' 2008 summer',' 2008 fall',' 2008 winter', $
       ' 2009 spring',' 2009 summer',' 2009 fall',' 2009 winter', $
       ' 2010 spring',' 2010 summer',' 2010 fall',' 2010 winter', $
       ' 2011 spring',' 2011 summer']

yr_loop=0
for iplot=0,n_elements(title)-1 do begin
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
  ;ytop=44
  xtop=xarr(n_elements(xarr)-1)+int/2 ; right edge of bins
  print,xarr,hist
  plot,xarr, $
    [0,hist,0],psym=10,xrange=[zero,top],xstyle=1,ystyle=1, $
    yrange=[0,ytop],ytitle="% time",$
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
  print, "yarr ", yarr
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
  if (!p.multi(0) eq 0 or iplot eq n_elements(title)-1 ) then begin
    write_gif,'hist_tephin_qtr_'+ $
              strcompress(yr_label(yr_loop),/remove_all)+'.gif',tvrd()
    yr_loop=yr_loop+1
  endif
endfor ; for iplot=0,n_elements(title) do begin

end
