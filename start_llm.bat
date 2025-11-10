@echo off
set MODEL_PATH=C:\Users\msira\Downloads\breezer_sonnet\mistral.gguf
server.exe -m %MODEL_PATH% --port 8080
