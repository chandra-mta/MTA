x=mta_db_get_add(outfile='hrmatherm.fits',ter_cols='_4rt555t_avg,_4rt556t_avg,_4rt557t_avg,_4rt558t_avg,_4rt559t_avg,_4rt560t_avg,_4rt561t_avg,_4rt562t_avg,_4rt563t_avg,_4rt564t_avg,_4rt565t_avg,_4rt567t_avg,_4rt568t_avg,_4rt569t_avg,_4rt570t_avg,_4rt575t_avg,_4rt576t_avg,_4rt577t_avg,_4rt578t_avg,_4rt579t_avg,_4rt580t_avg,_4rt581t_avg')
dtrend,'hrmatherm.fits',wsmooth=30

x=mta_db_get_add(outfile='pt_suncent.fits',ter_cols='pt_suncent_ang',/debug)
x=mta_db_get_add(outfile='pt_alt.fits',ter_cols='sc_altitude',/debug)
tmp_save,'hrmatherm.fits','hrmatherm_att.fits',n_out=-1,merge='pt_suncent.fits'
tmp_save,'hrmatherm.fits','hrmatherm_alt.fits',n_out=-1,merge='pt_alt.fits'
dtrend, 'hrmatherm_att.fits', xax='pt_suncent_ang', ccode='time'
dtrend, 'hrmatherm_alt.fits', xax='sc_altitude', ccode='time'

x=mta_db_get_add(outfile='hrmastruts.fits',ter_cols='_4rt582t_avg,_4rt583t_avg,_4rt584t_avg,_4rt585t_avg,_4rt586t_avg,_4rt587t_avg,_4rt588t_avg,_4rt589t_avg,_4rt590t_avg,_4rt591t_avg,_4rt592t_avg,_4rt593t_avg,_4rt594t_avg,_4rt595t_avg,_4rt596t_avg,_4rt597t_avg,_4rt598t_avg')
dtrend,'hrmastruts.fits',wsmooth=30
tmp_save,'hrmastruts.fits','hrmastruts_att.fits',n_out=-1,merge='pt_suncent.fits'
tmp_save,'hrmastruts.fits','hrmastruts_alt.fits',n_out=-1,merge='pt_alt.fits'
dtrend, 'hrmastruts_att.fits', xax='pt_suncent_ang', ccode='time'
dtrend, 'hrmastruts_alt.fits', xax='sc_altitude', ccode='time'

x=mta_db_get_add(outfile='obfwdbulkhead.fits',ter_cols='_4rt700t_avg,_4rt701t_avg,_4rt702t_avg,_4rt703t_avg,_4rt704t_avg,_4rt705t_avg,_4rt706t_avg,_4rt707t_avg,_4rt708t_avg,_4rt709t_avg,_4rt710t_avg,_4rt711t_avg')
dtrend,'obfwdbulkhead.fits',wsmooth=30
tmp_save,'obfwdbulkhead.fits','obfwdbulkhead_att.fits',n_out=-1,merge='pt_suncent.fits'
tmp_save,'obfwdbulkhead.fits','obfwdbulkhead_alt.fits',n_out=-1,merge='pt_alt.fits'
dtrend, 'obfwdbulkhead_att.fits', xax='pt_suncent_ang', ccode='time'
dtrend, 'obfwdbulkhead_alt.fits', xax='sc_altitude', ccode='time'

x=mta_db_get_add(outfile='precoll.fits',ter_cols='_4prt1at_avg,_4prt1bt_avg,_4prt2at_avg,_4prt2bt_avg,_4prt3at_avg,_4prt3bt_avg,_4prt4at_avg,_4prt4bt_avg,_4prt5at_avg,_4prt5bt_avg')
dtrend,'precoll.fits',wsmooth=30
tmp_save,'precoll.fits','precoll_att.fits',n_out=-1,merge='pt_suncent.fits'
tmp_save,'precoll.fits','precoll_alt.fits',n_out=-1,merge='pt_alt.fits'
dtrend, 'precoll_att.fits', xax='pt_suncent_ang', ccode='time'
dtrend, 'precoll_alt.fits', xax='sc_altitude', ccode='time'

exit
