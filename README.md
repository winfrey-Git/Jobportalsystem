[README.md](https://github.com/user-attachments/files/33759585/README.md)

# Job Portal System

A Django-based web project for a job portal. The repository includes Django application folders, templates, media/static assets, `manage.py`, and a SQLite database file.

## Overview

The project provides a web application structure for a job portal. Inspect the views, URL configuration, models, and templates in the source code to verify the exact features implemented in this version.

## Technologies

- Python
- Django
- HTML templates
- SQLite
- Static and media assets

## Getting started

### Prerequisites

- Python 3
- `pip`

### Setup

1. Clone the repository:

   ```bash
   git clone https://github.com/winfrey-Git/Jobportalsystem.git
   cd Jobportalsystem
   ```

2. Create and activate a virtual environment.

   **Windows**
   ```bash
   py -m venv .venv
   .venv\Scripts\activate
   ```

   **macOS/Linux**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. Install Django:

   ```bash
   pip install django
   ```

   If your local copy contains `requirements.txt`, use `pip install -r requirements.txt` to install the project's listed dependencies.

4. Apply migrations:

   ```bash
   python manage.py migrate
   ```

5. Start the development server:

   ```bash
   python manage.py runserver
   ```

6. Visit `http://127.0.0.1:8000/`.

## Before deployment

- Review `settings.py` and move secret values to environment variables.
- Configure a production database and static-file hosting.
- Do not expose the local SQLite database if it contains real or personal data.
- Verify all features and routes before describing them as complete.

## Repository

[winfrey-Git/Jobportalsystem](https://github.com/winfrey-Git/Jobportalsystem)

## Author

**Winfred Kive**  
GitHub: [winfrey-Git](https://github.com/winfrey-Git)
