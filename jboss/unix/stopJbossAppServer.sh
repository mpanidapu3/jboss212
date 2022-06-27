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

. ./setJBossPFEnv.sh

echo Shutting down AppServer: $DATE $TIME

cd ../scripts

jython stopJbossAppServer.py

cd ../unix
