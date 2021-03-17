x=mta_db_get_add(outfile='hrctemp.fits',ter_cols='_2ceahvpt_avg,_2chtrpzt_avg,_2condmxt_avg,_2dcentrt_avg,_2dtstatt_avg,_2fhtrmzt_avg,_2fradpyt_avg,_2pmt1t_avg,_2pmt2t_avg,_2uvlspxt_avg', /debug)
dtrend,'hrctemp.fits',wsmooth=10
x=mta_db_get_add(outfile='pt_suncent.fits',ter_cols='pt_suncent_ang')
tmp_save,'hrctemp.fits','hrctemp_att.fits',n_out=-1,merge='pt_suncent.fits'
dtrend,'hrctemp_att.fits',xax='pt_suncent_ang',ccode='time'

;hrcelec
;  following includes temporary workaround (extra \ before ') for 
;   a dataseeker bug
x=mta_db_get_add(outfile='hrcelec_i.fits',prim="SI=\'HRC-I\',CORADMEN=\'ENAB\',CCSDSTMF=\'FMT1\'",ter_cols='_2detart_avg,_2detbrt_avg,_calpalv_avg,_cbhuast_avg,_cbhvast_avg,_cbluast_avg,_cblvast_avg,_fcpuast_avg,_fcpvast_avg,_hvpsstat_avg,_imbpast_avg,_imhblv_avg,_imhvlv_avg,_imtpast_avg,_lldialv_avg,_mlswenbl_avg,_mlswstat_avg,_mtrcmndr_avg,_mtritmp_avg,_mtrselct_avg,_mtrstatr_avg,_n15cast_avg,_p15cast_avg,_p24cast_avg,_rsrfalv_avg,_s1hvlv_avg,_s1hvst_avg,_s2hvlv_avg,_s2hvst_avg,_scidpren_avg,_scthast_avg,_spbpast_avg,_sphblv_avg,_sphvlv_avg,_sptpast_avg,_wdthast_avg',/debug)
dtrend,'hrcelec_i.fits'
x=mta_db_get_add(outfile='hrcelec_s.fits',prim="SI=\'HRC-S\',CORADMEN=\'ENAB\',CCSDSTMF=\'FMT1\'",ter_cols='_2detart_avg,_2detbrt_avg,_calpalv_avg,_cbhuast_avg,_cbhvast_avg,_cbluast_avg,_cblvast_avg,_fcpuast_avg,_fcpvast_avg,_hvpsstat_avg,_imbpast_avg,_imhblv_avg,_imhvlv_avg,_imtpast_avg,_lldialv_avg,_mlswenbl_avg,_mlswstat_avg,_mtrcmndr_avg,_mtritmp_avg,_mtrselct_avg,_mtrstatr_avg,_n15cast_avg,_p15cast_avg,_p24cast_avg,_rsrfalv_avg,_s1hvlv_avg,_s1hvst_avg,_s2hvlv_avg,_s2hvst_avg,_scidpren_avg,_scthast_avg,_spbpast_avg,_sphblv_avg,_sphvlv_avg,_sptpast_avg,_wdthast_avg',/debug)
dtrend,'hrcelec_s.fits'
x=mta_db_get_add(outfile='hrcelec_ai.fits',prim="SI=\'ACIS-I\',CORADMEN=\'ENAB\'",ter_cols='_2detart_avg,_2detbrt_avg,_calpalv_avg,_cbhuast_avg,_cbhvast_avg,_cbluast_avg,_cblvast_avg,_fcpuast_avg,_fcpvast_avg,_hvpsstat_avg,_imbpast_avg,_imhblv_avg,_imhvlv_avg,_imtpast_avg,_lldialv_avg,_mlswenbl_avg,_mlswstat_avg,_mtrcmndr_avg,_mtritmp_avg,_mtrselct_avg,_mtrstatr_avg,_n15cast_avg,_p15cast_avg,_p24cast_avg,_rsrfalv_avg,_s1hvlv_avg,_s1hvst_avg,_s2hvlv_avg,_s2hvst_avg,_scidpren_avg,_scthast_avg,_spbpast_avg,_sphblv_avg,_sphvlv_avg,_sptpast_avg,_wdthast_avg',/debug)
x=mta_db_get_add(outfile='hrcelec_as.fits',prim="SI=\'ACIS-S\',CORADMEN=\'ENAB\'",ter_cols='_2detart_avg,_2detbrt_avg,_calpalv_avg,_cbhuast_avg,_cbhvast_avg,_cbluast_avg,_cblvast_avg,_fcpuast_avg,_fcpvast_avg,_hvpsstat_avg,_imbpast_avg,_imhblv_avg,_imhvlv_avg,_imtpast_avg,_lldialv_avg,_mlswenbl_avg,_mlswstat_avg,_mtrcmndr_avg,_mtritmp_avg,_mtrselct_avg,_mtrstatr_avg,_n15cast_avg,_p15cast_avg,_p24cast_avg,_rsrfalv_avg,_s1hvlv_avg,_s1hvst_avg,_s2hvlv_avg,_s2hvst_avg,_scidpren_avg,_scthast_avg,_spbpast_avg,_sphblv_avg,_sphvlv_avg,_sptpast_avg,_wdthast_avg',/debug)
x=mta_db_get_add(outfile='hrcelec_off.fits',prim="CORADMEN=\'DISA\'",ter_cols='_2detart_avg,_2detbrt_avg,_calpalv_avg,_cbhuast_avg,_cbhvast_avg,_cbluast_avg,_cblvast_avg,_fcpuast_avg,_fcpvast_avg,_hvpsstat_avg,_imbpast_avg,_imhblv_avg,_imhvlv_avg,_imtpast_avg,_lldialv_avg,_mlswenbl_avg,_mlswstat_avg,_mtrcmndr_avg,_mtritmp_avg,_mtrselct_avg,_mtrstatr_avg,_n15cast_avg,_p15cast_avg,_p24cast_avg,_rsrfalv_avg,_s1hvlv_avg,_s1hvst_avg,_s2hvlv_avg,_s2hvst_avg,_scidpren_avg,_scthast_avg,_spbpast_avg,_sphblv_avg,_sphvlv_avg,_sptpast_avg,_wdthast_avg',/debug)
dtrend,'hrcelec_off.fits'
;;dtrend,'hrcelec.fits',wsmooth=10
x=mta_db_get_add(prim="SI=\'ACIS-I\',CORADMEN=\'ENAB\'",ter_cols='mtahrc..hrcveto_avg',outfile='hrcveto_ai.fits',/debug)
x=mta_db_get_add(prim="SI=\'ACIS-S\',CORADMEN=\'ENAB\'",ter_cols='mtahrc..hrcveto_avg',outfile='hrcveto_as.fits',/debug)
x=mta_db_get_add(prim="SI=\'HRC-I\',CORADMEN=\'ENAB\',CCSDSTMF=\'FMT1\'",ter_cols='mtahrc..hrcveto_avg',outfile='hrcveto_i.fits',/debug)
x=mta_db_get_add(prim="SI=\'HRC-S\',CORADMEN=\'ENAB\',CCSDSTMF=\'FMT1\'",ter_cols='mtahrc..hrcveto_avg',outfile='hrcveto_s.fits',/debug)
x=mta_db_get_add(prim="CORADMEN=\'DISA\'",ter_cols='mtahrc..hrcveto_avg',outfile='hrcveto_off.fits',/debug)
dtrend,'hrcveto.fits',wsmooth=30

; see ephL1_read x=mta_db_get_add(outfile='eph_L1.fits',ter_cols='SCE1300_AVG,SCP4GM_AVG,SCP41GM_AVG,SCINT_AVG')
x=eph_read('ephin_L1')
tmp_save,'hrcveto_ai.fits','hrcveto_ai_eph.fits',n_out=-1,merge='eph_L1.fits'
tmp_save,'hrcveto_as.fits','hrcveto_as_eph.fits',n_out=-1,merge='eph_L1.fits'
dtrend,'hrcveto_eph.fits',xax='shevart_avg',ccode='time'

x=mta_db_get_add(outfile='hrchk.fits',ter_cols='_c05palv_avg,_c15nalv_avg,_c15palv_avg,_c24palv_avg,_fe00atm_avg,_fepratm_avg,_imhvatm_avg,_iminatm_avg,_lvplatm_avg,_prbscr_avg,_prbsvl_avg,_smtratm_avg,_sphvatm_avg,_spinatm_avg',/debug)
dtrend,'hrchk.fits',wsmooth=10
exit
