iru=mrdfits('pcaditv.fits',1)
mintime=170208063
iru=iru(where(iru.time gt mintime))
!p.multi=[0,1,5,0,0]
window,0,xsize=580, ysize=720
loadct,39
yellow=190
green=150
blue=100
xmin=min(iru.time)-20000
xmax=max(iru.time)+20000
plot,iru.time,iru.AGWS2V_avg,psym=3,xrange=[xmin,xmax], $
  title="GYRO WHEEL SUPPLY 2 INPUT VOLTAGE",ytitle="AGWS2V (V)", $
  ystyle=1,xstyle=1,xtickformat='s2doy_axis_labels',charsize=1.8, $
  yrange=[-0.2,2.8],/nodata,ymargin=[2,2]
oplot,iru.time,iru.AGWS2V_avg,psym=3,color=blue
plot,iru.time,iru.AIRU2G1T_avg,psym=3,xrange=[xmin,xmax], $
  title="IRU-2 GYRO #1 TEMP",ytitle="AIRU2G1T (K)", $
  ystyle=1,xstyle=1,xtickformat='s2doy_axis_labels',charsize=1.8, $
  yrange=[288,348],/nodata,ymargin=[2,2]
oplot,iru.time,iru.AIRU2G1T_avg,psym=3,color=blue
oba3=mrdfits('obaheaters3.fits',1)
oba3=oba3(where(oba3.time gt mintime))
plot,oba3.time,oba3.OOBTHR47_avg,psym=3,xrange=[xmin,xmax], $
  title="RT 69: TFTE COVER",ytitle="OOBTHR47 (K)", $
  ystyle=1,xstyle=1,/nodata,xtickformat='s2doy_axis_labels',charsize=1.8, $
  yrange=[256,271],ymargin=[2,2]
b=where(oba3.OOBTHR47_avg ge 261.9)
oplot,oba3(b).time,oba3(b).OOBTHR47_avg,psym=3,color=yellow
b=where(oba3.OOBTHR47_avg lt 261.9)
oplot,oba3(b).time,oba3(b).OOBTHR47_avg,psym=3,color=green
hstr=mrdfits('hrmastruts.fits',1)
hstr=hstr(where(hstr.time gt mintime))
plot,hstr.time,hstr.x4RT596T_avg,psym=3,xrange=[xmin,xmax], $
  title="RT 596 - TFTE TEMP",ytitle="_4RT596T (K)", $
  ystyle=1,xstyle=1,/nodata,xtickformat='s2doy_axis_labels',charsize=1.8, $
  yrange=[280,292],ymargin=[2,2]
b=where(hstr.x4RT596T_avg ge 283.0)
oplot,hstr(b).time,hstr(b).x4RT596T_avg,psym=3,color=yellow
b=where(hstr.x4RT596T_avg lt 283.0)
oplot,hstr(b).time,hstr(b).x4RT596T_avg,psym=3,color=green
obf=mrdfits('obfwdbulkhead.fits',1)
obf=obf(where(obf.time gt mintime))
plot,obf.time,obf.x4RT711T_avg,psym=3,xrange=[xmin,xmax], $
  title="RT 711 - OB BULKHEAD TEMP",ytitle="_4RT711T (K)", $
  ystyle=1,xstyle=1,/nodata, xtitle="Time (DOY [UT])", $
  xtickformat='s2doy_axis_labels',charsize=1.8, $
  yrange=[284,286.5],ymargin=[3,1.5]
b=where(obf.x4RT711T_avg ge 285.8)
oplot,obf(b).time,obf(b).x4RT711T_avg,psym=3,color=yellow
b=where(obf.x4RT711T_avg lt 285.8)
oplot,obf(b).time,obf(b).x4RT711T_avg,psym=3,color=green
write_gif,'0626_iru_hrma.gif',tvrd()
