PRO MAKE_ACISPWR

d1=mrdfits('aciseleca.fits',1)
d2=mrdfits('aciselecb.fits',1)
print,tag_names(d1)
print,tag_names(d2)
a={acispwr1,time:0.0,x1dppwra_avg:0.0,x1dppwrb_avg:0.0}
data1 = replicate({acispwr1}, n_elements(d1))
data1.time=d1.time
data1.x1dppwra_avg=d1._1DPICACU_avg*d1._1DE28AVO_avg
;data1.x1dppwrb_avg=d2._1DPICBCU_avg*d2._1DE28BVO_avg
mwrfits,data1,'compacispwr.fits',/create
end
