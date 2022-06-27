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
# (C) 2021 DXC Technology Company.
# All rights reserved.                                        
#******************************************************************************

def main():
    connected = False
    cli = CLI.newInstance()

    try:
        createServer()
        createAdminUser()
        startServer()

    except:
        print 'ERROR: Pre-initialization failed: ', sys.exc_info()[1]
    finally:
        if connected:
            print 'INFO: Disconnecting...'
            cli.disconnect()

#******************************************************************************
# This method will create the PathFinder server by copying the server 
# template files from the JBoss/standalone directory to a directory in
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

    print 'INFO: Ending PathFinder server pre initialization'
else:
    print 'ERROR: Entry point main not found - script aborts'    
