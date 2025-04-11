INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Мои приложения
    'users.apps.UsersConfig',
    'core.apps.CoreConfig',
    'blog.apps.BlogConfig',
    'recovery_stories.apps.RecoveryStoriesConfig',
    'requests.apps.RequestsConfig',
    'facilities.apps.FacilitiesConfig',
    'staff.apps.StaffConfig',
    'admin_logs.apps.AdminLogsConfig',
] 