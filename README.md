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

### 5. Set up Gmail API for verification emails

SousPaw sends account verification emails through the Gmail API. This uses Google's OAuth flow instead of a normal SMTP password.

1. Open Google Cloud Console and create or select a project.
2. Enable the Gmail API for that project.
3. Set up the OAuth consent screen.
4. Create an OAuth client with application type `Desktop app`.
5. Download the OAuth JSON file from Google Cloud.
6. Save that file in the project root as `gmail_credentials.json`.
7. Copy `.env.example` to `.env`.
8. Add your Gmail API settings to `.env`.
9. Run the one-time authorization command:

```bash
python SWE_Project/manage.py setup_gmail_api
```

10. A browser window opens. Sign in with the Gmail account you want the app to send from and approve access.
11. After approval, the app creates `gmail_token.json` in the project root.
12. Start the server and test signup. Future emails reuse the saved token.

Example `.env`:

```env
EMAIL_PROVIDER=gmail_api
DEFAULT_FROM_EMAIL=yourgmail@gmail.com
GMAIL_API_SENDER=yourgmail@gmail.com
GMAIL_API_CREDENTIALS_FILE=/Users/yourname/path/to/SWE_Project/gmail_credentials.json
GMAIL_API_TOKEN_FILE=/Users/yourname/path/to/SWE_Project/gmail_token.json
```

Important:

- Do not commit `gmail_credentials.json`, `gmail_token.json`, or `.env`.
- If signup stays on the same page instead of redirecting to `/verify-email/`, the email send likely failed.
- If you change Google accounts or regenerate credentials, delete `gmail_token.json` and run `setup_gmail_api` again.

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
