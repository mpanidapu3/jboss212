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
# (C) 2010-2022 DXC Technology Company.
# All rights reserved.                                        
#******************************************************************************

from utilityFunctions import *
from serverConfiguration import *

#******************************************************************************
# This file contains configuration entries for PathFinder with 
# DXC Ingenium and should be updated to match your configuration.
# Please inspect all items marked with the UPDATE HERE comment
# and ensure they match your environment.
#******************************************************************************

# -------------------- UPDATE HERE ---------------------------------
# If using LDAP then we need to add the IngeniumRole mapping to
# the list of mappings that will be stored in the mappings 
# configuration file.
#
# The first element is the role defined in the LDAP server while
# the second element is the role specified in the web.xml
# -------------------- UPDATE HERE ---------------------------------

if security.useLdap:
    security.ldap.roleMappings.append(['IngeniumGroup', 'IngeniumRole']);

class ingenium:
    # -------------------- UPDATE HERE ---------------------------------
    # The gateway variable identifies a Gateway implementation that is
    # used by PathFinder when it needs to communicate with the DXC 
    # Ingenium server. The variable gateway must be set to one of the 
    # following values:
    #
    # JMS		The JMSGateway is used. The MQ RAR will be installed.
    # IBMCICS	The IBMCicsGateway is used
    # AS400		The AS400Gateway is used
    # ACTIVEMQ  The ACTIVEMQ is used. The ACTIVEMQ RAR will be installed.
    #
    # Set usePFC to True to enable PathFinderConnector.
    # -------------------- UPDATE HERE ---------------------------------

    gateway = 'ACTIVEMQ'
    usePFC = True

    class applications:
        class pfc:
            deploy = getEnvironmentVariable('DEPLOY_PATHFINDERCONNECTOR').lower() == 'true'
            name = 'PathFinderConnector'
            fileName = '../../PathFinderConnectorEar.ear'

            # -------------------- UPDATE HERE ---------------------------------
            # The listener variable can be set to 'QUEUE' or 'SOCKET'. If set 
            # to 'QUEUE', PFC will use an MQ queue to communicate with DXC 
            # Ingenium. If set to 'SOCKET' then PFC will use TCP/IP sockets.
            # -------------------- UPDATE HERE ---------------------------------

            listener = 'QUEUE'

            #******************************************************************************
            # This section is only relevant if listener is set to 'QUEUE'
            #******************************************************************************

            class jms:
                # -------------------- UPDATE HERE ---------------------------------
                # The rarFile variable specifies the fully qualified name of the MQ 
                # RAR file. Use the 8 character short name for any directory names 
                # that have spaces in them.
                # -------------------- UPDATE HERE ---------------------------------

                rarFile = 'C:\Libs\MQ-9.2.0.1\wmq.jmsra.rar'
                connectionClass = 'com.ibm.mq.connector.outbound.ManagedQueueConnectionFactoryImpl'
                connectionName = 'PFCConnectionFactory'
                connectionJndiName = 'java:/app/eis/PFCConnectionFactory'

                # -------------------- UPDATE HERE ---------------------------------
                # Update the configuration properties for the MQ server used to
                # communicate with INGENIUM.
                # -------------------- UPDATE HERE ---------------------------------

                attributes = [
                    ['hostName', '206.122.3.242'],
                    ['port', '1414'],
                    ['queueManager', 'PFP01'],
                    ['channel', 'PFCLIENT'],
                    ['username', 'pfclient'],
                    ['password', 'solcorp-1234'],
                    ['transportType', 'CLIENT']
                    ]

                # -------------------- UPDATE HERE ---------------------------------
                # These attribute are used by the PathFinderConnectorMDB's 
                # jboss-ejb3.xml deployment file to set the value of the activation 
                # config properties. These attributes are set as system properties 
                # that are referenced using the ${PFCConnectionFactory.destination} 
                # notation. These values must match the values specified in the
                # attributes element above.
                # -------------------- UPDATE HERE ---------------------------------

                mdbAttributes = [
                    ['PathFinderConnectorMDB.destination', 'java:/app/jms/PFCRequestQueue'],
                    ['PathFinderConnectorMDB.hostName', '206.122.3.242'],
                    ['PathFinderConnectorMDB.port', '1414'],
                    ['PathFinderConnectorMDB.username', 'pfclient'],
                    ['PathFinderConnectorMDB.password', 'solcorp-1234'],
                    ]

                class queues:
                    # -------------------- UPDATE HERE ---------------------------------
                    # Specify the properties for the queue that PFC uses to receive a
                    # request to DXC Ingenium. The name property is used to build the 
                    # JNDI name of the queue. If you change it you will need to change
                    # the JNDI name specified in the file:
                    # Deployment\jboss\deployplans\PathFinderConnectorEar\
                    #        PathFinderConnectorEjb.jar\META-INF-jboss-ejb3.xml
                    # -------------------- UPDATE HERE ---------------------------------

                    class requestQueue:
                        name      = 'PFCRequestQueue'
                        queueName = 'PF.PFC.PR221.REQUEST'
                        className = 'com.ibm.mq.connector.outbound.MQQueueProxy'
                        attributes = [
                            ['targetClient', 'MQ'],
                            ['baseQueueManagerName', 'PFP01'],
                            ['persistence', 'NON']
                            ]

                    # -------------------- UPDATE HERE ---------------------------------
                    # Specify the properties for the queue that PFC uses to send a 
                    # response to DXC Ingenium. The name property is used to build the 
                    # JNDI name of the queue. If you change it you will need to change 
                    # the JNDI name specified in the file:
                    # Deployment\jboss\deployplans\PathFinderConnectorEar\
                    #        PathFinderConnectorEjb.jar\META-INF-jboss-ejb3.xml
                    # -------------------- UPDATE HERE ---------------------------------

                    class responseQueue:
                        name      = 'PFCResponseQueue'
                        queueName = 'PF.PFC.PR221.RESPONSE'
                        className = 'com.ibm.mq.connector.outbound.MQQueueProxy'
                        attributes = [
                            ['targetClient', 'MQ'],
                            ['baseQueueManagerName', 'PFP01'],
                            ['persistence', 'NON']
                            ]

                    list = [requestQueue, responseQueue]

            class jmsActiveMQ:
                # -------------------- UPDATE HERE ---------------------------------
                # The rarFile variable specifies the fully qualified name of the MQ 
                # RAR file. Use the 8 character short name for any directory names 
                # that have spaces in them.
                # -------------------- UPDATE HERE ---------------------------------

                rarFile = 'C:/Libs/ActiveMQ/activemq-rar.rar'
                connectionClass = 'org.apache.activemq.ra.ActiveMQManagedConnectionFactory'
                connectionName = 'PFCConnectionFactory'
                connectionJndiName = 'java:/app/eis/PFCConnectionFactory'

                # -------------------- UPDATE HERE ---------------------------------
                # Update the configuration properties for the MQ server used to
                # communicate with INGENIUM.
                # -------------------- UPDATE HERE ---------------------------------

                attributes = [
                    ['UserName', 'admin'],
                    ['Password', 'admin'],
                    ['ServerUrl', 'tcp://206.122.3.127:61616']
                    ]

                # -------------------- UPDATE HERE ---------------------------------
                # These attribute are used by the PathFinderConnectorMDB's 
                # jboss-ejb3.xml deployment file to set the value of the activation 
                # config properties. These attributes are set as system properties 
                # that are referenced using the ${PFCConnectionFactory.destination} 
                # notation. These values must match the values specified in the
                # attributes element above.
                # -------------------- UPDATE HERE ---------------------------------

                mdbAttributes = [
                    ['PathFinderConnectorMDB.destination', 'java:/app/jms/PFCRequestQueue']
                    ]

                class queues:
                    # -------------------- UPDATE HERE ---------------------------------
                    # Specify the properties for the queue that PFC uses to receive a
                    # request to DXC Ingenium. The name property is used to build the 
                    # JNDI name of the queue. If you change it you will need to change
                    # the JNDI name specified in the file:
                    # Deployment\jboss\deployplans\PathFinderConnectorEar\
                    #        PathFinderConnectorEjb.jar\META-INF-jboss-ejb3.xml
                    # -------------------- UPDATE HERE ---------------------------------

                    class requestQueue:
                        name      = 'PFCRequestQueue'
                        queueName = 'PF.PFC.PR221.REQUEST'
                        className = 'org.apache.activemq.command.ActiveMQQueue'
                        jndiName = 'java:/app/jms/PFCRequestQueue'
                        attributes = [
                           ['PhysicalName', 'PF.PFC.PR221.REQUEST']
                           ]

                    # -------------------- UPDATE HERE ---------------------------------
                    # Specify the properties for the queue that PFC uses to send a 
                    # response to DXC Ingenium. The name property is used to build the 
                    # JNDI name of the queue. If you change it you will need to change 
                    # the JNDI name specified in the file:
                    # Deployment\jboss\deployplans\PathFinderConnectorEar\
                    #        PathFinderConnectorEjb.jar\META-INF-jboss-ejb3.xml
                    # -------------------- UPDATE HERE ---------------------------------

                    class responseQueue:
                        name      = 'PFCResponseQueue'
                        queueName = 'PF.PFC.PR221.RESPONSE'
                        className = 'org.apache.activemq.command.ActiveMQQueue'
                        jndiName = 'java:/app/jms/PFCResponseQueue'                        
                        attributes = [
                           ['PhysicalName', 'PF.PFC.PR221.RESPONSE']
                           ]

                    list = [requestQueue, responseQueue]
    #******************************************************************************
    # This section is only relevant if you are using CICS to communicate with 
    # DXC Ingenium.
    #******************************************************************************

    class CICSGateway:
        # -------------------- UPDATE HERE ---------------------------------
        # The rarFile variable specifies the fully qualified name of the 
        # cicseci.rar file provided by the CICS Transaction Gateway.  Use 
        # the 8 character short name for any directory names that have 
        # spaces in them.
        # -------------------- UPDATE HERE ---------------------------------

        rarFile = 'c:\Libs\CICS\cicseci.rar'
        connectionClass = 'com.ibm.connector2.cics.ECIManagedConnectionFactory'
        connectionName = 'IngeniumConnectionFactory'
        connectionJndiName = 'java:/app/eis/IngeniumConnectionFactory'

        # -------------------- UPDATE HERE ---------------------------------
        # Specify the name, URL and port number of the CTG server.  If
        # you are using a local CTG then the connectionURL should be the
        # string 'local:'.  If using a remote CTG then connectionURL will
        # be 'tcp://server.name.com'.
        # Set userName and password to the name and password of the CICS
        # user under which the call to DXC Ingenium will be made.
        # -------------------- UPDATE HERE ---------------------------------

        attributes = [
            ['serverName', 'PR721'],
            ['connectionURL', 'tcp://206.122.3.162'],
            ['portNumber', '2006'],
            ['userName', 'CICSUSER'],
            ['password', 'CICSUSER']
            ]

    #******************************************************************************
    # This section is only relevant if you are using IBM MQ to
    # communicate with DXC Ingenium.
    #******************************************************************************

    class JMSGateway:
            # -------------------- UPDATE HERE ---------------------------------
            # The rarFile variable specifies the fully qualified name of the MQ 
            # rar file. Use the 8 character short name for any directory names 
            # that have spaces in them. If the name of the rar file isn't 
            # wmq.jmsra.rar then you must either rename it to that or update the 
            # module dependency in the JMS Gateway's jboss-deployment-structure.xml
            # since the name of the module is based upon the name of the rar file.
            # -------------------- UPDATE HERE ---------------------------------

            rarFile = 'C:\Libs\MQ-9.2.0.1\wmq.jmsra.rar'
            connectionClass = 'com.ibm.mq.connector.outbound.ManagedQueueConnectionFactoryImpl'
            connectionName = 'IngeniumJmsGatewayConnectionFactory'
            connectionJndiName = 'java:/app/eis/IngeniumJmsGatewayConnectionFactory'

            # -------------------- UPDATE HERE ---------------------------------
            # Update the configuration properties for the MQ server used to
            # communicate with INGENIUM.
            # -------------------- UPDATE HERE ---------------------------------

            attributes = [
                ['hostName', '206.122.3.242'],
                ['port', '1414'],
                ['queueManager', 'PFP01'],
                ['channel', 'PFCLIENT'],
                ['username', 'pfclient'],
                ['password', 'solcorp-1234'],
                ['transportType', 'CLIENT']
                ]

            class queues:
                # -------------------- UPDATE HERE ---------------------------------
                # Specify the properties for the dispatch queue that DXC Ingenium 
                # uses to indicate that it is ready to process a request. The name 
                # property is used to build the JNDI name of the queue. If you 
                # change it you will need to change the JNDI name specified in the 
                # JMS gateway's jboss-ejb3.xml file.
                # -------------------- UPDATE HERE ---------------------------------

                class dispatchQueue:
                    name      = 'IngeniumDispatchQueue'
                    queueName = 'PF.INGENIUM.PR221.D'
                    className = 'com.ibm.mq.connector.outbound.MQQueueProxy'
                    attributes = [
                        ['targetClient', 'MQ'],
                        ['persistence', 'NON']
                        ]

                # -------------------- UPDATE HERE ---------------------------------
                # Specify the properties for the input queue that DXC Ingenium uses
                # to receive requests from the PathFinder.  The name property is 
                # used to build the JNDI name of the queue. If you change it you 
                # will need to change the JNDI name specified in the JMS gateway's
                # jboss-ejb3.xml file.
                # -------------------- UPDATE HERE ---------------------------------

                class inQueue:
                    name      = 'IngeniumInQueue'
                    queueName = 'PF.INGENIUM.PR221.I'
                    className = 'com.ibm.mq.connector.outbound.MQQueueProxy'
                    attributes = [
                        ['targetClient', 'MQ'],
                        ['persistence', 'NON']
                        ]

                # -------------------- UPDATE HERE ---------------------------------
                # Specify the properties for the output queue that DXC Ingenium uses
                # to send responses back to the PathFinder.  The name property is 
                # used to build the JNDI name of the queue. If you change it you 
                # will need to change the JNDI name specified in the JMS gateway's
                # jboss-ejb3.xml file.
                # -------------------- UPDATE HERE ---------------------------------

                class outQueue:
                    name      = 'IngeniumOutQueue'
                    queueName = 'PF.INGENIUM.PR221.O'
                    className = 'com.ibm.mq.connector.outbound.MQQueueProxy'
                    attributes = [
                        ['targetClient', 'MQ'],
                        ['persistence', 'NON']
                        ]

                list = [dispatchQueue, inQueue, outQueue]
                
    class ActiveMQGateway:
            # -------------------- UPDATE HERE ---------------------------------
            # The rarFile variable specifies the fully qualified name of the MQ 
            # rar file. Use the 8 character short name for any directory names 
            # that have spaces in them. If the name of the rar file isn't 
            # wmq.jmsra.rar then you must either rename it to that or update the 
            # module dependency in the JMS Gateway's jboss-deployment-structure.xml
            # since the name of the module is based upon the name of the rar file.
            # -------------------- UPDATE HERE ---------------------------------

            rarFile = 'C:/Libs/ActiveMQ/activemq-rar.rar'
            connectionClass = 'org.apache.activemq.ra.ActiveMQManagedConnectionFactory'
            connectionName = 'IngeniumJmsGatewayConnectionFactory'
            connectionJndiName = 'java:/app/eis/IngeniumJmsGatewayConnectionFactory'

            # -------------------- UPDATE HERE ---------------------------------
            # Update the configuration properties for the MQ server used to
            # communicate with INGENIUM.
            # -------------------- UPDATE HERE ---------------------------------

            attributes = [
                ['UserName', 'admin'],
                ['Password', 'admin'],
                ['ServerUrl', 'tcp://206.122.3.127:61616']
                ]

            class queues:
                # -------------------- UPDATE HERE ---------------------------------
                # Specify the properties for the dispatch queue that DXC Ingenium 
                # uses to indicate that it is ready to process a request. The name 
                # property is used to build the JNDI name of the queue. If you 
                # change it you will need to change the JNDI name specified in the 
                # JMS gateway's jboss-ejb3.xml file.
                # -------------------- UPDATE HERE ---------------------------------

                class dispatchQueue:
                    name      = 'IngeniumDispatchQueue'
                    queueName = 'PF.INGENIUM.PR221.D'
                    className = 'org.apache.activemq.command.ActiveMQQueue'
                    attributes = [['PhysicalName','PF.INGENIUM.PR221.D']]
                  

                # -------------------- UPDATE HERE ---------------------------------
                # Specify the properties for the input queue that DXC Ingenium uses
                # to receive requests from the PathFinder.  The name property is 
                # used to build the JNDI name of the queue. If you change it you 
                # will need to change the JNDI name specified in the JMS gateway's
                # jboss-ejb3.xml file.
                # -------------------- UPDATE HERE ---------------------------------

                class inQueue:
                    name      = 'IngeniumInQueue'
                    queueName = 'PF.INGENIUM.PR221.I'
                    className = 'org.apache.activemq.command.ActiveMQQueue'
                    attributes = [['PhysicalName','PF.INGENIUM.PR221.I']]

                # -------------------- UPDATE HERE ---------------------------------
                # Specify the properties for the output queue that DXC Ingenium uses
                # to send responses back to the PathFinder.  The name property is 
                # used to build the JNDI name of the queue. If you change it you 
                # will need to change the JNDI name specified in the JMS gateway's
                # jboss-ejb3.xml file.
                # -------------------- UPDATE HERE ---------------------------------

                class outQueue:
                    name      = 'IngeniumOutQueue'
                    queueName = 'PF.INGENIUM.PR221.O'
                    className = 'org.apache.activemq.command.ActiveMQQueue'
                    attributes = [['PhysicalName','PF.INGENIUM.PR221.O']]

                list = [dispatchQueue, inQueue, outQueue]
                
    class ingeniumDatabaseConnection:
        # -------------------- UPDATE HERE ---------------------------------
        # Update these entries with the server name, database name and
        # port of the database server hosting the DXC Ingenium database.
        # Specify the user ID and password of a user with at least read 
        # access to the database.
		# connectionUrl = 'jdbc:sqlserver://206.122.3.80:1433;DatabaseName=INGENIUM'
        # driverName = 'sqlserver'
        # -------------------- UPDATE HERE ---------------------------------

        connectionUrl = 'jdbc:sqlserver://206.122.3.127:1433;DatabaseName=SS2211P1'
        driverName = 'sqlserver'
        userId = 'ingenium'
        password = 'develop-1234'
