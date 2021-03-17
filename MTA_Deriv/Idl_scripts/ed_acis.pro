;;acistemp
; start temp trends at 2000-02-01
x=mta_db_get_add(timestart=65750463,outfile='acistemp.fits',ter_cols='_1cbat_avg,_1cbbt_avg,_1crat_avg,_1crbt_avg,_1dactbt_avg,_1deamzt_avg,_1dpamyt_avg,_1dpamzt_avg,_1oahat_avg,_1oahbt_avg,_1pdeaat_avg,_1pdeabt_avg,_1pin1at_avg,_1wrat_avg,_1wrbt_avg',/debug)
x=mta_db_get_add(outfile='pt_suncent.fits',ter_cols='pt_suncent_ang')
x=mta_db_get_add(outfile='pt_alt.fits',ter_cols='sc_altitude')
dtrend,'acistemp.fits',wsmooth=30
;;;tmp_save,'acistemp.fits','acistemp2.fits',n_out=10000   ; test ccode
;;;spawn, "mv acistemp2.fits acistemp.fits"                ; test ccode
;;;dtrend,'acistemp.fits',wsmooth=30,ccode='time'          ; test ccode
tmp_save,'acistemp.fits','acistemp_sa.fits',n_out=-1,merge='pt_suncent.fits'
tmp_save,'acistemp.fits','acistemp_alt.fits',n_out=-1,merge='pt_alt.fits'
dtrend,'acistemp_sa.fits',wsmooth=30
spawn, "cp acistemp_sa.fits acistemp_att.fits"
dtrend,'acistemp_att.fits',xax='pt_suncent_ang', ccode='time'
dtrend,'acistemp_alt.fits',xax='sc_altitude', ccode='time'
x=mta_db_get_add(outfile='aciseleca.fits',ter_cols='_1dahacu_avg,_1dahavo_avg,_1dahhavo_avg,_1de28avo_avg,_1deicacu_avg,_1den0avo_avg,_1den1avo_avg,_1dep0avo_avg,_1dep1avo_avg,_1dep2avo_avg,_1dep3avo_avg,_1dp28avo_avg,_1dpicacu_avg,_1dpp0avo_avg', /debug)
dtrend,'aciseleca.fits',wsmooth=30
x=mta_db_get_add(outfile='aciselecb.fits',ter_cols='_1dahbcu_avg,_1dahbvo_avg,_1dahhbvo_avg,_1de28bvo_avg,_1deicbcu_avg,_1den0bvo_avg,_1den1bvo_avg,_1dep0bvo_avg,_1dep1bvo_avg,_1dep2bvo_avg,_1dep3bvo_avg,_1dp28bvo_avg,_1dpicbcu_avg,_1dpp0bvo_avg', /debug)
dtrend,'aciselecb.fits',wsmooth=30
x=mta_db_get_add(ter_cols='_1hoprapr_avg,_1hoprbpr_avg',outfile='acismech.fits', /debug)
dtrend,'acismech.fits',wsmooth=30

; see deahk_read x=mta_db_get_add(outfile='deahk_elec.fits',ter_cols='DEAHK17_avg,DEAHK18_avg,DEAHK19_avg,DEAHK20_avg,DEAHK25_avg,DEAHK26_avg,DEAHK27_avg,DEAHK28_avg,DEAHK29_avg,DEAHK30_avg,DEAHK31_avg,DEAHK32_avg,DEAHK33_avg,DEAHK34_avg,DEAHK35_avg,DEAHK36_avg,DEAHK37_avg,DEAHK38_avg,DEAHK39_avg,DEAHK40_avg')
; see deahk_read x=mta_db_get_add(outfile='deahk_temp.fits',ter_cols='DEAHK1_avg,DEAHK2_avg,DEAHK3_avg,DEAHK4_avg,DEAHK5_avg,DEAHK6_avg,DEAHK7_avg,DEAHK8_avg,DEAHK9_avg,DEAHK10_avg,DEAHK11_avg,DEAHK12_avg,DEAHK13_avg,DEAHK15_avg,DEAHK16_avg')
x=deahk_read('deahk_elec')
dtrend,'deahk_elec.fits',wsmooth=30
x=deahk_read('deahk_temp')
dtrend,'deahk_temp.fits',sig=3,wsmooth=30

tmp_save,'deahk_temp.fits','deahk_temp_att.fits',n_out=-1,merge='pt_suncent.fits'
tmp_save,'deahk_temp.fits','deahk_temp_alt.fits',n_out=-1,merge='pt_alt.fits'
dtrend,'deahk_temp_att.fits',xax='pt_suncent_ang', ccode='time'
dtrend,'deahk_temp_alt.fits',xax='sc_altitude', ccode='time'


exit
