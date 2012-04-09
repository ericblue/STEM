#!/usr/bin/perl

# $Id: call.cgi,v 1.1 2012-04-09 16:12:17 ericblue76 Exp $
#
# Author: Eric Blue - http://eric-blue.com
# Project: STEM - Samsung TV Enhanced Messaging
# Description:  Sends call notifications to your Samsung TV using Twilio (http://www.twilio.com/)
#
#


use CGI;
use CGI::Carp qw/fatalsToBrowser/;
use LWP::UserAgent;
use HTTP::Request;
use XML::Simple;
use HTML::Entities;
use Data::Dumper;
use POSIX;
use Carp;
use strict;

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
    <Dial>
        <Number>
            $config->{'forward_phone'}
        </Number>
    </Dial>
</Response>
};

my $cgi = CGI->new();

my $from_phone = $cgi->param('From');
$from_phone = "Unknown" if !defined($from_phone);

# Only available if you have Caller Name Lookup enabled in Twilio

my $caller_name = $cgi->param('CallerName');
$caller_name = "Unknown Caller" if !defined($caller_name);

my $from_city = $cgi->param('FromCity');
$from_phone = "Unknown City" if !defined($from_city);

my $from_state = $cgi->param('FromState');
$from_state = "Unknown State" if !defined($from_state);


my $call = {
	Category    => 'Incoming Call',
	DisplayType => 'Maximum',
	CallTime    => {
		Date => strftime( "%Y-%m-%d", localtime),
		Time => strftime( "%H:%M:%S", localtime)
	},
	Callee => {
		Name   => 'Me',
		Number => $config->{'forward_phone'}
	},
	Caller => {
		Name   => "$caller_name ($from_city, $from_state)",
		Number => $from_phone
	}
};

my $call_xml = XMLout( $call, RootName => undef, NoAttr => 1 );
my $call_xml_encoded = encode_entities($call_xml);
chop $call_xml_encoded;

# Load the template SOAP body and insert the encoded XML message

open( TEMPLATE, "template/soap_envelope.tpl" )
  or die "Can't open SOAP envelope!";
my $soap_envelope = do { local ($/); <TEMPLATE> };
close(TEMPLATE);

my $message = $soap_envelope;
$message =~ s/\$MESSAGE\$/$call_xml_encoded/;

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

