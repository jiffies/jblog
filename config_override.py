
#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Override configurations.
'''
import sae.const
print "@@@@@@@@@@@@@@@@",sae.const.MYSQL_HOST
print "@@@@@@@@@@@@@@@@",sae.const.MYSQL_PORT
print "@@@@@@@@@@@@@@@@",sae.const.MYSQL_USER
print "@@@@@@@@@@@@@@@@",sae.const.MYSQL_PASS
print "@@@@@@@@@@@@@@@@",sae.const.MYSQL_DB

configs = {
    'db': {
        'host': sae.const.MYSQL_HOST,
        'port': sae.const.MYSQL_PORT,
        'user': sae.const.MYSQL_USER,
        'password': sae.const.MYSQL_PASS,
        'database': sae.const.MYSQL_DB,
    },
}
