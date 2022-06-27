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
# This command file should not be run directly since it requires that the
# DEPLOY_* environment variables be set.
# ******************************************************************************

if [[ $DEPLOY_PATHFINDER  == "" ]];  then
	echo This command file cannot be run directly. 
	exit 1
fi

# ******************************************************************************
# Set the environment variables used in this batch file.
# ******************************************************************************

echo Starting deployment: $DATE $TIME
. ./setJBossPFEnv.sh


cd ../scripts

jython deploy.py 

cd ../unix

echo Finished deployment: $DATE $TIME
