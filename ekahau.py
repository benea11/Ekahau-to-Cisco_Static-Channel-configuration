from zipfile import ZipFile
import json
import argparse
import pandas as pd
import ast
import netmiko
import getpass
import shutil

parser = argparse.ArgumentParser(
    description='Collect static channel assignment from ekahau and connect to a Cisco WLC to assign static channels')
parser.add_argument('file', metavar='file', help='Ekahau project file')
parser.add_argument('siteID', metavar='siteID', help='Consult iTOP')
parser.add_argument('userName', metavar='username', help='your administrator username for WLC access')
parser.add_argument('WlcIP', metavar='wlcIP', help='The IP Address of the WLC')

args = parser.parse_args()
pwd = getpass.getpass(prompt='Administrator Password:', stream=None)
eka_file = args.file
siteID = args.siteID
userName = args.userName
wlcIp = args.WlcIP
ap_Dict = {}
ap_Dict['accessPoints'] = []

#extract ekahau project to /project directory
with ZipFile(eka_file, 'r') as zip:
    zip.extractall('project')

#read access point and simulated radio JSON to retrieve data required
with open('project/accessPoints.json') as r:
    apJSON = json.load(r)

with open('project/simulatedRadios.json') as s:
    srJSON = json.load(s)

#build the dictionary by reading and comparing the two JSONs
for ap in apJSON['accessPoints']:
    ap_Name = ap['name']
    ap_Vendor = ap['vendor']
    ap_Model = ap['model'].split(' +')[0]
    ap_Id = ap['id']
    for sr in srJSON['simulatedRadios']:
        if ap['id'] == sr['accessPointId']:
            if sr['accessPointIndex'] == 1:
                ap_Channel5 = sr['channel']
            elif sr['accessPointIndex'] == 2:
                ap_Channel2 = sr['channel']
    ap_Dict['accessPoints'].append({
        #'id': ap_Id,
        'name': ap_Name,
        #'vendor': ap_Vendor,
        #'model': ap_Model,
        'channel_2g': ap_Channel2,
        'channel_5g': ap_Channel5
    })
#format the dictionary as a table, and print it.
pd.set_option("display.max_rows", None, "display.max_columns", None)
pda = pd.DataFrame.from_dict(ap_Dict['accessPoints'])
print(pda)
print("")
print("Verify AP and Channels above...")
print("")
print("Are you sure you want to continue? Y/N..")
confirmation = input("")
confirmation = confirmation.upper()
#if user confirms the changes, proceed, test connection to WLC, then execute changes line by line
if confirmation == "Y":
    for ap in ap_Dict['accessPoints']:
        print('config ap disable ' + ap['name'])
        print('config 802.11a channel ap ' + ap['name'], ap['channel_5g'][0])
        print('config ap enable ' + ap['name'])
    #while True:
        #try:
            #ConnectHandler(ip = args.WlcIP, port = 22, username = args.userName, password = pwd, device_type = 'cisco_wlc')
        # except:
        #    exit_str = 1
        #if exit_str == 1:
        #    print('Something went wrong while connecting to the WLC ')
        #    exit()
        #with ConnectHandler(ip = args.h, port = 22, username = args.u, password = pwd, device_type = 'cisco_wlc') as ch:
            #ch.send_command_timing("config paging disable")
            #for ap in ap_Dict['accessPoints']:
                #ch.send_command_timing("config ap disable " + ap['name'])
                #ch.send_command_timing("config 802.11a channel ap " + ap['name'] + " " + ap['Channel5']
                #ch.send_command_timing('config ap enable ' + ap['name'])
                #ch.disconnect()
shutil.rmtree('project')