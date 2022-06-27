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
# Environment Setup for the PathFinder Installation Scripts
# ******************************************************************************
export JAVA_HOME=/opt/PF/jdk8u282-b08/
export JBOSS_HOME=/opt/PF/jboss73/
export JYTHON_HOME=/opt/PF/jython272/
export PATH="$PATH:/opt/PF/java/bin"
export PATH="$PATH:/opt/PF/jboss73/bin/client/jboss-cli-client.jar"
export CLASSPATH="$CLASSPATH:$PATH"


#[ ! -d "$JAVA_HOME" ] && echo "JAVA_HOME does not exist."
#[ ! -d "$JBOSS_HOME" ] && echo "JBOSS_HOME does not exist."
#[ ! -d "$JYTHON_HOME" ] && echo "JYTHON_HOME does not exist."


