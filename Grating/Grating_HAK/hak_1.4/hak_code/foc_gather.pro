PRO foc_gather, gfr_structure_out
;+
; PRO foc_gather [, gfr_structure_out]
;
; This procedure reads the obs_anal output 'summary.rdb and
; 'linelist.rdb files from the various foc exposures and
; combines them into one big "gathered fwhm results" file
; which can be used to make plots, etc.
;
; KEYWORDS:
;   STREAK  - if this is set then the streak FWHM etc are
;             used in place of the (piled up) zo values.
;    ----------------------------------------------------
;  8/8/99 dd Added STREAK keyword.
;  8/11/99 dd if STREAK not supplied set it based on foc_streak;
;             add dx_min and dx_min_err to the gfr structure.
;  8/12/99 lose the STREAK keyword: if XY or Streak values are
;          present then include them...  spec_part is then
;          'Zero,Core' or 'Zero,Strk'.  (No more foc_streak.)
;    ----------------------------------------------------
;-

@foc_common

print, ''
print, ' foc_gather_file = '+foc_gather_file
print, ''

; Create and fill the structure, gfr, with the gathered
; FWHM etc. results from the various rdb files.
; Each line in the structure has the columns:
struct_defn = {name:'', focus:0.0, spec_part:'', $
		grat_code:0, order:0, $
		proc_meth:'', source:'', $
		peak_bin_count:0.0, $
		energy:0.0, roi_counts:0.0, $
		fwhm:0.0, fwhm_err:0.0, $
		acf:0.0, acf_err:0.0, $
		dx_min:0.0, dx_min_err:0.0}
; name      is from foc_names
; focus     is from foc_focs
; spec_part is 'Zero,[Core,Strk]' or of the form '[LEG|MEG|HEG][p|m]'
; grat_code is 0,1,2,3 for NONE, HEG, MEG, LEG
; order     is diffraction order, 0, +/-1
; proc_meth is from foc_gather_meth
; source    is from foc_gather_source (e.g., 'S1')
; next 7 columns are as in the linelist.rdb files
; dx_min    is the foc_plot dx_min output
; dx_min_err is uncertainty on above

;( Man, this is a pile of messy code! - but it beats
;  cutting and pasting the values from the browser
;  into emacs - or does it?!?! )

; Use this to flag to signal that gfr has been created
gathered_some = 0  ; not created yet

; Loop over the names and find all the
; summary.rdb and linelist.rdb files
; for those names.  Then read in each
; file found and add its lines
; to the gfr structure.

for in = 0, n_elements(foc_names)-1 do begin
  if foc_gather_sel(in) EQ 1 then begin

    print, ' '+foc_names(in)+' :'

    ; summary.rdb files, spect_part is 'Zero,[Core,Strk]'
    ;
    files = FINDFILE(foc_obs_dir+'/'+ $
	foc_names(in)+'_'+foc_gather_meth+'_summary.rdb',COUNT=nfound)
    if nfound GE 1 then begin
      for iff=0,nfound-1 do begin
        print, '   ' + files(iff)
        ; read in the file
        params = rdb_read(files(iff),/SILENT)
        ; Make a 3 element array for the possible zero-order fwhms
        new_gfr = REPLICATE(struct_defn, 3)
        ; set the values
        new_gfr.name = foc_names(in)
        new_gfr.focus = foc_focs(in)
        new_gfr.spec_part = ['Zero,Core','Zero,Strk','Zero,Core']
        new_gfr.grat_code = 0
        new_gfr.order = 0
        new_gfr(0).proc_meth = foc_gather_meth
        new_gfr(1).proc_meth = foc_gather_meth
        new_gfr(2).proc_meth = 'L1a'
        new_gfr.source = foc_gather_source
        ; set energy to 0.0 since it consists of many
        ; energies...
        new_gfr.energy = 0.0
        new_gfr.peak_bin_count = 0.0  ; used in diffracted measurements only

        ; Get the available zero-order measurements
        ; This measurement should always be in the file:
        rpf_get_value, params, 'zo_fwhm_fit', value, ERROR=valerr
        new_gfr(0).fwhm = value
        new_gfr(0).fwhm_err = valerr
        rpf_get_value, params, 'zo_acf', value, ERROR=valerr
        new_gfr(0).acf = value
        new_gfr(0).acf_err = valerr
        rpf_get_value, params, 'zo_detail_events', value
        new_gfr(0).roi_counts = value
        inext = 1
        ; See if there is a streak measurment available:
        if TOTAL(params.name EQ 'strk_fwhm_fit') GT 0 then begin
          rpf_get_value, params, 'strk_fwhm_fit', value, ERROR=valerr
          new_gfr(inext).fwhm = value
          new_gfr(inext).fwhm_err = valerr
          rpf_get_value, params, 'strk_acf', value, ERROR=valerr
          new_gfr(inext).acf = value
          new_gfr(inext).acf_err = valerr
          rpf_get_value, params, 'strk_events', value
          new_gfr(inext).roi_counts = value
          inext= inext + 1
        end
        ; and see if XY coords ("Level 1") measurement is available:
        if TOTAL(params.name EQ 'zo_xy_fwhm_fit') GT 0 then begin
          rpf_get_value, params, 'zo_xy_fwhm_fit', value, ERROR=valerr
          new_gfr(inext).fwhm = value
          new_gfr(inext).fwhm_err = valerr
          rpf_get_value, params, 'zo_xy_acf', value, ERROR=valerr
          new_gfr(inext).acf = value
          new_gfr(inext).acf_err = valerr
          rpf_get_value, params, 'zo_detail_events', value
          new_gfr(inext).roi_counts = value
          inext= inext + 1
        end

        ; Keep only the valid ones:
        new_gfr = new_gfr(0:inext-1)

        ; and append these to the result (or create the result)
        if gathered_some NE 0 then begin
          gfr = [gfr, new_gfr]
        end else begin
          gfr = new_gfr
          gathered_some = 1
        end

      end
    end

    ; The dispersed spectra results are in files
    ; with the grating spectral part in the file name.
    ; Loop over the parts too...
    if foc_grating NE 'NONE' then begin
      parts = ['MEGm','MEGp','HEGm','HEGp']
      part_grats = [2,2,1,1]
      part_orders = [-1,1,-1,1]
      if foc_grating EQ 'LETG' then begin
        parts = ['LEGm','LEGp']
        part_grats = [3,3]
        part_orders = [-1,1]
      end
      for ip=0, n_elements(parts)-1 do begin

        ; non-level 1.5 dispersed results
        ;
        files = FINDFILE(foc_obs_dir+'/' + $
		foc_names(in)+'_'+foc_gather_meth+ $
		'_'+ parts(ip)+'*_linelist.rdb',COUNT=nfound)
        if nfound GE 1 then begin
          for iff=0,nfound-1 do begin
            print, '   ' + files(iff)
        ;-->
        ; read in the file
        llist = rdb_read(files(iff),/SILENT)
        ; Use only the peak_flag=0 entries:
        llist = llist(where(llist.peak_flag EQ 0))

        ; Make a N-element array for these lines
        new_gfr = REPLICATE(struct_defn, n_elements(llist))
        ; set the values, these are the same for all lines:
        new_gfr.name = foc_names(in)
        new_gfr.focus = foc_focs(in)
        new_gfr.spec_part = parts(ip)
        new_gfr.grat_code = part_grats(ip)
        new_gfr.order = part_orders(ip)
        new_gfr.proc_meth = foc_gather_meth
        new_gfr.source = foc_gather_source
        ; and loop over the lines to fill this in...
        for il=0,n_elements(llist)-1 do begin
          new_gfr(il).peak_bin_count = llist(il).peak_bin_count
          new_gfr(il).energy = llist(il).energy
          new_gfr(il).fwhm = llist(il).fwhm
          new_gfr(il).fwhm_err = llist(il).fwhm_err
          new_gfr(il).acf = llist(il).acf
          new_gfr(il).acf_err = llist(il).acf_err
          new_gfr(il).roi_counts = llist(il).roi_counts
        end

        if gathered_some NE 0 then begin
          gfr = [gfr, new_gfr]
        end else begin
          gfr = new_gfr
          gathered_some = 1
        end
        ;-->
          end
        end

        ; level 1.5 dispersed results
        ;
        files = FINDFILE(foc_obs_dir+'/' + $
		foc_names(in)+'_L1.5'+ $
		'_'+ foc_gather_source +parts(ip)+ $
		'1_linelist.rdb', COUNT=nfound)
        if nfound GE 1 then begin
          for iff=0,nfound-1 do begin
            print, '   ' + files(iff)
        ;-->
        ; read in the file
        llist = rdb_read(files(iff),/SILENT)
        ; Use only the peak_flag=0 entries:
        llist = llist(where(llist.peak_flag EQ 0))

        ; Make a N-element array for these lines
        new_gfr = REPLICATE(struct_defn, n_elements(llist))
        ; set the values, these are the same for all lines:
        new_gfr.name = foc_names(in)
        new_gfr.focus = foc_focs(in)
        new_gfr.spec_part = parts(ip)
        new_gfr.grat_code = part_grats(ip)
        new_gfr.order = part_orders(ip)
        new_gfr.proc_meth = 'L1a'
        new_gfr.source = foc_gather_source
        ; and loop over the lines to fill this in...
        for il=0,n_elements(llist)-1 do begin
          new_gfr(il).energy = llist(il).energy
          new_gfr(il).peak_bin_count = llist(il).peak_bin_count
          new_gfr(il).fwhm = llist(il).fwhm
          new_gfr(il).fwhm_err = llist(il).fwhm_err
          new_gfr(il).acf = llist(il).acf
          new_gfr(il).acf_err = llist(il).acf_err
          new_gfr(il).roi_counts = llist(il).roi_counts
        end

        if gathered_some NE 0 then begin
          gfr = [gfr, new_gfr]
        end else begin
          gfr = new_gfr
          gathered_some = 1
        end
        ;-->
          end
        end

      end ; part loop

    end  ; of check for NONE

  end
end

; write out the gathered results
if gathered_some NE 0 then begin
  rdb_write, foc_results_dir+'/'+foc_gather_file, gfr, /SILENT
  ; 'return' the structure too
  gfr_structure_out = gfr
  print, ''
  print, ' Gathered FWHM Results file : '+foc_results_dir+'/'+foc_gather_file
end else begin
  print, '*** No results were gathered ?!?'
end

RETURN
END
