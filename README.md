# Transaction Simulation

## Table of Contents
- [Description](#description)
- [Features](#features)
- [Tools Used](#tools-used)
- [Setup Instructions](#setup-instructions)
- [Database Setup](#database-setup)
- [Running the Project](#running-the-project)
- [Redis Usage](#redis-usage)
- [Database Indexes](#database-indexes)
- [Throttle Rate Limits](#throttle-rate-limits)
- [API Endpoints](#api-endpoints)
- [Author](#author)

---

## Description

The aim of the project is to build a transaction simulation API that authenticates users, enables users to transact, view balances, and retrieve transaction history.

---

## Features

- Admin dashboard to view lists of users and transactions, blacklist tokens
- Redis for cache management of transactions
- Throttler to limit sign up and login attempts and pagination

---

## Tools Used

| Tool         | Description                       | Tags                                      |
| ------------ | --------------------------------- | ------------------------------------------ |
| GitHub       | Version Control                   | [Version-Control], [Repo]                  |
| Django       | Python Based Backend Framework    | [python], [Django]                         |
| PostgreSQL   | Relational Database               | [Relational Integrity], [Database]         |
| Virtualenv   | Python Environment Manager        | [Virtual Environment], [Dependency]        |
| Redis        | In-memory Cache Manager           | [Cache Manager]                            |

---

## Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/andrewindeche/transactionsimulation.git
```
Or download the ZIP file from GitHub and unzip it.

### 2. Create and Activate Virtual Environment

```bash
python3.13 -m venv virtual
source virtual/bin/activate
```

### 3. Install Dependencies

Navigate to your Django project directory and install dependencies:

```bash
pip3 install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the Django root folder. Use `env.example` as a guide for required variables.

---

## Database Setup

Set up your PostgreSQL database:

```sql
CREATE DATABASE database;
CREATE USER newuser WITH PASSWORD 'newpassword';
GRANT ALL PRIVILEGES ON DATABASE database TO newuser;
```

---

## Running the Project

### 1. Migrate the Database

```bash
python3 manage.py migrate
```

### 2. Create a Superuser

```bash
python3 manage.py createsuperuser
```

### 3. Start the Development Server

```bash
python3 manage.py runserver
```

Access the server at: [http://localhost:8000/](http://localhost:8000/)

---

## Redis Usage

Start the Redis CLI:

```bash
redis-cli
```

Check for cached keys:

```bash
KEYS transaction_history_*
```

Inspect cached data:

```bash
GET transaction_history_123
```

---

## Database Indexes

To optimize database queries, apply the following indexes:

```sql
-- Speed up queries filtering/joining Transaction by user
CREATE INDEX idx_transaction_user ON transactions_transaction(user_id);

-- Improve speed for queries filtering by transaction_type
CREATE INDEX idx_transaction_type ON transactions_transaction(transaction_type);

-- Speed up queries filtering by user's email address
CREATE INDEX idx_user_email ON transactions_user(email);
```

---

## Throttle Rate Limits

API calls are limited as follows:

- Anonymous: `40/day`
- User: `40/day`
- Login: `50/minute`
- Signup: `60/minute`

---

## API Endpoints

### 1. Sign Up

**POST** `http://localhost:8000/api/register/`

Example payload:
```json
{
    "username": "paul",
    "email": "paul@abc.com",
    "first_name": "Paul",
    "last_name": "Walker",
    "password": "Complexpasword#"
}
```

### 2. Login

**POST** `http://localhost:8000/api/login/`

Example payload:
```json
{
    "username_or_email": "username",
    "password": "Password35$"
}
```

### 3. Refresh Token

**POST** `http://localhost:8000/api/token/refresh/`

Example payload:
```json
{
    "token": "TOKEN-ABC"
}
```

### 4. Get Account Details

**GET** `http://localhost:8000/api/account/`

Headers: `Authorization: Bearer <your_jwt_access_token>`

All users start with a balance of `1000.0`.

### 5. Create a Transaction (Deposit/Withdrawal)

**POST** `http://localhost:8000/api/transaction/`

Deposit example:
```json
{
    "transaction_type": "deposit",
    "amount": 100.50
}
```

Withdrawal example:
```json
{
    "transaction_type": "withdrawal",
    "amount": 50.00
}
```

### 6. Get Transaction History

**GET** `http://localhost:8000/api/transactions/`

Headers: `Authorization: Bearer <your_jwt_access_token>`

---

## Author

Built by **Andrew Indeche**