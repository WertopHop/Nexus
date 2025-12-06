from aiohttp import web
import socketio
import logging
import socket


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)
sio = socketio.AsyncServer(
    cors_allowed_origins='*',
    async_mode='aiohttp',
    logger=False,
    engineio_logger=False
)
app = web.Application()
sio.attach(app)
peers = {}
peer_sessions = {}


@sio.event
async def connect(sid, environ):
    client_ip = environ.get('REMOTE_ADDR', 'unknown')
    logger.info(f"✅ Новое подключение | SID: {sid} | IP: {client_ip}")


@sio.event
async def disconnect(sid):
    if sid in peers:
        peer_id = peers[sid]
        logger.info(f"❌ Отключение | Пир: {peer_id} | SID: {sid}")
        del peers[sid]
        if peer_id in peer_sessions:
            del peer_sessions[peer_id]
        logger.info(f"📊 Пиров онлайн: {len(peer_sessions)}")
    else:
        logger.info(f"❌ Отключение незарегистрированного клиента | SID: {sid}")


@sio.event
async def register(sid, data):
    try:
        peer_id = data.get('peer_id')
        if not peer_id:
            await sio.emit('error', {'message': 'peer_id обязателен для регистрации'}, room=sid)
            logger.warning(f"⚠️  Попытка регистрации без peer_id | SID: {sid}")
            return
        if peer_id in peer_sessions and peer_sessions[peer_id] != sid:
            await sio.emit('error', {'message': f'peer_id "{peer_id}" уже используется'}, room=sid)
            logger.warning(f"⚠️  Попытка использовать занятый peer_id: {peer_id} | SID: {sid}")
            return
        peers[sid] = peer_id
        peer_sessions[peer_id] = sid
        logger.info(f"📝 Зарегистрирован пир: {peer_id} | SID: {sid}")
        logger.info(f"📊 Пиров онлайн: {len(peer_sessions)}")
        await sio.emit('registered', {'status': 'ok','peer_id': peer_id}, room=sid)
    except Exception as e:
        logger.error(f"❌ Ошибка при регистрации | SID: {sid} | Ошибка: {e}")
        await sio.emit('error', {
            'message': 'Ошибка сервера при регистрации'
        }, room=sid)


@sio.event
async def get_peers(sid, data):
    try:
        online_peers = list(peer_sessions.keys())
        current_peer = peers.get(sid)
        if current_peer:
            online_peers = [p for p in online_peers if p != current_peer]
        logger.info(f"📋 Запрос списка пиров от {current_peer or sid} | Найдено: {len(online_peers)}")
        await sio.emit('peers_list', {'peers': online_peers}, room=sid)
    except Exception as e:
        logger. error(f"❌ Ошибка при получении списка пиров | SID: {sid} | Ошибка: {e}")
        await sio.emit('error', {'message': 'Ошибка сервера при получении списка пиров'}, room=sid)


@sio.event
async def signal(sid, data):
    try:
        target_peer_id = data.get('target')
        signal_type = data.get('type')
        signal_data = data.get('data')
        if not target_peer_id or not signal_type or not signal_data:
            await sio.emit('error', {
                'message': 'Неполные данные сигнала'
            }, room=sid)
            logger.warning(f"⚠️  Получен неполный сигнал от {sid}")
            return
        if target_peer_id not in peer_sessions:
            await sio.emit('error', {
                'message': f'Пир "{target_peer_id}" не найден или не в сети'
            }, room=sid)
            logger.warning(f"⚠️  Попытка отправить сигнал несуществующему пиру: {target_peer_id}")
            return
        target_sid = peer_sessions[target_peer_id]
        sender_peer_id = peers.get(sid, 'unknown')
        signal_message = {
            'from': sender_peer_id,
            'type': signal_type,
            'data': signal_data
        }
        await sio.emit('signal', signal_message, room=target_sid)
        logger.info(f"📡 Сигнал {signal_type} | {sender_peer_id} → {target_peer_id}")
    except Exception as e:
        logger.error(f"❌ Ошибка при передаче сигнала | SID: {sid} | Ошибка: {e}")
        await sio.emit('error', {'message': 'Ошибка сервера при передаче сигнала'}, room=sid)


async def handle_root(request):
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>WebRTC Signaling Server</title>
        <meta charset="utf-8">
        <style>
            body {{
                font-family: Arial, sans-serif;
                max-width: 800px;
                margin: 50px auto;
                padding: 20px;
                background: #f5f5f5;
            }}
            .container {{
                background: white;
                padding: 30px;
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }}
            h1 {{ color: #333; }}
            . status {{ 
                color: #28a745; 
                font-size: 24px;
                font-weight: bold;
            }}
            .info {{
                background: #e9ecef;
                padding: 15px;
                border-radius: 5px;
                margin: 15px 0;
            }}
            code {{
                background: #f8f9fa;
                padding: 2px 6px;
                border-radius: 3px;
                font-family: monospace;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🚀 WebRTC Signaling Server</h1>
            <p class="status">✅ Сервер работает! </p>
            
            <div class="info">
                <h3>📊 Статистика:</h3>
                <p>Пиров онлайн: <strong>{len(peer_sessions)}</strong></p>
                <p>Активных соединений: <strong>{len(peers)}</strong></p>
            </div>
            
            <div class="info">
                <h3>📡 Подключение:</h3>
                <p>Используйте Socket.IO клиент для подключения к этому серверу. </p>
                <p>Endpoint: <code>{request.url}</code></p>
            </div>
            
            <div class="info">
                <h3>💡 Поддерживаемые события:</h3>
                <ul>
                    <li><code>register</code> - Регистрация пира</li>
                    <li><code>get_peers</code> - Получить список пиров</li>
                    <li><code>signal</code> - Передача WebRTC сигналов</li>
                </ul>
            </div>
        </div>
    </body>
    </html>
    """
    return web.Response(text=html, content_type='text/html')


async def handle_health(request):
    return web.json_response({
        'status': 'healthy',
        'peers_online': len(peer_sessions),
        'active_connections': len(peers)
    })


app.router.add_get('/', handle_root)
app.router.add_get('/health', handle_health)


def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except Exception:
        return "127.0.0.1"

def print_startup_info(host, port):
    local_ip = get_local_ip()
    
    print("\n" + "=" * 70)
    print("🚀 СИГНАЛЬНЫЙ СЕРВЕР WEBRTC ЗАПУЩЕН!")
    print("=" * 70)
    print("\n📍 АДРЕСА ДЛЯ ПОДКЛЮЧЕНИЯ:\n")
    print(f"   Localhost:        http://127.0.0.1:{port}")
    print(f"   Локальная сеть:   http://{local_ip}:{port}")
    print(f"   Все интерфейсы:   http://{host}:{port}")
    print("\n📊 МОНИТОРИНГ:\n")
    print(f"   Веб-интерфейс:    http://localhost:{port}/")
    print(f"   Health check:     http://localhost:{port}/health")
    print("\n" + "=" * 70)
    print("📡 СЕРВЕР ГОТОВ К ПРИЕМУ ПОДКЛЮЧЕНИЙ")
    print("=" * 70)
    print("\nДля остановки нажмите Ctrl+C\n")

    
if __name__ == '__main__':
    HOST = '0.0.0.0'
    PORT = 8080
    print_startup_info(HOST, PORT)
    try:
        web.run_app(
            app,
            host=HOST,
            port=PORT,
            print=None 
        )
    except KeyboardInterrupt:
        print("\n\n👋 Сервер остановлен пользователем")
    except Exception as e:
        logger.error(f"❌ Критическая ошибка: {e}")