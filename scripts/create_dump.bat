@echo off
REM Скрипт создания дампа базы данных для Windows
REM Использование: create_dump.bat [имя_файла]

REM Проверка, что мы в корне проекта Django
if not exist "manage.py" (
    echo Ошибка: manage.py не найден. Запустите скрипт из корня проекта Django.
    exit /b 1
)

REM Создание папки fixtures, если её нет
if not exist "fixtures" mkdir fixtures

REM Определение имени файла
if "%1"=="" (
    REM Создание дампа с временной меткой
    for /f "tokens=2 delims==" %%a in ('wmic OS Get localdatetime /value') do set "dt=%%a"
    set "TIMESTAMP=%dt:~0,8%_%dt:~8,6%"
    set "DUMP_FILE=fixtures\dump_%TIMESTAMP%.json"
) else (
    set "DUMP_FILE=fixtures\%1"
)

echo Создание дампа: %DUMP_FILE%

REM Создание дампа с кодировкой UTF-8
set "PYTHONIOENCODING=utf-8"
python manage.py dumpdata --exclude auth.permission --exclude contenttypes.contenttype --exclude admin.logentry --exclude sessions.session --indent 2 > "%DUMP_FILE%"

REM Проверка успешности создания
if %ERRORLEVEL% EQU 0 (
    echo ✓ Дамп создан успешно
    echo Файл: %DUMP_FILE%
    
    REM Показ размера файла (если доступен)
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
    echo Список моделей:
    python -c "import json; data=json.load(open('%DUMP_FILE%', 'r', encoding='utf-8')); models=sorted(set(item['model'] for item in data)); [print(f'  - {model}') for model in models]"
    
) else (
    echo ✗ Ошибка при создании дампа
    exit /b 1
)

echo.
echo Готово! 