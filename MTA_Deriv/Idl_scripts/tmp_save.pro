PRO TMP_SAVE, infile, outfile, N_OUT=n_out, MERGE=merge
; condense a fits file, resampling only n_out rows
; set keyword merge to another filename to merge into the first
; to merge entire file (no resampling) set n_out=-1

if (NOT keyword_set(n_out)) then n_out=7500L
indat=mrdfits(infile,1)
n_in=n_elements(indat)
if (n_out lt 0) then n_out=n_in
;indat=indat(0:n_in-n_out-1) ; temporary fix
n_in=n_elements(indat)      ; temporary fix
if (n_in gt n_out) then begin
  index=indgen(n_in,/long)
  ;print, "Maxi: ", max(index) ;debug
  outdex=congrid(index, n_out)
endif else begin
  outdex=indgen(n_in,/long)
endelse

if (keyword_set(merge)) then begin
  mdat=mrdfits(merge,1)
  mdex=indgen(n_elements(outdex),/long)
  mtags=tag_names(mdat)
  mtags(where(strupcase(mtags) eq 'TIME'))="MTIME" ; just change name of 
                                        ;second time col (for debugging now)
  itags=tag_names(indat)
  ntags=[itags,mtags]
  p=create_struct(ntags(0),0.0)
  for i=1,n_elements(ntags)-1 do begin
    p=create_struct(p,ntags(i),0.0)
  endfor ; for i=1,n_elements(ntags)-1 do begin
  
  outdat=replicate(p,n_elements(outdex))
                   
  s_indat=sort(indat.time)
  s_mdat=sort(mdat.time)
  s_mindex=1L
  nloop=n_elements(outdex)-1
  for i=0L, nloop do begin
    ;print, format='($,T12,"tmp_save ",3I,"% done")', fix(i*100/nloop)
    ;print, "working outdex ",i," of ", n_elements(outdex)-1, " ",s_mindex
    ; this isn't quite right, should check to be sure it makes
    ;  sense (ie. min(diff) lt n minutes), but I'll make it easy for now
    ;print,tag_names(mdat) ;debug
    ;print,mdat(0) ;debug
    while (mdat(s_mdat(s_mindex)).time lt indat(s_indat(i)).time and $
           s_mindex lt n_elements(s_mdat)-2) do begin
      s_mindex=s_mindex+1
    endwhile 
    for j=0,n_elements(ntags)-1 do begin
      if (j lt n_elements(itags)) then begin ; decide when to switch 
                                             ;  from old to new
        ;print, s_indat(i), outdex(s_indat(i)) ; debug
        outdat(s_indat(i)).(j)=indat(outdex(s_indat(i))).(j)
      endif else begin
        outdat(s_indat(i)).(j)=mdat(s_mdat(s_mindex-1)).(j-n_elements(itags))
      endelse ; if (j lt n_elements(itags)) then begin 
    endfor ; for j=0,n_elements(ntags)-1 do begin
  endfor ; for i=0L, n_elements(outdex)-1 do begin
  mwrfits, outdat, outfile, /create
endif else begin
  mwrfits, indat(outdex), outfile, /create
endelse ; if (keyword_set(merge)) then begin

end
