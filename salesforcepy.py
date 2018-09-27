from flask import Flask, render_template,request,url_for,redirect,flash,session
import random
import os
import psycopg2

from flask.ext.sqlalchemy import SQLAlchemy
#from refresh_token import refresh_token,instance_url
from flask import request


import requests
import json
from pprint import pprint

import rds_config

dbName=rds_config.db_name
uname=rds_config.db_username
upwd=rds_config.db_password
host=rds_config.host
#session={}


redirect_url='https://sfdcschemapy.herokuapp.com/getcode'
app = Flask(__name__)
app.secret_key = 'any random string'
con='postgres://'+uname+':'+upwd+'@'+host+':5432/'+dbName
print(con)
app.config['1'] = 'postgres://'+uname+':'+upwd+'@'+host+':5432/'+dbName

db = SQLAlchemy(app)


@app.route('/',methods = ['get','POST'])
def home():
  error=request.args.get('error')
  success=request.args.get('success')
  logout=request.args.get('logout')
  #sucess=None
  if request.method == 'POST':
        client_id="3MVG9YDQS5WtC11oVIcikfdzsMBHOXFw2S3t38tAgNZFSKA10ews9pMB.mejIcW871MS3uV6z_6CDkCmh7owz"
        print(client_id)
        redirect_url="https://sfdcschemapy.herokuapp.com/getcode"
        params = {"response_type":"code","client_id":client_id,"redirect_uri":redirect_url}
        url = "https://login.salesforce.com/services/oauth2/authorize"
        querystring = {"redirect_uri":"https://sfdcschemapy.herokuapp.com/getcode","client_id":"3MVG9YDQS5WtC11oVIcikfdzsMBHOXFw2S3t38tAgNZFSKA10ews9pMB.mejIcW871MS3uV6z_6CDkCmh7owz","response_type":"code"}
        response = requests.request("POST", url, params=querystring)
        print(response.url)
        #print(response.params)
        #print(response.headers)
        return response.text
        
  else:
    return render_template('home.html',error=error,success=success,logout=logout)

@app.route('/about')
def about():
  return render_template('about.html')


@app.route('/logout')

def logout():
    
    if  session:
        print("session.clear()")
        session.clear()
        #session.pop('username',None)
        #session['username']=''
        return redirect(url_for('home',logout='logout successfully'))
    else:
        session.clear()
        #session.pop('username',None)
        return 'should login'

@app.route('/Signup', methods = ['get','POST'])
def Signup():
    global dbName,uname,upwd,host
    dbName=rds_config.db_name
    uname=rds_config.db_username
    upwd=rds_config.db_password
    host=rds_config.host
    error=None
    if request.method == 'POST':
      name = request.form['name']
      pwd = request.form['pwd']
      repwd = request.form['repwd']
      if pwd!=repwd:
        error = 'Didnot match the password'
        return render_template('Signup.html',error=error)
      elif pwd=='' and name=='' :
        error = 'name and password should not be empty'
        return render_template('Signup.html',error=error)
      elif name=='':
        error = 'name should not be empty'
        return render_template('Signup.html',error=error)
      elif pwd=='':
        error = 'password should not be empty'
        return render_template('Signup.html',error=error)
      else:
        con = psycopg2.connect(host=host,database=dbName, user=uname, password=upwd)  
        cur = con.cursor()
        cur.execute("CREATE TABLE IF NOT EXISTS users(id SERIAL UNIQUE, Name VARCHAR(20), pwd VARCHAR(20), refresh_token VARCHAR(100), instance_url VARCHAR(100)) ")
            
        
        quer = "SELECT Name FROM users WHERE Name=%s"
        cur.execute(quer,(name,))
        
        
        getrows = cur.rowcount
        con.commit()
        con.close()
        if getrows==0:
            con = psycopg2.connect(host=host,database=dbName, user=uname, password=upwd)  
            cur = con.cursor()
            cur.execute("CREATE TABLE IF NOT EXISTS users( Name VARCHAR(20), pwd VARCHAR(20), refresh_token VARCHAR(100), instance_url VARCHAR(100)) ")
            con.commit()
            query = "INSERT INTO users ( Name, pwd) VALUES ( %s, %s)"
            cur.execute(query, (name, pwd))
            con.commit()
            con.close()
            
            
            return redirect(url_for('Login'))
        else:
            error = 'User already Exist'
            return render_template('Signup.html',error=error)
        
    else:
      return render_template('Signup.html',error=error)
      
      
      

@app.route('/Login',methods = ['GET','POST'] )
def Login(guest=''):
    global dbName,uname,upwd,host
    dbName=rds_config.db_name
    uname=rds_config.db_username
    upwd=rds_config.db_password
    host=rds_config.host
    
    error=None
    #print('login before->',session['username'])
    if request.method == 'POST':
      lname = request.form['lname']
      lpwd = request.form['lpwd']
      session['username'] = request.form['lname']
      
      
      if lpwd=='' and lname=='' :
        error = 'name and password should not be empty'
        return render_template('Login.html',error=error)
      elif lname=='':
        error = 'name should not be empty'
        return render_template('Login.html',error=error)
      elif lpwd=='':
        error = 'password should not be empty'
        return render_template('Login.html',error=error)
      elif lpwd=='admin' and lname=='admin':
          flash('You were successfully logged in')
          return redirect(url_for('Login'))
       
        
      elif lpwd!='' and lname!='' :
        
        con = psycopg2.connect(host=host,database=dbName, user=uname, password=upwd)  
        cur = con.cursor()
        quer = "SELECT id,Name,pwd,access_token FROM users WHERE Name=%s and pwd=%s"
        #quer = "SELECT id,Name,pwd,access_token FROM users WHERE Name='{}' and pwd='{}'".format(lname,lpwd)
        print(quer)
        cur.execute(quer,(lname,lpwd))
        #cur.execute(quer)
        print
        
        
        getrows = cur.rowcount
        for r in cur:
            print('id-->',r[0])
            keyid=r[0]
            access_token=r[3]
        con.commit()
        con.close()
        if getrows==1:
          
          session['username']=lname
          print('login->',session['username'])
          session['access_token']=access_token
          print(session['username'],          session['access_token'])
          return redirect(url_for('home'))
          
          '''else:
            return "records found"'''
        else:
            error="Invalid User"
            return render_template('Login.html',error=error)
        
    else:
      
      return render_template('Login.html')


@app.route('/<string:name>/home/',methods = ['get','POST'])
def loginhome(name):
    global refresh_token,instance_url,redirect_url
    error=None
    print('\n *************eneterd into loginhome method******** \n')
    if request.method == 'POST':
        client_id="3MVG9YDQS5WtC11oVIcikfdzsMBHOXFw2S3t38tAgNZFSKA10ews9pMB.mejIcW871MS3uV6z_6CDkCmh7owz"
        params = {"response_type":"code","client_id":client_id,"redirect_uri":redirect_url}
        url = "https://login.salesforce.com/services/oauth2/authorize"
        querystring = {"redirect_uri":"https://sfdcschemapy.herokuapp.com/getcode","client_id":"3MVG9YDQS5WtC11oVIcikfdzsMBHOXFw2S3t38tAgNZFSKA10ews9pMB.mejIcW871MS3uV6z_6CDkCmh7owz","response_type":"code"}
        response = requests.request("POST", url, params=querystring)
        print(response.url)
        #print(response.params)
        #print(response.headers)
        return response.text
    else:
        return render_template('home.html',error=error)

#@app.route('/getcode', defaults={'code': None})
@app.route('/getcode')
def getcode():
    dbName=rds_config.db_name
    uname=rds_config.db_username
    upwd=rds_config.db_password
    host=rds_config.host
    redirect_url="https://sfdcschemapy.herokuapp.com/getcode"
    print('redirect_url in getcode',redirect_url)
    code = request.args.get('code')
    print('code,session name--->',code,session['username'])
    name=session['username']
    print(name,'session name',type(session['username']))
    print('\n ****Entered into acess_token*****\n ')
    print('acestoken name -->',session['username'])
    try:
      if session['username'] == '':
          error='You Should login to connect to Salesforce'
          return render_template('home.html',error=error)
      else:
          url = "https://login.salesforce.com/services/oauth2/token"
          print('acestoken entered get block')
          querystring = {"code":code,
                         "grant_type":"authorization_code",
                         "client_id":"3MVG9YDQS5WtC11oVIcikfdzsMBHOXFw2S3t38tAgNZFSKA10ews9pMB.mejIcW871MS3uV6z_6CDkCmh7owz",
                         "client_secret":"6652060970452995834",
                         "redirect_uri":"https://sfdcschemapy.herokuapp.com/getcode"
                         }
          response = requests.request("POST", url, params=querystring)
          print(response,'access_token response',response.text)
          #print(response.params)
          print(response.headers)
          data=response.json()
          print(data,'error' in data,"'refresh_token' in data'",'refresh_token' in data)
          #return response.text
          if 'error' in data:
              print('entered into error to get acces token')
              print(str(data['error_description']))
              return render_template('home.html',error=str(response.text))
              #return data['error_description']
              #return render_template('home.html',error=str(data['error_description']))
              #return data['error_description']
          else:
              if 'refresh_token' in data:
                  refresh_token=data['refresh_token']
                  instance_url=data['instance_url']
                  access_token=data['access_token']
                  print('instance_url---',instance_url,'\n---refresh',refresh_token,'\naccess_token',access_token)
                  con = psycopg2.connect(host=host,database=dbName, user=uname, password=upwd)
                  cur = con.cursor()
                  cur.execute("CREATE TABLE IF NOT EXISTS users( Name VARCHAR(20), pwd VARCHAR(20), refresh_token VARCHAR(100), instance_url VARCHAR(100)) ")
                  query = "UPDATE users SET  refresh_token='"+refresh_token+"', instance_url='"+instance_url +"',access_token='"+access_token+"' where Name='"+session['username']+"'"
                  print(query)
                  cur.execute(query)
                  con.commit()
                  con.close()
                  accounts(session['username'])
                  return render_template('home.html',success='Connected Successfully',authToken=access_token)
              else:
                  return render_template('home.html',error=str(response.text))
          return render_template('home.html',error=str(response.text))
      
        
    except Exception as e:
        return render_template('home.html',error=str(e))
        
    #return render_template('temp.html',recs=ac_data['records'],records='Total records : '+str(ac_data['totalSize'])+' records Found')
    #return "hello"+str(code)
  
#@app.route('/access_token',methods = ['get','POST'])
#@app.route('/<string:name>/access_token',methods = ['get','POST'])  
def access_token(code):
  
    print('\n ****Entered into acess_token*****\n ')
    print('acestoken name -->',session['username'])
    global redirect_url
    global dbName,uname,upwd,host
    redirect_url="https://sfdcschemapy.herokuapp.com/getcode"
    dbName=rds_config.db_name
    uname=rds_config.db_username
    upwd=rds_config.db_password
    host=rds_config.host
    print('\n code: ',code,redirect_url)
    error=None
    
    if request.method == 'POST':
        error='You Should login to connect to Salesforce'
        return render_template('home.html',error=error)
    else:
        url = "https://login.salesforce.com/services/oauth2/token"
        print('acestoken entered get block')
        querystring = {"code":code,
                       "grant_type":"authorization_code",
                       "client_id":"3MVG9YDQS5WtC11oVIcikfdzsMBHOXFw2S3t38tAgNZFSKA10ews9pMB.mejIcW871MS3uV6z_6CDkCmh7owz",
                       "client_secret":"6652060970452995834",
                       "redirect_uri":"https://sfdcschemapy.herokuapp.com/getcode"
                       }
        response = requests.request("POST", url, params=querystring)
        print(response,'access_token response',response.text)
        #print(response.params)
        print(response.headers)
        data=response.json()
        print(data,'error' in data,"'refresh_token' in data'",'refresh_token' in data)
        #return response.text
        if 'error' in data:
            print('entered into error to get acces token')
            print(str(data['error_description']))
            return render_template('home.html',error=str(response.text))
            #return data['error_description']
            #return render_template('home.html',error=str(data['error_description']))
            #return data['error_description']
        else:
            if 'refresh_token' in data:
                refresh_token=data['refresh_token']
                instance_url=data['instance_url']
                access_token=data['access_token']
                print('instance_url---',instance_url,'\n---refresh',refresh_token,'\naccess_token',access_token)
                con = psycopg2.connect(host=host,database=dbName, user=uname, password=upwd)
                cur = con.cursor()
                cur.execute("CREATE TABLE IF NOT EXISTS users( Name VARCHAR(20), pwd VARCHAR(20), refresh_token VARCHAR(100), instance_url VARCHAR(100)) ")
                query = "UPDATE users SET  refresh_token='"+refresh_token+"', instance_url='"+instance_url +"',access_token='"+access_token+"' where Name='"+session['username']+"'"
                print(query)
                cur.execute(query)
                con.commit()
                con.close()
                accounts(session['username'])
                return render_template('home.html')
            else:
                return render_template('home.html',error=str(response.text))
        return render_template('home.html',error=str(response.text))

@app.route('/accounts',methods = ['get','POST'])
@app.route('/<string:name>/accounts',methods = ['get','POST'])
def accounts(name=None):
    global refresh_token,instance_url,redirect_url,access_token
    global dbName,uname,upwd,host
    dbName=rds_config.db_name
    uname=rds_config.db_username
    upwd=rds_config.db_password
    host=rds_config.host
    print(session['username'],'----name')
    #print(session['username'],'----name')
    con = psycopg2.connect(host=host,database=dbName, user=uname, password=upwd)
    print(con)
    cur = con.cursor()
    quer = "SELECT refresh_token,instance_url,access_token FROM users WHERE Name=%s "
    print(quer)
    cur.execute(quer,(session['username'],))
    #print(cur.execute(quer,(session['username'],)))
    getrows = cur.fetchall()
    print('getrows',getrows,getrows[0][0],cur)
    if getrows[0][0] is None:
        return render_template('home.html',error='Refresh token empty, Connect To SFDC first')
        
    for r in getrows:
        print('\nrefresh_token-->',redirect_url,r[0])
        refresh_token=r[0]
        instance_url=r[1]
        access_token=r[2]
        con.commit()
        con.close()
    error=None
    if request.method == 'POST':
        print('entered into post \n')
        uname =request.form['user']
        if uname!='':
            query = {"q":uname}
        else:
            query = {"q":"SELECT name,id,phone from Account limit 10"}
    else:
        query = {"q":"SELECT name,id,phone from Account limit 10"}
        print(query)
        
    
    finalurl = instance_url+'/services/data/v20.0/query/'
    print(finalurl)
    
    headers = {
    'authorization': "OAuth "+str(access_token),
    'content-type': "application/x-www-form-urlencoded",
    }
    Ac_response = requests.request("GET", finalurl, headers=headers, params=query)
    ac_data=Ac_response.json()
    
    #print('type(ac_data)',type(ac_data),"\n\n'error' in ac_data,query",'error' in ac_data,query,"\n'errorCode' in ac_data",'errorCode' in ac_data,'\n',ac_data)
    #return 'ac_data'+Ac_response.text
    if type(ac_data) is list:
        print('ac_data list\n',ac_data)
        if ac_data[0]['errorCode']=='INVALID_TYPE':
            INVALID_TYPE_error=str(ac_data[0]['message'])
            return render_template('home.html',error="INVALID_TYPE : "+INVALID_TYPE_error)
            
        if 'errorCode' in ac_data[0]:
            print('\nentered into errorcode', ac_data[0]['errorCode'],'\n refresh token',refresh_token)
            return generate_token(instance_url,refresh_token,query)
            
            #return render_template('home.html',error=ac_data[0]['errorCode']+'\n connectetosalesforce again')
        if 'error' in ac_data[0]:
            print('error block \n')
            return generate_token(instance_url,refresh_token,query)
    else:
        return render_template('temp.html',recs=ac_data['records'],records='Total records : '+str(ac_data['totalSize'])+' records Found')
    
            
def generate_token(instance_url,refresh_token,query):
  global redirect_url
  print('generate token redirect_url',redirect_url,refresh_token,query)
  querystring = {"grant_type":"refresh_token",
                 "client_id":"3MVG9YDQS5WtC11oVIcikfdzsMBHOXFw2S3t38tAgNZFSKA10ews9pMB.mejIcW871MS3uV6z_6CDkCmh7owz",
                 "client_secret":"6652060970452995834",
                 "redirect_uri":"https://sfdcschemapy.herokuapp.com/getcode",
                 "refresh_token":refresh_token}
  url=instance_url+"/services/oauth2/token"
  response2 = requests.request("POST", url, params=querystring)
  print(response2,'generate_token \n',response2.text)
  #print(response.params)
  print(response2.headers)
  data2=response2.json()
  #pprint(data2)
  if 'access_token' in data2:
    print('access_token gebnerated ')
    access_token=data2['access_token']
    instance_url=data2['instance_url']
    print( "\naccess_token--- "+data2['access_token']+'\n refresh_token---'+refresh_token)
    con = psycopg2.connect(host=host,database=dbName, user=uname, password=upwd)
    cur = con.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS users( Name VARCHAR(20), pwd VARCHAR(20), refresh_token VARCHAR(100), instance_url VARCHAR(100)) ")
    upquery = "UPDATE users SET  access_token='"+access_token+"' where Name='"+session['username']+"'"
    print(upquery)
    cur.execute(upquery)
    con.commit()
    con.close()
    finalurl = instance_url+'/services/data/v20.0/query/'
    print('\nfinalurl',finalurl,query)
    headers = {
      'authorization': "OAuth "+str(access_token),
      'content-type': "application/x-www-form-urlencoded",
      }
    Ac_response = requests.request("GET", finalurl, headers=headers, params=query)
    ac_data=Ac_response.json()
    print(Ac_response.headers)
    print(type(ac_data),'after acess token get')
    pprint(ac_data)
    #pprint(ac_data['records'],ac_data['totalSize'])
    #return '\n\nac_data\n'+Ac_response.text
    print('-----\n\n after')
    return render_template('temp.html',recs=ac_data['records'],records='Total records : '+str(ac_data['totalSize'])+' records Found')
    #return render_template('temp.html',recs=ac_data['records'],records='Total records : '+str(ac_data['totalSize'])+' records Found')
    #return redirect(url_for('accounts'))
    #return 'ac_data'+Ac_response.text
    #return render_template('temp.html',recs=ac_data['records'],records='Total records : '+str(ac_data['totalSize'])+' records Found')
  else:
    return render_template('home.html',error="Access token exipred you need to reconect salesforce")
  


if __name__ == '__main__':
  app.debug = True
  app.secret_key = 'any random string'
  #app.secret_key = 'random string'
  app.run()
