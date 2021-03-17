FUNCTION poiss_f, mean, nmax
; Evaluate Poisson dist for a mean rate mean and
; for bins n=0 to n = nmax

norm = EXP(-mean)
n_array = fltarr(nmax+1)
n_array(0) = norm
FOR ip=1,nmax DO n_array(ip) = n_array(ip-1)*mean/FLOAT(ip)

RETURN, n_array
END
