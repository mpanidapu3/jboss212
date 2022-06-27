@echo off

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
@rem (C) 2014-2020 DXC Technology Company.
@rem All rights reserved.                                        
@rem ******************************************************************************

@rem ******************************************************************************
@rem This command file deploys the web service EAR to the JBoss application 
@rem server. This batch file can accept one parameter which will be used to 
@rem identify the JBoss server being used.  If this parameter is not 
@rem specified then a default value is used.  This allows you to deploy multiple 
@rem servers without having to modify these files.
@rem ******************************************************************************

setlocal
setlocal enableextensions
setlocal enabledelayedexpansion

@rem ******************************************************************************
@rem These variables specify which components to install. You must have created
@rem the web services EAR file using the utilities in WebServicesBuilder and
@rem copied the EAR file to the deployment folder before running this command.
@rem ******************************************************************************

set DEPLOY_PATHFINDER=false
set DEPLOY_CONSOLESERVER=false
set DEPLOY_BAMSERVER=false
set DEPLOY_WEBSERVICES=true
set DEPLOY_WEBSERVICES_JAXRS=false
set DEPLOY_PATHFINDERCONNECTOR=false
set DEPLOY_BIRTWAR=false

call deployCore %1
if %ERRORLEVEL% NEQ 0 exit /B 1

endlocal
