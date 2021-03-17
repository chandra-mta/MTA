x = mta_rad('2018:054')
spawn, 'mv rad_cnts.gif rad_cnts_curr.gif'
spawn, 'mv rad_use.gif rad_use_curr.gif'
print, 'Done current'
retall
x = mta_rad('2018:061.0','2018:090')
spawn, 'mv rad_cnts.gif rad_cnts_mar18.gif'
spawn, 'mv rad_use.gif rad_use_mar18.gif'
spawn, 'mv eph_diff.gif eph_diff_mar18.gif'
spawn, 'mv mon_diff.gif mon_diff_mar18.gif'
spawn, 'mv per_diff.gif per_diff_mar18.gif'
spawn, 'mv xper_diff.gif mon_per_diff_mar18.gif'
print, 'Done mar18'
x = mta_rad('2017:001','2018:001')
spawn, 'mv rad_cnts.gif rad_cnts_17.gif'
spawn, 'mv rad_use.gif rad_use_17.gif'
spawn, 'mv eph_diff.gif eph_diff_17.gif'
spawn, 'mv mon_diff.gif mon_diff_17.gif'
spawn, 'mv per_diff.gif per_diff_17.gif'
spawn, 'mv xper_diff.gif mon_per_diff_17.gif'
print, 'Done 17'
x = mta_rad('2017:084','2018:084')
spawn, 'mv rad_cnts.gif rad_cnts_last_one_year.gif'
spawn, 'mv rad_use.gif rad_use_last_one_year.gif'
spawn, 'mv eph_diff.gif eph_diff_last_one_year.gif'
spawn, 'mv mon_diff.gif mon_diff_last_one_year.gif'
spawn, 'mv per_diff.gif per_diff_last_one_year.gif'
spawn, 'mv xper_diff.gif mon_per_diff_last_one_year.gif'
print, 'Done Last One Year
x = mta_rad()
spawn, 'mv rad_cnts.gif rad_cnts_all.gif'
spawn, 'mv rad_use.gif rad_use_all.gif'
spawn, 'mv eph_diff.gif eph_diff_all.gif'
spawn, 'mv mon_diff.gif mon_diff_all.gif'
spawn, 'mv per_diff.gif per_diff_all.gif'
print, 'Done all'
retall
exit
