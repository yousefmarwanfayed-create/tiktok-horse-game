const express = require('express');
const path = require('path');
const { WebcastPushConnection } = require('tiktok-live-connector');

const app = express();
const PORT = process.env.PORT || 10000;
const TIKTOK_USER = 'yo_u__ef';

app.use(express.static(path.join(__dirname, 'public')));

app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

app.listen(PORT, async () => {
    console.log('🚀 الخادم يعمل على المنفذ ' + PORT);
    console.log('🔄 جاري الاتصال بـ @' + TIKTOK_USER + '...');
    try {
        const conn = new WebcastPushConnection(TIKTOK_USER, {
            enableWebsocketUpgrade: true,
            requestOptions: { timeout: 20000 }
        });
        conn.on('connected', (state) => {
            console.log('✅ متصل بالبث @' + TIKTOK_USER + ' | الغرفة: ' + state.roomId);
        });
        conn.on('disconnected', () => {
            console.log('🔌 انقطع الاتصال');
        });
        conn.on('gift', (gift) => {
            console.log('🎁 هدية:', gift.giftName, '×', gift.repeatCount);
        });
        await conn.connect();
    } catch (err) {
        console.log('❌ فشل الاتصال: ' + err.message);
    }
});
