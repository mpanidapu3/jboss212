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

def main():
    try:
        deleteServer()
    except:
        print 'ERROR: Server deletion failed: ', sys.exc_info()[1]

#******************************************************************************
# Delete the JBoss server by removing the server folder and the modules
# folder.
#******************************************************************************

def deleteServer():
    jBossHome = getEnvironmentVariable('JBOSS_HOME').replace('"', '').replace('\\', '/')

    #******************************************************************************
    # If the server folder doesn't exist then there's nothing to do.
    #******************************************************************************

    if not os.path.isdir(pathFinderServerFolder):
        print 'INFO: The \'%s\' server does not exist' % pathFinderServerName
        return

    #******************************************************************************
    # The folder exists, so confirm that the user wants to delete it.
    #******************************************************************************

    delete = raw_input('Press Y and enter to delete the \'%s\' server: ' % pathFinderServerName).upper()
    if delete == 'Y':
        #******************************************************************************
        # There are two folders to delete. The server folder and the modules folder
        # where components like the JDBC drivers are located.
        #******************************************************************************

        moduleFolder = jBossHome + '/modules/%s' % pathFinderServerName

        print 'INFO: Deleting the \'%s\' server' % pathFinderServerName
        shutil.rmtree(pathFinderServerFolder, True)
        shutil.rmtree(moduleFolder, True)

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
    else:
        print 'INFO: Server deletion cancelled'

#******************************************************************************
# Initial entry point
#******************************************************************************

if (__name__ == '__main__'):
    import sys, os, shutil
    from utilityFunctions import *
    from serverConfiguration import *

    main()
else:
    print 'ERROR: Entry point main not found - script aborts'    
