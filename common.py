#!/usr/bin/env python
# vim:set et ts=2 sw=2 fileencoding=utf-8:

import os
import re
import pwd
import os.path
import random
import socket
import configparser

class AppConfig(object):
  def __init__(self, src):
    self.cf = configparser.SafeConfigParser()
    self.cf.read(src)

  def update(self, config):
    for section in config:
      for option in config[section]:
        self.cf.set(section, option, config[section][option])

  def save(self, out):
    with open(out, 'wb') as cnf:
      self.cf.write(cnf)

class SupervisorConfig(AppConfig):
  def __init__(self, src, working_dir):

    self.cf = configparser.SafeConfigParser()
    self.cf.read(src)

    socket  = os.path.join(working_dir, "logs/supervisor.sock")
    logfile = os.path.join(working_dir, "logs/supervisord.log")
    #cronlog = os.path.join(working_dir, "logs/program-crond.log")

    self.cf.set('unix_http_server', 'file',      socket)
    self.cf.set('supervisorctl',    'serverurl', 'unix://' + socket)
    self.cf.set('supervisord',      'logfile',   logfile)
    #self.cf.set('program:crond',    'stdout_logfile', cronlog)

class AutoZabbixConfig(object):
  def __init__(self, appname):
    self.path = "/var/lib/zabbix/%s/" % appname

    if not os.path.isdir(self.path):
      os.makedirs(self.path, 0o755)

  def fixpermissions(self, cnf):
    gid = GetZabbixGID("/host-passwd")
    os.chmod(cnf, 0o640)
    os.chown(cnf, -1, gid)

class Crond(object):
  def __init__(self):
    if os.path.isfile("/run/crond.pid"):
      os.unlink("/run/crond.pid")
    os.system("/usr/sbin/cron")

  def update(self, tasks, crontab):
    ct = open(crontab, "w")
    ct.write(tasks)
    ct.close()

  def save(self,user,crontab):
    os.system("crontab -u %s %s" % (user, crontab))

class RsyncConfig(object):
  def __init__(self, config):
    self.ip       = config["ip"]
    self.dest     = config["dest"]
    self.password = config["password"]
    self.pwfile   = "/rsync.pass"

    self.options  = ''
    if "options" in config:
      self.options  = config["options"]

    self.port  = 2873
    if "port" in config:
      self.port  = config["port"]

    _WritePassword(self.pwfile, self.password)

    self.cmd = "/usr/bin/rsync -al --port=%s --password-file=%s %s" % ( self.port, self.pwfile, self.options)

def _WritePassword(pwfile, password):
  with open(pwfile, 'wb') as pw:
    pw.write("%s\n" % password)
  os.chmod(pwfile, 0o600)


# 添加用于运行应用的受限账户
def AddRunUser(uid):

  try:
    pwd.getpwuid(uid)
  except KeyError:
    os.system('/usr/sbin/useradd -U -u %d -m -s /bin/false docker' % uid)

  return uid

# 获取宿主上zabbix用户的组id
def GetZabbixGID(passwd_file, user="zabbix"):
  group_id = 1000;
  if os.path.isfile(passwd_file):
    pw = open(passwd_file, "r")
    for line in pw:
      fields = line.split(':')
      if str(fields[0]) == str(user):
        group_id = int(fields[3])
        break
    pw.close()
  return group_id

def GetEnv(pattern):
  '''
  input(env):
    - slave_master_host=172.17.42.1
    - slave_master_port=3301

  output(dict):
    {'slave': {'master_host': '172.17.42.1', 'master_port': '3301'} }
  '''
  config = {}
  envs   = os.environ

  try:
    uid = int(os.getenv('User_Id'))
  except:
    uid = 1000

  config["uid"]  = uid

  for pat in pattern:
    for key in envs:
      m = pat.match(key)
      if m:
        section = m.group(1)
        options = m.group(2)

        if section in config:
          config[section][options] = envs[key]
        else:
          config[section] = { options: envs[key] }

  return config

def GenPasswd(pw_length=8):

  mypw = ""
  alphabet = "abcdefghijklmnopqrstuvwxyz"

  for i in range(pw_length):
    next_index = random.randrange(len(alphabet))
    mypw = mypw + alphabet[next_index]

  # replace 1 or 2 characters with a number
  for i in range(random.randrange(1,3)):
    replace_index = random.randrange(len(mypw)//2)
    mypw = mypw[0:replace_index] + str(random.randrange(10)) + mypw[replace_index+1:]

  # replace 1 or 2 letters with an uppercase letter
  for i in range(random.randrange(1,3)):
    replace_index = random.randrange(len(mypw)//2,len(mypw))
    mypw = mypw[0:replace_index] + mypw[replace_index].upper() + mypw[replace_index+1:]

  return mypw


if __name__ == '__main__':
  pass
