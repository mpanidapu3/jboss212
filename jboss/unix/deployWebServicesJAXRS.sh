#!/usr/bin/ksh
# ******************************************************************************
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
# ******************************************************************************

# ******************************************************************************
# This command file deploys the web services EAR to the WebSphere
# application server on the domain running on ADMINPORT.
# This batch file can accept one parameter which will be used to identify the 
# PathFinder application server being used.  If this parameter is not 
# specified then a default value is used.  This allows you to deploy multiple 
# servers on one WAS instance without having to modify these files.
# ******************************************************************************

# ******************************************************************************
# These variables specify which components to install.  Note that setting
# the DEPLOY_PATHFINDERCONNECTOR variable to true does not guarantee that 
# PathFinderConnector will be used since installation will depend upon other
# variables defined in setWasPfEnv.cmd.  Setting DEPLOY_PATHFINDERCONNECTOR to
# true simply indicates whether installation should be an option.
# ******************************************************************************

export DEPLOY_PATHFINDER=false
export DEPLOY_CONSOLESERVER=false
export DEPLOY_BAMSERVER=false
export DEPLOY_WEBSERVICES=false
export DEPLOY_WEBSERVICES_JAXRS=true
export DEPLOY_PATHFINDERCONNECTOR=false
export DEPLOY_BIRTWAR=false

./deployCore.sh $1

