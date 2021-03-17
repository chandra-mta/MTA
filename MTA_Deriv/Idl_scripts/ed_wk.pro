wk_start=cxtime('2010-08-16T00:00:00','cal','sec')
wk_end=cxtime('2010-08-23T00:00:00','cal','sec')
; what happens to weekkly_dir, need to reset after each dtrend_wk call?????
weekly_dir='/data/mta4/www/DAILY/mta_deriv/081610'
spawn,"mkdir "+weekly_dir
x=mta_db_get(outfile='pt_suncent_wk.fits',ter_cols='pt_suncent_ang,sc_altitude',timestart=wk_start,timestop=wk_end)

x=mta_db_get(outfile='ephtv_wk.fits',ter_cols='_5eiot_avg,_5ephint_avg,_hkabiasleaki_avg,_hkbbiasleaki_avg,_hkcbiasleaki_avg,_hkdbiasleaki_avg,_hkebiasleaki_avg,_hkeboxtemp_avg,_hkfbiasleaki_avg,_hkghv_avg,_hkn6i_avg,_hkn6v_avg,_hkp27i_avg,_hkp27v_avg,_hkp5i_avg,_hkp5v_avg,_hkp6i_avg,_hkp6v_avg,_teio_avg,_tephin_avg',timestart=wk_start,timestop=wk_end)
weekly_dir='/data/mta4/www/DAILY/mta_deriv/081610'
dtrend_wk,'ephtv_wk.fits',wsmooth=30,outdir=weekly_dir
;tmp_save,'ephtv_wk.fits','ephtv_att_wk.fits',n_out=-1,merge='pt_suncent_wk.fits'
;dtrend,'ephtv_att_wk.fits',xax='pt_suncent_ang', ccode='time'
weekly_dir='/data/mta4/www/DAILY/mta_deriv/081610'


x=mta_db_get(outfile='hrmatherm_wk.fits',ter_cols='_4rt555t_avg,_4rt556t_avg,_4rt557t_avg,_4rt558t_avg,_4rt559t_avg,_4rt560t_avg,_4rt561t_avg,_4rt562t_avg,_4rt563t_avg,_4rt564t_avg,_4rt565t_avg,_4rt567t_avg,_4rt568t_avg,_4rt569t_avg,_4rt570t_avg,_4rt575t_avg,_4rt576t_avg,_4rt577t_avg,_4rt578t_avg,_4rt579t_avg,_4rt580t_avg,_4rt581t_avg',timestart=wk_start,timestop=wk_end)
weekly_dir='/data/mta4/www/DAILY/mta_deriv/081610'
dtrend_wk,'hrmatherm_wk.fits',wsmooth=30, outdir=weekly_dir
x=mta_db_get(outfile='hrmastruts_wk.fits',ter_cols='_4rt582t_avg,_4rt583t_avg,_4rt584t_avg,_4rt585t_avg,_4rt586t_avg,_4rt587t_avg,_4rt588t_avg,_4rt589t_avg,_4rt590t_avg,_4rt591t_avg,_4rt592t_avg,_4rt593t_avg,_4rt594t_avg,_4rt595t_avg,_4rt596t_avg,_4rt597t_avg,_4rt598t_avg',timestart=wk_start,timestop=wk_end)
weekly_dir='/data/mta4/www/DAILY/mta_deriv/081610'
dtrend_wk,'hrmastruts_wk.fits',wsmooth=30, outdir=weekly_dir
x=mta_db_get(outfile='obfwdbulkhead_wk.fits',ter_cols='_4rt700t_avg,_4rt701t_avg,_4rt702t_avg,_4rt703t_avg,_4rt704t_avg,_4rt705t_avg,_4rt706t_avg,_4rt707t_avg,_4rt708t_avg,_4rt709t_avg,_4rt710t_avg,_4rt711t_avg',timestart=wk_start,timestop=wk_end)
weekly_dir='/data/mta4/www/DAILY/mta_deriv/081610'
dtrend_wk,'obfwdbulkhead_wk.fits',wsmooth=30, outdir=weekly_dir
x=mta_db_get(outfile='precoll_wk.fits',ter_cols='_4prt1at_avg,_4prt1bt_avg,_4prt2at_avg,_4prt2bt_avg,_4prt3at_avg,_4prt3bt_avg,_4prt4at_avg,_4prt4bt_avg,_4prt5at_avg,_4prt5bt_avg',timestart=wk_start,timestop=wk_end)
weekly_dir='/data/mta4/www/DAILY/mta_deriv/081610'
dtrend_wk,'precoll_wk.fits',wsmooth=30, outdir=weekly_dir

;;obaheaters
x=mta_db_get(outfile='obaheaters_wk.fits',ter_cols='_oobthr01_avg,_oobthr02_avg,_oobthr03_avg,_oobthr04_avg,_oobthr05_avg,_oobthr06_avg,_oobthr07_avg,_oobthr08_avg,_oobthr09_avg,_oobthr10_avg,_oobthr11_avg,_oobthr12_avg,_oobthr13_avg,_oobthr14_avg,_oobthr15_avg,_oobthr16_avg,_oobthr17_avg,_oobthr18_avg,_oobthr19_avg,_oobthr20_avg,_oobthr21_avg,_oobthr22_avg,_oobthr23_avg,_oobthr24_avg,_oobthr25_avg,_oobthr26_avg,_oobthr27_avg,_oobthr28_avg,_oobthr29_avg,_oobthr30_avg,_oobthr31_avg,_oobthr32_avg,_oobthr33_avg,_oobthr34_avg,_oobthr35_avg,_oobthr36_avg,_oobthr37_avg,_oobthr38_avg,_oobthr39_avg,_oobthr40_avg,_oobthr41_avg,_oobthr42_avg,_oobthr43_avg,_oobthr44_avg,_oobthr45_avg,_oobthr46_avg,_oobthr47_avg,_oobthr48_avg,_oobthr49_avg,_oobthr50_avg,_oobthr51_avg,_oobthr52_avg,_oobthr53_avg,_oobthr54_avg,_oobthr55_avg,_oobthr56_avg,_oobthr57_avg,_oobthr58_avg,_oobthr59_avg,_oobthr60_avg,_oobthr61_avg,_oobthr62_avg,_oobthr63_avg,_oobthr64_avg',timestart=wk_start,timestop=wk_end)
weekly_dir='/data/mta4/www/DAILY/mta_deriv/081610'
dtrend_wk,'obaheaters_wk.fits',wsmooth=30,filt_it=2,outdir=weekly_dir
x=mta_db_get(ter_cols='_oobagrd1_avg,_oobagrd2_avg,_oobagrd4_avg,_oobagrd5_avg,_oobagrd7_avg,_oobagrd8_avg',outfile='obagrad_wk.fits',timestart=wk_start,timestop=wk_end)
weekly_dir='/data/mta4/www/DAILY/mta_deriv/081610'
dtrend_wk,'obagrad_wk.fits',wsmooth=30,filt_it=3, outdir=weekly_dir
;;hrmaheaters
x=mta_db_get(outfile='hrmaheaters_wk.fits',ter_cols='_ohrthr01_avg,_ohrthr02_avg,_ohrthr03_avg,_ohrthr04_avg,_ohrthr05_avg,_ohrthr06_avg,_ohrthr07_avg,_ohrthr08_avg,_ohrthr09_avg,_ohrthr10_avg,_ohrthr11_avg,_ohrthr12_avg,_ohrthr13_avg,_ohrthr14_avg,_ohrthr15_avg,_ohrthr16_avg,_ohrthr17_avg,_ohrthr18_avg,_ohrthr19_avg,_ohrthr20_avg,_ohrthr21_avg,_ohrthr22_avg,_ohrthr23_avg,_ohrthr24_avg,_ohrthr25_avg,_ohrthr26_avg,_ohrthr28_avg,_ohrthr29_avg,_ohrthr30_avg,_ohrthr31_avg,_ohrthr32_avg,_ohrthr33_avg,_ohrthr34_avg,_ohrthr35_avg,_ohrthr36_avg,_ohrthr37_avg,_ohrthr38_avg,_ohrthr39_avg,_ohrthr40_avg,_ohrthr41_avg,_ohrthr44_avg,_ohrthr45_avg,_ohrthr46_avg,_ohrthr47_avg,_ohrthr48_avg,_ohrthr49_avg,_ohrthr50_avg,_ohrthr51_avg,_ohrthr52_avg,_ohrthr53_avg,_ohrthr54_avg,_ohrthr55_avg,_ohrthr56_avg,_ohrthr57_avg,_ohrthr58_avg,_ohrthr59_avg,_ohrthr60_avg,_ohrthr61_avg,_ohrthr62_avg,_ohrthr63_avg,_ohrthr64_avg',timestart=wk_start,timestop=wk_end)
weekly_dir='/data/mta4/www/DAILY/mta_deriv/081610'
dtrend_wk,'hrmaheaters_wk.fits',wsmooth=30,filt_it=3, outdir=weekly_dir
x=mta_db_get(outfile='hrmagrad_wk.fits',ter_cols='_ohrmgrd1_avg,_ohrmgrd2_avg,_ohrmgrd3_avg,_ohrmgrd4_avg,_ohrmgrd5_avg,_ohrmgrd6_avg,_ohrmgrd7_avg,_ohrmgrd8_avg',timestart=wk_start,timestop=wk_end)
weekly_dir='/data/mta4/www/DAILY/mta_deriv/081610'
dtrend_wk,'hrmagrad_wk.fits',wsmooth=30,filt_it=3, outdir=weekly_dir

x=mta_db_get(outfile='pcadtemp_wk.fits',ter_cols='_aacbppt_avg,_aacbprt_avg,_aacccdpt_avg,_aacccdrt_avg,_aach1t_avg,_aach2t_avg,_aaotalt_avg,_aaotapmt_avg,_aaotasmt_avg,_aaoth2mt_avg',timestart=wk_start,timestop=wk_end)
weekly_dir='/data/mta4/www/DAILY/mta_deriv/081610'
dtrend_wk,'pcadtemp_wk.fits',wsmooth=30, outdir=weekly_dir
x=mta_db_get(ter_cols='_ohrthr27_avg,_ohrthr42_avg,_ohrthr43_avg,_oobagrd3_avg,_oobagrd6_avg', outfile='pcadftsgrad_wk.fits',timestart=wk_start,timestop=wk_end)
weekly_dir='/data/mta4/www/DAILY/mta_deriv/081610'
dtrend_wk,'pcadftsgrad_wk.fits',wsmooth=30, filt_it=3, outdir=weekly_dir

;;simtemp
x=mta_db_get(outfile='simtemp_wk.fits',ter_cols='_3btu_bpt_avg,_3fabraat_avg,_3fabrcat_avg,_3famyzat_avg,_3fapyzat_avg,_3faralat_avg,_3flcabpt_avg,_3rctubpt_avg,_3tsmxcet_avg,_3tsmxspt_avg,_3tsmydpt_avg,_3tspyfet_avg,_3tspzdet_avg,_3tspzspt_avg,_3ttacs1t_avg,_3ttacs2t_avg,_3ttacs3t_avg,_3ttbrgbt_avg,_3tthrc1t_avg,_3tthrc2t_avg,_3tthrc3t_avg,_3ttralat_avg,_3ttralct_avg,_3ttvalvt_avg,_boxtemp_avg,_famtrtemp_avg,_flexatemp_avg,_flexatset_avg,_flexbtemp_avg,_flexbtset_avg,_flexctemp_avg,_flexctset_avg,_psutemp_avg,_tscmtrtemp_avg',timestart=wk_start,timestop=wk_end)
weekly_dir='/data/mta4/www/DAILY/mta_deriv/081610'
dtrend_wk,'simtemp_wk.fits',wsmooth=10, outdir=weekly_dir


x=mta_db_get(outfile='mups_wk.fits',ter_cols='_pline01t_avg,_pline02t_avg,_pline03t_avg,_pline04t_avg,_pline05t_avg,_pline06t_avg,_pline07t_avg,_pline08t_avg,_pline09t_avg,_pline10t_avg,_pline11t_avg,_pline12t_avg,_pline13t_avg,_pline14t_avg,_pline15t_avg,_pline16t_avg',timestart=wk_start,timestop=wk_end)

weekly_dir='/data/mta4/www/DAILY/mta_deriv/081610'
dtrend_wk,'mups_wk.fits',wsmooth=30, outdir=weekly_dir

;;sc_main_temp
x=mta_db_get(outfile='sc_anc_temp_wk.fits',ter_cols='_tatecdpt_avg,_tatecdrt_avg,_tboltcut_avg,_tcnr_brm_avg,_tesh1_avg,_tesh2_avg,_tfssbkt1_avg,_tfssbkt2_avg,_tfutsupn_avg,_tmyhng_avg,_toxtsupn_avg,_trspmtpc_avg,_trspotep_avg,_trspotex_avg,_trspotpc_avg,_trsprwbb_avg,_trsprwbc_avg,_trsprwcm_avg,_tsciusf1_avg,_tsciusf2_avg,_tsciusf5_avg,_tsciusf8_avg,_tsctsf1_avg,_tsctsf2_avg,_tsctsf3_avg,_tsctsf4_avg,_tsctsf5_avg,_tsctsf6_avg',timestart=wk_start,timestop=wk_end)
x=mta_db_get(outfile='sc_anc_temp_wk.fits',ter_cols='_tfssbkt1_avg,_tfssbkt2_avg',timestart=wk_start,timestop=wk_end)
weekly_dir='/data/mta4/www/DAILY/mta_deriv/081610'
dtrend_wk,'sc_anc_temp_wk.fits',wsmooth=30,outdir=weekly_dir
x=mta_db_get(outfile='sc_main_temp_wk.fits',ter_cols='_tape1pst_avg,_tape2pst_avg,_tapea1t_avg,_tapea2t_avg,_tasppcm_avg,_tasppcp_avg,_tasppcu_avg,_tasprwc_avg,_tcm_ctu_avg,_tcm_ifu_avg,_tcm_obc_avg,_tcm_pa1_avg,_tcm_pa2_avg,_tcm_pan_avg,_tcm_rfas_avg,_tcm_ssr1_avg,_tcm_ssr2_avg,_tcm_tx1_avg,_tcm_tx2_avg,_tcm_uso_avg,_tcylaft1_avg,_tcylaft2_avg,_tcylaft3_avg,_tcylaft4_avg,_tcylaft5_avg,_tcylaft6_avg,_tcylcmm_avg,_tcylfmzm_avg,_tcylfmzp_avg,_tcylpcm_avg,_tcylpcp_avg,_tcylrwc_avg,_tcyz_rw1_avg,_tcyz_rw6_avg,tep_bpan_avg,_tep_eia_avg,_tep_pcu_avg,_tep_ppan_avg,_tep_psu1_avg,_tep_psu2_avg,_tep_rctu_avg,_tfspcmm_avg,_tfspcmp_avg,_tfsppcm_avg,_tfsppcp_avg,_tfsppcu_avg,_tfsprwc_avg,_tmysada_avg,_tmzlgabm_avg,_tmzp_cnt_avg,_tmzp_my_avg,_tmzp_py_avg,_tpcm_rw4_avg,_tpcm_rw5_avg,_tpcp_rw2_avg,_tpcp_rw3_avg,_tpc_cea_avg,_tpc_dea_avg,_tpc_ese_avg,_tpc_fsse_avg,_tpc_pan_avg,_tpc_rctu_avg,_tpc_wda_avg,_tpysada_avg,_tpzlgabm_avg,_tsamyt_avg,_tsapyt_avg',timestart=wk_start,timestop=wk_end)

weekly_dir='/data/mta4/www/DAILY/mta_deriv/081610'
dtrend_wk,'sc_main_temp_wk.fits',wsmooth=30,outdir=weekly_dir

max_pitch_temp_wk
min_pitch_temp_wk
exit
