db:
	duckdb data\main.db

app:
	uv run uvicorn app:app --host 0.0.0.0 --port 8000

api:
	Start-Process "microsoft-edge:localhost:8000/docs" 

debug:
	$env:DEBUG=1

nodebug:
	$env:DEBUG=0

help:
	powershell Write-Host "ukazi: app, db, debug, nodebug, help" -ForegroundColor Green

.PHONY: db app api debug nodebug help

.DEFAULT_GOAL := help
