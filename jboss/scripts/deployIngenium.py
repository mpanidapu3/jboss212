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

from utilityFunctions import *
from serverConfiguration import *
from ingeniumServerConfiguration import *

#******************************************************************************
# This method is called by the deploy script and gives you an opportunity
# to perform any administration server specific functions. For DXC Ingenium, 
# we need to deploy the PathFinderConnector application if it's being used.
#******************************************************************************

def deployAdministrationServerApps(cli):
    if ingenium.usePFC:
        buildPFCEar(ingenium.applications.pfc)
        deploy(cli, ingenium.applications.pfc)

#******************************************************************************
# Build the PathFinder EAR file
#******************************************************************************

def buildPFCEar(application):
    if not application.deploy:
        return

    earFileName = os.path.realpath(application.fileName).replace('\\', '/')
    print 'INFO: Building PathFinderConnector EAR ' + earFileName

    currentDirectory = os.getcwd()
    os.chdir('../..')

    #******************************************************************************
    # Create a temporary directory where we'll store files used to build the EAR.
    # First, delete the directory to ensure we're starting clean, then copy the
    # files from the Deployment/PathFinderEar folder there.
    #******************************************************************************

    tempDir = (tempfile.gettempdir() + '/PathFinderConnectorEar').replace('\\', '/')
    if os.path.exists(tempDir):
        shutil.rmtree(tempDir, False, onerror=handleRemoveReadonly)

    try:
        print 'INFO: Copying temporary files'
        shutil.copytree('PathFinderConnectorEar', tempDir)
    except:
        pass

    deployPlans = 'jboss/deployplans/PathFinderConnectorEar'

    ############################################################################
    # Build the PFC config jar and add it to the EAR's lib folder.
    ############################################################################

    print 'INFO: Creating PathFinderConnectorConfig.jar'
    sourceDir = tempDir + '/PathFinderConnectorConfig'
    updateArchive(tempDir + '/lib/PathFinderConnectorConfig.jar', sourceDir)
    shutil.rmtree(sourceDir, False, onerror=handleRemoveReadonly)

    ############################################################################
    # If using a JMS queue for the listener then add the JBoss specific files
    # and create the PathFinderConnectorEjb.jar file
    ############################################################################

    if ingenium.applications.pfc.listener == 'QUEUE':
        sourceDir = tempDir + '/PathFinderConnectorEjb'
        shutil.copy(deployPlans + '/PathFinderConnectorEjb.jar/META-INF/jboss-ejb3.xml', sourceDir + '/META-INF')
        shutil.copy(deployPlans + '/PathFinderConnectorEjb.jar/jboss-deployment-structure.xml', tempDir + '/META-INF')
        updateArchive(tempDir + '/PathFinderConnectorEjb.jar', sourceDir)
        shutil.rmtree(sourceDir, False, onerror=handleRemoveReadonly)

    ############################################################################
    # Create the WAR file
    ############################################################################

    sourceDir = tempDir + '/PathFinderConnectorWar'
    shutil.copy(deployPlans + '/PathFinderConnectorWar.war/WEB-INF/jboss-web.xml', sourceDir + '/WEB-INF')
    updateArchive(tempDir + '/PathFinderConnectorWar.war', sourceDir)
    shutil.rmtree(sourceDir, False, onerror=handleRemoveReadonly)

    updateArchive(tempDir + '/PathFinderConnector.jar', deployPlans + '/PathFinderConnector.jar', 'a')

    ############################################################################
    # Build the PFC EAR file.
    ############################################################################

    print 'INFO: Creating PathFinderConnector EAR file'
    updateArchive(earFileName, tempDir)
    shutil.rmtree(tempDir, False, onerror=handleRemoveReadonly)

    os.chdir(currentDirectory)

    print 'INFO: Finished building PathFinderEarConnector EAR'
