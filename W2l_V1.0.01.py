# -*- coding: utf-8 -*-
"""
Created on Sat Apr 22 18:14:50 2023

@author: rtackett
"""
import dpkt
import socket
import pygeoip

# writes finished kmldoc to kml document to be summited to googlemaps
def pwrite(kmldoc):
    try:
        # creates document
        pcapkml = open('pcapkml.kml', 'a')
    except:
        # prints error
        print("failure to create document")
    try:
        # writes to the document
        pcapkml.write(kmldoc)
    except:
        # prints error
        print("failure to write to document")
    try:
        # closes document
        pcapkml.close()
    except:
        # prints error
        print("failure to close document")

# database containing geolocation data for ips that we give it
gi = pygeoip.GeoIP('GeoLiteCity.dat')

def retKML(dstip, srcip):
    # sets the dst (destination) ip address
    dst = gi.record_by_name(dstip)

    # sets the src (source) ip address use your public ip can be found on 'https://whatismyipaddress.com/'
    src = gi.record_by_name('131.150.163.37')
    try:
        #set destination longitude to dstlongitude
        dstlongitude = dst['longitude']
        
        #set destination latitude to dstlatitude
        dstlatitude = dst['latitude']
        
        #set source longitude to srclongitude
        srclongitude = src['longitude']
        
        #set source latitude to srclatitude
        srclatitude = src['latitude']

        kml = (
                  '<Placemark>\n'
                  '<name>%s</name>\n'
                  '<extrude>1</extrude>\n'
                  '<tessellate>1</tessellate>\n'
                  '<styleUrl>#transBluePoly</styleUrl>\n'
                  '<LineString>\n'
                  '<coordinates>%6f,%6f\n%6f,%6f</coordinates>\n'
                  '</LineString>\n'
                  '</Placemark>\n'
              ) % (dstip, dstlongitude, dstlatitude, srclongitude, srclatitude)
        return kml
    except:
        return ''
    
    
# loop over the pcap data and extract source and destination ip 
# addresses of each captured network packet
def plotIPs(pcap):
    kmlPts = ''
    # for each frame in the pcap file sets the correct data for source and destination
    for (ts, buf) in pcap:
        try:
            eth = dpkt.ethernet.Ethernet(buf)
            ip = eth.data
            src = socket.inet_ntoa(ip.src)
            dst = socket.inet_ntoa(ip.dst)
            # the attached geolocation data
            KML = retKML(dst,src)
            kmlPts = kmlPts + KML
        except: 
            pass
    return kmlPts
    
def main():
    #needs to be opened in binary format to be processed correctly 
    f = open('net_cap.pcap', 'rb')
    pcap = dpkt.pcap.Reader(f)
    
    # using a kml file a format that googlemaps can use
    # we set the style of how the data will be shown
    kmlheader = '<?xml version="1.0" encoding="UTF-8"?> \n<kml xmlns="http://www.opengis.net/kml/2.2">\n<Document>\n' \
                '<Style id="transBluePoly">' \
                '<LineStyle>' \
                '<width>1.5</width>' \
                '<color>501400E6</color>' \
                '</LineStyle>' \
                '</Style>'
    kmlfooter = '</Document>\n</kml>\n'
    
    # creates the full document to use 
    kmldoc = kmlheader + plotIPs(pcap) + kmlfooter
    pwrite(kmldoc)

if __name__ == '__main__':
    main()