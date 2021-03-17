PRO MTA_RDB_GET, tab
; get rdb table and output it as a fits file
;  because dtrend tools need fits files and dataseeker is
;  is being tricky with rdb repository files
; 28 Apr 2003 BDS

repos_path="/data/mta/DataSeeker/data/repository"

readcol,tab,tags,numlines=1

; assume all float columns
rdfloat,tab,
