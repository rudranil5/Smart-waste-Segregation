'''This  module is to be used mainly for the smart bin  project. it is capable to storing logs with automated timestamps generated in mysql side
and this module also maintains a log of all images processed.
this is also capable of entering values int any random table, but with some limitations.
the initializeBinServer() function is to be used at the beginning phase of
installation of code at a machine for the first time .

Upon running it independently, without any alteration, it creates the required tables along with databases if not already there,
and then enters a test value into the log.

This program is almost ready , just some minor fixes are needed. in the unknowninsert function it is for minimal requirements
and only works for in and char and varchar datatypes with noi specifications in table. need to update it.
'''

import mysql.connector as sql
connection=None
def initializeBinServer():  #creates the required databases and tables for logs
    host=input("Enter Mysql Server Hostname: ")
    user=input("Enter Mysql Server Username: ")
    passwd=input(f"Enter Mysql Server Password for {user}: ")
    connection=sql.connect(host=host,user=user,password=passwd)
    cursor=connection.cursor()
    cursor.execute("show databases")
    if connection:
        a=cursor.fetchall()
        mkproject,mkthelog=0,0
        for i in a:
            if 'projects2' == i[0]:
                mkproject=1
                break
        for i in a:
            if 'thelogs2' == i[0]:
                mkthelog=1
                break
                
        if not mkproject:
            cursor.execute("create database projects2")
            cursor.execute("use projects2")
            cursor.execute("create table waste_data_test (serial int,filepath varchar(100),category varchar(50),confidence varchar(20))")
        if not mkthelog:
            cursor.execute("create database thelogs2")
            cursor.execute("use thelogs2")
            cursor.execute("create table waste_bin_server (serial int,time Timestamp default current_timestamp,log varchar(500))")
            cursor.execute("create table waste_bin_client (serial int,time Timestamp default current_timestamp,log varchar(500))")
    else:
        print("Connection Error !! retry with correct details: ")
    
def connectDb(): #establish connection to mysql database server
    global connection
    connection=sql.connect(host='localhost',user='root',password='root')
    if connection.is_connected():          #to check if connection is done
        #print(connection)      
        print("connected to database on localhost  ")


def  closeDb():   #close the connection to database server
    print("\nClosed Connection to Database Server ---")
    connection.close()
       
def showTable(): # show tables from the projects database
    connection=sql.connect(host='localhost',user='root',password='root',database='projects')
    cursor=connection.cursor()
    cursor.execute("select * from waste_data_test")
    k=cursor.fetchall()
    for i in k :
        print(i)

def insertRow_unknown(): #add values to any table #table needed to be specified  by user  
    workingDatabase=input("Enter the database name : ")
    connection=sql.connect(host='localhost',user='root',password='root',database=workingDatabase)      #connection to database
    if connection.is_connected():          #to check if connection is done
        print(connection)      
        print(f'connected to database {workingDatabase}')
    cursor=connection.cursor()

    print(f"The following Tables are found in the database {workingDatabase}")
    cursor.execute('show tables')
    k=cursor.fetchall()# list of tuples
    for i in k :
        print(i)
    print('\n')
    

    table=input("choose the table to work with : \n  --- ")
    if table.isnumeric():
        print("Table : table \n")
        
        table=str(k[(int(table))-1][0])

    cursor.execute(f"desc {table}")
    k=cursor.fetchall()
    for i in k:
        print(i)
    print("\n")

    query=(f"Insert into {table} values(")
    values=[]
    for i in range(len(k)):
        query+="%s,"
        dd=k[i][0]
        tt=input(f"Enter the {dd} ")
        values.append(tt)if k[i][1][:7]=="varchar" else values.append (int(tt))
    query=(query[:-1])+")"
    
    print(query)
    print(tuple(values))
    cursor.execute(query,tuple(values))
    connection.commit()
    pass

def insertRow(filepath,category="skipped",confidence="skipped"):   #add values to smart bin test results     #table and database chosen inside function already

    '''connection=sql.connect(host='localhost',user='root',password='root',database='projects')      #connection to database
    if connection.is_connected():          #to check if connection is done
        #print(connection)      
        print('connected to database projects')
    '''
    cursor=connection.cursor()
    
    cursor.execute("use projects")
    cursor.execute("select max(serial) from waste_data_test")
    k=cursor.fetchall()
    
    for i in k :
        serial=int(i[0]+1)
        #print(serial)

    cursor.execute("select filepath from waste_data_test")
    k=cursor.fetchall()
    try:
        
        #if filepath not in i[0]:
        query=("Insert into waste_data_test values (%s,%s,%s,%s)")
        datas=(serial,filepath,category,confidence)
        cursor.execute(query,datas)
        connection.commit()
        #else :
    except Exception as e:
        print(e)
        print(f"File path {filepath} already there !!! ")
        return ("duplicate")
    
    
def writeLogBinServer(log): # log for the smart bin
    
    cursor=connection.cursor()
    try:
        cursor.execute("use TheLogs")
        cursor.execute("select max(serial) from waste_bin_server")
        k=cursor.fetchall()
        
        for i in k :
            serial=int(i[0]+1)
            #print(serial)
      
        query=("Insert into waste_bin_server (serial,log)values (%s,%s)")
        datas=(serial,log)
        cursor.execute(query,datas)
        connection.commit()
        return
    except Exception as e:
        print("\n___\t___\t___\n\n")
        print(e)
        print("\n\n___\t___\t___\n\n")
        print("The data to log is - ",log)
        query=("Insert into waste_bin_server (serial,log)values (%s,%s)")
        cursor.execute(query,str(e))      
        #closeDb()
        return
    

def writeLogBinClient(log): # log for the smart bin
    
    cursor=connection.cursor()
    try:
        cursor.execute("use TheLogs")
        cursor.execute("select max(serial) from waste_bin_client")
        k=cursor.fetchall()
        
        for i in k :
            if i[0] is None:
                serial=1
                break
            serial=int(i[0]+1)
            #print(serial)
      
        query=("Insert into waste_bin_client (serial,log)values (%s,%s)")
        datas=(serial,log)
        cursor.execute(query,datas)
        connection.commit()
        return
    except Exception as e:
        print("\n___\t___\t___\n\n")
        print(e)
        print("\n\n___\t___\t___\n\n")
        print("The data to log is - ",log)
        query=("Insert into waste_bin_client (serial,log)values (%s,%s)")
        cursor.execute(query,str(e))      
        #closeDb()
        return
 
    
if __name__=="__main__":
    #insertRow_unknown()
    #showTable()
    initializeBinServer()
    connectDb()#connection needs to be done for below 2 only
    writeLogBinServer("This is a test")
    #insertRow("testpath2","n","n")
    closeDb()
    
