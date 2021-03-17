; IDL Version 5.3 (sunos sparc)
; Journal File for mta@colossus
; Working directory: /data/mta/Script/Deriv
; Date: Thu Oct 24 13:58:25 2002
 
s=mrdfits('acistemp_sa_x.fits',1)
;MRDFITS: Binary table.  22 columns by  84674 rows.
print, tag_names(s)
;TIME X1CBAT_AVG X1CBBT_AVG X1CRAT_AVG X1CRBT_AVG X1DACTBT_AVG X1DEAMZT_AVG
; X1DPAMYT_AVG X1DPAMZT_AVG X1MAHCAT_AVG X1MAHCBT_AVG X1MAHOAT_AVG X1MAHOBT_AVG
; X1OAHAT_AVG X1OAHBT_AVG X1PDEAAT_AVG X1PDEABT_AVG X1PIN1AT_AVG X1WRAT_AVG
; X1WRBT_AVG pt_suncent_ang AOSARES2
plot_3dbox,s.time,s.X1PIN1AT_AVG,s.pt_suncent_ang
; % Array has too many elements.
; % Program caused arithmetic error: Floating illegal operand
time=congrid(s.time,1000)
temp=congrid(s.X1PIN1AT_AVG,1000)
ang=congrid(s.pt_suncent_ang,1000)
plot_3dbox,time,temp,ang
; % Program caused arithmetic error: Floating illegal operand
loadct,39
plot_3dbox,time,temp,ang,psym=3
; % Program caused arithmetic error: Floating illegal operand
plot_3dbox,time,temp,ang,psym=3,charsize=2, $
xtitle="TIME",ytitle="1PIN1AT",ztitle="Sun Angle"
; % Syntax error.
xtitle="TIME",ytitle="x1PIN1AT",ztitle="Sun Angle"
; % Syntax error.
plot_3dbox,time,temp,ang,psym=3,charsize=2, $
xtitle="TIME",ytitle="x1PIN1AT",ztitle="Sun Angle"
; % Program caused arithmetic error: Floating illegal operand
?
plot_3dbox,time,temp,ang,psym=3,charsize=2, symsize=3, $
xtitle="TIME",ytitle="x1PIN1AT",ztitle="Sun Angle"
; % Program caused arithmetic error: Floating illegal operand
plot_3dbox,time,temp,ang,psym=3,charsize=2, symsize=6, $
xtitle="TIME",ytitle="x1PIN1AT",ztitle="Sun Angle"
; % Program caused arithmetic error: Floating illegal operand
b=where(temp ge 303.15)
; % Program caused arithmetic error: Floating illegal operand
print, n_elements(b)
;           3
plots,time(b),temp(b),ang(b),/t3d,psym=2,color=185
b=where(temp ge 300)
; % Program caused arithmetic error: Floating illegal operand
print, n_elements(b)
;          27
plots,time(b),temp(b),ang(b),/t3d,psym=2,color=185
plot_3dbox,time,temp,ang,psym=1,charsize=2, symsize=6, $
xtitle="TIME",ytitle="x1PIN1AT",ztitle="Sun Angle"
; % Program caused arithmetic error: Floating illegal operand
plot_3dbox,time,temp,ang,psym=1,charsize=2, symsize=1, $
xtitle="TIME",ytitle="x1PIN1AT",ztitle="Sun Angle"
; % Program caused arithmetic error: Floating illegal operand
plots,time(b),temp(b),ang(b),/t3d,psym=2,color=185
plot_3dbox,time,ang,temp,psym=1,charsize=2, symsize=1, $
xtitle="TIME",ztitle="x1PIN1AT",ytitle="Sun Angle"
; % Program caused arithmetic error: Floating illegal operand
plot_3dbox,time,ang,temp,psym=1,charsize=2, symsize=1, $
xtitle="TIME",ztitle="x1PIN1AT",ytitle="Sun Angle", $
ax=45
; % Program caused arithmetic error: Floating illegal operand
plot_3dbox,time,ang,temp,psym=1,charsize=2, symsize=1, $
xtitle="TIME",ztitle="x1PIN1AT",ytitle="Sun Angle", $
ax=70
; % Program caused arithmetic error: Floating illegal operand
plot_3dbox,time,ang,temp,psym=1,charsize=2, symsize=1, $
xtitle="TIME",ztitle="x1PIN1AT",ytitle="Sun Angle", $
ax=15
; % Program caused arithmetic error: Floating illegal operand
plot_3dbox,time,ang,temp,psym=1,charsize=2, symsize=1, $
xtitle="TIME",ztitle="x1PIN1AT",ytitle="Sun Angle", $
ax=25
; % Program caused arithmetic error: Floating illegal operand
plot_3dbox,time,ang,temp,psym=1,charsize=2, symsize=1, $
xtitle="TIME",ztitle="x1PIN1AT",ytitle="Sun Angle", $
ax=25,az=50
; % Program caused arithmetic error: Floating illegal operand
plot_3dbox,time,ang,temp,psym=1,charsize=2, symsize=1, $
xtitle="TIME",ztitle="x1PIN1AT",ytitle="Sun Angle", $
ax=25,az=90
; % Program caused arithmetic error: Floating illegal operand
plot_3dbox,time,ang,temp,psym=1,charsize=2, symsize=1, $
xtitle="TIME",ztitle="x1PIN1AT",ytitle="Sun Angle", $
ax=25,az=75
; % Program caused arithmetic error: Floating illegal operand
plot_3dbox,time,ang,temp,psym=1,charsize=2, symsize=1, $
xtitle="TIME",ztitle="x1PIN1AT",ytitle="Sun Angle", $
ax=35,az=50
; % Program caused arithmetic error: Floating illegal operand
plot_3dbox,time,ang,temp,psym=1,charsize=2, symsize=1, $
xtitle="TIME",ztitle="x1PIN1AT",ytitle="Sun Angle", $
ax=35,az=50,ystyle=1
; % Program caused arithmetic error: Floating illegal operand
plot_3dbox,time,ang,temp,psym=1,charsize=2, symsize=1, $
xtitle="TIME",ztitle="x1PIN1AT",ytitle="Sun Angle", $
ax=35,az=50,ystyle=1,yrange=[45,180]
; % Program caused arithmetic error: Floating illegal operand
plots,time(b),ang(b),temp(b),/t3d,psym=2,color=185
plots,time,ang,temp,/t3d,psym=2,color=100
; % Program caused arithmetic error: Floating illegal operand
plots,time(b),ang(b),temp(b),/t3d,psym=2,color=185
write_gif,'sa_1pin1at_3d_1.gif',tvrd()
plot,time,ang,psym=1,charsize=2, symsize=1, $
xtitle="TIME",ytitle="Sun Angle", $
ystyle=1,yrange=[45,180],title="x1PIN1AT gt 300K"
oplot,time(b),ang(b),psym=2,color=185
oplot,time,ang,psym=3,color=100
plot,time,ang,psym=1,charsize=3, symsize=1, $
xtitle="TIME",ytitle="Sun Angle", $
ystyle=1,yrange=[45,180],title="x1PIN1AT gt 300K"
oplot,time(b),ang(b),psym=2,color=185
oplot,time,ang,psym=3,color=100
plot,time,ang,psym=3,charsize=2, symsize=1, $
xtitle="TIME",ytitle="Sun Angle", $
ystyle=1,yrange=[45,180],title="x1PIN1AT gt 300K"
oplot,time(b),ang(b),psym=2,color=185
oplot,time,ang,psym=3,color=100
write_gif,'sa_1pin1at_2d_1.gif',tvrd()
plot,time,temp,psym=3,charsize=2, symsize=1, $
xtitle="TIME",ytitle="x1PIN1AT", $
ystyle=1,title="x1pin1at oplot sa_ang"
oplot,time(b),temp(b),psym=2,color=185
oplot,time,temp,psym=3,color=100
oplot,time,(ang-45)*(25.0/135.0)+275,psym=3,color=40
oplot,time,(ang-45)*(25.0/135.0)+275,color=40
plot,time,temp,psym=3,charsize=2, symsize=1, $
xtitle="TIME",ytitle="x1PIN1AT", xrange=[1.45e8,1.53e8],$
ystyle=1,title="x1pin1at oplot sa_ang zoomed"
plot,time,temp,psym=3,charsize=2, symsize=1, $
xtitle="TIME",ytitle="x1PIN1AT", xrange=[1.45e8,1.52e8],$
ystyle=1,title="x1pin1at oplot sa_ang zoomed"
oplot,time(b),temp(b),psym=2,color=185
oplot,time,temp,psym=3,color=100
oplot,time,(ang-45)*(25.0/135.0)+275,color=40
oplot,time,(ang-45)*(25.0/135.0)+275,color=220
 write_gif,'sa_1pin1at_2do_1.gif',tvrd()
