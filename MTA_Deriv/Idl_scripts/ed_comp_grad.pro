spawn, "/data/mta4/Deriv/Script/Idl_scripts/get_comp_data"
;;COMPS
dtrend,'compaciscent.fits',wsmooth=90
; see make_acispwr.pro
dtrend,'compacispwr.fits',wsmooth=90
dtrend,'compephkey.fits',wsmooth=90
dtrend,'compgradkodak.fits',wsmooth=90
dtrend,'compsimoffsetb.fits',wsmooth=90
; quarterly gets too sparse above, so rerun
dtrend,'compaciscent.fits',/qtr_only
dtrend,'compacispwr.fits',/qtr_only
dtrend,'compephkey.fits',/qtr_only
dtrend,'compgradkodak.fits',/qtr_only
dtrend,'compsimoffsetb.fits',/qtr_only
;
spawn, "/data/mta4/Deriv/Script/Idl_scripts/get_grad_data"
dtrend,'gradablk.fits',wsmooth=90,sig=1,filt_it=2
dtrend,'gradahet.fits',wsmooth=90,sig=1,filt_it=2
dtrend,'gradaincyl.fits',wsmooth=90,sig=1,filt_it=2
dtrend,'gradcap.fits',wsmooth=90,sig=1,filt_it=2
dtrend,'gradfap.fits',wsmooth=90,sig=1,filt_it=2
dtrend,'gradfblk.fits',wsmooth=90,sig=1,filt_it=2
dtrend,'gradhcone.fits',wsmooth=90,sig=1,filt_it=2
dtrend,'gradhhflex.fits',wsmooth=90,sig=1,filt_it=2
dtrend,'gradhpflex.fits',wsmooth=90,sig=1,filt_it=2
dtrend,'gradhstrut.fits',wsmooth=90,sig=1,filt_it=2
dtrend,'gradocyl.fits',wsmooth=90,sig=1,filt_it=2
dtrend,'gradpcolb.fits',wsmooth=90,sig=1,filt_it=2
dtrend,'gradperi.fits',wsmooth=90,sig=1,filt_it=2
dtrend,'gradsstrut.fits',wsmooth=90,sig=1,filt_it=2
dtrend,'gradtfte.fits',wsmooth=90,sig=1,filt_it=2

; quarterly gets too sparse above, but restrictions are needed
;  but data is messy.  Rerun quarterly without restrictions
dtrend,'gradablk.fits',/qtr_only
dtrend,'gradahet.fits',/qtr_only
dtrend,'gradaincyl.fits',/qtr_only
dtrend,'gradcap.fits',/qtr_only
dtrend,'gradfap.fits',/qtr_only
dtrend,'gradfblk.fits',/qtr_only
dtrend,'gradhcone.fits',/qtr_only
dtrend,'gradhhflex.fits',/qtr_only
dtrend,'gradhpflex.fits',/qtr_only
dtrend,'gradhstrut.fits',/qtr_only
dtrend,'gradocyl.fits',/qtr_only
dtrend,'gradpcolb.fits',/qtr_only
dtrend,'gradperi.fits',/qtr_only
dtrend,'gradsstrut.fits',/qtr_only
dtrend,'gradtfte.fits',/qtr_only
exit
