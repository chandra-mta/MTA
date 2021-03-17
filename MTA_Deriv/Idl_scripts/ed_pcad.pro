x=mta_db_get_add(outfile='pcadtemp.fits',ter_cols='_aacbppt_avg,_aacbprt_avg,_aacccdpt_avg,_aacccdrt_avg,_aach1t_avg,_aach2t_avg,_aaotalt_avg,_aaotapmt_avg,_aaotasmt_avg,_aaoth2mt_avg')
dtrend,'pcadtemp.fits',wsmooth=30
x=mta_db_get_add(outfile='pcaditv.fits',ter_cols='_afsspc1v_avg,_afsspc2v_avg,_agws1v_avg,_agws2v_avg,_airu1bt_avg,_airu1g1i_avg,_airu1g1t_avg,_airu1g2i_avg,_airu1g2t_avg,_airu1vft_avg,_airu2bt_avg,_airu2g1i_avg,_airu2g1t_avg,_airu2g2i_avg,_airu2g2t_avg,_airu2vft_avg,_aocssi1_avg,_aocssi2_avg,_aocssi3_avg,_aocssi4_avg')
dtrend,'pcaditv.fits',wsmooth=30
;;;pcadgrate
x=mta_db_get_add(outfile='pcadgrate1.fits',ter_cols='_ai1ax1x_avg,_ai1ax1y_avg,_ai1ax2x_avg,_ai1ax2y_avg,_ai2ax1x_avg,_ai2ax1y_avg,_ai2ax2x_avg,_ai2ax2y_avg,_aoalpang_avg,_aoattqt1_avg,_aoattqt2_avg,_aoattqt3_avg,_aoattqt4_avg,_aobetang_avg')
x=mta_db_get_add(outfile='pcadgrate2.fits',ter_cols='_aocmdqt1_avg,_aocmdqt2_avg,_aocmdqt3_avg,_aoscpos1_avg,_aoscpos2_avg,_aoscpos3_avg,_aoscvel1_avg,_aoscvel2_avg,_aoscvel3_avg,_aosunec1_avg,_aosunec2_avg,_aosunec3_avg,_aosunsa1_avg,_aosunsa2_avg,_aosunsa3_avg,_aotarqt1_avg,_aotarqt2_avg,_aotarqt3_avg')
dtrend,'pcadgrate.fits',wsmooth=30
x=mta_db_get_add(ter_cols='_ohrthr27_avg,_ohrthr42_avg,_ohrthr43_avg,_oobagrd3_avg,_oobagrd6_avg', outfile='pcadftsgrad.fits')
dtrend,'pcadftsgrad.fits',wsmooth=30, filt_it=3
x=mta_db_get_add(outfile='pcadrwrate.fits',ter_cols='_aorwcmd1_avg,_aorwcmd2_avg,_aorwcmd3_avg,_aorwcmd4_avg,_aorwcmd5_avg,_aorwcmd6_avg,_aorwcnt1_avg,_aorwcnt2_avg,_aorwcnt3_avg,_aorwcnt4_avg,_aorwcnt5_avg,_aorwcnt6_avg,_aorwmc1_avg,_aorwmc4_avg,_aorwmc5_avg,_aorwspd1_avg,_aorwspd2_avg,_aorwspd3_avg,_aorwspd4_avg,_aorwspd5_avg,_aorwspd6_avg')
dtrend,'pcadrwrate.fits',wsmooth=30, filt_it=1
x=mta_db_get_add(ter_cols='_aogbias1_avg,_aogbias2_avg,_aogbias3_avg,_aogyrct1_avg,_aogyrct2_avg,_aogyrct3_avg,_aogyrct4_avg',outfile='pcadgdrift.fits')
dtrend,'pcadgdrift.fits',wsmooth=30, filt_it=1

;x=mta_db_get_add(outfile='mups_1.fits',ter_cols='PM1THV1T_avg,PM1THV2T_avg,PM2THV1T_avg,PM2THV2T_avg,PM3THV1T_avg,PM3THV2T_avg,PM4THV1T_avg,PM4THV2T_avg,PMFP01T_avg,PMTANK1T_avg,PMTANK2T_avg,PMTANK3T_avg,PMTANKP_avg,TRSPMTPC_avg,AOTHRST1_avg,AOTHRST2_avg,AOTHRST3_avg,AOTHRST4_avg')

; see mups_read x=mta_db_get_add(outfile='mups_pcad1.fits',ter_cols='AOBEGFIR_avg,AOFTHRST_avg,AOMUPDEN_avg,AOPSTHCD_avg,AOPSTHCS_avg,AOVAM1FS_avg,AOVAM2FS_avg,AOVAM3FS_avg,AOVAM4FS_avg,AOVAMPWR_avg,AOVAPWRN_avg,AOMUPS1P_avg,AOMUPS2P_avg,AOMUPS3P_avg,AOMUPS4P_avg,AOMUPSMP_avg')
; see mups_read x=mta_db_get_add(outfile='mups_pcad2.fits',ter_cols='AOVBM1FS_avg,AOVBM2FS_avg,AOVBM3FS_avg,AOVBM4FS_avg,AOVBMPWR_avg,AOVBPWRN_avg,AOMUPS1R_avg,AOMUPS2R_avg,AOMUPS3R_avg,AOMUPS4R_avg,AOMUPSMR_avg')

; see mups_read x=mta_db_get_add(outfile='mups_prop1.fits',ter_cols='PVDETMA1_avg,PVDETMA2_avg,PVDETMB1_avg,PVDETMB2_avg,PF1MV1C1_avg,PF1MV1C2_avg,PF1MV2C1_avg,PF1MV2C2_avg,PMCBHTP1_avg,PMCBHTP2_avg,PMCBHTR1_avg,PMCBHTR2_avg,PMFTHSUR_avg,PMFTHTP1_avg,PMFTHTP2_avg,PMFTHTR1_avg,PMFTHTR2_avg')
; see mups_read x=mta_db_get_add(outfile='mups_prop2.fits',ter_cols='PMHSPRTN_avg,PMHSPSEL_avg,PMP1K4P1_avg,PMP1K4P2_avg,PMP1K4R1_avg,PMP1K4R2_avg,PMP1K5P1_avg,PMP1K5P2_avg,PMP1K5R1_avg,PMP1K5R2_avg,PMPDPP1_avg,PMPDPP2_avg,PMPDPR1_avg,PMPDPR2_avg,PMVHP1X_avg,PMVHP2X_avg,PMVHR1X_avg,PMVHR2X_avg')

x=mta_db_get_add(outfile='mups_2a.fits',ter_cols='_pcm01t_avg,_pcm02t_avg,_pcm03t_avg,_pcm04t_avg,_pfdm101t_avg,_pfdm102t_avg,_pfdm201t_avg,_pfdm202t_avg,_pffp01t_avg,_pftank1t_avg,_pftank2t_avg,_pftankip_avg,_pftankop_avg,_phetankp_avg,_phetankt_avg,_phofp1t_avg,_pxdm01t_avg,_pxdm02t_avg,_pxtank1t_avg,_pxtank2t_avg,_pxtankip_avg,_pxtankop_avg')
x=mta_db_get_add(outfile='mups_2b.fits',ter_cols='_pline01t_avg,_pline02t_avg,_pline03t_avg,_pline04t_avg,_pline05t_avg,_pline06t_avg,_pline07t_avg,_pline08t_avg,_pline09t_avg,_pline10t_avg,_pline11t_avg,_pline12t_avg,_pline13t_avg,_pline14t_avg,_pline15t_avg,_pline16t_avg')

###########dtrend,'mups.fits',wsmooth=30
###########tmp_save,'mups.fits','mups_sa.fits',n_out=-1,merge='pt_suncent.fits'
###########dtrend,'mups_sa.fits',wsmooth=30
tmp_save,'mups_2b.fits','mups_att.fits',n_out=-1,merge='pt_suncent.fits'
dtrend,'mups_att.fits',xax='pt_suncent_ang', ccode='time'

exit
