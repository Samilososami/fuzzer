import argparse
import requests
from queue import Queue
import threading
import time
from urllib.parse import urljoin
from colorama import Fore, Style

def fuzz_url(url, diccionario_queue):
    while not diccionario_queue.empty():
        palabra = diccionario_queue.get()
        try:
         
            full_url = urljoin(url, palabra.strip())
            response = requests.get(full_url)
            if response.status_code == 200:
                print(Fore.GREEN + Style.BRIGHT + f"[{response.status_code}] --> {full_url}" + Style.RESET_ALL)
            elif response.status_code == 404:
                print(Fore.RED + f"[{response.status_code}] --> {full_url}" + Style.RESET_ALL)
            else:
                print(Fore.YELLOW + f"[{response.status_code}] --> {full_url}" + Style.RESET_ALL)
        except requests.RequestException as e:
            print(f"Error con {full_url}: {e}")
        diccionario_queue.task_done()

# Función principal
def main():
    parser = argparse.ArgumentParser(description="Script de fuzzing web con diccionario")
    parser.add_argument('-w', '--web', type=str, required=True, help="URL")
    parser.add_argument('-d', '--diccionario', type=str, required=True, help="Diccionario")
    parser.add_argument('-t', '--threads', type=int, default=10, help="Número de hilos")

    args = parser.parse_args()

    # Asegurarnos de que la URL base termina con una barra
    if not args.web.endswith('/'):
        args.web += '/'

    print(Fore.CYAN + "[+] Cargando el diccionario...\n" + Style.RESET_ALL)

    diccionario_queue = Queue()
    with open(args.diccionario, 'r') as diccionario_file:
        for linea in diccionario_file:
            diccionario_queue.put(linea.strip())

    for _ in range(args.threads):
        worker = threading.Thread(target=fuzz_url, args=(args.web, diccionario_queue))
        worker.start()

    time.sleep(0.5)
    diccionario_queue.join()
    print(Fore.GREEN + f"\n[+] Fuzzing completado.\n" + Style.RESET_ALL)
