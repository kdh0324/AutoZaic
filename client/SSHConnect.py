# coding=utf-8
"""
# usage
ssh = SSHConnect("141.223.181.102", 22, "oop8917", "8917")
ssh.mkdir_on_sever("/home/oop8917/dongwoo/videos", True)

- parameter order : from , to(no relation with local, remote)
- write exact file and dir name
ssh.file_upload("videos/sj2.mp4", "/home/oop8917/dongwoo/videos/sj2.mp4")
ssh.file_download("/home/oop8917/dongwoo/output.avi", "output.avi")
ssh.directory_upload("./dataset", "/home/oop8917/dongwoo/")
ssh.directory_download("/home/oop8917/dongwoo/dataset", "./", )
ssh.ssh_execute("pwd;source cuda-env;source ~/.bashrc; cd dongwoo;pwd;python main.py")

"""
import paramiko
import os
import platform
from stat import *

class SSHConnect:
    def __init__(self, ip, port, username, password):
        self.get_ssh(ip, port, username, password)
        self.get_sftp()

    def __del__(self, ):
        self.ssh.close()
        self.sftp.close()

    def mkdir_on_sever(self, remote, is_dir=False):
        # create route on sftp
        # if remote path is directory, is_dir should be  True
        dirs_ = []
        if is_dir:
            dir_ = remote
        else:
            dir_, basename = os.path.split(remote)
        while len(dir_) > 1:
            dirs_.append(dir_)
            dir_, _ = os.path.split(dir_)

        if len(dir_) == 1 and not dir_.startswith("/"):
            dirs_.append(dir_)

        while len(dirs_):
            dir_ = dirs_.pop()
            try:
                self.sftp.stat(dir_)
            except:
                print("making ... dir", dir_)
                self.sftp.mkdir(dir_)

    def mkdir_on_local(self, local, is_dir=False):
        # if remote path is directory, is_dir should be  True
        dirs_ = []
        if is_dir:
            dir_ = local
        else:
            dir_, basename = os.path.split(local)
        while len(dir_) > 1:
            dirs_.append(dir_)
            dir_, _ = os.path.split(dir_)

        if len(dir_) == 1 and not dir_.startswith("/"):
            dirs_.append(dir_)

        while len(dirs_):
            dir_ = dirs_.pop()
            try:
                os.stat(dir_)
            except:
                print("making ... dir", dir_)
                os.mkdir(dir_)

    def file_upload(self, local_path, remote_path):
        self.mkdir_on_sever(remote_path)
        try:
            self.sftp.put(local_path, remote_path)
        except Exception as e:
            print("fail to upload " + local_path + " ==> " + remote_path)
            raise e
        print("success to upload " + local_path + " ==> " + remote_path)
        return True

    def file_download(self, remote_path, local_path):
        self.mkdir_on_local(local_path)
        try:
            self.sftp.get(remote_path, local_path)
        except Exception as e:
            print("fail to download " + remote_path + " ==> " + local_path)
            raise e
        print("success to downdload " + remote_path + " ==> " + local_path)
        return True

    def directory_upload(self, local_directory, remote_directory):
        self.mkdir_on_sever(remote_directory, True)
        cwd = os.getcwd()
        os.chdir(os.path.split(local_directory)[0])
        parent = os.path.split(local_directory)[1]
        is_window = (platform.system() == "Windows")
        for walker in os.walk(parent):
            try:
                for file in walker[2]:
                    pathname = os.path.join(remote_directory, walker[0], file)
                    if is_window:
                        pathname = pathname.replace('\\', '/')
                        self.file_upload(os.path.join(walker[0], file), pathname)
            except Exception as e:
                print(e)
                raise e
        return True

    def directory_download(self, remote_directory, local_directory):
        basename = os.path.split(remote_directory)[1]
        local_directory = os.path.join(local_directory, basename)
        self.mkdir_on_local(local_directory, True)
        remote_directory += '/'

        for walker in self.sftp_walk(remote_directory):
            try:
                for file in walker[1]:
                    localpath = os.path.join(local_directory, os.path.split(walker[0])[1], file)
                    remotepath = os.path.join(walker[0], file)
                    localpath = localpath.replace('\\', '/')
                    remotepath = remotepath.replace('\\', '/')
                    self.file_download(remotepath, localpath)

            except Exception as e:
                print(e)
                raise e
        return True

    def sftp_walk(self, remotepath):
        # get all folder and file in remotepath
        path = remotepath
        files = []
        folders = []
        for f in self.sftp.listdir_attr(remotepath):
            if S_ISDIR(f.st_mode):
                folders.append(f.filename)
            else:
                files.append(f.filename)
        if files:
            yield path, files
        for folder in folders:
            new_path = os.path.join(remotepath, folder)
            for x in self.sftp_walk(new_path):
                yield x

    def ssh_execute(self, command, is_print=True):
        # execute command on server ex) command = "cd dir_name"
        # if you don't want to print respond, then set is_print false

        mark = "ssh_helper_result_mark!!@@="
        command = command + ";echo " + mark + "$?"

        try:
            stdin, stdout, stderr = self.ssh.exec_command(command, get_pty=True)
        except Exception as e:
            print(e)
            raise e

        for line in stdout:
            msg = line.strip('\n')
            if (msg.startswith(mark)):
                exit_status = msg[len(mark):]
            else:
                if (is_print == True):
                    print(line.strip('\n'))

        return True

    def get_ssh(self, host_ip, port, id, pw):
        try:
            # create ssh client
            self.ssh = paramiko.SSHClient()

            # set ssh policy
            self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            # connect
            self.ssh.connect(hostname=host_ip, port=port, username=id, password=pw)
        except Exception as e:
            print(e)
            raise e

    def get_sftp(self):
        try:
            self.sftp = paramiko.SFTPClient.from_transport(self.ssh.get_transport())
        except Exception as e:
            print(e)
            raise e
