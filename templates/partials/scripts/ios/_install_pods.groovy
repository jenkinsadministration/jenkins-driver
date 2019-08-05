stage('Install Pods') {
    steps {
        script {
            try {
                sh "rm Podfile.lock"
                retry {
                    sh "export LANG=en_US.UTF-8 &amp;&amp; /usr/local/bin/pod repo update"
                }
                retry {
                    sh "export LANG=en_US.UTF-8 &amp;&amp; /usr/local/bin/pod install"
                }
            } catch (exc) {
                    currentBuild.result = 'FAILED'
                    build_ok = false
            }
        }
    }
}