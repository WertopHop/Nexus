import asyncio
import socketio
import json
import sys
from aiortc import RTCPeerConnection, RTCSessionDescription, RTCIceCandidate, RTCDataChannel
import logging

logging.basicConfig(level=logging.WARNING)

class P2PMessenger:
    def __init__(self, peer_id, signaling_server):
        self.peer_id = peer_id
        self.signaling_server = signaling_server
        
        self.sio = socketio.AsyncClient()
        
        self.peer_connections = {}
        self.data_channels = {}
        self.pending_candidates = {}

        self.sio.on('registered', self.on_registered)
        self.sio.on('peers_list', self.on_peers_list)
        self.sio.on('signal', self.on_signal)
        self.sio.on('error', self.on_error)


    async def on_registered(self, data):
        print(f"✅ Зарегистрированы как: {data['peer_id']}")
        print("\nКоманды:")
        print("  list - показать онлайн пиров")
        print("  call <peer_id> - позвонить пиру")
        print("  exit - выход")
        print("  любой текст - отправить сообщение всем\n")
    

    async def on_peers_list(self, data):
        peers = data['peers']
        if peers:
            print("\n📋 Онлайн пиры:")
            for peer in peers:
                status = "🟢 подключен" if peer in self. data_channels else "⚪ не подключен"
                print(f"  - {peer} ({status})")
        else:
            print("\n📋 Нет других пиров онлайн")
    

    async def on_error(self, data):
        print(f"\n❌ Ошибка: {data['message']}")


    async def on_signal(self, data):
        from_peer = data['from']
        signal_type = data['type']
        signal_data = data['data']
        
        print(f"\n📡 Получен сигнал {signal_type} от {from_peer}")
        
        if signal_type == 'offer':
            await self.handle_offer(from_peer, signal_data)
        elif signal_type == 'answer':
            await self.handle_answer(from_peer, signal_data)
        elif signal_type == 'ice-candidate':
            await self.handle_ice_candidate(from_peer, signal_data)


    async def create_peer_connection(self, peer_id):
        pc = RTCPeerConnection()
        
        self.peer_connections[peer_id] = pc
        self.pending_candidates[peer_id] = []
        
        @pc.on("datachannel")
        def on_datachannel(channel):
            asyncio.create_task(self.setup_data_channel(peer_id, channel))
        
        @pc.on("icecandidate")
        async def on_icecandidate(candidate):
            if candidate:
                await self.send_signal(peer_id, 'ice-candidate', {
                    'candidate': candidate. candidate,
                    'sdpMid': candidate.sdpMid,
                    'sdpMLineIndex': candidate.sdpMLineIndex
                })
        
        @pc.on("connectionstatechange")
        async def on_connectionstatechange():
            print(f"\n🔗 Соединение с {peer_id}: {pc.connectionState}")
            
            if pc.connectionState == "failed":
                await pc.close()
                if peer_id in self.peer_connections:
                    del self.peer_connections[peer_id]
                if peer_id in self.data_channels:
                    del self.data_channels[peer_id]
        
        return pc
    

    async def setup_data_channel(self, peer_id, channel):
        self.data_channels[peer_id] = channel
        print(f"\n✅ Data channel открыт с {peer_id}")
        
        @channel.on("message")
        def on_message(message):
            print(f"\n💬 {peer_id}: {message}")
            print("Вы: ", end="", flush=True) 
        
        @channel.on("close")
        def on_close():
            print(f"\n❌ Data channel закрыт с {peer_id}")
            if peer_id in self.data_channels:
                del self.data_channels[peer_id]

    
    async def call_peer(self, peer_id):
        print(f"\n📞 Звоним {peer_id}...")
        
        pc = await self.create_peer_connection(peer_id)
        
        channel = pc.createDataChannel("chat")
        await self.setup_data_channel(peer_id, channel)
        
        offer = await pc.createOffer()
        await pc.setLocalDescription(offer)
        
        await self.send_signal(peer_id, 'offer', {
            'sdp': pc.localDescription.sdp,
            'type': pc.localDescription.type
        })

    async def handle_offer(self, peer_id, offer_data):
        print(f"\n📞 Входящий звонок от {peer_id}")
        
        pc = await self.create_peer_connection(peer_id)
        
        offer = RTCSessionDescription(sdp=offer_data['sdp'], type=offer_data['type'])
        await pc.setRemoteDescription(offer)
        
        answer = await pc.createAnswer()
        await pc.setLocalDescription(answer)
        
        await self.send_signal(peer_id, 'answer', {
            'sdp': pc.localDescription.sdp,
            'type': pc.localDescription.type
        })
        
        if peer_id in self.pending_candidates:
            for candidate_data in self.pending_candidates[peer_id]:
                await self.add_ice_candidate(pc, candidate_data)
            self.pending_candidates[peer_id] = []

    async def handle_answer(self, peer_id, answer_data):
        pc = self.peer_connections.get(peer_id)
        if not pc:
            print(f"❌ Нет peer connection для {peer_id}")
            return
        
        answer = RTCSessionDescription(sdp=answer_data['sdp'], type=answer_data['type'])
        await pc.setRemoteDescription(answer)
        
        if peer_id in self.pending_candidates:
            for candidate_data in self.pending_candidates[peer_id]:
                await self.add_ice_candidate(pc, candidate_data)
            self.pending_candidates[peer_id] = []

    async def handle_ice_candidate(self, peer_id, candidate_data):
        pc = self.peer_connections.get(peer_id)
        
        if pc and pc.remoteDescription:
            await self.add_ice_candidate(pc, candidate_data)
        else:
            if peer_id not in self.pending_candidates:
                self.pending_candidates[peer_id] = []
            self.pending_candidates[peer_id].append(candidate_data)
    
    async def add_ice_candidate(self, pc, candidate_data):
        if candidate_data and candidate_data.get('candidate'):
            candidate = RTCIceCandidate(
                candidate=candidate_data['candidate'],
                sdpMid=candidate_data.get('sdpMid'),
                sdpMLineIndex=candidate_data.get('sdpMLineIndex')
            )
            await pc.addIceCandidate(candidate)


    async def send_signal(self, target_peer_id, signal_type, signal_data):
        await self.sio.emit('signal', {
            'target': target_peer_id,
            'type': signal_type,
            'data': signal_data
        })

    async def send_message(self, message):
        if not self.data_channels:
            print("❌ Нет активных соединений. Используйте 'list' и 'call <peer_id>'")
            return
        
        for peer_id, channel in self.data_channels.items():
            if channel.readyState == "open":
                channel.send(message)
        
        print(f"✉️ Отправлено {len(self.data_channels)} пирам")

    async def connect_to_signaling(self):
        try:
            await self.sio.connect(self.signaling_server)
            await self.sio.emit('register', {'peer_id': self.peer_id})
        except Exception as e:
            print(f"❌ Не удалось подключиться к серверу: {e}")
            sys.exit(1)

    async def input_loop(self):
        loop = asyncio.get_event_loop()
        
        while True:
            try:
                message = await loop.run_in_executor(None, input, "Вы: ")
                if message.lower() == 'exit':
                    break
                elif message.lower() == 'list':
                    await self.sio.emit('get_peers', {})
                elif message.lower(). startswith('call '):
                    peer_id = message. split()[1]
                    await self. call_peer(peer_id)
                else:
                    await self.send_message(message)
            except EOFError:
                break
            except Exception as e:
                print(f"❌ Ошибка: {e}")

    async def run(self):
        print(f"🚀 Запуск P2P мессенджера...")
        print(f"🆔 Ваш ID: {self.peer_id}")
        print(f"🌐 Сервер: {self.signaling_server}\n")
        await self.connect_to_signaling()
        await self.input_loop()
        
        for pc in self.peer_connections.values():
            await pc.close()
        await self.sio.disconnect()
        
        print("\n👋 До свидания!")

async def main():
    if len(sys.argv) < 3:
        print("Использование: python Nexus-socket.py <peer_id> <signaling_server>")
        print("Пример: python Nexus-socket.py alice http://localhost:8080")
        sys.exit(1)
    
    peer_id = sys.argv[1]
    signaling_server = sys.argv[2]
    
    messenger = P2PMessenger(peer_id, signaling_server)
    await messenger.run()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n👋 Прервано пользователем")