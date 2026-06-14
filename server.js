const { WebcastPushConnection } = require('tiktok-live-connector');
const TIKTOK_USER = 'janteeshaaban'; 

// الاتصال المباشر بأبسط صورة ممكنة
const tiktokLiveConnection = new WebcastPushConnection(TIKTOK_USER);

tiktokLiveConnection.connect().then(state => {
    console.log("✅ متصل بنجاح: " + state.roomId);
}).catch(err => {
    console.log("❌ فشل الاتصال، تأكد أن الحساب في حالة بث مباشر حالياً.");
});

tiktokLiveConnection.on('gift', (data) => {
    console.log("🎁 وصلت هدية:", data.giftName);
});
