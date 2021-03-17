FUNCTION EPH_READ,froot
; special read ephin level 1 data from rdb files

; can read only 19 columns using rdfloat
;  so we split things up very confusingly

if (froot eq 'ephin_L1') then begin
  rdfloat,'/data/mta/DataSeeker/data/repository/ephin_L1.rdb', $
    time, SCE1300,SCP4GM,SCP41GM,SCINT ,skipline=2,$
    columns=[1,2,3,4]
  e1 = {eph1, time:time(0),SCE1300L1_AVG:0.0,SCP4GML1_AVG:0.0, $
    SCP41GML1_AVG:0.0,SCINTL1_AVG:0.0}
  b=where(time gt 0, bnum)
  data1 = replicate({eph1}, bnum)
  data1.time=time(b)
  data1.SCE1300L1_AVG=SCE1300(b)
  data1.SCP4GML1_AVG=SCP4GM(b)
  data1.SCP41GML1_AVG=SCP41GM(b)
  data1.SCINTL1_AVG=SCINT(b)
  mwrfits,data1,'eph_L1.fits',/create
  return, data1
endif ; if (froot eq 'ephin_L1') then begin
end
