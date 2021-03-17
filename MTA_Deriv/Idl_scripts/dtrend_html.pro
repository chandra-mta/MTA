PRO DTREND_HTML, mintime, maxtime, text, file, label
; write dtrend html page
; 12.JUL2002 BDS added window.document.close() for netscape6

; constants
speryr = 31536000.

; setup html file
get_lun, sunit ; file unit for stat ouput
openw, sunit, file
printf, sunit, '<HTML>'
printf, sunit, '<HEAD>'
printf, sunit, '     <TITLE>'+strupcase(label)+'_AVG Trends</TITLE>'
printf, sunit, '</HEAD>'
printf, sunit, '<BODY TEXT="#DDDDDD" BGCOLOR="#000000"'+ $
               'LINK="#00CCFF" VLINK="#EEEEEE" ALINK="#7500FF">'
printf, sunit, '<h1><center>'+strupcase(label)+'   Trends</center></h1>'
printf, sunit, '<br><hr><br>'

; this part is terribly confusing
;  you need both kinds of quotes, so have to switch back and forth
printf, sunit, ''
printf, sunit, '<script language="JavaScript">'
printf, sunit, '  function WindowOpener(imgname) {'
printf, sunit, '    msgWindow = open("","displayname",'+ $
               '"toolbar=no,directories=no,menubar=no,'+ $
               'location=no,scrollbars=no,status=no,'+ $
               'width=1024,height=850,resize=no");'
printf, sunit, '    msgWindow.document.clear();'
printf, sunit, '    msgWindow.document.write("<HTML><TITLE>Trend plot:   "'+ $
               '+imgname+"</TITLE>");'
printf, sunit, '    msgWindow.document.write("<BODY TEXT='+"'white'"+ $
               ' BGCOLOR='+"'black'"+'>");'
printf, sunit, '    msgWindow.document.write("<A HREF='+ $
               "'convert.cgi?file="+'"+imgname+"'+"' target=_blank"+  $
               '>Postscript Version</a><br/>");'
printf, sunit, '    msgWindow.document.write("<IMG SRC='+"'"+'"'+ $
               '+imgname+'+ $
               '"'+"'"+' BORDER=0><P></BODY></HTML>");'
printf, sunit, '    msgWindow.document.close();'
printf, sunit, '    msgWindow.focus();'
printf, sunit, '  }'
printf, sunit, '</script>'
printf, sunit, ''

printf, sunit, '<table width=100% border=0>'
printf, sunit, '<tr>'
printf, sunit, '<td align=center colspan=2>Last updated: '
update = systime(1) - speryr*21 - 7*(speryr+86400)
printf, sunit, strtrim(cxtime(update,'sec','cal'),2)
printf, sunit, 'DOM '
printf, sunit, strtrim(string(fix(cxtime(update,'sec','met'))),2)
printf, sunit, '</td></tr>'
printf, sunit, '<td align=left>Data start: '
printf, sunit, strtrim(cxtime(mintime,'sec','cal'),2)
printf, sunit, 'DOM '
printf, sunit, strtrim(string(fix(cxtime(mintime,'sec','met'))),2)
printf, sunit, '</td>'
printf, sunit, '<td align=right>Data end: '
printf, sunit, strtrim(cxtime(maxtime,'sec','cal'),2)
printf, sunit, 'DOM '
printf, sunit, strtrim(string(fix(cxtime(maxtime,'sec','met'))),2)
printf, sunit, '</td>'
printf, sunit, '</tr>'
printf, sunit, '</table>'

printf, sunit, '<br><hr><br>'
printf, sunit, '<center>'
printf, sunit, '<table border=1 cellpadding=3>'

for i=0, n_elements(text)-1 do begin
  printf, sunit, text(i)
endfor

printf, sunit, '</table>'
printf, sunit, '</center>'
printf, sunit, '</body></html>'
close, sunit
free_lun, sunit
end
