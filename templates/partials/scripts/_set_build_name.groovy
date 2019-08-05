stage('Set Build Name') {
    steps {
        script {
            currentBuild.displayName = "Build_" + "${BUILD_TIMESTAMP}"
        }
    }
}