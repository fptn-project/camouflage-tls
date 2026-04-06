import time
import json
import random
import socket
import urllib.error
import urllib.request

from typing import Set
from threading import Lock
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed


SNI_LIST = [
    "t.me",
    "x.ai",
    "g.co",
    "a.co",
    "ya.ru",
    "ok.ru",
    "x.com",
    "hh.ru",
    "vk.com",
    "mts.ru",
    "dns.ru",
    "fb.com",
    "rbc.ru",
    "ozon.ru",
    "yota.ru",
    "tass.ru",
    "nspk.ru",
    "avito.ru",
    "lenta.ru",
    "metro.ru",
    "mamba.ru",
    "habr.com",
    "yandex.ru",
    "rutube.ru",
    "apple.com",
    "github.io",
    "twitch.tv",
    "pikabu.ru",
    "tiktok.com",
    "google.com",
    "openai.com",
    "amazon.com",
    "yandex.com",
    "weather.com",
    "discord.com",
    "booking.com",
    "youtube.com",
    "samsung.com",
    "xhamster.com",
    "telegram.org",
    "facebook.com",
    "kaspersky.ru",
    "theverge.com",
    "microsoft.com",
    "wikipedia.org",
    "mailchimp.com",
    "duckduckgo.com",
    "aliexpress.com",
    "cloudflare.com",
]

random.shuffle(SNI_LIST)
SNI_LIST = SNI_LIST[:10]


def fetch_domains(domain: str) -> set:
    try:
        url = f"https://api.certspotter.com/v1/issuances?domain={domain}&include_subdomains=true&match_wildcards=true&expand=dns_names"

        req = urllib.request.Request(
            url,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            },
        )

        with urllib.request.urlopen(req, timeout=30) as response:
            if response.getcode() != 200:
                print(f"Domain {domain}: HTTP {response.getcode()}")
                return {domain}
            data = json.loads(response.read().decode("utf-8"))
            domains = {domain}
            for issuance in data:
                if issuance.get("revoked", False):
                    continue
                dns_names = issuance.get("dns_names", [])
                for dns_name in dns_names:
                    d = dns_name.strip().lower()
                    if d.endswith(domain) or d.endswith("." + domain):
                        if "*" not in d and "--" not in d and "@" not in d:
                            domains.add(d)
            print(f"Domain {domain}: found {len(domains)} domains via CertSpotter")
            return domains
    except Exception as e:
        print(f"errr> {domain}: {e}")
        return {domain}


def fetch_all_domains(sni_list: list) -> set:
    all_domains = set()
    for i, domain in enumerate(sni_list):
        print(f"\nProgress: {i+1}/{len(sni_list)} - Fetching {domain}")
        domains = fetch_domains(domain)
        all_domains.update(domains)
        time.sleep(10)
    return all_domains


def check_exists(domain: str, timeout: int = 3) -> bool:
    try:
        response = requests.get(
            f"https://{domain}", timeout=timeout, verify=True, allow_redirects=True
        )
        return 200 <= response.status_code < 400
    except:
        return False


def main():
    all_domains = fetch_all_domains(SNI_LIST)

    print(f"\nTotal domains collected: {len(all_domains)}")

    grouped = defaultdict(list)
    for d in all_domains:
        grouped[len(d)].append(d)

    print(f"Lengths available: {sorted(grouped.keys())}")
    for length in sorted(grouped.keys()):
        print(f"  Length {length}: {len(grouped[length])} domains")

    result = defaultdict(list)
    lock = Lock()
    for length in sorted(grouped.keys()):
        domains_to_check = grouped[length]
        with ThreadPoolExecutor(max_workers=2) as executor:
            futures = {
                executor.submit(check_exists, domain): domain
                for domain in domains_to_check
            }
            for future in as_completed(futures):
                if len(result[length]) >= 5:
                    break
                domain = futures[future]
                try:
                    if future.result():
                        with lock:
                            if len(result[length]) < 5:
                                result[length].append(domain)
                except:
                    pass
        print(f"  Found {len(result[length])} valid domains for length {length}")

    print("\nvalid_domains = [")
    for length in sorted(result.keys()):
        for d in sorted(result[length]):
            print(f'    "{d}",  # {len(d)}')
    print("]")


if __name__ == "__main__":
    main()
    print("DONE! Thank you!")
    time.sleep(99999)
