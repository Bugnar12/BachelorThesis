# Automated Phishing Detection in Emails Using Artificial Intelligence

This repository contains the implementation of my Bachelor’s thesis, which focuses on building a **multi-layered automated system for phishing detection in emails**. The project integrates **machine learning and deep learning**, **real-time Gmail monitoring**, and **browser-side augmentation** to provide active and efficient defense against phishing attacks.

---

## 🎯 Project Aim

The main goal is to design and implement a **robust phishing detection architecture** capable of:
- **Real-time email analysis** using Gmail API push notifications.
- **Multi-layered classification** combining text, URL, and domain features.
- **AI-driven predictions** augmented with external threat intelligence.
- **Seamless user integration** via a web dashboard and browser extension.

---

## 🛠️ Architecture Overview

The system is structured in **three defense layers**:

1. **Text Analysis Layer**  
   - LSTM-based deep learning model for phishing vs. legitimate email classification.  
   - Preprocessing pipeline for cleaning, tokenization, embedding, and model evaluation.  
   - Metrics: accuracy, precision, confusion matrix, mock predictions.

2. **URL Analysis Layer**  
   - Transformer-based pretrained model ([`urlbert-tiny-v4-phishing-classifier`](https://huggingface.co/CrabInHoney/urlbert-tiny-v4-phishing-classifier)) integrated locally.  
   - Predicts phishing likelihood from URLs embedded in emails.

3. **Domain Scan Layer**  
   - VirusTotal API integration for static checks against known phishing/malicious domains.  
   - Final verdict follows a **prudent rule**: if any layer flags suspicious → the email is marked as phishing.

---

## ⚙️ Backend (Flask)

- Modular **Flask backend** with:
  - Gmail OAuth2 authentication.  
  - **Push-based Gmail inbox monitoring** (Pub/Sub) → no polling.  
  - Structured service layer (`EmailService`, `GmailService`).  
  - SQLAlchemy with **PostgreSQL database** for storing email data and predictions.  
  - REST endpoints for frontend consumption and manual text/URL analysis.  
  - JWT-based authentication with **refresh and access tokens**.

---

## 💻 Frontend (Angular)

- Angular application styled with **Angular Material**.  
- Features:
  - **Dashboard** with master-detail email viewer.  
  - **Pagination** for browsing scanned emails.  
  - **Manual analysis page** for testing custom text/URLs.  
  - Integration of VirusTotal verdicts into email details.  
  - Notifications via **Service Workers** and web push.  
  - Modernized UI with light Material theme.

---

## 🌐 Browser Extension

- Published Chrome extension that overlays detection verdicts directly within **Gmail’s web interface**.  
- Provides **inline phishing alerts** in real-time when new emails arrive.

---

## 📊 Models & Analysis

- **LSTM text classifier**:
  - TensorFlow, Adam optimizer, binary crossentropy loss.  
  - Early stopping with patience=5.  
  - Performance evaluation with accuracy, precision, recall, F1, and confusion matrix.  

- **Transformer URL classifier**:
  - Local Hugging Face model integration.  
  - Lightweight, fast inference for real-time scenarios.

- **VirusTotal integration**:
  - Domain verdict aggregation (legitimate / phishing).  
  - Combined with AI layers for conservative classification.

---

## 🔔 Real-Time Monitoring

- Gmail API push notifications → Flask Pub/Sub endpoint at `/gmail/notification`.  
- Emails processed through **feature extraction, classification, and storage**.  
- Push notifications trigger frontend updates + browser alerts.

---

## 🧪 Testing & Validation

- Benchmarked multiple AI models for phishing detection.  
- Tested **CI/CD integration with GitLab** for running automated tests.  
- Evaluated frontend/backend integration, push pipeline, and browser extension.  
- Designed test suites (smoke vs. regression) for functional validation.

---

## 🧩 Extra Features

- **Quiz module**: phishing awareness questions (single-choice, 4 options, easy/medium).  
- **VirusTotal UI reflection**: users can see AI + VT combined verdicts in the dashboard.  
- **Report generation** (planned): exportable detailed reports per email.

---

## 🚀 Contributions & Work Performed

- Designed and implemented a **full-stack phishing detection system**.  
- Integrated **AI/ML models** (LSTM, transformer) for phishing classification.  
- Developed **Flask backend** with Gmail API, JWT authentication, PostgreSQL persistence.  
- Built **Angular Material frontend** with dashboards, pagination, and master-detail views.  
- Created and published a **browser extension** for real-time Gmail phishing alerts.  
- Integrated **VirusTotal API** for external threat intelligence.  
- Implemented **push notification system** with service workers.  
- Conducted **benchmarking, testing, and validation** of ML models and system performance.  
- Documented architecture, testing, and results as part of the Bachelor’s thesis.

---
