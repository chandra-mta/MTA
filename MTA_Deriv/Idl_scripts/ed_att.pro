tmp_save,'pcadtemp.fits','pcadtemp_att.fits',n_out=-1,merge='pt_suncent.fits'
dtrend,'pcadtemp_att.fits',xax='pt_suncent_ang', ccode='time'
tmp_save,'sc_main_temp1a.fits','sc_main_temp1a_att.fits',n_out=-1,merge='pt_suncent.fits'
tmp_save,'sc_main_temp1b.fits','sc_main_temp1b_att.fits',n_out=-1,merge='pt_suncent.fits'
tmp_save,'sc_main_temp2a.fits','sc_main_temp2a_att.fits',n_out=-1,merge='pt_suncent.fits'
tmp_save,'sc_main_temp2b.fits','sc_main_temp2b_att.fits',n_out=-1,merge='pt_suncent.fits'
tmp_save,'sc_anc_temp1.fits','sc_anc_temp1_att.fits',n_out=-1,merge='pt_suncent.fits'
tmp_save,'sc_anc_temp2.fits','sc_anc_temp2_att.fits',n_out=-1,merge='pt_suncent.fits'
dtrend,'sc_main_temp_att.fits',xax='pt_suncent_ang', ccode='time'
dtrend,'sc_anc_temp_att.fits',xax='pt_suncent_ang', ccode='time'
tmp_save,'batt_temp.fits','batt_temp_att.fits',n_out=-1,merge='pt_suncent.fits'
dtrend,'batt_temp_att.fits',xax='pt_suncent_ang', ccode='time'
x=mta_db_get_add(ter_cols='_ohrthr27_avg,_ohrthr42_avg,_ohrthr43_avg,_oobagrd3_avg,_oobagrd6_avg', outfile='pcadftsgrad.fits')
tmp_save,'pcadftsgrad.fits','pcadftsgrad_att.fits',n_out=-1,merge='pt_suncent.fits'
dtrend,'pcadftsgrad_att.fits',xax='pt_suncent_ang', ccode='time'

exit
