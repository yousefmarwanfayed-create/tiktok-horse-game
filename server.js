const { WebcastPushConnection } = require('tiktok-live-connector');
const TIKTOK_USER = 'janteeshaaban';

const tiktokLiveConnection = new WebcastPushConnection(TIKTOK_USER, {
    requestOptions: {
        timeout: 10000,
        // هذه الترويسات هي التي "تخدع" تيك توك وتوهمه أننا متصفح
        headers: {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Referer": "https://www.tiktok.com/",
            "Cookie": "tt_chain_token=YOUR_TOKEN_HERE" // اختياري، لكن يساعد أحياناً
        }
    }
});

tiktokLiveConnection.connect().then(state => {
    console.log("✅ تم الاتصال بنجاح كمتصفح! الغرفة ID: " + state.roomId);
}).catch(err => {
    console.error("❌ فشل الاتصال، تأكد من أن الحساب في حالة بث مباشر.", err.message);
});

tiktokLiveConnection.on('gift', (data) => {
    console.log(`🎁 هدية من ${data.uniqueId}: ${data.giftName}`);
});
