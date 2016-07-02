import datetime
from suds.client import Client
import xml.etree.ElementTree as ET
import re
from xml.dom import minidom

AUTH_URL = 'http://search.webofknowledge.com/esti/wokmws/ws/WOKMWSAuthenticate?wsdl'
SEARCH_URL = 'http://search.webofknowledge.com/esti/wokmws/ws/WokSearch?wsdl'


#query = 'AU = Fabila-Monroy* Ruy*'

#edition= {'collection' : 'WOS', 'edition' : 'SCI'} 


def SetQueryToSoap(query,databaseId = 'WOK',queryLanguage='en',timeSpanStart = datetime.date(1900,01,01),timeSpanEnd=datetime.datetime.now().date()):

	soap =  {'databaseId' : databaseId, 'userQuery' : query, 'queryLanguage': queryLanguage}
	soaptime = {}
	#if edition is not None:soap['editions']=edition
	soaptime['begin'] = timeSpanStart.isoformat()
	soaptime['end'] = timeSpanEnd.isoformat()
	if soaptime:
		soap['timeSpan'] = soaptime
	return soap

def retrieveParamToSoap():
	soap = {
			
			'firstRecord' : 1,
			'count':100
		}
	return soap

def setQuery(quer):
	query = quer

def closeSOAPsession(authClient):
	authClient.service.closeSession()

def search_author(query):
	authClient=Client(AUTH_URL)
	SID=authClient.service.authenticate()

	headers = { 'Cookie': 'SID='+SID}
	authClient.set_options(soapheaders=headers)
	searchClient=Client(SEARCH_URL,headers=headers)
	
	setquery=SetQueryToSoap(query)#setquery=SetQueryToSoap('AU = Fabila-Monroy* Ruy*')
	#setQuery('AU = Fabila Ruy')
	
	setretrieve=retrieveParamToSoap()
	resp=searchClient.factory.create('searchResponse')
	resp=searchClient.service.search(setquery,setretrieve)
	records = re.sub(' xmlns="http://scientific.thomsonreuters.com/schema/wok5.4/public/FullRecord"', '', resp.records, count=1)
	recordsTree=ET.fromstring(records)
	for rec in recordsTree.iter('REC'):for author in rec.findall('static_data/summary/names/name'):
			if author.attrib['role']=='author':
				if 'dais_id' in author.attrib :
					auth={str(author.attrib['dais_id']):dict()}
					key_temp=str(author.attrib['dais_id'])
	


def parseresponse(resp):
	list_records=[]
	records = re.sub(' xmlns="http://scientific.thomsonreuters.com/schema/wok5.4/public/FullRecord"', '', resp.records, count=1)
	recordsTree=ET.fromstring(records)
	for rec in recordsTree.iter('REC'):
		record ={"UID":rec.find('UID').text}#Encuentra el valor que se encuentra dentro de las etiquetas UID
		#PUBYEAR
		record['pubyear']=None
		date=rec.find('static_data/summary/pub_info')
		if 'pubyear' in date.attrib:
			record['pubyear']=date.attrib['pubyear']
		#SOURCE AND TITLE PAPER
		record['source']=None
		record['title']=None
		for title in rec.findall('static_data/summary/titles/title'):
			if title.attrib['type']=='source':
				record['source']=title.text
			if title.attrib['type']=='item':
				record['title']=title.text
		#AUTHORS
		record['authors']=dict()
		for author in rec.findall('static_data/summary/names/name'):
			if author.attrib['role']=='author':
				if 'dais_id' in author.attrib :
					auth={str(author.attrib['dais_id']):dict()}
					key_temp=str(author.attrib['dais_id'])
				else:
					if 'daisng_id' in author.attrib:
						auth={str(author.attrib['daisng_id']):dict()}
						key_temp=str(author.attrib['daisng_id'])	
					else:
						auth={'-':dict()}#Change
						key_temp="-"
				if author.find('display_name') is not None:
					auth[key_temp]['display_name']=author.find('display_name').text
				else:
					auth[key_temp]['display_name']=None
				if author.find('full_name') is not None:
					auth[key_temp]['full_name']=author.find('full_name').text
				else:
					auth[key_temp]['full_name']=None
				if author.find('wos_standard') is not None:
					auth[key_temp]['wos_standard']=author.find('wos_standard').text
				else:
					auth[key_temp]['wos_standard']=None
				if author.find('wos_standard') is not None:
					auth[key_temp]['wos_standard']=author.find('wos_standard').text
				else:
					auth[key_temp]['wos_standard']=None
				if 'addr_no' in author.attrib:
					auth[key_temp]['addr_number']=(author.attrib['addr_no']).split()
			record['authors'].update(auth)
		#ADRESSES
		record['adresses']=dict()
		for adresses in rec.findall('static_data/fullrecord_metadata/addresses/address_name'):
			address={str(adresses.find('address_spec').attrib['addr_no']):adresses.find('address_spec/full_address').text}
			record['adresses'].update(address)
		list_records.append(record)
	return list_records

def format_xml_from_raw(resp):
	records = re.sub(' xmlns="http://scientific.thomsonreuters.com/schema/wok5.4/public/FullRecord"', '', resp.records, count=1)
	recordsTree = ET.fromstring(records)
	rough_string = ET.tostring(recordsTree, 'utf-8')
	reparsed = minidom.parseString(rough_string)
	with open("/home/gerry/file.xml", 'wb') as fp:
		reparsed.writexml(fp, indent="", addindent="\t", newl="\n")


def main():
	authClient=Client(AUTH_URL)
	SID=authClient.service.authenticate()
	headers = { 'Cookie': 'SID='+SID}
	authClient.set_options(soapheaders=headers)
	searchClient=Client(SEARCH_URL,headers= { 'Cookie': 'SID='+SID})
	#setQuery('AU = Fabila Ruy')
	setquery=SetQueryToSoap('AU = Fabila-Monroy* Ruy*')
	setretrieve=retrieveParamToSoap()
	resp=searchClient.factory.create('searchResponse')
	resp=searchClient.service.search(setquery,setretrieve)
	print parseresponse(resp)
main()
 