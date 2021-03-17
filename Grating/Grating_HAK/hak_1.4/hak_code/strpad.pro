FUNCTION strpad, in_str, total_length, CLIP=clip, COMPRESS = compress, $
	RIGHT = right
;+
; FUNCTION strpad, in_str, total_length, CLIP=clip, COMPRESS = compress, $
;	RIGHT = right
;
; Pad a string out to the size total_length
; If CLIP keyword is present then clip longer inputs to that size as well.
; If COMPRESS is present, then all white space is removed before padding
; by applying STRCOMPRESS( /REMOVE_ALL) to the input.
; If RIGHT is set then right justify the output.
;    -------------------------------------------------------------
;-

input_string = in_str

if KEYWORD_SET(COMPRESS) then input_string = STRCOMPRESS(in_str,/REMOVE_ALL)

in_len = STRLEN(input_string)
if in_len GE total_length then begin
  ; string is already long enough (keep extra too)
  padded = input_string
  ; clip it to length if desired
  if KEYWORD_SET(CLIP) then begin
    padded = STRMID(padded,0,total_length)
  end
end else begin
  padded = input_string
  if KEYWORD_SET(RIGHT) then begin
    for ip = 1, total_length - in_len  do padded = ' ' + padded
  end else begin
    for ip = 1, total_length - in_len  do padded = padded + ' '
  end
end

RETURN, padded
END
