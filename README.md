# Network Scanner

Scanner de rede em Python que descobre hosts ativos em uma sub-rede e identifica portas abertas em cada um deles. Desenvolvido como projeto prático unindo conhecimentos de redes (TCP/IP, portas, protocolos) com programação Python.

---

## Funcionalidades

- Varredura de hosts via ping em qualquer range CIDR (ex: `192.168.1.0/24`)
- Detecção de 16 portas comuns com identificação do serviço (HTTP, SSH, FTP, RDP...)
- Resolução de hostname dos hosts encontrados
- Execução paralela para varredura rápida (ThreadPoolExecutor)
- Relatório exportado em `.txt` com data e hora
- Output colorido no terminal

---

## Pré-requisitos

- Python 3.10+
- Biblioteca `colorama`

```bash
pip install colorama
```

---

## Como usar

```bash
python scanner.py
```

O programa vai pedir o range de rede no formato CIDR:

```
  Rede: 192.168.1.0/24
```

### Exemplos de ranges

| Range              | Hosts escaneados |
|--------------------|-----------------|
| `192.168.1.0/24`   | 254             |
| `192.168.1.0/28`   | 14              |
| `10.0.0.0/30`      | 2               |

---

## Exemplo de output

```
=======================================================
  Network Scanner — 192.168.1.0/24
  23/04/2025 14:32:01
=======================================================

  [+] Host ativo: 192.168.1.1  (router.local)
       ├─ 80     HTTP
       ├─ 443    HTTPS

  [+] Host ativo: 192.168.1.10  (desktop-pc)
       ├─ 139    NetBIOS
       ├─ 445    SMB
       ├─ 3389   RDP

=======================================================
  Hosts escaneados : 254
  Hosts ativos     : 2
  Tempo total      : 12.4s
=======================================================
```

---

## Portas escaneadas

| Porta | Serviço  | Porta | Serviço  |
|-------|----------|-------|----------|
| 21    | FTP      | 443   | HTTPS    |
| 22    | SSH      | 445   | SMB      |
| 23    | Telnet   | 3306  | MySQL    |
| 25    | SMTP     | 3389  | RDP      |
| 53    | DNS      | 5900  | VNC      |
| 80    | HTTP     | 8080  | HTTP-Alt |
| 110   | POP3     | 8443  | HTTPS-Alt|
| 139   | NetBIOS  | 143   | IMAP     |

---

## Conceitos aplicados

- **Sockets TCP** — conexão nas portas para verificar se estão abertas (`socket.connect_ex`)
- **ICMP / ping** — detecção de hosts ativos via subprocess
- **Threading** — varredura paralela com `ThreadPoolExecutor` para reduzir o tempo total
- **CIDR / sub-redes** — parsing e iteração de ranges IP com `ipaddress`
- **Resolução de DNS reverso** — `socket.gethostbyaddr` para obter o hostname

---

## Aviso

Use apenas em redes que você tem permissão para escanear (sua rede local, laboratório, ambiente de estudo). Escanear redes de terceiros sem autorização é ilegal.

---

## Autor

**[Gabriel R. Pires]** — Estudante de Engenharia de Computação, IFSP Piracicaba  
GitHub: [@Rezecon](https://github.com/Rezecon)
