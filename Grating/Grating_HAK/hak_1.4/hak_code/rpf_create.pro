PRO rpf_create, rpf, HEADER=rpf_header
;+
; PRO rpf_create, rpf, HEADER=rpf_header
;
; This procedure creates and returns an rpf structure
; and a generic rpf_header.
;
; For more information see:  <this_directory>/rpf_description.txt
;     -------------------------------------------------
; 7/3/99 dd
;     -------------------------------------------------
;-

; Create and initialize the rpf structure
rpf = REPLICATE({Name:'rpf_creation_time', $
	DataType:'StringValue', $
	ScalarValue:DOUBLE(0.0), Unit:'', Error:DOUBLE(0.0), $
	StringValue:SYSTIME(), Description:''},1)

; Create the rpf_header
rpf_header = ['# ', $
		'# rdb parameter file ("rpf") format', $
		'# ']

RETURN
END
