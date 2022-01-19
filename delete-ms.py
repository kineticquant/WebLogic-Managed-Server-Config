# Script needs to be initialized by WLST
#!/usr/bin/python

import re
import os
import sys
from ConfigParser import ConfigParser
import getopt
from java.lang import String

# These options are in config.xml
# This is the same credential that is encrypted in the boot.properties file
#wls_user           = "weblogic"
#wls_pass           = "randomweblogicpw (normally this is weblogic1 or weblogic_admin by default)"
#wls_url            = "t3://localhost:7001"

# Script can also prompt for credentials by just passing connect() method to prevent hard-coding the credentials
#connect(wls_user, wls_pass, wls_url)
#connect()
# This connection method below will accept the WebLogic defaults simply by pressing enter.
console = System.console()
uname = raw_input("Weblogic username (weblogic): ")
if uname == "":
    uname = "weblogic"
pw = "".join(java.lang.System.console().readPassword("%s", ["Password for %s: " % uname]))
url = raw_input("Enter AdminServer url (t3://localhost:7001): ")
if url == "":
    url = "t3://localhost:7001"
connect(uname, pw, url)

cd('/')

# Retrieve list of the managed servers
listOfManagedServer = cmo.getServers()
msServerCount = len(listOfManagedServer)
for managedServerInstance in listOfManagedServer:
    
    tempDSName = managedServerInstance.getName()     
    print tempDSName   
    
# Retrieve the managed server selected from user input 
msName = raw_input("Identify which managed server you wish to delete: ") 


# Loop to link up the servers to match the user input
tmpContine = false
i = 1 
while i < msServerCount:
    for managedServerInstance in listOfManagedServer:        
        tempDSName = managedServerInstance.getName()  
        searchObj = re.match(msName.lower(), tempDSName.lower())
        if searchObj:
            print("Successfully matched the managed server to user input. Deleting the server.")
            tmpContine = true
            print(msName.lower())
            print(tempDSName.lower())            
        # The else clause is commented out but can be used for debugging 
        #else:
        #    print(msName.lower())
        #    print(tempDSName.lower())
        #   #sys.exit("Unable to find managed server.")
    i += 1
    
if tmpContine:   
    print("Successfully matched the managed server to user input. Deleting the server.")
else:
    sys.exit("Unable to find managed server.")
    
def deleteDataSource(): 
    serverConfig() 
    edit()
    startEdit()

    cd('/')

    listOfDataSources = cmo.getJDBCSystemResources()
    for datasourceInstance in listOfDataSources:
        tempDSName = datasourceInstance.getName()
        #print tempDSName
        searchObj = re.search(msName, tempDSName)
        if searchObj:
            print("searchObj.group() : ", tempDSName)
            datasourceInstance.setTargets(None)
            cmo.destroyJDBCSystemResource(datasourceInstance)
        
    save()
    activate()
    serverConfig()
    
def deleteJmsServer(): 
    serverConfig() 
    edit()
    startEdit()

    cd('/')

    listOfJmsServers = cmo.getJMSServers()
    for JmsServerInstance in listOfJmsServers:
        tempDSName = JmsServerInstance.getName()
        #print tempDSName
        searchObj = re.search(msName, tempDSName)
        if searchObj:
            print("searchObj.group() : ", tempDSName)
            # first delete targets
            JmsServerInstance.setTargets(None)
            # delete
            cmo.destroyJMSServer(JmsServerInstance)
        
    save()
    activate()
    serverConfig()
    
def deleteSystemModules(): 
    serverConfig() 
    edit()
    startEdit()

    cd('/')

    listOfJmsSystemResources = cmo.getJMSSystemResources()
    for JmsSystemResourcesInstance in listOfJmsSystemResources:
        tempDSName = JmsSystemResourcesInstance.getName()
        #print tempDSName
        searchObj = re.search(msName, tempDSName)
        if searchObj:
            print("searchObj.group() : ", tempDSName)
            # first delete targets
            JmsSystemResourcesInstance.setTargets(None)
            # delete
            cmo.destroyJMSSystemResource(JmsSystemResourcesInstance)
        
    save()
    activate()
    serverConfig()
     
def deleteManagedServer(jMgSrvName):
    serverConfig() 
    edit()
    startEdit()
    cd('/')
     
    listOfManagedServer = cmo.getServers()
    for managedServerInstance in listOfManagedServer:
        
        tempDSName = managedServerInstance.getName()
        print tempDSName
        searchObj = re.search(msName, tempDSName)
        if searchObj:
            print ("match %s")  % tempDSName
            # Retrieve the server state
            domainRuntime()
            serverRuntime = getMBean(jMgSrvName)
            myState = serverRuntime.getState()
            print (myState)

            # Shutdown the managed server if it is already running
            if myState == "RUNNING":
                print "Shutting down %s" % managedServerInstance.getName()
                shutdown(managedServerInstance.getName() ,  force="true")
                os.system('sleep 10')

            edit()
            cd('/')
            cd('/Servers/' + msName)
            print(msName)
            managedServerInstance.setCluster(None)
            managedServerInstance.setMachine(None)

            editService.getConfigurationManager().removeReferencesToBean(getMBean('/Servers/' + msName))
            cd('/')
            cmo.destroyServer(getMBean('/Servers/' + msName))
        
    save()
    activate()
    serverConfig()   
     
deleteDataSource()
deleteSystemModules()
deleteJmsServer()
jtmp = ("/ServerLifeCycleRuntimes/%s") % msName
deleteManagedServer(jtmp)

disconnect()
exit()
