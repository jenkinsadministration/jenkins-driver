stage('Slack Notification Starting') {
    steps {
        script {
            slackSend channel: '{{slack_channel}}', message: "Build ${env.JOB_NAME.replace('/', ' > ')} - #${env.BUILD_DISPLAY_NAME} started (&lt;${env.BUILD_URL}|Open>)", color: '#439FE0', botUser: true, teamDomain: 'deliveryhero', tokenCredentialId: 'SlackToken'
        }
    }
}