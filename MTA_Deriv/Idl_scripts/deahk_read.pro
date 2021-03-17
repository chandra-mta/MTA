FUNCTION DEAHK_READ, froot
; special read dea housekeeping data from rdb files

; can read only 19 columns using rdfloat
;  so we split things up very confusingly

if (froot eq 'deahk_temp') then begin
  rdfloat,'/data/mta/DataSeeker/data/repository/deahk_temp.rdb', $
    time, DEAHK1,DEAHK2,DEAHK3,DEAHK4,DEAHK5,DEAHK6,DEAHK7,DEAHK8, $
    DEAHK9,DEAHK10,DEAHK11,DEAHK12,DEAHK13,DEAHK15,DEAHK16,skipline=2,$
    columns=[1,3,5,7,9,11,13,15,17,19,21,23,25,27,29,31]
  d1 = {dea1, time:time(0),DEAHK1_avg:0.0,DEAHK2_avg:0.0,DEAHK3_avg:0.0, $
     DEAHK4_avg:0.0,DEAHK5_avg:0.0,DEAHK6_avg:0.0,DEAHK7_avg:0.0, $
     DEAHK8_avg:0.0,DEAHK9_avg:0.0,DEAHK10_avg:0.0,DEAHK11_avg:0.0, $
     DEAHK12_avg:0.0,DEAHK13_avg:0.0,DEAHK15_avg:0.0,DEAHK16_avg:0.0}
  b=where(time gt 100000,bnum)
  data1 = replicate({dea1}, bnum)
  data1.time=time(b)
  data1.DEAHK1_avg=DEAHK1(b)
  data1.DEAHK2_avg=DEAHK2(b)
  data1.DEAHK3_avg=DEAHK3(b)
  data1.DEAHK4_avg=DEAHK4(b)
  data1.DEAHK5_avg=DEAHK5(b)
  data1.DEAHK6_avg=DEAHK6(b)
  data1.DEAHK7_avg=DEAHK7(b)
  data1.DEAHK8_avg=DEAHK8(b)
  data1.DEAHK9_avg=DEAHK9(b)
  data1.DEAHK10_avg=DEAHK10(b)
  data1.DEAHK11_avg=DEAHK11(b)
  data1.DEAHK12_avg=DEAHK12(b)
  data1.DEAHK13_avg=DEAHK13(b)
  c=where(deahk15 lt -1000,cnum)
  if (cnum gt 0) then deahk15(c)='NaN'
  data1.DEAHK15_avg=DEAHK15(b)
  c=where(deahk16 lt -1000,cnum)
  if (cnum gt 0) then deahk16(c)='NaN'
  data1.DEAHK16_avg=DEAHK16(b)
  ;print,max(data1.time),n_elements(data1),data1(n_elements(data1)-1).time,bnum,cnum  ;debug
  mwrfits,data1(b),'deahk_temp.fits',/create
  return, data1(b)
endif ; if (froot eq 'deahk_temp') then begin
if (froot eq 'deahk_elec') then begin
  rdfloat,'/data/mta/DataSeeker/data/repository/deahk_elec.rdb', $
    time, DEAHK17,DEAHK18,DEAHK19,DEAHK20,DEAHK25,DEAHK26,DEAHK27, $
    DEAHK28,DEAHK29,DEAHK30 ,skipline=2,$
    columns=[1,3,5,7,9,11,13,15,17,19,21]
  rdfloat,'/data/mta/DataSeeker/data/repository/deahk_elec.rdb', $
   DEAHK31,DEAHK32,DEAHK33,DEAHK34,DEAHK35,DEAHK36,DEAHK37,DEAHK38, $
   DEAHK39,DEAHK40,skipline=2, $
   columns=[23,25,27,29,31,33,35,37,39,41]
  d2 = {dea2, time:time(0), DEAHK17_avg:0.0,DEAHK18_avg:0.0, $
     DEAHK19_avg:0.0,DEAHK20_avg:0.0,DEAHK25_avg:0.0,DEAHK26_avg:0.0, $
     DEAHK27_avg:0.0,DEAHK28_avg:0.0,DEAHK29_avg:0.0,DEAHK30_avg:0.0, $
     DEAHK31_avg:0.0,DEAHK32_avg:0.0,DEAHK33_avg:0.0,DEAHK34_avg:0.0, $
     DEAHK35_avg:0.0,DEAHK36_avg:0.0,DEAHK37_avg:0.0,DEAHK38_avg:0.0, $
     DEAHK39_avg:0.0,DEAHK40_avg:0.0}
  b=where(time gt 100000,bnum)
  data1 = replicate({dea2}, bnum)
  data1.time=time(b)
  data1.DEAHK17_avg=DEAHK17(b)
  data1.DEAHK18_avg=DEAHK18(b)
  data1.DEAHK19_avg=DEAHK19(b)
  data1.DEAHK20_avg=DEAHK20(b)
  data1.DEAHK25_avg=DEAHK25(b)
  data1.DEAHK26_avg=DEAHK26(b)
  data1.DEAHK27_avg=DEAHK27(b)
  data1.DEAHK28_avg=DEAHK28(b)
  data1.DEAHK29_avg=DEAHK29(b)
  data1.DEAHK30_avg=DEAHK30(b)
  data1.DEAHK31_avg=DEAHK31(b)
  data1.DEAHK32_avg=DEAHK32(b)
  data1.DEAHK33_avg=DEAHK33(b)
  data1.DEAHK34_avg=DEAHK34(b)
  data1.DEAHK35_avg=DEAHK35(b)
  data1.DEAHK36_avg=DEAHK36(b)
  data1.DEAHK37_avg=DEAHK37(b)
  data1.DEAHK38_avg=DEAHK38(b)
  data1.DEAHK39_avg=DEAHK39(b)
  data1.DEAHK40_avg=DEAHK40(b)
  mwrfits,data1(b),'deahk_elec.fits',/create
  return, data1(b)
endif ; if (froot eq 'deahk_elec') then begin
end
