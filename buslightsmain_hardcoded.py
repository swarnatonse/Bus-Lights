from __future__ import print_function
from twilio import twiml
from twilio.rest import TwilioRestClient
from flask import Flask, request
from datetime import datetime, timedelta
import dateutil.parser
import json
import requests
import pytz
import sys
import time
from circuitplayground import CircuitPlayground

eastern = pytz.timezone('US/Eastern')
routes_id = { '4001170' : '12',
              '4008432' : '37' }

routes_num = { '12' : '4001170',
               '37' : '4008432',
               'all' : '4001170%2C4008432' }
stops_name = { 'cc' : '4093766',
               'stone' : '4195938',
               'rawlings' : '4093246',
               'reitz' : '4093250' }

url = 'https://transloc-api-1-2.p.mashape.com/arrival-estimates.json?agencies=116&callback=call'
hds1 = {
            "X-Mashape-Key": "ayK260XAjgmshBGGBApDm4RaUEjSp1W7ktdjsngDEsOgWwRl5v",
            "Accept": "application/json"
        }
stop_flag = False

client = TwilioRestClient('AC967eb24d951cf34dc1d2337be54a052a','4e16db7df5b4c6661098bb0620922477')

port = 'COM4'
board = CircuitPlayground(port)
board.set_pixel_brightness(50)
scale = [262, 294, 330, 349, 392, 440, 494, 440, 392, 349, 330, 294, 262, 262, 294, 330, 349, 392, 440, 494, 440, 392, 349, 330, 294, 262, 262, 294, 330, 349, 392, 440, 494, 440, 392, 349, 330, 294, 262, 262, 294, 330, 349, 392, 440, 494, 440, 392, 349, 330, 294, 262]
duration = 250

def right_changed(data):
    global stop_flag
    print('Right button changed!')
    stop_flag = True
    return

def left_changed(data):
    global stop_flag
    print('Left button changed!')
    stop_flag = True
    return

board.set_pin_mode(4, board.INPUT, board.DIGITAL, left_changed)
board.set_pin_mode(19, board.INPUT, board.DIGITAL, right_changed)

def crazyboard(route):
    global stop_flag
    if route == '4001170':
        board.set_pixel(1, 139,69,19)
        board.set_pixel(2, 139,69,19)
        board.set_pixel(3, 139,69,19)
        board.set_pixel(4, 139,69,19)
        board.set_pixel(5, 139,69,19)
        board.set_pixel(6, 139,69,19)
    if route == '4008432':
        board.set_pixel(1, 128,0,128)
        board.set_pixel(2, 128,0,128)
        board.set_pixel(3, 128,0,128)
        board.set_pixel(4, 128,0,128)
        board.set_pixel(5, 128,0,128)
        board.set_pixel(6, 128,0,128)
    
    board.show_pixels()
    for note in scale:
        if stop_flag:
            print("button pressed!!!!!!!!!!!")
            break
        board.tone(note, duration)
        time.sleep((duration+100.0)/1000.0)
    board.clear_pixels()
    board.show_pixels()
    stop_flag = False
    return
        
    

app = Flask(__name__)


@app.route('/sms', methods=['POST'])
def sms():
    message = request.form['Body']
    number = request.form['From']
    message_body = message.split()
    resp = twiml.Response()
    estimate = ''
    counter = 0
    if message_body[0] == 'Start'or message_body[0] == 'START' or message_body[0] == 'start':
        route = message_body[1]
        threshold = message_body[2]
        url_send = url+'&routes='+routes_num[route]+'&stops=4093766'
        r = requests.get(url_send, headers=hds1)
        if(r.ok):
            estimate = json.loads(r.content.decode('utf-8'))
        t1 = timedelta(minutes=int(threshold))
        t2 = timedelta(minutes=int(threshold)+2)
        pock = 6
        while(r.ok):
##            if not estimate['data']:
##                client.messages.create(from_='(352) 224-9931',
##                                          to='(352) 870-3916',
##                                          body='There are no buses')
##                break
##            if estimate['data'][0]['arrivals'] is not None:
##                arr_time = dateutil.parser.parse(estimate['data'][0]['arrivals'][0]['arrival_at'])
##                curr_time = eastern.localize(datetime.now())
##                t = arr_time - curr_time
            t = timedelta(minutes = pock)
            if t >= t1 and t <= t2:
               client.messages.create(from_='(352) 224-9931',
                                      to='(352) 870-3916',
                                      body='Bus is arriving!')
               crazyboard(routes_num[route])                  
               break
            else:
                print("Wait")
                if counter > 30:
                    break
                time.sleep(60)
                counter += 1
                pock+=2
            r = requests.get(url_send, headers=hds1)
        resp.message("Done")

    else:
        resp.message("Command not found")            

    return str(resp)



if __name__ == '__main__':
    app.run()
    #app.run(debug=True, port=5000)

    
