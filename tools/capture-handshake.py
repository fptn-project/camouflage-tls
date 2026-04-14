import os
import re
import sys
import time
import copy
import socket
import signal
import atexit
import random
import tempfile
import argparse
import platform
import threading
import subprocess

from pathlib import Path
from datetime import datetime
from collections import defaultdict
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass


def generate_domains_by_length(min_length=4, max_length=65) -> Dict[int, List[str]]:
    domains_by_length = defaultdict(list)
    #domains_by_length[1] = ["t.m"]

    # Generate for lengths 4 through 64
    for length in range(min_length, max_length):
        random_part_len = length - 4
        chars = "0123456789"
        random_part = "".join(random.choices(chars, k=random_part_len))
        domain = f"t{random_part}.me"
        domains_by_length[length].append(domain)
    return dict(domains_by_length)


DOMAINS_BY_LENGTH = generate_domains_by_length()


class HostsPatcher:
    def __init__(self):
        self.hosts_path = (
            "/etc/hosts"
            if platform.system() != "Windows"
            else r"C:\Windows\System32\drivers\etc\hosts"
        )
        self.backup_content = None
        self.marker_start = "# TLS_FAKE_DOMAINS_START"
        self.marker_end = "# TLS_FAKE_DOMAINS_END"

    def _get_all_domains(self) -> List[str]:
        domains = []
        for length in range(4, 65):
            if length in DOMAINS_BY_LENGTH:
                domains.append(DOMAINS_BY_LENGTH[length][0])
        return domains

    def patch(self) -> None:
        domains = self._get_all_domains()
        with open(self.hosts_path, "r") as f:
            content = f.read()

        self.backup_content = content
        lines = content.splitlines()
        new_lines = []
        skip = False
        for line in lines:
            if self.marker_start in line:
                skip = True
                continue
            if skip and self.marker_end in line:
                skip = False
                continue
            if not skip:
                new_lines.append(line)
        new_lines.append(self.marker_start)
        for domain in domains:
            new_lines.append(f"127.0.0.1 {domain}")
        new_lines.append(self.marker_end)

        with open(self.hosts_path, "w") as f:
            f.write("\n".join(new_lines) + "\n")
        print(f"[HOSTS] Added {len(domains)} fake domains")

    def restore(self) -> None:
        if self.backup_content is None:
            return

        with open(self.hosts_path, "r") as f:
            current = f.read()

        lines = current.splitlines()
        new_lines = []
        skip = False

        for line in lines:
            if self.marker_start in line:
                skip = True
                continue
            if skip and self.marker_end in line:
                skip = False
                continue
            if not skip:
                new_lines.append(line)

        with open(self.hosts_path, "w") as f:
            f.write("\n".join(new_lines) + "\n")

        print("[HOSTS] Removed fake domains")


class TCPBlackHole:
    def __init__(self, expected_sni, host="127.0.0.1", port=443):
        self.expected_sni = expected_sni
        self.host = host
        self.port = port
        self.server = None
        self.running = False

        self.handshakes = []

    def clear_handshakes(self):
        self.handshakes = []

    def get_handshakes(self):
        return copy.deepcopy(self.handshakes)

    def start(self):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind((self.host, self.port))
        self.server.listen(100)
        self.running = True

        thread = threading.Thread(target=self._accept, daemon=True)
        thread.start()

    def _extract_info(self, data: bytes) -> tuple:
        try:
            if len(data) < 5 or data[0] != 0x16:
                return None, b"\x00" * 32, b"\x00" * 32

            offset = 5
            # ClientHello: type(1) + length(3)
            if data[offset] != 0x01:
                return None, b"\x00" * 32, b"\x00" * 32

            handshake_length = int.from_bytes(data[offset + 1 : offset + 4], "big")
            offset += 4

            # TLS version (2 bytes)
            offset += 2

            # Random (32 bytes)
            random = data[offset : offset + 32]
            offset += 32

            # Session ID length
            session_id_len = data[offset]
            offset += 1

            # Session ID
            if session_id_len > 0:
                session_id = data[offset : offset + session_id_len]
                offset += session_id_len
            else:
                session_id = b""

            session_id = session_id.ljust(32, b"\x00")
            sni = None
            if offset + 2 > len(data):
                return sni, session_id, random
            cipher_len = int.from_bytes(data[offset : offset + 2], "big")
            offset += 2 + cipher_len
            if offset >= len(data):
                return sni, session_id, random
            comp_len = data[offset]
            offset += 1 + comp_len
            if offset + 2 > len(data):
                return sni, session_id, random
            ext_len = int.from_bytes(data[offset : offset + 2], "big")
            offset += 2

            end = offset + ext_len

            # SNI extension (type = 0)
            while offset + 4 <= end and offset + 4 <= len(data):
                ext_type = int.from_bytes(data[offset : offset + 2], "big")
                ext_len = int.from_bytes(data[offset + 2 : offset + 4], "big")
                offset += 4
                if ext_type == 0:  # SNI
                    if offset + 2 <= len(data):
                        # Пропускаем sni_list_length (2 байта)
                        sni_list_len = int.from_bytes(data[offset : offset + 2], "big")
                        offset += 2

                        # sni_type (1 байт) - должен быть 0
                        sni_type = data[offset]
                        offset += 1
                        # sni_host_len (2 байта)
                        sni_host_len = int.from_bytes(data[offset : offset + 2], "big")
                        offset += 2
                        # Сам hostname
                        if offset + sni_host_len <= len(data):
                            sni = data[offset : offset + sni_host_len].decode("utf-8")
                    break
                offset += ext_len
            return sni, session_id, random

        except Exception as e:
            print(f"Parse error: {e}")
            return None, b"\x00" * 32, b"\x00" * 32

    def _accept(self):
        while self.running:
            try:
                client, addr = self.server.accept()
                try:
                    client.settimeout(1)
                    data = client.recv(1024 * 16)
                    if data and len(data) > 1500:
                        sni, session_id, random = self._extract_info(data)
                        if sni and session_id and random and sni == self.expected_sni:
                            self.handshakes.append(
                                {
                                    "sni": sni,
                                    "random": random,
                                    "session_id": session_id,
                                    "data": data,
                                }
                            )
                    client.close()
                except Exception as e:
                    print(f"  Error: {e}")
                    client.close()
            except Exception as e:
                print(f"[TCP] Accept error: {e}")

    def stop(self):
        self.running = False
        if self.server:
            self.server.close()
        print("[TCP] Stopped")


@dataclass
class HandshakeRecord:
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
    """Captures TLS handshakes using TCPBlackHole (no tshark)"""

    def __init__(self, timeout: int = 3, browser: str = "chrome"):
        self.timeout = timeout
        self.browser = browser.lower()
        self.handshakes: List[HandshakeRecord] = []
        self.blackhole = None

    def set_blackhole(self, blackhole):
        self.blackhole = blackhole

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

        browser_config = {
            "chrome": {
                "names": ["Google Chrome", "chrome", "google-chrome"],
                "app_name": "Google Chrome",
                "process": "chrome",
            },
            "firefox": {
                "names": ["Firefox", "firefox"],
                "app_name": "Firefox",
                "process": "firefox",
            },
            "yandex": {
                "names": ["Yandex", "yandex", "yandex-browser"],
                "app_name": "Yandex",
                "process": "yandex",
            },
            "safari": {"names": ["Safari"], "app_name": "Safari", "process": "safari"},
        }

        if self.browser not in browser_config:
            return

        config = browser_config[self.browser]

        if system == "Windows":
            for proc in config["names"]:
                subprocess.run(
                    ["taskkill", "/f", "/im", f"{proc}.exe"],
                    capture_output=True,
                    timeout=3,
                )
        elif system == "Darwin":  # macOS
            # Use AppleScript to quit the browser gracefully
            applescript = f"""
                tell application "{config['app_name']}"
                    if it is running then
                        quit
                    end if
                end tell
                """
            subprocess.run(
                ["osascript", "-e", applescript], capture_output=True, timeout=5
            )
            time.sleep(1)

            # Force kill if still running
            result = subprocess.run(
                ["pgrep", "-f", config["process"]], capture_output=True
            )
            if result.returncode == 0:
                subprocess.run(
                    ["pkill", "-TERM", "-f", config["process"]],
                    capture_output=True,
                    timeout=3,
                )
                time.sleep(1)
        else:  # Linux
            for proc in config["names"]:
                subprocess.run(["pkill", "-f", proc], capture_output=True, timeout=3)

    def capture_all(
        self, domains_by_length: Dict[int, List[str]], needed_per_length: int = 1
    ) -> Dict[str, bool]:
        results = {}

        for length, domains in domains_by_length.items():
            if not domains:
                continue

            successful = 0
            while successful < needed_per_length:
                # Берем один домен
                domain = random.choice(domains)

                # Сколько еще нужно захватить для этого домена
                remaining = needed_per_length - successful
                batch_size = min(remaining, 10)

                blackhole = TCPBlackHole(expected_sni=domain)
                blackhole.start()

                time.sleep(0.5)

                self._launch_browser(f"https://{domain}")

                captured = blackhole.get_handshakes()
                blackhole.stop()

                print(f"    Captured {len(captured)} handshakes")

                for hs in captured:
                    if hs["sni"] == domain and successful < needed_per_length:
                        record = HandshakeRecord(
                            sni=hs["sni"],
                            session_id=hs["session_id"],
                            random=hs["random"],
                            data=hs["data"],
                        )
                        self.handshakes.append(record)
                        successful += 1
                        print(
                            f"    [OK] {hs['sni']} ({successful}/{needed_per_length})"
                        )
                if successful >= needed_per_length:
                    break

        return results

    def _sanitize_version(self, version: str) -> str:
        sanitized = re.sub(r"[^a-zA-Z0-9]", "_", version)
        sanitized = re.sub(r"_+", "_", sanitized)
        sanitized = sanitized.strip("_")
        return sanitized

    def _get_browser_version(self) -> str:
        browser_versions = {
            "chrome": self._get_chrome_version,
            "firefox": self._get_firefox_version,
            "yandex": self._get_yandex_version,
            "safari": self._get_safari_version,
        }
        if self.browser not in browser_versions:
            return "unknown"
        return browser_versions[self.browser]()

    def _get_chrome_version(self) -> str:
        system = platform.system()
        try:
            if system == "Darwin":
                cmd = [
                    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
                    "--version",
                ]
                result = subprocess.run(cmd, capture_output=True, text=True)
                return result.stdout.strip().split()[-1]
            elif system == "Windows":
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
            else:
                cmd = ["google-chrome", "--version"]
                result = subprocess.run(cmd, capture_output=True, text=True)
                return result.stdout.strip().split()[-1]
        except:
            pass
        return "unknown"

    def _get_firefox_version(self) -> str:
        system = platform.system()
        try:
            if system == "Darwin":
                cmd = ["/Applications/Firefox.app/Contents/MacOS/firefox", "--version"]
                result = subprocess.run(cmd, capture_output=True, text=True)
                return result.stdout.strip().split()[-1]
            elif system == "Windows":
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
            else:
                cmd = ["firefox", "--version"]
                result = subprocess.run(cmd, capture_output=True, text=True)
                return result.stdout.strip().split()[-1]
        except:
            pass
        return "unknown"

    def _get_yandex_version(self) -> str:
        system = platform.system()
        try:
            if system == "Darwin":
                cmd = ["/Applications/Yandex.app/Contents/MacOS/Yandex", "--version"]
                result = subprocess.run(cmd, capture_output=True, text=True)
                return result.stdout.strip().split()[-1]
            elif system == "Windows":
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
            else:
                cmd = ["yandex-browser", "--version"]
                result = subprocess.run(cmd, capture_output=True, text=True)
                return result.stdout.strip().split()[-1]
        except:
            pass
        return "unknown"

    def _get_safari_version(self) -> str:
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

    def generate_cpp_output(
        self, output_dir: str = ".", count: int = 5
    ) -> Optional[str]:
        if not self.handshakes:
            return None

        browser_version = self._get_browser_version()
        browser_version_clean = self._sanitize_version(browser_version)

        browser_dir = Path(output_dir) / f"{self.browser}_{browser_version_clean}"
        browser_dir.mkdir(parents=True, exist_ok=True)

        base_name = f"{self.browser}_{browser_version_clean}"
        h_file = browser_dir / f"{base_name}.hpp"
        cpp_file = browser_dir / f"{base_name}.cpp"

        browser_capitalized = self.browser.capitalize()
        variable_name = f"kBrowser{browser_capitalized}_{browser_version_clean}"

        grouped: Dict[int, List[HandshakeRecord]] = defaultdict(list)
        for hs in self.handshakes:
            grouped[len(hs.sni)].append(hs)

        # Maximum records per entry (matches TLS_MAX_RECORDS from C++ header)
        MAX_RECORDS_PER_ENTRY = count

        with open(h_file, "w") as f:
            f.write("// Auto-generated TLS Handshake Data\n")
            f.write(f"// Generated: {datetime.now().isoformat()}\n")
            f.write(f"// Browser: {self.browser} {browser_version}\n\n")
            f.write("#pragma once\n\n")
            f.write('#include "camouflage/tls/types.hpp"\n\n')
            f.write("namespace camouflage::tls {\n\n")
            f.write(f"extern const HandshakeData {variable_name};\n\n")
            f.write("}  // namespace camouflage::tls\n")

        with open(cpp_file, "w") as f:
            f.write("// Auto-generated TLS Handshake Data\n")
            f.write(f"// Generated: {datetime.now().isoformat()}\n")
            f.write(f"// Browser: {self.browser} {browser_version}\n\n")
            f.write(f'#include "{base_name}.hpp"\n\n')
            f.write('#include "camouflage/tls/types.hpp"\n\n')
            f.write("namespace camouflage::tls {\n\n")

            f.write(f"const HandshakeData {variable_name} = {{\n")
            f.write(f"    .entry_count = {len(grouped)},\n")
            f.write(f"    .entries = {{\n")

            for sni_len, records in sorted(grouped.items()):
                # Split records into chunks of MAX_RECORDS_PER_ENTRY
                for chunk_idx in range(0, len(records), MAX_RECORDS_PER_ENTRY):
                    chunk = records[chunk_idx : chunk_idx + MAX_RECORDS_PER_ENTRY]

                    f.write(f"        {{\n")
                    f.write(f"            .sni_length = {sni_len},\n")
                    f.write(f"            .record_count = {len(chunk)},\n")
                    f.write(f"            .records = {{\n")

                    for hs in chunk:
                        f.write(f"                {{\n")

                        # SNI (string with null terminator)
                        sni_str = hs.sni
                        sni_bytes = sni_str.encode() + b"\x00"
                        sni_hex = ", ".join(
                            f"'{chr(b)}'" if b >= 32 and b < 127 else f"0x{b:02x}"
                            for b in sni_bytes
                        )
                        f.write(f"                    .sni = {{{sni_hex}}},\n")

                        # Session ID (32 bytes)
                        sid = hs.session_id.ljust(32, b"\x00")
                        sid_hex = ", ".join(f"0x{b:02x}" for b in sid)
                        f.write(f"                    .session_id = {{{sid_hex}}},\n")

                        # Random (32 bytes)
                        rand = hs.random
                        rand_hex = ", ".join(f"0x{b:02x}" for b in rand)
                        f.write(f"                    .random = {{{rand_hex}}},\n")

                        # Handshake packet
                        data = hs.data
                        f.write(f"                    .handshake_packet = {{\n")
                        for i in range(0, len(data), 16):
                            chunk_data = data[i : i + 16]
                            hex_bytes = ", ".join(f"0x{b:02x}" for b in chunk_data)
                            f.write(f"                        {hex_bytes},\n")
                        # Pad to TLS_MAX_PACKET_SIZE (2048)
                        if len(data) < 2048:
                            f.write(
                                f"                        {', '.join(['0x00'] * (2048 - len(data)))}\n"
                            )
                        f.write(f"                    }},\n")
                        f.write(
                            f"                    .handshake_packet_size = {len(data)}\n"
                        )
                        f.write(f"                }},\n")

                    f.write(f"            }}\n")
                    f.write(f"        }},\n")

            f.write(f"    }}\n")
            f.write(f"}};\n\n")

            f.write("}  // namespace camouflage::tls\n")

        print(f"[GENERATED] {browser_dir}/")
        print(f"  - {h_file.name}")
        print(f"  - {cpp_file.name}")

        return str(browser_dir)

    def print_summary(self) -> None:
        print(f"\n[SUMMARY] Captured: {len(self.handshakes)} handshakes")
        for hs in self.handshakes:
            print(f"  {hs.sni}: {len(hs.data)} bytes")


def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="Capture TLS handshakes for specified SNIs"
    )
    parser.add_argument(
        "-c",
        "--count",
        type=int,
        default=5,
        help="Number of handshakes to capture for EACH domain length (max 5)",
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
    args = parser.parse_args()
    if args.count > 5:
        print(f"[WARNING] Count {args.count} exceeds maximum 5, reducing to 5")
        args.count = 5

    if args.count < 1:
        print(f"[WARNING] Count {args.count} is less than 1, setting to 1")
        args.count = 1
    return args


def main() -> int:
    """Main entry point"""
    args = parse_arguments()

    print("=" * 60)
    print("TLS HANDSHAKE CAPTURE TOOL")
    print("=" * 60)
    # print(f"Interface: {args.interface}")
    print(f"Wait time: {args.wait}s")
    print(f"Count: {args.count}")
    print(f"Iterations: {args.repeat}")
    print(f"Browser: {args.browser}")
    print(f"Platform: {platform.system()} {platform.release()}")
    print(f"Output dir: {args.output}")
    print("=" * 60)

    patcher = HostsPatcher()

    def cleanup():
        patcher.restore()
        sys.exit(0)

    signal.signal(signal.SIGINT, lambda s, f: cleanup())
    signal.signal(signal.SIGTERM, lambda s, f: cleanup())
    atexit.register(cleanup)

    print("\n[SETUP] Patching /etc/hosts...")
    patcher.patch()

    capture = TLSHandshakeCapture(timeout=args.wait, browser=args.browser)

    all_handshakes = []
    for iteration in range(args.repeat):
        if args.repeat > 1:
            print(f"\n[ITERATION {iteration + 1}/{args.repeat}]")

        capture.handshakes = []
        capture.capture_all(DOMAINS_BY_LENGTH, needed_per_length=args.count)

        if capture.handshakes:
            all_handshakes.extend(capture.handshakes)
            capture.print_summary()

    patcher.restore()

    if all_handshakes:
        capture.handshakes = all_handshakes
        output_file = capture.generate_cpp_output(args.output, args.count)
        if output_file:
            print(f"\n[SUCCESS] Handshake data saved to: {output_file}")
        return 0
    else:
        return 1


if __name__ == "__main__":
    sys.exit(main())
