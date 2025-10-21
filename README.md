# 🌞 Solaris Conexus — Blockchain-Enabled Solar Energy Management System

[![GitHub Repo](https://img.shields.io/badge/GitHub-trevor--gituru/solaris__conexus-blue?logo=github)](https://github.com/trevor-gituru/solaris_conexus)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

> A **blockchain-integrated solar energy management and communication system** that enables real-time monitoring, peer-to-peer energy trading, and transparent token-based incentives for small-scale producers.

---

## 🧭 Overview

**Solaris Conexus** is a decentralized solar energy management system designed to address transparency, incentive, and communication inefficiencies in Kenya’s renewable energy sector.
It integrates **blockchain technology (Starknet Cairo smart contract)**, **IoT hardware (Arduino)**, and **hybrid backend systems (FastAPI + MQTT + Next.js)** to enable:

* **Real-time solar power monitoring**
* **Peer-to-peer power trading**
* **Tokenized incentives for surplus producers**
* **Secure blockchain-backed data integrity**

The system promotes **energy equity and sustainability**, supporting **Kenya’s Vision 2030 clean energy goals**.

---

## ⚙️ System Architecture

The project comprises **five interconnected modules**:

### 1. 🧩 `arduino/`

Contains Arduino microcontroller code for:

* Measuring **current, voltage, and power** via sensors
* Displaying status on **LCD**
* Handling **keypad input** for local control
* Communicating with estate backend via **serial/MQTT**

### 2. 🌐 `frontend-central/`

The **Next.js + Tailwind CSS** web interface that allows users to:

* Authenticate and view **profiles**
* Monitor **live power usage and balances**
* **Buy tokens**, create and accept **trade requests**
* Manage **devices** linked to their house

### 3. 🛠️ `backend-central/`

The **FastAPI** server that forms the core communication and data layer.
Responsibilities:

* Interacts with the **Starknet blockchain**
* Handles **token minting, trading, and transfers**
* Exposes **REST APIs** for frontend and estate backend
* Persists state using **SQLAlchemy ORM**

### 4. 🏘️ `estate-backend/`

A local server that bridges IoT devices and blockchain backend.
Features:

* Uses **MQTT** for device communication
* Relays readings and instructions between Arduino and backend-central
* Manages **device registration** and **estate-level control**

### 5. 🔗 `solaris_conexus_token/`

Smart contract written in **Cairo** for **Starknet**, implementing:

* **Solaris Conexus Token (SCT)** — a tradable power token
* Minting logic for producers
* Transfer and trade lifecycle management
* Transparent on-chain energy accounting

---

## 🧱 Project Structure

```bash
solaris_conexus/
├── .git/                   # Git version control
├── .gitignore              # Git ignore file
├── arduino/                # Arduino microcontroller code
├── backend-central/        # Central backend (FastAPI + SQLAlchemy)
├── estate-backend/         # Estate-level MQTT backend
├── frontend-central/       # Frontend web app (Next.js + Tailwind)
├── solaris_conexus_token/  # Cairo smart contract (Starknet)
├── resources/              # Additional project documentation
├── project-setup.md        # Development setup notes
└── README.md               # You are here
```

---

## 🚀 Features

| Feature                             | Description                                                |
| ----------------------------------- | ---------------------------------------------------------- |
| 🔋 **Real-time Energy Monitoring**  | Tracks live power consumption and production per house     |
| 🪙 **Tokenized Rewards (SCT)**      | Generates and transfers tokens based on surplus energy     |
| 🤝 **Peer-to-Peer Energy Trading**  | Users can sell or buy tokens directly                      |
| 🔗 **Blockchain Transparency**      | Immutable, decentralized record of all energy transactions |
| 📶 **Hybrid Communication Network** | Arduino ↔ MQTT ↔ Backend ↔ Blockchain ↔ Web UI             |
| 🧠 **Smart Automation**             | Controls load and optimizes energy use via device logic    |

---

## 🧰 Tech Stack

**Hardware:**

* Arduino Uno
* ACS712 Current Sensor
* LCD Display
* Keypad
* MOSFETs + DC converters
* MQTT communication module

**Software & Frameworks:**

* **Backend:** FastAPI, SQLAlchemy, MQTT, Python 3.11
* **Frontend:** Next.js, React, Tailwind CSS, AOS, Braavos Wallet
* **Smart Contract:** Cairo (Starknet Sepolia)
* **Database:** PostgreSQL
* **Communication Protocol:** MQTT

---

## 🧑‍💻 Getting Started

To get started with a specific part of the project (e.g., frontend, backend), please refer to the `README.md` file located in the corresponding sub-directory.

Each submodule contains detailed instructions for setup, installation, and running the application.

-   [`arduino/README.md`](./arduino/README.md)
-   [`backend-central/README.md`](./backend-central/README.md)
-   [`estate-backend/README.md`](./estate-backend/README.md)
-   [`frontend-central/README.md`](./frontend-central/README.md)
-   [`solaris_conexus_token/README.md`](./solaris_conexus_token/README.md)

---

## 📊 System Flow

```
[ Arduino Sensors ] 
       ↓
 [ Estate Backend (MQTT) ]
       ↓
 [ Central Backend (FastAPI + Starknet) ]
       ↓
 [ Smart Contract (SolarisConexusToken) ]
       ↓
 [ Web Frontend (Next.js) ]
```

---

## 📸 Screenshots (from Report)

* Dashboard overview
* Power Token purchase interface
* Trade history logs
* Device registration panel
* Braavos wallet integration

*(See `/resources/` for project documentation and figures.)*

---

## 🧾 Research Context

This project was developed as part of the **Bachelor of Science in Telecommunication and Information Engineering** at **Jomo Kenyatta University of Agriculture and Technology (JKUAT)** by:

* **Trevor Muriuki Gituru – ENE221-0095/2019**
* **Michael Murage Ndegwa – ENE221-0094/2020**
* **Supervisor:** Dr. Lawrence Ngugi

📘 Full documentation:

* `resources/Final Report.docx`
* `resources/Project Report on Blockchain Enabled Communication System.docx`

---

## 🌍 Impact

* Promotes **clean and decentralized energy access**
* Provides **financial incentives** for small producers
* Demonstrates a **scalable model** for blockchain-based smart grids
* Aligns with **Kenya’s Vision 2030** sustainability agenda

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).

---

## 📫 Contact

**Author:** Trevor Muriuki Gituru
📧 [giturutrevor@gmail.com](mailto:giturutrevor@gmail.com)
🌐 [solaris.razaoul.xyz](https://solaris.razaoul.xyz)
