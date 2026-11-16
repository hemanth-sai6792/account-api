// Declarative pipeline for account-api.
// Jenkins checks GitHub every minute. If app code or data changed,
// it tests -> builds -> publishes -> deploys -> smoke tests,
// and rolls back automatically if the new version is unhealthy.

pipeline {
  agent any

  triggers {
    pollSCM('* * * * *')            // check the repo for new commits every minute
  }

  options {
    disableConcurrentBuilds()       // never run two deploys at the same time
    buildDiscarder(logRotator(numToKeepStr: '20'))
  }

  environment {
    IMAGE   = 'localhost:5001/account-api'   // local registry from docker-compose
    APP     = 'account-api'                  // container name of the running app
    NETWORK = 'cicd'                         // shared Docker network with Jenkins
  }

  stages {
    stage('Release') {
      // Only release when something that changes the running app was pushed.
      // A README-only commit is picked up but every stage below is skipped.
      when {
        anyOf {
          triggeredBy 'UserIdCause'           // a person clicked "Build Now"
          changeset 'app.py'
          changeset 'data/**'
          changeset 'requirements.txt'
          changeset 'Dockerfile'
        }
      }

      stages {
        stage('Version') {
          steps {
            script {
              env.SHORT_SHA = sh(script: 'git rev-parse --short HEAD', returnStdout: true).trim()
              env.TAG = "v${env.BUILD_NUMBER}-${env.SHORT_SHA}"
            }
            echo "Releasing ${env.IMAGE}:${env.TAG}"
          }
        }

        stage('Test') {
          steps {
            sh '''
              python3 -m venv .venv
              . .venv/bin/activate
              pip install -q -r requirements.txt
              pytest -q --junitxml=report.xml
            '''
          }
          post {
            always { junit 'report.xml' }     // test results show up in the Jenkins UI
          }
        }

        stage('Build') {
          steps {
            sh 'docker build --build-arg APP_VERSION=$TAG -t $IMAGE:$TAG .'
          }
        }

        stage('Publish') {
          steps {
            sh 'docker push $IMAGE:$TAG'
          }
        }

        stage('Deploy') {
          steps {
            script {
              // Remember what is running now, so we can roll back to it.
              env.PREV_IMAGE = sh(
                script: 'docker inspect -f "{{.Config.Image}}" $APP 2>/dev/null || true',
                returnStdout: true
              ).trim()
              env.DEPLOYED = 'true'
            }
            sh '''
              docker rm -f $APP 2>/dev/null || true
              docker run -d --name $APP --network $NETWORK -p 8081:5000 \
                --restart unless-stopped $IMAGE:$TAG
            '''
          }
        }

        stage('Smoke test') {
          steps {
            sh '''
              curl -fsS --retry 10 --retry-connrefused --retry-delay 1 http://$APP:5000/health
              curl -fsS http://$APP:5000/version | grep "$TAG"
              curl -fsS http://$APP:5000/accounts
            '''
          }
        }
      }
    }
  }

  post {
    failure {
      script {
        // Only roll back if we actually replaced the running app.
        if (env.DEPLOYED == 'true' && env.PREV_IMAGE) {
          echo "Smoke test failed. Rolling back to ${env.PREV_IMAGE}"
          sh '''
            docker rm -f $APP 2>/dev/null || true
            docker run -d --name $APP --network $NETWORK -p 8081:5000 \
              --restart unless-stopped $PREV_IMAGE
          '''
        }
      }
    }
    success {
      echo 'Live at http://localhost:8081/version'
    }
  }
}
