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

import sys, os, re, subprocess, java.lang.System
from utilityFunctions import *
from serverConfiguration import *

#******************************************************************************
# This function will start the JBoss application server
#******************************************************************************

def startServer():
    #******************************************************************************
    # The environment variable JAVA_OPTS will be set to the value of the 
    # javaOptions array.
    #******************************************************************************

    javaOptions = [
        ' -Djboss.socket.binding.port-offset=%d' % configuration.portOffset,
        ' -Djboss.server.base.dir=%s' % pathFinderServerFolder,
        ' -Djboss.server.config.user.dir=%s/configuration' % pathFinderServerFolder,
        ' -Djboss.domain.config.user.dir=%s/configuration' % pathFinderServerFolder,
        ' -Djava.net.preferIPv4Stack=true'
        ]

    #******************************************************************************
    # serverOptions contains parameters passed to the JBoss server at startup.
    #******************************************************************************

    serverOptions = [
        '' if not configuration.debug else ' --debug %d' % (8787 + configuration.portOffset),
        ' -c standalone-full.xml' if not cluster.useCluster else ' -c standalone-full-ha.xml',
        ' -Djboss.bind.address.management=%s' % configuration.serverName,
        ' -Djboss.node.name=%s:%s' % (configuration.serverName, pathFinderServerName),
        ' -b=%s' % configuration.serverName
        ]
    
    #******************************************************************************
    # Determine which operating system we're running on. If Windows, then we
    # need to run the standalone.bat file using 'start' to ensure that it
    # opens in its own console window.
    # 
    # The NOPAUSE environment variable prevents the JBoss batch files from 
    # displaying the "Press any key to continue" message when they end.
    #******************************************************************************

    if re.search('windows', java.lang.System.getProperty('os.name').lower()):
        command = 'cmd.exe /C start'
        fileExt = '.bat'	
    else:
        command = ''
        fileExt = '.sh'			

    os.putenv('NOPAUSE', 'True')
    os.putenv('JAVA_OPTS', ''.join(javaOptions))

    workingDir = getEnvironmentVariable('JBOSS_HOME').replace('"', '') + '/bin'
    cmd = workingDir + '/standalone' +  fileExt

    process = subprocess.Popen('%s %s %s' % (command, cmd, ''.join(serverOptions)), shell=True, cwd=workingDir)
    process.communicate()
