#******************************************************************************
# All right, title and interest in and to the software
# (the 'Software') and the accompanying documentation or
# materials (the 'Documentation'), including all proprietary
# rights, therein including all patent rights, trade secrets,
# trademarks and copyrights, shall remain the exclusive
# property of DXC Technology Company.
# No interest, license or any right respecting the Software
# and the Documentation, other than expressly granted in
# the Software License Agreement, is granted by implication
# or otherwise.
#
# (C) 2014-2021 DXC Technology Company.
# All rights reserved.
#******************************************************************************

import errno, stat, os, time, tempfile, shutil, signal, sys
from zipfile import ZipFile, ZIP_STORED, ZipInfo
from org.jboss.as.cli.scriptsupport import CLI

#******************************************************************************
# Get the value of an environment variable.
#******************************************************************************

def getEnvironmentVariable(variableName):
    try:
        return os.environ[variableName]
    except:
        return ''

#******************************************************************************
# Check that an operation was successful. An exception will be thrown if
# not.
#******************************************************************************

def checkSuccess(result):
    if not result.isSuccess():
        message = 'ERROR: The operation failed: ' + result.getCliCommand()
        print message
        raise Exception(message)

#******************************************************************************
# Establish a connection to the JBoss EAP server. 
#******************************************************************************

def connectToServer(cli, configuration):
    print 'INFO: Connecting to server'

    attempts = 10

    #******************************************************************************
    # Check for the initial connection to the server. Once we get a connection then
    # we need to ensure that the server is in the 'running' state.
    #******************************************************************************

    for count in range(attempts):
        try:
            cli.connect(configuration.serverName, 9990 + configuration.portOffset, configuration.adminUserId, configuration.adminUserPassword)
        except:
            print 'WARN: Unable to connect to the JBoss server. Trying again after a 5 second delay.  %d of %d' % (count + 1, attempts)
            time.sleep(5);
        else:
            print 'INFO: Connected'
            break;
    else:
        #******************************************************************************
        # If no connection after repeated tries then exit 
        #******************************************************************************

        raise Exception('ERROR: Unable to connect to the JBoss server. Has it been started? Please run preInitialize command')

    #******************************************************************************
    # Now ensure that the state is 'running' 
    #******************************************************************************

    for count in range(attempts):
        response = cli.cmd(':read-attribute(name=server-state)').getResponse()

        result = response.get('result').asString()

        if result == 'running':
            break
        elif 'reload' in result:
            print 'INFO: Reloading server configuration'
            cli.cmd(':reload')

        print 'INFO: Waiting for server to get to running state... %d of %d' % (count + 1, attempts)
        time.sleep(5);
    else:
        raise Exception('ERROR: Unable to determine if the JBoss server is running')

    return True

#******************************************************************************
# The PathFinder server name will have the value of the PFINSTANCEID
# environment variable appended to it if it exists. If PFINSTANCEID hasn't
# been defined, then the baseName passed in is returned.
#******************************************************************************

def getPathFinderServerName(baseName):
    instanceId = getEnvironmentVariable('PFINSTANCEID')
    return baseName if instanceId == '' else baseName + instanceId

#******************************************************************************
# The PathFinder server folder is the directory where the PathFinder server's
# configuration files are located.
#******************************************************************************

def getPathFinderServerFolder(pathFinderServerName):
    jBossHome = getEnvironmentVariable('JBOSS_HOME').replace('"', '').replace('\\', '/')
    if not os.path.isdir(jBossHome):
        print 'ERROR: The JBOSS_HOME environment variable is not set to a valid directory: %s' % jBossHome
        sys.exit(1)

    return jBossHome + '/PathFinderServers/' + pathFinderServerName

#******************************************************************************
# The port offset is used to allow mutiple instances of JBoss to run on one
# server without conflicts. See the comments in serverConfiguration.py for
# more details.
#******************************************************************************

def getPortOffset(portOffsets):
    instanceId = getEnvironmentVariable('PFINSTANCEID')
    if instanceId == '':
        instanceId = 'default'

    if instanceId not in portOffsets:
        print 'ERROR: A port offset has not been defined for the PFINSTANCEID value of %s. Please update the serverConfiguration.py file' % instanceId
        sys.exit(1)

    return portOffsets[instanceId]
    
#******************************************************************************
# Deploy an application. It will be undeployed if it is already deployed.
#******************************************************************************

def deploy(cli, config):
    #******************************************************************************
    # Make sure we're supposed to deploy the application.
    #******************************************************************************

    if not config.deploy:
        return

    name = config.name

    #******************************************************************************
    # Check to see if it's already deployed. If so, re-deploy it
    #******************************************************************************

    command = '/deployment=%s:read-attribute(name=status)' % name
    result = cli.cmd(command)

    runtimeName = os.path.split(config.fileName)[1]
    if result.success:
        print 'INFO: Re-deploying ' + name
        command = 'deploy %s --name=%s --runtime-name=%s --force' % (config.fileName, name, runtimeName)
        result = cli.cmd(command)
    else:
        print 'INFO: Deploying ' + name
        command = 'deploy %s --name=%s --runtime-name=%s' % (config.fileName, name, runtimeName)
        result = cli.cmd(command)
		
    if result.success:
        print 'INFO: Successfully deployed ' + name
    else:
        print 'ERROR: Deployment of %s failed' % name
        sys.exit(1)

#******************************************************************************
# Add the contents of a folder to a ZIP archive file.
# 
# archive   - The name of the ZIP file to create or update
# sourceDir - The folder whose contents will be added to the archive
# mode      - 'a' to add to an existing archive or 'w' to create a new archive
# excludeFiles - An array of file names that will not be added to the archive
#
# Note that any directories with the letters 'CVS' in their name will not
# be added.
#******************************************************************************

def updateArchive(archive, sourceDir, mode = 'w', excludeFiles = None):
    with UpdateableZipFile(archive, mode) as archive:
        for root, dirs, files in os.walk(sourceDir):
            for fileName in files:
                if excludeFiles != None:
                    if fileName in excludeFiles:
                        continue

                absolutePath = os.path.join(root, fileName).replace('\\', '/')
                relativePath = absolutePath.replace(sourceDir + '/', '')
                if not 'CVS' in relativePath:
                    archive.write(absolutePath, relativePath)

#******************************************************************************
# This function is used with shutil.rmtree to handle the deletion of
# directories containing read-only files. rmtree fails on Windows if there
# are read-only files in the directory.
#******************************************************************************

def handleRemoveReadonly(func, path, exc):
  if func in (os.rmdir, os.remove):
      if os.path.isfile(path):
          os.chmod(path, stat.S_IRWXU| stat.S_IRWXG| stat.S_IRWXO) # 0777
          func(path)
      else:
          os.rmdir(path)
  else:
      raise

#******************************************************************************
# Delete a file and do not fail if the file doesn't exist.
#******************************************************************************

def silentRemove(filename):
    try:
        os.remove(filename)
    except OSError as e:
        if e.errno != errno.ENOENT: # errno.ENOENT = no such file or directory
            raise # re-raise exception if a different error occurred

#******************************************************************************
# Display the ports that are being used
#******************************************************************************

def displayPorts(cli):
    command = '/socket-binding-group=standard-sockets/socket-binding=http:read-attribute(name=bound-port)'
    response = cli.cmd(command).getResponse()
    print 'INFO: HTTP port =', response.get("result")

    command = '/socket-binding-group=standard-sockets/socket-binding=management-http:read-attribute(name=bound-port)'
    response = cli.cmd(command).getResponse()
    print 'INFO: HTTP admin port =', response.get("result")

#******************************************************************************
# The base ZipFile utility in Jython doesn't allow you to update a file in
# an existing ZIP file. This class extends ZipFile and provides that
# capability.
#******************************************************************************

class UpdateableZipFile(ZipFile):
    class DeleteMarker(object):
        pass

    def __init__(self, file, mode = 'r', compression = ZIP_STORED, allowZip64 = False):
        #******************************************************************************
        # Init base
        #******************************************************************************
        super(UpdateableZipFile, self).__init__(file, mode = mode, compression = compression, allowZip64 = allowZip64)
        #******************************************************************************
        # track file to override in zip
        #******************************************************************************
        self._replace = {}
        #******************************************************************************
        # Whether the with statement was called
        #******************************************************************************
        self._allow_updates = False

    def writestr(self, zinfo_or_arcname, bytes, compress_type = None):
        if isinstance(zinfo_or_arcname, ZipInfo):
            name = zinfo_or_arcname.filename
        else:
            name = zinfo_or_arcname
        #******************************************************************************
        # If the file exits, and needs to be overridden, mark the entry, and create a 
        # temp-file for it we allow this only if the with statement is used
        #******************************************************************************

        if self._allow_updates and name in self.namelist():
            temp_file = self._replace[name] = self._replace.get(name, tempfile.TemporaryFile())
            temp_file.write(bytes)
        #******************************************************************************
        # Otherwise just act normally
        #******************************************************************************
        else:
            super(UpdateableZipFile, self).writestr(zinfo_or_arcname, bytes, compress_type = compress_type)

    def write(self, filename, arcname = None, compress_type = None):
        arcname = arcname or filename
        #******************************************************************************
        # If the file exits, and needs to be overridden, mark the entry, and create a 
        # temp-file for it we allow this only if the with statement is used
        #******************************************************************************
        if self._allow_updates and arcname in self.namelist():
            temp_file = self._replace[arcname] = self._replace.get(arcname,
                                                                   tempfile.TemporaryFile())
            with open(filename, 'rb') as source:
                shutil.copyfileobj(source, temp_file)
        #******************************************************************************
        # Otherwise just act normally
        #******************************************************************************
        else:
            super(UpdateableZipFile, self).write(filename, arcname = arcname, compress_type = compress_type)

    def __enter__(self):
        #******************************************************************************
        # Allow updates
        #******************************************************************************
        self._allow_updates = True
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        #******************************************************************************
        # call base to close zip file, organically
        #******************************************************************************
        try:
            super(UpdateableZipFile, self).__exit__(exc_type, exc_val, exc_tb)
            if len(self._replace) > 0:
                self._rebuild_zip()
        finally:
            #******************************************************************************
            # In case rebuild zip failed, be sure to still release all the temp files
            #******************************************************************************
            self._close_all_temp_files()
            self._allow_updates = False

    def _close_all_temp_files(self):
        for temp_file in self._replace.itervalues():
            if hasattr(temp_file, 'close'):
                temp_file.close()

    def remove_file(self, path):
        self._replace[path] = self.DeleteMarker()

    def _rebuild_zip(self):
        tempdir = tempfile.mkdtemp()
        try:
            temp_zip_path = os.path.join(tempdir, 'new.zip')
            with ZipFile(self.filename, 'r') as zip_read:
                #******************************************************************************
                # Create new zip with assigned properties
                #******************************************************************************
                with ZipFile(temp_zip_path, 'w', compression = self.compression, allowZip64 = self._allowZip64) as zip_write:
                    for item in zip_read.infolist():
                        #******************************************************************************
                        # Check if the file should be replaced / or deleted
                        #******************************************************************************
                        replacement = self._replace.get(item.filename, None)
                        #******************************************************************************
                        # If marked for deletion, do not copy file to new zipfile
                        #******************************************************************************
                        if isinstance(replacement, self.DeleteMarker):
                            del self._replace[item.filename]
                            continue
                        #******************************************************************************
                        # If marked for replacement, copy temp_file, instead of old file
                        #******************************************************************************
                        elif replacement is not None:
                            del self._replace[item.filename]
                            #******************************************************************************
                            # Write replacement to archive, and then close it (deleting the temp file)
                            #******************************************************************************
                            replacement.seek(0)
                            data = replacement.read()
                            replacement.close()
                        else:
                            data = zip_read.read(item.filename)
                        zip_write.writestr(item, data)
            #******************************************************************************
            # Override the archive with the updated one
            #******************************************************************************
            shutil.move(temp_zip_path, self.filename)
        finally:
            shutil.rmtree(tempdir, onerror=handleRemoveReadonly)
