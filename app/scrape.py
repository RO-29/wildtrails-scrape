import json
import requests
import os
import sys
from flask import Flask,jsonify
from flask import request, session, g, redirect, url_for, abort, flash, _app_ctx_stack, render_template
import datetime
from flask import Flask
from flask_cors import CORS, cross_origin
from bs4 import BeautifulSoup
import config
import datetime

app = Flask(__name__)
CORS(app)

def findGates(headingDiv):
    gatesHeading = headingDiv.findAll('td')
    gates = []
    if gatesHeading:
        gatesHeading.pop(0);gatesHeading.pop(0);
        for th in gatesHeading:
            gates.append(th.text)
    return gates

def findAvailabilty(gates, content):
    gypsyContent = {}
    dates = []
    for gypsySlot in content:
        gateSlot = gypsySlot.findAll('td')
        date, slot = gateSlot[0].text, gateSlot[1].text
        if date not in dates:
            dates.append(date)
        gateSlot.pop(0);gateSlot.pop(0);
        for i, numbers in enumerate(gateSlot):
            if gates[i] not in gypsyContent:
                gypsyContent[gates[i]] = {}
            if date not in gypsyContent[gates[i]]:
                gypsyContent[gates[i]][date] = []
            availability = numbers.a.text or numbers.a.get("title","closed")
            try:
                availability = int(availability)
            except ValueError:
                pass
            gypsyContent[gates[i]][date].append(
                {
                    'slot':slot,
                    'availability':availability
                }
            )
    return gypsyContent, dates

def extract_form_hiddens(soup, id = -1):
    '''
    Extract FORM hidden Values identified by their Id's.. return a list of Values
    '''
    tsManager       = soup.select("#ToolkitScriptManager1_HiddenField")[0]['value'] if soup.select("#ToolkitScriptManager1_HiddenField") else ""
    if id == 10:
        eventTarget = soup.select("#__EVENTTARGET")[0]['value'] if soup.select("#__EVENTTARGET") else config.ctlUtilityRajiv
    else:
        eventTarget = soup.select("#__EVENTTARGET")[0]['value'] if soup.select("#__EVENTTARGET") else config.ctlUtility
    eventArgument   = soup.select("#__EVENTARGUMENT")[0]['value'] if soup.select("#__EVENTARGUMENT") else ""
    lastFocus       = soup.select("#__LASTFOCUS")[0]['value'] if soup.select("#__LASTFOCUS") else ""
    viewstate       = soup.select("#__VIEWSTATE")[0]['value']
    eventValidation = soup.select("#__EVENTVALIDATION")[0]['value'] if soup.select("#__EVENTVALIDATION") else ""
    viewStateGen    = soup.select("#__VIEWSTATEGENERATOR")[0]['value'] if soup.select("#__VIEWSTATEGENERATOR") else ""
    return tsManager, eventTarget, eventArgument, lastFocus, viewstate,eventValidation,viewStateGen

def formData(soup, id = -1):
    config.formData['ToolkitScriptManager1_HiddenField'],\
    config.formData["__EVENTTARGET"],\
    config.formData["__EVENTARGUMENT"],\
    config.formData["__LASTFOCUS"],\
    config.formData["__VIEWSTATE"],\
    config.formData["__EVENTVALIDATION"],\
    config.formData["__VIEWSTATEGENERATOR"] = extract_form_hiddens(soup, id)
    return config.formData


def buildRajivContent(soup):
    types = []
    timesrange = []
    content = {}
    divs = soup.findAll('div')
    for divIndex, div in enumerate(divs):
        types.append(div.find('span').text)
        content[div.find('span').text] = {}
        times = div.findAll('li', {"class":"subHeadColor"})
        seats = div.findAll('li', {"class":"cellColor"})
        for i, time in enumerate(times):
            if time.text not in timesrange:
                timesrange.append(time.text)
            content[types[divIndex]][time.text] = seats[i].text
    return content, types ,timesrange

def extract_data_park_sanjay_gandhi(parkID, dateTime):
    headers = config.headers
    headers["Host"]    = "sgnp.mahaonline.gov.in"
    headers["Origin"]  = "https://sgnp.mahaonline.gov.in"
    headers["Referer"] = "https://sgnp.mahaonline.gov.in/NationalPark/Booking.aspx?ServiceID=2139"

    session = requests.session()
    res = session.get(config.BASE_URL_RAJIV, headers = headers ,verify=False)
    soup = BeautifulSoup(res.text,'lxml')
    config.formData = formData(soup, 10)
    config.formData[config.ctlUtilityRajiv] = dateTime
    res = session.post(config.BASE_URL_RAJIV, config.formData, headers = headers, verify=False)
    soup = BeautifulSoup(res.text,'lxml')
    content = soup.find("div", {"id":"pnlResource"})
    if content:
        return buildRajivContent(content)
    return {},[],[]

def extract_data_park(parkID, dateTime):
    if parkID =="10":
        return extract_data_park_sanjay_gandhi(parkID, dateTime)
    session = requests.session()
    res = session.get(config.BASE_URL,headers = config.headers, verify=False)
    soup = BeautifulSoup(res.text,'lxml')
    config.formData = formData(soup)
    config.formData[config.ctlUtility],config.formData[config.ctltxtDate] = parkID ,dateTime
    res = session.post(config.BASE_URL, config.formData, headers = config.headers, verify=False)
    soup = BeautifulSoup(res.text,'lxml')
    tableDiv = soup.find('div',{'id':'CPH_pnlFacility'})
    content = {}
    gates = []
    dates = []
    if tableDiv:
        tableDiv = tableDiv.findAll('table')
        gates = findGates(tableDiv[0])
        tableDiv.pop(0)
        content , dates = findAvailabilty(gates, tableDiv)
    return content, gates, dates

@app.route("/getSanctuaryMap", methods=["GET"])
def get_sanctuary_map():
    return jsonify(config.parksMapping)

@app.route("/getAvailability", methods = ["POST"])
def get_availability():
    date = request.json.get("date")
    sanctuary = config.parksMapping.get(str(request.json.get("sanctuary","")))
    if date:
        try:
            date = datetime.datetime.strptime(date,config.dateFormat).strftime(config.dateFormat)
        except (ValueError,SyntaxError, TypeError):
            date = ''
    if not date or not sanctuary:
        return jsonify({"error":"Invalid POST request body", "status":"HTTP_400_BAD_REQUEST"})

    content, gates, dates = extract_data_park(config.invParksMapping[sanctuary], date)
    return jsonify(
        {
            "sanctuaryName"  : sanctuary,
            "datesRange"     : dates,
            "sanctuaryZones" : gates,
            "dataZones"      : content,
        }
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0",port = 8020,debug = True)
