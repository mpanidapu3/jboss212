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

def main():
    connected = False
    cli = CLI.newInstance()

    try:
        connected = connectToServer(cli, configuration)

        configurePathFinderServer(cli)

        if (cluster.useCluster):
            configureCluster(cli)	
        
        initializeSecurity(cli)
        
        configureJDBC(cli)

        configureJMS(cli)
        
        initializeAdministrationServer(cli)

        displayPorts(cli)

        print 'INFO: Reloading the server configuration'
        cli.cmd(':reload')
    except:
        print 'ERROR: Initialization failed: ', sys.exc_info()[1]
    finally:
        if connected:
            print 'INFO: Disconnecting...'
            cli.disconnect()

#******************************************************************************
# This method will create the PathFinder server by copying the server 
# template files from the JBoss/standlone directory to a directory in
# JBoss/PathFinderServers with the name of the server appended by the 
# value of the PFINSTANCEID environment variable, if it is defined.
#******************************************************************************

def createServer():
    #******************************************************************************
    # templateFolder will be the name of the JBoss standalone folder used to 
    # create the PathFinder server. Make sure that it exists.
    #******************************************************************************

    jBossHome = getEnvironmentVariable('JBOSS_HOME').replace('"', '').replace('\\', '/')
    templateFolder = jBossHome + '/standalone'
    if not os.path.isdir(templateFolder):
        print 'ERROR: The default JBoss server folder %s does not exist' % templateFolder
        sys.exit(1)

    #******************************************************************************
    # If the PathFinder server folder already exists, then ask the user if the
    # want to delete it. If they do, remove the server folder and the modules
    # folder.
    #******************************************************************************

    if os.path.isdir(pathFinderServerFolder):
        #******************************************************************************
        # There are two folders to delete. The server folder and the modules folder
        # where components like the JDBC drivers are located.
        #******************************************************************************

        moduleFolder = jBossHome + '/modules/' + pathFinderServerName

        delete = raw_input('The server \'%s\' already exists. Press Y and enter to delete the existing server: ' % pathFinderServerName).upper()

        if delete == 'Y':
            print 'INFO: Deleting the \'%s\' server' % pathFinderServerName
            shutil.rmtree(pathFinderServerFolder, True)
            shutil.rmtree(moduleFolder, True)
        else:
            print 'INFO: Initialization cancelled'
            sys.exit()

        #******************************************************************************
        # There may be situations where we cannot delete the folders because the user
        # has a log file open or some other situation. We'll log an error if the 
        # folder still exists.
        #******************************************************************************

        if os.path.isdir(pathFinderServerFolder):
            print 'ERROR: Unable to delete the folder %s' % pathFinderServerFolder
            sys.exit(1)

        if os.path.isdir(moduleFolder):
            print 'ERROR: Unable to delete the folder %s' % moduleFolder
            sys.exit(1)

    #******************************************************************************
    # Copy the server template folder to the PathFinder server folder.
    #******************************************************************************

    try:
        print 'INFO: Copying server configuration from %s to %s' % (templateFolder, pathFinderServerFolder)
        shutil.copytree(templateFolder, pathFinderServerFolder)
    except:
        pass

#******************************************************************************
# We need to run the add-user batch file to add the administrative user to the
# server. The administrative user is used to log into the JBoss admin console
# and to connect to the server to deploy applications.
#******************************************************************************

def createAdminUser():
    print 'INFO: Adding the administrative user \'%s\'' % configuration.adminUserId

    #******************************************************************************
    # The extension of the command will be different between Windows and Unix.
    #******************************************************************************

    if re.search('windows', java.lang.System.getProperty('os.name').lower()):
        fileExt = '.bat'	
    else:
        fileExt = '.sh'			

    #******************************************************************************
    # The JAVA_OPTS environment variable specifesthe location of the configuration 
    # that we want to update. The NOPAUSE environment variable prevents the 
    # add-user batch file from prompting the user to "press any key to continue" 
    # when it ends.
    #******************************************************************************			

    javaOptions = [
        ' -Djboss.server.config.user.dir=%s/configuration' % pathFinderServerFolder,
        ' -Djboss.domain.config.user.dir=%s/configuration' % pathFinderServerFolder
        ]

    os.putenv('NOPAUSE', 'True')
    os.putenv('JAVA_OPTS', ''.join(javaOptions))

    workingDir = getEnvironmentVariable('JBOSS_HOME').replace('"', '') + '/bin'

    cmd = workingDir + '/add-user%s --silent=true %s %s' % (fileExt, configuration.adminUserId, configuration.adminUserPassword)
    process = subprocess.Popen(cmd, shell = True, cwd = workingDir)
    process.communicate()

#******************************************************************************
# Initialize the PathFinder server
#******************************************************************************

def configurePathFinderServer(cli):
    print 'INFO: Configuring the PathFinder server'

    #******************************************************************************
    # Create system property for BIRT reports
    #******************************************************************************

    command = '/system-property=reports.folder:add(value=%s)' % pathFinder.applications.bamServer.reportsLocation
    checkSuccess(cli.cmd(command))

    #******************************************************************************
    # Create the singleton MDB pool that restricts the number of MDBs 
    # associated with it to one instance. MDBs are associated using the 
    # pool/bean-instance-pool-ref element in the jboss-ejb3.xml file
    #******************************************************************************

    command = '/subsystem =ejb3/strict-max-bean-instance-pool=mdb-strict-singleton-pool:add(max-pool-size=1, timeout=5, timeout-unit="MINUTES")'
    checkSuccess(cli.cmd(command))

    #******************************************************************************
    # Enable compression of the returned files.
    #******************************************************************************

    command = '/system-property=org.apache.coyote.http11.Http11Protocol.COMPRESSION:add(value="on")'
    checkSuccess(cli.cmd(command))

    command = '/system-property=org.apache.coyote.http11.Http11Protocol.COMPRESSION_MIME_TYPES:add(value="text/javascript,text/css,text/html")'
    checkSuccess(cli.cmd(command))


    #******************************************************************************
    # Changing the MAX_PARAMETER to http listner in the JBOSS
    # for huge volume exchange between ingenium and JBOSS App Server
    #******************************************************************************

    command = '/subsystem=undertow/server=default-server/http-listener=default/:write-attribute(name=max-parameters,value=3000)'
    checkSuccess(cli.cmd(command))


#******************************************************************************
# Initialize the security parameters
#******************************************************************************

def initializeSecurity(cli):
    users = [
        security.users.pathFinderClient, 
        security.users.consoleServerClient, 
        security.users.debugClient
        ]

    #******************************************************************************
    # Turn off the flag that says that all methods on a secured EJB are secured
    # if they don't specify a security descriptor.
    #******************************************************************************

    command = '/subsystem=ejb3:write-attribute(name=default-missing-method-permissions-deny-access, value=false)'
    checkSuccess(cli.cmd(command))

    #******************************************************************************
    # Add the PathFinder security domain
    #******************************************************************************

    realmName = 'PathFinderRealm'
    domainName = 'pathfinder-domain'

    print 'INFO: Creating the %s realm' % realmName

    command = '/core-service=management/security-realm=%s:add()' % realmName
    checkSuccess(cli.cmd(command))

    command = '/core-service=management/security-realm=%s/authentication=jaas:add(name=%s)' % (realmName, domainName)
    checkSuccess(cli.cmd(command))

    #******************************************************************************
    # We need to set the realm for the remoting-connector to the PathFinder realm
    #******************************************************************************

    command = '/subsystem=remoting/http-connector=http-remoting-connector:write-attribute(name=security-realm,value=%s)' % realmName
    checkSuccess(cli.cmd(command))

    print 'INFO: Creating the %s security domain' % domainName

    command = '/subsystem=security/security-domain=%s/:add(cache-type=default)' % domainName
    checkSuccess(cli.cmd(command))

    #******************************************************************************
    # If not using LDAP then add the standard file based login module
    #******************************************************************************

    if not security.useLdap:
        print 'INFO: Configuring the file based security login module'

        command = '/subsystem=security/security-domain=%s/authentication=classic:add(login-modules=[' + \
            '{"code"=>"RealmUsersRoles", "flag"=>"required", "module-options"=>[' + \
                '("usersProperties"=>"${jboss.server.config.dir}/pathfinder-users.properties"),' + \
                '("rolesProperties"=>"${jboss.server.config.dir}/pathfinder-roles.properties"),' + \
                '("realm"=>"%s"),' + \
                '("hashAlgorithm"=>"MD5"),' + \
                '("hashEncoding"=>"hex"),' + \
                '("password-stacking"=>"useFirstPass")' + \
                ']}' + \
            '])'
        checkSuccess(cli.cmd(command % (domainName, realmName)))

        #******************************************************************************
        # Create the role properties file
        #******************************************************************************

        rolesPropertiesFileName = '%s/configuration/pathfinder-roles.properties' % pathFinderServerFolder
        print 'INFO: Creating the roles properties file %s' % rolesPropertiesFileName

        rolesFile = open(rolesPropertiesFileName, 'w')
        for user in users:
            rolesFile.write('%s=%s\n' % (user.id, user.role))
        rolesFile.close()

        #******************************************************************************
        # Create the users properties file
        #******************************************************************************

        usersPropertiesFileName = '%s/configuration/pathfinder-users.properties' % pathFinderServerFolder
        print 'INFO: Creating the users properties file %s' % usersPropertiesFileName

        usersFile = open(usersPropertiesFileName, 'w')
        for user in users:
            md5 = hashlib.md5()
            md5.update(user.id + ':' + realmName + ':' + user.password)
            usersFile.write('%s=%s\n' % (user.id, md5.hexdigest()))
        usersFile.close()
    else:
        #******************************************************************************
        # If using LDAP then add the LDAP login module and create the role mapping file
        #******************************************************************************

        print 'INFO: Configuring the LDAP based security login module'

        c = security.ldap
        command = '/subsystem=security/security-domain=%s/authentication=classic:add(login-modules=[' + \
            '{"code"=>"LdapExtended", "flag"=>"required", "module-options"=>[' + \
                '("java.naming.provider.url"=>"' + c.javaNamingProviderUrl + \
                '"),("java.naming.factory.initial"=>"com.sun.jndi.ldap.LdapCtxFactory' + \
                '"),("java.naming.security.authentication"=>"simple' + \
                '"),("roleRecursion"=>"0' + \
                '"),("bindDN"=>"' + c.bindDN + \
                '"),("bindCredential"=>"' + c.bindCredential + \
                '"),("baseCtxDN"=>"' + c.baseCtxDN + \
                '"),("baseFilter"=>"' + c.baseFilter + \
                '"),("rolesCtxDN"=>"' + c.rolesCtxDN + \
                '"),("roleFilter"=>"' + c.roleFilter + \
                '"),("roleNameAttributeID"=>"' + c.roleNameAttributeID + \
                '"),("roleAttributeIsDN"=>"' + c.roleAttributeIsDN + \
                '"),("unauthenticatedIdentity"=>"' + c.unauthenticatedIdentity + \
                '")]},' + \
            '{"code"=>"RoleMapping", "flag"=>"optional", "module-options"=>[' + \
                '("rolesProperties"=>"file:${jboss.server.config.dir}/pathfinder-ldap-role-mapping.properties")' + \
                ']}' + \
            '])'

        checkSuccess(cli.cmd(command % domainName))

        fileName = '%s/configuration/pathfinder-ldap-role-mapping.properties' % pathFinderServerFolder
        
        print 'INFO: Creating the %s LDAP role mapping file' % fileName

        mappingFile = open(fileName, 'w')
        for mapping in security.ldap.roleMappings:
            mappingFile.write('%s=%s\n' % (mapping[0], mapping[1]))
        mappingFile.close()

#******************************************************************************
# Initialize the JDBC connections
#******************************************************************************

def configureJDBC(cli):
    print 'INFO: Initializing PathFinder JDBC connections'

    #******************************************************************************
    # Create the JDBC driver modules
    #******************************************************************************

    for module in pathFinder.jdbc.modules.list:
        #******************************************************************************
        # Resources is the JBoss terminology for driver jars.
        #******************************************************************************

        resources = ''
        for resourceName in module.resources:
            if len(resources) > 0:
                resources += ','
            fileName = '%s/%s' % (module.resourceFolder, resourceName)
            if not os.path.isfile(fileName):
                raise Exception('Unable to locate the JDBC driver file %s' % fileName)

            resources += '%s/%s' % (module.resourceFolder, resourceName)

        #******************************************************************************
        # List the module dependencies on other other modules
        #******************************************************************************

        dependencies = ''
        for dependency in module.dependencies:
            if len(dependencies) > 0:
                dependencies += ','

            dependencies += dependency

        print 'INFO: Creating JDBC module ', module.moduleName
        command = 'module add --name=%s --resource-delimiter=, --resources=%s --dependencies=%s' % (module.moduleName, resources, dependencies)
        cli.cmd(command)

        #******************************************************************************
        # Register a driver that uses the module.
        #******************************************************************************

        print 'INFO: Creating JDBC driver ', module.driverName
        command = '/subsystem=datasources/jdbc-driver=%s:add(driver-name=%s,driver-module-name=%s,driver-class-name=%s)' % (module.driverName, module.driverName, module.moduleName, module.driverClass)
        checkSuccess(cli.cmd(command))

    #******************************************************************************
    # Create the BamServer database connection
    #******************************************************************************

    connection = pathFinder.jdbc.bamServer
    print 'INFO: Creating the BamServer database connection %s' % connection.connectionUrl

    command = 'data-source add --name=BamServerDataSource --jndi-name=java:/app/jdbc/BamServerDataSource --driver-name=%s --connection-url="%s" --user-name=%s --password=%s --pool-prefill=false --use-java-context=true' % (connection.driverName, connection.connectionUrl, connection.userId, connection.password)
    checkSuccess(cli.cmd(command))

    print 'INFO: Testing the BamServer database connection'
    command = 'data-source test-connection-in-pool --name=BamServerDataSource'
    checkSuccess(cli.cmd(command))

    #******************************************************************************
    # Create the PathFinder process pool database connection
    #******************************************************************************

    connection = pathFinder.jdbc.processPool
    print 'INFO: Creating the PathFinder process pool database connection %s' % connection.connectionUrl

    command = 'data-source add --name=ProcessPoolDataSource --jndi-name=java:/app/jdbc/ProcessPool --driver-name=%s --connection-url="%s" --user-name=%s --password=%s --pool-prefill=false --use-java-context=true' % (connection.driverName, connection.connectionUrl, connection.userId, connection.password)
    checkSuccess(cli.cmd(command))

    print 'INFO: Testing the PathFinder process pool database connection'
    command = 'data-source test-connection-in-pool --name=ProcessPoolDataSource'
    checkSuccess(cli.cmd(command))
    
    #******************************************************************************
    # Remove default datasource
    #******************************************************************************

    checkSuccess(cli.cmd('data-source remove --name=ExampleDS'))
    command = '/subsystem=ee/service=default-bindings/:undefine-attribute(name=datasource)'
    checkSuccess(cli.cmd(command))

#******************************************************************************
# Initialize the JMS parameters
#******************************************************************************

def configureJMS(cli):
    print 'INFO: Creating the BAM server JMS destination'
    command = '/subsystem=messaging-activemq/server=default/jms-queue=PhysicalBamServerDestination/:add(entries=["java:/app/jms/BamServerDestination"])'
    checkSuccess(cli.cmd(command))

    print 'INFO: Creating the synchronizer JMS destination'
    command = '/subsystem=messaging-activemq/server=default/jms-topic=PhysicalSynchronizerDestination/:add(entries=["java:/global/jms/SynchronizerDestination"])'
    checkSuccess(cli.cmd(command))

#******************************************************************************
# Cluster Configuration 
#******************************************************************************
		
def configureCluster(cli):
    print 'INFO: Configuring cluster'		
    command = '/subsystem=logging/console-handler=CONSOLE:add'
    checkSuccess(cli.cmd(command))
    
    command = '/subsystem=logging/console-handler=CONSOLE:write-attribute(name="level", value="INFO")'
    checkSuccess(cli.cmd(command))  	
    
    command = '/subsystem=logging/console-handler=CONSOLE:write-attribute(name="named-formatter", value="COLOR-PATTERN")'
    checkSuccess(cli.cmd(command))
    
    command = '/subsystem=logging/root-logger=ROOT/:add-handler(name=CONSOLE)'
    checkSuccess(cli.cmd(command))
    
    command = '/subsystem=jgroups/channel=ee/:write-attribute(name=stack,value=tcp)'
    checkSuccess(cli.cmd(command))
    
    command = '/subsystem=jgroups/stack=tcp/protocol=TCPPING/:add'
    checkSuccess(cli.cmd(command))
    
    command = '/subsystem=jgroups/stack=tcp/protocol=TCPPING/property=initial_hosts/:add(value="%s")' % cluster.initialHosts
    checkSuccess(cli.cmd(command))
    
    command = '/subsystem=jgroups/stack=tcp/protocol=TCPPING/property=port_range/:add(value=0)'
    checkSuccess(cli.cmd(command))
    
    command = '/subsystem=messaging-activemq/server=default/:write-attribute(name=cluster-password,value="%s")' % cluster.password
    checkSuccess(cli.cmd(command))
    
    command = '/subsystem=messaging-activemq/server=default/broadcast-group=bg-group1/:write-attribute(name=jgroups-channel,value=ee)'
    checkSuccess(cli.cmd(command))
    
    command = '/subsystem=messaging-activemq/server=default/discovery-group=dg-group1/:write-attribute(name=jgroups-channel,value=ee)'
    checkSuccess(cli.cmd(command))    
    
    command = '/socket-binding-group=standard-sockets/socket-binding=jgroups-mping/:write-attribute(name=interface,value=public)'
    checkSuccess(cli.cmd(command))
    
    command = '/socket-binding-group=standard-sockets/socket-binding=jgroups-tcp/:write-attribute(name=interface,value=public)'
    checkSuccess(cli.cmd(command))

    #******************************************************************************
    # adding outbound socket with webserver(httpd) host ip and port  
    # where mod_cluster will connect and advertise the jboss appserver
    #******************************************************************************
    
    command = '/socket-binding-group=standard-sockets/remote-destination-outbound-socket-binding=modproxy/:add(host=%s,port=%d)' % (cluster.webserverName, cluster.webserverPort)
    checkSuccess(cli.cmd(command))
    
    command = '/subsystem=modcluster/proxy=default:write-attribute(name=proxies,value=["modproxy"])'
    checkSuccess(cli.cmd(command))


#******************************************************************************
# Initial entry point
#******************************************************************************

if (__name__ == '__main__'):
    import sys, hashlib, os, shutil, re, subprocess, java.lang.System
    from org.jboss.as.cli.scriptsupport import CLI
    from utilityFunctions import *
    from serverConfiguration import *
    from startServer import *

    print 'INFO: Starting PathFinder server initialization'

    serverConfigurationScript = configuration.serverConfigurationScript
    print 'INFO: Importing the server configuration script ' + serverConfigurationScript
    exec 'from ' + serverConfigurationScript + ' import *'

    serverInitializeScript = configuration.serverInitializeScript
    print 'INFO: Importing the server initialization script ' + serverInitializeScript
    exec 'from ' + serverInitializeScript + ' import *'

    main()

    print 'INFO: Ending PathFinder server initialization'
else:
    print 'ERROR: Entry point main not found - script aborts'    
