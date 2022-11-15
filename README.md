# Zoho

Check-in/check-out in Zoho

## Requirements

For building and running the application you need:

- [Python 3.8.10](https://www.python.org/downloads/release/python-3810/)
- [selenium](https://pypi.org/project/selenium/)
- [pyotp](https://pypi.org/project/pyotp/)

## Prerequisite

1. Input username
2. Input password
3. Input OTP (if enabled)

## Create scheduled task on Windows

1. Find where python is installed on your PC. Usually it'll be at `C:\Users\{user}\AppData\Local\Programs\Python\Python310\python.exe`
2. Create a `.bat` file in the same folder. 
3. Put this inside the bat file: `"C:\Users\{user}\AppData\Local\Programs\Python\Python310\python.exe" "{current dir}/zoho.py"`. e.g. `"C:\Users\tient\AppData\Local\Programs\Python\Python39\python.exe" "C:\repos\zoho\zoho.py"`
4. Open `Task Scheduler`
5. On the right hand side, click `Create Task...`
6. Go to `Triggers|New...` and set the schedule for check-in. e.g. 9AM every weekday
7. Create another schedule for check-out. e.g. 5PM every weekday
8. Go to `Actions|New...`
  1. Action: Start a program
  2. Program/script: {bat file path}. e.g `C:\repos\zoho\daily.bat`
  3. Start in (optional): {current dir}. e.g. `C:\repos\zoho`
9. Click OK
