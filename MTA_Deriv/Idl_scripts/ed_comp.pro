; see make_acispwr.pro
dtrend,'compaciscent_c.fits',wsmooth=90
dtrend,'compacispwr_c.fits',wsmooth=90
;dtrend,'compephkey.fits',wsmooth=90
;dtrend,'compgradkodak.fits',wsmooth=90
dtrend,'compsimoffsetb_c.fits',wsmooth=90
; quarterly gets too sparse above, so rerun
dtrend,'compaciscent_c.fits',/qtr_only
dtrend,'compacispwr_c.fits',/qtr_only
;dtrend,'compephkey.fits',/qtr_only
;dtrend,'compgradkodak.fits',/qtr_only
dtrend,'compsimoffsetb_c.fits',/qtr_only
