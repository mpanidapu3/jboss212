@rem ******************************************************************************
@rem All right, title and interest in and to the software        
@rem (the "Software") and the accompanying documentation or      
@rem materials (the "Documentation"), including all proprietary  
@rem rights, therein including all patent rights, trade secrets, 
@rem trademarks and copyrights, shall remain the exclusive       
@rem property of DXC Technology Company.
@rem No interest, license or any right respecting the Software      
@rem and the Documentation, other than expressly granted in      
@rem the Software License Agreement, is granted by implication   
@rem or otherwise.                                               
@rem                                                            
@rem (C) 2014-2022 DXC Technology Company.
@rem All rights reserved.                                        
@rem ******************************************************************************

@rem ******************************************************************************
@rem This batch file expects one parameter which should be a unique ID that is used
@rem to identify the PathFinder region being used.  The PFINSTANCEID environment 
@rem variable will be set to the value of this parameter if it doesn't already
@rem exist in the user's environment. The PFINSTANCEID is used to determine
@rem the port offset for the JBoss server. This allows multiple JBoss servers
@rem to run on the same server without conflict.
@rem ******************************************************************************

if not defined PFINSTANCEID set PFINSTANCEID=%1

@rem ******************************************************************************
@rem Do not use names with spaces in them. Use the short name equivalent.
@rem ******************************************************************************

set JAVA_HOME=C:\PROGRA~1\AdoptOpenJDK\jdk-8.0.212.04-hotspot
set JBOSS_HOME=C:\JBOSSEAP-7.3.0
set JYTHON_HOME=C:\jython2.7.2

if not exist %JAVA_HOME% (
	echo The JAVA_HOME variable refers to a directory that doesn't exist: %JAVA_HOME%
	exit /B 1
)

if not exist %JBOSS_HOME% (
	echo The JBOSS_HOME variable refers to a directory that doesn't exist: %JBOSS_HOME%
	exit /B 1
)

if not exist %JYTHON_HOME% (
	echo The JYTHON_HOME variable refers to a directory that doesn't exist: %JYTHON_HOME%
	exit /B 1
)

@rem ******************************************************************************
@rem Add the CLI client jar to the classpath for use by the Jython scripts
@rem Add the Jython bin folder to the path to be able to run the Jython command.
@rem ******************************************************************************

set CLASSPATH=%CLASSPATH%;%JBOSS_HOME%\bin\client\jboss-cli-client.jar
set PATH=%PATH%;%JYTHON_HOME%\bin
