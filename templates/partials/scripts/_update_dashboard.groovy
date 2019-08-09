stage('Update Dashboard') {
    steps {
        script {
            try {
                httpRequest httpMode: 'GET', ignoreSslErrors: true, responseHandle: 'NONE', url: 'https://us-central1-atenea-33daf.cloudfunctions.net/api/notifications'
            } catch (exc) {}
        }
    }
}