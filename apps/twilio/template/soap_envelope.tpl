<?xml version="1.0" encoding="UTF-8"?>
<s:Envelope s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/" xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" >
	<s:Body>
		<u:AddMessage xmlns:u="urn:samsung.com:service:MessageBoxService:1">
			<MessageID>1</MessageID>
			<MessageType>text/xml</MessageType>
				<Message>
				$MESSAGE$
				</Message>
		</u:AddMessage>
	</s:Body>
</s:Envelope>