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
# (C) 2014-2022 DXC Technology Company.
# All rights reserved.                                        
#******************************************************************************

import os, sys
from utilityFunctions import *

#******************************************************************************
# Please inspect all items marked with the UPDATE HERE comment
# and ensure they match your environment.
#******************************************************************************

# -------------------- UPDATE HERE ----------------------------------
# portOffsets allows you specify a port offset used by JBoss when
# more than one JBoss server will be running on a physical box. The
# port offset value gets added to each port used by JBoss to avoid
# conflicts.
#
# The 'default' entry will be 0 and is used if the PFINSTANCEID
# environment variable has not been specified.
#
# If you want to have two users, USERA and USERB, on the same machine,
# add the following entries:
#
# portOffsets = {
#         'default':0,
#         'USERA':1,
#         'USERB':2
#         }
# 
# Then set PFINSTANCEID to 'USERA' or 'USERB' for each user. 
# Alternatively, start each of the batch files with a parameter
# specifying the user ID. For example:
#
# initialize USERA
# deploy USERA
# startJBossAppServer USERA
# -------------------- UPDATE HERE ----------------------------------

portOffsets = {
        'default':0
        }

pathFinderServerName = getPathFinderServerName('pathfinder')
pathFinderServerFolder = getPathFinderServerFolder(pathFinderServerName)

class configuration:
    # -------------------- UPDATE HERE ----------------------------------
    # Setting debug to True allows developers to debug the PathFinder
    # server using a tool like Eclipse.
    #
    # The adminServer variable identifies the administration server that 
    # the PathFinder is being used with.  Valid values are 'INGENIUM' or
    # 'RADIENCE'.
    #
    # The pageSource variable identifies the type of pages being used.
    # PageBuilder uses JSP pages while PageServer uses HTML templates.
    # Valid values are 'HTML' or 'JSP'.
    #
    # serverConfigurationScript specifies the name of a jython file that
    # contains configuration information specific to your administration 
    # server. This is going to be Jython classes that provide variables 
    # used in your administration server specific scripts.
    #
    # serverInitializeScript is the name of a script containing routines
    # to perform initialization that is specific to your administration 
    # server. This script must contain a method called 
    # initializeAdministrationServer(cli) as this will be called by the 
    # initialize.py script.
    #
    # serverDeployScript is the name of the a script containing routines
    # to perform custom deployment actions for your administration 
    # server. This script must contain a method called 
    # deployAdministrationServerApps(cli) that will be called by the base
    # deployment script and provides the opportunity to deploy any 
    # applications that are unique to the administration server being
    # used. You must define the deployAdministrationServerApps(cli) method 
    # even if it doesn't do anything.
    # 
    # Do not include the .py extension in the script name.
    #
    # adminUserId is the ID of the administrative user for JBoss.
    # adminUserPassword is the password of the adminUserId.
    #
    # serverName is the name or IP address of the Windows or Unix server
    # where JBoss is running.
    # -------------------- UPDATE HERE ----------------------------------

    debug = True
    adminServer = 'INGENIUM'
    pageSource = 'JSP'

    serverConfigurationScript = 'ingeniumServerConfiguration'
    serverInitializeScript = 'initializeIngenium'
    serverDeployScript = 'deployIngenium'

    adminUserId = 'admin'
    adminUserPassword = 'solcorp-1234'

    serverName = '206.122.3.127'

    portOffset = getPortOffset(portOffsets)

class cluster:
    # -------------------- UPDATE HERE ----------------------------------
    # If clustered, set useCluster = True, else False 
    #
    # initialHosts is a comma separated list of servers and their 
    # jgroups-tcp ports that will be members of the cluster. For example:
    #
    # 'host1[7600], host1[7700]'
    #
    # In this example, host1 is running two instances of JBoss. The first
    # has a port offset of 0 meaning that the default port 7600 is used,
    # while the second has a port offset of 100, giving a jgroups-tcp port 
    # of 7700.
    #
    # 'host3[7600], host4[7600]'
    #
    # In this example, there are two servers, host3 and host 4, each 
    # running one instance of JBoss with a port offset of 0.
    #
    # password defines a password that controls which JBoss servers
    # can join the cluster. All JBoss servers listed in initialHosts 
    # must have the same password.
    # -------------------- UPDATE HERE ---------------------------------	

    useCluster = False
    initialHosts = 'CASPS243.americas.hpqcorp.net[7600], CASPS243.americas.hpqcorp.net[7700]'
    password = 'Cluster1'
	
    # -------------------- UPDATE HERE ---------------------------------
    # webserverName is the name of the Windows or Unix server where the 
    # HTTP server running mod_cluster is running.
    #
    # webserverPort is the web server port that JBoss will call to tell 
    # the web server that it is a member of the cluster. This port is 
    # specified in the httpd.conf file in the VirtualHost element. For 
    # example:
    #
    # <VirtualHost CASPS243.americas.hpqcorp.net:9090>
    #
    # In this example, the webserverPort is 9090.
    # -------------------- UPDATE HERE ---------------------------------

    webserverName = 'CASPS243.americas.hpqcorp.net'
    webserverPort = 9090

class security:
    # -------------------- UPDATE HERE ---------------------------------
    # Set this to True to use LDAP or False to use file based
    # user configuration.
    # -------------------- UPDATE HERE ---------------------------------

    useLdap = False

    class users:
        class manager:
            #******************************************************************************
            # These values are defined in the setJBossPFEnv.cmd batch file.  These 
            # credentials are used to sign in to the JBoss server for administration 
            # purposes.
            #******************************************************************************
            
            id = getEnvironmentVariable('ADMIN_USER_ID')
            password = getEnvironmentVariable('ADMIN_USER_PWD')
        class pathFinderClient:
            id = 'pfclient'
            password = 'solcorp-1234'
            role = 'pfrole'
        class consoleServerClient:
            id = 'csadmin'
            password = 'solcorp-1234'
            role = 'csrole'
        class debugClient:
            id = 'edclient'
            password = 'solcorp-1234'
            role = 'debugrole'

    #******************************************************************************
    # This section is only relevant if the security.useLdap variable is set to True
    #******************************************************************************

    class ldap:
        # -------------------- UPDATE HERE ---------------------------------
        # Update these values as appropriate for your LDAP server.
        # -------------------- UPDATE HERE ---------------------------------

        javaNamingProviderUrl = 'ldap://CASPS019.americas.hpqcorp.net:389/'
        bindDN = 'cn=root'
        bindCredential = 'solcorp1'
        baseCtxDN = 'ou=employees,DC=SOLCORP,DC=COM'
        baseFilter = '(uid={0})'
        rolesCtxDN = 'DC=SOLCORP,DC=COM'
        roleFilter = '(member=uid={0}*)'
        roleNameAttributeID = 'cn'
        roleAttributeIsDN = 'true'
        unauthenticatedIdentity = 'anonymous'

        # -------------------- UPDATE HERE ---------------------------------
        # Define the mapping between the role in the LDAP server and the
        # JBoss role. The first element is the role defined in the ldap 
        # while the second element is the EJB role used in JBoss.
        # -------------------- UPDATE HERE ---------------------------------

        roleMappings = [
            ['csrole', 'csrole'],
            ['pfrole', 'pfrole'],
            ['debugrole', 'debugrole']
        ]

#******************************************************************************
# PathFinder Configuration Information
#******************************************************************************

class pathFinder:
    class applications:
        class pathFinder:
            deploy = getEnvironmentVariable('DEPLOY_PATHFINDER').lower() == 'true'
            name = 'PathFinder'
            fileName = '../../PathFinderEar.ear'

            # -------------------- UPDATE HERE ---------------------------------
            # The .warContent variable can be the name of a directory
            # containing files that are going to be added to the WAR file.
            #
            # If set to None, then no extra files are added to the PageBuilder 
            # or PageServer WAR other than those in the Deployment folder. 
            #
            # If warContent is set to a folder name, then the contents of that 
            # folder are added to the servlet WAR prior to deployment. The folder
            # must have a directory structure that matches the WAR file
            # structure since the contents will be added to the WAR as-is.
            # -------------------- UPDATE HERE ---------------------------------

            warContent = None
        class bamServer:
            deploy = getEnvironmentVariable('DEPLOY_BAMSERVER').lower() == 'true'
            name = 'BamServer'
            fileName = '../../BamServerEar.ear'

            # -------------------- UPDATE HERE ---------------------------------
            # This is the directory where BAM report templates are stored.
            # This value will be assigned to the reports.folder JVM property.
            # -------------------- UPDATE HERE ---------------------------------

            reportsLocation = 'E:/I221_Windows/PR/Presentation/BamServer/reports'
        class consoleServer:
            deploy = getEnvironmentVariable('DEPLOY_CONSOLESERVER').lower() == 'true'
            name = 'ConsoleServer'
            fileName = '../../ConsoleServerEar.ear'
        class webServices:
            deploy = getEnvironmentVariable('DEPLOY_WEBSERVICES').lower() == 'true'
            name = 'WebServices'
            fileName = '../../PFWebServices.ear'
        class webServicesJaxrs:
            deploy = getEnvironmentVariable('DEPLOY_WEBSERVICES_JAXRS').lower() == 'true'
            name = 'WebServicesJaxrs'
            fileName = '../../PFWebServicesJaxrs.ear'			
        class birt:
            deploy = getEnvironmentVariable('DEPLOY_BIRTWAR').lower() == 'true'
            name = 'BirtReports'
            fileName = '../../birt-4.9.0.war'
    class jdbc:
        class modules:
            class DB2:
                # -------------------- UPDATE HERE ---------------------------------
                # Resource is the JBoss terminology for driver jars. Update the 
                # names of the driver jars and the folder where they're found.
                # -------------------- UPDATE HERE ---------------------------------

                driverName = 'db2jcc4'
                driverClass = 'com.ibm.db2.jcc.DB2Driver'
                moduleName = pathFinderServerName + '.com.ibm.db2'
                resourceFolder = 'c:\libs\DB2-11.5'
                resources = [ 'db2jcc4.jar', 'db2jcc_license_cu.jar' ]
                dependencies = [ 'javax.api', 'javax.transaction.api', 'sun.jdk']

            class Oracle:
                # -------------------- UPDATE HERE ---------------------------------
                # Resource is the JBoss terminology for driver jars. Update the 
                # names of the driver jars and the folder where they're found.
                # -------------------- UPDATE HERE ---------------------------------

                driverName = 'oracle'
                driverClass = 'oracle.jdbc.driver.OracleDriver'
                moduleName = pathFinderServerName + '.com.oracle'
                resourceFolder = 'c:\Libs\oracle'
                resources = [ 'ojdbc6.jar' ]
                dependencies = [ 'javax.api', 'javax.transaction.api' ]
                
            class SQL:
                # -------------------- UPDATE HERE ---------------------------------
                # Resource is the JBoss terminology for driver jars. Update the 
                # names of the driver jars and the folder where they're found.
                # -------------------- UPDATE HERE ---------------------------------

                driverName = 'sqlserver'
                driverClass = 'com.microsoft.sqlserver.jdbc.SQLServerDriver'
                moduleName = pathFinderServerName + '.com.microsoft.sqlserver'
                resourceFolder = 'C:\SqlserverLib\sqljdbc_9.4\enu'
                resources = [ 'mssql-jdbc-9.4.0.jre8.jar' ]
                dependencies = [ 'javax.api', 'javax.transaction.api', 'sun.jdk']

            # -------------------- UPDATE HERE ---------------------------------
            # Specify which JDBC driver modules to create. For example, if
            # you're only using DB2 then just specify DB2:
            #
            # list = [ DB2() ]
            #
            # If you're using a mixture of DB2, Oracle and SQL then specify both like 
            # this:
            #
            # list = [ DB2(), Oracle(), SQL() ]
            #
            # and both modules will be created.
            # -------------------- UPDATE HERE ---------------------------------

            list = [ SQL() ]

        class processPool:
            # -------------------- UPDATE HERE ---------------------------------
            # Update these entries with the server name, database name and
            # port of the database server hosting the PathFinder process pool
            # database. This is the database where the PathFinder stores
            # process state.
            # -------------------- UPDATE HERE ---------------------------------

            #******************************************************************************
            # Use the following settings to create a process pool using the internal H2
            # database. The H2 database should not be used in a production environment.
            # Be sure to specify the correct path to the PFCreateTable.sql script.
            #
            # connectionUrl = "jdbc:h2:${jboss.server.data.dir}/processpool;INIT=RUNSCRIPT FROM 'c:/dev/deployment/database/h2/PFCreateTable.sql'"
            # driverName = 'h2'
            # userId = 'sa'
            # password = 'sa'
            #
            # These settings configure the process pool on a DB2 database
            #
            # connectionUrl = 'jdbc:db2://casps240.americas.hpqcorp.net:50001/PFJBOSS'
            # driverName = 'db2jcc4'
            # userId = 'pfuser'
            # password = 'develop-1234'
			#
			# These settings configure the process pool on a SQL Server database
			#
			# connectionUrl = "jdbc:sqlserver://206.122.3.80:1433;DatabaseName=PATHFINDER"
            # driverName = 'sqlserver'
            # userId = 'ingenium'
            # password = 'develop-1234'
			#
            #******************************************************************************

            connectionUrl = "jdbc:sqlserver://206.122.3.127:1433;DatabaseName=PATHFINDER"
            driverName = 'sqlserver'
            userId = 'ingenium'
            password = 'develop-1234'

        class bamServer:
            # -------------------- UPDATE HERE ---------------------------------
            # Set the connection URL and the user id and password of the
            # database connection. This is the database used by the BamServer
            # to store the BAM data used to generate reports.
            # -------------------- UPDATE HERE ---------------------------------

            #******************************************************************************
            # The following settings configure BAM logging to use the internal H2 database.
            # The H2 database should not be used in a production environment.
            #
            # connectionUrl = 'jdbc:h2:${jboss.server.data.dir}/bamlogging'
            # driverName = 'h2'
            # userId = 'sa'
            # password = 'sa'
            #
            # These settings configure BAM logging to use a DB2 database
            #
            # connectionUrl = 'jdbc:db2://casps240.americas.hpqcorp.net:50001/PFJBOSS'
            # driverName = 'db2jcc4'
            # userId = 'pfuser'
            # password = 'develop-1234'
			#
			# These settings configure BAM logging to use a SQL Server database
			#
			# connectionUrl = "jdbc:sqlserver://206.122.3.80:1433;DatabaseName=PATHFINDER"
            # driverName = 'sqlserver'
            # userId = 'ingenium'
            # password = 'develop-1234'
			#
            #******************************************************************************

             connectionUrl = 'jdbc:sqlserver://206.122.3.127:1433;DatabaseName=PATHFINDER'
             driverName = 'sqlserver'
             userId = 'ingenium'
             password = 'develop-1234'
