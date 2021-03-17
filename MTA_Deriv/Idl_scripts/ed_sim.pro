;;simtemp
x=mta_db_get_add(outfile='pt_suncent.fits',ter_cols='pt_suncent_ang',/debug)
x=mta_db_get_add(outfile='pt_alt.fits',ter_cols='sc_altitude',/debug)
x=mta_db_get_add(outfile='simtemp1.fits',ter_cols='_3btu_bpt_avg,_3fabraat_avg,_3fabrcat_avg,_3famyzat_avg,_3fapyzat_avg,_3faralat_avg,_3flcabpt_avg,_3rctubpt_avg,_3tsmxcet_avg,_3tsmxspt_avg,_3tsmydpt_avg,_3tspyfet_avg,_3tspzdet_avg,_3tspzspt_avg,_3ttacs1t_avg,_3ttacs2t_avg,_3ttacs3t_avg,_3ttbrgbt_avg')
x=mta_db_get_add(outfile='simtemp2.fits',ter_cols='_3tthrc1t_avg,_3tthrc2t_avg,_3tthrc3t_avg,_3ttralat_avg,_3ttralct_avg,_3ttvalvt_avg,_boxtemp_avg,_famtrtemp_avg,_flexatemp_avg,_flexatset_avg,_flexbtemp_avg,_flexbtset_avg,_flexctemp_avg,_flexctset_avg,_psutemp_avg,_tscmtrtemp_avg')
; now done in dtrend_read x=mta_rdb_get_add(outfile='simtempaux.fits',ter_cols='3FAMTRAT_AVG,3FAPSAT_AVG,3FASEAAT_AVG,3TRMTRAT_AVG,3SMOTOC_AVG,3SMOTSTL_AVG')
dtrend,'simtemp.fits',wsmooth=10
tmp_save,'simtemp1.fits','simtemp1_att.fits',n_out=-1,merge='pt_suncent.fits'
tmp_save,'simtemp2.fits','simtemp2_att.fits',n_out=-1,merge='pt_suncent.fits'
tmp_save,'simtempaux.fits','simtempaux_att.fits',n_out=-1,merge='pt_suncent.fits'
dtrend, 'simtemp_att.fits', xax='pt_suncent_ang', ccode='time'

tmp_save,'simtemp1.fits','simtemp1_alt.fits',n_out=-1,merge='pt_alt.fits'
tmp_save,'simtemp2.fits','simtemp2_alt.fits',n_out=-1,merge='pt_alt.fits'
tmp_save,'simtempaux.fits','simtempaux_alt.fits',n_out=-1,merge='pt_alt.fits'
dtrend, 'simtemp_alt.fits', xax='sc_altitude', ccode='time'

x=mta_db_get_add(outfile='simelec.fits',ter_cols='_agrndadc_avg,_fatabadc_avg,_n15vadc_avg,_p15vadc_avg,_p5vadc_avg,_tsctabadc_avg')
dtrend,'simelec.fits',wsmooth=10, filt_it=2
x=mta_db_get_add(outfile='simactu.fits',ter_cols='_faedge_avg,_fapos_avg,_fatabwid_avg,_ldrtnum_avg,_ldrtrelpos_avg,_mrmdest_avg,_pwmlevel_avg,_tscedge_avg,_tscpos_avg,_tsctabwid_avg')
dtrend,'simactu.fits',wsmooth=10
exit
