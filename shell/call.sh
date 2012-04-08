#!/bin/sh

TVIP=192.168.2.40

echo "Sending Incoming Call message to TV $TVIP ..."

POST -H 'SOAPACTION: "urn:samsung.com:service:MessageBoxService:1#AddMessage"' \
-c 'text/xml' http://$TVIP:52235/PMR/control/MessageBoxService \
< ../example/call.xml