@echo off
start "" http://localhost:8766
python "%~dp0mailer_server.py"
