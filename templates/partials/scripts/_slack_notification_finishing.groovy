stage('Slack Notification Finishing') {
    steps {
        script {
            def status = ""
            def color = ""
            if(build_ok) {
                status = "success"
                color = "good"
            } else {
                status = "failed"
                color = "danger"
            }
            slackSend channel: '{{slack_channel}}', message: "Build ${env.JOB_NAME.replace('/', ' > ')} - #${env.BUILD_DISPLAY_NAME} was ${status} after ${currentBuild.durationString.replace(' and counting', '')} (&lt;${env.BUILD_URL}|Open>)", color: "${color}", botUser: true, teamDomain: 'deliveryhero', tokenCredentialId: 'SlackToken'
        }
    }
}