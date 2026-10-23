"""
Capture high-resolution screenshots of PredictiveGuard sections via CDP.
"""

import os
import sys
import time
import json
import base64
import subprocess
import urllib.request
import websocket

def capture_all():
    os.makedirs("screenshots", exist_ok=True)
    edge_path = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
    user_data = os.path.join(os.environ.get("TEMP", "C:\\Temp"), "edge_cdp_screens")
    
    cmd = [
        edge_path,
        "--headless=new",
        "--remote-debugging-port=9222",
        "--remote-allow-origins=*",
        f"--user-data-dir={user_data}",
        "--window-size=1360,780",
        "--hide-scrollbars",
        "--disable-gpu",
        "--no-first-run",
        "--no-default-browser-check",
        "about:blank"
    ]
    proc = subprocess.Popen(cmd)
    time.sleep(2.5)

    try:
        # Get existing target
        req = urllib.request.Request("http://127.0.0.1:9222/json/list")
        with urllib.request.urlopen(req) as r:
            targets = json.loads(r.read().decode())
        
        target_info = next((t for t in targets if t.get("type") == "page"), targets[0])
        ws_url = target_info["webSocketDebuggerUrl"]
        ws = websocket.create_connection(ws_url, timeout=15)
        
        msg_id = 0
        def send_cmd(method, params=None):
            nonlocal msg_id
            msg_id += 1
            payload = {"id": msg_id, "method": method, "params": params or {}}
            ws.send(json.dumps(payload))
            while True:
                resp = json.loads(ws.recv())
                if resp.get("id") == msg_id:
                    return resp.get("result", {})

        send_cmd("Page.enable")
        send_cmd("Network.enable")
        send_cmd("Emulation.setDeviceMetricsOverride", {
            "width": 1360,
            "height": 765,
            "deviceScaleFactor": 1,
            "mobile": False
        })

        sections = [
            ("dashboard", "fig2_dashboard.png", 3.0),
            ("logs", "fig3_logs.png", 2.0),
            ("anomalies", "fig4_anomalies.png", 2.0),
            ("predictions", "fig5_predictions.png", 2.0),
            ("recovery", "fig6_recovery.png", 2.0),
            ("timeline", "fig7_timeline.png", 2.0),
        ]

        for sec, filename, wait_time in sections:
            url = f"http://localhost:5000/?section={sec}"
            print(f"Navigating to {sec}...")
            send_cmd("Page.navigate", {"url": url})
            time.sleep(wait_time)
            
            # Capture screenshot
            res = send_cmd("Page.captureScreenshot", {"format": "png"})
            data = base64.b64decode(res["data"])
            filepath = os.path.join("screenshots", filename)
            with open(filepath, "wb") as f:
                f.write(data)
            print(f"Saved {filepath} ({len(data)} bytes)")

        # Also capture Settings / Configuration or Alerts view
        # We can click the alert bell to show the alert dropdown
        send_cmd("Runtime.evaluate", {"expression": "document.getElementById('alert-bell').click()"})
        time.sleep(0.5)
        res = send_cmd("Page.captureScreenshot", {"format": "png"})
        data = base64.b64decode(res["data"])
        filepath = os.path.join("screenshots", "fig10_alerts.png")
        with open(filepath, "wb") as f:
            f.write(data)
        print(f"Saved {filepath} (alert dropdown)")

        # Also capture metrics / models details
        # Let's navigate to dashboard and scroll slightly down
        send_cmd("Page.navigate", {"url": "http://localhost:5000/?section=dashboard"})
        time.sleep(2.0)
        send_cmd("Runtime.evaluate", {"expression": "window.scrollTo(0, 320)"})
        time.sleep(0.5)
        res = send_cmd("Page.captureScreenshot", {"format": "png"})
        data = base64.b64decode(res["data"])
        filepath = os.path.join("screenshots", "fig8_metrics_charts.png")
        with open(filepath, "wb") as f:
            f.write(data)
        print(f"Saved {filepath} (metrics charts)")

        ws.close()
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=3)
        except Exception:
            pass

if __name__ == "__main__":
    capture_all()
