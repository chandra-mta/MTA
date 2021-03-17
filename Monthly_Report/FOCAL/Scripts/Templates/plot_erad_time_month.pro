PRO PLOT_ERAD_TIME_MONTH
set_plot,'z'
device,set_resolution=[1040,520]
!p.multi=[0,1,1,0,0]
fp_temp=mrdfits('dataseek_deahk_temp.0.fits',1)
alt=mrdfits('dataseek_avg.fits',1)

rdfloat,'/data/mta/DataSeeker/data/repository/earth_rad_ang.rdb',etime,tot_ang,p_ang,r_ang,skipline=2

fp_temp=fp_temp(where(fp_temp.deahk16_avg gt -125 and fp_temp.deahk16_avg lt 0))

xmin=#START#.

xmax=xmin+86400.*32.2
ymin=floor(min(fp_temp.deahk16_avg))-1.
ymax=ceil(max(fp_temp.deahk16_avg))

loadct,39

bcolor=0
lcolor=255
print,"XMIN ",xmin
plot,fp_temp.time,fp_temp.deahk16_avg,psym=2,symsize=0.6,backgr=bcolor,color=lcolor, $
   ytitle="Focal Plane Temp (degC)", $
   xtitle=" 2016",yrange=[ymin,ymax],xrange=[xmin,xmax], $
   xstyle=1,ystyle=1,ymargin=[6,4],xmargin=[10,6], $
   title="Focal Plane Temp and Sun Angle", $
   xtickv=[#SDATELIST#], $
   xticks=3, $
   xtickn=[#LDATELIST#],xminor=10

xyouts,0.985,0.75,"Angle (degrees)",align=0.5,orient=90,color=lcolor,/norm
xyouts,xmax+5000,ymin,'0',color=lcolor,align=0,/data
xyouts,xmax+5000,ymin+45.*(ymax-ymin)/180.,'45',color=lcolor,align=0,/data
xyouts,xmax+5000,ymin+90.*(ymax-ymin)/180.,'90',color=lcolor,align=0,/data
xyouts,xmax+5000,ymin+135.*(ymax-ymin)/180.,'135',color=lcolor,align=0,/data
xyouts,xmax+5000,ymax,'180',color=lcolor,align=0,/data

alt_range=max(alt.sc_altitude)-min(alt.sc_altitude)
alt_sc=(alt.sc_altitude-min(alt.sc_altitude))*(ymax-ymin)/alt_range+ymin
oplot,alt.time,alt_sc,color=200,linestyle=0,thick=2

sang_sc=(alt.pt_suncent_ang)*(ymax-ymin)/180+ymin
oplot,alt.time,sang_sc,color=240,linestyle=0,thick=2

xyouts,0.15,0.51,"FP_temp",color=lcolor,/norm
xyouts,0.30,0.51,"Sun angle",color=240,/norm
xyouts,0.75,0.51,"Altitude",color=200,/norm

write_gif,'#GIFNAME#',tvrd()




; find temp peaks
for i=0,n_elements(fp_temp)-1 do begin
  peak=0 ; no peak yet
  if (fp_temp(i).deahk16_avg gt -119.2) then begin
    tstart=fp_temp(i).time
    max_temp=fp_temp(i).deahk16_avg
    max_time=fp_temp(i).time
    while (fp_temp(i).deahk16_avg gt -119.5 and $
           i lt n_elements(fp_temp)-2) do begin
      i=i+1
      if (fp_temp(i).deahk16_avg gt max_temp) then begin
        max_temp=fp_temp(i).deahk16_avg
        max_time=fp_temp(i).time
      endif
    endwhile
    tstop=fp_temp(i).time
    print, cxtime(max_time,'sec','doy'),max_temp,(tstop-tstart)/86400.
  endif ; if (fp_temp(i).deahk16_avg gt -119.2) then begin
endfor ; for i=0,n_elements(fp_temp)-1 do begin

end
