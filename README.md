
## Step 1: Create a Django App 📱
```bash
# Replace 'myapp' with your desired app name
pip install django-allauth
```

Add your app to the `INSTALLED_APPS` in `myproject/settings.py`:
```python
INSTALLED_APPS = [
    ...,
    'django.contrib.sites',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
]
```

## Step 2: Add Authentication Backends
Edit `myproject/settings.py` to configure your database:
```python
AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',  # Default backend
    'allauth.account.auth_backends.AuthenticationBackend',  # Allauth backend
)
```

## Step 3: Set Site ID
```bash
SITE_ID = 1
```

## Step 4: Configure Allauth Settings
```bash
ACCOUNT_AUTHENTICATION_METHOD = 'username'  # or 'email' if you use email as username
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_EMAIL_VERIFICATION = 'mandatory'
ACCOUNT_USERNAME_REQUIRED = False  # Set to True if you want a username field
LOGIN_REDIRECT_URL = '/'  # URL to redirect after login
LOGOUT_REDIRECT_URL = '/'  # URL to redirect after logout
```

## Step 5: Include Allauth URLs in urls.py
```bash
from django.urls import path, include

urlpatterns = [
    ...
    path('accounts/', include('allauth.urls')),  # Allauth URLs
    ...
]
```

Then run:
```bash
python manage.py makemigrations
python manage.py migrate
```
