import rds_config
from email_send import email_send

import pymysql


#******************* AWS RDS CONFIGURATION ***********************************************
#********************************************************************************************************

host='ec2-54-204-43-7.compute-1.amazonaws.com'
dbName=rds_config.db_name
uname=rds_config.db_username
upwd=rds_config.db_password
mail_user=rds_config.mail_user
mail_pwd=rds_config.mail_pwd

#********************** AWS RDS Connection Establisation ****************************************
try:
    #charset='utf8'
    conn = pymysql.connect(host=host,database=dbName, user=uname, password=upwd,charset='utf8',use_unicode=True)
    print('\n********************** AWS RDS Connection Establisation ****************************************\n')
except Exception as e:
    email_send('RDS_CONFIGURATION')
    print(e)
