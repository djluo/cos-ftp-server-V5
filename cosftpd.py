#!/usr/bin/env python
# vim:set et ts=4 sw=4 fileencoding=utf-8:

import os
import re
import os.path
from common import GetEnv, AddRunUser
from ftp_v5 import server


def FixPermission():
    if os.path.isdir("data"):
        os.system("mkdir -pv data")
    if os.path.isdir("logs"):
        os.system("mkdir -pv logs")

    os.system("chown docker.docker -R data logs")


if __name__ == '__main__':

    # 应用路径
    working_dir = os.getcwd()

    # 环境变量
    pattern = [re.compile(r'^(COSFTPD)_(.*)')]
    envs = GetEnv(pattern)

    # 添加账号
    uid = envs["uid"]
    AddRunUser(uid)

    # 修复权限
    FixPermission()

    # 切换账号
    os.setgid(uid)
    os.setuid(uid)

    # 开启应用
    server.main()
