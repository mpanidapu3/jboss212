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
    cli = CLI.newInstance()

    try:
        connectToServer(cli, configuration)

        print 'INFO: Stopping the \'%s\' server' % pathFinderServerName

        cli.cmd('shutdown')
    except:
        print 'ERROR: Initialization failed: ', sys.exc_info()[1]

#******************************************************************************
# Initial entry point
#******************************************************************************

if (__name__ == '__main__'):
    import sys
    from org.jboss.as.cli.scriptsupport import CLI
    from utilityFunctions import *
    from serverConfiguration import *

    main()
else:
    print 'ERROR: Entry point main not found - script aborts'    
