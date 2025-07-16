# 🎧 Microservices Video-to-Audio Converter

[![Build Status](https://img.shields.io/badge/build-passing-brightgreen?style=flat-square)](#)
[![Kind](https://img.shields.io/badge/k8s-kind-blue?style=flat-square&logo=kubernetes)](#)
[![Helm](https://img.shields.io/badge/helm-ready-0f6ab4?style=flat-square&logo=helm)](#)
[![Taskfile](https://img.shields.io/badge/taskfile-powered-239120?style=flat-square&logo=task)](https://taskfile.dev)
[![Docker](https://img.shields.io/badge/docker-ready-2496ED?style=flat-square&logo=docker)](#)
[![RabbitMQ](https://img.shields.io/badge/RabbitMQ-ready-ff6600?style=flat-square&logo=rabbitmq)](#)
[![MongoDB](https://img.shields.io/badge/MongoDB-ready-47A248?style=flat-square&logo=mongodb)](#)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-ready-336791?style=flat-square&logo=postgresql)](#)
[![API Ready](https://img.shields.io/badge/API-Tested-green?style=flat-square)](#)

---

## 🧩 Overview
📺 Demo Video: Deploy Microservices to Kubernetes KIND Cluster   
[![Watch the video](https://img.youtube.com/vi/TnwbY3FMGg8/0.jpg)](https://www.youtube.com/watch?v=TnwbY3FMGg8)

This project demonstrates a complete **microservices-based video-to-audio converter** built using:

- Kubernetes (Kind)
- Helm Charts
- RabbitMQ
- PostgreSQL & MongoDB
- Taskfile for automation
- Python microservices

The system converts uploaded MP4 videos into MP3 audio and emails the result using a decoupled architecture with queues.

---

## 🧰 Devbox Environment

[Devbox](https://www.jetpack.io/devbox/) simplifies your development environment using Nix. A `devbox.json` is included to help automate setup.

### 🔧 Why Devbox?

- Reproducible local development
- No manual installation of tools
- Easy provisioning on WSL or new systems

### 📦 Installed Packages

- `kubectl`, `kind`, `helm`, `task`
- `python311`, `pip`, `jq`, `curl`, `zip`, `git`
- `mongosh`, `psql`, and more

### 🐧 Install on WSL

```bash
curl -fsSL https://get.jetpack.io/devbox | bash
cd your-project-directory/
devbox shell
```

> Add more tools via `devbox add <tool>`.

---

## 🛠️ Taskfile: Automation Made Easy

**Taskfile** is a YAML-based task runner like `Makefile`, used here to automate:

- Cluster creation
- Helm chart installs
- Microservice deployment
- API testing

### 🔧 Install Task

```bash
# macOS
brew install go-task/tap/go-task

# Linux
sh -c "$(curl --location https://taskfile.dev/install.sh)" -- -d
```

### 💡 Common Commands

```bash
task kind:01-create-cluster
task helm:install-all
task svc:install-all
task api:test-all
```

Located in:

```
kind-installation-and-setup/
Helm_charts/
src/
```

---

## 🧱 KIND Cluster Overview

This project runs locally on a **KIND (Kubernetes IN Docker)** cluster with a custom configuration to support service exposure, Helm deployments, and local development.   

Kind lets you spin up a full Kubernetes cluster inside Docker containers — no need for cloud services or VMs.  

If running on windows, make sure Docker Desktop  is installed.  

### 🗺️ Cluster Nodes

```text
kind-control-plane
kind-worker
kind-worker2
kind-worker3
```

Check:

```bash
kubectl get nodes -o wide
```

### ⚙️ Cluster Creation

Config: `kind-installation-and-setup/kind-config.yaml`

```bash
kind create cluster or
task kind:01-create-cluster
```

This command:

Pulls a lightweight Kubernetes Docker image from docker hub

Starts a control plane node (as a Docker container)

Sets up kubectl context to point to the new cluster

### 🌐 Exposed Ports

| Service             | Container | NodePort | Purpose                                |
|---------------------|-----------|----------|----------------------------------------|
| API Gateway         | 5000      | 30002    | Login, upload, download endpoints      |
| PostgreSQL          | 5432      | 30003    | Used internally by auth-server         |
| RabbitMQ Mgmt UI    | 15672     | 30004    | Debug queue processing                 |
| MongoDB             | 27017     | 30005    | File storage via GridFS                |

> Exposing services allows local tools (e.g., curl, browsers, psql) to communicate directly for testing/debugging.

---

## ⚡ Quickstart in 4 Commands

```bash
cd kind-installation-and-setup/
task kind:01-create-cluster

cd ../Helm_charts/
task helm:install-all

cd ../src/
task svc:install-all

task api:test-all
```

Update `.env` before running.

---

## 🏗️ Architecture

<p align="center">
  <img src="./Project documentation/ProjectArchitecture.png" width="600" alt="Architecture">
</p>

---

## 📂 Directory Structure

```text
.
├── kind-installation-and-setup/
│   ├── kind-config.yaml
│   └── Taskfile.yml
├── Helm_charts/
│   ├── Postgres/
│   ├── MongoDB/
│   ├── RabbitMQ/
│   └── Taskfile.yml
├── src/
│   ├── auth/
│   ├── gateway/
│   ├── converter/
│   ├── notification/
│   ├── assets/
│   └── Taskfile.yml
├── .env
```

---

## 🧩 Microservice Components

| Name               | Role                                   |
|--------------------|----------------------------------------|
| `auth-server`      | JWT login auth                         |
| `gateway-server`   | API Gateway for user interaction       |
| `converter-module` | Converts MP4 to MP3 using RabbitMQ     |
| `notification`     | Sends email with MP3 file ID           |
| `RabbitMQ`         | Message broker                         |
| `MongoDB`          | Stores files via GridFS                |
| `PostgreSQL`       | Stores users, sessions                 |

---

## 🔑 API Usage

### Login

```bash
curl -X POST http://localhost:30002/login -u email:password
```

### Upload

```bash
curl -X POST -F 'file=@./video.mp4' -H "Authorization: Bearer <TOKEN>" http://localhost:30002/upload
```

### Download

```bash
curl -o audio.mp3 -H "Authorization: Bearer <TOKEN>" "http://localhost:30002/download?fid=<id>"
```

---

## 📧 Email Notification Setup

Configure Gmail via:

1. Enable 2FA
2. Create App Password
3. Add credentials to `src/notification/manifest/secret.yaml`

---

## 🛠️ Helm Usage

Modify values under:

```text
Helm_charts/*/values.yaml
```

Services:

- PostgreSQL
- MongoDB
- RabbitMQ

---

## 🔁 Taskfile Commands Reference

```bash
task api:login
task api:upload
task api:download -- FILE_ID=<id>
```

---

## 🧼 Clean Up

```bash
cd kind-installation-and-setup/
task kind:04-delete-cluster
```

---

## 🙌 Acknowledgements

Based on: [@N4si/microservices-python-app](https://github.com/N4si/microservices-python-app)

Enhancements by Rabie:

- KIND support
- Taskfile automation
- Devbox env setup
- Helm-based provisioning
- Improved testing
- Documentation

---

## 📮 Contact

Built with ❤️ by **Rabie Rabie**  
📧 [rabeea2100@yahoo.com](mailto:rabeea2100@yahoo.com)  
🔗 [myresume.rabietech.dpdns.org](https://myresume.rabietech.dpdns.org)  
🐙 [GitHub Profile](https://github.com/rabie01)

Open an issue or PR to contribute!
