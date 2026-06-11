const express = require('express');
const WebSocket = require('ws');
const http = require('http');
const { WebcastPushConnection } = require('tiktok-live-connector');
const path = require('path');

const app = express();
const PORT = process.env.PORT || 3000;

// خدمة الملفات الثابتة
app.use(express.static(path.join(__dirname, 'public')));

// الصفحة الرئيسية
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

const server = http.createServer(app);
const wss = new WebSocket.Server({ server });

// قاموس الهدايا - يطابق أسماء الهدايا في TikTok مع أرقام الخيول
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
        const data = JSON.parse(message);

        // طلب الاتصال بـ TikTok
        if (data.action === 'connect') {
            try {
                if (tiktokConnection) {
                    await tiktokConnection.disconnect();
                }

                tiktokConnection = new WebcastPushConnection(data.username);

                tiktokConnection.on('connected', (state) => {
                    console.log(`✅ متصل بالبث: @${data.username}`);
                    ws.send(JSON.stringify({
                        type: 'connected',
                        username: data.username,
                        roomId: state.roomId
                    }));
                });

                // استقبال الهدايا
                tiktokConnection.on('gift', (giftData) => {
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
                    if (ws.readyState === WebSocket.OPEN) {
                        ws.send(JSON.stringify({ type: 'disconnected' }));
                    }
                });

                await tiktokConnection.connect();

            } catch (err) {
                ws.send(JSON.stringify({
                    type: 'error',
                    message: '❌ فشل الاتصال. تأكد أن البث مباشر واسم الحساب صحيح.'
                }));
            }
        }

        if (data.action === 'disconnect') {
            if (tiktokConnection) {
                await tiktokConnection.disconnect();
                tiktokConnection = null;
            }
        }
    });

    ws.on('close', () => {
        gameClient = null;
    });
});

server.listen(PORT, () => {
    console.log(`🚀 الخادم يعمل على المنفذ ${PORT}`);
});
