FUNCTION ELBI_LOW_READ, froot
; special read elbi_low data from rdb files

rdfloat,'/data/mta/DataSeeker/data/repository/elbi_low.rdb', $
    time,n,avg,std,$
    skipline=2
m1 = {elbi1, time:time(0), elbi_low_avg:0.0}
b=where(time gt 0, bnum)
data1 = replicate({elbi1}, bnum)
data1.time=time(b)
data1.elbi_low_avg=avg(b)
mwrfits,data1,'elbi_low_rdb.fits',/create
return, data1
end
