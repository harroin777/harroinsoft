from PIL import Image
from termcolor import colored
import requests, socket

def image_to_ascii(file_path, width=80):
    # Открываем изображение и уменьшаем до нужной ширины
    img = Image.open(file_path)
    aspect_ratio = img.height / img.width
    height = int(aspect_ratio * width * 0.55)  # 0.55 для пропорций символов
    img = img.resize((width, height))
    img = img.convert("L")  # Конвертируем в оттенки серого

    pixels = img.getdata()
    chars = ["@", "#", "S", "%", "?", "*", "+", ";", ":", ",", "."]  # от темного к светлому
    new_pixels = [chars[pixel//25] for pixel in pixels]
    new_pixels = ''.join(new_pixels)

    ascii_image = [new_pixels[index: index + width] for index in range(0, len(new_pixels), width)]
    return "\n".join(ascii_image)

def show_banner():
    ascii_img = image_to_ascii("fsociety.png", width=80)
    print(colored(ascii_img, "magenta"))
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
