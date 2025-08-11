# Expense Tracker App

A mobile-first, cross-platform expense tracking application designed to help users manage their personal finances effectively by tracking transactions, setting budgets, receiving alerts, and allocating funds to different categories.

---

## Features

- User registration, login, and secure authentication (JWT & refresh tokens)
- Link and manage multiple bank accounts via Account Aggregator framework
- Record and categorize transactions with UPI app, location, and merchant details
- Create and track budgets for different spending categories
- Set fund allocations (Fixed, Spend, Save) for better money management
- Real-time alerts and notifications for overspending and suspicious activities
- Push notifications support using Firebase Cloud Messaging (FCM)
- Audit logging for security and activity tracking

---

## Tech Stack

- **Frontend:** Cross-platform mobile framework (e.g., React Native or Flutter) *(To be decided)*
- **Backend:** FastAPI (Python)
- **Database:** PostgreSQL
- **Authentication:** JWT with refresh tokens
- **Notifications:** Firebase Cloud Messaging (FCM)
- **Deployment:** Cloud-based backend server *(Planned)*

---

## Getting Started

### Prerequisites

- Python 3.9+
- PostgreSQL
- Node.js and npm/yarn (if working on frontend)
- Firebase project setup for push notifications

### Installation

1. Clone the repository  
   ```bash
   git clone https://github.com/yourusername/expense-tracker.git
   cd expense-tracker

