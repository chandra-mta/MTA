d1=mrdfits('compgradkodak.fits',1,/dscale)
dat=float_struct(d1(where(d1.(1) ne -99)))
dat.time=dat.time*86400.+31536000.

b=where(dat.time ge 220924863. and dat.time lt 252460863.,bnum)
mwrfits,dat(b),'hrma2006.fits',/create
b=where(dat.time ge 236563263. and dat.time lt 252460863.,bnum)
mwrfits,dat(b),'hrma2006_6mo.fits',/create
b=where(dat.time ge 239241663. and dat.time lt 249782463.,bnum)
mwrfits,dat(b),'hrma2006_3mo.fits',/create

dtrend,'hrma2006.fits'
dtrend,'hrma2006_6mo.fits'
dtrend,'hrma2006_3mo.fits'

exit
