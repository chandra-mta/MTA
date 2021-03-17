;x=mta_db_get_add(outfile='pt_suncent.fits',ter_cols='pt_suncent_ang')

;x=mta_db_get_add(outfile='mups1.fits',ter_cols='_aothrst1_avg,_aothrst2_avg,_aothrst3_avg,_aothrst4_avg,_pm1thv1t_avg,_pm1thv2t_avg,_pm2thv1t_avg,_pm2thv2t_avg,_pm3thv1t_avg,_pm3thv2t_avg,_pm4thv1t_avg,_pm4thv2t_avg,_pmfp01t_avg,_pmtank1t_avg,_pmtank2t_avg,_pmtank3t_avg,_pmtankp_avg,_trspmtpc_avg')
;x=mta_db_get_add(outfile='mups_2a.fits',ter_cols='_pcm01t_avg,_pcm02t_avg,_pcm03t_avg,_pcm04t_avg,_pfdm101t_avg,_pfdm102t_avg,_pfdm201t_avg,_pfdm202t_avg,_pffp01t_avg,_pftank1t_avg,_pftank2t_avg,_pftankip_avg,_pftankop_avg,_phetankp_avg,_phetankt_avg,_phofp1t_avg,_pxdm01t_avg,_pxdm02t_avg,_pxtank1t_avg,_pxtank2t_avg,_pxtankip_avg,_pxtankop_avg')
;x=mta_db_get_add(outfile='mups_2b.fits',ter_cols='_pline01t_avg,_pline02t_avg,_pline03t_avg,_pline04t_avg,_pline05t_avg,_pline06t_avg,_pline07t_avg,_pline08t_avg,_pline09t_avg,_pline10t_avg,_pline11t_avg,_pline12t_avg,_pline13t_avg,_pline14t_avg,_pline15t_avg,_pline16t_avg')

;dtrend,'mups.fits',wsmooth=30
;dtrend,'mups.fits',wsmooth=30,/qtr_only
dtrend,'mups.fits',wsmooth=30,/avg_only
dtrend,'mups.fits',wsmooth=30,/wk_only
;tmp_save,'mups.fits','mups_sa.fits',n_out=-1,merge='pt_suncent.fits'
;dtrend,'mups_sa.fits',wsmooth=30
;tmp_save,'mups_2b.fits','mups_att.fits',n_out=-1,merge='pt_suncent.fits'
;dtrend,'mups_att.fits',xax='pt_suncent_ang',ccode='time'

; #dmtcalc mups1_org.fits mups1.fits expression="PMTANKP_AVG=(PMTANKP_AVG/6.89476)"
; #dmtcalc mups_2a_org.fits mups_2a.fits @convert_psi.lis
exit
