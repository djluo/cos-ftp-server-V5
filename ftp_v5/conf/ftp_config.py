# -*- coding:utf-8 -*-

import os
# import configparser
# import platform
import logging
import ftp_v5.conf.common_config

from multiprocessing import cpu_count

logger = logging.getLogger(__name__)


class CosFtpConfig:

    def __init__(self):

        self.secretid = os.getenv("COSFTPD_cos_secretid")
        self.secretkey = os.getenv("COSFTPD_cos_secretkey")
        self.bucket = os.getenv("COSFTPD_cos_bucket")

        if len(str(self.bucket).split("-")) < 2:
            msg = "Config error: bucket field must be {bucket name}-{appid}"
            raise ValueError(msg)

        self.host = os.getenv("COSFTPD_cos_endpoint", None)
        self.region = os.getenv("COSFTPD_cos_region")

        self.homedir = os.getenv("COSFTPD_cos_user_home_dir")

        login_users = os.getenv("COSFTPD_ftp_login_users")
        login_users = login_users.strip(" ").split(";")
        self.login_users = list()
        # self.login_users 的结构为 [ (user1,pass1,RW), (user2,pass2,RW) ]
        for element in login_users:
            login_user = element.split(":")
            self.login_users.append(tuple(login_user))

        self.masquerade_address = os.getenv("COSFTPD_ftp_masquerade_address",
                                            None)

        self.listen_port = int(os.getenv("COSFTPD_ftp_listen_port"))
        passive_ports = os.getenv('COSFTPD_ftp_passive_port').split(',')

        if len(passive_ports) > 1:
            self.passive_ports = range(int(passive_ports[0]), int(passive_ports[1]))
        elif len(passive_ports) == 1:
            self.passive_ports = range(int(passive_ports[0]), 65535)
        else:
            self.passive_ports = range(60000, 65535)

        sfms = 200 * ftp_v5.conf.common_config.GIGABYTE  # 默认单文件最大为200G
        self.single_file_max_size = int(
                os.getenv("COSFTPD_ftp_single_file_max_size", sfms))

        self.min_part_size = 2 * ftp_v5.conf.common_config.MEGABYTE
        self.upload_thread_num = cpu_count() * 4
        self.max_connection_num = 512
        self.max_list_file = 1000

        ll = str(os.getenv("COSFTPD_log_level", "INFO").upper())
        if ll in ("INFO", "WARN", "DEBUG", "ERROR", "CRITICAL"):
            self.log_level = eval("logging.%s" % ll)

        self.log_dir = str(os.getenv("COSFTPD_log_dir"))
        if not os.path.exists(self.log_dir):
            os.mkdir(self.log_dir)

        self.log_filename = "cos_v5.log"
        if str(self.log_dir).endswith("/"):
            self.log_filename = self.log_dir + self.log_filename
        else:
            self.log_filename = self.log_dir + "/" + self.log_filename

    def __repr__(self):
        return "%s()" % self.__class__.__name__

    def __str__(self):
        return "appid: %s \n" \
               "secretid: %s \n" \
               "secretekey: %s \n" \
               "bucket: %s \n" \
               "region: %s \n" \
               "homedir:%s \n" \
               "login_users: %s \n" \
               "masquerade_address: %s \n" \
               "listen_port: %d \n" \
               "passive_ports: %s \n" \
               "single_file_max_size:%d \n" \
               "min_part_size: %d \n" \
               "upload_thread_num: %d \n" \
               "max_connection_num: %d \n" \
               "max_list_file: %d \n" \
               "log_level: %s \n" \
               "log_dir: %s \n" \
               "log_file_name: %s \n" \
               "host: %s" % (
                   self.appid, self.secretid, self.secretkey, self.bucket, self.region, self.homedir,
                   self.login_users, self.masquerade_address, self.listen_port, self.passive_ports,
                   self.single_file_max_size, self.min_part_size, self.upload_thread_num, self.max_connection_num,
                   self.max_list_file, self.log_level, self.log_dir, self.log_filename, self.host)


# unittest
if __name__ == "__main__":
    print(CosFtpConfig())
