import socket
import json
import time

HOST = '0.0.0.0'
PORT = 5001

clients = {}

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) #Cria socket, UDP sempre usa SOCK_DGRAM.
s.bind((HOST, PORT))  #Faz o Bind, associa o socket ao host e porta 5001,(recebe pacotes em qualquer interface de rede)
print(f"[START] servidor UDP on {HOST}:{PORT}")

#Loop infinito recebendo mensagens
while True:
    #data = conteúdo da mensagem
    #addr = endereço do cliente — identificação do cliente
    data, addr = s.recvfrom(65536) #addr é o par (IP, porta) do cliente, ele serve como ID do cliente no UDP.
    text = data.decode('utf-8', errors='ignore').strip()
    # Registrar cliente novo se não estiver na lista
    # Como o UDP não cria conexão, você detecta um “cliente” quando recebe qualquer pacote.
    if addr not in clients:
        clients[addr] = f"{addr[0]}:{addr[1]}"
        print(f"[NOVO CLIENTE UDP] {addr}")

    # Identificar comandos
    if text.startswith('/nick '):
        newnick = text.split(' ',1)[1].strip()
        clients[addr] = newnick or clients[addr]
        reply = f"Seu nick agora é: {clients[addr]}"
        s.sendto(reply.encode(), addr)
        print(f"[NICK] {addr} -> {clients[addr]}")
        continue
    if text.startswith('/sair'): # comando de desconexão, remove da lista, como o UDP não tem conexão, é só esquecer o cliente.
        print(f"[ DESCONECTAR UDP] {addr} nick={clients.get(addr)}")
        clients.pop(addr, None)
        continue
    if text.startswith('/bench '): #o servidor mede quantos bytes recebeu do cliente dentro de 2 segundos
        try:
            n = int(text.split(' ',1)[1])
        except:
            s.sendto(b"Uso: /bench <bytes>", addr)
            continue
        # recebe n bytes (UDP: pode estar fragmentado/perdido) -> aqui confiamos em um único datagrama grande ou múltiplos envios
        # Para o teste de UDP, medimos os bytes recebidos até atingir o total ou o tempo limite
        s.settimeout(2.0)
        received = 0
        start = time.time()
        while received < n:
            try:
                chunk, a2 = s.recvfrom(65536)
                if a2 != addr:
                    # ignora outros clientes' bench
                    continue
                received += len(chunk) #O servidor soma o tamanho de cada um
            except socket.timeout: #Para quando recebe tudo ou quando dá timeout
                break
        elapsed = time.time() - start
        s.settimeout(None)
        s.sendto(f"/bench done: recebeu {received} bytes em {elapsed:.4f}s".encode(), addr) #envia o resultado
        print(f"[UDP BENCH] {clients.get(addr)} recebeu {received} bytes em {elapsed:.4f}s")
        continue

    # Mensagem comum: retransmite mensagem para todos os clientes UDP conhecidos
    nick = clients.get(addr, f"{addr[0]}:{addr[1]}")
    outgoing = f"{nick}: {text}"
    print(f"[MSG UDP] {outgoing}")
    for c in list(clients):
        if c != addr:
            try:
                s.sendto(outgoing.encode(), c)
            except Exception:
                clients.pop(c, None)