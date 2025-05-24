import requests
import socket
import json
import os

def get_ip_info(ip, abuse_api_key=None):
    info = {}

    # IP Geolocation (ip-api.com)
    try:
        res = requests.get(f"http://ip-api.com/json/{ip}").json()
        info['ip-api'] = res
    except Exception as e:
        info['ip-api'] = str(e)

    # IPInfo.io
    try:
        res = requests.get(f"https://ipinfo.io/{ip}/json").json()
        info['ipinfo'] = res
    except Exception as e:
        info['ipinfo'] = str(e)

    # AbuseIPDB check
    if abuse_api_key:
        try:
            headers = {
                'Key': abuse_api_key,
                'Accept': 'application/json'
            }
            res = requests.get(f"https://api.abuseipdb.com/api/v2/check?ipAddress={ip}", headers=headers).json()
            info['abuseipdb'] = res
        except Exception as e:
            info['abuseipdb'] = str(e)
    else:
        info['abuseipdb'] = "API-ключ не предоставлен"

    # Reverse DNS
    try:
        hostname = socket.gethostbyaddr(ip)[0]
        info['reverse_dns'] = hostname
    except Exception as e:
        info['reverse_dns'] = str(e)

    # Ping (Unix)
    try:
        response = os.popen(f"ping -c 3 {ip}").read()
        info['ping'] = response
    except Exception as e:
        info['ping'] = str(e)

    return info

if __name__ == "__main__":
    print("== Сбор информации по IP-адресу ==")
    target_ip = input("Введите IP-адрес: ").strip()
    abuse_api_key = input("Введите API-ключ для AbuseIPDB (или нажмите Enter для пропуска): ").strip()

    result = get_ip_info(target_ip, abuse_api_key if abuse_api_key else None)

    print("\n=== Результаты ===")
    print(json.dumps(result, indent=4, ensure_ascii=False))
