;;acistemp
;x=mta_db_get(timestart='2000-02-01',outfile='acistemp_sa.fits',ter_cols='_1cbat_avg,_1cbbt_avg,_1crat_avg,_1crbt_avg,_1dactbt_avg,_1deamzt_avg,_1dpamyt_avg,_1dpamzt_avg,_1oahat_avg,_1oahbt_avg,_1pdeaat_avg,_1pdeabt_avg,_1pin1at_avg,_1wrat_avg,_1wrbt_avg,pt_suncent_ang',/debug)
;;;spawn, "dmcopy 'acistemp_sa.fits[cols -pt_suncent_ang]' acistemp.fits"
;;;;x=mta_db_get(timestart='2002_05-01',outfile='acistemp_sa.fits',ter_cols='_1cbat_avg,_1cbbt_avg,_1crat_avg,_1crbt_avg,_1dactbt_avg,_1deamzt_avg,_1dpamyt_avg,_1dpamzt_avg,_1oahat_avg,_1oahbt_avg,_1pdeaat_avg,_1pdeabt_avg,_1pin1at_avg,_1wrat_avg,_1wrbt_avg,AOSARES1,AOSARES2',/debug)
;;;;spawn, "dmcopy 'acistemp_sa.fits[cols -AOSARES1,-AOSARES2]' acistemp.fits"
;dtrend,'acistemp.fits',wsmooth=30
;dtrend,'acistemp_sa.fits',wsmooth=30
;;;;spawn, "cp acistemp_sa.fits acistemp_att.fits"
;dtrend,'acistemp_att.fits',xax='pt_suncent_ang'
;x=mta_db_get(outfile='aciseleca.fits',ter_cols='_1dahacu_avg,_1dahavo_avg,_1dahhavo_avg,_1de28avo_avg,_1deicacu_avg,_1den0avo_avg,_1den1avo_avg,_1dep0avo_avg,_1dep1avo_avg,_1dep2avo_avg,_1dep3avo_avg,_1dp28avo_avg,_1dpicacu_avg,_1dpp0avo_avg', /debug)
;dtrend,'aciseleca.fits',wsmooth=30
;x=mta_db_get(outfile='aciselecb.fits',ter_cols='_1dahbcu_avg,_1dahbvo_avg,_1dahhbvo_avg,_1de28bvo_avg,_1deicbcu_avg,_1den0bvo_avg,_1den1bvo_avg,_1dep0bvo_avg,_1dep1bvo_avg,_1dep2bvo_avg,_1dep3bvo_avg,_1dp28bvo_avg,_1dpicbcu_avg,_1dpp0bvo_avg', /debug)
;dtrend,'aciselecb.fits',wsmooth=30
;x=mta_db_get(ter_cols='mtaacis..acismech_avg',outfile='acismech.fits', /debug)
;dtrend,'acismech.fits',wsmooth=30

;x=mta_db_get(outfile='ephhk.fits',ter_cols='_eiostatus_a_avg,_eiostatus_b_avg,_eiostatus_c_avg,_eiostatus_d_avg,_eiostatus_e_avg,_eiostatus_f_avg,_eiostatus_g_avg,_eiostatus_h_avg,_ephsimstatus_avg,_hkcmdsuccess_avg,_hkretryneed_avg,_hkreturncode_avg,_hktimatimout_avg,_hktimdtimout_avg,_sccmdsuccess_avg,_scretryneed_avg,_screturncode_avg,_tccmdsuccess_avg,_tcnaksent_avg,_tcretryneed_avg,_tcreturncode_avg,_tctimatimout_avg,_tctimdtimout_avg,_telecmdcnt_avg,_telecmdcode_avg')
;dtrend,'ephhk.fits',wsmooth=10
;x=mta_db_get(outfile='ephtv.fits',ter_cols='_5eiot_avg,_5ephint_avg,_hkabiasleaki_avg,_hkbbiasleaki_avg,_hkcbiasleaki_avg,_hkdbiasleaki_avg,_hkebiasleaki_avg,_hkeboxtemp_avg,_hkfbiasleaki_avg,_hkghv_avg,_hkn6i_avg,_hkn6v_avg,_hkp27i_avg,_hkp27v_avg,_hkp5i_avg,_hkp5v_avg,_hkp6i_avg,_hkp6v_avg,_teio_avg,_tephin_avg')
;dtrend,'ephtv.fits',wsmooth=30
;;ephrate
;x=mta_db_get(outfile='ephrate1.fits',ter_cols='_sca00_avg,_sca01_avg,_sca02_avg,_sca03_avg,_sca04_avg,_sca05_avg,_scb00_avg,_scb01_avg,_scb02_avg,_scb04_avg,_scb05_avg,_scc0_avg,_scct1_avg,_scct2_avg,_scct3_avg,_scct4_avg,_scct5_avg,_scd0_avg,_sce0_avg,_scf0_avg,_scg0_avg,_sch25gr_avg')
;x=mta_db_get(outfile='ephrate2.fits',ter_cols='_sch25s1_avg,_sch25s23_avg,_sch41gr_avg,_sch41s1_avg,_sch41s23_avg,_sch4gr_avg,_sch4s1_avg,_sch4s23_avg,_sch8gr_avg,_sch8s1_avg,_sch8s23_avg,_scp25gr_avg,_scp25s_avg,_scp41gr_avg,_scp41s_avg,_scp4gr_avg,_scp4s_avg,_scp8gr_avg,_scp8s_avg')
;dtrend,'ephrate.fits',wsmooth=30
;x=mta_db_get(outfile='ephkey.fits',ter_cols='_scct0_avg,_sce1300_avg,_sce150_avg,_sce300_avg,_sce3000_avg,_sch25gm_avg,_sch41gm_avg,_sch4gm_avg,_sch8gm_avg,_scint_avg,_scp25gm_avg,_scp41gm_avg,_scp4gm_avg,_scp8gm_avg')
;dtrend,'ephkey.fits',wsmooth=30
;x=mta_db_get(outfile='ephtvkey.fits',ter_cols='_hkabiasleaki_avg,_hkbbiasleaki_avg,_hkcbiasleaki_avg,_hkdbiasleaki_avg,_hkebiasleaki_avg,_hkeboxtemp_avg,_hkfbiasleaki_avg,_teio_avg,_tephin_avg,_hkp27i_avg,_sce1300_avg,_sce150_avg,_scp41gm_avg,_scp4gm_avg')
;dtrend,'ephtvkey.fits',xax='tephin'

;x=mta_db_get(ter_cols='mtatel..gratgen_avg',outfile='gratgen.fits')
;dtrend,'gratgen.fits',wsmooth=180

;x=mta_db_get(outfile='hrctemp.fits',ter_cols='_2ceahvpt_avg,_2chtrpzt_avg,_2condmxt_avg,_2dcentrt_avg,_2dtstatt_avg,_2fhtrmzt_avg,_2fradpyt_avg,_2pmt1t_avg,_2pmt2t_avg,_2uvlspxt_avg', /debug)
;dtrend,'hrctemp.fits',wsmooth=10
;hrcelec
;  following includes temporary workaround (extra \ before ') for 
;   a dataseeker bug
;x=mta_db_get(outfile='hrcelec_i.fits',prim="SI=\'HRC-I\',CORADMEN=\'ENAB\',CCSDSTMF=\'FMT1\'",ter_cols='_2detart_avg,_2detbrt_avg,_calpalv_avg,_cbhuast_avg,_cbhvast_avg,_cbluast_avg,_cblvast_avg,_fcpuast_avg,_fcpvast_avg,_hvpsstat_avg,_imbpast_avg,_imhblv_avg,_imhvlv_avg,_imtpast_avg,_lldialv_avg,_mlswenbl_avg,_mlswstat_avg,_mtrcmndr_avg,_mtritmp_avg,_mtrselct_avg,_mtrstatr_avg,_n15cast_avg,_p15cast_avg,_p24cast_avg,_rsrfalv_avg,_s1hvlv_avg,_s1hvst_avg,_s2hvlv_avg,_s2hvst_avg,_scidpren_avg,_scthast_avg,_spbpast_avg,_sphblv_avg,_sphvlv_avg,_sptpast_avg,_wdthast_avg',/debug)
;dtrend,'hrcelec_i.fits'
;x=mta_db_get(outfile='hrcelec_s.fits',prim="SI=\'HRC-S\',CORADMEN=\'ENAB\',CCSDSTMF=\'FMT1\'",ter_cols='_2detart_avg,_2detbrt_avg,_calpalv_avg,_cbhuast_avg,_cbhvast_avg,_cbluast_avg,_cblvast_avg,_fcpuast_avg,_fcpvast_avg,_hvpsstat_avg,_imbpast_avg,_imhblv_avg,_imhvlv_avg,_imtpast_avg,_lldialv_avg,_mlswenbl_avg,_mlswstat_avg,_mtrcmndr_avg,_mtritmp_avg,_mtrselct_avg,_mtrstatr_avg,_n15cast_avg,_p15cast_avg,_p24cast_avg,_rsrfalv_avg,_s1hvlv_avg,_s1hvst_avg,_s2hvlv_avg,_s2hvst_avg,_scidpren_avg,_scthast_avg,_spbpast_avg,_sphblv_avg,_sphvlv_avg,_sptpast_avg,_wdthast_avg',/debug)
;dtrend,'hrcelec_s.fits'
;x=mta_db_get(outfile='hrcelec_ai.fits',prim="SI=\'ACIS-I\',CORADMEN=\'ENAB\'",ter_cols='_2detart_avg,_2detbrt_avg,_calpalv_avg,_cbhuast_avg,_cbhvast_avg,_cbluast_avg,_cblvast_avg,_fcpuast_avg,_fcpvast_avg,_hvpsstat_avg,_imbpast_avg,_imhblv_avg,_imhvlv_avg,_imtpast_avg,_lldialv_avg,_mlswenbl_avg,_mlswstat_avg,_mtrcmndr_avg,_mtritmp_avg,_mtrselct_avg,_mtrstatr_avg,_n15cast_avg,_p15cast_avg,_p24cast_avg,_rsrfalv_avg,_s1hvlv_avg,_s1hvst_avg,_s2hvlv_avg,_s2hvst_avg,_scidpren_avg,_scthast_avg,_spbpast_avg,_sphblv_avg,_sphvlv_avg,_sptpast_avg,_wdthast_avg',/debug)
;x=mta_db_get(outfile='hrcelec_as.fits',prim="SI=\'ACIS-S\',CORADMEN=\'ENAB\'",ter_cols='_2detart_avg,_2detbrt_avg,_calpalv_avg,_cbhuast_avg,_cbhvast_avg,_cbluast_avg,_cblvast_avg,_fcpuast_avg,_fcpvast_avg,_hvpsstat_avg,_imbpast_avg,_imhblv_avg,_imhvlv_avg,_imtpast_avg,_lldialv_avg,_mlswenbl_avg,_mlswstat_avg,_mtrcmndr_avg,_mtritmp_avg,_mtrselct_avg,_mtrstatr_avg,_n15cast_avg,_p15cast_avg,_p24cast_avg,_rsrfalv_avg,_s1hvlv_avg,_s1hvst_avg,_s2hvlv_avg,_s2hvst_avg,_scidpren_avg,_scthast_avg,_spbpast_avg,_sphblv_avg,_sphvlv_avg,_sptpast_avg,_wdthast_avg',/debug)
;x=mta_db_get(outfile='hrcelec_off.fits',prim="CORADMEN=\'DISA\'",ter_cols='_2detart_avg,_2detbrt_avg,_calpalv_avg,_cbhuast_avg,_cbhvast_avg,_cbluast_avg,_cblvast_avg,_fcpuast_avg,_fcpvast_avg,_hvpsstat_avg,_imbpast_avg,_imhblv_avg,_imhvlv_avg,_imtpast_avg,_lldialv_avg,_mlswenbl_avg,_mlswstat_avg,_mtrcmndr_avg,_mtritmp_avg,_mtrselct_avg,_mtrstatr_avg,_n15cast_avg,_p15cast_avg,_p24cast_avg,_rsrfalv_avg,_s1hvlv_avg,_s1hvst_avg,_s2hvlv_avg,_s2hvst_avg,_scidpren_avg,_scthast_avg,_spbpast_avg,_sphblv_avg,_sphvlv_avg,_sptpast_avg,_wdthast_avg',/debug)
;dtrend,'hrcelec_off.fits'
;;dtrend,'hrcelec.fits',wsmooth=10
;x=mta_db_get(prim="SI=\'ACIS-I\',CORADMEN=\'ENAB\'",ter_cols='mtahrc..hrcveto_avg',outfile='hrcveto_ai.fits',/debug)
;x=mta_db_get(prim="SI=\'ACIS-S\',CORADMEN=\'ENAB\'",ter_cols='mtahrc..hrcveto_avg',outfile='hrcveto_as.fits',/debug)
;x=mta_db_get(prim="SI=\'HRC-I\',CORADMEN=\'ENAB\',CCSDSTMF=\'FMT1\'",ter_cols='mtahrc..hrcveto_avg',outfile='hrcveto_i.fits',/debug)
;x=mta_db_get(prim="SI=\'HRC-S\',CORADMEN=\'ENAB\',CCSDSTMF=\'FMT1\'",ter_cols='mtahrc..hrcveto_avg',outfile='hrcveto_s.fits',/debug)
;x=mta_db_get(prim="CORADMEN=\'DISA\'",ter_cols='mtahrc..hrcveto_avg',outfile='hrcveto_off.fits',/debug)
;dtrend,'hrcveto.fits',wsmooth=30
;x=mta_db_get(outfile='hrchk.fits',ter_cols='_c05palv_avg,_c15nalv_avg,_c15palv_avg,_c24palv_avg,_fe00atm_avg,_fepratm_avg,_imhvatm_avg,_iminatm_avg,_lvplatm_avg,_prbscr_avg,_prbsvl_avg,_smtratm_avg,_sphvatm_avg,_spinatm_avg',/debug)
;dtrend,'hrchk.fits',wsmooth=10

;x=mta_db_get(outfile='pcadtemp.fits',ter_cols='_aacbppt_avg,_aacbprt_avg,_aacccdpt_avg,_aacccdrt_avg,_aach1t_avg,_aach2t_avg,_aaotalt_avg,_aaotapmt_avg,_aaotasmt_avg,_aaoth2mt_avg')
;dtrend,'pcadtemp.fits',wsmooth=30
;x=mta_db_get(outfile='pcaditv.fits',ter_cols='_afsspc1v_avg,_afsspc2v_avg,_agws1v_avg,_agws2v_avg,_airu1bt_avg,_airu1g1i_avg,_airu1g1t_avg,_airu1g2i_avg,_airu1g2t_avg,_airu1vft_avg,_airu2bt_avg,_airu2g1i_avg,_airu2g1t_avg,_airu2g2i_avg,_airu2g2t_avg,_airu2vft_avg,_aocssi1_avg,_aocssi2_avg,_aocssi3_avg,_aocssi4_avg')
;dtrend,'pcaditv.fits',wsmooth=30
;;;pcadgrate
;x=mta_db_get(outfile='pcadgrate1.fits',ter_cols='_ai1ax1x_avg,_ai1ax1y_avg,_ai1ax2x_avg,_ai1ax2y_avg,_ai2ax1x_avg,_ai2ax1y_avg,_ai2ax2x_avg,_ai2ax2y_avg,_aoalpang_avg,_aoattqt1_avg,_aoattqt2_avg,_aoattqt3_avg,_aoattqt4_avg,_aobetang_avg')
;x=mta_db_get(outfile='pcadgrate2.fits',ter_cols='_aocmdqt1_avg,_aocmdqt2_avg,_aocmdqt3_avg,_aoscpos1_avg,_aoscpos2_avg,_aoscpos3_avg,_aoscvel1_avg,_aoscvel2_avg,_aoscvel3_avg,_aosunec1_avg,_aosunec2_avg,_aosunec3_avg,_aosunsa1_avg,_aosunsa2_avg,_aosunsa3_avg,_aotarqt1_avg,_aotarqt2_avg,_aotarqt3_avg')
;dtrend,'pcadgrate.fits',wsmooth=30
;x=mta_db_get(ter_cols='mtapcad..pcadftsgrad_avg',outfile='pcadftsgrad.fits')
;dtrend,'pcadftsgrad.fits',wsmooth=30, filt_it=3
;x=mta_db_get(outfile='pcadrwrate.fits',ter_cols='_aorwcmd1_avg,_aorwcmd2_avg,_aorwcmd3_avg,_aorwcmd4_avg,_aorwcmd5_avg,_aorwcmd6_avg,_aorwcnt1_avg,_aorwcnt2_avg,_aorwcnt3_avg,_aorwcnt4_avg,_aorwcnt5_avg,_aorwcnt6_avg,_aorwmc1_avg,_aorwmc4_avg,_aorwmc5_avg,_aorwspd1_avg,_aorwspd2_avg,_aorwspd3_avg,_aorwspd4_avg,_aorwspd5_avg,_aorwspd6_avg')
;dtrend,'pcadrwrate.fits',wsmooth=30, filt_it=1
;x=mta_db_get(ter_cols='mtapcad..pcadgdrift_avg',outfile='pcadgdrift.fits')
;dtrend,'pcadgdrift.fits',wsmooth=30, filt_it=1

;;simtemp
;x=mta_db_get(outfile='pt_suncent.fits',ter_cols='pt_suncent_ang')
;x=mta_db_get(outfile='simtemp1.fits',ter_cols='_3btu_bpt_avg,_3fabraat_avg,_3fabrcat_avg,_3famyzat_avg,_3fapyzat_avg,_3faralat_avg,_3flcabpt_avg,_3rctubpt_avg,_3tsmxcet_avg,_3tsmxspt_avg,_3tsmydpt_avg,_3tspyfet_avg,_3tspzdet_avg,_3tspzspt_avg,_3ttacs1t_avg,_3ttacs2t_avg,_3ttacs3t_avg,_3ttbrgbt_avg')
;x=mta_db_get(outfile='simtemp2.fits',ter_cols='_3tthrc1t_avg,_3tthrc2t_avg,_3tthrc3t_avg,_3ttralat_avg,_3ttralct_avg,_3ttvalvt_avg,_boxtemp_avg,_famtrtemp_avg,_flexatemp_avg,_flexatset_avg,_flexbtemp_avg,_flexbtset_avg,_flexctemp_avg,_flexctset_avg,_psutemp_avg,_tscmtrtemp_avg')
;dtrend,'simtemp.fits',wsmooth=10
;x=mta_db_get(outfile='simelec.fits',ter_cols='_agrndadc_avg,_fatabadc_avg,_n15vadc_avg,_p15vadc_avg,_p5vadc_avg,_tsctabadc_avg')
;dtrend,'simelec.fits',wsmooth=10, filt_it=2
;x=mta_db_get(outfile='simactu.fits',ter_cols='_faedge_avg,_fapos_avg,_fatabwid_avg,_ldrtnum_avg,_ldrtrelpos_avg,_mrmdest_avg,_pwmlevel_avg,_tscedge_avg,_tscpos_avg,_tsctabwid_avg')
;dtrend,'simactu.fits',wsmooth=10

;x=mta_db_get(outfile='epsbatt.fits',ter_cols='_eb1ci_avg,_eb1di_avg,_eb1v_avg,_eb2ci_avg,_eb2di_avg,_eb2v_avg,_eb3ci_avg,_eb3di_avg,_eb3v_avg,_ecnv1v_avg,_ecnv2v_avg,_ecnv3v_avg,_eepa5v_avg,_eepb5v_avg,_eochrgb1_avg,_eochrgb2_avg,_eochrgb3_avg,_eoeb1cic_avg,_eoeb1dic_avg,_eoeb1vc_avg,_eoeb2cic_avg,_eoeb2vc_avg,_eoeb3cic_avg,_eoeb3vc_avg,_eoecnv1c_avg,_eoecnv2c_avg,_eoecnv3c_avg,_eoesac1c_avg,_eoesac2c_avg')
;dtrend,'epsbatt.fits',wsmooth=30

;;sc_main_temp
;x=mta_db_get(outfile='sc_main_temp1a.fits',ter_cols='_tape1pst_avg,_tape2pst_avg,_tapea1t_avg,_tapea2t_avg,_tasppcm_avg,_tasppcp_avg,_tasppcu_avg,_tasprwc_avg,_tcm_ctu_avg,_tcm_ifu_avg,_tcm_obc_avg,_tcm_pa1_avg,_tcm_pa2_avg,_tcm_pan_avg,_tcm_rfas_avg,_tcm_ssr1_avg,_tcm_ssr2_avg')
;x=mta_db_get(outfile='sc_main_temp1b.fits',ter_cols='_tcm_tx1_avg,_tcm_tx2_avg,_tcm_uso_avg,_tcylaft1_avg,_tcylaft2_avg,_tcylaft3_avg,_tcylaft4_avg,_tcylaft5_avg,_tcylaft6_avg,_tcylcmm_avg,_tcylfmzm_avg,_tcylfmzp_avg,_tcylpcm_avg,_tcylpcp_avg,_tcylrwc_avg,_tcyz_rw1_avg,_tcyz_rw6_avg')
;x=mta_db_get(outfile='sc_main_temp2a.fits',ter_cols='_tep_bpan_avg,_tep_eia_avg,_tep_pcu_avg,_tep_ppan_avg,_tep_psu1_avg,_tep_psu2_avg,_tep_rctu_avg,_tfspcmm_avg,_tfspcmp_avg,_tfsppcm_avg,_tfsppcp_avg,_tfsppcu_avg,_tfsprwc_avg,_tmysada_avg,_tmzlgabm_avg')
;x=mta_db_get(outfile='sc_main_temp2b.fits',ter_cols='_tmzp_cnt_avg,_tmzp_my_avg,_tmzp_py_avg,_tpcm_rw4_avg,_tpcm_rw5_avg,_tpcp_rw2_avg,_tpcp_rw3_avg,_tpc_cea_avg,_tpc_dea_avg,_tpc_ese_avg,_tpc_fsse_avg,_tpc_pan_avg,_tpc_rctu_avg,_tpc_wda_avg,_tpysada_avg,_tpzlgabm_avg,_tsamyt_avg,_tsapyt_avg')
;dtrend,'sc_main_temp.fits',wsmooth=30
;x=mta_db_get(outfile='sc_anc_temp1.fits',ter_cols='_tatecdpt_avg,_tatecdrt_avg,_tboltcut_avg,_tcnr_brm_avg,_tesh1_avg,_tesh2_avg,_tfssbkt1_avg,_tfssbkt2_avg,_tfutsupn_avg,_tmyhng_avg,_toxtsupn_avg,_trspmtpc_avg,_trspotep_avg,_trspotex_avg')
;x=mta_db_get(outfile='sc_anc_temp2.fits',ter_cols='_trspotpc_avg,_trsprwbb_avg,_trsprwbc_avg,_trsprwcm_avg,_tsciusf1_avg,_tsciusf2_avg,_tsciusf5_avg,_tsciusf8_avg,_tsctsf1_avg,_tsctsf2_avg,_tsctsf3_avg,_tsctsf4_avg,_tsctsf5_avg,_tsctsf6_avg')
;dtrend,'sc_anc_temp.fits',wsmooth=30
;x=mta_db_get(outfile='batt_temp.fits',ter_cols='_tb1t1_avg,_tb1t2_avg,_tb1t3_avg,_tb2t1_avg,_tb2t2_avg,_tb2t3_avg,_tb3t1_avg,_tb3t2_avg,_tb3t3_avg')
;dtrend,'batt_temp.fits',wsmooth=30
;x=mta_db_get(outfile='spcelec1.fits',ter_cols='_ade1p5cv_avg,_ade2p5cv_avg,_ahknatpr_avg,_ahknatrd_avg,_avacmonv_avg,_avd1cv5v_avg,_avd2cv5v_avg,_awd1cv5v_avg,_awd1tqi_avg,_awd2cv5v_avg,_awd2tqi_avg,_awd3cv5v_avg,_awd3tqi_avg,_awd4cv5v_avg')
;x=mta_db_get(outfile='spcelec2.fits',ter_cols='_awd4tqi_avg,_awd5cv5v_avg,_awd5tqi_avg,_awd6cv5v_avg,_awd6tqi_avg,_cveep_avg,_cveer_avg,_edissnpr_avg,_elbi_avg,_elbv_avg,_epovspr_avg,_es1p5cv_avg,_es2p5cv_avg,_esamyi_avg,_esapyi_avg,_euvsenpr_avg,_obattpwr_avg,_ohrmapwr_avg,_oobapwr_avg')
;dtrend,'spcelec.fits',wsmooth=30
;spceleca
;x=mta_db_get(outfile='spceleca1.fits',ter_cols='_acpa5cv_avg,_aflc10ai_avg,_aflc11ai_avg,_aflc12ai_avg,_aflc13ai_avg,_aflc14ai_avg,_aflca1ai_avg,_aflca2ai_avg,_aflca3ai_avg,_aflca4ai_avg,_aflca5ai_avg,_aflca6ai_avg,_aflca7ai_avg,_aflca8ai_avg,_aflca9ai_avg,_aflcaah_avg,_aioap5cv_avg,_aovapwr_avg,_aspea5cv_avg')
;x=mta_db_get(outfile='spceleca2.fits',ter_cols='_c28vmona_avg,_ciua15v_avg,_ciua5v_avg,_cpa1pwr_avg,_cpa1v_avg,_cpa2pwr_avg,_cpa2v_avg,_cpca15v_avg,_cpca5v_avg,_crxav_avg,_csita15v_avg,_csita5v_avg,_cssr1cav_avg,_ctsa15v_avg,_ctsa5v_avg,_ctua15v_avg,_ctua5v_avg,_ctxapwr_avg,_ctxav_avg,_cusoa28v_avg,_cxo5voba_avg,_eiacvav_avg,_epa15v_avg')
;dtrend,'spceleca.fits',wsmooth=30
;;;spcelecb
;x=mta_db_get(outfile='spcelecb1.fits',ter_cols='_acpb5cv_avg,_aflc10bi_avg,_aflc11bi_avg,_aflc12bi_avg,_aflc13bi_avg,_aflc14bi_avg,_aflca1bi_avg,_aflca2bi_avg,_aflca3bi_avg,_aflca4bi_avg,_aflca5bi_avg,_aflca6bi_avg,_aflca7bi_avg,_aflca8bi_avg,_aflca9bi_avg,_aflcabh_avg')
;x=mta_db_get(outfile='spcelecb2.fits',ter_cols='_aiobp5cv_avg,_aovbpwr_avg,_aspeb5cv_avg,_c28vmonb_avg,_ciub15v_avg,_ciub5v_avg,_cpcb15v_avg,_cpcb5v_avg,_crxbv_avg,_csitb15v_avg,_csitb5v_avg,_cssr2cbv_avg,_ctsb15v_avg,_ctsb5v_avg,_ctub15v_avg,_ctub5v_avg,_ctxbpwr_avg,_ctxbv_avg,_cusob28v_avg,_cxo5vobb_avg,_eiacvbv_avg,_epb15v_avg')
;dtrend,'spcelecb.fits',wsmooth=30

;;obaheaters
;x=mta_db_get(outfile='obaheaters1.fits',ter_cols='_oobthr01_avg,_oobthr02_avg,_oobthr03_avg,_oobthr04_avg,_oobthr05_avg,_oobthr06_avg,_oobthr07_avg,_oobthr08_avg,_oobthr09_avg,_oobthr10_avg,_oobthr11_avg,_oobthr12_avg,_oobthr13_avg,_oobthr14_avg,_oobthr15_avg')
;x=mta_db_get(outfile='obaheaters2.fits',ter_cols='_oobthr16_avg,_oobthr17_avg,_oobthr18_avg,_oobthr19_avg,_oobthr20_avg,_oobthr21_avg,_oobthr22_avg,_oobthr23_avg,_oobthr24_avg,_oobthr25_avg,_oobthr26_avg,_oobthr27_avg,_oobthr28_avg,_oobthr29_avg,_oobthr30_avg,_oobthr31_avg,_oobthr32_avg')
;x=mta_db_get(outfile='obaheaters3.fits',ter_cols='_oobthr33_avg,_oobthr34_avg,_oobthr35_avg,_oobthr36_avg,_oobthr37_avg,_oobthr38_avg,_oobthr39_avg,_oobthr40_avg,_oobthr41_avg,_oobthr42_avg,_oobthr43_avg,_oobthr44_avg,_oobthr45_avg,_oobthr46_avg,_oobthr47_avg')
;x=mta_db_get(outfile='obaheaters4.fits',ter_cols='_oobthr48_avg,_oobthr49_avg,_oobthr50_avg,_oobthr51_avg,_oobthr52_avg,_oobthr53_avg,_oobthr54_avg,_oobthr55_avg,_oobthr56_avg,_oobthr57_avg,_oobthr58_avg,_oobthr59_avg,_oobthr60_avg,_oobthr61_avg,_oobthr62_avg,_oobthr63_avg,_oobthr64_avg')
;dtrend,'obaheaters.fits',wsmooth=30,filt_it=3,/avg_only
;x=mta_db_get(ter_cols='mtatel..obagrad_avg',outfile='obagrad.fits')
;dtrend,'obagrad.fits',wsmooth=30,filt_it=3,/avg_only
;;hrmaheaters
;x=mta_db_get(outfile='hrmaheaters1.fits',ter_cols='_ohrthr01_avg,_ohrthr02_avg,_ohrthr03_avg,_ohrthr04_avg,_ohrthr05_avg,_ohrthr06_avg,_ohrthr07_avg,_ohrthr08_avg,_ohrthr09_avg,_ohrthr10_avg,_ohrthr11_avg,_ohrthr12_avg,_ohrthr13_avg,_ohrthr14_avg')
;x=mta_db_get(outfile='hrmaheaters2.fits',ter_cols='_ohrthr15_avg,_ohrthr16_avg,_ohrthr17_avg,_ohrthr18_avg,_ohrthr19_avg,_ohrthr20_avg,_ohrthr21_avg,_ohrthr22_avg,_ohrthr23_avg,_ohrthr24_avg,_ohrthr25_avg,_ohrthr26_avg,_ohrthr28_avg,_ohrthr29_avg,_ohrthr30_avg,_ohrthr31_avg,_ohrthr32_avg')
;x=mta_db_get(outfile='hrmaheaters3.fits',ter_cols='_ohrthr33_avg,_ohrthr34_avg,_ohrthr35_avg,_ohrthr36_avg,_ohrthr37_avg,_ohrthr38_avg,_ohrthr39_avg,_ohrthr40_avg,_ohrthr41_avg,_ohrthr44_avg,_ohrthr45_avg,_ohrthr46_avg,_ohrthr47_avg,_ohrthr48_avg,_ohrthr49_avg,_ohrthr50_avg')
;x=mta_db_get(outfile='hrmaheaters4.fits',ter_cols='_ohrthr51_avg,_ohrthr52_avg,_ohrthr53_avg,_ohrthr54_avg,_ohrthr55_avg,_ohrthr56_avg,_ohrthr57_avg,_ohrthr58_avg,_ohrthr59_avg,_ohrthr60_avg,_ohrthr61_avg,_ohrthr62_avg,_ohrthr63_avg,_ohrthr64_avg')
;dtrend,'hrmaheaters.fits',wsmooth=30,filt_it=3,/avg_only
;x=mta_db_get(ter_cols='mtatel..hrmagrad_avg',outfile='hrmagrad.fits')
;dtrend,'hrmagrad.fits',wsmooth=30,filt_it=3,/avg_only

;x=mta_db_get(outfile='hrmatherm.fits',ter_cols='_4rt555t_avg,_4rt556t_avg,_4rt557t_avg,_4rt558t_avg,_4rt559t_avg,_4rt560t_avg,_4rt561t_avg,_4rt562t_avg,_4rt563t_avg,_4rt564t_avg,_4rt565t_avg,_4rt567t_avg,_4rt568t_avg,_4rt569t_avg,_4rt570t_avg,_4rt575t_avg,_4rt576t_avg,_4rt577t_avg,_4rt578t_avg,_4rt579t_avg,_4rt580t_avg,_4rt581t_avg')
;dtrend,'hrmatherm.fits',wsmooth=30
;x=mta_db_get(outfile='hrmastruts.fits',ter_cols='_4rt582t_avg,_4rt583t_avg,_4rt584t_avg,_4rt585t_avg,_4rt586t_avg,_4rt587t_avg,_4rt588t_avg,_4rt589t_avg,_4rt590t_avg,_4rt591t_avg,_4rt592t_avg,_4rt593t_avg,_4rt594t_avg,_4rt595t_avg,_4rt596t_avg,_4rt597t_avg,_4rt598t_avg')
;dtrend,'hrmastruts.fits',wsmooth=30
;x=mta_db_get(outfile='obfwdbulkhead.fits',ter_cols='_4rt700t_avg,_4rt701t_avg,_4rt702t_avg,_4rt703t_avg,_4rt704t_avg,_4rt705t_avg,_4rt706t_avg,_4rt707t_avg,_4rt708t_avg,_4rt709t_avg,_4rt710t_avg,_4rt711t_avg')
;dtrend,'obfwdbulkhead.fits',wsmooth=30
;x=mta_db_get(outfile='precoll.fits',ter_cols='_4prt1at_avg,_4prt1bt_avg,_4prt2at_avg,_4prt2bt_avg,_4prt3at_avg,_4prt3bt_avg,_4prt4at_avg,_4prt4bt_avg,_4prt5at_avg,_4prt5bt_avg')
;dtrend,'precoll.fits',wsmooth=30

;obsolete;;specialprocessing
;obsolete;;elbi_low
;obsolete;dtrend,'elbi_low.fits',wsmooth=30
;obsolete;;gratingsmoves
;obsolete;dtrend_otg
;obsolete;dtrend,'letg_in.fits',wsmooth=180,sig=100
;obsolete;dtrend,'letg_re.fits',wsmooth=180,sig=100
;obsolete;dtrend,'hetg_in.fits',wsmooth=180,sig=100
;obsolete;dtrend,'hetg_re.fits',wsmooth=180,sig=100

;;COMPS
dtrend,'compaciscent.fits',wsmooth=90
dtrend,'compacispwr.fits',wsmooth=90
dtrend,'compephkey.fits',wsmooth=90
dtrend,'compgradkodak.fits',wsmooth=90
dtrend,'compsimoffsetb.fits',wsmooth=90
;
dtrend,'gradablk.fits',wsmooth=90,sig=1,filt_it=2
;dtrend,'gradahet.fits',wsmooth=90,sig=1,filt_it=2
dtrend,'gradaincyl.fits',wsmooth=90,sig=1,filt_it=2
dtrend,'gradcap.fits',wsmooth=90,sig=1,filt_it=2
dtrend,'gradfap.fits',wsmooth=90,sig=1,filt_it=2
dtrend,'gradfblk.fits',wsmooth=90,sig=1,filt_it=2
dtrend,'gradhcone.fits',wsmooth=90,sig=1,filt_it=2
dtrend,'gradhhflex.fits',wsmooth=90,sig=1,filt_it=2
dtrend,'gradhpflex.fits',wsmooth=90,sig=1,filt_it=2
dtrend,'gradhstrut.fits',wsmooth=90,sig=1,filt_it=2
dtrend,'gradocyl.fits',wsmooth=90,sig=1,filt_it=2
dtrend,'gradpcolb.fits',wsmooth=90,sig=1,filt_it=2
dtrend,'gradperi.fits',wsmooth=90,sig=1,filt_it=2
dtrend,'gradsstrut.fits',wsmooth=90,sig=1,filt_it=2
dtrend,'gradtfte.fits',wsmooth=90,sig=1,filt_it=2

;;SCI
;dtrend,'cpix',outdir='/data/mta/www/mta_deriv/SCI',sig=20
;dtrend,'cti',outdir='/data/mta/www/mta_deriv/SCI'

exit
