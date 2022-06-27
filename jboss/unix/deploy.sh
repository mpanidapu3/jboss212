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
# Set the environment variables used in this batch file.
# ******************************************************************************

# ******************************************************************************
# These variables specify which components to install.  Note that setting
# the DEPLOY_PATHFINDERCONNECTOR variable to true does not guarantee that 
# PathFinderConnector will be used since installation will depend upon other
# variables defined in setWasPfEnv.cmd.  Setting DEPLOY_PATHFINDERCONNECTOR to
# true simply indicates whether installation should be an option.
# ******************************************************************************

export DEPLOY_PATHFINDER=true
export DEPLOY_CONSOLESERVER=true
export DEPLOY_BAMSERVER=true
export DEPLOY_WEBSERVICES=true
export DEPLOY_WEBSERVICES_JAXRS=true
export DEPLOY_PATHFINDERCONNECTOR=true
export DEPLOY_BIRTWAR=true

./deployCore.sh $1
