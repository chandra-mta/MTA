pro units

infile=mrdfits('pcadtemp.fits',1)
for i=1,n_elements(tag_names(infile))-1 do begin
  infile.(i)=(infile.(i)-273.15)*9/5+32
endfor
mwrfits,infile,'pcadtemp_F.fits'

infile=mrdfits('sc_anc_temp1.fits',1)
for i=1,n_elements(tag_names(infile))-1 do begin
  infile.(i)=(infile.(i)-273.15)*9/5+32
endfor
mwrfits,infile,'sc_anc_temp1_F.fits'

infile=mrdfits('sc_anc_temp2.fits',1)
for i=1,n_elements(tag_names(infile))-1 do begin
  infile.(i)=(infile.(i)-273.15)*9/5+32
endfor
mwrfits,infile,'sc_anc_temp2_F.fits'

infile=mrdfits('ephtv.fits',1)
  infile.X5EIOT_AVG=(infile.X5EIOT_AVG-273.15)*9/5+32
  infile.X5EPHINT_AVG=(infile.X5EPHINT_AVG-273.15)*9/5+32
  infile.TEIO_AVG=(infile.TEIO_AVG-273.15)*9/5+32
  infile.TEPHIN_AVG=(infile.TEPHIN_AVG-273.15)*9/5+32
mwrfits,infile,'ephtv_F.fits'

infile=mrdfits('pcadftsgrad.fits',1)
  infile.OHRTHR27_AVG=(infile.OHRTHR27_AVG-273.15)*9/5+32
  infile.OHRTHR42_AVG=(infile.OHRTHR42_AVG-273.15)*9/5+32
  infile.OHRTHR43_AVG=(infile.OHRTHR43_AVG-273.15)*9/5+32
  infile.OOBAGRD3_AVG=(infile.OOBAGRD3_AVG)*9/5
  infile.OOBAGRD6_AVG=(infile.OOBAGRD6_AVG)*9/5
mwrfits,infile,'pcadftsgrad_F.fits'
end
