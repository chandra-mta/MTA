//
// --- updated date for each page
//

function writeDate() {
    var months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']; 
    var theDate = new Date(document.lastModified);
    theDate.setTime((theDate.getTime()+(5000*60*60)) )
    with (theDate) {
        var year = 1900 + getYear()
        document.write("<i>Last Updated: " + months[getMonth()] + ' '+getDate() + ',  '+ year +"</i>")
    } 
}

//
// --- main page updated date
//

function writeDate2 () {
    var months = ['January', 'Febraury', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'];
    var theDate = new Date(document.lastModified);
    theDate.setTime((theDate.getTime()+(5000*60*60)) )
    with (theDate) {
        var year = 1900 + getYear()
        document.write("<i>Last Updated: " + months[getMonth()] + ' '+getDate() + ',  '+ year +"</i>")
    } 
}
