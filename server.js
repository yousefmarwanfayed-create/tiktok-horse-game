const express = require('express');
const app = express();
const http = require('http').createServer(app);
const io = require('socket.io')(http);
const path = require('path');
const { WebcastPushConnection } = require('tiktok-live-connector');

const TIKTOK_USER = 'janteeshaaban'; 

app.use(express.static(path.join(__dirname, 'public')));

const tiktokLiveConnection = new WebcastPushConnection(TIKTOK_USER);

tiktokLiveConnection.connect().then(state => {
    console.log(`✅ متصل بـ: ${state.roomId}`);
}).catch(err => {
    console.error("❌ فشل الاتصال:", err.message);
});

tiktokLiveConnection.on('gift', (data) => {
    console.log(`🎁 هدية من ${data.uniqueId}: ${data.giftName}`);
    io.emit('giftEvent', data);
});

http.listen(3000, () => console.log('🚀 السيرفر يعمل على http://localhost:3000'));
