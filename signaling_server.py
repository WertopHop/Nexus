import socket
import threading
import json

class SignalingServer:
    def __init__(self, port=8000):
        self.port = port
        self.peers = {}
        
    def handle_peer(self, conn, addr):
        peer_id = None
        try:
            while True:
                data = conn.recv(1024).decode()
                if not data:
                    break
                    
                msg = json.loads(data)
                
                if msg['type'] == 'register':
                    peer_id = msg['peer_id']
                    self.peers[peer_id] = {
                        'socket': conn,
                        'addr': addr,
                        'public_addr': msg.get('public_addr')
                    }
                    print(f"Зарегистрирован: {peer_id}")
                    conn.send(json.dumps({'status': 'registered'}).encode())
                
                elif msg['type'] == 'request_peer':
                    target_id = msg['target_id']
                    if target_id in self.peers:
                        peer_info = self.peers[target_id]
                        response = {
                            'type': 'peer_info',
                            'peer_id': target_id,
                            'addr': peer_info['public_addr']
                        }
                        conn.send(json.dumps(response).encode())
                        
                        notify = {
                            'type': 'incoming_request',
                            'from_peer': peer_id,
                            'addr': msg. get('my_addr')
                        }
                        peer_info['socket'].send(json.dumps(notify).encode())
                    else:
                        conn.send(json.dumps({'error': 'peer_not_found'}).encode())
                
        except Exception as e:
            print(f"Ошибка: {e}")
        finally:
            if peer_id and peer_id in self.peers:
                del self.peers[peer_id]
            conn.close()
    
    def start(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind(('0.0.0.0', self.port))
        server.listen(10)
        
        print(f"Сигнальный сервер запущен на {self.port}")
        
        while True:
            conn, addr = server.accept()
            threading.Thread(target=self.handle_peer, args=(conn, addr), daemon=True).start()

if __name__ == "__main__":
    SignalingServer().start()