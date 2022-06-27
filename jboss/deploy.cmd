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
@rem This command file deploys all PathFinder components to the JBoss application 
@rem server. This batch file can accept one parameter which will be used to 
@rem identify the JBoss server being used.  If this parameter is not 
@rem specified then a default value is used.  This allows you to deploy multiple 
@rem servers without having to modify these files.
@rem ******************************************************************************

setlocal
setlocal enableextensions
setlocal enabledelayedexpansion

@rem ******************************************************************************
@rem These variables specify which components to install.  Note that setting
@rem the DEPLOY_PATHFINDERCONNECTOR variable to true does not guarantee that 
@rem PathFinderConnector will be used since installation will depend upon the 
@rem value of the ingenium.usePFC variable in the ingeniumServerConfiguration.py
@rem file. Setting DEPLOY_PATHFINDERCONNECTOR to true simply indicates whether 
@rem installation should be an option.
@rem ******************************************************************************

set DEPLOY_PATHFINDER=true
set DEPLOY_CONSOLESERVER=true
set DEPLOY_BAMSERVER=true
set DEPLOY_WEBSERVICES=true
set DEPLOY_WEBSERVICES_JAXRS=true
set DEPLOY_PATHFINDERCONNECTOR=true
set DEPLOY_BIRTWAR=true

call deployCore %1
if %ERRORLEVEL% NEQ 0 exit /B 1

endlocal
