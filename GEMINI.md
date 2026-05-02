# MyShop: Django 5 E-commerce Project

This project is a comprehensive e-commerce application built with **Django 5**, following the curriculum of the book **"Django 5 By Example"** by Antonio Melé (starting from Chapter 9).

## Project Overview

MyShop is a functional online store with features including product catalog, session-based shopping cart, order management, and secure payment processing. It is designed for learning and demonstrates modern Django development patterns.

### Main Technologies
- **Backend:** Django 5.2.x (Python 3.x)
- **Database:** SQLite (Development default)
- **Asynchronous Tasks:** Celery with **RabbitMQ** as the broker
- **Payments:** Stripe integration
- **Email:** Django SMTP (configured for Gmail)
- **Media:** Pillow for product image management
- **Documentation/Learning:** NotebookLM integration for study notes

## Setup and Installation

### 1. Prerequisites
- Python 3.10+
- [RabbitMQ](https://www.rabbitmq.com/download.html) (running on `localhost:5672` with default `guest/guest` credentials)

### 2. Installation
```bash
# Clone the repository and navigate to the project root
# Create and activate a virtual environment
python -m venv env
source env/bin/activate  # On Windows: env\Scripts\activate

# Install dependencies (Note: file has a typo in original project)
pip install -r requiremets.txt
```

### 3. Database and Superuser
```bash
cd myshop/
python manage.py migrate
python manage.py createsuperuser
```

### 4. Environment Configuration
Create a `.env` file in the `myshop/` directory with the following variables:
```env
STRIPE_PUBLISHABLE_KEY=your_publishable_key
STRIPE_SECRET_KEY=your_secret_key
STRIPE_WEBHOOK_SECRET=your_webhook_secret
EMAIL_HOST_USER=your_gmail@gmail.com
EMAIL_HOST_PASSWORD=your_app_password
```

## Running the Project

### Django Development Server
```bash
cd myshop/
python manage.py runserver
```

### Celery Worker
Ensure RabbitMQ is running, then start the worker from the `myshop/` directory:
```bash
celery -A myshop worker -l info
```

### Celery Monitoring (Flower)
```bash
celery -A myshop flower
```

## Architecture

The project is structured into modular Django apps:

- **`shop/`**: Manages the product catalog (Categories and Products).
- **`cart/`**: Implements a session-based shopping cart. No database models; logic resides in `cart/cart.py`.
- **`orders/`**: Handles order creation and storage. Fires asynchronous tasks via Celery.
- **`payment/`**: Manages Stripe payment flow and webhooks.

## Development Conventions

### Learning & Documentation Workflow
The project includes a specialized learning loop:
1.  Study concepts from the "Django 5 By Example" book.
2.  Update `notes.md` with new learnings.
3.  Sync `notes.md` with **NotebookLM** using the `notebooklm-py` tool (ID: `d960d5ec-b62a-4174-a77d-9e79e0bf560b`).

### Testing
Always run tests before pushing changes:
```bash
# Run all tests
python manage.py test

# Run tests for a specific app
python manage.py test shop
```

## Key Files
- `myshop/myshop/settings.py`: Core configuration (Stripe, Celery, Email).
- `myshop/cart/cart.py`: Core logic for the shopping cart.
- `myshop/orders/tasks.py`: Asynchronous tasks for order notifications.
- `notes.md`: Shared study notes for NotebookLM.
