PRO POST_PRINT, output_file_name
;+
; PRO POST_PRINT, output_file_name
;
; This procedure closes the PS device and returns to
; 'X' output device.  If no file name is given the 
; idl.ps file is sent to the printer.
;   -------------------------------------------------------------
; 4/19/91 - dd
; 5/15/97 - dd modified to accept a file name.
;   -------------------------------------------------------------
;-

device, /close_file

file = 'idl.' + STRLOWCASE(!D.NAME)

if n_elements(output_file_name) gt 0 then begin
  cmd = 'mv ' + file + ' ' + output_file_name
end else begin
  cmd = 'lpr ' + file
end

SPAWN, cmd

SET_PLOT, 'X'

RETURN

END