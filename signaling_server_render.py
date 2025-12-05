from aiohttp import web
import socketio
import os

sio = socketio.AsyncServer(cors_allowed_origins='*', async_mode='aiohttp')
app = web.Application()
sio.attach(app)

peers = {}
peer_sessions = {}

@sio.event
async def connect(sid, environ):
    print(f"✅ Клиент подключился: {sid}")

@sio. event
async def disconnect(sid):
    if sid in peers:
        peer_id = peers[sid]
        print(f"❌ Клиент отключился: {peer_id}")
        del peers[sid]
        if peer_id in peer_sessions:
            del peer_sessions[peer_id]

@sio.event
async def register(sid, data):
    peer_id = data['peer_id']
    peers[sid] = peer_id
    peer_sessions[peer_id] = sid
    print(f"📝 Зарегистрирован пир: {peer_id}")
    await sio.emit('registered', {'status': 'ok', 'peer_id': peer_id}, room=sid)

@sio.event
async def get_peers(sid, data):
    online_peers = list(peer_sessions.keys())
    current_peer = peers.get(sid)
    if current_peer:
        online_peers = [p for p in online_peers if p != current_peer]
    await sio.emit('peers_list', {'peers': online_peers}, room=sid)

@sio. event
async def signal(sid, data):
    target_peer_id = data['target']
    
    if target_peer_id not in peer_sessions:
        await sio.emit('error', {'message': 'Пир не найден'}, room=sid)
        return
    
    target_sid = peer_sessions[target_peer_id]
    sender_peer_id = peers[sid]
    
    signal_data = {
        'from': sender_peer_id,
        'type': data['type'],
        'data': data['data']
    }
    
    await sio.emit('signal', signal_data, room=target_sid)
    print(f"📡 Сигнал {data['type']} от {sender_peer_id} к {target_peer_id}")

if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 10000))
    print(f"🚀 Сервер запущен на порту {PORT}")
    web.run_app(app, host='0.0.0.0', port=PORT)