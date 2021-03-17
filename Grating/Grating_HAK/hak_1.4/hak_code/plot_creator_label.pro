PRO plot_creator_label, additional_string
;+
; PRO plot_creator_label, additional_string
; 
; Add creation information to lower-left of a plot page,
; e.g, 
;
;    ddidl/xrcf/test.pro
;    dd Sat Jun 26 13:08:28 1999
;
; is added with the call:
;    plot_creator_label, 'ddidl/xrcf/test.pro'
;   --------------------------------------------------
; 6/26/99 dd
;   --------------------------------------------------
;-

; Get user name
; could use this...
;whoami = getenv('USER')
; but this is more reliable?!?
SPAWN, 'whoami', whoami

save_char = !p.charsize
save_region = !p.region

; Set to full region
!p.region = [0.,0.,1.,1.]
; Smaller characters
!p.charsize = 0.8

if n_elements(additional_string) GT 0 then begin
  xyouts, 0.01, 0.01, /NORM, whoami+' '+SYSTIME()
  xyouts, 0.01, 0.033, /NORM, additional_string
end else begin
  xyouts, 0.01, 0.01, /NORM, whoami+' '+SYSTIME()
end

!p.charsize = save_char
!p.region = save_region

RETURN
END
