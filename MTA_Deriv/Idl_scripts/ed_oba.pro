;;obaheaters
x=mta_db_get_add(outfile='obaheaters1.fits',ter_cols='_oobthr01_avg,_oobthr02_avg,_oobthr03_avg,_oobthr04_avg,_oobthr05_avg,_oobthr06_avg,_oobthr07_avg,_oobthr08_avg,_oobthr09_avg,_oobthr10_avg,_oobthr11_avg,_oobthr12_avg,_oobthr13_avg,_oobthr14_avg,_oobthr15_avg')
x=mta_db_get_add(outfile='obaheaters2.fits',ter_cols='_oobthr16_avg,_oobthr17_avg,_oobthr18_avg,_oobthr19_avg,_oobthr20_avg,_oobthr21_avg,_oobthr22_avg,_oobthr23_avg,_oobthr24_avg,_oobthr25_avg,_oobthr26_avg,_oobthr27_avg,_oobthr28_avg,_oobthr29_avg,_oobthr30_avg,_oobthr31_avg,_oobthr32_avg')
x=mta_db_get_add(outfile='obaheaters3.fits',ter_cols='_oobthr33_avg,_oobthr34_avg,_oobthr35_avg,_oobthr36_avg,_oobthr37_avg,_oobthr38_avg,_oobthr39_avg,_oobthr40_avg,_oobthr41_avg,_oobthr42_avg,_oobthr43_avg,_oobthr44_avg,_oobthr45_avg,_oobthr46_avg,_oobthr47_avg')
x=mta_db_get_add(outfile='obaheaters4.fits',ter_cols='_oobthr48_avg,_oobthr49_avg,_oobthr50_avg,_oobthr51_avg,_oobthr52_avg,_oobthr53_avg,_oobthr54_avg,_oobthr55_avg,_oobthr56_avg,_oobthr57_avg,_oobthr58_avg,_oobthr59_avg,_oobthr60_avg,_oobthr61_avg,_oobthr62_avg,_oobthr63_avg,_oobthr64_avg')
dtrend,'obaheaters.fits',wsmooth=30,filt_it=2

x=mta_db_get_add(outfile='pt_suncent.fits',ter_cols='pt_suncent_ang',/debug)
x=mta_db_get_add(outfile='pt_alt.fits',ter_cols='sc_altitude',/debug)

tmp_save,'obaheaters1.fits','obaheaters1_att.fits',n_out=-1,merge='pt_suncent.fits'
tmp_save,'obaheaters2.fits','obaheaters2_att.fits',n_out=-1,merge='pt_suncent.fits'
tmp_save,'obaheaters3.fits','obaheaters3_att.fits',n_out=-1,merge='pt_suncent.fits'
tmp_save,'obaheaters4.fits','obaheaters4_att.fits',n_out=-1,merge='pt_suncent.fits'
dtrend, 'obaheaters_att.fits', xax='pt_suncent_ang', ccode='time'
tmp_save,'obaheaters1.fits','obaheaters1_alt.fits',n_out=-1,merge='pt_alt.fits'
tmp_save,'obaheaters2.fits','obaheaters2_alt.fits',n_out=-1,merge='pt_alt.fits'
tmp_save,'obaheaters3.fits','obaheaters3_alt.fits',n_out=-1,merge='pt_alt.fits'
tmp_save,'obaheaters4.fits','obaheaters4_alt.fits',n_out=-1,merge='pt_alt.fits'
dtrend, 'obaheaters_alt.fits', xax='sc_altitude', ccode='time'

x=mta_db_get_add(ter_cols='_oobagrd1_avg,_oobagrd2_avg,_oobagrd4_avg,_oobagrd5_avg,_oobagrd7_avg,_oobagrd8_avg',outfile='obagrad.fits')
dtrend,'obagrad.fits',wsmooth=30,filt_it=3
tmp_save,'obagrad.fits','obagrad_att.fits',n_out=-1,merge='pt_suncent.fits'
dtrend, 'obagrad_att.fits', xax='pt_suncent_ang', ccode='time'
tmp_save,'obagrad.fits','obagrad_alt.fits',n_out=-1,merge='pt_alt.fits'
dtrend, 'obagrad_alt.fits', xax='sc_altitude', ccode='time'
;;hrmaheaters
x=mta_db_get_add(outfile='hrmaheaters1.fits',ter_cols='_ohrthr01_avg,_ohrthr02_avg,_ohrthr03_avg,_ohrthr04_avg,_ohrthr05_avg,_ohrthr06_avg,_ohrthr07_avg,_ohrthr08_avg,_ohrthr09_avg,_ohrthr10_avg,_ohrthr11_avg,_ohrthr12_avg,_ohrthr13_avg,_ohrthr14_avg')
x=mta_db_get_add(outfile='hrmaheaters2.fits',ter_cols='_ohrthr15_avg,_ohrthr16_avg,_ohrthr17_avg,_ohrthr18_avg,_ohrthr19_avg,_ohrthr20_avg,_ohrthr21_avg,_ohrthr22_avg,_ohrthr23_avg,_ohrthr24_avg,_ohrthr25_avg,_ohrthr26_avg,_ohrthr28_avg,_ohrthr29_avg,_ohrthr30_avg,_ohrthr31_avg,_ohrthr32_avg')
x=mta_db_get_add(outfile='hrmaheaters3.fits',ter_cols='_ohrthr33_avg,_ohrthr34_avg,_ohrthr35_avg,_ohrthr36_avg,_ohrthr37_avg,_ohrthr38_avg,_ohrthr39_avg,_ohrthr40_avg,_ohrthr41_avg,_ohrthr44_avg,_ohrthr45_avg,_ohrthr46_avg,_ohrthr47_avg,_ohrthr48_avg,_ohrthr49_avg,_ohrthr50_avg')
x=mta_db_get_add(outfile='hrmaheaters4.fits',ter_cols='_ohrthr51_avg,_ohrthr52_avg,_ohrthr53_avg,_ohrthr54_avg,_ohrthr55_avg,_ohrthr56_avg,_ohrthr57_avg,_ohrthr58_avg,_ohrthr59_avg,_ohrthr60_avg,_ohrthr61_avg,_ohrthr62_avg,_ohrthr63_avg,_ohrthr64_avg')
dtrend,'hrmaheaters.fits',wsmooth=30,filt_it=3
tmp_save,'hrmaheaters1.fits','hrmaheaters1_att.fits',n_out=-1,merge='pt_suncent.fits'
tmp_save,'hrmaheaters2.fits','hrmaheaters2_att.fits',n_out=-1,merge='pt_suncent.fits'
tmp_save,'hrmaheaters3.fits','hrmaheaters3_att.fits',n_out=-1,merge='pt_suncent.fits'
tmp_save,'hrmaheaters4.fits','hrmaheaters4_att.fits',n_out=-1,merge='pt_suncent.fits'
dtrend, 'hrmaheaters_att.fits', xax='pt_suncent_ang', ccode='time'
tmp_save,'hrmaheaters1.fits','hrmaheaters1_alt.fits',n_out=-1,merge='pt_alt.fits'
tmp_save,'hrmaheaters2.fits','hrmaheaters2_alt.fits',n_out=-1,merge='pt_alt.fits'
tmp_save,'hrmaheaters3.fits','hrmaheaters3_alt.fits',n_out=-1,merge='pt_alt.fits'
tmp_save,'hrmaheaters4.fits','hrmaheaters4_alt.fits',n_out=-1,merge='pt_alt.fits'
dtrend, 'hrmaheaters_alt.fits', xax='sc_altitude', ccode='time'

x=mta_db_get_add(outfile='hrmagrad.fits',ter_cols='_ohrmgrd1_avg,_ohrmgrd2_avg,_ohrmgrd3_avg,_ohrmgrd4_avg,_ohrmgrd5_avg,_ohrmgrd6_avg,_ohrmgrd7_avg,_ohrmgrd8_avg')
dtrend,'hrmagrad.fits',wsmooth=30,filt_it=3
tmp_save,'hrmagrad.fits','hrmagrad_att.fits',n_out=-1,merge='pt_suncent.fits'
dtrend, 'hrmagrad_att.fits', xax='pt_suncent_ang', ccode='time'
tmp_save,'hrmagrad.fits','hrmagrad_alt.fits',n_out=-1,merge='pt_alt.fits'
dtrend, 'hrmagrad_alt.fits', xax='sc_altitude', ccode='time'
exit
