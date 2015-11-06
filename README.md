# Cegatron
<b>python Cegatrong.py --request "http://example.net?id=123" --based error</b>
Options:

	-h, --help					- Show help message
	-v 						- Verbose mode (Show Request, payload & Response Headers)

Request:

	--request="http[s]://www.example.gob.mx?id=5"	- Url target to scan
	--method=[get|post]				- Method Get or Post to launch scan (Get by default)
	--user-agent="Googlebot/2.1"			- User Agent string to use
	--random-agent					- Random User Agent to use (by default)
	--data="param1=value1{sust}&param2=value2"	- Data used for post method (Use '{sust}' where you want insert payload [Mandatory use it!!!])
	--cookies="PHPSESSID=ue2;date=20151003"		- Cookie data to use a session
	--proxy="127.0.0.1:8080"			- Proxy ip and port to use at every query [http proxy by default]

Injection:

	--server=(MySQL,Postgres,Mssql)			- Database querys to use (by default use all queries)
	--based=[error|time]				- Force usage of given HTTP method (error based by default)
	--success="Success Phrase"			- String to compare when a response is correct
	--error="Error Phrase"				- String to compare when a response is incorrect
	--time=[1.5]					- Time to use in Time Based Attempt

Enumeration:

	--db 						- Retrieve Database names
	--dbname=db1,db2,db3				- Retrieve Table names of Databases specified
	--tables=table1,table2,table3			- Retrieve Column names of tables specified
	--columns=column1,column2			- Retrieve records of columns specified
