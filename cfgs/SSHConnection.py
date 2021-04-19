from paramiko.client import SSHClient, WarningPolicy
from paramiko import RSAKey
import os


class SSHConnection(object):
    __instance = None
    connection = None
    key = None

    def __new__(cls):
        if SSHConnection.__instance is None:
            SSHConnection.__instance = object.__new__(cls)
            SSHConnection.connection = SSHClient()
            SSHConnection.connection.load_system_host_keys()
            SSHConnection.connection.set_missing_host_key_policy(WarningPolicy)
            homePath = os.path.expanduser('~')
            key = RSAKey.from_private_key_file(str(homePath)+"/.ssh/id_rsa")
        return SSHConnection.__instance

    def getConnection(self, ip):
        SSHConnection.connection.connect(
            ip, username='root', pkey=SSHConnection.key, timeout=60)
        return SSHConnection.connection
