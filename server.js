const express = require('express');
const WebSocket = require('ws');
const http = require('http');
const { WebcastPushConnection } = require('tiktok-live-connector');
const path = require('path');

const app = express();
const PORT = process.env.PORT || 10000;

app.use(express.static(path.join(__dirname, 'public')));

app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

const server = http.createServer(app);
const wss = new WebSocket.Server({ server, path: '/ws' });

const GIFT_MAP = {
    'Rose': 0,
    'TikTok': 1,
    'Love You So Much': 2,
    'Got It Right': 3,
    "You're Awesome": 4,
    'Ice Cream': 5,
    'Lightning Bolt': 6,
    'Hot Chili Pepper': 7,
    "It's an Atom": 8,
    'Smoke Heart': 9,
    'Light Banter': 10,
    'New Songs': 11,
    'Old School Vibes': 12
};

let tiktokConnection = null;
let gameClient = null;

wss.on('connection', (ws) => {
    console.log('🎮 اتصال جديد من اللعبة');
    gameClient = ws;

    ws.on('message', async (message) => {
        try {
            const data = JSON.parse(message);
            console.log('📨 رسالة من اللعبة:', data.action);

            if (data.action === 'connect') {
                try {
                    if (tiktokConnection) {
                        await tiktokConnection.disconnect();
                    }

                    console.log('🔄 جاري الاتصال بـ @' + data.username);
                    tiktokConnection = new WebcastPushConnection(data.username);

                    tiktokConnection.on('connected', (state) => {
                        console.log('✅ متصل بالبث: @' + data.username);
                        ws.send(JSON.stringify({
                            type: 'connected',
                            username: data.username,
                            roomId: state.roomId
                        }));
                    });

                    tiktokConnection.on('gift', (giftData) => {
                        console.log('🎁 هدية:', giftData.giftName, '×', giftData.repeatCount);
                        const horseIndex = GIFT_MAP[giftData.giftName];
                        if (horseIndex !== undefined && ws.readyState === WebSocket.OPEN) {
                            ws.send(JSON.stringify({
                                type: 'gift',
                                horseIndex: horseIndex,
                                count: giftData.repeatCount || 1,
                                giftName: giftData.giftName,
                                sender: giftData.uniqueId
                            }));
                        }
                    });

                    tiktokConnection.on('disconnected', () => {
                        console.log('🔌 انقطع الاتصال');
                        if (ws.readyState === WebSocket.OPEN) {
                            ws.send(JSON.stringify({ type: 'disconnected' }));
                        }
                    });

                    await tiktokConnection.connect();

                } catch (err) {
                    console.log('❌ خطأ:', err.message);
                    ws.send(JSON.stringify({
                        type: 'error',
                        message: 'فشل الاتصال. تأكد أن البث مباشر والحساب صحيح.'
                    }));
                }
            }

            if (data.action === 'disconnect') {
                if (tiktokConnection) {
                    await tiktokConnection.disconnect();
                    tiktokConnection = null;
                }
            }
        } catch (e) {
            console.log('❌ خطأ في الرسالة:', e.message);
        }
    });

    ws.on('close', () => {
        console.log('🔌 اللعبة انفصلت');
        gameClient = null;
    });

    ws.send(JSON.stringify({ type: 'ready', message: 'الخادم جاهز' }));
});

server.listen(PORT, () => {
    console.log('🚀 الخادم يعمل على المنفذ ' + PORT);
});
