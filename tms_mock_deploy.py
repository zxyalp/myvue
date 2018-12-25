# -*- coding: utf-8 -*-
"""
Created on 2018/12/21

@author: xing yan
"""
import os
import sys
from datetime import datetime

import paramiko

MOCK_SVN_PATH = r'svn://svn.howbuy.test/usr/local/subversion-1.4.4/web_repos/Projects/tms-mock/'

MOCK_CONFIG_SVN = 'svn://192.168.220.100/usr/local/subversion-1.4.4/repos_doc/IT/部门级/质量管理部QA/配置管理/config/{tms_ip}'

MOCK_WEB_CONFIG_SVN = MOCK_CONFIG_SVN+'/tomcat/tomcat-tms-mock-web/tms-mock-web/WEB-INF/classes {app_tmp_dir}/WEB-INF/classes'

MOCK_WEBSERVICE_CONFIG_SVN = MOCK_CONFIG_SVN+'/tomcat/tomcat-tms-mock-webservice/ROOT/WEB-INF/classes/ {app_tmp_dir}/WEB-INF/classes'

MOCK_REMOTE_CONFIG_SVN = MOCK_CONFIG_SVN+'/remote/howbuy-tms-mock-remote {app_tmp_dir}/conf'

app_name_list = ['tms-mock-web', 'tms-mock-webservice', 'tms-mock-service', 'tms-mock-remote']

jdk_version = {'1.6': '/data/jdk/jdk1.6.0', '1.7': '/usr/local/jdk'}

all_provider_xml = {
    "acc-center-provider": "dubbo-mock-acc-center-provider.xml",
    "cc-provider": "dubbo-mock-cc-provider.xml",
    "crm-pre-provider": "dubbo-mock-crm-pre-provider.xml",
    "fp-simu-provider": "dubbo-mock-fp-simu-provider.xml",
    "fund-provider": "dubbo-mock-fund-provider.xml",
    "online-trade-provider": "dubbo-mock-online-trade-provider.xml",
}

FRONT_IP = {'192.168.221.217': '192.168.221.25', '192.168.221.218': '192.168.220.25',
            '192.168.221.202': '192.168.221.27', '192.168.221.210': '192.168.220.24',
            '192.168.221.219': '192.168.221.87', '192.168.222.88': '192.168.221.90',
            '192.168.221.220': '192.168.221.109', '192.168.221.106': '192.168.221.105',
            '192.168.221.54': '192.168.221.52', '192.168.221.55': '192.168.221.53',
            '192.168.221.172': '192.168.221.171', '192.168.221.216': '192.168.221.24',
            '192.168.221.215': '192.168.220.115', '192.168.221.212': '192.168.220.128',
            '192.168.221.211': '192.168.221.30', '192.168.221.214': '192.168.221.88',
            '192.168.221.223': '192.168.221.222', '192.168.221.201': '192.168.221.89',
            '192.168.221.213': '192.168.221.28', '192.168.224.18': '192.168.224.19',
            '192.168.221.123': '192.168.221.122', '192.168.222.87': '192.168.221.26'}


class MockDeploy:

    _debug = True

    MOCK_BASE_PATH = r'/data/shared/TMS_MOCK/' if not _debug else r'F:\svn\pub'

    MOCK_DIR = 'tms-mock'

    PROVIDER_XML_DIR = r"tms-mock-service\src\main\resources\META-INF\spring"

    # 包依赖顺序
    app_modules = {'tms-mock-web': ['tms-mock-client', 'tms-mock-web'],
                   'tms-mock-webservice': ['tms-mock-webservice'],
                   'tms-mock-remote': ['tms-mock-client', 'tms-mock-dao', 'tms-mock-service', 'tms-mock-remote']
                   }

    def __init__(self, workspace, app_name, tms_ip, remove_providers=None, mock_svn_url='trunk'):

        self.workspace = workspace
        self.app_name = app_name
        self.tms_ip = tms_ip
        self.remove_providers = remove_providers
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
        os.system('rm -rf {workspace}/* && svn export {svn_url}'.format(workspace=self.workspace, svn_url=svn_url))

    def all_export_svn(self):
        self.export_svn(MOCK_SVN_PATH)

    def mvn_deploy(self, file_path):
        os.chdir(os.path.join(self.workspace, file_path))
        print("开始编译打包: mvn deploy {}".format(os.path.abspath('.')))
        os.system('export JAVA_HOME="{}" && mvn clean deploy -Dmaven.test.skip=true -U'.format(jdk_version.get('1.7')))

    def mvn_install(self, file_path):
        os.chdir(os.path.join(self.workspace, file_path))
        print("开始编译打包: mvn install {}".format(os.path.abspath('.')))
        os.system('mvn clean install -Dmaven.test.skip=true -U')
        print("-------------done---------------")

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
        provider_xml = []
        abs_provider_xml_dir = os.path.join(self.MOCK_BASE_PATH, self.MOCK_DIR, self.PROVIDER_XML_DIR)

        if self.remove_providers:
            return

        for provider in self.remove_providers:
            provider_xml.append(all_provider_xml.get(provider))

        for xml in provider_xml:
            print("移除不需要的服务声明文件:{}".format(xml))
            os.system("rm -rf {}".format(os.path.join(abs_provider_xml_dir, xml)))

    def pre_package(self):
        """
        预处理已经编译完成的部署包
        :return: app.tar
        """

        # merge配置文件
        app_tmp_dir = os.path.join(self.MOCK_BASE_PATH, self.MOCK_DIR, '{0}_{1}'.format(self.app_name, self.get_sysdate()))

        print("生成临时目录路径：", app_tmp_dir)

        if 'tms-mock-web' == self.app_name:
            os.system('mkdir -p {0} && unzip -o target/tms-mock-web.war -d {0}'.format(app_tmp_dir))
            os.system('svn export --force {}'.format(MOCK_WEB_CONFIG_SVN.format(tms_ip=self.tms_ip, app_tmp_dir=app_tmp_dir)))

        if 'tms-mock-webservice' == self.app_name:
            os.system('mkdir -p {0} && unzip -o target/tms-mock-webservice.war -d {0}'.format(app_tmp_dir))
            os.system('svn export --force {}'.format(MOCK_WEBSERVICE_CONFIG_SVN.format(tms_ip=self.tms_ip, app_tmp_dir=app_tmp_dir)))

        if 'tms-mock-remote' == self.app_name:
            os.system('mkdir -p {0} && cp -r target/tms-mock-remote/remote/* {0}'.format(app_tmp_dir))
            os.system('mkdir -p {0}/conf {0}/logs'.format(app_tmp_dir))
            os.system('svn export --force {}'.format(MOCK_REMOTE_CONFIG_SVN.format(tms_ip=self.tms_ip, app_tmp_dir=app_tmp_dir)))

        os.system('tar cvf {0}.tar {0}'.format(app_tmp_dir))

        return '{}.tar'.format(app_tmp_dir)

    def ssh_connect(self):
        tran = paramiko.Transport(self.tms_ip)
        tran.connect(username='tomcat', password='howbuy2015')
        return tran

    def sftp_put(self, local_path, remote_path):

        sftp = paramiko.SFTPClient.from_transport(self.ssh_connect())

        try:
            sftp.put(local_path, remote_path)
        except Exception as e:
            print("Put file {} 失败, {}".format(local_path, repr(e)))
            pass
        else:
            print("Put file {} 成功!".format(local_path))

    def ssh_exec(self, cmd):
        ssh = paramiko.SSHClient()
        ssh._transport = self.ssh_connect()
        try:
            _, stdout, stderr = ssh.exec_command(cmd)
        except Exception as e:
            print(e)
            pass
        else:
            print('stderr\n', stderr.read().decode())
            print('stdout:\n', stdout.read().decode())

    def close(self):
        self.ssh_connect().close()

    def tms_mock_put(self):
        """
        将本地部署包上传到指定的应用服务器
        """
        web_remote_dir = '/usr/local/tomcat-tms-mock-web/webapps/tms-mock-web'
        webservice_remote_dir = '/usr/local/tomcat-tms-mock-web/webapps/ROOT'
        app_remote_dir = '/data/app/howbuy-tms-mock-remote'

        if 'tms-mock-web' == self.app_name:
            self.ssh_exec('rm -rf {}/*'.format(web_remote_dir))
            self.sftp_put(self.pre_package(), '{0}/{1}'.format(web_remote_dir, self.pre_package()))
            self.ssh_exec('tar xvf {0}/{1}'.format(web_remote_dir, self.pre_package()))

        if 'tms-mock-webservice' == self.app_name:
            self.ssh_exec('rm -rf {}/*'.format(web_remote_dir))
            self.sftp_put(self.pre_package(), '{0}/{1}'.format(webservice_remote_dir, self.pre_package()))
            self.ssh_exec('tar xvf {0}/{1}'.format(webservice_remote_dir, self.pre_package()))
            
        if 'tms-mock-remote' == self.app_name:
            self.ssh_exec('rm -rf {}/*'.format(app_remote_dir))
            self.sftp_put(self.pre_package(), '{0}/{1}'.format(app_remote_dir, self.pre_package()))
            self.ssh_exec('tar xvf {0}/{1}'.format(app_remote_dir, self.pre_package()))

        self.close()


if __name__ == '__main__':

    """
    workspace: job空间
    app_name：应用名称
    tms_ip： 部署环境IP
    remove_providers: 需要移除的服务
    mock_svn_url： mock svn path
    """
    workspace = r'F:\svn\test'
    app_name = 'tms-mock-remote'
    tms_ip = '192.168.221.123'
    remove_providers = ''
    mock_svn_url = 'trunk'

    print("job请求参数：", sys.argv)
    mockd = MockDeploy(workspace, app_name, tms_ip, remove_providers, mock_svn_url)
    mockd.execute()

