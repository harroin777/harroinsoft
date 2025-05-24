import ascii_magic
from termcolor import colored
import requests, socket, os

def show_banner():
    output = ascii_magic.from_image_file("fsociety.png", columns=80, char="#")
    ascii_magic.to_terminal(output)
    print(colored("\n== IP Информационный Сканер ==", "red", attrs=["bold"]))

def get_ip_info(ip):
    info = {}
    try:
        res = requests.get(f"http://ip-api.com/json/{ip}").json()
        info.update(res)
    except Exception as e:
        info['error'] = str(e)

    try:
        info['reverse_dns'] = socket.gethostbyaddr(ip)[0]
    except:
        info['reverse_dns'] = "N/A"

    return info

if __name__ == "__main__":
    show_banner()
    ip = input(colored("\nВведите IP: ", "yellow"))
    data = get_ip_info(ip)

    print("\n" + colored("Результаты:", "cyan", attrs=["bold"]))
    for key, value in data.items():
        print(colored(f"{key}:", "green"), value)
