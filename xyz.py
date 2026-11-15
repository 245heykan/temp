import base64
import hashlib
import json
import random
import re
from datetime import datetime, timedelta
from urllib.parse import urljoin, urlsplit
from zoneinfo import ZoneInfo

import requests
from bs4 import BeautifulSoup
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad

BASE_URL = "https://xyzstreams.space"

SERVERS = [
    "https://404found.it.com",
    "https://hls.kozow.com",
    "https://us-xyz.work.gd",
]

KEY = "TXlTdXBlclNlY3JldEtleTEyMyE="

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}


def decrypt_token(secret: str, token_h: str, iv_h: str) -> str:
    key = hashlib.sha256(secret.encode("utf-8")).digest()
    iv = bytes.fromhex(iv_h)
    cipher_t = bytes.fromhex(token_h)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    dec = unpad(cipher.decrypt(cipher_t), AES.block_size)
    raw = dec.decode("utf-8", errors="ignore")
    return re.sub(r"[^\x20-\x7E]", "", raw).strip()


def get_events() -> list[dict]:
    events = []
    try:
        res = requests.get(BASE_URL, headers=HEADERS, timeout=15)
        if res.status_code != 200:
            print(f"[HATA] Ana sayfa acilamadi: {res.status_code}")
            return events

        ptrn = re.compile(r"EVENTS_DATA\s*=\s*(\[.*?^\])", re.S | re.M | re.I)
        match = ptrn.search(res.text)
        if not match:
            print('[HATA] "EVENTS_DATA" verisi bulunamadi.')
            return events

        clean_json = re.sub(r",\s*\]$", "]", match.group(1))
        event_data = json.loads(clean_json)

        est_tz = ZoneInfo("America/New_York")
        now_est = datetime.now(est_tz)

        for game in event_data:
            sport = game.get("category")
            name = game.get("title")
            event_time = game.get("start")
            href = game.get("href")

            if not all([sport, name, event_time, href]):
                continue

            event_time = event_time.replace("24:00:00", "00:00:00")
            try:
                event_dt = datetime.fromisoformat(event_time).replace(tzinfo=est_tz)
            except ValueError:
                continue

            # Sadece bugunun ve baslamasina 30 dk kalmis veya devam eden maclari alir
            if event_dt.date() != now_est.date():
                continue

            start_window = now_est - timedelta(minutes=180)
            end_window = now_est + timedelta(minutes=30)

            if start_window <= event_dt <= end_window:
                events.append({
                    "sport": sport,
                    "name": name,
                    "logo": game.get("bg") or "",
                    "link": urljoin(BASE_URL, href)
                })
    except Exception as e:
        print(f"[HATA] Etkinlikler cekilirken hata: {e}")

    return events


def process_event(url: str) -> str | None:
    server = random.choice(SERVERS)
    try:
        html_res = requests.get(url, headers={**HEADERS, "Referer": BASE_URL}, timeout=15)
        if html_res.status_code != 200:
            return None

        api_res = requests.get(
            urljoin(server, "api/token"),
            headers={**HEADERS, "Referer": url},
            timeout=15
        )
        if api_res.status_code != 200:
            return None

        token_data = api_res.json()
        token = token_data.get("token")
        token_iv = token_data.get("iv")

        if not (token and token_iv):
            return None

        if "stream.html" in url:
            ifr_src = url.replace("stream.html", "embed")
        else:
            soup = BeautifulSoup(html_res.text, "html.parser")
            iframe = soup.select_one("iframe#stream-player")
            if not iframe or not iframe.get("src"):
                return None
            ifr_src = iframe.get("src")

        strm_path = urlsplit(ifr_src).query
        secret_key = base64.b64decode(KEY).decode("utf-8")
        raw_token = decrypt_token(secret_key, token, token_iv)

        return urljoin(server, f"{strm_path}/mono.ts.m3u8?token={raw_token}")
    except Exception:
        return None


def main():
    print(f"[+] {BASE_URL} taraniyor...")
    events = get_events()
    print(f"[+] Uygun {len(events)} etkinlik bulundu.\n")

    m3u_content = "#EXTM3U\n"
    success_count = 0

    for idx, ev in enumerate(events, 1):
        title = f"[{ev['sport']}] {ev['name']}"
        print(f"[{idx}/{len(events)}] Isleniyor: {title}")

        stream_url = process_event(ev["link"])
        if stream_url:
            print(f"    └─ [OK] {stream_url}")
            logo_attr = f' tvg-logo="{ev["logo"]}"' if ev["logo"] else ""
            m3u_content += f'#EXTINF:-1 group-title="XYZ"{logo_attr}, {title}\n'
            m3u_content += f"#EXTVLCOPT:http-user-agent={HEADERS['User-Agent']}\n"
            m3u_content += f"#EXTVLCOPT:http-referrer={ev['link']}\n"
            m3u_content += f"{stream_url}\n"
            success_count += 1
        else:
            print("    └─ [SKIP]")

    with open("xyz.m3u", "w", encoding="utf-8") as f:
        f.write(m3u_content)

    print(f"\n[+] Tamamlandi! {success_count} yayin ana dizindeki 'xyz.m3u' dosyasina kaydedildi.")


if __name__ == "__main__":
    main()
