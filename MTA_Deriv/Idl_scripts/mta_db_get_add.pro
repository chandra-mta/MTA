;; MTA_DB_GET_ADD  BDS June 2001 Sept 2003
;;  extracts mta average tables for specified msids using DataSeeker
;;  returns an idl structure of arrays 
;;  returns -1 on error
;;
;;  Calling sequence
;;    result = mta_db_get(ter_cols='', $
;;                       [ prim='', sec='', $
;;                         timestart='', timestop='', $
;;                         outfile='', opt='' ] )
;;     where - ter_cols is a string containing comma delimited column
;;                        names (eg. '_1dahacu_avg') or full 
;;                        DataSeeker style specs
;;                        (eg. 'mtaacis..aciseleca_avg._1dahacu_avg')
;;           - prim is an optional comma delimited list of DataSeeker 
;;                        primary criteria, value pairs
;;                        (eg. prim='obsid=9999, grating=HETG')
;;                        valid criteria are: obsid, rafrom, rato,
;;                             decfrom, decto, rollfrom, rollto,
;;                             si, grating, format, pcadmode, radmon
;;           - sec is an optional comma delimited list of DataSeeker 
;;                        secondary (configuration) criteria, value pairs
;;                        (eg. sec='_ctufmtsl=FMT2')
;;           - timestart is an optional start time filter
;;              valid formats are:
;;                    SECS    Elapsed seconds since 1998-01-01T00:00:00
;;                    DATE    YYYY:DDD:hh:mm:ss.ss...
;;                    CALDATE YYYYMonDD at hh:mm:ss.ss...
;;                    FITS date/time format YYYY-MM-DDThh:mm:ss.ss...
;;           - timestop is an optional stop time filter
;;           - outfile is an optional filename for the fits output.
;;           - opt is an optional string of additional DataSeeker options
;;                      to append to command line. Use with caution.
;;           - debug is an optional keyword for extra verbosity
;;
;;   coming soon:
;;     expanded capabilty to pass primary and secondary 
;;            criteria to DataSeeker - done
;;     lookup table for db and table names, so columns can
;;            be specified with msid only - done
;;
;;  Limitations:
;;
;;  Examples:
;;  ; get columns _ohrthr42_avg and _1hoprapr_avg between
;;       ;  Jan 01,2002 and Jan 02,2002 and save a fits file, 
;;       ;   as well as assigning output structure to test_data
;;       test_data = mta_db_get(timestart='2002-01-01',timestop='2002-01-02', $
;;                   ter_cols='_ohrthr42_avg,_1hoprapr_avg,_1hoprapr_std', $
;;                   outfile='test2.fits')
;;  
;;       ; get some columns during a specific time specified as 
;;       ;  seconds since 01/01/1998
;;       test_data = mta_db_get(timestart=127500000,timestop=128500000, $
;;                   ter_cols='_tscpos_avg,_ohrthr42_avg,_1hoprapr_avg', $
;;                   outfile='test2.fits')
;;  
;;       ; get some columns during a specific time in FMT4
;;       test_data = mta_db_get(timestart=127500000,timestop=128500000, $
;;                   sec='ctufmtsl=FMT4', $
;;                   ter_cols='_tscpos_avg,_ohrthr42_avg,_1hoprapr_avg', $
;;                   outfile='test2.fits')
;;  
;;       ; get some columns for obsid 3383
;;       test_data = mta_db_get(prim='obsid=3383', $
;;                   ter_cols='_tscpos_avg,_ohrthr42_avg,_1hoprapr_avg', $
;;                   outfile='test2.fits')
;;  
;;       ; get a whole table and some other columns for obsid 3383
;;       test_data = mta_db_get(prim='obsid=3383', $
;;                   ter_cols='mtaacis..acismech_avg,_ohrthr42_avg', $
;;                   outfile='test2.fits')
;;  
;;       ; get some columns for obsid 3383 during FMT4, 
;;       ;  but use a different ccdm lookup table
;;       test_data = mta_db_get(prim='obsid=3383', sec='ctufmtsl=FMT4', $
;;                   ter_cols='mtaacis..acismech_avg,_ohrthr42_avg', $
;;                   outfile='test2.fits', opt='-c myccdm.tab')
;;
;;  History
;;  Version 2.0 - updated 2/2002 BDS for new dataseeker.pl release version
;;  Version 2.1 - updated 8/2002 BDS for new dataseeker.pl release version
;;                must have parameter file style arguments
;;  mta_db_get_add - updated 9/2003 BDS get only updated data and 
;;                   merge with 1 hr averages
;;                   calls outside routines: mk_avg.pro
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

FUNCTION ID, msid, type
  ; OBSELETE in 2.0, let dataseeker.pl handle this
   return, msid
  ; return db..table.column string given column
  if (type eq 1) then lookup = 'avgdb.rdb'
  if (type eq 2) then lookup = 'configdb.rdb'
  get_lun, lunit
  ; figure num lines input
  xnum = strarr(1)
  spawn, 'wc -l '+lookup, xnum
  xxnum = fltarr(2)
  xxnum = strsplit(xnum(0),' ', /extract)
  numobs = long(xxnum(0))
  
  openr, lunit, lookup
  
  array = strarr(numobs)
  readf, lunit, array
  
  free_lun, lunit
  
  i = 1
  line = strsplit(array(i), '	', /extract)
  while (line(2) ne msid and i le numobs-2) do begin
    line = strsplit(array(i), '	', /extract)
    i = i + 1
  endwhile
  
  if (line(2) ne msid) then begin
    print, msid, ' not found
    return, -1
  endif else begin
    return, strcompress(line(0)+'..'+line(1)+'.'+line(2), /remove_all)
  endelse
end

FUNCTION PRIM_VALID, str
  ; check for primary criteria validity
  v_opts = ['COBSRQID', 'AOATTRAS>', 'AOATTRAS<', $
            'AOATTDEC>', 'AOATTDEC<', 'AOATTROL>', 'AOATTROL<', $
            'SCIINS','GRATING','AOPCADMD','CCSDSTMF','CORADMEN']
  tmp = strsplit(strcompress(str, /remove_all), '=', /extract)
  ; change old mnemonics to new
case (strlowcase(tmp(0))) of
  'obsid':    tmp(0)= 'COBSRQID'
  'rafrom':   tmp(0)= 'AOATTRAS>'
  'rato':     tmp(0)= 'AOATTRAS<'
  'decfrom':  tmp(0)= 'AOATTDEC>'
  'decto':    tmp(0)= 'AOATTDEC<'
  'rollfrom': tmp(0)= 'AOATTROL>'
  'rollto':   tmp(0)= 'AOATTROL<'
  'si':       tmp(0)= 'SCIINS'
  'grating':  tmp(0)= 'GRATING'
  'pcadmode': tmp(0)= 'AOPCADMD'
  'format':   tmp(0)= 'CCSDSTMF'
  'radmon':   tmp(0)= 'CORADMEN'
  else:       tmp(0)= strupcase(tmp(0))
endcase
  i = 0
  for i = 0, n_elements(v_opts) - 1 do begin
    if (strupcase(tmp(0)) eq v_opts(i)) then $
      return, strcompress(tmp(0)+"="+string(tmp(1)), /remove_all)
  endfor
  ; valid option not found
  print, "Valid primary criteria are: ", v_opts
  return, "NULL"
end

FUNCTION DATE_VALID, str
  ; OBSELETE in 2.0, let dataseeker.pl handle this
   return, str
  ; be sure date string is valid for DataSeeker
  ;  checks format but not sanity
  ;  if invalid, return NULL
  ;  if valid as is, return str
  ;  if invalid but fixable, return fixed string
  bad = "NULL"
  fix = 0
  inv = 0
  tmp = strsplit(strcompress(str), " ", /extract)
  if (n_elements(tmp lt 2)) then tmp = [tmp, " "]
  big = strsplit(tmp(0), "/", /extract)
  if (fix(big(2)) ge 50 and fix(big(2)) le 99) then begin
    fix = fix + 1
    big(2) = strtrim(1900+fix(big(2)),2)
  endif
  if (fix(big(2)) ge 0 and fix(big(2)) le 49) then begin
    fix = fix + 1
    big(2) = strtrim(2000+fix(big(2)),2)
  endif
  if (fix(big(1)) gt 12) then begin
    if (fix(big(0)) le 12) then begin
      fix = fix + 1
      mtmp = big(1)
      big(1) = big(0) 
      big(0) = mtmp
    endif else inv = inv + 1
  endif
  if (inv ge 1) then return, bad
  if (fix ge 1) then return, strcompress(big(0)+"/"+big(1)+"/"+big(2), /remove_all)+" "+tmp(1)
  return, str
end

;;;;;;;;;;;;;;;;;;; main ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
FUNCTION MTA_DB_GET_ADD, TIMESTART=timestart, TIMESTOP=timestop, $
                     TER_COLS=ter_cols, PRIM=prim, SEC=sec, $
                     OUTFILE=outfile, OPT=opt, DEBUG=debug

; temporarily switch to DS7.0.0 til it moves up to release, 
;  fixes RDB table problems  BDS 21 aug 03
;  
;dspath = '/proj/cm/Integ/install.DS7.0.0/bin/dataseeker.pl'
dspath = '/home/ascds/DS.release/bin/dataseeker.pl'
;dspath = '/home/mta/overbeck/dataseeker.pl'
;dspath = '/data/mta/Script/Deriv/dataseeker.pl'

cleanout = 0 ; don't delete outfile when you're done
mergeout = 0 ; don't merge outfile unless it exists
if (keyword_set(outfile)) then begin
  ; delete old outfile
  ;  or else old values will be silently returned on dataseeker failure
  junk = findfile(outfile, count=outfilecnt)
  if (outfilecnt gt 0) then begin
    if (keyword_set(opt)) then begin
      if (strpos(opt, "-b") gt -1) then begin
        print, outfile+" exists and noclobber is set"
        return, -1
      endif ; if (strpos(opt, "-b") gt -1) then begin
    endif ; if (keyword_set(opt)) then begin
    ;spawn, '/usr/bin/rm '+outfile
    olddat=mrdfits(outfile,1)
    timestart=max(olddat.time)  ; only ask for new data
    mastfile=outfile  ; save outfile name (so I don't have to change
    outfile="ds_"+outfile ; all outfile references below)
    mergeout=1
  endif ; if (outfilecnt gt 0) then begin
endif else begin
  cleanout = 1 ; delete outfile when you're done
  tmpname = strtrim(systime(1),2)
  outfile = 'ds'+tmpname+'.fits
endelse

; begin building command line
;  we'll add on as we go, depending of keywords set
;old command = dspath+' -o '+outfile+' -f ds.cfg -n -u '+user+' -w '+pwd+' -s "'
;command = dspath+' -o '+outfile+' -n -u '+user+' -w '+pwd+' -s "'
; for now must specify some extra stuff
;command = dspath+' -o '+outfile+' -n -u '+user+' -w '+pwd+' -p ./pcadfilter.out -c ./ccdmfilter.out -r avgdb.rdb -d sqlocc -s "'
; this will work if ciao environment is set up correctly
command = dspath+' mode=h clobber=yes outfile='+outfile+' search_crit="'

; set time range
if (keyword_set(timestart)) then $
    command = command+"timestart="+ $
              strcompress(string(timestart),/remove_all)+"\ "
if (keyword_set(timestop)) then $
    command = command+"timestop="+ $
              strcompress(string(timestop),/remove_all)+"\ "
 
; set primary criteria
;  options are obsid, rafrom, rato, decfrom, decto, rollfrom, rollto,
;              si, grating
if (keyword_set(prim)) then begin
  parse = strsplit(prim, ',', /extract)
  for i = 0, n_elements(parse)-1 do begin
    pv = prim_valid(parse(i))
    if (pv eq 'NULL') then begin
      print, parse(i), " is invalid primary criteria. Aborting."
      return, -1
    endif else begin
      ;command = command+' '+strcompress(pv, /remove_all)
      ;command = command+strcompress(pv, /remove_all)+" "
      ; following includes a temporary workaround (extra "\")
      ;  for a dataseeker.pl bug
      command = command+strcompress(pv, /remove_all)+"\ "
    endelse
  endfor
endif

; set secondary criteria
if (keyword_set(sec)) then begin
  parse = strsplit(sec, ',', /extract)
  for i = 0, n_elements(parse)-1 do begin
    if (strpos(parse(i), ".") ge 0) then mnemonic = parse(i) $
    else begin
      val = strsplit(parse(i), "=", /extract)
      mnemonic = id(strtrim(val(0),2), 2)
    endelse
    if (mnemonic eq "-1") then begin
      print, "Mnemonic error.  Aborting"
      return, -1
    endif else begin
      ;command = command+' '+mnemonic+'='+val(1)
      command = command+mnemonic+'='+val(1)+' '
    endelse
  endfor
  command=command+' '
endif

; set tertiary columns
if (keyword_set(ter_cols)) then begin
  parse = strsplit(ter_cols, ',', /extract)
  if (strpos(parse(0), ".") ge 0) then mnemonic = parse(0) $
  else mnemonic = id(parse(0), 1)
  if (mnemonic eq "-1") then begin
    print, "Mnemonic error.  Aborting."
    return, -1
  endif else begin
    command = command+'columns='+mnemonic
  endelse
  for i = 1, n_elements(parse)-1 do begin
    if (strpos(parse(i), ".") ge 0) then mnemonic = parse(i) $
    else mnemonic = id(parse(i), 1)
      if (mnemonic eq "-1") then begin
        print, "Mnemonic error.  Aborting"
        return, -1
      endif else begin
        command = command+','+mnemonic
      endelse
  endfor
  command=command+' '
endif else begin
  print, " "
  print, "You asked for no data - that's what I'm giving you."
  ;print, "  Specify columns to return with keyword TER_COLS in DataSeeker fashion"
  ;print, "  like this: ter_cols=dbname..table.column"
  ;print, "             ter_cols=mtaacis..aciseleca_avg,mtapcad..pcadftsgrad_avg._ohrthr27_avg"
  print, "  Specify columns to return with keyword TER_COLS"
  print, "  like this: ter_cols='column_mnemonic'"
  print, "             ter_cols='_1dahacu_avg,_ohrthr27_avg'"
  return, -1
endelse
  
; close the quotes, here we go
command = command+'" loginFile=loginfile'

if (keyword_set(opt)) then command = command+" "+opt

command = strcompress(command)
print, "command ", command

;not needed now, maybe later -->get_lun, cunit
;not needed now, maybe later -->openw, cunit, tmpcfg
;not needed now, maybe later -->printf, cunit, "timestart="+times[0]
;not needed now, maybe later -->printf, cunit, "timestop="+times[1]
;not needed now, maybe later -->free_lun, cunit
; oldcommand = './dataseeker.pl -o '+outfile+$
; old        ' -s"timestart='+times[0]+' timestop='+times[1]+ $
; old        ' ter-columns='+ter_cols+ $
; old        '" -fds.cfg -u '+user+ $
; old        ' -w '+pwd+' -n'

; this just takes pwd out of command for debugging at STDOUT
;break = strpos(command, "-w") + 2
;pwdbreak = strpos(command, pwd)
;comm_len = strlen(command)
;pass_len = strlen(pwd)
;command2 = strmid(command, 0, break)+" ***"+strmid(command, pwdbreak+pass_len, comm_len)
if (keyword_set(debug)) then print, "command used > "+command ; debug

time0=systime(1)
spawn, "setenv PATH '"+getenv('PATH')+"' ; "+command
;spawn, command
print, command
e_time=systime(1)-time0

; read into struct, print some info and return struct
junk = findfile(outfile, count=outfilecnt)
if (outfilecnt eq 0) then begin
  print, 'No data was retrieved in '+string(e_time)+' seconds'
  return, -1
endif else begin
  get_lun, tunit
  openr, tunit, outfile
  status = fstat(tunit)
  free_lun, tunit
  if (status.size le 0) then begin
    print, 'No data was retrieved in '+string(e_time)+' seconds'
    return, -1
  endif else begin
    intab = mrdfits(outfile, 1)
    if (keyword_set(debug)) then begin
      print, ' '
      print, 'Columns:'
      print, tag_names(intab)
      print, ' retrieved in '+string(e_time)+' seconds'
      print, ' '
    endif ; if (keyword_set(debug)) then begin
    inavg=mk_avg(intab,3600)
    if (mergeout gt 0) then begin ; yes, we want to merge with old file
      outdat=olddat  ; start with olddat in case there is nothing to add
      if (inavg(0).(0) ne -999) then begin ; there is something to add
        ; idl is picky, so do some tricks to get it to concat
        ; should check for errors and sanity first
        ;  (but I think idl's pickiness takes care of some potential probs)
        newdat=olddat  ; copy structure
        struct_assign,inavg,newdat  ; write data to struct definition
        newdat=newdat(0:n_elements(inavg)-1) ; keep only new data
        outdat=[olddat,newdat] 
      endif ;if (inavg(0).(0) ne -999) then begin
    endif ; if (mergeout gt 0) then begin
    if (mergeout eq 0) then outdat=inavg ; don't want to merge or there is
                                         ;  no old file to merge with
    mwrfits,outdat,mastfile,/create
    return, intab
  endelse
endelse

; do some cleanup
if (cleanout eq 1 and NOT keyword_set(debug)) then $
  spawn, '/usr/bin/rm -f '+outfile

end
