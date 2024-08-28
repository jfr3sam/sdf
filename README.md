# 🛠️ Django Setup Guide
Follow these steps to set up a Django project from scratch.

## Step 1: Install Python 🐍
Ensure you have Python installed on your system. Django is compatible with Python 3.9 and above. Download Python from the [official Python website](https://www.python.org/downloads/).

## Step 2: Install Virtual Environment 🌐
It's a good practice to use a virtual environment to manage your project dependencies. You can create a virtual environment using `venv` or `virtualenv`.
```bash
# Install virtualenv if not already installed
pip install virtualenv

# Create a virtual environment named 'venv'
virtualenv venv

# Activate the virtual environment
# On Windows
.\\venv\\Scripts\\activate

# On macOS/Linux
source venv/bin/activate
```

## Step 3: Install Django 🎯
```bash
# Install the latest version of Django
pip install django
```

## Step 4: Create a Django Project 🚀
```bash
# Replace 'myproject' with your desired project name
django-admin startproject myproject

cd myproject
```

## Step 5: Run the Development Server 🖥️
```bash
# Migrate the initial database schema
python manage.py migrate

# Start the development server
python manage.py runserver
```

## Step 6: Create a Django App 📱
```bash
# Replace 'myapp' with your desired app name
python manage.py startapp myapp
```

Add your app to the `INSTALLED_APPS` in `myproject/settings.py`:
```python
INSTALLED_APPS = [
    ...,
    'myapp',
]
```

## Step 7: Set Up the Database 💾
Edit `myproject/settings.py` to configure your database:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',  # For SQLite
        'NAME': BASE_DIR / 'db.sqlite3',
        
        # For PostgreSQL
        # 'ENGINE': 'django.db.backends.postgresql',
        # 'NAME': 'your_db_name',
        # 'USER': 'your_db_user',
        # 'PASSWORD': 'your_db_password',
        # 'HOST': 'localhost',
        # 'PORT': '5432',
        
        # For MySQL
        # 'ENGINE': 'django.db.backends.mysql',
        # 'NAME': 'your_db_name',
        # 'USER': 'your_db_user',
        # 'PASSWORD': 'your_db_password',
        # 'HOST': 'localhost',
        # 'PORT': '3306',
    }
}
```

Then run:
```bash
python manage.py makemigrations
python manage.py migrate
```

## Step 8: Create a Superuser 👑
```bash
python manage.py createsuperuser
```

## Step 9: Run the Project 🏃
```bash
python manage.py runserver
```

## Step 10: Access the Admin Panel 🔑
Navigate to http://127.0.0.1:8000/admin and log in with the superuser credentials you created.