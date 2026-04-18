@echo off
echo Installing dependencies...
pip install customtkinter Pillow cairosvg pyinstaller

echo.
echo Building exe...
pyinstaller --onefile --windowed ^
    --name "TischEins_Prompt_Generator" ^
    --hidden-import customtkinter ^
    --collect-all customtkinter ^
    --collect-all cairosvg ^
    --add-data "assets;assets" ^
    main.py

echo.
echo Done! Die exe liegt in dist\TischEins_Prompt_Generator.exe
pause
