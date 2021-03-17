; IDL Version 5.3 (sunos sparc)
; Journal File for mta@colossus
; Working directory: /data/mta/Script/Deriv
; Date: Wed Nov 13 16:15:40 2002
 
x=mrdfits('acistemp_att.fits',1)
;MRDFITS: Binary table.  17 columns by  286853 rows.
a=n_elements(x)
;;b=congrid(indgen(a,/long),5000)
;;x=x(b)
print, tag_names(x)
;TIME X1CBAT_AVG X1CBBT_AVG X1CRAT_AVG X1CRBT_AVG X1DACTBT_AVG X1DEAMZT_AVG
; X1DPAMYT_AVG X1DPAMZT_AVG X1OAHAT_AVG X1OAHBT_AVG X1PDEAAT_AVG X1PDEABT_AVG
; X1PIN1AT_AVG X1WRAT_AVG X1WRBT_AVG PT_SUNCENT_ANG
loadct,39
!P.MULTI=[0,2,1,0,0]
xticks=5
xmin=min(x.time)
xmax=max(x.time)
doyticks = pick_doy_ticks(xmin,xmax-43200,num=nticks)
t=x.X1PIN1AT_AVG
i=fix((t-min(t))*256/(max(t)-min(t)))
trange=indgen(256)*(max(t)-min(t))/256+min(t)
plot,x.time,x.pt_suncent_ang,psym=1,ystyle=1,xmargin=[8,-40], $
  xtitle="TIME (DOY)", ytitle="Sun Cent Angle (deg)", $
  xticks=nticks-1, xtickv = doyticks, xminor=10, $
  xtickformat='s2doy_axis_labels'
plots,x.time,x.pt_suncent_ang,color=i,psym=1
ycon = convert_coord([0],[0], /device, /to_data)
label_year, xmin, xmax, ycon(1), csize=1.2
plot,0*indgen(256),trange,thick=10,xmargin=[45,6], $
xrange=[-1,1],xstyle=5,ystyle=9,xticks=1
; % Program caused arithmetic error: Floating illegal operand
plots,0*indgen(256),trange,color=indgen(256),thick=10
; % Program caused arithmetic error: Floating illegal operand
xyouts, 0.97,0.5,'1PINIAT',color=256,align=0.5,orient=90,charsize=2, /norm
write_gif, 'x1piniat_clratt.gif', tvrd()

t=x.X1DPAMZT_AVG
i=fix((t-min(t))*256/(max(t)-min(t)))
trange=indgen(256)*(max(t)-min(t))/256+min(t)
plot,x.time,x.pt_suncent_ang,psym=1,ystyle=1,xmargin=[8,-40], $
  xtitle="TIME (DOY)", ytitle="Sun Cent Angle (deg)", $
  xticks=nticks-1, xtickv = doyticks, xminor=10, $
  xtickformat='s2doy_axis_labels'
plots,x.time,x.pt_suncent_ang,color=i,psym=1
ycon = convert_coord([0],[0], /device, /to_data)
label_year, xmin, xmax, ycon(1), csize=1.2
plot,0*indgen(256),trange,thick=10,xmargin=[45,6], $
xrange=[-1,1],xstyle=5,ystyle=9,xticks=1
; % Program caused arithmetic error: Floating illegal operand
plots,0*indgen(256),trange,color=indgen(256),thick=10
; % Program caused arithmetic error: Floating illegal operand
xyouts, 0.97,0.5,'1DPAMZT',color=256,align=0.5,orient=90,charsize=2, /norm
write_gif, 'x1dpamzt_clratt.gif', tvrd()
