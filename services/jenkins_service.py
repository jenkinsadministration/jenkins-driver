import jenkins
from jenkins import Jenkins
from jinja2 import FileSystemLoader, Environment, select_autoescape
import json

from libs.constans import OS_iOS, OS_Android
from libs.ios import IOS


def get_job_label(job_configuration):
    if job_configuration['type'] == 'TEST':
        if job_configuration['platform'] == 'ANDROID':
            return 'TEST_ANDROID'


def get_global_environment_vars(environment_var):
    return ''


class JenkinsService:
    # initializing the variables
    server: Jenkins = None
    template_env = None

    # defining constructor
    def __init__(self, server):
        self.server = server
        file_loader = FileSystemLoader('templates')
        self.template_env = Environment(loader=file_loader, autoescape=select_autoescape(['xml']))

    # defining class methods
    def create_folder(self, folder_name, silent=False):
        if not silent:
            print(" - Creating folder %s ..." % folder_name)
        with open('templates/folder_config.xml', 'r') as file:
            try:
                self.server.create_job(folder_name, file.read())
            except jenkins.JenkinsException:
                if not silent:
                    print("   Folder %s already exists" % folder_name)

    def create_test_job(self, job_name, setup, label, platform, browser, update_if_exists=True):
        repository = setup['repository']
        branch = setup['branch']
        cron = setup['cron']
        log_rotate = int(setup['log_rotate'])
        template_name = setup['template']
        if 'parameters' in setup:
            parameters = setup['parameters']
        else:
            parameters = []
        if 'athenea_project' in setup:
            athenea = setup['athenea_project']
        else:
            athenea = None
        android_home = get_global_environment_vars('ANDROID_HOME')
        maven_params = ''

        if platform == 'Web':
            platform = 'REMOTEWD'

        maven_params += ' -DDRIVER=' + platform.upper()
        maven_params += ' -DBROWSER=' + browser.upper()

        for p in parameters:
            if p['is_maven_param']:
                if p['is_parameterizable']:
                    maven_params += " -D%s=\'${params.%s}\'" % (p['maven_key'], p['name'])
                else:
                    maven_params += " -D%s=\'%s\'" % (p['maven_key'], p['default_value'])

        template = self.template_env.get_template(template_name)

        job_config = template.render(
            repository=repository,
            branch=branch,
            cron=cron,
            log_rotate=log_rotate,
            parameters=parameters,
            label=label,
            maven_params=maven_params,
            android_home=android_home,
            athenea=athenea
        )

        self.create_folder_path(job_name)

        try:
            self.server.create_job(job_name, job_config)
            print(" - Job «%s» was created successfully" % job_name)
        except jenkins.JenkinsException:
            if update_if_exists:
                self.server.reconfig_job(job_name, job_config)
                print(" - Job «%s» was updated successfully" % job_name)
            else:
                print("   The job «%s» already exists" % job_name)

    def create_build_job(self, job_name, setup, label, update_if_exists=True):
        repository = setup['repository']
        cron = setup['cron']
        log_rotate = int(setup['log_rotate'])
        template_name = setup['template']
        if 'parameters' in setup:
            parameters = setup['parameters']
        else:
            parameters = []
        if 'athenea_project' in setup:
            athenea = setup['athenea_project']
        else:
            athenea = None

        template = self.template_env.get_template(template_name)

        job_config = template.render(
            repository=repository,
            cron=cron,
            log_rotate=log_rotate,
            parameters=parameters,
            label=label,
            athenea=athenea
        )

        self.create_folder_path(job_name)

        try:
            self.server.create_job(job_name, job_config)
            print(" - Job «%s» was created successfully" % job_name)
        except jenkins.JenkinsException:
            if update_if_exists:
                self.server.reconfig_job(job_name, job_config)
                print(" - Job «%s» was updated successfully" % job_name)
            else:
                print("   The job «%s» already exists" % job_name)

    def create_folder_path(self, job_name):
        paths = job_name.split('/')

        base_path = ''

        for (i, p) in enumerate(paths[:-1]):
            if i < 1:
                base_path = p
            else:
                base_path += '/' + p

            self.create_folder(base_path, silent=True)
