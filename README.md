# DNS Monitor SaaS

A DNS monitoring SaaS platform that tracks domain record changes, stores historical data, and provides a real-time dashboard for visibility and analysis.

## Overview

This project is designed to help users monitor DNS records and detect changes over time. It simulates a SaaS-style architecture with a backend API, data storage, and a frontend dashboard for visualization.

The system continuously checks DNS records, logs changes, and allows users to view historical activity through a clean interface.

## Features

- Monitor DNS records (A, CNAME, MX, etc.)
- Detect and log changes over time
- Store historical DNS data
- REST API for data access
- Dashboard for viewing records and changes
- Background task processing for periodic checks

## Tech Stack

### Backend
- FastAPI (Python)
- SQL (database for storing records & history)

### Frontend
- React

### Other Tools
- REST APIs
- Git & Version Control

## How It Works

1. A domain is added to the system
2. The backend periodically checks DNS records
3. Any changes are detected and stored in the database
4. The frontend dashboard displays:
   - Current DNS state
   - Historical changes
   - Monitoring insights

## Project Structure
backend/ → FastAPI application, API routes, DNS logic
frontend/ → React dashboard


## Getting Started

### Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```
###  Frontend

```bash

cd frontend
npm install
npm run dev
```
Future Improvements
Multi-tenant support (SaaS users & accounts)
Authentication & authorization (JWT)
Alert system (email/SMS on DNS changes)
Deployment (Docker + cloud hosting)
Performance optimization & caching

Author
Elisha Gilbert
Email: elishagilbert60@gmail.com
