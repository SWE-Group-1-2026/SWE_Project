# Project: SousPaw
SousPaw is an interactive cooking website designed to make cooking more engaging and less intimidating. The app features a virtual pet that assists users throughout the cooking process by providing step-by-step guidance, reminders, and helpful tips. By combining recipe management with gamification elements, SousPaw motivates users to cook at home while building confidence in the kitchen. The solution transforms traditional recipe-following into an enjoyable, supportive experience that encourages consistent user engagement.

## How to Run the Project

This project is now organized as a Django application.

1. Open a terminal in `/Users/eesha/Downloads/Archive/Desktop/UF/CEN3031/SWE_Project/SWE_Project`
2. Activate your virtual environment if needed
3. Run `python manage.py migrate`
4. Run `python manage.py runserver`
5. Open `http://127.0.0.1:8000/`

## Project Structure
- `SWE_Project/manage.py`: Django entry point
- `SWE_Project/SWE_Project/`: Django project settings and URL configuration
- `SWE_Project/recipes/`: Main app with views, routes, templates, and static assets
- `SWE_Project/recipes/templates/`: Django templates for landing, auth, pet, profile, tutorial, search, and recipe pages
- `SWE_Project/recipes/static/recipes/`: CSS, JavaScript, and image assets served by Django

