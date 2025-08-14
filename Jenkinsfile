pipeline {
    agent {
        kubernetes {
            defaultContainer 'jnlp'
            yaml """
apiVersion: v1
kind: Pod
spec:
  serviceAccountName: jenkins
  containers:
  - name: docker
    image: docker:24.0.5-cli
    command:
    - cat
    tty: true
    volumeMounts:
    - name: docker-sock
      mountPath: /var/run/docker.sock
  - name: kubectl
    image: bitnami/kubectl:latest
    command:
    - cat
    tty: true
    securityContext:
      runAsUser: 1000
  - name: helm
    image: alpine/helm:3.13.2
    command:
    - /bin/sh
    tty: true
  - name: psql
    image: bitnami/postgresql:16
    command:
    - /bin/bash
    tty: true
    securityContext:
      runAsUser: 1000
  - name: curl
    image: curlimages/curl:8.6.0
    command:
    - /bin/sh
    tty: true
    securityContext:
      runAsUser: 1000
  volumes:
  - name: docker-sock
    hostPath:
      path: /var/run/docker.sock   
"""
        }
    }
    environment {
        LOGIN_EMAIL = 'rabie.moohamed@gmail.com'
        PSQL_HOST = 'db.jenkins.svc.cluster.local'
        PSQL_PORT = '5432'
        RMQ_HOST = 'rabbitmq.jenkins.svc.cluster.local'
        RMQ_PORT = '15672'
        // Add additional static envs here if needed
    }
    stages {
        stage('Inject Credentials') {
            steps {
                withCredentials([
                    usernamePassword(credentialsId: 'psql-user', usernameVariable: 'PSQL_USER', passwordVariable: 'PSQL_PASS'),
                    usernamePassword(credentialsId: 'rabbitmq-user', usernameVariable: 'RMQ_USER', passwordVariable: 'RMQ_PASS')
                ]) {
                    script {
                        env.PSQL_USER = env.PSQL_USER
                        env.PSQL_PASS = env.PSQL_PASS
                        env.RMQ_USER = env.RMQ_USER
                        env.RMQ_PASS = env.RMQ_PASS
                    }
                }
            }
        }
        stage('Checkout') {
            steps {
                git url: 'https://github.com/rabie01/kubernates-microservices-python.git', branch: 'feature/return-mp3-fid-on-upload'
            }
        }
        stage('Helm Install Charts') {
            steps {
                container('helm') {
                    script {
                        sh 'helm version'
                        sh 'helm upgrade --install postgres ./Helm_charts/Postgres --namespace jenkins --create-namespace'
                        sh 'helm upgrade --install mongodb ./Helm_charts/MongoDB --namespace jenkins --create-namespace'
                        sh 'helm upgrade --install rabbitmq ./Helm_charts/RabbitMQ --namespace jenkins --create-namespace'
                    }
                }
            }
        }
        stage('Wait for Postgres') {
            steps {
                container('psql') {
                    sh '''
                    set +e
                    echo "Testing DNS and connectivity:"
                    getent hosts $PSQL_HOST || (echo "❌ DNS failed"; exit 1)
                    nc -vz $PSQL_HOST $PSQL_PORT || echo "nc failed (but may require busybox or netcat installed)"
                    echo "PG_HOST=$PSQL_HOST, PG_PORT=$PSQL_PORT, PG_USER=$PSQL_USER"
                    for i in {1..20}; do
                      if pg_isready -h $PSQL_HOST -p $PSQL_PORT -U $PSQL_USER -d authdb; then
                        echo "✅ PostgreSQL is ready!"
                        exit 0
                      fi
                      echo "Waiting for PostgreSQL..."
                      sleep 5
                    done
                    echo "❌ PostgreSQL did not become ready in time."
                    exit 1
                    '''
                }
            }
        }
        stage('Postgres Init SQL') {
            steps {
                container('psql') {
                    sh 'PGPASSWORD=$PSQL_PASS psql -h $PSQL_HOST -p $PSQL_PORT -U $PSQL_USER -d authdb -f ./Helm_charts/Postgres/init.sql'
                }
            }
        }
        stage('Wait for RabbitMQ') {
            steps {
                container('curl') {
                    sh '''
                    for i in {1..20}; do
                      if curl -u $RMQ_USER:$RMQ_PASS -s http://$RMQ_HOST:$RMQ_PORT/api/overview > /dev/null; then
                        echo "✅ RabbitMQ is ready!"
                        exit 0
                      fi
                      echo "Waiting for RabbitMQ..."
                      sleep 5
                    done
                    echo "❌ RabbitMQ not ready"
                    exit 1
                    '''
                }
            }
        }
        stage('RabbitMQ Create Queues') {
            steps {
                container('curl') {
                    sh '''
                    curl -u $RMQ_USER:$RMQ_PASS -X PUT -H "content-type:application/json" http://$RMQ_HOST:$RMQ_PORT/api/queues/%2f/video -d '{"durable":true}'
                    curl -u $RMQ_USER:$RMQ_PASS -X PUT -H "content-type:application/json" http://$RMQ_HOST:$RMQ_PORT/api/queues/%2f/mp3 -d '{"durable":true}'
                    '''
                }
            }
        }
        stage('Build and Push Docker Images') {
            steps {
            container('docker') {
            withCredentials([usernamePassword(credentialsId: 'docker-hub-credentials', usernameVariable: 'DOCKER_USERNAME', passwordVariable: 'DOCKER_PASSWORD')]) {
                script {
                    sh 'echo $DOCKER_PASSWORD | docker login -u $DOCKER_USERNAME --password-stdin'
                    def services = ['auth', 'converter', 'gateway', 'notification']
                    for (svc in services) {
                        def image = "${DOCKER_USERNAME}/${svc}:latest"
                        dir("src/${svc}-service") {
                            sh "docker build -t ${image} ."
                            sh "docker push ${image}"
                        }
                    }
                }
            }
        }
    }
}
        stage('Deploy to Kubernetes') {
            steps {
                container('kubectl') {
                    script {
                        def manifests = [
                            'src/auth-service/manifest',
                            'src/converter-service/manifest',
                            'src/gateway-service/manifest',
                            'src/notification-service/manifest'
                        ]
                        for (m in manifests) {
                            sh "kubectl apply -f ${m}"
                        }
                    }
                }
            }
        }
    }
}
