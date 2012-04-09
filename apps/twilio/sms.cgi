#!/usr/bin/perl

# $Id: sms.cgi,v 1.1 2012-04-09 16:12:17 ericblue76 Exp $
#
# Author: Eric Blue - http://eric-blue.com
# Project: STEM - Samsung TV Enhanced Messaging
# Description:  Sends SMS messages to your Samsung TV using Twilio (http://www.twilio.com/)
#
#

use CGI;
use CGI::Carp qw/fatalsToBrowser/;
use LWP::UserAgent;
use HTTP::Request;
use XML::Simple;
use HTML::Entities;
use POSIX;
use Carp;
use strict;

# TODO Add time of day settings to only send notifications in the evenings and on weekends

sub load_config {

    my ($filename) = @_;

    $/ = "";
    open( CONFIG, "$filename" ) or croak "Can't open config $filename!";
    my $config_file = <CONFIG>;
    close(CONFIG);
    undef $/;

    my $config = eval($config_file) or croak "Invalid config file format!";

    return $config;

}

# Load config, or just define them inline
my $config = load_config("stem.cnf");

print "Content-type: text/xml\n\n";

# Have Twilio forward to your normal number while the notification to your TV happens
print qq{<?xml version="1.0" encoding="UTF-8"?>};

print qq{ 
<Response> 
    <Sms>Message Recieved</Sms>
</Response>
};

my $cgi = CGI->new();

my $from_phone = $cgi->param('From');
$from_phone = "Unknown" if !defined($from_phone);

my $body = $cgi->param('Body');

my $from_city = $cgi->param('FromCity');
$from_phone = "Unknown City" if !defined($from_city);

my $from_state = $cgi->param('FromState');
$from_state = "Unknown State" if !defined($from_state);


my $sms = {
	Category    => 'SMS',
	DisplayType => 'Maximum',
	ReceiveTime    => {
		Date => strftime( "%Y-%m-%d", localtime),
		Time => strftime( "%H:%M:%S", localtime)
	},
	Receiver => {
		Name   => 'Me',
		Number => $config->{'forward_phone'}
	},
	Sender => {
		Name   => "$from_city, $from_state",
		Number => $from_phone
	},
	Body => $body
};

my $sms_xml = XMLout( $sms, RootName => undef, NoAttr => 1 );
my $sms_xml_encoded = encode_entities($sms_xml);
chop $sms_xml_encoded;

# Load the template SOAP body and insert the encoded XML message

open( TEMPLATE, "template/soap_envelope.tpl" )
  or die "Can't open SOAP envelope!";
my $soap_envelope = do { local ($/); <TEMPLATE> };
close(TEMPLATE);

my $message = $soap_envelope;
$message =~ s/\$MESSAGE\$/$sms_xml_encoded/;

# Send the call notification to the TV

my $userAgent = LWP::UserAgent->new();
my $request   =
  HTTP::Request->new(
	POST => "http://$config->{'tvip'}:52235/PMR/control/MessageBoxService" );
$request->header(
	SOAPAction => '"urn:samsung.com:service:MessageBoxService:1#AddMessage"' );
$request->content($message);
$request->content_type("text/xml; charset=utf-8");

my $response = $userAgent->request($request);

if($response->code != 200) {
	warn $response->error_as_HTML;
}

