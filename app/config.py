import datetime

BASE_URL = "https://nationalpark.mahaonline.gov.in/User/Availability.aspx"
BASE_URL_RAJIV = "https://sgnp.mahaonline.gov.in/NationalPark/Booking.aspx?ServiceID=2139"
ctlUtility = "ctl00$CPH$ddlUtility"
ctltxtDate = "ctl00$CPH$txtDate"
ctlUtilityRajiv = "ctl00$ContentPlaceHolder1$txtValidFrom"

headers = {
            "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Encoding":"gzip, deflate, br",
            "Accept-Language":"en-US,en;q=0.8",
            "Cache-Control":"max-age=0",
            "Connection":"keep-alive",
            "Content-Type":"application/x-www-form-urlencoded",
            "Host":"nationalpark.mahaonline.gov.in",
            "Origin":"https://nationalpark.mahaonline.gov.in",
            "Referer":"https://nationalpark.mahaonline.gov.in/User/Availability.aspx",
            "Upgrade-Insecure-Requests":"1",
            "User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36"
          }

parksMapping =   {
                    "1":"Pench Tiger Reserve",
                    "3":"Bor Sanctuary",
                    "4":"Nawegaon-nagzira Tiger Reserve",
                	"7":"Tadoba-Andhari Tiger Reserve",
                    "8":"Umred - Kharandla Sanctuary",
                    "9":"Tippeshwar Wildlife Sanctuary",
                    "10":"Sanjay Gandhi",
                    "11":"Sipna Wildlife Melghat Tiger Reserve",
                    "12":"Gugamal Wildlife Melghat Tiger Reserve",
                    "13":"Akot Wildlife Melghat Tiger Reserve",
                }
invParksMapping = {v: k for k, v in parksMapping.items()}


dateFormat = "%d-%m-%Y"

formData = {
		'ToolkitScriptManager1_HiddenField':'',
		'__EVENTTARGET':'',
		'__EVENTARGUMENT':'',
		'__LASTFOCUS':'' ,
		'__VIEWSTATE':"",
        "__EVENTVALIDATION":"",
        ctlUtility : 1,
        ctltxtDate : datetime.datetime.now().strftime(dateFormat)
		}
