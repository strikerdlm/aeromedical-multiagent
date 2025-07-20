import subprocess
import sys
import ipaddress
import platform
import concurrent.futures
import socket

def ping_host(ip):
    """Ping a single IP address"""
    try:
        # Use ping command based on OS
        if platform.system().lower() == 'windows':
            result = subprocess.run(['ping', '-n', '1', '-w', '1000', str(ip)], 
                                  capture_output=True, text=True, timeout=5)
        else:
            result = subprocess.run(['ping', '-c', '1', '-W', '1', str(ip)], 
                                  capture_output=True, text=True, timeout=5)
        
        if result.returncode == 0:
            return str(ip)
    except:
        pass
    return None

def get_hostname_and_mac(ip):
    """Try to get hostname and MAC address for an IP"""
    hostname = "Unknown"
    mac = "Unknown"
    
    try:
        # Try to get hostname
        hostname = socket.gethostbyaddr(ip)[0]
    except:
        pass
    
    try:
        # Try to get MAC address from ARP table
        if platform.system().lower() == 'windows':
            result = subprocess.run(['arp', '-a', ip], capture_output=True, text=True)
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                for line in lines:
                    if ip in line:
                        parts = line.split()
                        if len(parts) >= 2:
                            mac = parts[1]
                            break
    except:
        pass
    
    return hostname, mac

def identify_raspberry_pi(ip, hostname, mac):
    """Try to identify if device is a Raspberry Pi"""
    indicators = []
    
    # Check hostname patterns
    if hostname.lower().startswith('raspberry') or 'pi' in hostname.lower():
        indicators.append("Hostname suggests Raspberry Pi")
    
    # Check MAC address OUI (first 3 bytes) for Raspberry Pi Foundation
    if mac != "Unknown":
        mac_clean = mac.replace('-', ':').replace('.', ':').upper()
        # Common Raspberry Pi MAC prefixes
        rpi_prefixes = [
            'B8:27:EB',  # Raspberry Pi Foundation
            'DC:A6:32',  # Raspberry Pi Foundation
            'E4:5F:01',  # Raspberry Pi Foundation
            '28:CD:C1',  # Raspberry Pi Foundation
        ]
        
        for prefix in rpi_prefixes:
            if mac_clean.startswith(prefix):
                indicators.append(f"MAC address ({mac}) matches Raspberry Pi Foundation OUI")
                break
    
    # Try to check for common Raspberry Pi services
    try:
        # Check for SSH (common on RPi)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex((ip, 22))
        if result == 0:
            indicators.append("SSH service detected")
        sock.close()
    except:
        pass
    
    return indicators

def scan_network(network_range="192.168.1.0/24"):
    """Scan network for active devices"""
    network = ipaddress.IPv4Network(network_range, strict=False)
    
    print(f"Scanning network: {network_range}")
    print("This may take a few moments...")
    print("-" * 60)
    
    # Use threading for faster scanning
    with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
        # Submit ping tasks
        future_to_ip = {executor.submit(ping_host, ip): ip for ip in network.hosts()}
        
        active_ips = []
        for future in concurrent.futures.as_completed(future_to_ip):
            result = future.result()
            if result:
                active_ips.append(result)
    
    print(f"Found {len(active_ips)} active devices:")
    print("-" * 60)
    
    rpi_candidates = []
    
    for ip in sorted(active_ips, key=lambda x: ipaddress.IPv4Address(x)):
        hostname, mac = get_hostname_and_mac(ip)
        indicators = identify_raspberry_pi(ip, hostname, mac)
        
        print(f"IP: {ip}")
        print(f"  Hostname: {hostname}")
        print(f"  MAC: {mac}")
        
        if indicators:
            print(f"  🍓 POSSIBLE RASPBERRY PI:")
            for indicator in indicators:
                print(f"    - {indicator}")
            rpi_candidates.append((ip, hostname, mac, indicators))
        
        print()
    
    if rpi_candidates:
        print("=" * 60)
        print("RASPBERRY PI CANDIDATES:")
        print("=" * 60)
        for ip, hostname, mac, indicators in rpi_candidates:
            print(f"🍓 {ip} ({hostname})")
            for indicator in indicators:
                print(f"   - {indicator}")
            print()
    else:
        print("No obvious Raspberry Pi devices found.")
        print("Note: Some devices may not respond to ping or may have security settings")
        print("that prevent detection.")

if __name__ == "__main__":
    # You can modify this network range based on your router's configuration
    # Common ranges: 192.168.1.0/24, 192.168.0.0/24, 10.0.0.0/24
    
    if len(sys.argv) > 1:
        network_range = sys.argv[1]
    else:
        network_range = "192.168.1.0/24"
    
    scan_network(network_range)
