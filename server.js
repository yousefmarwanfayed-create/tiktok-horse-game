const express = require('express');
const app = express();
const http = require('http').createServer(app);
const io = require('socket.io')(http);
const { WebcastPushConnection } = require('tiktok-live-connector');

// يمكنك تغيير اسم المستخدم هنا
const TIKTOK_USER = 'elzain_agency';
const tiktokLiveConnection = new WebcastPushConnection(TIKTOK_USER);

app.use(express.static('public'));

tiktokLiveConnection.connect().then(state => {
    console.log("✅ متصل ببث: " + TIKTOK_USER);
}).catch(err => console.log("❌ خطأ: " + err.message));

// التقاط كل أنواع الأحداث
['chat', 'gift', 'follow', 'like', 'member'].forEach(eventName => {
    tiktokLiveConnection.on(eventName, (data) => {
        io.emit('tiktokEvent', {
            type: eventName,
            data: {
                nickname: data.uniqueId || data.sender?.uniqueId,
                avatar: data.profilePictureUrl || data.sender?.profilePictureUrl?.urlList[0],
                comment: data.comment,
                giftName: data.giftName,
                repeatCount: data.repeatCount,
                userId: data.userId
            }
        });
    });
});

http.listen(3000, () => console.log('🚀 السيرفر يعمل على بورت 3000 بكامل الصلاحيات'));
