
Download code from Github
===========================

Download code GitHub: https://github.com/yinbri/my-rewards-api. Let the local working directory be c:\project\my-rewards-api.


# Install MongoDB (skip if you have installed before)

1. Download community edition (https://www.mongodb.com/try/download/community) and choose to installation path, e.g. c:\tools, which will direct MongoDB to be installed at c:\tools\MongoDB

2. Start MongoDB
```
  > c:\tools\MongoDB\Server\6..0\bin\bin>mongod --dbpath c:\project\my-rewards-api\data
```
if this runs successfully, the mongod will not exit to windows command line prompt

# Install Mongosh (skip if you have installed before)

1.Download (https://www.mongodb.com/try/download/shell)

2.Run installer and install it to c:\tools. Mongosh will be installed to c:\tools\mongosh-1.8-win32-x64

3.Start mongosh
```
c:\tools\mongosh-1.8-win32-x64\mongosh
```
Mongosh prompt will show up if it is started successfully  

Run command to test installation of both the shell and the MongoDB
```
> show dbs
```

# Load testing data to MongoDB

go to the Mongosh window and run:
```
> use mydb
> load("dbscript.txt")
> db.getCollectionNames()
```  
The following collections share be in the list: user, adminuser, activity, useractivity


## SHort Reference of the MongoDB commands used in this project
```
use mydb
db.getCollectionNames()
db.user.find()
db.user.insertOne({"username":"luis@gmail.com", "password":"test"})
db.user.deleteOne({"username":"luis@gmail.com", "password":"test"})
db.user.insertOne([{"username":"luis@gmail.com", "password":"test"},
{"username":"mary@gmail.com", "password":"test"}])
```

# Develop web services with Python

1.IDE used: PyCharm CE
2.The core was previously downloaded to c:\project\my-rewards-api
3.Install Flask from cmd window
```
   > cd c:\project\my-web-api
   > pip install flask
```
4.Browse the app.py file to familiar with the logic

5.Start the web services and let it listen on localhost, port 3000
```
> cd c:\project\my-we-api
> flask run -h localhost -p 3000
```
by default, Flask will load the app.py file

# Test web service with SoapUI

1.Download and install SoapUI if you don't have one installed. My version is 5.7.0
2.Create a project
3.Create a new request with the following data entered:
```
   Choose Request
   Method: POST
   Endpoint: http://localhost:3000/login_service
   MediaType: application/json
   Add the following as the content of request:
   {
    "username": "brain@gmail.com",
    "password": "test"
   }
```
4.Click the green arrow button to send the request
   Expect the following on the right side response window when viewing as JSON
```
   {
   "status": "success",
   "username": "brian@gmail.com"
   }
```
5.Other services can be tested similarly
                      

