import socket
import threading
import sys

HOST = "127.0.0.1"
PORT = 5000

def recv_loop(sock, running_flag): #thread que recebe mensagens do servidor e printa na tela
    try:
        while running_flag["running"]:
            try:
                data = sock.recv(4096)
            except OSError: #socket fechado externamente
                break
            if not data:
                print("\n conexão encerrada pelo servidor")
                running_flag["running"] = False
                break
            # tenta decodificar e imprimir
            try:
                text = data.decode("utf-8")
            except UnicodeDecodeError:
                text = repr(data)
            # printa o que o servidor enviou
            print(text.rstrip("\n"))
    except Exception as e:
        print(f"\n[recv] erro: {e}")
        running_flag["running"] = False


def main(): 
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # cria um socket tcp ipv4
    try:
        sock.connect((HOST, PORT)) #tenta conectar ao servidor
    except Exception as e:
        print(f"Erro ao conectar em {HOST}:{PORT}; {e}")
        return
    

    print(f"conectado a {HOST}:{PORT}. digite /nick <nome> para escolher seu nome, /sair para encerrar")

    running = {"running": True}

    # nick local (mostrado antes das mensagens que o usuário envia)
    nick = f"{sock.getsockname()[0]}:{sock.getsockname()[1]}" #usa seu ip:porta ate escolher um nick
    # inicia thread de recebimento
    t = threading.Thread(target=recv_loop, args=(sock, running), daemon=True) #cria e inicia a thread que ficara recebendo mensagens do servidor 
    t.start()
    try:
        while running["running"]:
            try:
                line = input()
            except EOFError:# ctrl d ou input fechado
                line = "/sair"
            except KeyboardInterrupt: #ctrl c
                line = "/sair"
            if not running["running"]: #checa se running foi desligado
                break 
            if line.startswith("/nick "): #comando /nick
                newnick = line[6:].strip()
                if newnick == "":
                    print("[system] nick inválido. Use: /nick SeuNome")
                    continue
                # atualiza nick local e avisa o servidor
                nick = newnick
                try:
                    sock.sendall(f"/nick {nick}\n".encode("utf-8"))
                except Exception as e:
                    print(f" erro enviando /nick: {e}")
                    running["running"] = False
                    break
                print(f" seu nick agora é: {nick}")
                continue
            if line.strip() == "/sair": # comando /sair
                try:
                    sock.sendall("/sair\n".encode("utf-8"))
                except:
                    pass
                running["running"] = False
                break
            # mensagem comum: mostra localmente com o nick e envia para o servidor
            to_send = line.strip()
            if to_send == "":
                continue
            # mostra no terminal
            print(f"[{nick}] {to_send}")
            try:
                sock.sendall((to_send + "\n").encode("utf-8")) #envia a mensagem ao servidor
            except Exception as e: #se tiver erro finaliza o cliente
                print(f"[system] erro enviando mensagem: {e}")
                running["running"] = False
                break
    finally:
        try:
            sock.close() #fecha o socket
        except:
            pass
        running["running"] = False #garante que running fique False pra recepção de thread parar
        print("desconectado")
if __name__ == "__main__":
    main()

