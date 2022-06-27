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

        deployBamServer(cli)
        deployBIRT(cli)
        deployPathFinder(cli)
        deployConsoleServer(cli)
        deployWebServices(cli)
        deployWebServicesJaxrs(cli)		

        #******************************************************************************
        # Deploy any administration server specific applications
        #******************************************************************************

        deployAdministrationServerApps(cli)

        displayPorts(cli)

        #******************************************************************************
        # Reload the server configuration to ensure that all components are started
        # properly after redeploying.
        #******************************************************************************

        print 'INFO: Reloading the server configuration'
        cli.cmd(':reload')
    except:
        print 'ERROR: Deployment failed: ', sys.exc_info()[1]
    finally:
        if connected:
            print 'INFO: Disconnecting...'
            cli.disconnect()

#******************************************************************************
# Deploy the PathFinder application. 
#******************************************************************************

def deployPathFinder(cli):
    buildPathFinderEar(pathFinder.applications.pathFinder)
    deploy(cli, pathFinder.applications.pathFinder)

#******************************************************************************
# Build the PathFinder EAR file
#******************************************************************************

def buildPathFinderEar(application):
    if not application.deploy:
        return

    earFileName = os.path.realpath(application.fileName).replace('\\', '/')
    print 'INFO: Building PathFinder EAR ' + earFileName

    currentDirectory = os.getcwd()
    os.chdir('../..')

    #******************************************************************************
    # Create a temporary directory where we'll store files used to build the EAR.
    # First, delete the directory to ensure we're starting clean, then copy the
    # files from the Deployment/PathFinderEar folder there.
    #******************************************************************************

    tempDir = (tempfile.gettempdir() + '/PathFinderEar').replace('\\', '/')
    if os.path.exists(tempDir):
        shutil.rmtree(tempDir, False, onerror=handleRemoveReadonly)

    try:
        print 'INFO: Copying temporary files'
        shutil.copytree('PathFinderEar', tempDir)
    except:
        pass

    os.mkdir(tempDir + '/META-INF')
    deployPlans = 'jboss/deployplans/PathFinderEar'

    ############################################################################
    # Build the PathFinder config jar and add it to the EAR's lib folder.
    ############################################################################

    print 'INFO: Creating PathFinderConfig.jar'
    sourceDir = tempDir + '/PathFinderConfig'
    updateArchive(tempDir + '/lib/PathFinderConfig.jar', sourceDir)
    shutil.rmtree(sourceDir, False, onerror=handleRemoveReadonly)

    ############################################################################
    # Add the jboss-ejb3.xml files to the CodeServer and PathFinder EJB jars.
    ############################################################################

    updateArchive(tempDir + '/CodeServerEjb.jar', deployPlans + '/CodeServerEjb.jar', 'a')
    updateArchive(tempDir + '/PathFinderEjb.jar', deployPlans + '/PathFinderEjb.jar', 'a')

    ############################################################################
    # Add the jboss-web.xml and jboss-ejb3.xml to either the PageBuilder or 
    # PageServer components. Then move the jar containing the servlet code to 
    # the EAR's lib folder.
    ############################################################################

    servletName = 'PageBuilder' if configuration.pageSource == 'JSP' else 'PageServer'

    shutil.copy(deployPlans + '/%s.war/WEB-INF/jboss-web.xml' % servletName, tempDir + '/%s/WEB-INF' % servletName)
    shutil.copy(deployPlans + '/%sEjb.jar/META-INF/jboss-ejb3.xml' % servletName, tempDir + '/%sEjb/META-INF' % servletName)
    shutil.move(tempDir + '/%s/WEB-INF/lib/%s.jar' % (servletName, servletName), tempDir + '/lib')

    ############################################################################
    # Build either the PageServerEjb or PageBuilderEjb jar file
    ############################################################################

    print 'INFO: Creating %sEjb JAR file' % servletName
    updateArchive(tempDir + '/%sEjb.jar' % servletName, tempDir + '/%sEjb' % servletName)
    
    tempDirPageBuilderEjb = (tempDir + '/PageBuilderEjb').replace('\\', '/')
    if os.path.exists(tempDirPageBuilderEjb):
        shutil.rmtree(tempDirPageBuilderEjb, False, onerror=handleRemoveReadonly)
        
    tempDirPageServerEjb = (tempDir + '/PageServerEjb').replace('\\', '/')
    if os.path.exists(tempDirPageServerEjb):
        shutil.rmtree(tempDirPageServerEjb, False, onerror=handleRemoveReadonly)    

    ############################################################################
    # Build either the PageServer or PageBuilder war file
    ############################################################################

    print 'INFO: Building the %s WAR file' % servletName

    updateArchive(tempDir + '/%s.war' % servletName, tempDir + '/%s' % servletName)

    ############################################################################
    # The application.warContent variable can be the name of a directory
    # containing files that are going to be added to the WAR file. If set
    # to None, then skip this part otherwise verify that the directory
    # specified is valid and add the contents to the WAR.
    ############################################################################

    if not application.warContent == None:
        if not os.path.isdir(application.warContent):
            print 'ERROR: The pathFinder.applications.pathFinder.warContent element in serverConfiguration.py does not refer to a valid directory.'
            sys.exit(1)

        print 'INFO: Adding contents of the %s folder to the %s WAR file' % (application.warContent, servletName)
        updateArchive(tempDir + '/%s.war' % servletName, application.warContent, 'a')

    # remove temporary war file
    try: 
        shutil.rmtree(tempDir + '/PageBuilder', False, onerror=handleRemoveReadonly)        
    except:
        pass

    # remove temporary war file
    try: 
        shutil.rmtree(tempDir + '/PageServer', False, onerror=handleRemoveReadonly)        
    except:
        pass

    tempDirPageBuilder = (tempDir + '/PageBuilderEjb').replace('\\', '/')
    if os.path.exists(tempDirPageBuilder):
        shutil.rmtree(tempDir + '/PageBuilder', False, onerror=handleRemoveReadonly)
        
    tempDirPageServer = (tempDir + '/PageServerEjb').replace('\\', '/')
    if os.path.exists(tempDirPageServer):
        shutil.rmtree(tempDir + '/PageServer', False, onerror=handleRemoveReadonly)

    ############################################################################
    # Add the INGENIUM specific components
    ############################################################################

    if configuration.adminServer == 'INGENIUM':
        ############################################################################
        # Add the jboss-ejb3.xml files to the INGENIUM jar file. The IBMCICS
        # and JMS jars require the jboss-deployment-structure.xml file to be 
        # added to the META-INF folder of the EAR file.
        ############################################################################

        updateArchive(tempDir + '/Ingenium.jar', deployPlans + '/Ingenium.jar', 'a')

        silentRemove(tempDir + '/IBMCicsGateway.jar')
        silentRemove(tempDir + '/JmsGateway.jar')
        silentRemove(tempDir + '/AS400Gateway.jar')
        silentRemove(tempDir + '/MQGateway.jar')
        silentRemove(tempDir + '/ActiveMQGateway.jar')

        if ingenium.gateway == 'IBMCICS':
            jarName = 'IBMCicsGateway.jar'
            shutil.move(tempDir + '/Gateways/%s' % jarName, tempDir)
            updateArchive(tempDir + '/%s' % jarName, deployPlans + '/%s' % jarName, 'a', ['jboss-deployment-structure.xml'])
            shutil.copy(deployPlans + '/%s/jboss-deployment-structure.xml' % jarName, tempDir + '/META-INF')
        elif ingenium.gateway == 'JMS':
            jarName = 'JmsGateway.jar'
            shutil.move(tempDir + '/Gateways/%s' % jarName, tempDir)
            updateArchive(tempDir + '/%s' % jarName, deployPlans + '/%s' % jarName, 'a', ['jboss-deployment-structure.xml'])
            shutil.copy(deployPlans + '/%s/jboss-deployment-structure.xml' % jarName, tempDir + '/META-INF')
        elif ingenium.gateway == 'AS400':
            jarName = 'AS400Gateway.jar'
            shutil.move(tempDir + '/Gateways/%s' % jarName, tempDir)
        elif ingenium.gateway == 'MQ':
            jarName = 'MQGateway.jar'
            shutil.move(tempDir + '/Gateways/%s' % jarName, tempDir)
        elif ingenium.gateway == 'ACTIVEMQ':
            jarName = 'ActiveMQGateway.jar'
            shutil.move(tempDir + '/Gateways/%s' % jarName, tempDir)
            updateArchive(tempDir + '/%s' % jarName, deployPlans + '/%s' % jarName, 'a', ['jboss-deployment-structure.xml'])
            shutil.copy(deployPlans + '/%s/jboss-deployment-structure.xml' % jarName, tempDir + '/META-INF')
        else:
            print 'ERROR: Unrecognized ingenium.gateway value: ' + ingenium.gateway
            sys.exit(1)
    else:
        ############################################################################
        # Radience doesn't need the INGENIUM specific files
        ############################################################################

        os.remove(tempDir + '/Ingenium.jar')

    shutil.rmtree(tempDir + '/Gateways', False, onerror=handleRemoveReadonly)

    ############################################################################
    # Build the PathFinder EAR file.
    ############################################################################

    print 'INFO: Creating PathFinder EAR file'
    updateArchive(earFileName, tempDir)
    shutil.rmtree(tempDir, False, onerror=handleRemoveReadonly)

    os.chdir(currentDirectory)

    print 'INFO: Finished building PathFinderEar EAR'

#******************************************************************************
# Deploy the PathFinder application. 
#******************************************************************************

def deployConsoleServer(cli):
    buildConsoleServerEar(pathFinder.applications.consoleServer)
    deploy(cli, pathFinder.applications.consoleServer)

#******************************************************************************
# Build the ConsoleServer EAR file
#******************************************************************************

def buildConsoleServerEar(application):
    if not application.deploy:
        return

    earFileName = os.path.realpath(application.fileName).replace('\\', '/')
    print 'INFO: Building ConsoleServer EAR ' + earFileName

    currentDirectory = os.getcwd()
    os.chdir('../..')

    #******************************************************************************
    # Create a temporary directory where we'll store files used to build the EAR.
    # First, delete the directory to ensure we're starting clean, then copy the
    # files from the Deployment/ConsoleServerEar folder there.
    #******************************************************************************

    tempDir = (tempfile.gettempdir() + '/ConsoleServerEar').replace('\\', '/')
    if os.path.exists(tempDir):
        shutil.rmtree(tempDir, False, onerror=handleRemoveReadonly)

    try:
        print 'INFO: Copying temporary files'
        shutil.copytree('ConsoleServerEar', tempDir)
    except:
        pass

    #******************************************************************************
    # Set the servletName variable that will be used to build paths to the proper
    # files to use.
    #******************************************************************************

    servletName = 'PageBuilder'
    if configuration.pageSource == 'HTML':
        servletName = 'PageServer'

    deployPlans = 'jboss/deployplans/ConsoleServerEar'

    #******************************************************************************
    # Add the JBoss specific files to the EJB jar
    #******************************************************************************

    updateArchive(tempDir + '/ConsoleServerEjb.jar', deployPlans + '/ConsoleServerEjb.jar/%s' % servletName, 'a')

    #******************************************************************************
    # Copy the JBoss specific files for the WAR to the temporary folder.
    #******************************************************************************

    shutil.copy(deployPlans + '/ConsoleServer.war/%s/WEB-INF/jboss-web.xml' % servletName, tempDir + '/ConsoleServer/WEB-INF')
    shutil.copy(deployPlans + '/jboss-deployment-structure.xml', tempDir + '/META-INF')
    
    #******************************************************************************
    # Create the WAR file
    #******************************************************************************

    sourceDir = tempDir + '/ConsoleServer'
    updateArchive(tempDir + '/ConsoleServer.war', sourceDir)
    shutil.rmtree(sourceDir, False, onerror=handleRemoveReadonly)

    #******************************************************************************
    # Create the EAR file
    #******************************************************************************

    updateArchive(earFileName, tempDir)
    shutil.rmtree(tempDir, False, onerror=handleRemoveReadonly)

    os.chdir(currentDirectory)

    print 'INFO: Finished building ConsoleServerEar'

#******************************************************************************
# Deploy the BamServer application. 
#******************************************************************************

def deployBamServer(cli):
    buildBamServerEar(pathFinder.applications.bamServer)
    deploy(cli, pathFinder.applications.bamServer)

#******************************************************************************
# Deploy the BIRT application. 
#******************************************************************************

def deployBIRT(cli):
    application = pathFinder.applications.birt
    if not application.deploy:
        return
		
    if not os.path.exists(pathFinder.applications.birt.fileName):
        return

    print 'INFO: Configuring Birt war'

    currentDirectory = os.getcwd()
    os.chdir('../..')

    #******************************************************************************
    # Update the BIRT WAR with JBoss specific files. We don't know the exact
    # name of the BIRT war so we use the glob() function to match any WAR matching
    # the pattern 'birt*.war'
    #******************************************************************************

    for fileName in glob.glob(os.path.join(os.getcwd(), 'birt*.war')):
        with UpdateableZipFile(fileName, 'a') as war:
            war.write('jboss/deployplans/birt.war/WEB-INF/jboss-web.xml', 'WEB-INF/jboss-web.xml')

    os.chdir(currentDirectory)			
    print 'INFO: Finished Configuring Birt war'
	
    deploy(cli, pathFinder.applications.birt)

#******************************************************************************
# Build the BamServer EAR file
#******************************************************************************

def buildBamServerEar(application):
    if not application.deploy:
        return

    earFileName = os.path.realpath(application.fileName).replace('\\', '/')
    print 'INFO: Building BamServer EAR ' + earFileName

    currentDirectory = os.getcwd()
    os.chdir('../..')

    #******************************************************************************
    # Create a temporary directory where we'll store files used to build the EAR.
    # First, delete the directory to ensure we're starting clean, then copy the
    # files from the Deployment/BamServerEar folder there.
    #******************************************************************************

    tempDir = (tempfile.gettempdir() + '/BamServerEar').replace('\\', '/')
    if os.path.exists(tempDir):
        shutil.rmtree(tempDir, False, onerror=handleRemoveReadonly)
    try:
        print 'INFO: Copying temporary files'
        #os.mkdir(tempDir, 0o777)	
        shutil.copytree('BamServerEar', tempDir)
    except:
        pass

    deployPlans = 'jboss/deployplans/BamServerEar'

    #******************************************************************************
    # Add the JBoss specific files to the EJB jar
    #******************************************************************************

    updateArchive(tempDir + '/BamServerEjb.jar', deployPlans + '/BamServerEjb.jar', 'a')

    #******************************************************************************
    # Copy the JBoss specific files for the WAR to the temporary folder.
    #******************************************************************************

    shutil.copy(deployPlans + '/BamServerWar.war/WEB-INF/jboss-web.xml', tempDir + '/BamServerWar/WEB-INF')

    #******************************************************************************
    # Create the BamServerConfig.jar and put it into the EAR lib folder
    #******************************************************************************

    sourceDir = tempDir + '/BamServerConfig'
    updateArchive(tempDir + '/lib/BamServerConfig.jar', sourceDir)
    shutil.rmtree(sourceDir, False, onerror=handleRemoveReadonly)

    #******************************************************************************
    # Create the WAR file
    #******************************************************************************

    sourceDir = tempDir + '/BamServerWar'
    updateArchive(tempDir + '/BamServerWar.war', sourceDir)
    shutil.rmtree(sourceDir, False, onerror=handleRemoveReadonly)

    #******************************************************************************
    # Create the EAR file
    #******************************************************************************

    updateArchive(earFileName, tempDir)
    os.chdir(currentDirectory)

    print 'INFO: Finished building BamServerEar'
	
#******************************************************************************
# Deploy the web services. The addWebServiceDeployOptions(options)
# method in your administration server specific deployment script will be 
# called giving you an opportunity to add any deployment options that are
# unique to your administration server.
#******************************************************************************

def deployWebServices(cli):
    if not os.path.exists(pathFinder.applications.webServices.fileName):
        return

    deploy(cli, pathFinder.applications.webServices)


#******************************************************************************
# Deploy the web services. The addWebServiceDeployOptions(options)
# method in your administration server specific deployment script will be 
# called giving you an opportunity to add any deployment options that are
# unique to your administration server.
#******************************************************************************

def deployWebServicesJaxrs(cli):
    if not os.path.exists(pathFinder.applications.webServicesJaxrs.fileName):
        return

    deploy(cli, pathFinder.applications.webServicesJaxrs)
	
#******************************************************************************
# Removing All the temporory files created while deploying
#******************************************************************************

def clearTempFiles(cli):
    tempDir = (tempfile.gettempdir() + '/BamServerEar').replace('\\', '/')
    if os.path.exists(tempDir):
        shutil.rmtree(tempDir, False, onerror=handleRemoveReadonly)

    tempDir = (tempfile.gettempdir() + '/ConsoleServerEar').replace('\\', '/')
    if os.path.exists(tempDir):
        shutil.rmtree(tempDir, False, onerror=handleRemoveReadonly)

    tempDir = (tempfile.gettempdir() + '/PathFinderEar').replace('\\', '/')
    if os.path.exists(tempDir):
        shutil.rmtree(tempDir, False, onerror=handleRemoveReadonly)		
#******************************************************************************
# Main entry point
#******************************************************************************

if (__name__ == '__main__'):
    import os, sys, shutil, glob, time
    from org.jboss.as.cli.scriptsupport import CLI
    from utilityFunctions import *
    from serverConfiguration import *

    print 'INFO: Starting PathFinder deployment'

    serverConfigurationScript = configuration.serverConfigurationScript
    print 'INFO: Importing the server configuration script ' + serverConfigurationScript
    exec 'from ' + serverConfigurationScript + ' import *'

    serverDeployScript = configuration.serverDeployScript
    print 'INFO: Importing the server deployment script ' + serverDeployScript
    exec 'from ' + serverDeployScript + ' import *'

    main()

    print 'INFO: Ended PathFinder deployment'
else:
    print 'ERROR: Entry main not found - script aborts'

