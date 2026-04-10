# Project: SousPaw
SousPaw is an interactive cooking website designed to make cooking more engaging and less intimidating. The app features a virtual pet that assists users throughout the cooking process by providing step-by-step guidance, reminders, and helpful tips. By combining recipe management with gamification elements, SousPaw motivates users to cook at home while building confidence in the kitchen. The solution transforms traditional recipe-following into an enjoyable, supportive experience that encourages consistent user engagement.

## How to Run the Project

This project is a Django application. After cloning the repository onto your own computer, run it with the steps below. Also, make sure to install python3 in your terminal. If you type in python3 -m venv venv in your terminal it should automatically provide you with the next steps to do so if it is not already installed in your terminal.

### 1. Clone the repository

```bash
git clone https://github.com/SWE-Group-1-2026/SWE_Project.git
cd SWE_Project
```

### 2. Create and activate a virtual environment

On macOS or Linux:

```bash
python3 -m venv venv
source venv/bin/activate
```

On Windows:

```powershell
py -m venv venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, you can still run everything using the virtual environment Python directly:

```powershell
.\venv\Scripts\python.exe -m pip install -r requirements.txt
.\venv\Scripts\python.exe SWE_Project\manage.py migrate
.\venv\Scripts\python.exe SWE_Project\manage.py runserver
```
If receiving an error with the venv\Scripts\Activate.ps1 command do: Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass and then try the command again.

### 3. Install dependencies

On macOS or Linux:

```bash
pip install -r requirements.txt
```
For Windows: 
py -m pip install -r requirements.txt

On Windows PowerShell:

```powershell
py -m pip install -r requirements.txt
```

### 4. Set up MongoDB

The recipes page uses MongoDB Atlas. Update the MongoDB connection string in `SWE_Project/recipes/views.py` or, preferably, configure it from an environment variable before running the server.

Make sure:

- your MongoDB Atlas cluster is running
- your IP address is allowed in Atlas Network Access
- the database user credentials are valid
- the `SousPaw` database and `Recipes` collection exist

### 5. Set up Gmail for verification emails

The signup flow sends a verification email before a new user can log in. The easiest setup is Gmail SMTP with an App Password.

1. Turn on 2-Step Verification for the Gmail account you want to send from.
2. Create a Google App Password for that account.
3. Copy `.env.example` to `.env`.
4. Replace the placeholder values in `.env` with your Gmail address and App Password.

Example `.env`:

```env
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=yourgmail@gmail.com
EMAIL_HOST_PASSWORD=your_16_character_app_password
DEFAULT_FROM_EMAIL=yourgmail@gmail.com
EMAIL_USE_TLS=True
```

### 6. Run Django migrations

On macOS or Linux:

```bash
python SWE_Project/manage.py migrate
```

On Windows PowerShell:

```powershell
py SWE_Project\manage.py migrate
```

### 7. Start the development server

On macOS or Linux:

```bash
python SWE_Project/manage.py runserver
```
Or py SWE_Project/manage.py runserver

On Windows PowerShell:

```powershell
py SWE_Project\manage.py runserver
```

### 8. Open the app

Visit in your local browser:

```text
http://127.0.0.1:8000/
```

## Notes

- Do not commit your local `venv/` folder.
- If `python` does not work on your machine, use `python3`.
- On Windows, if `pip` or `pip3` is not recognized, use `py -m pip` instead.
- On Windows PowerShell, if `Activate.ps1` is blocked, use `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` for the current terminal session.
- If the recipes page does not load, the most common issue is MongoDB Atlas access or connection settings.

## Project Structure
- `SWE_Project/manage.py`: Django entry point
- `SWE_Project/SWE_Project/`: Django project settings and URL configuration
- `SWE_Project/recipes/`: Main app with views, routes, templates, and static assets
- `SWE_Project/recipes/templates/`: Django templates for landing, auth, pet, profile, tutorial, search, and recipe pages
- `SWE_Project/recipes/static/recipes/`: CSS, JavaScript, and image assets served by Django
