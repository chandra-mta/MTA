dtrend,'deahk_elec.fits',wsmooth=30
dtrend,'deahk_temp.fits',sig=3,wsmooth=30

tmp_save,'deahk_temp.fits','deahk_temp_att.fits',n_out=-1,merge='pt_suncent.fits'
tmp_save,'deahk_temp.fits','deahk_temp_alt.fits',n_out=-1,merge='pt_alt.fits'
dtrend,'deahk_temp_att.fits',xax='pt_suncent_ang', ccode='time'
dtrend,'deahk_temp_alt.fits',xax='sc_altitude', ccode='time'


exit
