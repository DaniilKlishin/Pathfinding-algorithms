@echo off
echo Установка PyInstaller...
pip install pyinstaller

echo Создание EXE файла...
pyinstaller --onefile --name=PathFinder --console --clean main.py

echo.
echo ============================================
echo Готово! EXE файл создан: dist\PathFinder.exe
echo ============================================
pause