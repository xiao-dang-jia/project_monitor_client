#!/usr/bin/python
# -*- coding: UTF-8 -*-
'''
Created on 2013-7-4

@author: administrator
'''

import LOGGER as LOGGER
import paramiko
import shlex
import subprocess
import time
from fabric.api import lcd,local
logger = LOGGER.genLogger(__name__)
loggerCommandLine = LOGGER.genLogger(__name__, LOGGER.logProperties.logCommandLine)

def strToLogOutput(output, limitSize=50):
    out = str(output)
    if type(out) is str or type(out) is unicode:
        if len(out)>50:
            partOut = out[:50]+'...'
            return partOut
        else:
            return out
    else:
        return ''

class ShellExecutor(object):
    
    def execute(self, command, cwd=None):
        loggerCommandLine.info('[local]%s:%s start' % (cwd, command))
        args = shlex.split(command)
        logger.debug(command)
        if cwd is not None:
            logger.debug(cwd)
        p = subprocess.Popen(args,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,cwd=cwd)

        stdout, stderr = p.communicate()
        returncode = p.returncode
        loggerCommandLine.info('[local]%s:%s end. Result:%d ' % (cwd, command, returncode))
        if returncode != 0:
            logger.debug('error:%s returncode: %d ' % (command,returncode))
            logger.debug('stdout:%s ' % (strToLogOutput(stdout)))
            raise Exception
        
        return stdout
    
    def executeExceptionRetry(self, command, retryNum=3, sleep=3):
        isFirst = True
        isError = False
        while isFirst or (isError and retryNum>0):
            if isFirst:
                isFirst = False
            else:
                time.sleep(sleep)
            
            retryNum -= 1
            try:
                self.execute(command)
                isError = False
            except Exception,e:
                isError = True
                logger.error('execute command:%s exception ! ' % command)
                logger.error( e )
        return not isError
    
    def executeExceptionOutput(self, command, retryNum=3, sleep=3):
        isFirst = True
        isError = False
        while isFirst or (isError and retryNum>0):
            if isFirst:
                isFirst = False
            else:
                time.sleep(sleep)
            
            retryNum -= 1
            try:
                return self.execute(command)
            except Exception,e:
                isError = True
                logger.error('execute command:%s exception ! ' % command)
                logger.error( e )
        if isError:
            raise Exception
    
    def getMD5Key(self, path):
        command = 'md5sum ' + path
        stdout = self.execute(command)
        md5_key = stdout.split(' ')[0]
        if md5_key.strip() == '':
                raise Exception
        return md5_key
    
    #特殊方法执行
    def execOther(self,command,cwd=None):
        loggerCommandLine.info('[local-execOther]%s:%s ' % (cwd, command))
        logger.debug(command)
        logger.debug(cwd)
        if cwd is None:
            return local(command)
        with lcd(cwd):
            return local(command)
    
class MySSH(object):
    def __init__(self):
        self._ssh = None
        self._host = None
        self._port = None
        self._username = None
        self._password = None

    def connect(self, host, port, username, password):
        self._host = host
        self._port = port
        self._username = username
        self._password = password

        self._ssh = paramiko.SSHClient()
        self._ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self._ssh.connect(host, port=port, username=username, password=password, look_for_keys=False)
        # self._channel = self._ssh.get_transport().open_session()


    def execute(self, command):
        loggerCommandLine.info("[SSH] <%s:%s> start " % (self._host, command))

        channel = self._ssh.get_transport().open_session()
        channel.exec_command(command)
        status = channel.recv_exit_status()
        channel.close()

        loggerCommandLine.info("[SSH] <%s:%s> end. Result: [%s] " % (self._host, command, status))
        
        if status != 0:
            raise Exception
        return status
    
    def executeExceptionRetry(self, command, retryNum=3, sleep=3):
        isFirst = True
        isError = False
        while isFirst or (isError and retryNum>0):
            if isFirst:
                isFirst = False
            else:
                time.sleep(sleep)
            
            retryNum -= 1
            try:
                self.execute(command)
                isError = False
            except Exception,e:
                isError = True
                logger.error('execute command:%s exception ! ' % command)
                logger.error( e )
        return not isError
    
    def output(self, command):
        loggerCommandLine.info("[SSH-output] <%s:%s> start " % (self._host, command))

        stdin, stdout, stderr = self._ssh.exec_command(command)
        lines = stdout.readlines()
        
        loggerCommandLine.info("[SSH-output] <%s:%s> end. Result: [%s] " % (self._host, command, strToLogOutput(lines)))
        
        if lines:
            return lines

    def upload(self, localpath, remotepath):
        loggerCommandLine.info("[SFTP-upload] <%s => %s:%s> transfer start..." % (localpath, self._host, remotepath))

        sftp = self._ssh.open_sftp()
        sftp.put(localpath, remotepath)
        sftp.close()

        loggerCommandLine.info("[SFTP-upload] <%s> => <%s:%s> transfer end." % (localpath, self._host, remotepath))

    def download(self, localpath, remotepath):
        loggerCommandLine.info("[SFTP-download] <%s => %s:%s> transfer start..." % (localpath, self._host, remotepath))

        sftp = self._ssh.open_sftp()
        sftp.get(remotepath, localpath)
        sftp.close()

        loggerCommandLine.info("[SFTP-download] <%s> => <%s:%s> transfer end." % (localpath, self._host, remotepath))
        
    def exists(self, path):
        logger.info("[SSH-exists] <%s:%s> start " % (self._host, path))
        
        b = False
        
        pathip = path.strip()
        if pathip.endswith('/'):
            pathip = pathip[:len(pathip)-1]
        
        name = pathip.split('/').pop()
        fs = self.getFiles(pathip[:pathip.rindex(name)])
        if not fs:
            return b
        for f in fs:
            if name == f.replace('\n',''):
                b = True
        
        logger.info("[SSH-exists] <%s:%s> end. Result: [%s] " % (self._host, path, b))
        return b
    
    def getFiles(self, path):
        logger.info("[SSH-getFiles] <%s:%s> start " % (self._host, path))
        
        files = []
        currentFiles = self.output('ls ' + path)
        if currentFiles is None:
            return files
        
        if not currentFiles:
            return files
        
        for f in currentFiles:
            files.append(f.replace('\n',''))
        
        logger.info("[SSH-getFiles] <%s:%s> end. Result: [%s] " % (self._host, path, strToLogOutput(files)))
        return files
    
    def getMD5Key(self, path):
        output = self.output('md5sum '+path)
        md5_key = output[0].split(' ')[0]
        if md5_key.strip() == '':
            raise Exception
        return md5_key
    
    def checkMD5FileEqu(self,first,second):
        first_key = self.getMD5Key(first)
        second_key = self.getMD5Key(second)
        if first_key != second_key:
            return False
        return True
    
    def checkMD5DirectoryEqu(self, first, second, removeFiles=[], removeFolders=[]):
        first_key = self.genMD5Directory(first, removeFiles, removeFolders)
        second_key = self.genMD5Directory(second, removeFiles, removeFolders)
        if first_key != second_key:
            return False
        return True
    
#     获取文件夹下的所有文件的MD5值
#     directory：文件夹
#     removeFiles：需要排除的文件,文件格式不带目录
#     removeFolders：需要排除的文件夹,格式按照例子
    def genMD5Directory(self, directory, removeFiles=[], removeFolders=[]):
        removeFolderStr = None
        removeFolderLength = len(removeFolders)
        removeFileStr = None
        removeFileLength = len(removeFiles)
        
        if removeFolderLength>0:
            removeFolderStr = ''
        if removeFileLength>0:
            removeFileStr = ''
        
        for folder in removeFolders:
            index_tmp = self._get_index_(removeFolders, folder)
            if index_tmp == 0:
                removeFolderStr += (' -path %s -prune -o ' % folder)
            elif index_tmp == removeFolderLength-1:
                removeFolderStr += (' -path %s -prune ' % folder)
            else:
                removeFolderStr += (' -path %s -prune -o ' % folder)
            
        for fileName in removeFiles:
            removeFileStr += (' -not -name "%s" ' % fileName)
            
        removeStr = ''
        if removeFolderStr is not None and removeFileStr is not None:
            removeStr = ' %s -o %s ' % (removeFolderStr, removeFileStr)
        elif removeFolderStr is not None:
            removeStr = removeFolderStr
        elif removeFileStr is not None:
            removeStr = removeFileStr
        
        out = self.output('cd %s; find ./ %s -type  f -exec md5sum {} \;|sort|md5sum' % (directory, removeStr))[0]
        md5_key = out.split()[0]
        return md5_key
    
    def _get_index_(self, list, val):
        index = 0
        for li in list:
            if li == val:
                return index
            else:
                index += 1
        return -1
    
    def isFileNotDirectory(self, path):
        command = 'stat ' + path
        output = self.output(command)
#        没有找到目录或无输出
        if output == '':
            raise Exception
#         firstLine = output[0]
        secondLine = output[1]
        val_file = 'file'
#         val_directory = 'directory'
        if secondLine.find(val_file) != -1:
            return True
    
    def copy(self, fromPath, toPath):
# 拷贝文件
#         cp dir/a dir2/ --this
#         cp dir/a dir2/a --this
# 拷贝文件夹
#         cp a/dir a/  --this
#         cp a/dir/* a/dir --err
        isFile = self.isFileNotDirectory(fromPath)
        command = None
        
        #备份目录不存在创建
        if not self.exists(toPath):
            self.execute('mkdir -p %s ' % toPath)
            
#       判断是文件还是文件夹  
        if isFile:
            command = 'cp %s %s' % (fromPath,toPath)
        else:
            command = 'cp -r %s %s' % (fromPath,toPath)
        
        if command is None:
            return False
        else:
            self.execute(command)
        return True
    
if __name__ == '__main__':
#     _ssh = MySSH()
#     _ssh.connect('192.168.30.254',21069,'admin','datayun9332')
#     for f in _ssh.output('ls'):
#         print f.replace('\n','')
#     path = ' /tmp/asd1 '
#     print _ssh.exists(path)
#     print path
#     _ssh.execute("ls /tmp")
#     _ssh.upload('/tmp/aa.py', '/tmp/aa/aa.py')

    try:
#         os.system('df -h1')
        sh = ShellExecutor()
#         path = '/tmp/publish/CCMS-SD/CCMS-SD_root/REL/4.1.4/ccms-web-builder-4.1.4.war'
#         print sh.getMD5Key(path)
        sh.execute('find  /tmp/publish  -type  f  -exec md5sum {} \;|sort|md5sum')

#         _ssh = MySSH()
#         _ssh.connect('192.168.30.254',21069,'admin','datayun9332')
#         path = '/data/resin/resin-4.0.25/CCMS-PUBLISH/ccms-web-builder-4.1.4.war'
#         print _ssh.getMD5Key(path)
        
#         _ssh = MySSH()
#         _ssh.connect('192.168.30.254',21069,'admin','datayun9332')
#         command = 'echo hello'
#         command = 'ls'
#         command = 'md5sum /data/auto-publish/config.py'
#         command = 'sh /data/resin/resin-4.0.25/bin/resinctl web-app-stop --host web.fabutest ROOT'
#         command = 'unzip -fo /data/resin/resin-4.0.25/CCMS-PUBLISH/ccms-web-builder-4.1.4.war -d /data/resin/resin-4.0.25/hosts/fabutest/webapps/ROOT'
#         command = '/usr/local/mybatis-migrations-3.1.0/bin/migrate --path=/usr/local/mybatis-migrations-3.1.0/ccms/ --env=fabutest status'
#         command = 'sh /data/resin/resin-4.0.25/bin/resin.sh stop'
        
#         print _ssh.copy('/tmp/dir','/tmp/dir2')
                
        print 33
    except Exception,e:
            print e
            print 22
    finally:
        print 11
