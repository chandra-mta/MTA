pro find_gaps, infile

data=mrdfits(infile,1)

p=[data.time,0]-[0,data.time]
b=where(p gt 300,num)

print, "Start ", cxtime(min(data.time),'sec','cal')
print, "End ", cxtime(max(data.time),'sec','cal')
print, "Gaps:"
if (num gt 1) then begin
  for i = 1, num-1 do begin
    print, cxtime(data(b(i)-1:b(i)).time,'sec','cal')
  endfor
endif
end
