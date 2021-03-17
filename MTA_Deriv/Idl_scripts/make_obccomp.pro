PRO MAKE_OBCCOMP

; computed obc comps from obaheaters and hrmaheaters thermistors
; formerly known as compgradkodak
; formulas from /home/ascds/DS.ops/config/mta/data/mta_obc_comp_limits.list

; read indiv. files from dataseeker
oob1=mrdfits('obaheaters1.fits',1)
oob2=mrdfits('obaheaters2.fits',1)
oob3=mrdfits('obaheaters3.fits',1)
oob4=mrdfits('obaheaters4.fits',1)
ohr1=mrdfits('hrmaheaters1.fits',1)
ohr2=mrdfits('hrmaheaters2.fits',1)
ohr3=mrdfits('hrmaheaters3.fits',1)
ohr4=mrdfits('hrmaheaters4.fits',1)
obf=mrdfits('obfwdbulkhead.fits',1)
hrm=mrdfits('hrmatherm.fits',1)
a={oobtab1,time:0.0, $
       OBAAVG_avg:0.0, $
       OBACONEAVG_avg:0.0, $
       FWBLKHDT_avg:0.0, $
       AFTBLKHDT_avg:0.0, $
       OBAAXGRD_avg:0.0, $
       MZOBACONE_avg:0.0, $
       PZOBACONE_avg:0.0, $
       OBADIAGRAD_avg:0.0, $
       TFTE_MIN_avg:0.0, $
       TFTE_MAX_avg:0.0, $
       TFTERANGE_avg:0.0, $
       HSTRUT_MIN_avg:0.0, $
       HSTRUT_MAX_avg:0.0, $
       HRMASTRUTRNGE_avg:0.0, $
       SSTRUT_MIN_avg:0.0, $
       SSTRUT_MAX_avg:0.0, $
       SCSTRUTRNGE_avg:0.0 }

oobarr = replicate({oobtab1}, n_elements(oob1))

b={ohrtab1,time:0.0, $
       HRMAAVG_avg:0.0, $
       HRMACAV_avg:0.0, $
       HRMAXGRD_avg:0.0, $
       HRMARADGRD_avg:0.0, $
       OHRTHR_MIN_avg:0.0, $
       OHRTHR_MAX_avg:0.0, $
       HRMARANGE_avg:0.0 }
ohrarr = replicate({ohrtab1}, n_elements(ohr1))
oobarr.time=oob1.time
ohrarr.time=ohr1.time

HRMASUM1=(ohr1.OHRTHR02_avg+ohr1.OHRTHR03_avg+ohr1.OHRTHR04_avg+ohr1.OHRTHR05_avg+ohr1.OHRTHR06_avg+ohr1.OHRTHR07_avg+ohr1.OHRTHR08_avg+ohr1.OHRTHR09_avg+ohr1.OHRTHR10_avg+ohr1.OHRTHR11_avg)
;HRMASUM2=(ohr1.OHRTHR12_avg+ohr1.OHRTHR13_avg+ohr2.OHRTHR21_avg+ohr2.OHRTHR22_avg+ohr2.OHRTHR23_avg+ohr2.OHRTHR24_avg+ohr2.OHRTHR25_avg+ohr2.OHRTHR26_avg+ohr2.OHRTHR27+ohr2.OHRTHR28_avg)
HRMASUM2=(ohr1.OHRTHR12_avg+ohr1.OHRTHR13_avg+ohr2.OHRTHR21_avg+ohr2.OHRTHR22_avg+ohr2.OHRTHR23_avg+ohr2.OHRTHR24_avg+ohr2.OHRTHR25_avg+ohr2.OHRTHR26_avg+ohr2.OHRTHR28_avg)
;HRMASUM3=(ohr2.OHRTHR29_avg+ohr2.OHRTHR30_avg+ohr3.OHRTHR33_avg+ohr3.OHRTHR36_avg+ohr3.OHRTHR37_avg+ohr.OHRTHR42+ohr3.OHRTHR44_avg+ohr3.OHRTHR45_avg+ohr3.OHRTHR46_avg+ohr3.OHRTHR47_avg)
HRMASUM3=(ohr2.OHRTHR29_avg+ohr2.OHRTHR30_avg+ohr3.OHRTHR33_avg+ohr3.OHRTHR36_avg+ohr3.OHRTHR37_avg+ohr3.OHRTHR44_avg+ohr3.OHRTHR45_avg+ohr3.OHRTHR46_avg+ohr3.OHRTHR47_avg)
HRMASUM4=(ohr3.OHRTHR49_avg+ohr3.OHRTHR50_avg+ohr4.OHRTHR51_avg+ohr4.OHRTHR52_avg+ohr4.OHRTHR53_avg+ohr4.OHRTHR55_avg+ohr4.OHRTHR56_avg)
;ohrarr.HRMAAVG_avg=(HRMASUM1+HRMASUM2+HRMASUM3+HRMASUM4)/37.0
ohrarr.HRMAAVG_avg=(HRMASUM1+HRMASUM2+HRMASUM3+HRMASUM4)/35.0

HRMACS1=(ohr1.OHRTHR06_avg+ohr1.OHRTHR07_avg+ohr1.OHRTHR08_avg+ohr1.OHRTHR09_avg+ohr1.OHRTHR10_avg+ohr1.OHRTHR11_avg+ohr1.OHRTHR12_avg+ohr1.OHRTHR13_avg+ohr1.OHRTHR14_avg)
HRMACS2=(ohr2.OHRTHR15_avg+ohr2.OHRTHR17_avg+ohr2.OHRTHR25_avg+ohr2.OHRTHR26_avg+ohr2.OHRTHR29_avg+ohr2.OHRTHR30_avg+ohr2.OHRTHR31_avg+ohr3.OHRTHR33_avg+ohr3.OHRTHR34_avg)
HRMACS3=(ohr3.OHRTHR35_avg+ohr3.OHRTHR36_avg+ohr3.OHRTHR37_avg+ohr3.OHRTHR39_avg+ohr3.OHRTHR40_avg+ohr3.OHRTHR50_avg+ohr4.OHRTHR51_avg+ohr4.OHRTHR52_avg+ohr4.OHRTHR53_avg)
HRMACS4=(ohr4.OHRTHR54_avg+ohr4.OHRTHR55_avg+ohr4.OHRTHR56_avg+ohr4.OHRTHR57_avg+ohr4.OHRTHR58_avg+ohr4.OHRTHR60_avg+ohr4.OHRTHR61_avg)
ohrarr.HRMACAV_avg=(HRMACS1+HRMACS2+HRMACS3+HRMACS4)/34.0

HRMAXGRD_avg1=(ohr1.OHRTHR10_avg+ohr1.OHRTHR11_avg+ohr3.OHRTHR34_avg+ohr3.OHRTHR35_avg+ohr4.OHRTHR55_avg+ohr4.OHRTHR56_avg)/6.0
HRMAXGRD_avg2=(ohr1.OHRTHR12_avg+ohr1.OHRTHR13_avg+ohr3.OHRTHR36_avg+ohr3.OHRTHR37_avg+ohr4.OHRTHR57_avg+ohr4.OHRTHR58_avg)/6.0
ohrarr.HRMAXGRD_avg=(HRMAXGRD_avg1-HRMAXGRD_avg2)

HRMARAD1GRD=(ohr1.OHRTHR08_avg+ohr2.OHRTHR31_avg+ohr3.OHRTHR33_avg+ohr4.OHRTHR52_avg)/4.0
HRMARAD2GRD=(ohr1.OHRTHR09_avg+ohr4.OHRTHR53_avg+ohr4.OHRTHR54_avg)/3.0
ohrarr.HRMARADGRD_avg=(HRMARAD1GRD-HRMARAD2GRD)

OBASUM1=(oob1.OOBTHR08_avg+oob1.OOBTHR09_avg+oob1.OOBTHR10_avg+oob1.OOBTHR11_avg+oob1.OOBTHR12_avg+oob1.OOBTHR11_avg+oob1.OOBTHR12_avg+oob1.OOBTHR13_avg+oob1.OOBTHR14_avg+oob1.OOBTHR15_avg)
OBASUM2=(oob2.OOBTHR17_avg+oob2.OOBTHR18_avg+oob2.OOBTHR19_avg+oob2.OOBTHR20_avg+oob2.OOBTHR21_avg+oob2.OOBTHR22_avg+oob2.OOBTHR23_avg+oob2.OOBTHR24_avg+oob2.OOBTHR25_avg+oob2.OOBTHR26_avg)
OBASUM3=(oob2.OOBTHR27_avg+oob2.OOBTHR28_avg+oob2.OOBTHR29_avg+oob2.OOBTHR30_avg+oob2.OOBTHR31_avg+oob3.OOBTHR33_avg+oob3.OOBTHR34_avg+oob3.OOBTHR35_avg+oob3.OOBTHR36_avg+oob3.OOBTHR37_avg)
OBASUM4=(oob3.OOBTHR38_avg+oob3.OOBTHR39_avg+oob3.OOBTHR40_avg+oob3.OOBTHR41_avg+oob3.OOBTHR44_avg+oob3.OOBTHR45_avg+oob3.OOBTHR36_avg)
oobarr.OBAAVG_avg=(OBASUM1+OBASUM2+OBASUM3+OBASUM4)/37.0

OBACONE1=(oob1.OOBTHR08_avg+oob1.OOBTHR09_avg+oob1.OOBTHR10_avg+oob1.OOBTHR11_avg+oob1.OOBTHR12_avg+oob1.OOBTHR13_avg+oob1.OOBTHR14_avg+oob1.OOBTHR15_avg+oob2.OOBTHR17_avg+oob2.OOBTHR18_avg)
OBACONE2=(oob2.OOBTHR19_avg+oob2.OOBTHR20_avg+oob2.OOBTHR21_avg+oob2.OOBTHR22_avg+oob2.OOBTHR23_avg+oob2.OOBTHR24_avg+oob2.OOBTHR25_avg+oob2.OOBTHR26_avg+oob2.OOBTHR27_avg+oob2.OOBTHR28_avg)
OBACONE3=(oob2.OOBTHR29_avg+oob2.OOBTHR30_avg+oob4.OOBTHR57_avg+oob4.OOBTHR58_avg+oob4.OOBTHR59_avg+oob4.OOBTHR60_avg+oob4.OOBTHR61_avg)
oobarr.OBACONEAVG_avg=(OBACONE1+OBACONE2+OBACONE3)/27.0

FWBLKHDT1_avg=(oob4.OOBTHR62_avg+oob4.OOBTHR63_avg+obf.x4RT700T_avg+obf.x4RT701T_avg+obf.x4RT702T_avg+obf.x4RT703T_avg+obf.x4RT704T_avg)
FWBLKHDT2_avg=(obf.x4RT705T_avg+obf.x4RT706T_avg+obf.x4RT707T_avg+obf.x4RT708T_avg+obf.x4RT709T_avg+obf.x4RT710T_avg+obf.x4RT711T_avg)
oobarr.FWBLKHDT_avg=(FWBLKHDT1_avg+FWBLKHDT2_avg)/14.0

oobarr.AFTBLKHDT_avg=(oob2.OOBTHR31_avg+oob3.OOBTHR33_avg+oob3.OOBTHR34_avg)/3.0

oobarr.OBAAXGRD_avg=(oobarr.FWBLKHDT_avg-oobarr.AFTBLKHDT_avg)

oobarr.MZOBACONE_avg=(oob1.OOBTHR08_avg+oob2.OOBTHR19_avg+oob2.OOBTHR26_avg+oob2.OOBTHR31_avg+oob4.OOBTHR57_avg+oob4.OOBTHR60_avg+hrm.x4RT575T_avg)/7.0

oobarr.PZOBACONE_avg=(oob1.OOBTHR13_avg+oob2.OOBTHR22_avg+oob2.OOBTHR23_avg+oob2.OOBTHR28_avg+oob2.OOBTHR29_avg+oob4.OOBTHR61_avg)/6.0

oobarr.OBADIAGRAD_avg=(oobarr.MZOBACONE_avg-oobarr.PZOBACONE_avg)

print, ohr1.OHRTHR02_avg , ohr1.OHRTHR03_avg
print, ohrarr.OHRTHR_MIN_avg

for i=0L, n_elements(ohr1)-1 do begin
  if (ohr1(i).OHRTHR02_avg le ohr1(i).OHRTHR03_avg) then ohrarr(i).OHRTHR_MIN_avg=ohr1(i).OHRTHR02_avg else ohrarr(i).OHRTHR_MIN_avg=ohr1(i).OHRTHR03_avg
  if (ohr1(i).OHRTHR04_avg le ohrarr(i).OHRTHR_MIN_avg) then ohrarr(i).OHRTHR_MIN_avg=ohr1(i).OHRTHR04_avg
  if (ohr1(i).OHRTHR05_avg le ohrarr(i).OHRTHR_MIN_avg) then ohrarr(i).OHRTHR_MIN_avg=ohr1(i).OHRTHR05_avg
  if (ohr1(i).OHRTHR06_avg le ohrarr(i).OHRTHR_MIN_avg) then ohrarr(i).OHRTHR_MIN_avg=ohr1(i).OHRTHR06_avg
  if (ohr1(i).OHRTHR07_avg le ohrarr(i).OHRTHR_MIN_avg) then ohrarr(i).OHRTHR_MIN_avg=ohr1(i).OHRTHR07_avg
  if (ohr1(i).OHRTHR08_avg le ohrarr(i).OHRTHR_MIN_avg) then ohrarr(i).OHRTHR_MIN_avg=ohr1(i).OHRTHR08_avg
  if (ohr1(i).OHRTHR09_avg le ohrarr(i).OHRTHR_MIN_avg) then ohrarr(i).OHRTHR_MIN_avg=ohr1(i).OHRTHR09_avg
  if (ohr1(i).OHRTHR10_avg le ohrarr(i).OHRTHR_MIN_avg) then ohrarr(i).OHRTHR_MIN_avg=ohr1(i).OHRTHR10_avg
  if (ohr1(i).OHRTHR11_avg le ohrarr(i).OHRTHR_MIN_avg) then ohrarr(i).OHRTHR_MIN_avg=ohr1(i).OHRTHR11_avg
  if (ohr1(i).OHRTHR12_avg le ohrarr(i).OHRTHR_MIN_avg) then ohrarr(i).OHRTHR_MIN_avg=ohr1(i).OHRTHR12_avg
  if (ohr1(i).OHRTHR13_avg le ohrarr(i).OHRTHR_MIN_avg) then ohrarr(i).OHRTHR_MIN_avg=ohr1(i).OHRTHR13_avg
  if (ohr2(i).OHRTHR21_avg le ohrarr(i).OHRTHR_MIN_avg) then ohrarr(i).OHRTHR_MIN_avg=ohr2(i).OHRTHR21_avg
  if (ohr2(i).OHRTHR22_avg le ohrarr(i).OHRTHR_MIN_avg) then ohrarr(i).OHRTHR_MIN_avg=ohr2(i).OHRTHR22_avg
  if (ohr2(i).OHRTHR23_avg le ohrarr(i).OHRTHR_MIN_avg) then ohrarr(i).OHRTHR_MIN_avg=ohr2(i).OHRTHR23_avg
  if (ohr2(i).OHRTHR24_avg le ohrarr(i).OHRTHR_MIN_avg) then ohrarr(i).OHRTHR_MIN_avg=ohr2(i).OHRTHR24_avg
  if (ohr2(i).OHRTHR25_avg le ohrarr(i).OHRTHR_MIN_avg) then ohrarr(i).OHRTHR_MIN_avg=ohr2(i).OHRTHR25_avg
  if (ohr2(i).OHRTHR26_avg le ohrarr(i).OHRTHR_MIN_avg) then ohrarr(i).OHRTHR_MIN_avg=ohr2(i).OHRTHR26_avg
  ;if (ohr.OHRTHR27 le ohrarr.OHRTHR_MIN_avg) then ohrarr.OHRTHR_MIN_avg=ohr.OHRTHR27
  if (ohr2(i).OHRTHR29_avg le ohrarr(i).OHRTHR_MIN_avg) then ohrarr(i).OHRTHR_MIN_avg=ohr2(i).OHRTHR29_avg
  if (ohr2(i).OHRTHR30_avg le ohrarr(i).OHRTHR_MIN_avg) then ohrarr(i).OHRTHR_MIN_avg=ohr2(i).OHRTHR30_avg
  if (ohr3(i).OHRTHR33_avg le ohrarr(i).OHRTHR_MIN_avg) then ohrarr(i).OHRTHR_MIN_avg=ohr3(i).OHRTHR33_avg
  if (ohr3(i).OHRTHR36_avg le ohrarr(i).OHRTHR_MIN_avg) then ohrarr(i).OHRTHR_MIN_avg=ohr3(i).OHRTHR36_avg
  if (ohr3(i).OHRTHR37_avg le ohrarr(i).OHRTHR_MIN_avg) then ohrarr(i).OHRTHR_MIN_avg=ohr3(i).OHRTHR37_avg
  ;if (ohr.OHRTHR42 le ohrarr.OHRTHR_MIN_avg) then ohrarr.OHRTHR_MIN_avg=ohr.OHRTHR42
  if (ohr3(i).OHRTHR44_avg le ohrarr(i).OHRTHR_MIN_avg) then ohrarr(i).OHRTHR_MIN_avg=ohr3(i).OHRTHR44_avg
  if (ohr3(i).OHRTHR45_avg le ohrarr(i).OHRTHR_MIN_avg) then ohrarr(i).OHRTHR_MIN_avg=ohr3(i).OHRTHR45_avg
  if (ohr3(i).OHRTHR46_avg le ohrarr(i).OHRTHR_MIN_avg) then ohrarr(i).OHRTHR_MIN_avg=ohr3(i).OHRTHR46_avg
  if (ohr3(i).OHRTHR47_avg le ohrarr(i).OHRTHR_MIN_avg) then ohrarr(i).OHRTHR_MIN_avg=ohr3(i).OHRTHR47_avg
  if (ohr3(i).OHRTHR49_avg le ohrarr(i).OHRTHR_MIN_avg) then ohrarr(i).OHRTHR_MIN_avg=ohr3(i).OHRTHR49_avg
  if (ohr3(i).OHRTHR50_avg le ohrarr(i).OHRTHR_MIN_avg) then ohrarr(i).OHRTHR_MIN_avg=ohr3(i).OHRTHR50_avg
  if (ohr4(i).OHRTHR51_avg le ohrarr(i).OHRTHR_MIN_avg) then ohrarr(i).OHRTHR_MIN_avg=ohr4(i).OHRTHR51_avg
  if (ohr4(i).OHRTHR52_avg le ohrarr(i).OHRTHR_MIN_avg) then ohrarr(i).OHRTHR_MIN_avg=ohr4(i).OHRTHR52_avg
  if (ohr4(i).OHRTHR53_avg le ohrarr(i).OHRTHR_MIN_avg) then ohrarr(i).OHRTHR_MIN_avg=ohr4(i).OHRTHR53_avg
  if (ohr4(i).OHRTHR55_avg le ohrarr(i).OHRTHR_MIN_avg) then ohrarr(i).OHRTHR_MIN_avg=ohr4(i).OHRTHR55_avg
  if (ohr4(i).OHRTHR56_avg le ohrarr(i).OHRTHR_MIN_avg) then ohrarr(i).OHRTHR_MIN_avg=ohr4(i).OHRTHR56_avg
  if (ohr1(i).OHRTHR02_avg ge ohr1(i).OHRTHR03_avg) then ohrarr(i).OHRTHR_MAX_avg=ohr1(i).OHRTHR02_avg else ohrarr(i).OHRTHR_MAX_avg=ohr1(i).OHRTHR03_avg
  if (ohr1(i).OHRTHR04_avg ge ohrarr(i).OHRTHR_MAX_avg) then ohrarr(i).OHRTHR_MAX_avg=ohr1(i).OHRTHR04_avg
  if (ohr1(i).OHRTHR05_avg ge ohrarr(i).OHRTHR_MAX_avg) then ohrarr(i).OHRTHR_MAX_avg=ohr1(i).OHRTHR05_avg
  if (ohr1(i).OHRTHR06_avg ge ohrarr(i).OHRTHR_MAX_avg) then ohrarr(i).OHRTHR_MAX_avg=ohr1(i).OHRTHR06_avg
  if (ohr1(i).OHRTHR07_avg ge ohrarr(i).OHRTHR_MAX_avg) then ohrarr(i).OHRTHR_MAX_avg=ohr1(i).OHRTHR07_avg
  if (ohr1(i).OHRTHR08_avg ge ohrarr(i).OHRTHR_MAX_avg) then ohrarr(i).OHRTHR_MAX_avg=ohr1(i).OHRTHR08_avg
  if (ohr1(i).OHRTHR09_avg ge ohrarr(i).OHRTHR_MAX_avg) then ohrarr(i).OHRTHR_MAX_avg=ohr1(i).OHRTHR09_avg
  if (ohr1(i).OHRTHR10_avg ge ohrarr(i).OHRTHR_MAX_avg) then ohrarr(i).OHRTHR_MAX_avg=ohr1(i).OHRTHR10_avg
  if (ohr1(i).OHRTHR11_avg ge ohrarr(i).OHRTHR_MAX_avg) then ohrarr(i).OHRTHR_MAX_avg=ohr1(i).OHRTHR11_avg
  if (ohr1(i).OHRTHR12_avg ge ohrarr(i).OHRTHR_MAX_avg) then ohrarr(i).OHRTHR_MAX_avg=ohr1(i).OHRTHR12_avg
  if (ohr1(i).OHRTHR13_avg ge ohrarr(i).OHRTHR_MAX_avg) then ohrarr(i).OHRTHR_MAX_avg=ohr1(i).OHRTHR13_avg
  if (ohr2(i).OHRTHR21_avg ge ohrarr(i).OHRTHR_MAX_avg) then ohrarr(i).OHRTHR_MAX_avg=ohr2(i).OHRTHR21_avg
  if (ohr2(i).OHRTHR22_avg ge ohrarr(i).OHRTHR_MAX_avg) then ohrarr(i).OHRTHR_MAX_avg=ohr2(i).OHRTHR22_avg
  if (ohr2(i).OHRTHR23_avg ge ohrarr(i).OHRTHR_MAX_avg) then ohrarr(i).OHRTHR_MAX_avg=ohr2(i).OHRTHR23_avg
  if (ohr2(i).OHRTHR24_avg ge ohrarr(i).OHRTHR_MAX_avg) then ohrarr(i).OHRTHR_MAX_avg=ohr2(i).OHRTHR24_avg
  if (ohr2(i).OHRTHR25_avg ge ohrarr(i).OHRTHR_MAX_avg) then ohrarr(i).OHRTHR_MAX_avg=ohr2(i).OHRTHR25_avg
  if (ohr2(i).OHRTHR26_avg ge ohrarr(i).OHRTHR_MAX_avg) then ohrarr(i).OHRTHR_MAX_avg=ohr2(i).OHRTHR26_avg
  ;if (ohr(i).OHRTHR27 ge ohrarr(i).OHRTHR_MAX_avg) then ohrarr(i).OHRTHR_MAX_avg=ohr(i).OHRTHR27
  if (ohr2(i).OHRTHR29_avg ge ohrarr(i).OHRTHR_MAX_avg) then ohrarr(i).OHRTHR_MAX_avg=ohr2(i).OHRTHR29_avg
  if (ohr2(i).OHRTHR30_avg ge ohrarr(i).OHRTHR_MAX_avg) then ohrarr(i).OHRTHR_MAX_avg=ohr2(i).OHRTHR30_avg
  if (ohr3(i).OHRTHR33_avg ge ohrarr(i).OHRTHR_MAX_avg) then ohrarr(i).OHRTHR_MAX_avg=ohr3(i).OHRTHR33_avg
  if (ohr3(i).OHRTHR36_avg ge ohrarr(i).OHRTHR_MAX_avg) then ohrarr(i).OHRTHR_MAX_avg=ohr3(i).OHRTHR36_avg
  if (ohr3(i).OHRTHR37_avg ge ohrarr(i).OHRTHR_MAX_avg) then ohrarr(i).OHRTHR_MAX_avg=ohr3(i).OHRTHR37_avg
  ;if (ohr(i).OHRTHR42 ge ohrarr(i).OHRTHR_MAX_avg) then ohrarr(i).OHRTHR_MAX_avg=ohr(i).OHRTHR42
  if (ohr3(i).OHRTHR44_avg ge ohrarr(i).OHRTHR_MAX_avg) then ohrarr(i).OHRTHR_MAX_avg=ohr3(i).OHRTHR44_avg
  if (ohr3(i).OHRTHR45_avg ge ohrarr(i).OHRTHR_MAX_avg) then ohrarr(i).OHRTHR_MAX_avg=ohr3(i).OHRTHR45_avg
  if (ohr3(i).OHRTHR46_avg ge ohrarr(i).OHRTHR_MAX_avg) then ohrarr(i).OHRTHR_MAX_avg=ohr3(i).OHRTHR46_avg
  if (ohr3(i).OHRTHR47_avg ge ohrarr(i).OHRTHR_MAX_avg) then ohrarr(i).OHRTHR_MAX_avg=ohr3(i).OHRTHR47_avg
  if (ohr3(i).OHRTHR49_avg ge ohrarr(i).OHRTHR_MAX_avg) then ohrarr(i).OHRTHR_MAX_avg=ohr3(i).OHRTHR49_avg
  if (ohr3(i).OHRTHR50_avg ge ohrarr(i).OHRTHR_MAX_avg) then ohrarr(i).OHRTHR_MAX_avg=ohr3(i).OHRTHR50_avg
  if (ohr4(i).OHRTHR51_avg ge ohrarr(i).OHRTHR_MAX_avg) then ohrarr(i).OHRTHR_MAX_avg=ohr4(i).OHRTHR51_avg
  if (ohr4(i).OHRTHR52_avg ge ohrarr(i).OHRTHR_MAX_avg) then ohrarr(i).OHRTHR_MAX_avg=ohr4(i).OHRTHR52_avg
  if (ohr4(i).OHRTHR53_avg ge ohrarr(i).OHRTHR_MAX_avg) then ohrarr(i).OHRTHR_MAX_avg=ohr4(i).OHRTHR53_avg
  if (ohr4(i).OHRTHR55_avg ge ohrarr(i).OHRTHR_MAX_avg) then ohrarr(i).OHRTHR_MAX_avg=ohr4(i).OHRTHR55_avg
  if (ohr4(i).OHRTHR56_avg ge ohrarr(i).OHRTHR_MAX_avg) then ohrarr(i).OHRTHR_MAX_avg=ohr4(i).OHRTHR56_avg
  ohrarr(i).HRMARANGE_avg=((ohrarr(i).OHRTHR_MAX_avg)-(ohrarr(i).OHRTHR_MIN_avg))
  if (oob3(i).OOBTHR42_avg le oob3(i).OOBTHR43_avg) then oobarr(i).TFTE_MIN_avg=oob3(i).OOBTHR42_avg else oobarr(i).TFTE_MIN_avg=oob3(i).OOBTHR43_avg
  if (oob3(i).OOBTHR44_avg le oobarr(i).TFTE_MIN_avg) then oobarr(i).TFTE_MIN_avg=oob3(i).OOBTHR44_avg
  if (oob3(i).OOBTHR42_avg ge oob3(i).OOBTHR43_avg) then oobarr(i).TFTE_MAX_avg=oob3(i).OOBTHR42_avg else oobarr(i).TFTE_MAX_avg=oob3(i).OOBTHR43_avg
  if (oob3(i).OOBTHR44_avg ge oobarr(i).TFTE_MAX_avg) then oobarr(i).TFTE_MAX_avg=oob3(i).OOBTHR44_avg
  oobarr(i).TFTERANGE_avg=((oobarr(i).TFTE_MAX_avg)-(oobarr(i).TFTE_MIN_avg))
  if (oob1(i).OOBTHR02_avg le oob1(i).OOBTHR03_avg) then oobarr(i).HSTRUT_MIN_avg=oob1(i).OOBTHR02_avg else oobarr(i).HSTRUT_MIN_avg=oob1(i).OOBTHR03_avg
  if (oob1(i).OOBTHR04_avg le oobarr(i).HSTRUT_MIN_avg) then oobarr(i).HSTRUT_MIN_avg=oob1(i).OOBTHR04_avg
  if (oob1(i).OOBTHR05_avg le oobarr(i).HSTRUT_MIN_avg) then oobarr(i).HSTRUT_MIN_avg=oob1(i).OOBTHR05_avg
  if (oob1(i).OOBTHR06_avg le oobarr(i).HSTRUT_MIN_avg) then oobarr(i).HSTRUT_MIN_avg=oob1(i).OOBTHR06_avg
  if (oob1(i).OOBTHR07_avg le oobarr(i).HSTRUT_MIN_avg) then oobarr(i).HSTRUT_MIN_avg=oob1(i).OOBTHR07_avg
  if (oob1(i).OOBTHR02_avg ge oob1(i).OOBTHR03_avg) then oobarr(i).HSTRUT_MAX_avg=oob1(i).OOBTHR02_avg else oobarr(i).HSTRUT_MAX_avg=oob1(i).OOBTHR03_avg
  if (oob1(i).OOBTHR04_avg ge oobarr(i).HSTRUT_MAX_avg) then oobarr(i).HSTRUT_MAX_avg=oob1(i).OOBTHR04_avg
  if (oob1(i).OOBTHR05_avg ge oobarr(i).HSTRUT_MAX_avg) then oobarr(i).HSTRUT_MAX_avg=oob1(i).OOBTHR05_avg
  if (oob1(i).OOBTHR06_avg ge oobarr(i).HSTRUT_MAX_avg) then oobarr(i).HSTRUT_MAX_avg=oob1(i).OOBTHR06_avg
  if (oob1(i).OOBTHR07_avg ge oobarr(i).HSTRUT_MAX_avg) then oobarr(i).HSTRUT_MAX_avg=oob1(i).OOBTHR07_avg
  oobarr(i).HRMASTRUTRNGE_avg=((oobarr(i).HSTRUT_MAX_avg)-(oobarr(i).HSTRUT_MIN_avg))
  if (oob4(i).OOBTHR49_avg le oob4(i).OOBTHR50_avg) then oobarr(i).SSTRUT_MIN_avg=oob4(i).OOBTHR49_avg else oobarr(i).SSTRUT_MIN_avg=oob4(i).OOBTHR50_avg
  if (oob4(i).OOBTHR51_avg le oobarr(i).SSTRUT_MIN_avg) then oobarr(i).SSTRUT_MIN_avg=oob4(i).OOBTHR51_avg
  if (oob4(i).OOBTHR52_avg le oobarr(i).SSTRUT_MIN_avg) then oobarr(i).SSTRUT_MIN_avg=oob4(i).OOBTHR52_avg
  if (oob4(i).OOBTHR53_avg le oobarr(i).SSTRUT_MIN_avg) then oobarr(i).SSTRUT_MIN_avg=oob4(i).OOBTHR53_avg
  if (oob4(i).OOBTHR54_avg le oobarr(i).SSTRUT_MIN_avg) then oobarr(i).SSTRUT_MIN_avg=oob4(i).OOBTHR54_avg
  if (oob4(i).OOBTHR49_avg ge oob4(i).OOBTHR50_avg) then oobarr(i).SSTRUT_MAX_avg=oob4(i).OOBTHR49_avg else oobarr(i).SSTRUT_MAX_avg=oob4(i).OOBTHR50_avg
  if (oob4(i).OOBTHR51_avg ge oobarr(i).SSTRUT_MAX_avg) then oobarr(i).SSTRUT_MAX_avg=oob4(i).OOBTHR51_avg
  if (oob4(i).OOBTHR52_avg ge oobarr(i).SSTRUT_MAX_avg) then oobarr(i).SSTRUT_MAX_avg=oob4(i).OOBTHR52_avg
  if (oob4(i).OOBTHR53_avg ge oobarr(i).SSTRUT_MAX_avg) then oobarr(i).SSTRUT_MAX_avg=oob4(i).OOBTHR53_avg
  if (oob4(i).OOBTHR54_avg ge oobarr(i).SSTRUT_MAX_avg) then oobarr(i).SSTRUT_MAX_avg=oob4(i).OOBTHR54_avg
  oobarr(i).SCSTRUTRNGE_avg=((oobarr(i).SSTRUT_MAX_avg)-(oobarr(i).SSTRUT_MIN_avg))

endfor
  
mwrfits,ohrarr,'hrma_comp_ohr.fits',/create
mwrfits,oobarr,'hrma_comp_oob.fits',/create
  
end
  
