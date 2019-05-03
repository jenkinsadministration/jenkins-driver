# -*- coding: utf-8 -*-
from libs.constans import BUILD_JOB
from services.jenkins_service import JenkinsService
from services.jenkins_service import get_job_label

import argparse
import base64
import jenkins
import json
import requests
import time


def set_scripts_parameters():
    parser = argparse.ArgumentParser(description='Process Jenkins parameters')

    parser.add_argument('--jenkins_url', metavar='jenkins_url', type=str,
                        help='Jenkins server url')

    parser.add_argument('--jenkins_user', metavar='jenkins_user', type=str,
                        help='Jenkins admin user')

    parser.add_argument('--jenkins_password', metavar='jenkins_password', type=str,
                        help='Jenkins admin password')

    return parser.parse_args()


def restart_server():
    url = args.jenkins_url + "/restart"

    auth_token = base64.b64encode(
        "%s:%s" % (args.jenkins_user, args.jenkins_password)
    )

    headers = {
        'Content-Type': "application/x-www-form-urlencoded",
        'Authorization': "Basic %s" % auth_token,
    }

    response = requests.request("POST", url, data='', headers=headers)


def get_jobs():
    resp = requests.get(
                url='https://us-central1-jenkinsadmin.cloudfunctions.net/jobs'
            )
            
    if resp.status_code != 200:
        raise Exception('Something gone wrong')

    return resp.json()


def get_plugins():
    data = {
        query: '{ plugins { data { name } } }'
    }

    resp = request.post(
            url='https://us-central1-jenkinsadmin.cloudfunctions.net/query/graphql',
            json=data
        )
    
    if resp.status_code != 200:
        raise Exception('Something gone wrong')

    return resp.json()['data']['plugins']


def main():

    args = set_scripts_parameters()

    server = jenkins.Jenkins(
        args.jenkins_url, 
        args.jenkins_user, 
        args.jenkins_password
    )

    print("Hello %s " % server.get_whoami()['fullName'])

    jenkins_service = JenkinsService(server)

    install_plugins = False

    if install_plugins:

        plugins = get_plugins()

        print('\nPreparing to install all the necessary plugins')

        for p in plugins:
            print(" - Installing plugin %s ..." % p)
            try:
                server.install_plugin(p['data']['name'], True)
            except IndexError:
                pass

        print('\nAll plugins were installed')

        print('\nRestarting server')

        restart_server()

        time.sleep(120)

        print('\nServer restarted')

    print('\nCreating jobs:')

    jobs = get_jobs()

    for job in jobs:
        if job['type'] == 'TEST':
            jenkins_service.create_test_job(
                job['full_name'],
                job['setup'],
                get_job_label(job),
                job['platform'],
                job['browser'],
                update_if_exists=True
            )
        elif job['type'] == 'BUILD':
            jenkins_service.create_build_job(
                job['full_name'],
                job['setup'],
                get_job_label(job),
                update_if_exists=True
            )

    print('\nAll jobs were created')

    print('\nConfiguration finished... enjoy your jenkins')


if __name__ == "__main__":
    main()
    