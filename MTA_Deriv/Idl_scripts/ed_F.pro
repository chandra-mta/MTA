dtrendf,'ephtv_F.fits',wsmooth=30,/avg_only
tmp_save,'ephtv_F.fits','ephtv_F_att.fits',n_out=-1,merge='pt_suncent.fits'
dtrendf,'ephtv_F_att.fits',xax='pt_suncent_ang', ccode='time',/avg_only
dtrendf,'pcadtemp_F.fits',wsmooth=30,/avg_only
dtrendf,'pcadftsgrad_F.fits',wsmooth=30, filt_it=3,/avg_only
tmp_save,'pcadtemp_F.fits','pcadtemp_att_F.fits',n_out=-1,merge='pt_suncent.fits'
dtrendf,'pcadtemp_att_F.fits',xax='pt_suncent_ang', ccode='time',/avg_only
tmp_save,'pcadftsgrad_F.fits','pcadftsgrad_att_F.fits',n_out=-1,merge='pt_suncent.fits'
dtrendf,'pcadftsgrad_att_F.fits',xax='pt_suncent_ang', ccode='time',/avg_only
dtrendf,'sc_anc_temp_F.fits',wsmooth=30,/avg_only
tmp_save,'sc_anc_temp1_F.fits','sc_anc_temp1_F_att.fits',n_out=-1,merge='pt_suncent.fits'
tmp_save,'sc_anc_temp2_F.fits','sc_anc_temp2_F_att.fits',n_out=-1,merge='pt_suncent.fits'
dtrendf,'sc_anc_temp_F_att.fits',xax='pt_suncent_ang', ccode='time',/avg_only
exit
