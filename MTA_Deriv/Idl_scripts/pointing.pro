; IDL Version 5.3 (sunos sparc)
; Journal File for mta@colossus
; Working directory: /data/mta/Script/Deriv
; Date: Thu Oct 31 16:11:42 2002
pro pointing 
x=mrdfits('test_att.fits',1)
n=n_elements(x)

for i=0,n-1,8 do begin

  plot_3dbox,[0,0],[0,0],[0,0], $
    xrange=[-1,1],yrange=[-1,1],zrange=[-1,1],charsize=2,$
    xtitle="X",ytitle="Y",ztitle="Z",psym=2,symsize=10
  plots,[0,0],[0,0],[0,0], psym=4,symsize=10,/t3d
  print,i
  ;TIME X1DEAMZT_AVG X1DPAMYT_AVG X1DPAMZT_AVG PT_SUNCENT_ANG SC_ALTITUDE
  ; SC_POINT_X SC_POINT_Y SC_POINT_Z AOSARES1
  plots,[0,x(i).sc_point_x],[0,x(i).sc_point_y],[0,x(i).sc_point_z], /t3d
  write_gif,strcompress('Test/att'+string(i)+'.gif',/remove_all),tvrd()
endfor
end
;convert -delay 10 att*gif movies.gif
