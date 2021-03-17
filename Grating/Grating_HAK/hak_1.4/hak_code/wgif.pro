PRO wgif, wid, filename
;+
; PRO wgif, wid, filename
;
; Simple gif writing helping routine... from dph
;    --------------------------------------
;-

   wshow, wid, iconic = 0
   tvlct, r, g, b, /get
   write_gif, filename, tvrd(), r, g, b
   
END
