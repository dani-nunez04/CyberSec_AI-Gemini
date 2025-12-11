#!/usr/bin/env python3
"""
validate_webhooks.py

Script small to validate each configured Discord webhook and print HTTP status and optional response body.
"""
import os
import requests
from dotenv import load_dotenv
from urllib.parse import urlparse

load_dotenv()

webhooks = {
    'LOGS_ANALISIS': os.getenv('DISCORD_WEBHOOK_LOGS_ANALISIS'),
    'ERRORES': os.getenv('DISCORD_WEBHOOK_ERRORES'),
    'DESARROLLO': os.getenv('DISCORD_WEBHOOK_DESARROLLO')
}

print('📋 Webhook validation')
print('-------------------')
for k, url in webhooks.items():
    if not url:
        print(f"{k}: NOT CONFIGURED")
        continue

    print(f"{k}: Testing {url}")
    try:
        payload = {'content': f'Test message for {k} (validate_webhooks)'}
        # Use a small timeout
        r = requests.post(url, json=payload, timeout=5)
        print(f"   Status: {r.status_code}")
        if r.status_code != 204:
            print(f"   Response: {r.text}")
    except Exception as e:
        print(f"   ERROR: {e}")

print('\n✅ Done. Check the Discord channel(s) and adjust (.env) if needed')
