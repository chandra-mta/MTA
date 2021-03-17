PRO MUPS_FIX
; some columns were shifted in the original mups_read and rdb is now
;  incomplete (gaps), so try to fix from extant fits files.

A=mrdfits('mups_2a_mar2105.fits',1)
B=mrdfits('mups_2b_mar2105.fits',1)

sel=where(A.time lt 195106000)
a=a(sel)
b=b(sel)
a_new=a
b_new=b

a_new.PFTANKOP_avg= a.PHETANKT_avg
a_new.PHETANKP_avg= a.PHETANKT_avg
a_new.PHETANKT_avg= a.PHOFP1T_avg
a_new.PHOFP1T_avg=b.PLINE01T_avg
a_new.PXDM01T_avg= a.PXDM02T_avg
a_new.PXDM02T_avg= a.PXTANK1T_avg
a_new.PXTANK1T_avg= a.PXTANK2T_avg
a_new.PXTANK2T_avg= a.PXTANKIP_avg
a_new.PXTANKIP_avg= a.PXTANKOP_avg
mwrfits,a_new,'mups_2a.fits',/create

b_new.PLINE01T_AVG = b.PLINE02T_AVG
b_new.PLINE02T_AVG = b.PLINE03T_AVG
b_new.PLINE03T_AVG = b.PLINE04T_AVG
b_new.PLINE04T_AVG = b.PLINE05T_AVG
b_new.PLINE05T_AVG = b.PLINE06T_AVG
b_new.PLINE06T_AVG = b.PLINE07T_AVG
b_new.PLINE07T_AVG = b.PLINE08T_AVG
b_new.PLINE08T_AVG = b.PLINE09T_AVG
b_new.PLINE09T_AVG = b.PLINE10T_AVG
b_new.PLINE10T_AVG = b.PLINE11T_AVG
b_new.PLINE11T_AVG = b.PLINE12T_AVG
b_new.PLINE12T_AVG = b.PLINE13T_AVG
b_new.PLINE13T_AVG = b.PLINE14T_AVG
b_new.PLINE14T_AVG = b.PLINE15T_AVG
b_new.PLINE15T_AVG = b.PLINE16T_AVG
b_new.PLINE16T_AVG = a.PXDM01T_AVG
mwrfits,b_new,'mups_2b.fits',/create

end
if (froot eq 'mups_2') then begin
  rdfloat,'/data/mta/DataSeeker/data/repository/mups_2.rdb', time, $
    PCM01T,PCM02T,PCM03T,PCM04T,PFDM101T,PFDM102T, PFDM201T,PFDM202T,$
    PFFP01T,PFTANK1T,PFTANK2T,PFTANKIP, PFTANKOP,skipline=2, $
    columns=[1,3,5,7,9,11,13,15,17,19,21,23,25,27]
  rdfloat,'/data/mta/DataSeeker/data/repository/mups_2.rdb', $
    PHETANKP,PHETANKT,$
    PHOFP1T,PLINE01T,PLINE02T, PLINE03T,PLINE04T,PLINE05T,PLINE06T,$
    PLINE07T,PLINE08T, PLINE09T,PLINE10T,skipline=2, $
    columns=[29,31,33,35,37,39,41,43,45,47,49,51,53]
  rdfloat,'/data/mta/DataSeeker/data/repository/mups_2.rdb', $
    PLINE11T,PLINE12T, PLINE13T,$
    PLINE14T, PLINE15T,PLINE16T,PXDM01T,PXDM02T,PXTANK1T,PXTANK2T, $
    PXTANKIP,PXTANKOP,skipline=2, $
    columns=[55,57,59,61,63,65,67,69,71,73,75,77]
  m2 = {mups2, time:0L, PCM01T_avg:0.0,PCM02T_avg:0.0,PCM03T_avg:0.0, $
     PCM04T_avg:0.0,PFDM101T_avg:0.0,PFDM102T_avg:0.0,PFDM201T_avg:0.0, $
     PFDM202T_avg:0.0,PFFP01T_avg:0.0,PFTANK1T_avg:0.0,PFTANK2T_avg:0.0, $
     PFTANKIP_avg:0.0,PFTANKOP_avg:0.0,PHETANKP_avg:0.0,PHETANKT_avg:0.0, $
     PHOFP1T_avg:0.0,PXDM01T_avg:0.0,PXDM02T_avg:0.0,PXTANK1T_avg:0.0, $
     PXTANK2T_avg:0.0,PXTANKIP_avg:0.0,PXTANKOP_avg:0.0}

  mP = {mupsP, time:0L, $
     PLINE01T_avg:0.0,PLINE02T_avg:0.0,PLINE03T_avg:0.0, $
     PLINE04T_avg:0.0,PLINE05T_avg:0.0,PLINE06T_avg:0.0,PLINE07T_avg:0.0, $
     PLINE08T_avg:0.0,PLINE09T_avg:0.0,PLINE10T_avg:0.0,PLINE11T_avg:0.0, $
     PLINE12T_avg:0.0,PLINE13T_avg:0.0,PLINE14T_avg:0.0,PLINE15T_avg:0.0, $
     PLINE16T_avg:0.0}

  b=where(time gt 0, num)
  data1 = replicate({mups2}, num)
  data1.time=time(b)
  data1.PCM01T_avg=PCM01T(b)
  data1.PCM02T_avg=PCM02T(b)
  data1.PCM03T_avg=PCM03T(b)
  data1.PCM04T_avg=PCM04T(b)
  data1.PFDM101T_avg=PFDM101T(b)
  data1.PFDM102T_avg=PFDM102T(b)
  data1.PFDM201T_avg=PFDM201T(b)
  data1.PFDM202T_avg=PFDM202T(b)
  data1.PFFP01T_avg=PFFP01T(b)
  data1.PFTANK1T_avg=PFTANK1T(b)
  data1.PFTANK2T_avg=PFTANK2T(b)
  data1.PFTANKIP_avg=PFTANKIP(b)
  data1.PFTANKOP_avg=PFTANKOP(b)
  data1.PHETANKP_avg=PHETANKP(b)
  data1.PHETANKT_avg=PHETANKT(b)
  data1.PHOFP1T_avg=PHOFP1T(b)
  data1.PXDM01T_avg=PXDM01T(b)
  data1.PXDM02T_avg=PXDM02T(b)
  data1.PXTANK1T_avg=PXTANK1T(b)
  data1.PXTANK2T_avg=PXTANK2T(b)
  data1.PXTANKIP_avg=PXTANKIP(b)
  data1.PXTANKOP_avg=PXTANKOP(b)
  data1=data1(uniq(data1.time,sort(data1.time)))
  mwrfits,data1,'mups2_rdb.fits',/create
  data1 = replicate({mupsP}, num)
  data1.time=time(b)
  data1.PLINE01T_avg=PLINE01T(b)
  data1.PLINE02T_avg=PLINE02T(b)
  data1.PLINE03T_avg=PLINE03T(b)
  data1.PLINE04T_avg=PLINE04T(b)
  data1.PLINE05T_avg=PLINE05T(b)
  data1.PLINE06T_avg=PLINE06T(b)
  data1.PLINE07T_avg=PLINE07T(b)
  data1.PLINE08T_avg=PLINE08T(b)
  data1.PLINE09T_avg=PLINE09T(b)
  data1.PLINE10T_avg=PLINE10T(b)
  data1.PLINE11T_avg=PLINE11T(b)
  data1.PLINE12T_avg=PLINE12T(b)
  data1.PLINE13T_avg=PLINE13T(b)
  data1.PLINE14T_avg=PLINE14T(b)
  data1.PLINE15T_avg=PLINE15T(b)
  data1.PLINE16T_avg=PLINE16T(b)
  data1=data1(uniq(data1.time,sort(data1.time)))
  mwrfits,data1,'mups3_rdb.fits',/create
  return,data1
endif ;if (froot eq 'mups_2') then begin
if (froot eq 'mups_pcad') then begin
  rdfloat,'/data/mta/DataSeeker/data/repository/mups_pcad.rdb', time, $
    AOBEGFIR,AOFTHRST,AOMUPDEN,AOPSTHCD,AOPSTHCS,AOVAM1FS, AOVAM2FS, $
    AOVAM3FS,AOVAM4FS,AOVAMPWR,AOVAPWRN,AOMUPS1P, AOMUPS2P,AOMUPS3P, $
    skipline=2,columns=[1,3,5,7,9,11,13,15,17,19,21,23,25,27,29]
  rdfloat,'/data/mta/DataSeeker/data/repository/mups_pcad.rdb', $
    AOMUPS4P,AOMUPSMP,AOVBM1FS,AOVBM2FS, AOVBM3FS,AOVBM4FS,AOVBMPWR, $
    AOVBPWRN,AOMUPS1R,AOMUPS2R, AOMUPS3R,AOMUPS4R,AOMUPSMR,skipline=2, $
    columns=[31,33,35,37,39,41,43,45,47,49,51,53,55]
  m3 = {mups3, time:0L, AOBEGFIR_avg:0.0,AOFTHRST_avg:0.0,AOMUPDEN_avg:0.0, $
        AOPSTHCD_avg:0.0,AOPSTHCS_avg:0.0,AOVAM1FS_avg:0.0,AOVAM2FS_avg:0.0, $
        AOVAM3FS_avg:0.0,AOVAM4FS_avg:0.0,AOVAMPWR_avg:0.0,AOVAPWRN_avg:0.0, $
        AOMUPS1P_avg:0.0,AOMUPS2P_avg:0.0,AOMUPS3P_avg:0.0,AOMUPS4P_avg:0.0, $
        AOMUPSMP_avg:0.0,AOVBM1FS_avg:0.0,AOVBM2FS_avg:0.0,AOVBM3FS_avg:0.0, $
        AOVBM4FS_avg:0.0,AOVBMPWR_avg:0.0,AOVBPWRN_avg:0.0,AOMUPS1R_avg:0.0, $
        AOMUPS2R_avg:0.0,AOMUPS3R_avg:0.0,AOMUPS4R_avg:0.0,AOMUPSMR_avg:0.0}
  b=where(time gt 0, num)
  data1 = replicate({mups3}, num)
  data1.time=time(b)
  data1.AOBEGFIR_avg=AOBEGFIR(b)
  data1.AOFTHRST_avg=AOFTHRST(b)
  data1.AOMUPDEN_avg=AOMUPDEN(b)
  data1.AOPSTHCD_avg=AOPSTHCD(b)
  data1.AOPSTHCS_avg=AOPSTHCS(b)
  data1.AOVAM1FS_avg=AOVAM1FS(b)
  data1.AOVAM2FS_avg=AOVAM2FS(b)
  data1.AOVAM3FS_avg=AOVAM3FS(b)
  data1.AOVAM4FS_avg=AOVAM4FS(b)
  data1.AOVAMPWR_avg=AOVAMPWR(b)
  data1.AOVAPWRN_avg=AOVAPWRN(b)
  data1.AOMUPS1P_avg=AOMUPS1P(b)
  data1.AOMUPS2P_avg=AOMUPS2P(b)
  data1.AOMUPS3P_avg=AOMUPS3P(b)
  data1.AOMUPS4P_avg=AOMUPS4P(b)
  data1.AOMUPSMP_avg=AOMUPSMP(b)
  data1.AOVBM1FS_avg=AOVBM1FS(b)
  data1.AOVBM2FS_avg=AOVBM2FS(b)
  data1.AOVBM3FS_avg=AOVBM3FS(b)
  data1.AOVBM4FS_avg=AOVBM4FS(b)
  data1.AOVBMPWR_avg=AOVBMPWR(b)
  data1.AOVBPWRN_avg=AOVBPWRN(b)
  data1.AOMUPS1R_avg=AOMUPS1R(b)
  data1.AOMUPS2R_avg=AOMUPS2R(b)
  data1.AOMUPS3R_avg=AOMUPS3R(b)
  data1.AOMUPS4R_avg=AOMUPS4R(b)
  data1.AOMUPSMR_avg=AOMUPSMR(b)
  data1=data1(uniq(data1.time,sort(data1.time)))
  mwrfits,data1,'mupspcad_rdb.fits'
  return,data1
endif ;if (froot eq 'mups_pcad') then begin
if (froot eq 'mups_prop') then begin
  rdfloat,'/data/mta/DataSeeker/data/repository/mups_prop.rdb', time, $
    PVDETMA1,PVDETMA2,PVDETMB1,PVDETMB2,PF1MV1C1,PF1MV1C2, PF1MV2C1, $
    PF1MV2C2,PMCBHTP1,PMCBHTP2,PMCBHTR1,PMCBHTR2, PMFTHSUR,PMFTHTP1, $
    PMFTHTP2,PMFTHTR1,PMFTHTR2,PMHSPRTN, skipline=2, $
    columns=[1,3,5,7,9,11,13,15,17,19,21,23,25,27,29,31,33,35,37]
  rdfloat,'/data/mta/DataSeeker/data/repository/mups_prop.rdb', $
     PMHSPSEL,PMP1K4P1,PMP1K4P2, $
    PMP1K4R1,PMP1K4R2,PMP1K5P1, PMP1K5P2,PMP1K5R1,PMP1K5R2,PMPDPP1, $
    PMPDPP2,PMPDPR1, PMPDPR2,PMVHP1X,PMVHP2X,PMVHR1X,PMVHR2X,skipline=2, $
    columns=[39,41,43,45,47,49,51,53,55,57,59,61,63,65,67,69,71]
  m4 = {mups4, time:0L, PVDETMA1_avg:0.0,PVDETMA2_avg:0.0, $
    PVDETMB1_avg:0.0,PVDETMB2_avg:0.0,PF1MV1C1_avg:0.0,PF1MV1C2_avg:0.0, $
    PF1MV2C1_avg:0.0,PF1MV2C2_avg:0.0,PMCBHTP1_avg:0.0,PMCBHTP2_avg:0.0, $
    PMCBHTR1_avg:0.0,PMCBHTR2_avg:0.0,PMFTHSUR_avg:0.0,PMFTHTP1_avg:0.0, $
    PMFTHTP2_avg:0.0,PMFTHTR1_avg:0.0,PMFTHTR2_avg:0.0,PMHSPRTN_avg:0.0, $
    PMHSPSEL_avg:0.0,PMP1K4P1_avg:0.0,PMP1K4P2_avg:0.0,PMP1K4R1_avg:0.0, $
    PMP1K4R2_avg:0.0,PMP1K5P1_avg:0.0,PMP1K5P2_avg:0.0,PMP1K5R1_avg:0.0, $
    PMP1K5R2_avg:0.0,PMPDPP1_avg:0.0,PMPDPP2_avg:0.0,PMPDPR1_avg:0.0, $
    PMPDPR2_avg:0.0,PMVHP1X_avg:0.0,PMVHP2X_avg:0.0,PMVHR1X_avg:0.0, $
    PMVHR2X_avg:0.0}
  b=where(time gt 0, num)
  data1 = replicate({mups4}, num)
  data1.time=time(b)
  data1.PVDETMA1_avg=PVDETMA1(b)
  data1.PVDETMA2_avg=PVDETMA2(b)
  data1.PVDETMB1_avg=PVDETMB1(b)
  data1.PVDETMB2_avg=PVDETMB2(b)
  data1.PF1MV1C1_avg=PF1MV1C1(b)
  data1.PF1MV1C2_avg=PF1MV1C2(b)
  data1.PF1MV2C1_avg=PF1MV2C1(b)
  data1.PF1MV2C2_avg=PF1MV2C2(b)
  data1.PMCBHTP1_avg=PMCBHTP1(b)
  data1.PMCBHTP2_avg=PMCBHTP2(b)
  data1.PMCBHTR1_avg=PMCBHTR1(b)
  data1.PMCBHTR2_avg=PMCBHTR2(b)
  data1.PMFTHSUR_avg=PMFTHSUR(b)
  data1.PMFTHTP1_avg=PMFTHTP1(b)
  data1.PMFTHTP2_avg=PMFTHTP2(b)
  data1.PMFTHTR1_avg=PMFTHTR1(b)
  data1.PMFTHTR2_avg=PMFTHTR2(b)
  data1.PMHSPRTN_avg=PMHSPRTN(b)
  data1.PMHSPSEL_avg=PMHSPSEL(b)
  data1.PMP1K4P1_avg=PMP1K4P1(b)
  data1.PMP1K4P2_avg=PMP1K4P2(b)
  data1.PMP1K4R1_avg=PMP1K4R1(b)
  data1.PMP1K4R2_avg=PMP1K4R2(b)
  data1.PMP1K5P1_avg=PMP1K5P1(b)
  data1.PMP1K5P2_avg=PMP1K5P2(b)
  data1.PMP1K5R1_avg=PMP1K5R1(b)
  data1.PMP1K5R2_avg=PMP1K5R2(b)
  data1.PMPDPP1_avg=PMPDPP1(b)
  data1.PMPDPP2_avg=PMPDPP2(b)
  data1.PMPDPR1_avg=PMPDPR1(b)
  data1.PMPDPR2_avg=PMPDPR2(b)
  data1.PMVHP1X_avg=PMVHP1X(b)
  data1.PMVHP2X_avg=PMVHP2X(b)
  data1.PMVHR1X_avg=PMVHR1X(b)
  data1.PMVHR2X_avg=PMVHR2X(b)
  data1=data1(uniq(data1.time,sort(data1.time)))
  mwrfits,data1,'mupsprop_rdb.fits'
  return,data1
endif ;if (froot eq 'mups_prop') then begin

end
