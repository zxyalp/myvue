# -*- coding: utf-8 -*-
"""
Created on 2018/12/21

@author: yang.zhou
"""
import os
import subprocess
import sys
import shutil
from datetime import datetime
import logging

import paramiko

MOCK_SVN_PATH = r'svn://svn.howbuy.test/usr/local/subversion-1.4.4/web_repos/Projects/tms-mock/'

MOCK_CONFIG_SVN = 'svn://192.168.220.100/usr/local/subversion-1.4.4/repos_doc/IT/部门级/质量管理部QA/配置管理/config/{tms_ip}'

MOCK_WEB_CONFIG_SVN = MOCK_CONFIG_SVN + '/tomcat/tomcat-tms-mock-web/tms-mock-web/WEB-INF/classes {' \
                                        'app_pub_dir}/WEB-INF/classes '

MOCK_WEBSERVICE_CONFIG_SVN = MOCK_CONFIG_SVN + '/tomcat/tomcat-tms-mock-webservice/ROOT/WEB-INF/classes/ {' \
                                               'app_pub_dir}/WEB-INF/classes '

MOCK_REMOTE_CONFIG_SVN = MOCK_CONFIG_SVN + '/remote/howbuy-tms-mock-remote {app_pub_dir}/base'

jdk_version = {'1.6': '/data/jdk/jdk1.6.0', '1.7': '/usr/local/jdk'}

# 启用日志打印
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s')
logger = logging.getLogger(__name__)


class MockDeploy:
    debug = False if 'linux' in sys.platform else True

    MOCK_BASE_PUB = r'F:\svn\pub' if debug else r'/data/shared/TMS_MOCK/'

    MOCK_DIR = 'tms-mock'

    PROVIDER_XML_DIR = r'tms-mock-service/src/main/resources/META-INF/spring'

    WORKSPACE_BAK = '/home/tomcat/.jenkins/workspace/tms_mock_deploy'

    # 包依赖顺序
    app_modules = {'tms-mock-web': ['tms-mock-client', 'tms-mock-web'],
                   'tms-mock-webservice': ['tms-mock-webservice'],
                   'tms-mock-remote': ['tms-mock-client', 'tms-mock-dao', 'tms-mock-service', 'tms-mock-remote']
                   }

    # mock服务声明文件
    all_provider_xml = {
        "acc-center-provider": "dubbo-mock-acc-center-provider.xml",
        "cc-provider": "dubbo-mock-cc-provider.xml",
        "crm-pre-provider": "dubbo-mock-crm-pre-provider.xml",
        "fp-simu-provider": "dubbo-mock-fp-simu-provider.xml",
        "fund-provider": "dubbo-mock-fund-provider.xml",
        "online-trade-provider": "dubbo-mock-online-trade-provider.xml",
        "gateway-provider": "dubbo-mock-gateway-provider.xml",
        "fbsonline-quickfundredeem": "dubbo-mock-fbsonline-quickfundredeem.xml"
    }

    def __init__(self, workspace, app_name, tms_ip, required_providers=None, mock_svn_url='trunk'):
        self.app_tar = None
        self.app_pub_dir = None
        self.workspace = workspace
        self.app_name = app_name
        self.tms_ip = tms_ip
        self.required_providers = required_providers
        self.mock_svn_url = mock_svn_url if mock_svn_url != 'trunk' else MOCK_SVN_PATH

    def execute(self):
        """
        tms-mock应用编译打包执行主方法
        """
        # 编译打包
        self.app_module_deploy()

        # 部署包预处理
        self.pre_package()

        # 推送部署包
        self.tms_mock_put()

    @staticmethod
    def get_sysdate():
        """
        返回当前时间格式,如yymmddhhmmss
        :return:
        """
        return datetime.today().strftime('%y%m%d%H%M%S')

    def export_svn(self, svn_url):
        """
        根据svn地址导出不带svn控制的项目
        :param svn_url:
        """
        os.chdir(self.workspace)
        self.with_system('rm -rf {workspace}/*'.format(workspace=self.workspace))
        os.system('svn export {svn_url}'.format(svn_url=svn_url))

    def all_export_svn(self):
        self.export_svn(MOCK_SVN_PATH)

    def mvn_deploy(self, app_path):
        os.chdir(os.path.join(self.workspace, app_path))
        logger.info("开始编译打包: mvn deploy {}".format(app_path))
        os.system('export JAVA_HOME="{}" && mvn clean deploy -Dmaven.test.skip=true -U'.format(jdk_version.get('1.7')))
        logger.info("done.")

    def mvn_install(self, app_path):
        os.chdir(os.path.join(self.workspace, app_path))
        logger.info("开始编译打包: mvn install {}".format(app_path))
        os.system('mvn clean install -Dmaven.test.skip=true -U')
        logger.info("done.")

    def all_mvn_deploy(self):
        self.mvn_deploy(self.MOCK_DIR)

    def app_module_deploy(self):
        """
        根据包依赖顺序打包
        :return:
        """
        self.all_export_svn()

        for app in self.app_modules.get(self.app_name):
            if 'tms-mock-service' == app:
                self.filter_mock_provider()
            self.mvn_install(os.path.join(self.MOCK_DIR, app))

    def cp_mock_config(self):
        pass

    def filter_mock_provider(self):
        """
        移除不需要打包的编译的provider.xml
        :return:
        """
        abs_provider_xml_dir = os.path.normpath(os.path.join(self.workspace, self.MOCK_DIR, self.PROVIDER_XML_DIR))

        if self.required_providers is None:
            self.required_providers = ''

        for provider in self.required_providers.split(','):
            self.all_provider_xml.pop(provider.strip())

        for xml in self.all_provider_xml:
            logger.info("移除Mock服务声明文件: %s", xml)
            self.with_system("rm -rf {}".format(os.path.join(abs_provider_xml_dir, xml)))

    def pre_package(self):
        """
        预处理已经编译完成的部署包
        :return: app.tar
        """

        app_date_dir = '{0}_{1}'.format(self.app_name, self.get_sysdate())

        # merge配置文件
        app_pub_dir = os.path.join(self.MOCK_BASE_PUB, self.MOCK_DIR, app_date_dir)

        self.with_mkdir(app_pub_dir)
        self.app_pub_dir = app_pub_dir

        if 'tms-mock-web' == self.app_name:
            os.system('unzip -o target/tms-mock-web.war -d {0}'.format(app_pub_dir))
            os.system(
                'svn export --force {}'.format(MOCK_WEB_CONFIG_SVN.format(tms_ip=self.tms_ip, app_pub_dir=app_pub_dir)))

        if 'tms-mock-webservice' == self.app_name:
            os.system('unzip -o target/tms-mock-webservice.war -d {0}'.format(app_pub_dir))
            os.system('svn export --force {}'.format(
                MOCK_WEBSERVICE_CONFIG_SVN.format(tms_ip=self.tms_ip, app_pub_dir=app_pub_dir)))

        if 'tms-mock-remote' == self.app_name:
            self.with_copytree('target/tms-mock-remote/remote', app_pub_dir)
            self.with_mkdir(os.path.join(app_pub_dir, 'base'))
            self.with_mkdir(os.path.join(app_pub_dir, 'logs'))
            os.system('svn export --force {}'.format(
                MOCK_REMOTE_CONFIG_SVN.format(tms_ip=self.tms_ip, app_pub_dir=app_pub_dir)))
            self.with_system('chmod +x {}/bin/*.sh'.format(app_pub_dir))

        self.app_tar_package(app_pub_dir)

    def app_tar_package(self, app_pub_dir):
        """
        将指定的目录打成一个tar包
        :param app_pub_dir:
        :return:
        """

        pub_dir, app_base = os.path.dirname(app_pub_dir), os.path.basename(app_pub_dir)
        os.chdir(pub_dir)
        os.system('tar cvf {0}.tar {0}'.format(app_base))
        app_tar = '{}.tar'.format(app_base)

        if not os.path.exists(app_tar):
            raise FileNotFoundError('Error:{}没有生成'.format(app_tar))
        else:
            logger.info('tar completion! {}'.format(app_tar))
            self.app_tar = app_tar

    def ssh_connect(self):
        tran = paramiko.Transport(self.tms_ip)
        tran.connect(username='tomcat', password='howbuy2015')
        return tran

    def sftp_put(self, local_path, remote_path):

        sftp = paramiko.SFTPClient.from_transport(self.ssh_connect())

        try:
            logger.info("开始远程推送部署包.")
            sftp.put(local_path, remote_path)
        except Exception as e:
            raise Exception("Put file {} 失败".format(local_path), e)
        else:
            logger.info("Put file {} 成功!".format(local_path))

    def ssh_exec(self, cmd):
        ssh = paramiko.SSHClient()
        ssh._transport = self.ssh_connect()
        try:
            logger.info("执行远程命令:{}".format(cmd))
            self.path_pre_check(cmd)
            _, stdout, stderr = ssh.exec_command(cmd)
        except Exception as e:
            raise Exception("SSH命令执行异常:{}".format(cmd), e)

        else:
            out, err = stdout.read(), stderr.read()

            if err != b'':
                try:
                    logger.info('stderr:{}'.format(err.decode('utf-8')))
                except UnicodeDecodeError:
                    logger.info('stderr:{}'.format(err.decode('gbk')))
                except Exception as e:
                    logger.info(e)
                    logger.info('stderr:{}'.format(err))

    def close(self):
        self.ssh_connect().close()

    def tms_mock_put(self):
        """
        将本地部署包上传到指定的应用服务器
        """
        web_base_dir = '/usr/local/tomcat-tms-mock-web'
        web_remote_dir = '{}/webapps/tms-mock-web'.format(web_base_dir)
        webservice_remote_dir = '{}/webapps/ROOT'.format(web_base_dir)
        app_remote_dir = '/data/app/howbuy-tms-mock-remote'

        if 'tms-mock-web' == self.app_name:
            self.remote_app_process(web_remote_dir)
            self.remote_app_restart(web_base_dir)

        if 'tms-mock-webservice' == self.app_name:
            self.remote_app_process(webservice_remote_dir)
            self.remote_app_restart(web_base_dir)

        if 'tms-mock-remote' == self.app_name:
            self.remote_app_process(app_remote_dir)
            self.remote_app_restart(app_remote_dir)

        self.close()

    def remote_app_process(self, remote_dir):
        """
        推送并解压部署包
        :param remote_dir:
        :return:
        """

        self.ssh_exec('rm -rf {}/*'.format(remote_dir))
        self.app_scp_post_process(remote_dir)

    def app_tar_post_process(self, remote_dir):

        if self.app_tar is None:
            raise ValueError('app_tar can not None.')

        tar_extract_dir = os.path.splitext(self.app_tar)[0]

        self.sftp_put(self.app_tar, '{0}/{1}'.format(remote_dir, self.app_tar))

        self.ssh_exec('tar xvmf {0}/{1} -C {0}'.format(remote_dir, self.app_tar))
        self.ssh_exec('mv {0}/{1}/* {0}'.format(remote_dir, tar_extract_dir))
        self.ssh_exec('rm -rf {0}/{1}'.format(remote_dir, tar_extract_dir))

    def app_scp_post_process(self, remote_dir):

        if self.app_pub_dir is None:
            raise ValueError('app_pub_dir can not None.')

        self.with_scp('{}/*'.format(self.app_pub_dir), remote_dir)

    def remote_app_restart(self, remote_dir):

        self.ssh_exec('sh {}/bin/restart.sh'.format(remote_dir))

    @staticmethod
    def path_pre_check(cmd):
        """
        path不能为空,'/' ,'/*' ,'\','\*'
        """
        path_list = []

        for t in cmd.split():
            if t in ['tar']:
                return cmd
            if t in ['rm']:
                continue
            if t[0] == '-':
                continue
            path_list.append(t)

        for path in path_list:
            logger.debug("开始命令路径预检查.")
            if not path or path in ['/', '/*', '//', '//*', '\\', '\\*']:
                raise Exception("The path to be deleted cannot be empty or '/'!")
        else:
            logger.debug("检查完毕, 执行路径未包含危险路径.")
        return cmd

    def with_system(self, cmd):
        self.with_call(self.path_pre_check(cmd))

    @staticmethod
    def with_call(cmd):
        logger.info('Execute command: %s', cmd)
        subprocess.check_call(cmd, shell=True)

    def with_mkdir(self, path):
        try:
            os.makedirs(path)
        except FileExistsError as e:
            logger.info(e)
            shutil.rmtree(self.path_pre_check(path))
            os.makedirs(path)
        else:
            logger.info("mkdir {} success!".format(path))

    def with_scp(self, local_path, remote_path):
        """
        scp命令
        :param local_path:
        :param remote_path:
        :return:
        """
        logger.info("执行scp.")
        scp_cmd = 'scp -r'
        if self.tms_ip in ['192.168.222.230']:
            scp_cmd = 'sshpass -p howbuy2015 scp -r'
        self.with_system("{scp} {local_path} {username}@{host}:{remote_path}".format(scp=scp_cmd, local_path=local_path,
                                                                                     username='tomcat',
                                                                                     host=self.tms_ip,
                                                                                     remote_path=remote_path))

    @staticmethod
    def with_copytree(src, dst, symlinks=False, ignore=None):
        if not os.path.exists(dst):
            os.makedirs(dst)
        for item in os.listdir(src):
            s = os.path.join(src, item)
            d = os.path.join(dst, item)
            if os.path.isdir(s):
                shutil.copytree(s, d, symlinks, ignore)
            else:
                shutil.copy2(s, d)


def parse_argv(arg):
    if len(arg) == 5:
        arg.insert(4, None)
    return arg[1:]


if __name__ == '__main__':
    """    
    workspace: job空间
    app_name：应用名称
    tms_ip： 部署环境IP
    required_providers: 需要移除的服务
    mock_svn_url： mock svn path
    """

    # workspace = r'F:\svn\test'
    # app_name = 'tms-mock-remote'
    # tms_ip = '192.168.221.207'
    # required_providers = 'all,acc-center-provider,cc-provider,online-trade-provider,fund-provider,fp-simu-provider,crm-pre-provider'
    # mock_svn_url = 'trunk'
    # mockd = MockDeploy(*parse_argv([None, workspace, app_name, tms_ip, required_providers, mock_svn_url]))

    mockd = MockDeploy(*parse_argv(sys.argv))
    mockd.execute()
