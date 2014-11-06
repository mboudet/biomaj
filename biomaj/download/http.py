import logging
import pycurl
import StringIO
import re
import os

from biomaj.utils import Utils
from biomaj.download.ftp import FTPDownload

class HTTPDownload(FTPDownload):
  '''
  Base class to download files from HTTP

  Makes use of http.parse.dir.line etc.. regexps to extract page information

  protocol=http
  server=ftp.ncbi.nih.gov
  remote.dir=/blast/db/FASTA/

  remote.files=^alu.*\\.gz$

  '''

  def __init__(self, protocol, host, rootdir, config):
    FTPDownload.__init__(self, protocol, host, rootdir)
    self.config = config


  def list(self, directory=''):
    '''
    List FTP directory

    :return: tuple of file and dirs in current directory with details
    '''
    logging.debug('Download:List:'+self.url+self.rootdir+directory)
    self.crl.setopt(pycurl.URL, self.url+self.rootdir+directory)
    output = StringIO.StringIO()
    # lets assign this buffer to pycurl object
    self.crl.setopt(pycurl.WRITEFUNCTION, output.write)
    self.crl.perform()
    # lets get the output in a string
    result = output.getvalue()
    '''
    'http.parse.dir.line': r'<a[\s]+href="([\S]+)/".*alt="\[DIR\]">.*([\d]{2}-[\w\d]{2,5}-[\d]{4}\s[\d]{2}:[\d]{2})',
    'http.parse.file.line': r'<a[\s]+href="([\S]+)".*([\d]{2}-[\w\d]{2,5}-[\d]{4}\s[\d]{2}:[\d]{2})[\s]+([\d\.]+[MKG]{0,1})',
    'http.group.dir.name': 1,
    'http.group.dir.date': 2,
    'http.group.file.name': 1,
    'http.group.file.date': 2,
    'http.group.file.size': 3,
    '''

    rfiles = []
    rdirs = []

    dirs = re.findall(self.config.get('http.parse.dir.line'), result)
    if dirs is not None and len(dirs)>0:
      for dir in dirs:
        rfile = {}
        rfile['permissions'] = ''
        rfile['group'] = ''
        rfile['user'] = ''
        rfile['size'] = '0'
        date = dir[int(self.config.get('http.group.dir.date'))-1]
        dirdate = date.split()
        parts = dirdate[0].split('-')
        #19-Jul-2014 13:02
        rfile['month'] = Utils.month_to_num(parts[1])
        rfile['day'] = parts[0]
        rfile['year'] = parts[2]
        rfile['name'] = dir[int(self.config.get('http.group.dir.name'))-1]
        rdirs.append(rfile)

    files = re.findall(self.config.get('http.parse.file.line'), result)
    if files is not None and len(files)>0:
      for file in files:
        rfile = {}
        rfile['permissions'] = ''
        rfile['group'] = ''
        rfile['user'] = ''
        rfile['size'] = file[int(self.config.get('http.group.file.size'))-1]
        date = file[int(self.config.get('http.group.file.date'))-1]
        dirdate = date.split()
        parts = dirdate[0].split('-')
        #19-Jul-2014 13:02
        rfile['month'] = Utils.month_to_num(parts[1])
        rfile['day'] = parts[0]
        rfile['year'] = parts[2]
        rfile['name'] = file[int(self.config.get('http.group.file.name'))-1]
        rfiles.append(rfile)

    return (rfiles, rdirs)