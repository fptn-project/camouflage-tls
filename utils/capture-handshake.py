import os
import re
import sys
import time
import random
import tempfile
import argparse
import platform
import subprocess

from datetime import datetime
from collections import defaultdict
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path


DOMAINS_BY_LENGTH = {
    4: [
        "t.me",
        "x.ai",
        "g.co",
        "a.co",
        "m.me",
    ],
    5: [
        "ya.ru",
        "ok.ru",
        "x.com",
        "vk.ru",
        "hh.ru",
    ],
    6: [
        "vk.com",
        "mts.ru",
        "dns.ru",
        "fb.com",
        "rbc.ru",
    ],
    7: [
        "ozon.ru",
        "yota.ru",
        "tass.ru",
        "nspk.ru",
    ],
    8: [
        "avito.ru",
        "lenta.ru",
        "metro.ru",
        "mamba.ru",
        "habr.com",
    ],
    9: [
        "yandex.ru",
        "rutube.ru",
        "apple.com",
        "github.io",
        "twitch.tv",
        "pikabu.ru",
    ],
    10: [
        "google.com",
        "openai.com",
        "amazon.com",
        "yandex.com",
    ],
    11: [
        "discord.com",
        "booking.com",
        "youtube.com",
        "maps.vk.com",
        "r.rutube.ru",
        "tech.vk.com",
    ],
    12: [
        "telegram.org",
        "facebook.com",
        "kaspersky.ru",
        "theverge.com",
        "cloud.vk.com",
        "dobro.vk.com",
        "facebook.com",
        "teams.vk.com",
        "telegram.org",
    ],
    13: [
        "microsoft.com",
        "wikipedia.org",
        "mailchimp.com",
        "aliexpress.com",
        "cloudflare.com",
        "finops.vk.com",
        "ftp.yandex.ru",
        "log.rutube.ru",
        "rabota.vk.com",
        "u.corp.vk.com",
    ],
    14: [
        "api.openai.com",
        "api.github.com",
        "ads.google.com",
        "auto.yandex.ru",
        "h.facebook.com",
        "p.facebook.com",
        "tutoria.vk.com",
    ],
    15: [
        "mail.google.com",
        "docs.google.com",
        "br.xhamster.com",
        "check.yandex.ru",
        "jp.xhamster.com",
        "pt.xhamster.com",
        "tovar.yandex.ru",
    ],
    16: [
        "drive.google.com",
        "portal.azure.com",
        "adblogger.vk.com",
        "amp.xhamster.com",
        "cdn.xhamster.com",
        "docs.tech.vk.com",
        "vigoda.yandex.ru",
    ],
    17: [
        "music.youtube.com",
        "dp-repo-cp.vk.com",
        "dp-repo-dp.vk.com",
        "igrotok.yandex.ru",
        "skills.google.com",
        "tiles.maps.vk.com",
    ],
    18: [
        "support.google.com",
        "disk.360.yandex.ru",
        "garderob.yandex.ru",
        "passport.yandex.ru",
        "wordstat.yandex.ru",
        "www.shop.yandex.ru",
    ],
    19: [
        "login.microsoft.com",
        "blog.cloudflare.com",
        "platform.openai.com",
        "discover.google.com",
        "games-sdk.yandex.ru",
        "intern.facebook.com",
        "login.microsoft.com",
        "verify.xhamster.com",
    ],
    20: [
        "news.ycombinator.com",
        "analytics.google.com",
        "classroom.google.com",
        "m.alpha.facebook.com",
        "myapps.microsoft.com",
        "prod-wf1.discord.com",
        "prod-wf2.discord.com",
        "wordstat-2.yandex.ru",
    ],
    21: [
        "guard.oauth.yandex.ru",
        "internmc.facebook.com",
        "lti.gemini.google.com",
        "new.contest.yandex.ru",
        "static-maps.yandex.ru",
    ],
    22: [
        "entra360.microsoft.com",
        "identity.microsoft.com",
        "myaccess.microsoft.com",
        "mygroups.microsoft.com",
        "telemost-ios.yandex.ru",
    ],
    23: [
        "androiddiag.discord.com",
        "m.internmc.facebook.com",
        "myprofile.microsoft.com",
        "mysignins.microsoft.com",
        "vendor.market.yandex.ru",
    ],
    24: [
        "crowdtest.mail.yandex.ru",
        "developer.tech.yandex.ru",
        "secure.beta.facebook.com",
        "secure.prod.facebook.com",
        "trunkstable.facebook.com",
    ],
    25: [
        "creatorsblog.xhamster.com",
        "invitations.microsoft.com",
        "mystaff-ppe.microsoft.com",
        "privacysandbox.google.com",
        "secure.alpha.facebook.com",
    ],
    26: [
        "applications.microsoft.com",
        "entra360-dev.microsoft.com",
        "logistics.market.yandex.ru",
        "monitoring.cloud.yandex.ru",
        "mygroups-ppe.microsoft.com",
    ],
    27: [
        "api.myaccount.microsoft.com",
        "console.eu.cloud.google.com",
        "console.in.cloud.google.com",
        "myprofile-ppe.microsoft.com",
        "myworkaccount.microsoft.com",
    ],
    28: [
        "cert-test.sandbox.google.com",
        "crowdtest.calendar.yandex.ru",
        "myapplications.microsoft.com",
        "testmymfa.auth.microsoft.com",
    ],
    29: [
        "myaccess.canary.microsoft.com",
        "enterpriseservices.openai.com",
        "safety-enforcement.tiktok.com",
    ],
    30: [
        "content-reviewers.xhamster.com",
        "wms-povar.retailtech.yandex.ru",
    ],
    31: [
        "enterpriseregistration.avito.ru",
        "api.myworkaccount.microsoft.com",
        "lpc-outsource-release.yandex.ru",
        "lti.meet.usercontent.google.com",
        "myworkaccount-ppe.microsoft.com",
        "secure.trunkstable.facebook.com",
    ],
    32: [
        "lti.drive.usercontent.google.com",
        "mfavalidation.auth.microsoft.com",
        "myapplications-ppe.microsoft.com",
        "prestable.corp.browser.yandex.ru",
        "enterprisecatalogue.kaspersky.ru",
        "eu.safety-enforcement.tiktok.com",
        "www.certifiedbuilds.kaspersky.ru",
    ],
    33: [
        "datasetsearch.research.google.com",
        "lti.gemini.usercontent.google.com",
        "snowsgiving-tale-2022.discord.com",
    ],
    34: [
        "crowd.testing.schoolbook.yandex.ru",
        "monitoring-staging.cloud.yandex.ru",
        "pf.rc.crowdtest.plus.tst.yandex.ru",
        "auth.enterpriseservices.openai.com",
    ],
    35: [
        "api.myworkaccount-ppe.microsoft.com",
        "programmablesearchengine.google.com",
    ],
    36: [
        "lti.workspace.usercontent.google.com",
        "snowsgiving-tale-2022-da.discord.com",
        "snowsgiving-tale-2022-it.discord.com",
        "snowsgiving-tale-2022-ko.discord.com",
        "snowsgiving-tale-2022-nl.discord.com",
    ],
}


@dataclass
class HandshakeRecord:
    """TLS handshake data structure"""

    sni: str
    session_id: bytes
    random: bytes
    data: bytes

    def __post_init__(self):
        """Validate handshake data"""
        if len(self.random) != 32:
            raise ValueError(f"Invalid random length: {len(self.random)}")
        if len(self.session_id) > 32:
            raise ValueError(f"Session ID too long: {len(self.session_id)}")
        if len(self.data) < 50:
            raise ValueError(f"Handshake data too small: {len(self.data)}")


class TLSHandshakeCapture:
    """Captures TLS handshakes using tshark"""

    def __init__(
        self, interface: str = "en0", timeout: int = 3, browser: str = "chrome"
    ):
        self.interface = interface
        self.timeout = timeout
        self.browser = browser.lower()
        self.handshakes: List[HandshakeRecord] = []

    def _sanitize_version(self, version: str) -> str:
        """Convert version string to valid C++ identifier format"""
        # Replace dots, spaces, and special chars with underscores
        sanitized = re.sub(r"[^a-zA-Z0-9]", "_", version)
        # Remove consecutive underscores
        sanitized = re.sub(r"_+", "_", sanitized)
        # Remove trailing underscore
        sanitized = sanitized.strip("_")
        return sanitized

    def _get_browser_version(self) -> str:
        """Get browser version based on platform and browser choice"""
        browser_versions = {
            "chrome": self._get_chrome_version,
            "firefox": self._get_firefox_version,
            "yandex": self._get_yandex_version,
            "safari": self._get_safari_version,
        }

        if self.browser not in browser_versions:
            print(f"[WARNING] Unknown browser: {self.browser}, defaulting to chrome")
            return self._get_chrome_version()

        return browser_versions[self.browser]()

    def _get_chrome_version(self) -> str:
        """Get Chrome version across platforms"""
        system = platform.system()
        try:
            if system == "Windows":
                cmd = [
                    "reg",
                    "query",
                    "HKEY_CURRENT_USER\\Software\\Google\\Chrome\\BLBeacon",
                    "/v",
                    "version",
                ]
                result = subprocess.run(cmd, capture_output=True, text=True, shell=True)
                for line in result.stdout.split("\n"):
                    if "version" in line:
                        parts = line.split()
                        if parts:
                            return parts[-1].strip()
            elif system == "Darwin":  # macOS
                cmd = [
                    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
                    "--version",
                ]
                result = subprocess.run(cmd, capture_output=True, text=True)
                return result.stdout.strip().split()[-1]
            else:  # Linux
                cmd = ["google-chrome", "--version"]
                result = subprocess.run(cmd, capture_output=True, text=True)
                return result.stdout.strip().split()[-1]
        except:
            pass
        return "unknown"

    def _get_firefox_version(self) -> str:
        """Get Firefox version across platforms"""
        system = platform.system()
        try:
            if system == "Windows":
                cmd = [
                    "reg",
                    "query",
                    "HKLM\\Software\\Mozilla\\Mozilla Firefox",
                    "/v",
                    "CurrentVersion",
                ]
                result = subprocess.run(cmd, capture_output=True, text=True, shell=True)
                for line in result.stdout.split("\n"):
                    if "CurrentVersion" in line:
                        parts = line.split()
                        if parts:
                            return parts[-1].strip()
            elif system == "Darwin":  # macOS
                cmd = ["/Applications/Firefox.app/Contents/MacOS/firefox", "--version"]
                result = subprocess.run(cmd, capture_output=True, text=True)
                return result.stdout.strip().split()[-1]
            else:  # Linux
                cmd = ["firefox", "--version"]
                result = subprocess.run(cmd, capture_output=True, text=True)
                return result.stdout.strip().split()[-1]
        except:
            pass
        return "unknown"

    def _get_yandex_version(self) -> str:
        """Get Yandex Browser version across platforms"""
        system = platform.system()
        try:
            if system == "Windows":
                cmd = [
                    "reg",
                    "query",
                    "HKCU\\Software\\Yandex\\YandexBrowser\\BLBeacon",
                    "/v",
                    "version",
                ]
                result = subprocess.run(cmd, capture_output=True, text=True, shell=True)
                for line in result.stdout.split("\n"):
                    if "version" in line:
                        parts = line.split()
                        if parts:
                            return parts[-1].strip()
            elif system == "Darwin":  # macOS
                cmd = ["/Applications/Yandex.app/Contents/MacOS/Yandex", "--version"]
                result = subprocess.run(cmd, capture_output=True, text=True)
                return result.stdout.strip().split()[-1]
            else:  # Linux
                cmd = ["yandex-browser", "--version"]
                result = subprocess.run(cmd, capture_output=True, text=True)
                return result.stdout.strip().split()[-1]
        except:
            pass
        return "unknown"

    def _get_safari_version(self) -> str:
        """Get Safari version (macOS only)"""
        if platform.system() != "Darwin":
            return "not_available_on_this_platform"
        try:
            cmd = [
                "/usr/bin/defaults",
                "read",
                "/Applications/Safari.app/Contents/Info",
                "CFBundleShortVersionString",
            ]
            result = subprocess.run(cmd, capture_output=True, text=True)
            return result.stdout.strip()
        except:
            return "unknown"

    def _check_tshark(self) -> bool:
        """Verify tshark is installed and accessible"""
        try:
            result = subprocess.run(
                ["tshark", "--version"], capture_output=True, check=True
            )
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False

    def _launch_browser(self, url: str) -> None:
        """Launch selected browser and close after timeout"""
        system = platform.system()

        browser_commands = {
            "chrome": lambda u: self._launch_chrome(u, incognito=True),
            "firefox": lambda u: self._launch_firefox(u, private=True),
            "yandex": lambda u: self._launch_yandex(u, incognito=True),
            "safari": lambda u: self._launch_safari(u, private=True),
        }

        if self.browser in browser_commands:
            browser_commands[self.browser](url)
        else:
            self._launch_chrome(url)

        time.sleep(self.timeout)
        self._close_browser()

    def _launch_chrome(self, url: str, incognito: bool = True) -> None:
        """Launch Chrome browser"""
        system = platform.system()
        flags = ["--new-window"]
        if incognito:
            flags.append("--incognito")

        if system == "Windows":
            subprocess.Popen(
                ["start", "chrome"] + flags + [url],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                shell=True,
            )
        elif system == "Darwin":
            subprocess.Popen(
                ["open", "-a", "Google Chrome", "--args"] + flags + [url],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        else:  # Linux
            subprocess.Popen(
                ["google-chrome"] + flags + [url],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )

    def _launch_firefox(self, url: str, private: bool = True) -> None:
        """Launch Firefox browser"""
        system = platform.system()
        flags = ["-new-window"]
        if private:
            flags.append("--private-window")

        if system == "Windows":
            subprocess.Popen(
                ["start", "firefox"] + flags + [url],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                shell=True,
            )
        elif system == "Darwin":
            subprocess.Popen(
                ["open", "-a", "Firefox", "--args"] + flags + [url],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        else:  # Linux
            subprocess.Popen(
                ["firefox"] + flags + [url],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )

    def _launch_yandex(self, url: str, incognito: bool = True) -> None:
        """Launch Yandex Browser"""
        system = platform.system()
        flags = ["--new-window"]
        if incognito:
            flags.append("--incognito")

        if system == "Windows":
            subprocess.Popen(
                ["start", "yandex"] + flags + [url],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                shell=True,
            )
        elif system == "Darwin":
            subprocess.Popen(
                ["open", "-a", "Yandex", "--args"] + flags + [url],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        else:  # Linux
            subprocess.Popen(
                ["yandex-browser"] + flags + [url],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )

    def _launch_safari(self, url: str, private: bool = True) -> None:
        """Launch Safari browser (macOS only)"""
        if platform.system() != "Darwin":
            return

        flags = []
        if private:
            flags.append("--args")
            flags.append("-private")

        if flags:
            subprocess.Popen(
                ["open", "-a", "Safari", url] + flags,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        else:
            subprocess.Popen(
                ["open", "-a", "Safari", url],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )

    def _close_browser(self) -> None:
        """Close the launched browser"""
        system = platform.system()

        browser_processes = {
            "chrome": ["Google Chrome", "chrome", "google-chrome"],
            "firefox": ["Firefox", "firefox"],
            "yandex": ["Yandex", "yandex", "yandex-browser"],
            "safari": ["Safari"],
        }

        if self.browser in browser_processes:
            for proc in browser_processes[self.browser]:
                if system == "Windows":
                    subprocess.run(
                        ["taskkill", "/f", "/im", f"{proc}.exe"], capture_output=True
                    )
                elif system == "Darwin":  # macOS
                    applescript = '''
                    tell application "Firefox"
                        if it is running then
                            quit
                        end if
                    end tell
                    '''
                    subprocess.run(["osascript", "-e", applescript],
                                   capture_output=True, timeout=5)
                    time.sleep(2)
                    result = subprocess.run(["pgrep", "-f", "Firefox"],
                                            capture_output=True)
                    if result.returncode == 0:
                        subprocess.run(["pkill", "-TERM", "-f", "Firefox"],
                                       capture_output=True)
                        time.sleep(1)
                else:
                    subprocess.run(["pkill", "-f", proc], capture_output=True)

    def _extract_handshake_data(
        self, pcap_file: str, sni: str
    ) -> Optional[Tuple[bytes, bytes]]:
        """Extract reassembled handshake data from pcap file"""
        analyze_cmd = [
            "tshark",
            "-r",
            pcap_file,
            "-Y",
            f'tls.handshake.extensions_server_name == "{sni}"',
            "-T",
            "fields",
            "-e",
            "tcp.reassembled.data",
            "-e",
            "tls.handshake.session_id",
        ]

        result = subprocess.run(analyze_cmd, capture_output=True, text=True)

        if not result.stdout or not result.stdout.strip():
            return None

        lines = result.stdout.strip().split("\n")
        for line in lines:
            if not line.strip():
                continue

            parts = line.split("\t")
            tls_hex = parts[0].strip() if parts else ""

            if tls_hex and tls_hex != "None":
                tls_hex = tls_hex.replace(":", "")
                tls_bytes = bytes.fromhex(tls_hex)

                session_id = b""
                if len(parts) > 1 and parts[1] and parts[1] != "None":
                    sid_hex = parts[1].replace(":", "")
                    session_id = bytes.fromhex(sid_hex)

                return tls_bytes, session_id

        return None

    def _extract_random(self, handshake_data: bytes) -> bytes:
        """Extract random bytes from ClientHello (bytes 11-43)"""
        if len(handshake_data) < 43:
            raise ValueError(
                f"Handshake too short for random extraction: {len(handshake_data)} bytes"
            )
        return handshake_data[11:43]

    def capture(self, sni: str) -> bool:
        """Capture TLS handshake for a single SNI"""
        with tempfile.NamedTemporaryFile(suffix=".pcap", delete=False) as tmpfile:
            pcap_file = tmpfile.name

        try:
            capture_cmd = [
                "tshark",
                "-i",
                self.interface,
                "-f",
                f"tcp port 443 and host {sni}",
                "-a",
                f"duration:{self.timeout + 1}",
                "-w",
                pcap_file,
            ]

            capture_proc = subprocess.Popen(
                capture_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
            )

            self._launch_browser(f"https://{sni}")
            capture_proc.wait(timeout=self.timeout + 2)

            extracted = self._extract_handshake_data(pcap_file, sni)
            if not extracted:
                return False

            handshake_data, session_id = extracted
            random_bytes = self._extract_random(handshake_data)

            record = HandshakeRecord(
                sni=sni, session_id=session_id, random=random_bytes, data=handshake_data
            )
            self.handshakes.append(record)

            print(f"[CAPTURED] {sni}")
            print(f"    session_id: {session_id.hex() if session_id else 'none'}")
            print(f"    random: {random_bytes.hex()}")
            print(f"    size: {len(handshake_data)} bytes")

            return True

        except subprocess.TimeoutExpired:
            print(f"[ERROR] Capture timeout for {sni}")
            return False
        except Exception as e:
            print(f"[ERROR] Failed to capture {sni}: {e}")
            return False
        finally:
            if os.path.exists(pcap_file):
                os.unlink(pcap_file)

    def capture_all(
        self, domains_by_length: Dict[int, List[str]], needed_per_length: int = 1
    ) -> Dict[str, int]:
        results = {}
        for length, domains in domains_by_length.items():
            if not domains:
                continue
            successful = 0
            while successful < needed_per_length:
                domain = random.choice(domains)
                print(f"  -> Trying {domain}")
                success = self.capture(domain)
                results[domain] = success
                if success:
                    successful += 1
                    print(f"  [OK] {successful}/{needed_per_length}")
                else:
                    print(f"  [FAIL] trying another")
        return results

    def generate_cpp_output(self, output_dir: str = ".") -> Optional[str]:
        if not self.handshakes:
            print("[ERROR] No handshakes captured")
            return None

        # Get browser version for filename and variable name
        browser_version = self._get_browser_version()
        browser_version_clean = self._sanitize_version(browser_version)

        # Create filename: browsername_version.cpp
        filename = Path(output_dir) / f"{self.browser}_{browser_version_clean}.cpp"

        # Create variable name
        browser_capitalized = self.browser.capitalize()
        variable_name = f"kBrowser{browser_capitalized}_{browser_version_clean}"

        # Group by SNI length for C++ structure
        grouped: Dict[int, List[HandshakeRecord]] = defaultdict(list)
        for hs in self.handshakes:
            grouped[len(hs.sni)].append(hs)

        with open(filename, "w") as f:
            f.write("// Auto-generated TLS Handshake Data\n")
            f.write(f"// Generated: {datetime.now().isoformat()}\n")
            f.write(f"// Browser: {self.browser} {browser_version}\n")
            f.write(f"// Platform: {platform.system()} {platform.release()}\n")
            f.write(f"// Total records: {len(self.handshakes)}\n\n")

            f.write("#include <array>\n")
            f.write("#include <cstdint>\n")
            f.write("#include <string>\n")
            f.write("#include <unordered_map>\n")
            f.write("#include <vector>\n\n")

            f.write('#include "src/browsers/handshake_data.h"\n\n')

            f.write("namespace camouflage::tls {\n\n")

            f.write(f"extern const HandshakeData {variable_name} = {{\n")

            sni_lengths = sorted(grouped.keys())
            for len_idx, sni_len in enumerate(sni_lengths):
                # Ключ мапы - длина SNI
                f.write(f"    {{{sni_len}, {{\n")  # Открываем вектор

                records = grouped[sni_len]
                for rec_idx, hs in enumerate(records):
                    f.write("        {\n")
                    f.write(f'            .sni = "{hs.sni}",\n')

                    # Session ID (pad with zeros to 32 bytes)
                    sid = hs.session_id
                    sid_list = [f"0x{b:02x}" for b in sid]
                    if len(sid_list) < 32:
                        sid_list.extend(["0x00"] * (32 - len(sid)))
                    f.write(f"            .session_id = {{{', '.join(sid_list)}}},\n")

                    # Random (always 32 bytes)
                    rand = hs.random
                    rand_list = [f"0x{b:02x}" for b in rand]
                    f.write(f"            .random = {{{', '.join(rand_list)}}},\n")

                    # Handshake packet data
                    data = hs.data
                    data_lines = []
                    for i in range(0, len(data), 16):
                        chunk = data[i : i + 16]
                        hex_bytes = ", ".join(f"0x{b:02x}" for b in chunk)
                        data_lines.append(f"                {hex_bytes}")

                    data_str = ",\n".join(data_lines)
                    f.write(
                        f"            .handshake_packet = {{\n{data_str}\n            }}\n"
                    )
                    f.write("        }")

                    if rec_idx < len(records) - 1:
                        f.write(",\n")
                    else:
                        f.write("\n")

                f.write("    }}")

                if len_idx < len(sni_lengths) - 1:
                    f.write(",\n")
                else:
                    f.write("\n")

            f.write("};\n\n")

            # Close the namespace
            f.write("}  // namespace camouflage::tls\n")

        print(f"[GENERATED] {filename} ({len(self.handshakes)} records)")
        print(f"[BROWSER] {self.browser} version {browser_version}")
        print(f"[VARIABLE] const HandshakeData {variable_name}")
        return str(filename)

    def print_summary(self) -> None:
        """Print capture summary"""
        print(f"\n[SUMMARY] Captured: {len(self.handshakes)} handshakes")
        for hs in self.handshakes:
            print(f"  {hs.sni}: {len(hs.data)} bytes")


def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="Capture TLS handshakes for specified SNIs"
    )
    parser.add_argument(
        "-i",
        "--interface",
        default="en0",
        help="Network interface to capture from (default: en0)",
    )
    parser.add_argument(
        "-c",
        "--count",
        type=int,
        default=1,
        help="Number of handshakes to capture for EACH domain length",
    )
    parser.add_argument(
        "-w",
        "--wait",
        type=int,
        default=7,
        help="Wait time in seconds before closing browser (default: 3)",
    )
    parser.add_argument(
        "-o",
        "--output",
        default=".",
        help="Output directory for generated C++ file (default: current directory)",
    )
    parser.add_argument(
        "--repeat",
        type=int,
        default=1,
        help="Number of capture iterations (default: 1)",
    )
    parser.add_argument(
        "-b",
        "--browser",
        choices=["chrome", "firefox", "yandex", "safari"],
        default="chrome",
        help="Browser to use for capture (default: chrome)",
    )

    return parser.parse_args()


def main() -> int:
    """Main entry point"""
    args = parse_arguments()

    print("=" * 60)
    print("TLS HANDSHAKE CAPTURE TOOL")
    print("=" * 60)
    print(f"Interface: {args.interface}")
    print(f"Wait time: {args.wait}s")
    print(f"Count: {args.count}")
    print(f"Iterations: {args.repeat}")
    print(f"Browser: {args.browser}")
    print(f"Platform: {platform.system()} {platform.release()}")
    print(f"Output dir: {args.output}")
    print("=" * 60)

    capture = TLSHandshakeCapture(
        interface=args.interface, timeout=args.wait, browser=args.browser
    )

    if not capture._check_tshark():
        print(
            "[ERROR] tshark not found. Install with: brew install wireshark (macOS) or apt-get install tshark (Linux)"
        )
        return 1

    all_handshakes = []

    for iteration in range(args.repeat):
        if args.repeat > 1:
            print(f"\n[ITERATION {iteration + 1}/{args.repeat}]")

        capture.handshakes = []
        capture.capture_all(DOMAINS_BY_LENGTH, needed_per_length=args.count)

        if capture.handshakes:
            all_handshakes.extend(capture.handshakes)
            capture.print_summary()

    if all_handshakes:
        capture.handshakes = all_handshakes
        output_file = capture.generate_cpp_output(args.output)
        if output_file:
            print(f"\n[SUCCESS] Handshake data saved to: {output_file}")
        return 0
    else:
        return 1


if __name__ == "__main__":
    sys.exit(main())
