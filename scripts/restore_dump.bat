@echo off
REM Скрипт восстановления базы данных из дампа для Windows
REM Использование: restore_dump.bat [путь_к_дампу]

REM Проверка, что мы в корне проекта Django
if not exist "manage.py" (
    echo Ошибка: manage.py не найден. Запустите скрипт из корня проекта Django.
    exit /b 1
)

REM Определение файла дампа
if "%1"=="" (
    REM Поиск последнего дампа
    for /f "delims=" %%i in ('dir /b /o-d fixtures\dump_*.json 2^>nul') do (
        set "DUMP_FILE=fixtures\%%i"
        goto :found_dump
    )
    echo Ошибка: дамп не найден. Укажите путь к файлу дампа.
    echo Использование: %0 [путь_к_дампу]
    exit /b 1
) else (
    set "DUMP_FILE=%1"
)

:found_dump

REM Проверка существования файла
if not exist "%DUMP_FILE%" (
    echo Ошибка: файл %DUMP_FILE% не найден
    exit /b 1
)

echo Восстановление из дампа: %DUMP_FILE%

REM Показ размера файла
for %%A in ("%DUMP_FILE%") do echo Размер дампа: %%~zA байт

REM Подтверждение действия
echo.
echo ВНИМАНИЕ: Это действие удалит текущую базу данных!
set /p "confirm=Продолжить? (y/N): "
if /i not "%confirm%"=="y" (
    echo Операция отменена
    exit /b 0
)

echo.
echo Начинаем восстановление...

REM Удалить старую БД
echo Удаление старой базы данных...
if exist "db.sqlite3" del "db.sqlite3"

REM Создать новую БД
echo Создание новой базы данных...
python manage.py migrate

REM Проверка успешности миграций
if %ERRORLEVEL% NEQ 0 (
    echo ✗ Ошибка при создании базы данных
    exit /b 1
)

REM Загрузить дамп
echo Загрузка данных из дампа...
python manage.py loaddata "%DUMP_FILE%"

REM Проверка успешности загрузки
if %ERRORLEVEL% EQU 0 (
    echo ✓ Восстановление завершено успешно
    echo.
    echo Статистика восстановления:
    echo Загружено объектов: 
    python -c "import json; data=json.load(open('%DUMP_FILE%', 'r', encoding='utf-8')); print(len(data))"
    echo.
    echo Модели: 
    python -c "import json; data=json.load(open('%DUMP_FILE%', 'r', encoding='utf-8')); models=set(item['model'] for item in data); print(len(models))"
    echo.
    echo Загруженные модели:
    python -c "import json; data=json.load(open('%DUMP_FILE%', 'r', encoding='utf-8')); models=sorted(set(item['model'] for item in data)); [print(f'  - {model}') for model in models]"
    
) else (
    echo ✗ Ошибка при загрузке дампа
    echo.
    echo Попробуйте очистить ContentType:
    echo python manage.py shell -c "from django.contrib.contenttypes.models import ContentType; ContentType.objects.all().delete()"
    echo python manage.py loaddata "%DUMP_FILE%"
    exit /b 1
)

echo.
echo Готово! База данных восстановлена. 