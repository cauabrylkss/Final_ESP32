import socket #comunicação UDP
import threading #thread paralela para receber mensagens
import sys #le do teclado (stdin)
import time # mede tempo do /bench

SERVER_HOST = '127.0.0.1'
SERVER_PORT = 5001

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) #Cria um socket UDP, AF_INET → IPv4, SOCK_DGRAM → protocolo UDP
s.bind(('', 0))  # Associa o socket a uma porta local, '':aceita mensagens em qualquer interface da máquina, 0:o s.o escolhe uma porta automática
# ↑ Assim, cada cliente tem uma porta aleatória !=. Permitindo rodar vários clientes simultaneamente na mesma máquina.

# Thread para receber mensagens do servidor
def receive_loop():
    while True:
        try:
            data, addr = s.recvfrom(65536) #Recebe mensagens (pacote UDP) do servidor (máx 65536 bytes),retorna o conteúdo(data) e o endereço(addr) do remetente
            print(data.decode('utf-8'), end='') #print da mensagem recebida
        except Exception as e: #Se der erro, sai do loop, a thred termina
            print("Erro recv:", e) 
            break 

#Inicia a thread de recebimento
t = threading.Thread(target=receive_loop, daemon=True) #Cria a thread, daemon=True(encerra junto com o programa principal)
t.start() #Inicia a thread

#Funcao para enviar uma linha ao servidor
def send_line(line):
    s.sendto(line.encode(), (SERVER_HOST, SERVER_PORT))

#Loop pra ler os comandos do usuario
try:
    while True:
        line = sys.stdin.readline() #lê uma linha digitada pelo usuário
        if not line:
            break
        line = line.rstrip('\n')
        if line.startswith('/bench '): 
            try:
                n = int(line.split(' ',1)[1]) #tamanho total, em bytes, que o cliente vai enviar ao servidor
            except:
                print("Uso: /bench <bytes>")
                continue
            send_line(line) #informa o servidor que vai fazer bench, envia n bytes
            chunk = b'x' * 65536 #Cria um bloco de 64 KB (chunk) cheio de 'x'
            tosend = n
            start = time.time()
            while tosend > 0: #envia pedaços de até 64 KB até completar n bytes
                sendnow = min(len(chunk), tosend)
                s.sendto(chunk[:sendnow], (SERVER_HOST, SERVER_PORT))
                tosend -= sendnow
            elapsed = time.time() - start #tempo gasto para enviar tudo, depois volta ao inicio do loop
            print(f"Enviados {n} bytes em {elapsed:.4f}s (client-side)")
            continue
        send_line(line) #Se a linha não for /bench, ela é enviada como mensagem normal.
        if line.strip() == '/sair': #finaliza se digitar sair 
            break
except KeyboardInterrupt: #trata Ctrl+C (interrupção do usuário)
    pass
finally: #Fecha o socket, finaliza o cliente UDP corretamente
    s.close()