import jenkins
from jenkins import Jenkins
from jinja2 import FileSystemLoader, Environment, select_autoescape


def get_job_label(job_configuration):
    if job_configuration['type'] == 'TEST':
        if job_configuration['platform'] != job_configuration['browser'] :
            return "TEST_%s_%s" % (job_configuration['platform'], job_configuration['browser'])
        else:
            return "TEST_%s" % job_configuration['platform']
    else:
        return "BUILD_%s" % job_configuration['platform']


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
        slack_channel = setup['slack_channel']
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

        mvn_path = '/usr/bin/mvn'

        if platform == 'iPhone':
            mvn_path = '/usr/local/bin/mvn'

        show_parameters = False

        for p in parameters:
            if p['is_maven_param']:
                if p['is_parameterizable']:
                    maven_params += " -D%s=\'${params.%s}\'" % (p['maven_key'], p['name'])
                else:
                    maven_params += " -D%s=\'%s\'" % (p['maven_key'], p['default_value'])

            if p['is_parameterizable']:
                show_parameters = True

        has_custom_subscribers = len([d for d in parameters if d['name'] in ['Emails_To_Notify']]) > 0

        update_execution_details = len(
            [d for d in parameters if d['name'] in ['Reason_Of_Execution', 'Started_By']]
        ) > 0

        template = self.template_env.get_template(template_name)

        job_config = template.render(
            repository=repository,
            branch=branch,
            cron=cron,
            log_rotate=log_rotate,
            parameters=parameters,
            show_parameters=show_parameters,
            label=label,
            mvn_path=mvn_path,
            maven_params=maven_params,
            android_home=android_home,
            athenea=athenea,
            slack_channel=slack_channel,
            has_custom_subscribers=has_custom_subscribers,
            update_execution_details=update_execution_details
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

    def create_build_job(self, job_name, setup, label, iphone_udid, jenkins_url='http://192.168.19.34:8080', update_if_exists=True):
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

        show_parameters = False

        job_of_test = ''

        if 'job_of_test' in setup:
            job_of_test = setup['job_of_test']

        for p in parameters:
            if p['is_parameterizable']:
                show_parameters = True

        if not show_parameters:
            show_parameters = 'custom_branch' in template_name

        job_path = '/job/' + '/job/'.join(job_name.split('/'))

        template = self.template_env.get_template(template_name)

        job_config = template.render(
            repository=repository,
            branch=branch,
            cron=cron,
            log_rotate=log_rotate,
            parameters=parameters,
            job_path=job_path,
            label=label,
            athenea=athenea,
            show_parameters=show_parameters,
            job_of_test=job_of_test,
            jenkins_url=jenkins_url,
            iphone_udid=iphone_udid
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
