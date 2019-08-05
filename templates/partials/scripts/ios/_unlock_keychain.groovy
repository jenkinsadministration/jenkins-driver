stage('Unlock Keychain') {
    steps {
        sh "security unlock-keychain -p Automation01 ~/Library/Keychains/login.keychain"
    }
}