import fnmatch
import logging

import paramiko


class SFTPClient:
    def __init__(self, host, username, password, port=22):
        self.host = host
        self.username = username
        self.password = password
        self.port = port

        self.transport = paramiko.Transport((self.host, self.port))
        self.transport.connect(username=self.username, password=self.password)
        self.client = paramiko.SFTPClient.from_transport(self.transport)

    def __del__(self):
        self.client.close()
        self.transport.close()

    def ls(self, path, glob_pattern):
        logging.debug(
            f'SFTP: Listing remote files matching {path}/{glob_pattern}')

        all_files = self.client.listdir(path)
        filtered_files = fnmatch.filter(all_files, glob_pattern)

        logging.debug(f'SFTP: Found {filtered_files}')

        return filtered_files

    def get(self, path):
        logging.debug(f'SFTP: Getting remote file {path}')

        with self.client.open(path, "r") as sftp_file:
            return sftp_file.read()

    def delete(self, path):
        logging.debug(f'SFTP: Deleting remote file {path}')
        self.client.remove(path)
