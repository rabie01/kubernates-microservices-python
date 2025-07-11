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

---

## 🧩 Overview

This project demonstrates a complete **microservices-based video-to-audio converter** built using:

- Kubernetes (Kind)
- Helm Charts
- RabbitMQ
- PostgreSQL & MongoDB
- Taskfile for automation
- Python microservices

The system converts uploaded MP4 videos into MP3 audio and emails the result using a decoupled architecture with queues.

---

## 🧪 4-Command Quickstart

You can get the whole system up and running using just **four Taskfile commands**:

```bash
# 1️⃣ Create Kind cluster
cd kind-installation-and-setup/
task kind:01-create-cluster

# 2️⃣ Install Helm charts (Postgres, MongoDB, RabbitMQ, etc.)
cd ../Helm_charts/
task helm:install-all

# 3️⃣ Deploy microservices (auth, gateway, converter, notification)
cd ../src/
task svc:install-all

# 4️⃣ Run full API test flow (login → upload → download)
task api:test-all
```

> 📝 Make sure to update the `.env` file in each directory if needed.

---

## 🏗️ Architecture

<p align="center">
  <img src="./Project documentation/ProjectArchitecture.png" width="600" title="Architecture" alt="Architecture">
</p>

---

## 📂 Directory Structure

```text
.
├── kind-installation-and-setup/     # KIND cluster setup and configs
│   ├── kind-config.yaml
│   └── Taskfile.yml                 # kind:01-create-cluster
│
├── Helm_charts/                     # Helm charts for services
│   ├── Postgres/
│   ├── MongoDB/
│   ├── RabbitMQ/
│   └── Taskfile.yml                 # helm:install-all
│
├── src/                             # Source code and manifests
│   ├── auth/
│   ├── gateway/
│   ├── converter/
│   ├── notification/
│   ├── assets/                      # Uploaded MP4s / downloaded MP3s
│   ├── Taskfile.yml                 # svc:install-all, api:test-all
├── .env                             # ENV configuration
```

> **Note:**  
> Normally, `.env` should be added to `.gitignore` and an `env.example` used instead, but here it is included for easier testing and minimal setup.


---

## ⚙️ Components

| Microservice       | Description |
|--------------------|-------------|
| `auth-server`      | Issues JWT tokens via login |
| `gateway-server`   | Public API (login, upload, download) |
| `converter-module` | Converts MP4 → MP3 via RabbitMQ |
| `notification-server` | Sends email with file ID via RabbitMQ |
| `RabbitMQ`         | Queueing layer (`video` / `mp3` queues) |
| `MongoDB`          | Stores video/audio (via GridFS) |
| `PostgreSQL`       | Stores user data and login sessions |

---

## 🔑 API Endpoints

### 🔐 Login

```http
POST http://localhost:30002/login
```

```bash
curl -X POST http://localhost:30002/login -u <email>:<password>
```

Response: JWT Token

---

### ⬆️ Upload

```http
POST http://localhost:30002/upload
```

```bash
curl -X POST -F 'file=@./video.mp4'   -H "Authorization: Bearer <JWT Token>"   http://localhost:30002/upload
```

---

### ⬇️ Download

```http
GET http://localhost:30002/download?fid=<file_id>
```

```bash
curl --output video.mp3 -X GET   -H "Authorization: Bearer <JWT Token>"   "http://localhost:30002/download?fid=<file_id>"
```

📩 The file ID will be emailed to the user once processing is complete.

---

## 🛠️ Notification Email Configuration

To configure Gmail notifications for the `notification-server`:

1. Go to your Google Account → **Security**
2. Enable **2-Step Verification**
3. Under **App passwords**, create one for this app
4. Add the app password and your Gmail in:
   ```yaml
   src/notification/manifest/secret.yaml
   ```

---

## 📋 Additional Taskfile Commands

```bash
task api:login         # Get JWT and save to .jwt_token
task api:upload        # Upload video from ./assets
task api:download -- FILE_ID=<your_id>  # Download audio
task kind:04           # Destroys the KIND cluster
```

---

## 🧱 Helm Notes

Helm charts are used for:

- PostgreSQL
- MongoDB
- RabbitMQ (with automated queue creation)

You can configure their values via `Helm_charts/**/values.yaml`.

---

## 🧼 Destroy Infrastructure

```bash
cd kind-installation-and-setup
task kind:04-delete-cluster
```

---

## 🙏 Acknowledgements

This project is built on top of the excellent work by [@N4si](https://github.com/N4si).  
Original repository: [N4si/microservices-python-app](https://github.com/N4si/microservices-python-app)

### Modifications and Enhancements:

- Deployed using **KIND** (Kubernetes IN Docker)
- Fully automated setup using **Taskfile**
- Infrastructure provisioned via **Helm charts**
- Environment variables managed via `.env` files
- Improved testing flow with token handling and upload/download validation
- Structured directory layout and service manifests
- Complete documentation and usage examples

## 📮 Contact

Built with ❤️ by **Rabie Rabie**  
📧 [rabeea2100@yahoo.com](mailto:rabeea2100@yahoo.com)  
🔗 [myresume.rabietech.dpdns.org](https://myresume.rabietech.dpdns.org)  
🐙 [GitHub Profile](https://github.com/rabie01)

Open an issue or PR for contributions!
