#!/usr/bin/python

# Ensure you replace the values with what you need to match your environment
# roleName is defined as the actual role that will be placed in the security realm - this needs changed
# This script enables SSL by default - you will need to return and attach the keystore in the SSL configuration settings
# You will need to define a user that belongs to the role that can connect across multiple builds if you use the adapter configuration settings
    # This is not necessary if you strip this script down to just building managed servers using the properties file

import os
import sys
from ConfigParser import ConfigParser
import getopt
from java.lang import String

# CLI argument to identify a file that may have the pre-built configuration
try:
    options, args = getopt.getopt(sys.argv[1:], "f:", "file=")
except getopt.GetoptError:
    print "Usage:"
    print "%s -f /path/to/configFile.cfg" % sys.argv[0]
    sys.exit(1)

for option, arg in options:
    if option in ("-f", "--file"):
        configFile = arg
    else:
        print "No option specified to retrieve config file"
        sys.exit(1)

if not os.path.exists(configFile):
    print "Could not locate %s." % configFile
    print "Please identify a config file with either -f or --file"
    sys.exit(1)

print "Reading configuration from identified config file"
config = ConfigParser()
config.read(configFile)

# Retrieving the defined options from the config file
wlsUser           = config.get("weblogic", "wls_user")
wlsPass           = config.get("weblogic", "wlsPass")
wlsUrl            = config.get("weblogic", "wlsUrl")
domainDir         = config.get("weblogic", "domainDir")

msName            = config.get("managed_server", "msName")
msMachine         = config.get("managed_server", "msMachine")
msListenPort     = config.get("managed_server", "msListenPort")
msListenAddress  = config.get("managed_server", "msListenAddress")
msSSLListenPort = config.get("managed_server", "msSSLListenPort")
serverKeystore    = config.get("managed_server", "ms_keystore")
keystorePass      = config.get("managed_server", "ms_keystorePass")
javaKeystorePass = config.get("managed_server", "ms_javaKeystorePass")
msConfigSSL      = config.get("managed_server", "msConfigSSL")

DBUser        = config.get("jdbc", "DBUser")
DBPass        = config.get("jdbc", "DBPass")
DBROUser        = config.get("jdbc", "DBROUser")
DBROPass        = config.get("jdbc", "DBROPass")
DBHostName        = config.get("jdbc", "DBHostName")
DBPort        = config.get("jdbc", "DBPort")
DBName     = config.get("jdbc", "DBName")
JNDIName          = config.get("jdbc", "JNDIName")
ROMaxCapacity = config.getint("jdbc", "ROMaxCapacityacity")
RWMaxCapacity = config.getint("jdbc", "RWMaxCapacityacity")
serviceName = config.get("jdbc", "serviceName")
roDBHostName = DBHostName
roDBPort = DBPort
roDBName = DBName
roServiceName = serviceName

# JMS Messaging names to configure
# Secondary is designed for mobile connection in case you wantd to use that
primaryJMSName        = "JMSServer-%s" % msName
secondaryJMSName        = "JMSServer-sec-%s" % msName
priSysModuleName = "SystemModule-%s" % msName
secSysModuleName = "SystemModule-sec-%s" % msName
priCFName         = "ConnectionFactory-%s" % msName
secCFName         = "MobileConnectionFactory-%s" % msName
msgBeanName        = "MsgBean-%s" % msName
msgRegName         = "MsgRegister-%s" % msName
secQueue           = "queue-name"

# JMS System Modules that will be configured
fsTargetServer       = config.get("managed_server", "fsTargetServer")
sysName               = config.get("managed_server", "sysName")

#Network Access Points that will be configured
secNapName           = config.get("managed_server", "secNapName")
secNapProtocol       = config.get("managed_server", "secNapProtocol")
secNapListenAddress = config.get("managed_server", "secNapListenAddress")
secNapListenPort    = config.getint("managed_server", "secNapListenPort")
secNapPublicAddress = config.get("managed_server", "secNapPublicAddress")
secNapPublicPort    = config.getint("managed_server", "secNapPublicPort")

#Foreign Server
foreignServerName                          = config.get("managed_server", "foreignServerName")
fsTargetServer                 = config.get("managed_server", "fsTargetServer")
fsSecurityPrincipalName        = config.get("managed_server", "fsSecurityPrincipalName")
fsSecurityPrincipalCred = config.get("managed_server", "fsSecurityPrincipalCred")

#Foreign Destination
foreignDestName   = config.get("managed_server", "foreignDestName")

#Foreign Connection Factory
foreignConnFactoryName = config.get("managed_server", "foreignConnFactoryName")


if config.has_option("managed_server", "max_message_size"):
    max_message_size   = config.get("managed_server", "max_message_size")
else:
    max_message_size = 100000000
if config.has_option("managed_server", "max_memory"):
    max_memory = config.get("managed_server", "max_memory")
else:
    max_memory = "4096m"
if config.has_option("managed_server", "extra_start_args"):
    extra_start_args = config.get("managed_server", "extra_start_args")
else:
    extra_start_args = None    

server_start_args = " ".join([
    "-Xms%s" % (max_memory),
    "-Xmx%s" % (max_memory),
    "-XX:+UseG1GC",
    "-Declipselink.target-server=weblogic",
    "-Dweblogic.jndi.allowGlobalResourceLookup=true",
    "-Dweblogic.jndi.allowExternalAppLookup=true",
    "-Dweblogic.system.StreamPoolSize=0",
    "-XX:+UnlockCommercialFeatures"
])
if extra_start_args:
    server_start_args += " " + extra_start_args % (msName)
    
if (config.has_option("log_rotation", "file_size")
        or config.has_option("log_rotation", "file_count")):
    if config.has_option("log_rotation", "file_size"):
        rot_file_size = config.getint("log_rotation", "file_size")
    else:
        rot_file_size = 500
    if config.has_option("log_rotation", "file_count"):
        rot_file_count = config.getint("log_rotation", "file_count")
    else:
        rot_file_count = 7
else:
    rot_file_size = None
    rot_file_count = None    


nLine = "############################## PROCESS SEPARATOR #################################"

def check_resource(name):
    if getMBean(name) is not None:
        print "ERROR: This already exists: " + name
        sys.exit(1)
        
def check_resources():
    check_resource("/JMSServers/" + primaryJMSName)
    check_resource("/JMSServers/" + secondaryJMSName)
    check_resource("/JMSSystemResources/" + secSysModuleName)
    check_resource("/JDBCSystemResources/JDBC Data Source-" + msName)
    check_resource("/JDBCSystemResources/JDBC Data Source-%s_ro" % (msName))

def config_jndi_policies():
    print "Creating the JNDI security policies."
    unchecked_policy_str = "?weblogic.entitlement.rules.UncheckedPolicy()"
    xacml = cmo.getSecurityConfiguration().getDefaultRealm().lookupAuthorizer('XACMLAuthorizer')
    # Generic jndi policy | Requires Admin permissions for access
    if xacml.policyExists("type=<jndi>"):
        print "Modifying the JNDI security policy for method 'ALL'"
        xacml.setPolicyExpression("type=<jndi>", "Rol(Admin)")
    else:
        print "Creating the JNDI security policy for method 'ALL'"
        xacml.createPolicy("type=<jndi>", "Rol(Admin)")

    # Lookup policy | Allows anyone to run lookups
    if xacml.policyExists("type=<jndi>, action=lookup"):
        print "Modifying the JNDI security policy for method 'LOOKUP'"
        xacml.setPolicyExpression("type=<jndi>, action=lookup", unchecked_policy_str)
    else:
        print "Creating the JNDI security policy for method 'LOOKUP'"
        xacml.createPolicy("type=<jndi>, action=lookup", unchecked_policy_str)
    print nLine

def config_jms_policies():
    print "Creating the security policies for JMS server."
    xacml = cmo.getSecurityConfiguration().getDefaultRealm().lookupAuthorizer('XACMLAuthorizer')
    # JMS policy definition
    if xacml.policyExists("type=<jms>, application=%s" % secSysModuleName):
        print "Modifying the security policy for the application deployment for module '%s'" % secSysModuleName
        xacml.setPolicyExpression("type=<jms>, application=%s" % secSysModuleName,
                                  "Rol(roleName)")
    else:
        print "Creating the security policy for the module %s" % secSysModuleName
        xacml.createPolicy("type=<jms>, application=%s" % secSysModuleName, "Rol(roleName)")
    print nLine


def create_datasource(ds_name, ms_target, jndi, db_user, db_pass, max_cap, host,
                      port, db_name, service_name):
    print "Creating the JDBC data source:", ds_name
    startEdit()
    server_mbean = getMBean("/Servers/%s" % msName)
    # TODO: Handle JDBCSystemResource already existing
    primaryDS = create(ds_name, "JDBCSystemResource")
    primaryDS.addTarget(server_mbean)

    dsResource = primaryDS.getJDBCResource()
    dsResource.setName(ds_name)

    dsParams = dsResource.getJDBCDataSourceParams()
    dsParams.setJNDINames(jarray.array([String(jndi)], String))

    # This is built for Oracle for now, but can be changed to your pre-determined DB type
    driverParams = dsResource.getJDBCDriverParams()
    if service_name:
        url = 'jdbc:oracle:thin:@%s:%s/%s' % (host, port, service_name)
    else:
        url = 'jdbc:oracle:thin:@%s:%s:%s' % (host, port, db_name)

    driverParams.setUrl(url)
    driverParams.setDriverName('oracle.jdbc.xa.client.OracleXADataSource')
    driverParams.setPassword(db_pass)

    driverProps = driverParams.getProperties()
    driverProps.createProperty('user', db_user)
    driverProps.createProperty('databaseName', db_name)

    cpParams = dsResource.getJDBCConnectionPoolParams()
    cpParams.setTestTableName('SQL SELECT 1 from DUAL')
    if max_cap:
        cpParams.setMaxCapacity(max_cap)

    activate()
    print nLine


def config_jms():
    print "Configuring the JMS messaging queue(s)"
    # Initialize the edit procedure
    startEdit()
    server_mbean = getMBean("/Servers/%s" % msName)

    cd('/')

    secJMS = create(secondaryJMSName, "JMSServer")
    secJMS.addTarget(server_mbean)

    secSysModule = create(secSysModuleName, 'JMSSystemResource')
    secSysModule.addTarget(server_mbean)
    secJMSResource = secSysModule.getJMSResource()

    # Create the JMS resources for the secondary (adapter)
    secConnFactory = secJMSResource.createConnectionFactory(secCFName)
    secConnFactory.setJNDIName("jms/MobileConnectionFactory")
    secConnFactory.setSubDeploymentName('DeployTo' + secondaryJMSName)

    deliveryParams = secConnFactory.getDefaultDeliveryParams()
    deliveryParams.setDefaultDeliveryMode('Non-Persistent')
    deliveryParams.setDefaultTimeToLive(30000)

    transactionParams = secConnFactory.getTransactionParams()
    transactionParams.setXAConnectionFactoryEnabled(true)

    clientParams = secConnFactory.getClientParams()
    clientParams.setAcknowledgePolicy('Previous')

    flowControlParams = secConnFactory.getFlowControlParams()
    flowControlParams.setOneWaySendMode('enabled')

    # This will allow multiple managed servers to exist within the same domain
    secJMSQueue = secJMSResource.createQueue(secQueue)
    secJMSQueue.setJNDIName('jms/' + secQueue)
    secJMSQueue.setSubDeploymentName('DeployTo' + secondaryJMSName)

    subdeploy = secSysModule.createSubDeployment('DeployTo' + secondaryJMSName)
    subdeploy.addTarget(secJMS)
    activate()
    print nLine


def set_log_rotation():
    if rot_file_size is None or rot_file_count is None:
        return
    print "Setting the log rotation parameters"
    startEdit()
    cd('/Servers/%s/Log/%s' % (msName, msName))
    set("RotationType", "bySize")
    set("FileCount", rot_file_count)
    set("FileMinSize", rot_file_size)
    set("NumberOfFilesLimited", "true")
    activate()
    print nLine


def check_ms():
    print "Checking the status of the managed server %s" % msName
    existing_servers = ls('/Servers', returnMap='true')
    if msName in existing_servers:
        print "%s ALREADY EXISTS. PLEASE DELETE" % msName
        print "Please delete the specified managed server and re-run this script"
        sys.exit(1)
    else:
        startEdit()
        # Build the managed server
        cd('/')
        cmo.createServer(msName)
        
        # Link the machine name to associate with the NodeManager
        cd('/Servers/%s' % msName)
        cmo.setMachine(getMBean('/Machines/' + msMachine))
        # Listen Address 
        cmo.setListenAddress(msListenAddress)
        # Listen Port
        cmo.setListenPort(int(msListenPort))
        set('NativeIOEnabled', "false")
        cmo.setMuxerClass("weblogic.socket.NIOSocketMuxer")
        
        # Protocols configuration
        # Set the message size
        cmo.setMaxMessageSize(int(max_message_size))
        cmo.setTunnelingEnabled(true)            
        
        # Set the RMI JDBC security flag to secure
        cd('/Servers/' + msName + '/DataSource/' + msName)
        cmo.setRmiJDBCSecurity("Secure")
        
        # Enable SSL
        cd('/Servers/' + msName + '/SSL/' + msName)
        cmo.setEnabled(true)
        cmo.setListenPort(int(msSSLListenPort))
        
        # Configures the keystores
        cd('/Servers/%s' % msName)
        cmo.setKeyStores("CustomIdentityAndJavaStandardTrust")
        cmo.setCustomIdentityKeyStoreType("JKS")
        cmo.setCustomIdentityKeyStoreFileName(serverKeystore)
        cmo.setCustomIdentityKeyStorePassPhrase(keystorePass)
        cmo.setJavaStandardTrustKeyStorePassPhrase(javaKeystorePass)
        cd('/Servers/' + msName + '/SSL/' + msName)
        cmo.setHostnameVerificationIgnored(true)

        # The ALIAS needs changed to align to whatever your certificate alias in the keystore is
        cmo.setServerPrivateKeyAlias("ALIAS")
        cmo.setServerPrivateKeyPassPhrase(keystorePass)
        
        # Server start parameters
        cd('/Servers/%s/ServerStart/%s' % (msName, msName))
        cmo.setArguments(server_start_args)
    
        activate()    
    print nLine        
        
def configSecNap():     
    startEdit() 
    cd('/')        
    cd('/Servers/' + msName)
    # Network Access Point - This sets a channel to communicate with an adapter on for the secondary
    secNapChannel = cmo.createNetworkAccessPoint(secNapName)
    secNapChannel.setProtocol(secNapProtocol)
    secNapChannel.setListenAddress(secNapListenAddress)
    secNapChannel.setListenPort(secNapListenPort)
    secNapChannel.setPublicAddress(secNapPublicAddress)
    secNapChannel.setPublicPort(secNapPublicPort)
    secNapChannel.setOutboundEnabled(true)
    secNapChannel.setHttpEnabledForThisProtocol(true)
    secNapChannel.setTunnelingEnabled(true)
    activate()    
    print nLine

def configSecDeploy():     
    startEdit() 
    server_mbean = getMBean("/Servers/%s" % msName)
    cd('/')        

    sys_mod_name = "SystemModule-%s-%s" % (sysName, msName)
    secSysModuleDeploy = create(sys_mod_name, 'JMSSystemResource')
    server_mbean = getMBean("/Servers/%s" % fsTargetServer)
    # This will error if the JDBC resource already esists
    secSysModuleDeploy.addTarget(server_mbean)
    secJMSResourceDeploy = secSysModuleDeploy.getJMSResource()
    # Foreign Server configuration  
    secJMSFSDeploy = secJMSResourceDeploy.createForeignServer(foreignServerName)       
    secJMSFSDeploy.setInitialContextFactory("weblogic.jndi.WLInitialContextFactory")
    # Builds the  connection URL
    ws_jms_conn_url = "%s://%s:%s" % (secNapProtocol, secNapListenAddress, secNapListenPort)
    secJMSFSDeploy.setConnectionURL(ws_jms_conn_url)
    secJMSFSDeploy.setJNDIPropertiesCredential(fsSecurityPrincipalCred)
    secJMSFSDeploy.setDefaultTargetingEnabled(true)
    # Creates the JNDI property configuration 
    secJMSFSDeploy_jndi_prop = secJMSFSDeploy.createJNDIProperty("java.naming.security.principal")    
    secJMSFSDeploy_jndi_prop.setValue(fsSecurityPrincipalName)
    # Foreign Destination to allow a connection from the secondary to the primary
    secJMSFSDeploy_dst = secJMSFSDeploy.createForeignDestination(foreignDestName)
    secJMSFSDeploy_dst.setLocalJNDIName("jms/sec-to-primary")
    secJMSFSDeploy_dst.setRemoteJNDIName("jms/sec-to-primary")
    # Foreign Connection Factory
    secJMSFSDeploy_connfac = secJMSFSDeploy.createForeignConnectionFactory(foreignConnFactoryName)
    secJMSFSDeploy_connfac.setLocalJNDIName("jms/MobileConnectionFactory")
    secJMSFSDeploy_connfac.setRemoteJNDIName("jms/MobileConnectionFactory")
    activate()    
    print nLine

connect(wls_user, wlsPass, wlsUrl)
check_resources()
config_jndi_policies()
config_jms_policies()
edit()
check_ms()
set_log_rotation()
config_jms()
create_datasource(
    "JDBC Data Source-" + msName,
    msName, JNDIName, DBUser, DBPass, RWMaxCapacity, DBHostName,
    DBPort, DBName, serviceName)
create_datasource(
    "JDBC Data Source-" + msName + "_ro",
    msName, JNDIName + "_readonly", DBROUser, DBROPass, ROMaxCapacity,
    roDBHostName, roDBPort, roDBName, roServiceName)


configSecNap()
configSecDeploy()

exit()
print "Script has finished creating the managed server(s) and all configuration"
