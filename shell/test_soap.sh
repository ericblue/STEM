#!/bin/sh

TVIP=192.168.2.40

echo "Testing Personal Message SOAP Service on TV $TVIP ..."
GET http://$TVIP:52235/pmr/PersonalMessageReceiver.xml

echo "Testing Message Box Service SOAP Service on TV $TVIP ..."
GET http://$TVIP:52235/pmr/MessageBoxService.xml