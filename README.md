# Devops Project: video-converter

documentation is STILL UNDER DEVELOPMENT BUT YOU CAN CHECK Taskfile.yaml in kind-installation-and-setup, Helm_charts, src DIRS. ALSO MAKE SURE YOU MODIFY .env FOR YOUR ENV IF NEEDED

BASICALLY YOUSHOULD BE ABLE TO GET IT RUNNING BY ONLY 4 COMMANDS FORM 3 TASKFILES

  cd kind-installation-and-setup/
  t kind:01-create-cluster 
  cd ../Helm_charts/
  t helm:install-all 
  cd ../src/
  t svc:install-all 
  t api:test-all 



Converting mp4 videos to mp3 in a microservices architecture Using KIND CLUSTER.

## Architecture

<p align="center">
  <img src="./Project documentation/ProjectArchitecture.png" width="600" title="Architecture" alt="Architecture">
  </p>

## Deploying a Python-based Microservice Application on KIND CLUSTER

### Introduction

This document provides a step-by-step guide for deploying a Python-based microservice application on KIND cluster. The application comprises four major microservices: `auth-server`, `converter-module`, `database-server` (PostgreSQL and MongoDB), and `notification-server`.

### Prerequisites

Before you begin, ensure that the following prerequisites are met:
- check .env file and make sure you add your vars if need to change anything


### High Level Flow of Application Deployment

Follow these steps to deploy your microservice application:

1. **MongoDB and PostgreSQL Setup:** Create databases and enable automatic connections to them.

2. **RabbitMQ Deployment:** Deploy RabbitMQ for message queuing, which is required for the `converter-module`.

3. **Create Queues in RabbitMQ:** Before deploying the `converter-module`, create two queues in RabbitMQ: `mp3` and `video`.

4. **Deploy Microservices:**
   - **auth-server:** Navigate to the `auth-server` manifest folder and apply the configuration.
   - **gateway-server:** Deploy the `gateway-server`.
   - **converter-module:** Deploy the `converter-module`. Make sure to provide your email and password in `converter/manifest/secret.yaml`.
   - **notification-server:** Configure email for notifications and two-factor authentication (2FA).

5. **Application Validation:** Verify the status of all components by running:
   ```bash
   kubectl get all
   ```

6. **Destroying the Infrastructure** 


### Low Level Steps

#### Cluster Creation


Here are some essential Kubernetes commands for managing your deployment:


### 

# 🎧 Microservices Video-to-Audio Converter (Kubernetes + Helm + RabbitMQ + MongoDB + PostgreSQL)

This project demonstrates a complete microservices system that converts uploaded videos into MP3 audio using a cloud-native stack. It is fully containerized and deployed using **Kubernetes**, **Helm**, and **Kind**, with services communicating over **RabbitMQ** and persisting data in **MongoDB** and **PostgreSQL**.

---

## 🚀 Quickstart in 4 Commands

> This setup uses [Taskfile](https://taskfile.dev/) for orchestration. You only need 4 commands to get everything running!

### 🔧 Prerequisites

Make sure you have the following installed:

- [Docker](https://www.docker.com/)
- [Kind](https://kind.sigs.k8s.io/)
- [kubectl](https://kubernetes.io/docs/tasks/tools/)
- [Helm](https://helm.sh/)
- [Taskfile (Task)](https://taskfile.dev/)
- [jq](https://stedolan.github.io/jq/) (for parsing JSON in shell)
- `curl`

---

### 🧪 Start the System

```bash
# 1️⃣ Create Kubernetes cluster with Kind
cd kind-installation-and-setup/
task kind:01-create-cluster

# 2️⃣ Install Helm charts (PostgreSQL, MongoDB, RabbitMQ + wait and queues)
cd ../Helm_charts/
task helm:install-all

# 3️⃣ Deploy microservices (Auth, Gateway, Notification, Converter, etc.)
cd ../src/
task svc:install-all

# 4️⃣ Test full API flow (login → upload video → download MP3)
task api:test-all


API Gateway: Handles all client requests (login, upload, download)

Auth Service: Authenticates and returns JWT tokens

Converter: Reads from RabbitMQ "video" queue, processes MP4s → MP3

Notification: Listens to "mp3" queue, sends email with download ID

MongoDB: Stores video and audio files

PostgreSQL: Stores user credentials and login sessions

RabbitMQ: Manages messaging queues

📂 Directory Structure
.
├── kind-installation-and-setup/     # Kind cluster configuration
│   └── kind-config.yaml
│   └── Taskfile.yml                 # kind:01-create-cluster
│
├── Helm_charts/                     # Helm chart deployment
│   ├── Postgres/
│   ├── MongoDB/
│   ├── RabbitMQ/
│   └── Taskfile.yml                 # helm:install-all
│
├── src/                             # Source code and Kubernetes manifests
│   ├── gateway/
│   ├── auth/
│   ├── converter/
│   ├── notification/
│   ├── assets/                      # Uploaded MP4s and output MP3s
│   ├── Taskfile.yml                 # svc:install-all, api:test-all
│   └── .env                         # Configuration variables



🔑 API Endpoints
🔐 Login
POST http://localhost:30002/login
Authorization: Basic <email>:<password>

Response: JWT token


⬆️ Upload Video
POST http://localhost:30002/upload
Headers:
  Authorization: Bearer <JWT Token>
Form:
  file=@video.mp4

⬇️ Download Audio
GET http://localhost:30002/download?fid=<file_id>
Headers:
  Authorization: Bearer <JWT Token>
📨 Your email (used at login) will receive the MP3 file ID once ready.

🧪 Example Task Usage
task api:login      # Logs in and stores JWT in .jwt_token
task api:upload     # Uploads video.mp4 from ./assets
task api:download -- FILE_ID=<your_id>  # Downloads video.mp3 to ./assets

📋 Notes
JWT token is stored in .jwt_token after login

RabbitMQ queues (video, mp3) are auto-created by Taskfile after RabbitMQ chart is installed

MongoDB uses GridFS to store large binary files like video/audio

Emails are simulated in the logs (you can later plug in a real SMTP)


To install Charts, set the vars in `values.yaml`




### Notification Configuration



For configuring email notifications and two-factor authentication (2FA), follow these steps:

1. Go to your Gmail account and click on your profile.

2. Click on "Manage Your Google Account."

3. Navigate to the "Security" tab on the left side panel.

4. Enable "2-Step Verification."

5. Search for the application-specific passwords. You will find it in the settings.

6. Click on "Other" and provide your name.

7. Click on "Generate" and copy the generated password.

8. Paste this generated password in `notification-service/manifest/secret.yaml` along with your email.

Run the application through the following API calls:

# API Definition

- **Login Endpoint**
  ```http request
  POST http://nodeIP:30002/login
  ```

  ```console
  curl -X POST http://nodeIP:30002/login -u <email>:<password>
  ``` 
  Expected output: success!

- **Upload Endpoint**
  ```http request
  POST http://nodeIP:30002/upload
  ```

  ```console
   curl -X POST -F 'file=@./video.mp4' -H 'Authorization: Bearer <JWT Token>' http://nodeIP:30002/upload
  ``` 
  
  Check if you received the ID on your email.

- **Download Endpoint**
  ```http request
  GET http://nodeIP:30002/download?fid=<Generated file identifier>
  ```
  ```console
   curl --output video.mp3 -X GET -H 'Authorization: Bearer <JWT Token>' "http://nodeIP:30002/download?fid=<Generated fid>"
  ``` 

## Destroying the Infrastructure

cd kind-installation-and-setup
t kind:04


# 🎧 Microservices Video-to-Audio Converter

[![Build Status](https://img.shields.io/badge/build-passing-brightgreen?style=flat-square)](#)
[![Kind](https://img.shields.io/badge/k8s-kind-blue?style=flat-square&logo=kubernetes)](#)
[![Helm](https://img.shields.io/badge/helm-ready-0f6ab4?style=flat-square&logo=helm)](#)
[![Taskfile](https://img.shields.io/badge/taskfile-powered-239120?style=flat-square&logo=task)](https://taskfile.dev)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg?style=flat-square)](LICENSE)
[![Docker](https://img.shields.io/badge/docker-ready-2496ED?style=flat-square&logo=docker)](#)
[![RabbitMQ](https://img.shields.io/badge/RabbitMQ-ready-ff6600?style=flat-square&logo=rabbitmq)](#)
[![MongoDB](https://img.shields.io/badge/MongoDB-ready-47A248?style=flat-square&logo=mongodb)](#)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-ready-336791?style=flat-square&logo=postgresql)](#)
[![API Ready](https://img.shields.io/badge/API-Tested-green?style=flat-square)](#)


📮 Contact
Built by Rabie | [GitHub](https://github.com/rabie01)
For questions or contributions, feel free to open an issue or pull request.
