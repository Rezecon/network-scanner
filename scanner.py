"""
network-scanner
---------------
Varre um range de IPs em busca de hosts ativos e escaneia
as portas mais comuns em cada host encontrado.

Uso:
    python scanner.py
"""

import socket
import subprocess
import ipaddress
import datetime
import platform
import colorama
from concurrent.futures import ThreadPoolExecutor, as_completed
from colorama import init, Fore, Style

init(autoreset=True)  # inicializa colorama no Windows

# Portas mais comuns e seus serviços
COMMON_PORTS = {
    21:   "FTP",
    22:   "SSH",
    23:   "Telnet",
    25:   "SMTP",
    53:   "DNS",
    80:   "HTTP",
    110:  "POP3",
    139:  "NetBIOS",
    143:  "IMAP",
    443:  "HTTPS",
    445:  "SMB",
    3306: "MySQL",
    3389: "RDP",
    5900: "VNC",
    8080: "HTTP-Alt",
    8443: "HTTPS-Alt",
}

# Ping
def is_host_alive(ip: str) -> bool:
    """Retorna True se o host responder ao ping."""
    sistema = platform.system().lower()

    if sistema == "windows":
        cmd = ["ping", "-n", "1", "-w", "500", str(ip)]
    else:
        cmd = ["ping", "-c", "1", "-W", "1", str(ip)]

    resultado = subprocess.run(
        cmd,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    return resultado.returncode == 0

# Scan de porta
def scan_port(ip: str, port: int, timeout: float = 0.5) -> bool:
    """Retorna True se a porta estiver aberta."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(timeout)
            resultado = s.connect_ex((str(ip), port))
            return resultado == 0
    except Exception:
        return False

# Resolução de hostname
def get_hostname(ip: str) -> str:
    """Tenta resolver o hostname do IP. Retorna '-' se não conseguir."""
    try:
        return socket.gethostbyaddr(str(ip))[0]
    except Exception:
        return "-"

# Scan completo de um host
def scan_host(ip: str) -> dict | None:
    """
    Verifica se o host está ativo e escaneia as portas comuns.
    Retorna um dicionário com os resultados ou None se offline.
    """
    if not is_host_alive(ip):
        return None

    hostname = get_hostname(ip)
    open_ports = []

    # Escaneia todas as portas comuns em paralelo
    with ThreadPoolExecutor(max_workers=20) as executor:
        futures = {
            executor.submit(scan_port, ip, port): port
            for port in COMMON_PORTS
        }
        for future in as_completed(futures):
            port = futures[future]
            if future.result():
                open_ports.append(port)

    return {
        "ip":         ip,
        "hostname":   hostname,
        "open_ports": sorted(open_ports),
    }

# Exibição no terminal
def print_header(network: str):
    print()
    print(Fore.CYAN + "=" * 55)
    print(Fore.CYAN + f"  Network Scanner — {network}")
    print(Fore.CYAN + f"  {datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print(Fore.CYAN + "=" * 55)
    print()

def print_host_result(result: dict):
    ip       = result["ip"]
    hostname = result["hostname"]
    ports    = result["open_ports"]

    print(Fore.GREEN + f"  [+] Host ativo: {ip}  ({hostname})")

    if ports:
        for port in ports:
            service = COMMON_PORTS.get(port, "?")
            print(Fore.YELLOW + f"       ├─ {port:<6} {service}")
    else:
        print(Fore.WHITE + "       └─ Nenhuma porta comum aberta")
    print()

def print_summary(total_hosts: int, active_hosts: int, elapsed: float):
    print(Fore.CYAN + "=" * 55)
    print(f"  Hosts escaneados : {total_hosts}")
    print(Fore.GREEN + f"  Hosts ativos     : {active_hosts}")
    print(f"  Tempo total      : {elapsed:.1f}s")
    print(Fore.CYAN + "=" * 55)
    print()

# Salvar relatório
def save_report(network: str, results: list[dict], elapsed: float):
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename  = f"scan_{timestamp}.txt"

    with open(filename, "w", encoding="utf-8") as f:
        f.write(f"Network Scanner — Relatório\n")
        f.write(f"Rede     : {network}\n")
        f.write(f"Data     : {datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
        f.write(f"Duração  : {elapsed:.1f}s\n")
        f.write("=" * 55 + "\n\n")

        for r in results:
            f.write(f"Host: {r['ip']}  ({r['hostname']})\n")
            if r["open_ports"]:
                for port in r["open_ports"]:
                    service = COMMON_PORTS.get(port, "?")
                    f.write(f"  Porta {port:<6} {service}\n")
            else:
                f.write("  Nenhuma porta comum aberta\n")
            f.write("\n")

        f.write(f"Total de hosts ativos: {len(results)}\n")

    print(Fore.CYAN + f"  Relatório salvo em: {filename}\n")

# Entrada do usuário
def get_network_input() -> str:
    """
    Pede ao usuário o range de rede no formato CIDR.
    Exemplos válidos: 192.168.1.0/24  |  192.168.0.0/24
    """
    print(Fore.CYAN + "\n  Network Scanner\n")
    print("  Digite o range de rede no formato CIDR.")
    print("  Exemplos:")
    print("    192.168.1.0/24   → varre de .1 até .254")
    print("    192.168.1.0/28   → varre apenas 14 hosts\n")

    while True:
        entrada = input("  Rede: ").strip()
        try:
            ipaddress.ip_network(entrada, strict=False)
            return entrada
        except ValueError:
            print(Fore.RED + "  Formato inválido. Use o formato CIDR (ex: 192.168.1.0/24)\n")

# Main 
def main():
    network_str = get_network_input()
    network     = ipaddress.ip_network(network_str, strict=False)
    hosts       = list(network.hosts())  # exclui endereço de rede e broadcast

    print_header(network_str)
    print(f"  Escaneando {len(hosts)} hosts...\n")

    inicio   = datetime.datetime.now()
    results  = []

    # Escaneia os hosts em paralelo (até 50 ao mesmo tempo)
    with ThreadPoolExecutor(max_workers=50) as executor:
        futures = {
            executor.submit(scan_host, str(ip)): ip
            for ip in hosts
        }
        for future in as_completed(futures):
            result = future.result()
            if result:
                results.append(result)
                print_host_result(result)

    fim     = datetime.datetime.now()
    elapsed = (fim - inicio).total_seconds()

    # Ordena por IP antes de exibir o resumo
    results.sort(key=lambda r: ipaddress.ip_address(r["ip"]))

    print_summary(len(hosts), len(results), elapsed)

    if results:
        salvar = input("  Salvar relatório em .txt? (s/n): ").strip().lower()
        if salvar == "s":
            save_report(network_str, results, elapsed)

if __name__ == "__main__":
    main()