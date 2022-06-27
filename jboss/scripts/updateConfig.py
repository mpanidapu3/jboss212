#******************************************************************************
# All right, title and interest in and to the software        
# (the "Software") and the accompanying documentation or      
# materials (the "Documentation"), including all proprietary  
# rights, therein including all patent rights, trade secrets, 
# trademarks and copyrights, shall remain the exclusive       
# property of DXC Technology Company.
# No interest, license or any right respecting the Software      
# and the Documentation, other than expressly granted in      
# the Software License Agreement, is granted by implication   
# or otherwise.                                               
#                                                            
# (C) 2017-2021 DXC Technology Company.
# All rights reserved.                                        
#******************************************************************************

def main(arguments):
    if len(arguments) != 2:    	
        print 'ERROR: One argument must be specified: CICSGATEWAY, JMSGATEWAY, or JDBC'
        sys.exit(1)

    global connected, cli
	
    connected = False

    cli = CLI.newInstance()

    try:
        connected = connectToServer(cli, configuration)
  
        if (arguments[1].upper() == 'CICSGATEWAY' and connected == True):
            updateCICSGateway()
        elif (arguments[1].upper() == 'JMSGATEWAY' and connected == True):
            updateJMSGateway()
        elif (arguments[1].upper() == 'JDBC' and connected == True):
            updateJDBCConnection()
        else:
            print 'ERROR: Invalid argument \'%s\': must be CICSGATEWAY, JMSGATEWAY, or JDBC' % arguments[1]         
    except:
        print 'ERROR: Update failed: ', sys.exc_info()[1]
    finally:
        if connected:
            print 'INFO: Disconnecting...' 	            
            cli.disconnect()
            
#******************************************************************************
# Update the CICS Gateway
#****************************************************************************                   

def updateCICSGateway():
    if ingenium.gateway != 'IBMCICS':
        print 'ERROR: This server does not use the CICS gateway.'
        sys.exit(1)

    config = ingenium.CICSGateway
    rarName = os.path.split(config.rarFile)[1]
    
    print 'INFO: Removing the existing CICS Connection %s' % config.connectionName     
    command = '/subsystem=resource-adapters/resource-adapter=%s/connection-definitions=%s/:remove' % (rarName, config.connectionName)
    cli.cmd(command)    
  
 
    #******************************************************************************
    # Add connection definitions and properties
    #******************************************************************************
    
    if connected == True:
       command = '/subsystem=resource-adapters/resource-adapter=%s/connection-definitions=%s:add(class-name=%s, jndi-name=%s)' % (rarName, config.connectionName, config.connectionClass, config.connectionJndiName)
       checkSuccess(cli.cmd(command))

       for attribute in config.attributes:
           command = '/subsystem=resource-adapters/resource-adapter=%s/connection-definitions=%s/config-properties=%s/:add(value=%s)' % (rarName, config.connectionName, attribute[0], attribute[1])
           checkSuccess(cli.cmd(command))

    print 'INFO: Reloading the server'
    cli.cmd(':reload')
	
#******************************************************************************
# Update the JMS Gateway
#****************************************************************************        
                    
def updateJMSGateway():
    if ingenium.gateway != 'JMS':
        print 'ERROR: This server does not use the JMS gateway.'
        sys.exit(1)

    config = ingenium.JMSGateway

    print 'INFO: Updating the %s MQ connection' % config.connectionName
   
    rarName = os.path.split(config.rarFile)[1]        
    
    #*****************************************************************************
    # Remove the existing connection factory
    #*****************************************************************************
    
    print 'INFO: Removing the existing connection factory %s ' % config.connectionName
    
    command = '/subsystem=resource-adapters/resource-adapter=%s/connection-definitions=%s/:remove' % (rarName, config.connectionName)
    cli.cmd(command)
    	
    for queueConfig in config.queues.list:
        print 'INFO: removing the existing queue %s' % queueConfig.name       
        
        #*****************************************************************************
        # Remove the admin objects
        #*****************************************************************************

        command = '/subsystem=resource-adapters/resource-adapter=%s/admin-objects=%s/:remove' % (rarName, queueConfig.queueName) 
        cli.cmd(command)
    
  
    if connected == True:
        configureMQResources(cli, config)          

    print 'INFO: Reloading the server'
    cli.cmd(':reload')
	
	
#******************************************************************************
# Update the JDBC connections
#******************************************************************************

def updateJDBCConnection():	
    print 'INFO: Updating JDBC connections'
    try:
        updateBamServerConnection()
    except Exception, exc:
        print 'ERROR: BamServer database connection update failed: \n', exc
    try:    
        updateIngeniumConnection()
    except Exception, exc:
        print 'ERROR: DXC Ingenium database connection update failed: \n', exc
    try:    
        updateProcessPoolConnection()
    except Exception, exc:
        print 'ERROR: PathFinder process pool connection update failed: \n', exc
    finally:
        print 'INFO: Reloading the server'
        # reloading the configurations	
        checkSuccess(cli.cmd(':reload'))	
#******************************************************************************
# Update the BamServer database connection
#******************************************************************************
    
def updateBamServerConnection():   
    connection = pathFinder.jdbc.bamServer    
    
    print 'INFO: Updating the BamServer database connection %s' % connection.connectionUrl

    command = '/subsystem=datasources/data-source=BamServerDataSource/:write-attribute(name=driver-name,value=%s)' % connection.driverName
    checkSuccess(cli.cmd(command))
    
    command = '/subsystem=datasources/data-source=BamServerDataSource/:write-attribute(name=connection-url,value=%s)' % connection.connectionUrl
    checkSuccess(cli.cmd(command))
    
    command = '/subsystem=datasources/data-source=BamServerDataSource/:write-attribute(name=user-name,value=%s)' % connection.userId
    checkSuccess(cli.cmd(command))
    
    command = '/subsystem=datasources/data-source=BamServerDataSource/:write-attribute(name=password,value=%s)' % connection.password
    checkSuccess(cli.cmd(command)) 
       
    #******************************************************************************
    # Testing the database connections BamServer connection
    #******************************************************************************	
    if connected == True:
        print 'INFO: Testing the BamServer database connection'
        command = 'data-source test-connection-in-pool --name=BamServerDataSource'
        checkSuccess(cli.cmd(command))   
                     
#******************************************************************************
# Update the PathFinder Ingenium database connection
#******************************************************************************
          
def updateIngeniumConnection():    
    connection = ingenium.ingeniumDatabaseConnection
    
    print 'INFO: Updating the DXC Ingenium database connection %s' % connection.connectionUrl
   
    command = '/subsystem=datasources/data-source=IngeniumDataSource/:write-attribute(name=driver-name,value=%s)' % connection.driverName
    checkSuccess(cli.cmd(command))
    
    command = '/subsystem=datasources/data-source=IngeniumDataSource/:write-attribute(name=connection-url,value=%s)' % connection.connectionUrl
    checkSuccess(cli.cmd(command))
    
    command = '/subsystem=datasources/data-source=IngeniumDataSource/:write-attribute(name=user-name,value=%s)' % connection.userId
    checkSuccess(cli.cmd(command))
    
    command = '/subsystem=datasources/data-source=IngeniumDataSource/:write-attribute(name=password,value=%s)' % connection.password
    checkSuccess(cli.cmd(command))    

    #******************************************************************************
    # Testing the database connections Ingenium connection
    #******************************************************************************	

    if connected == True:
        print 'INFO: Testing the DXC Ingenium database connection'
        command = 'data-source test-connection-in-pool --name=IngeniumDataSource'
        checkSuccess(cli.cmd(command))
        
#******************************************************************************
# Update the PathFinder process pool database connection
#******************************************************************************
           
def updateProcessPoolConnection():
    connection = pathFinder.jdbc.processPool

    print 'INFO: Updating the PathFinder process pool database connection %s' % connection.connectionUrl
            
    command = '/subsystem=datasources/data-source=ProcessPoolDataSource/:write-attribute(name=driver-name,value=%s)' % connection.driverName
    checkSuccess(cli.cmd(command))   

    command = '/subsystem=datasources/data-source=ProcessPoolDataSource/:write-attribute(name=connection-url,value="%s")' % connection.connectionUrl
    checkSuccess(cli.cmd(command))
        
    command = '/subsystem=datasources/data-source=ProcessPoolDataSource/:write-attribute(name=user-name,value=%s)' % connection.userId
    checkSuccess(cli.cmd(command))
    
    command = '/subsystem=datasources/data-source=ProcessPoolDataSource/:write-attribute(name=password,value=%s)' % connection.password
    checkSuccess(cli.cmd(command))

    #******************************************************************************
    # Testing the database connections process pool database connection
    #******************************************************************************	

    if connected == True:
        print 'INFO: Testing the PathFinder process pool database connection'        
        command = 'data-source test-connection-in-pool --name=ProcessPoolDataSource'
        checkSuccess(cli.cmd(command))   
    
#******************************************************************************
# Initial entry point
#******************************************************************************

if (__name__ == '__main__'):
    import sys
    from org.jboss.as.cli.scriptsupport import CLI
    from utilityFunctions import *
    from serverConfiguration import *
    
    serverConfigurationScript = configuration.serverConfigurationScript
    print 'INFO: Importing the server configuration script ' + serverConfigurationScript
    exec 'from ' + serverConfigurationScript + ' import *'

    serverInitializeScript = configuration.serverInitializeScript
    print 'INFO: Importing the server initialization script ' + serverInitializeScript
    exec 'from ' + serverInitializeScript + ' import *'

    main(sys.argv)
else:
    print 'ERROR: Entry point main not found - script aborts'    
