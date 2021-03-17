;;acistemp
; start temp trends at 2000-02-01
dtrend,'acis_eq_100k.fits',sig=3,wsmooth=30
dtrend,'acis_eq_50k.fits',sig=3,wsmooth=30
dtrend,'sim_eq.fits',sig=3,wsmooth=30
