# MOPDIC System

A comprehensive web application for managing events, news, projects, and media content.

## Features

- User authentication and authorization
- Event management
- News and articles
- Project portfolio
- Media library
- Admin dashboard

## Requirements

- Python 3.8+
- Django 5.2.3
- See requirements.txt for complete list of dependencies

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/Brianfadi/MOPDIC.git
   cd MOPDIC
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   .\venv\Scripts\activate  # On Windows
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run migrations:
   ```bash
   python manage.py migrate
   ```

5. Create a superuser:
   ```bash
   python manage.py createsuperuser
   ```

6. Run the development server:
   ```bash
   python manage.py runserver
   ```

## License

This project is licensed under the MIT License.
