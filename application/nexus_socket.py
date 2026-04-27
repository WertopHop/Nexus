import asyncio
import json
import socketio
from aiortc import RTCPeerConnection, RTCSessionDescription, RTCIceCandidate
import logging

from socket_parts.dh import (
    dh_generate_keypair,
    dh_derive_key,
    dh_decode_public_key,
    dh_make_init_message,
    dh_make_resp_message,
    dh_is_handshake_message,
    encrypt_message,
    decrypt_message,
    is_encrypted_message,
)
from socket_parts.signals import P2PMessengerSignals

logging.basicConfig(level=logging.WARNING)


class P2PMessenger:
    def __init__(self, peer_id: str, signaling_server: str):
        self.peer_id = peer_id
        self.signaling_server = signaling_server
        self.sio = socketio.AsyncClient()
        self.peer_connections = {}
        self.data_channels = {}
        self.pending_candidates = {}
        self.signals = P2PMessengerSignals()
        self.encryption_keys: dict = {}
        self._dh_private_keys: dict = {}
        self.sio.on('registered', self.on_registered)
        self.sio.on('peers_list', self.on_peers_list)
        self.sio.on('signal', self.on_signal)
        self.sio.on('error', self.on_error)

    # ------------------------------------------------------------------
    # Signaling server events
    # ------------------------------------------------------------------

    async def on_registered(self, data):
        self.signals.peer_registered.emit(data['peer_id'])

    async def on_peers_list(self, data):
        pass

    async def on_error(self, data):
        self.signals.error_occurred.emit(data['message'])

    async def on_signal(self, data):
        from_peer = data['from']
        signal_type = data['type']
        signal_data = data['data']

        if signal_type == 'offer':
            await self.handle_offer(from_peer, signal_data)
        elif signal_type == 'answer':
            await self.handle_answer(from_peer, signal_data)
        elif signal_type == 'ice-candidate':
            await self.handle_ice_candidate(from_peer, signal_data)

    # ------------------------------------------------------------------
    # WebRTC peer connection lifecycle
    # ------------------------------------------------------------------

    async def create_peer_connection(self, peer_id: str):
        pc = RTCPeerConnection()

        self.peer_connections[peer_id] = pc
        self.pending_candidates[peer_id] = []

        @pc.on("datachannel")
        def on_datachannel(channel):
            asyncio.create_task(self.setup_data_channel(peer_id, channel, is_initiator=False))

        @pc.on("icecandidate")
        async def on_icecandidate(candidate):
            if candidate:
                await self.send_signal(peer_id, 'ice-candidate', {
                    'candidate': candidate.candidate,
                    'sdpMid': candidate.sdpMid,
                    'sdpMLineIndex': candidate.sdpMLineIndex
                })

        @pc.on("connectionstatechange")
        async def on_connectionstatechange():
            if pc.connectionState == "connected":
                self.signals.connection_established.emit(peer_id)
            elif pc.connectionState in ("failed", "closed"):
                await self.cleanup_peer(peer_id)
                self.signals.connection_closed.emit(peer_id)

        return pc

    async def cleanup_peer(self, peer_id: str):
        if peer_id in self.peer_connections:
            await self.peer_connections[peer_id].close()
            del self.peer_connections[peer_id]
        if peer_id in self.data_channels:
            del self.data_channels[peer_id]
        if peer_id in self.encryption_keys:
            del self.encryption_keys[peer_id]
        if peer_id in self._dh_private_keys:
            del self._dh_private_keys[peer_id]

    # ------------------------------------------------------------------
    # Data channel
    # ------------------------------------------------------------------

    async def setup_data_channel(self, peer_id: str, channel, is_initiator: bool = False):
        self.data_channels[peer_id] = channel
        self.signals.connection_established.emit(peer_id)

        @channel.on("open")
        def on_open():
            if is_initiator:
                asyncio.create_task(self._dh_send_public_key(peer_id))

        @channel.on("message")
        def on_message(message):
            if dh_is_handshake_message(message):
                asyncio.create_task(self._dh_handle_message(peer_id, message))
            elif is_encrypted_message(message):
                key = self.encryption_keys.get(peer_id)
                if key:
                    try:
                        plaintext = decrypt_message(key, message)
                        self.signals.message_received.emit(peer_id, plaintext)
                    except ValueError:
                        logging.warning("Failed to decrypt message from %s", peer_id)
            else:
                self.signals.message_received.emit(peer_id, message)

        @channel.on("close")
        def on_close():
            if peer_id in self.data_channels:
                del self.data_channels[peer_id]
            self.signals.connection_closed.emit(peer_id)

    # ------------------------------------------------------------------
    # Diffie-Hellman key exchange
    # ------------------------------------------------------------------

    async def _dh_send_public_key(self, peer_id: str):
        private_key, public_key = dh_generate_keypair()
        self._dh_private_keys[peer_id] = private_key
        channel = self.data_channels.get(peer_id)
        if channel and channel.readyState == "open":
            channel.send(dh_make_init_message(public_key))

    async def _dh_handle_message(self, peer_id: str, raw: str):
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            return

        msg_type = data.get("_n")

        if msg_type == "dh_init":
            peer_public_key = dh_decode_public_key(data["pub"])
            private_key, public_key = dh_generate_keypair()
            self.encryption_keys[peer_id] = dh_derive_key(private_key, peer_public_key)
            channel = self.data_channels.get(peer_id)
            if channel and channel.readyState == "open":
                channel.send(dh_make_resp_message(public_key))
            self.signals.dh_key_established.emit(peer_id)

        elif msg_type == "dh_resp":
            private_key = self._dh_private_keys.pop(peer_id, None)
            if private_key is None:
                return
            peer_public_key = dh_decode_public_key(data["pub"])
            self.encryption_keys[peer_id] = dh_derive_key(private_key, peer_public_key)
            self.signals.dh_key_established.emit(peer_id)

    # ------------------------------------------------------------------
    # Call flow
    # ------------------------------------------------------------------

    async def call_peer(self, peer_id: str):
        if peer_id in self.peer_connections:
            return
        pc = await self.create_peer_connection(peer_id)
        channel = pc.createDataChannel("chat")
        await self.setup_data_channel(peer_id, channel, is_initiator=True)
        offer = await pc.createOffer()
        await pc.setLocalDescription(offer)
        await self.send_signal(peer_id, 'offer', {
            'sdp': pc.localDescription.sdp,
            'type': pc.localDescription.type
        })

    async def handle_offer(self, peer_id: str, offer_data: dict):
        self.signals.incoming_call.emit(peer_id)
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

    async def handle_answer(self, peer_id: str, answer_data: dict):
        pc = self.peer_connections.get(peer_id)
        if not pc:
            return
        answer = RTCSessionDescription(sdp=answer_data['sdp'], type=answer_data['type'])
        await pc.setRemoteDescription(answer)
        if peer_id in self.pending_candidates:
            for candidate_data in self.pending_candidates[peer_id]:
                await self.add_ice_candidate(pc, candidate_data)
            self.pending_candidates[peer_id] = []

    async def handle_ice_candidate(self, peer_id: str, candidate_data: dict):
        pc = self.peer_connections.get(peer_id)
        if pc and pc.remoteDescription:
            await self.add_ice_candidate(pc, candidate_data)
        else:
            if peer_id not in self.pending_candidates:
                self.pending_candidates[peer_id] = []
            self.pending_candidates[peer_id].append(candidate_data)

    async def add_ice_candidate(self, pc, candidate_data: dict):
        if candidate_data and candidate_data.get('candidate'):
            candidate = RTCIceCandidate(
                candidate=candidate_data['candidate'],
                sdpMid=candidate_data.get('sdpMid'),
                sdpMLineIndex=candidate_data.get('sdpMLineIndex')
            )
            await pc.addIceCandidate(candidate)

    # ------------------------------------------------------------------
    # Messaging
    # ------------------------------------------------------------------

    async def send_signal(self, target_peer_id: str, signal_type: str, signal_data: dict):
        await self.sio.emit('signal', {
            'target': target_peer_id,
            'type': signal_type,
            'data': signal_data
        })

    async def send_message(self, peer_id: str, message: str) -> bool:
        channel = self.data_channels.get(peer_id)
        if channel and channel.readyState == "open":
            key = self.encryption_keys.get(peer_id)
            payload = encrypt_message(key, message) if key else message
            channel.send(payload)
            return True
        return False

    async def send_message_to_all(self, message: str) -> int:
        sent_count = 0
        for peer_id, channel in self.data_channels.items():
            if channel.readyState == "open":
                key = self.encryption_keys.get(peer_id)
                payload = encrypt_message(key, message) if key else message
                channel.send(payload)
                sent_count += 1
        return sent_count

    def is_connected_to(self, peer_id: str) -> bool:
        channel = self.data_channels.get(peer_id)
        return channel is not None and channel.readyState == "open"

    # ------------------------------------------------------------------
    # Signaling server connection
    # ------------------------------------------------------------------

    async def connect_to_signaling(self):
        try:
            await self.sio.connect(self.signaling_server)
            await self.sio.emit('register', {'peer_id': self.peer_id})
            return True
        except Exception as e:
            self.signals.error_occurred.emit(f"Connection failed: {e}")
            return False

    async def disconnect(self):
        for peer_id in list(self.peer_connections.keys()):
            await self.cleanup_peer(peer_id)
        await self.sio.disconnect()

    async def request_peers_list(self):
        await self.sio.emit('get_peers', {})