# DNS Spoofing Attack

**Autor:** Edwin (Matrícula: 2024-2415)  
**Institución:** Instituto Tecnológico de las Américas (ITLA)  
**Programa:** Seguridad Informática  
**Materia:** Seguridad de Redes  
**Fecha:** 12 de Junio de 2026  

---

## Descripción General

Este repositorio contiene scripts, documentación y demostración de DNS Spoofing / DNS Poisoning. Se demuestra cómo un atacante puede redirigir tráfico DNS hacia servidores falsos sin que la víctima lo detecte.

**Ataque demostrado:**
- Interceptar queries DNS hacia itla.edu.do
- Responder con IP falsa (172.24.15.129)
- Servir página web maliciosa

---

## Objetivo del Laboratorio

Demostrar las vulnerabilidades del protocolo DNS:

1. DNS no valida el origen de las respuestas
2. El cliente acepta la primera respuesta que llega
3. No existe autenticación por defecto
4. Un atacante en la red puede redirigir tráfico
5. Impacto: phishing, malware, robo de credenciales

---

## Video Demostrativo

**Video:** DNS Spoofing Attack - Demostración práctica

[Ver en YouTube](https://youtu.be/wV6ox_iZ_sI)    
Contenido: Topología, explicación, ejecución del ataque, página falsa, mitigaciones

---

## Requisitos

### Software
- Linux (Parrot OS, Kali, Ubuntu, etc.)
- Python 3.x
- Scapy (librería Python para manipulación de paquetes)
- HTTP Server (incluido en Python)

### Hardware
- Atacante: máquina con Parrot OS
- Víctima: Windows 10 o Linux en la misma red
- Acceso a la red (no requiere acceso físico a switches)

### Instalación de dependencias

**Instalar Scapy:**

```bash
pip install scapy
```

O:

```bash
sudo apt install python3-scapy -y
```

---


## Uso Rápido

### Paso 1: Ejecutar script en Atacante (Parrot)

```bash
python3 dns_spoofing.py
```

Seleccionar:
- Opción: **[2] DNS SPOOFING + WEB SERVER**
- Dominio: **itla.edu.do** (o dejar default)
- IP falsa: **172.24.15.129** (o tu IP de atacante)
- Interfaz: **ens33** (o tu interfaz)
- Puerto web: **80**

### Paso 2: Configurar Víctima (Windows 10)

```cmd
ipconfig /flushdns
```

Abrir navegador:

```
http://itla.edu.do
```

### Resultado

La víctima ve página falsa servida por Parrot con:
- Título: FAKE PAGE - DNS SPOOFING DEMO
- Student: Edwin
- ID: 2024-2415
- Subject: Seguridad de Redes

---


## Fundamentos Técnicos

### Protocolo DNS

DNS es un protocolo de resolución de nombres que traduce nombres de dominio (itla.edu.do) a direcciones IP (172.67.69.129).

**Características:**
- Puerto: UDP 53
- Protocolo: Stateless (sin estado)
- Query: Cliente pregunta por dominio
- Response: Servidor responde con IP
- Sin autenticación por defecto
- Sin validación de origen

### Mecanismo de Vulnerabilidad

DNS confía en la primera respuesta que recibe, sin validar la fuente:

```
Víctima: "¿Cuál es la IP de itla.edu.do?"
  ↓
DNS Legítimo responde lentamente: "172.67.69.129"
Atacante responde rápido: "172.24.15.129" ← ACEPTA ESTA
  ↓
Víctima conecta a 172.24.15.129 (servidor malicioso)
```

### Flujo del Ataque

1. Atacante inicia script DNS Spoofing
2. Víctima intenta resolver itla.edu.do
3. Query DNS llega a Atacante
4. Atacante responde rápidamente con IP falsa
5. Víctima acepta respuesta y se conecta a servidor falso
6. Servidor web falso sirve página maliciosa

---

## Contra-Medidas

### Nivel 1: DNSSEC (Recomendado)

```bash
# Habilitar DNSSEC en resolver
echo "dnssec=yes" >> /etc/systemd/resolved.conf
```

Valida respuestas DNS con firmas criptográficas.

**Efectividad:** Muy Alta  
**Complejidad:** Alta (requiere infraestructura)

### Nivel 2: DNS over HTTPS (DoH)

Usa navegadores modernos con DoH habilitado:
- Firefox: Configuración → Privacidad → DNS over HTTPS
- Chrome: Configuración → Privacidad → Usar DNS seguro

**Efectividad:** Alta  
**Complejidad:** Baja (cliente)

### Nivel 3: DNS over TLS (DoT)

```bash
# Usar resolvedor que soporte DoT
# Ejemplo: Cloudflare (1.1.1.1)
echo "nameserver 1.1.1.1" > /etc/resolv.conf
```

**Efectividad:** Alta  
**Complejidad:** Media

### Nivel 4: ARP Protection

Previene que el atacante intercepte todo el tráfico:

```bash
# En Linux, habilitar GARP
echo "1" > /proc/sys/net/ipv4/gratuitous_arp
```

**Efectividad:** Media (complementario)  
**Complejidad:** Media

### Nivel 5: Network Monitoring

Detectar cambios anómalos de DNS:
- Monitorear resoluciones de DNS
- Alertas de dominios sospechosos
- Logs de tráfico DNS

**Efectividad:** Media  
**Complejidad:** Alta

### Mejor Práctica

**Configuración defensiva recomendada:**

1. Implementar DNSSEC en zona DNS
2. Habilitar DoH/DoT en clientes
3. Usar DNS confiable (Google 8.8.8.8, Cloudflare 1.1.1.1)
4. Monitorear tráfico DNS
5. Educación de usuarios sobre phishing

---

## Topología del Laboratorio

```
┌──────────────────┐
│   Windows 10     │
│   172.24.15.50   │ Víctima
│   DNS: Parrot    │
└────────┬─────────┘
         │
    ┌────▼────┐
    │ Topology│ (vnet8)
    └────┬────┘
         │
┌────────▼──────────┐
│  Parrot OS        │
│  172.24.15.129    │ Atacante
│  Escucha DNS 53   │
│  Servidor web 80  │
└───────────────────┘
```

---

## Impacto

### Antes del Ataque
- Víctima accede a itla.edu.do
- Resuelve a IP real (172.67.69.129)
- Accede a sitio legítimo

### Después del Ataque
- Víctima intenta acceder a itla.edu.do
- Resuelve a IP falsa (172.24.15.129)
- Accede a servidor malicioso
- Ve página falsa

### Consecuencias Potenciales
- Phishing (robo de credenciales)
- Malware (descarga de archivos maliciosos)
- Man-in-the-middle (captura de datos)
- Suplantación de identidad
- Daño a reputación

---

## Diferencias entre VTP, DTP y DNS

| Característica | VTP | DTP | DNS |
|---|---|---|---|
| Capa OSI | Capa 2 | Capa 2 | Capa 3/7 |
| Objetivo | Manipular VLAN DB | Convertir puerto a trunk | Redirigir tráfico DNS |
| Requiere | Acceso a puerto switch | Acceso a puerto switch | Estar en la red |
| Herramienta | Scapy/Python | Yersinia | Python/Scapy |
| Mitigación | VTP pruning | Deshabilitar DTP | DNSSEC/DoH |
| Impacto | Ver todas las VLANs | Acceso a VLANs | Phishing/malware |

---

## Limitaciones Conocidas

- DNSSEC habilitado: Ataque no funciona (valida firmas)
- DoH/DoT habilitado: Encriptación previene interception
- Firewall blocking port 53: Queries no llegan
- DNS cache agresivo: Respuestas cacheadas localmente
- El atacante debe estar en la misma red

---

## Referencias

- RFC 1035 - Domain Names Implementation and Specification
- RFC 4033 - DNSSEC Introduction and Requirements
- RFC 8484 - DNS Queries over HTTPS (DoH)
- RFC 7858 - Specification for DNS over Transport Layer Security (TLS)
- Scapy Documentation: https://scapy.readthedocs.io
- OWASP - DNS Spoofing

---

## Notas Importantes

Este código es **para fines educativos exclusivamente**. Solo para uso en laboratorios autorizados de ITLA.

**Prohibido usar en redes de producción o sin autorización explícita.**

---

## Autor

Edwin  
Matrícula: 2024-2415  
Programa: Seguridad Informática  
Materia: Seguridad de Redes  
Instituto Tecnológico de las Américas (ITLA)  
Santo Domingo, República Dominicana

---

**Última actualización:** 12 de Junio de 2026  
**Versión:** 1.0  
**GitHub:** https://github.com/edwindepaula10/9_dns_spoofing_attack
