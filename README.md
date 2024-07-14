# SmartCare Surgery System

## Overview

SmartCare Surgery System is a comprehensive web-based application designed to streamline healthcare facility operations. It offers features for appointment scheduling, patient management, prescription handling, and invoicing, catering to various user roles including patients, doctors, nurses, and administrators.

## Features

- User Authentication and Role-based Access Control
- Appointment Booking and Management
- Patient Records Management
- Prescription Issuance and Tracking
- Invoicing and Financial Reporting
- Integration with Google Calendar for Appointments
- Address Lookup using Google Maps API
- Collaboration Tools for Healthcare Providers

## Technology Stack

- Backend: Django, Django REST Framework
- Database: PostgreSQL
- Frontend: HTML, CSS, JavaScript (with Django Templates)
- API Integration: Google Calendar API, Google Maps API

## Prerequisites

- Python 3.9+
- PostgreSQL
- Google Cloud Platform account (for Calendar and Maps APIs)

## Installation and Setup

1. Clone the repository:
   ```sh
   git clone https://github.com/MTahsin77/SmartCare-Surgery-System.git
   cd smartcare-surgery-system
   ```

2. Create a virtual environment and activate it:
   ```sh
   python -m venv venv
   venv\Scripts\activate
   ```

3. Install the required packages:
   ```sh
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   Create a `.env` file in the root directory and add the following:
   ```env
   SECRET_KEY=your_secret_key
   DEBUG=True
   DATABASE_URL=postgres://user:password@localhost/smartcare_db
   GOOGLE_MAPS_API_KEY=your_google_maps_api_key
   GOOGLE_OAUTH2_CLIENT_ID=your_google_oauth_client_id
   GOOGLE_OAUTH2_CLIENT_SECRET=your_google_oauth_client_secret
   ```

5. Run database migrations:
   ```sh
   python manage.py migrate
   ```

6. Create a superuser:
   ```sh
   python manage.py createsuperuser
   ```

7. Run the development server:
   ```sh
   python manage.py runserver
   ```

8. Access the application at [http://localhost:8000](http://localhost:8000)

## Usage

### User Types and Functionalities

1. **Patients**
   - Register and manage profile
   - Book, view, and cancel appointments
   - View prescriptions and request refills
   - View and pay invoices

2. **Doctors**
   - View and manage appointments
   - Issue prescriptions
   - View patient records
   - Collaborate with other healthcare providers

3. **Nurses**
   - View and manage appointments
   - Assist in patient care
   - Update patient records

4. **Administrators**
   - Manage user accounts
   - Generate financial reports
   - Oversee system operations

### Key Workflows

1. **Appointment Booking**
   - Patients can book appointments through the calendar interface
   - Integration with Google Calendar for real-time availability

2. **Prescription Management**
   - Doctors can issue and manage prescriptions
   - Patients can view and request refills for their prescriptions

3. **Invoicing**
   - System generates invoices based on appointments and services
   - Patients can view and pay invoices online

4. **Reporting**
   - Administrators can generate various reports including financial summaries and patient statistics

## Contact

M Tahsin - tahsinarafat77@hotmail.com

Project Link: [GitHub](https://github.com/MTahsin77/SmartCare-Surgery-System)

## Acknowledgements

- [Django](https://www.djangoproject.com/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [Google Calendar API](https://developers.google.com/calendar)
- [Google Maps API](https://developers.google.com/maps)
