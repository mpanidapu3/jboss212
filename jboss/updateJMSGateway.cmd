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
@rem (C) 2017 DXC Technology Company.
@rem All rights reserved.                                        
@rem ******************************************************************************

setlocal
setlocal enableextensions
setlocal enabledelayedexpansion

@echo Starting JMS Gateway Update: %DATE% %TIME%

@rem ******************************************************************************
@rem Set the environment variables used in this batch file.  This batch file can 
@rem accept one parameter which will be used to identify the Jboss Enterprise 
@rem Application Server domain being used.  If this parameter is not specified then 
@rem a default value is used.  This allows you to deploy multiple domains on one 
@rem Jboss EAP instance without having to modify these files.
@rem ******************************************************************************

call setJBossPFEnv %1
if %ERRORLEVEL% NEQ 0 exit /B

pushd scripts

jython updateConfig.py JMSGATEWAY

popd

@echo Finished JMS Gateway Update: %DATE% %TIME%

endlocal
