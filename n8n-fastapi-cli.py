#!/usr/bin/env python3
import sys, time, json, urllib.request

def test_webhook(url, payload):
    print(f'[*] Sending test webhook to {url}...')
    t0 = time.time()
    req = urllib.request.Request(url, data=json.dumps(payload).encode(), headers={'Content-Type': 'application/json'}, method='POST')
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            dt = (time.time() - t0) * 1000
            print(f'[+] Status: {r.status} | Latency: {dt:.1f}ms')
    except Exception as e:
        print(f'[-] Webhook Error: {e}')

if __name__ == '__main__':
    target = sys.argv[1] if len(sys.argv) > 1 else 'http://localhost:8000/webhook'
    test_webhook(target, {'event': 'test_ping', 'source': 'n8n-fastapi-cli'})
