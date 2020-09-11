#!/usr/bin/env python3
# by Yiwen Shen (SKKU)
# Email: chrisshen@g.skku.edu

import socket
import time
import bluetooth
import sys
import threading

import ScanUtility
import bluetooth._bluetooth as bluez

#Set bluetooth device. Default 0.
beacons4Server = {}

seq = 0
# byteData = B""



def rcvdBeacon():
    global seq
    global thread_kill
    dev_id = 0
    try:
        sock = bluez.hci_open_dev(dev_id)
        print ("\n *** Looking for BLE Beacons ***\n")
        print ("\n *** CTRL-C to Cancel ***\n")
    except:
        print ("Error accessing bluetooth")

    ScanUtility.hci_enable_le_scan(sock)
    
    t=0.0
    #Scans for iBeacons
    try:
        while True:
            returnedList = ScanUtility.parse_events(sock, 100)
            #print(time.time(), returnedList)
            
            if returnedList:
                for item in returnedList:
                    if seq >= 12:
                        seq = 0
                    else:
                        seq += 1                
                    # print(item)
                    # byteData = item
                    #if beacons4Server[item['uuid']][1]
                    beacons4Server[item['uuid']] = [item['rssi'],seq]
                    #interval=time.time()-t
                    #print(interval, beacons4Server)
                    print(" ")
            else:
                for item in returnedList:
                    beacons4Server[item['uuid']] = [0.0, -1]

            returnedList.clear()
            
            if thread_kill:
                break
                #t=time.time()
    except KeyboardInterrupt:
        pass

def collectRSSI():
    # IPv4
    # client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # client.settimeout(0.2)
    currSeq = 0
    prevSeq = 0
    count = 0
    while True:
        message = ""

        for key, val in beacons4Server.items():
            message = str(time.time())+","+str(key)+","+str(val[0])+","+str(val[1])+"\n"
            currSeq = val[1]
        
        # print(currSeq, prevSeq)
        if currSeq != -1 and currSeq != prevSeq:
            print(message)
            prevSeq = currSeq
            count += 1
            with open('rssidata.csv', 'a') as f:
                f.write(message)
        else:
            pass
            # print("")
        # encodedMsg = message.encode(encoding="utf-8")
        # print(encodedMsg)

        # print(byteData)
        # client.sendto(encodedMsg, ('192.168.0.5', 6000)) # 2001:db8:100:15a::3

        # print("message sent!")
        
        if count == 500:
            thread_kill = True
            break
        
        time.sleep(0.02)

if __name__ == "__main__":
    # rcvdBeacon()
    thread_kill = False
    rcvdBeaconTh = threading.Thread(target=rcvdBeacon, args=())
    rcvdBeaconTh.start()

    udpSendBeaconTh = threading.Thread(target=collectRSSI, args=())
    udpSendBeaconTh.start()

