import os
import struct
import re

def patch_launcher_binary(src_exe, dst_exe):
    with open(src_exe, 'rb') as f:
        data = bytearray(f.read())

    orig_size = len(data)
    print(f"Original file size: {orig_size} bytes")

    # 1. Patch Config::Config() version values in .text
    # Pattern: 48 c7 05 68 4f 53 00 0b 00 00 00 bb 03 00 00 00
    pat = b'\x48\xc7\x05\x68\x4f\x53\x00\x0b\x00\x00\x00\xbb\x03\x00\x00\x00'
    idx = data.find(pat)
    if idx != -1:
        # Change VERSION_MAJOR from 11 (0x0b) to 1 (0x01)
        # Change VERSION_PATCH from 3 (0x03) to 0 (0x00)
        rep = b'\x48\xc7\x05\x68\x4f\x53\x00\x01\x00\x00\x00\xbb\x00\x00\x00\x00'
        data[idx:idx+len(rep)] = rep
        print("  ✅ Patched Config::Config() VERSION_MAJOR=1, VERSION_PATCH=0 (v1.0.0)")

    # 2. Patch printableVersionString literal
    # 0x7c2d6c: '11.0.3\x00' (7 bytes) -> '1.0.0\x00\x00' (7 bytes)
    s_1000 = b'1.0.0\x00\x00'
    idx_str = data.find(b'cdn.modrinth.com\x00\x00\x00\x0011.0.3\x00')
    if idx_str != -1:
        data[idx_str+20:idx_str+27] = s_1000
        print(f"  ✅ Patched printableVersionString literal to '1.0.0'")

    # 3. Patch PrismLauncher/11.0.3 User Agent (21 bytes)
    idx_ua = data.find(b'PrismLauncher/11.0.3\x00')
    if idx_ua != -1:
        data[idx_ua:idx_ua+21] = b'SIRLauncher/1.0.0\x00\x00\x00\x00'
        print("  ✅ Patched User-Agent to 'SIRLauncher/1.0.0'")

    # 4. Patch LAUNCHER_DISPLAYNAME 'Prism Launcher' (14 bytes) -> 'SIR Launcher\x00\x00' (14 bytes)
    # The null terminator ensures clean rendering with no trailing whitespace!
    p_disp = b'Prism Launcher'
    p_sir = b'SIR Launcher\x00\x00'
    count_disp = 0
    for m in list(re.finditer(re.escape(p_disp), data)):
        data[m.start():m.end()] = p_sir
        count_disp += 1
    print(f"  ✅ Replaced {count_disp} UTF-8 occurrences of 'Prism Launcher' -> 'SIR Launcher'")

    # Replace UTF-16 occurrences of Prism Launcher (28 bytes) -> 'SIR Launcher\x00\x00' (28 bytes)
    p_disp_u16 = 'Prism Launcher'.encode('utf-16le')
    p_sir_u16 = 'SIR Launcher\x00\x00'.encode('utf-16le')
    count_disp_u16 = 0
    for m in list(re.finditer(re.escape(p_disp_u16), data)):
        data[m.start():m.end()] = p_sir_u16
        count_disp_u16 += 1
    print(f"  ✅ Replaced {count_disp_u16} UTF-16 occurrences of 'Prism Launcher' -> 'SIR Launcher'")

    # 5. Patch PrismLauncher\x00 (14 bytes) -> SIR Launcher\x00\x00 (14 bytes)
    p_name = b'PrismLauncher\x00'
    p_sir_name = b'SIR Launcher\x00\x00'
    for m in list(re.finditer(re.escape(p_name), data)):
        data[m.start():m.end()] = p_sir_name

    # 6. Patch PE Version info strings ('11.0.3.0' = 16 bytes -> '1.0.0.0\x00' in utf-16le = 16 bytes)
    v_old = '11.0.3.0'.encode('utf-16le')
    v_new = '1.0.0.0\x00'.encode('utf-16le')
    for m in list(re.finditer(re.escape(v_old), data)):
        data[m.start():m.end()] = v_new
    print("  ✅ Patched PE version resource strings to 1.0.0.0")

    # 7. Manifest version ('version="11.0.3.0"' = 18 bytes -> 'version="1.0.0.0" ' = 18 bytes)
    m_old = b'version="11.0.3.0"'
    m_new = b'version="1.0.0.0" '
    for m in list(re.finditer(re.escape(m_old), data)):
        data[m.start():m.end()] = m_new
    print("  ✅ Patched XML manifest version to 1.0.0.0")

    # 8. Sanitize Prism telemetry / URLs
    url_replacements = [
        (b'https://prismlauncher.org/feed/feed.xml\x00', b'\x00' * len(b'https://prismlauncher.org/feed/feed.xml\x00')),
        (b'https://github.com/PrismLauncher/PrismLauncher/issues\x00', b'https://linktr.ee/sir.ahmed\x00'.ljust(len(b'https://github.com/PrismLauncher/PrismLauncher/issues\x00'), b'\x00')),
        (b'https://prismlauncher.org/matrix\x00', b'https://linktr.ee/sir.ahmed\x00'.ljust(len(b'https://prismlauncher.org/matrix\x00'), b'\x00')),
        (b'https://prismlauncher.org/discord\x00', b'https://linktr.ee/sir.ahmed\x00'.ljust(len(b'https://prismlauncher.org/discord\x00'), b'\x00')),
        (b'https://prismlauncher.org/reddit\x00', b'https://linktr.ee/sir.ahmed\x00'.ljust(len(b'https://prismlauncher.org/reddit\x00'), b'\x00')),
        (b'https://prismlauncher.org/news\x00', b'https://linktr.ee/sir.ahmed\x00'.ljust(len(b'https://prismlauncher.org/news\x00'), b'\x00')),
        (b'https://prismlauncher.org/wiki/\x00', b'https://linktr.ee/sir.ahmed\x00'.ljust(len(b'https://prismlauncher.org/wiki/\x00'), b'\x00')),
    ]
    for old_u, new_u in url_replacements:
        idx_u = data.find(old_u)
        if idx_u != -1:
            data[idx_u:idx_u+len(old_u)] = new_u
            print(f"  ✅ Sanitized URL: {old_u[:30].decode('latin1')}...")

    assert len(data) == orig_size, f"Size mismatch: {len(data)} != {orig_size}"
    with open(dst_exe, 'wb') as f:
        f.write(data)
    print(f"🎉 Successfully created white-labeled binary: {dst_exe} ({len(data)} bytes, 100% exact size)\n")

if __name__ == '__main__':
    src = r'D:\Projects\SIR ModPack\SIR Package\SIR Launcher\prismlauncher.exe'
    dst = r'D:\Projects\SIR ModPack\SIR Package\SIR Launcher\SIR Launcher.exe'
    patch_launcher_binary(src, dst)
