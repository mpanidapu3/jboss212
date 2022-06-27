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
# (C) 2014-2021 DXC Technology Company.
# All rights reserved.                                        
#******************************************************************************

import java
from utilityFunctions import *
from serverConfiguration import *
from ingeniumServerConfiguration import *
from org.jboss.as.cli.scriptsupport import CLI
from xml.dom.minidom import parse, parseString

#******************************************************************************
# This method will be called by the initialize.main() method.
# Perform any DXC Ingenium specific initialization here.
#******************************************************************************

def initializeAdministrationServer(cli):
    #******************************************************************************
    # Some of the DXC Ingenium pages have the ability to send back more than 512
    # parameters in the POST message. We need to bump up the maximum to allow for
    # these pages.
    #******************************************************************************

    command = '/system-property=org.apache.tomcat.util.http.Parameters.MAX_COUNT:add(value=1000)'
    checkSuccess(cli.cmd(command))

    configureIngeniumJDBC(cli)

    if ingenium.usePFC:
        configurePFCResources(cli)
    
    if ingenium.gateway == 'IBMCICS':
        configureIngeniumCicsGateway(cli)

    elif ingenium.gateway == 'JMS' or ingenium.gateway == 'MQ' or ingenium.gateway == 'ACTIVEMQ':
        configureIngeniumJMSGateway(cli)

    else:
        print 'ERROR: The gateway specified in the ingeniumServerConfiguration.py is invalid' 
        sys.exit(1)
#******************************************************************************
# Create the DXC Ingenium database connection
#******************************************************************************

def configureIngeniumJDBC(cli):
    connection = ingenium.ingeniumDatabaseConnection

    print 'INFO: Creating the DXC Ingenium database connection %s' % connection.connectionUrl

    command = 'data-source add --name=IngeniumDataSource --jndi-name=java:/app/jdbc/IngeniumDataSource --driver-name=%s --connection-url=%s --user-name=%s --password=%s --pool-prefill=false --use-java-context=true' % (connection.driverName, connection.connectionUrl, connection.userId, connection.password)
    checkSuccess(cli.cmd(command))

    print 'INFO: Testing the DXC Ingenium database connection'
    command = 'data-source test-connection-in-pool --name=IngeniumDataSource'
    checkSuccess(cli.cmd(command))

#******************************************************************************
# Create resources used by PathFinderConnector
#******************************************************************************

def configurePFCResources(cli):
    print 'INFO: Creating the PFC transmittal message queues'

    command = '/subsystem=messaging-activemq/server=default/jms-queue=PFCTransmitRequestQueue/:add(entries=["java:/app/jms/PFCTransmitRequestQueue"])'
    checkSuccess(cli.cmd(command))

    command = '/subsystem=messaging-activemq/server=default/jms-queue=PFCTransmitResponseQueue/:add(entries=["java:/app/jms/PFCTransmitResponseQueue"])'
    checkSuccess(cli.cmd(command))

    if ingenium.gateway == 'ACTIVEMQ' and ingenium.applications.pfc.listener == 'QUEUE':
        configureMQResources(cli, ingenium.applications.pfc.jmsActiveMQ)
    else:
        configureMQResources(cli, ingenium.applications.pfc.jms)

    #*********************************************************************
    # Add MDB attributes as system properties
    #*********************************************************************

    for attribute in ingenium.applications.pfc.jms.mdbAttributes:
        command = '/system-property=%s:add(value=%s)' % (attribute[0], attribute[1])
        checkSuccess(cli.cmd(command))

    #*********************************************************************
    # There's an issue with the IBM MQ RAR that causes it to spit out 
    # warning messages every two minutes. We'll set the com.arjuna logger 
    # to ERROR to suppress these warning messages.
    #*********************************************************************

    command = '/subsystem=logging/logger=com.arjuna:change-log-level(level=ERROR)'
    checkSuccess(cli.cmd(command))

#******************************************************************************
# Create the JMS resources needed by the JMSGateway
#******************************************************************************

def configureIngeniumJMSGateway(cli):
    if ingenium.gateway == 'ACTIVEMQ':
        configureMQResources(cli, ingenium.ActiveMQGateway)
    else:
        configureMQResources(cli, ingenium.JMSGateway)

#******************************************************************************
# Setup the CICS gateway
#******************************************************************************

def configureIngeniumCicsGateway(cli):
    config = ingenium.CICSGateway

    print 'INFO: Configuring the CICS gateway %s' % config.connectionName

    #******************************************************************************
    # We need to turn off validation because the CICS ECI RAR will not validate 
    # properly. It will fail with an error indicating that it doesn't implement the 
    # equals and hashcode methods as required by JCA 1.6
    #******************************************************************************

    command = '/subsystem=jca/archive-validation=archive-validation:write-attribute(name=enabled, value=false)'
    checkSuccess(cli.cmd(command))
    command = '/subsystem=jca/archive-validation=archive-validation:write-attribute(name=fail-on-error, value=false)'
    checkSuccess(cli.cmd(command))

    rarName = deployResourceAdapter(cli, config.rarFile)

    #******************************************************************************
    # Add the connection factory
    #******************************************************************************

    command = '/subsystem=resource-adapters/resource-adapter=%s/connection-definitions=%s:add(class-name=%s, jndi-name=%s)' % (rarName, config.connectionName, config.connectionClass, config.connectionJndiName)
    checkSuccess(cli.cmd(command))

    #******************************************************************************
    # Add connection properties
    #******************************************************************************

    for attribute in config.attributes:
        command = '/subsystem=resource-adapters/resource-adapter=%s/connection-definitions=%s/config-properties=%s/:add(value=%s)' % (rarName, config.connectionName, attribute[0], attribute[1])
        checkSuccess(cli.cmd(command))

#******************************************************************************
# Create the JMS resources needed by the JMSGateway
#******************************************************************************

def configureMQResources(cli, config):
    print 'INFO: Configuring the %s MQ connection' % config.connectionName

    rarName = deployResourceAdapter(cli, config.rarFile)

    #******************************************************************************
    # Add the connection factory
    #******************************************************************************

    command = '/subsystem=resource-adapters/resource-adapter=%s/connection-definitions=%s:add(use-ccm=false, class-name=%s, jndi-name=%s)' % (rarName, config.connectionName, config.connectionClass, config.connectionJndiName)
    checkSuccess(cli.cmd(command))

    #******************************************************************************
    # Add connection properties
    #******************************************************************************

    for attribute in config.attributes:
        command = '/subsystem=resource-adapters/resource-adapter=%s/connection-definitions=%s/config-properties=%s/:add(value=%s)' % (rarName, config.connectionName, attribute[0], attribute[1])
        checkSuccess(cli.cmd(command))

    for queueConfig in config.queues.list:
        print 'INFO: Creating the queue %s' % queueConfig.name

        # Add the admin object for the resource adapter
        command = '/subsystem=resource-adapters/resource-adapter=%s/admin-objects=%s:add(class-name=%s,jndi-name=java:/app/jms/%s)' % (rarName, queueConfig.queueName, queueConfig.className, queueConfig.name)
        checkSuccess(cli.cmd(command))

        if ingenium.gateway != 'ACTIVEMQ':
            # Add properties to the admin object
            command = '/subsystem=resource-adapters/resource-adapter=%s/admin-objects=%s/config-properties=baseQueueName/:add(value=%s)' % (rarName, queueConfig.queueName, queueConfig.queueName)
            checkSuccess(cli.cmd(command))

        for property in queueConfig.attributes:
            command = '/subsystem=resource-adapters/resource-adapter=%s/admin-objects=%s/config-properties=%s/:add(value=%s)' % (rarName, queueConfig.queueName, property[0], property[1])
            checkSuccess(cli.cmd(command))

#******************************************************************************
# Deploy the resource adapter if it isn't already deployed.
#******************************************************************************

def deployResourceAdapter(cli, fileName):
    rarName = os.path.split(fileName)[1]

    #******************************************************************************
    # Check to see if the resource adapter has already been installed. 
    #******************************************************************************

    command = '/deployment=%s:read-attribute(name=status)' % rarName
    result = cli.cmd(command)
    if not result.success:
        print 'INFO: Deploying the %s resource adapter ' % rarName

        #******************************************************************************
        # Deploy the resource adapter
        #******************************************************************************

        command = 'deploy %s --name=%s --runtime-name=%s' % (fileName, rarName, rarName)
        checkSuccess(cli.cmd(command))

        #******************************************************************************
        # Add the resource adapter configuration
        #******************************************************************************

        command = '/subsystem=resource-adapters/resource-adapter=%s:add(archive=%s, transaction-support=NoTransaction)' % (rarName, rarName)
        checkSuccess(cli.cmd(command))

    return rarName
