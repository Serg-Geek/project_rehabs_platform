@echo off
REM Скрипт создания дампа конкретного приложения для Windows
REM Использование: dump_app.bat [приложение] [имя_файла]

REM Проверка, что мы в корне проекта Django
if not exist "manage.py" (
    echo Ошибка: manage.py не найден. Запустите скрипт из корня проекта Django.
    exit /b 1
)

REM Проверка аргументов
if "%1"=="" (
    echo Ошибка: не указано приложение
    echo Использование: %0 [приложение] [имя_файла]
    echo.
    echo Доступные приложения:
    echo   - core
    echo   - facilities
    echo   - staff
    echo   - users
    echo   - blog
    echo   - requests
    echo   - medical_services
    echo   - reviews
    echo   - recovery_stories
    echo   - content
    exit /b 1
)

set "APP_NAME=%1"

REM Создание папки fixtures, если её нет
if not exist "fixtures" mkdir fixtures

REM Определение имени файла
if "%2"=="" (
    REM Создание дампа с временной меткой
    for /f "tokens=2 delims==" %%a in ('wmic OS Get localdatetime /value') do set "dt=%%a"
    set "TIMESTAMP=%dt:~0,8%_%dt:~8,6%"
    set "DUMP_FILE=fixtures\%APP_NAME%_dump_%TIMESTAMP%.json"
) else (
    set "DUMP_FILE=fixtures\%2"
)

echo Создание дампа приложения '%APP_NAME%': %DUMP_FILE%

REM Создание дампа с кодировкой UTF-8
set "PYTHONIOENCODING=utf-8"
python manage.py dumpdata "%APP_NAME%" --indent 2 > "%DUMP_FILE%"

REM Проверка успешности создания
if %ERRORLEVEL% EQU 0 (
    echo ✓ Дамп приложения '%APP_NAME%' создан успешно
    echo Файл: %DUMP_FILE%
    
    REM Показ размера файла
    for %%A in ("%DUMP_FILE%") do echo Размер: %%~zA байт
    
    echo Кодировка: UTF-8
    echo.
    echo Статистика дампа:
    echo Количество объектов: 
    python -c "import json; data=json.load(open('%DUMP_FILE%', 'r', encoding='utf-8')); print(len(data))"
    echo.
    echo Модели в дампе: 
    python -c "import json; data=json.load(open('%DUMP_FILE%', 'r', encoding='utf-8')); models=set(item['model'] for item in data); print(len(models))"
    echo.
    echo Модели в дампе:
    python -c "import json; data=json.load(open('%DUMP_FILE%', 'r', encoding='utf-8')); models=sorted(set(item['model'] for item in data)); [print(f'  - {model}') for model in models]"
    
) else (
    echo ✗ Ошибка при создании дампа приложения '%APP_NAME%'
    echo.
    echo Возможные причины:
    echo   - Приложение '%APP_NAME%' не существует
    echo   - В приложении нет данных
    echo   - Ошибка в структуре приложения
    exit /b 1
)

echo.
echo Готово! 