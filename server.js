const { WebcastPushConnection } = require('tiktok-live-connector');
const tiktokLiveConnection = new WebcastPushConnection('janteeshaaban');

tiktokLiveConnection.connect().then(state => {
    console.log("✅ متصل! الغرفة: " + state.roomId);
}).catch(err => {
    console.log("❌ فشل الاتصال. حاول مرة أخرى.");
});
