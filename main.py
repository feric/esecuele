#!/usr/bin/env python
#coding:utf-8
import requests
from sys import argv
from random import choice
from HTMLParser import HTMLParser
Agentes={
	'Chrome':'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36',
	'Google':'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)',
	'iExplorer':'Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; AS; rv:11.0) like Gecko',
	'Firefox':'Mozilla/5.0 (Windows NT 6.3; rv:36.0) Gecko/20100101 Firefox/36.0',
	'Safari':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.75.14 (KHTML, like Gecko) Version/7.0.3 Safari/7046A194A',
	'iPhone':'Mozilla/5.0 (iPhone; U; CPU iPhone OS 3_0 like Mac OS X; en-us) AppleWebKit/528.18 (KHTML, like Gecko) Version/4.0 Mobile/7A341 Safari/528.16',
	'Android':'Mozilla/5.0 (Linux; U; Android 4.0.3; ko-kr; LG-L160L Build/IML74K) AppleWebkit/534.30 (KHTML, like Gecko) Version/4.0 Mobile Safari/534.30'
}
def main():
	print ":D"
	try:
		server = argv[1]
	except:
		server = "http://www.altoromutual.com/bank/login.aspx"
	ua = choice(Agentes.keys())
	print ua
	cabeceras = {
	'User-Agent':Agentes.get(ua)
	}
	Response = str(requests.get(server,headers=cabeceras).text).lower()
	posIni = Response.find('post')
	posFin = Response.find('</form>',posIni)
	parametros = Response[posIni:posFin]
	datos = parametros[parametros.find('<table'):] 
	print datos
if __name__ == "__main__":
	main()
