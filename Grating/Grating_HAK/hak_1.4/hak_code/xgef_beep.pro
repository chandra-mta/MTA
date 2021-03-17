PRO xgef_beep
;+
; PRO xgef_beep
;
; Create a noticable "beep - beep ... beep" alert sound at terminal.
;    -------------------------------------------------------------
;-
      print, string([7B])
      wait, 0.3
      print, string([7B])
      wait, 0.6
      print, string([7B])
RETURN
END