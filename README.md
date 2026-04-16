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

SousPaw can send verification emails through the Gmail API. Google requires OAuth for this flow.

1. In Google Cloud, enable the Gmail API.
2. Configure the OAuth consent screen.
3. Create an OAuth client for a Desktop app.
4. Download the client JSON file and save it as `gmail_credentials.json` in the project root.
5. Copy `.env.example` to `.env`.
6. Fill in the Gmail API values in `.env`.
7. Run the one-time authorization command:

```bash
python SWE_Project/manage.py setup_gmail_api
```

8. Start the server and test signup. The token is saved to `gmail_token.json` and reused for later sends.

Example `.env`:

```env
EMAIL_PROVIDER=gmail_api
DEFAULT_FROM_EMAIL=yourgmail@gmail.com
GMAIL_API_SENDER=yourgmail@gmail.com
GMAIL_API_CREDENTIALS_FILE=/absolute/path/to/SWE_Project/gmail_credentials.json
GMAIL_API_TOKEN_FILE=/absolute/path/to/SWE_Project/gmail_token.json
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
