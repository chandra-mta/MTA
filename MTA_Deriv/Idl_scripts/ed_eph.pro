x=mta_db_get_add(outfile='ephhk1.fits',ter_cols='_eiostatus_a_avg,_eiostatus_b_avg,_eiostatus_c_avg,_eiostatus_d_avg,_eiostatus_e_avg,_eiostatus_f_avg,_eiostatus_g_avg,_eiostatus_h_avg,_ephsimstatus_avg,_hkcmdsuccess_avg,_hkretryneed_avg,_hkreturncode_avg,_hktimatimout_avg,_hktimdtimout_avg')
x=mta_db_get_add(outfile='ephhk2.fits',ter_cols='_sccmdsuccess_avg,_scretryneed_avg,_screturncode_avg,_tccmdsuccess_avg,_tcnaksent_avg,_tcretryneed_avg,_tcreturncode_avg,_tctimatimout_avg,_tctimdtimout_avg,_telecmdcnt_avg,_telecmdcode_avg')
dtrend,'ephhk.fits',wsmooth=10
x=mta_db_get_add(outfile='ephtv.fits',ter_cols='_5eiot_avg,_5ephint_avg,_hkabiasleaki_avg,_hkbbiasleaki_avg,_hkcbiasleaki_avg,_hkdbiasleaki_avg,_hkebiasleaki_avg,_hkeboxtemp_avg,_hkfbiasleaki_avg,_hkghv_avg,_hkn6i_avg,_hkn6v_avg,_hkp27i_avg,_hkp27v_avg,_hkp5i_avg,_hkp5v_avg,_hkp6i_avg,_hkp6v_avg,_teio_avg,_tephin_avg')
dtrend,'ephtv.fits',wsmooth=30
x=mta_db_get_add(outfile='pt_suncent.fits',ter_cols='pt_suncent_ang')
tmp_save,'ephtv.fits','ephtv_att.fits',n_out=-1,merge='pt_suncent.fits'
dtrend,'ephtv_att.fits',xax='pt_suncent_ang', ccode='time'
x=mta_db_get_add(outfile='pt_alt.fits',ter_cols='sc_altitude')
tmp_save,'ephtv.fits','ephtv_alt.fits',n_out=-1,merge='pt_alt.fits'
;dtrend,'ephtv_alt.fits',xax='sc_altitude', ccode='time'

;;ephrate
x=mta_db_get_add(outfile='ephrate1.fits',ter_cols='_sca00_avg,_sca01_avg,_sca02_avg,_sca03_avg,_sca04_avg,_sca05_avg,_scb00_avg,_scb01_avg,_scb02_avg,_scb04_avg,_scb05_avg,_scc0_avg,_scct1_avg,_scct2_avg,_scct3_avg,_scct4_avg,_scct5_avg,_scd0_avg,_sce0_avg,_scf0_avg,_scg0_avg,_sch25gr_avg')
x=mta_db_get_add(outfile='ephrate2.fits',ter_cols='_sch25s1_avg,_sch25s23_avg,_sch41gr_avg,_sch41s1_avg,_sch41s23_avg,_sch4gr_avg,_sch4s1_avg,_sch4s23_avg,_sch8gr_avg,_sch8s1_avg,_sch8s23_avg,_scp25gr_avg,_scp25s_avg,_scp41gr_avg,_scp41s_avg,_scp4gr_avg,_scp4s_avg,_scp8gr_avg,_scp8s_avg')
dtrend,'ephrate.fits',wsmooth=30
x=mta_db_get_add(outfile='ephkey.fits',ter_cols='_scct0_avg,_sce1300_avg,_sce150_avg,_sce300_avg,_sce3000_avg,_sch25gm_avg,_sch41gm_avg,_sch4gm_avg,_sch8gm_avg,_scint_avg,_scp25gm_avg,_scp41gm_avg,_scp4gm_avg,_scp8gm_avg')
dtrend,'ephkey.fits',wsmooth=30
x=mta_db_get_add(outfile='ephtvkey.fits',ter_cols='_hkabiasleaki_avg,_hkbbiasleaki_avg,_hkcbiasleaki_avg,_hkdbiasleaki_avg,_hkebiasleaki_avg,_hkeboxtemp_avg,_hkfbiasleaki_avg,_teio_avg,_tephin_avg,_hkp27i_avg,_sce1300_avg,_sce150_avg,_scp41gm_avg,_scp4gm_avg')
tmp_save,'ephtvkey.fits','ephtvkey2.fits',n_out=2000
spawn,"/home/ascds/DS.release/bin/dmcopy 'ephtvkey2.fits[cols TIME,SCE1300_AVG,SCE150_AVG,SCP41GM_AVG,SCP4GM_AVG,TEPHIN_AVG]' ephtvkey1a.fits clobber=yes"
;spawn,"/home/ascds/DS.release/bin/dmcopy 'ephtvkey2.fits[cols -SCE1300_AVG,-SCE150_AVG,-SCP41GM_AVG,-SCP4GM_AVG]' ephtvkey2.fits clobber=yes"
;x=eph_read('ephin_L1') ; see ed_hrc
tmp_save,'ephtvkey1a.fits','ephtvkey1.fits',n_out=-1,merge='eph_L1.fits'
; trend all tv vs. tephin  04 dec 2003
spawn,"cp ephtv.fits ephtvkey2.fits"
dtrend,'ephtvkey.fits',xax='tephin', ccode='time'
exit
