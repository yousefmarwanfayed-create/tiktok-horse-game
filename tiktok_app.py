from TikTokLive import TikTokLiveClient
from TikTokLive.events import CommentEvent, GiftEvent, ConnectEvent, FollowEvent, ShareEvent
from TikTokLive.client.errors import UserOfflineError
from flask import Flask, render_template_string
from flask_socketio import SocketIO
import threading
import time

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, cors_allowed_origins="*")

USERNAME = "aboaya_91"
client = TikTokLiveClient(unique_id=USERNAME)

HTML = """
<!DOCTYPE html>
<html lang="ar">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🎮 TikTok Live</title>
    <script src="https://cdn.socket.io/4.5.0/socket.io.min.js"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', system-ui, sans-serif;
            background: #0a0a12;
            color: #fff;
            min-height: 100vh;
            background: linear-gradient(135deg, #0a0a12 0%, #1a0a2e 50%, #0a0a12 100%);
            padding: 20px;
        }
        .header {
            background: rgba(26, 26, 46, 0.8);
            backdrop-filter: blur(20px);
            padding: 16px 24px;
            border-radius: 16px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            border: 1px solid rgba(254, 44, 85, 0.2);
            margin-bottom: 20px;
            flex-wrap: wrap;
            gap: 10px;
        }
        .logo {
            display: flex;
            align-items: center;
            gap: 10px;
            font-size: 24px;
            font-weight: 800;
            background: linear-gradient(135deg, #fe2c55, #ff6b8a);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .logo i { font-size: 28px; }
        .live-badge {
            background: #fe2c55;
            color: #fff;
            padding: 4px 16px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 700;
            display: flex;
            align-items: center;
            gap: 6px;
            animation: pulse 2s infinite;
        }
        @keyframes pulse { 0%,100% { transform: scale(1); } 50% { transform: scale(1.05); } }
        .status {
            color: #4ade80;
            font-size: 13px;
            font-weight: 500;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        .status-dot {
            display: inline-block;
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: #4ade80;
            animation: pulse 1.5s infinite;
        }
        .stats {
            display: flex;
            gap: 15px;
            flex-wrap: wrap;
        }
        .stat-box {
            background: rgba(255,255,255,0.05);
            padding: 8px 16px;
            border-radius: 12px;
            text-align: center;
            min-width: 70px;
        }
        .stat-box .num {
            font-size: 20px;
            font-weight: 700;
        }
        .stat-box .num.pink { color: #fe2c55; }
        .stat-box .num.gold { color: #ffd700; }
        .stat-box .num.green { color: #4ade80; }
        .stat-box .num.blue { color: #60a5fa; }
        .stat-box .label { font-size: 11px; color: #888; }
        .grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
        }
        .card {
            background: rgba(26, 26, 46, 0.7);
            backdrop-filter: blur(10px);
            border-radius: 16px;
            padding: 20px;
            border: 1px solid rgba(255,255,255,0.06);
        }
        .card-title {
            font-size: 15px;
            font-weight: 600;
            color: #aaa;
            display: flex;
            align-items: center;
            gap: 10px;
            margin-bottom: 16px;
        }
        .card-title .badge {
            background: #fe2c55;
            color: #fff;
            border-radius: 30px;
            padding: 0 12px;
            font-size: 12px;
            font-weight: 700;
            height: 22px;
            display: flex;
            align-items: center;
        }
        .card-title .badge.gold { background: #ffd700; color: #000; }
        .scroll-area {
            max-height: 350px;
            overflow-y: auto;
            padding-right: 4px;
        }
        .scroll-area::-webkit-scrollbar { width: 4px; }
        .scroll-area::-webkit-scrollbar-thumb { background: #fe2c55; border-radius: 10px; }
        .scroll-area.gift-scroll::-webkit-scrollbar-thumb { background: #ffd700; }
        .comment-item {
            display: flex;
            align-items: flex-start;
            gap: 12px;
            padding: 10px 12px;
            border-radius: 12px;
            margin-bottom: 6px;
            animation: slideIn 0.4s ease;
            background: rgba(255,255,255,0.02);
        }
        .comment-item:hover { background: rgba(255,255,255,0.05); }
        .comment-item .avatar {
            width: 40px;
            height: 40px;
            border-radius: 50%;
            border: 2px solid #fe2c55;
            object-fit: cover;
            flex-shrink: 0;
        }
        .comment-item .info { flex: 1; }
        .comment-item .name {
            font-size: 13px;
            font-weight: 600;
            color: #fe2c55;
        }
        .comment-item .text {
            font-size: 14px;
            color: #e0e0e0;
            margin-top: 2px;
            word-wrap: break-word;
        }
        .gift-item {
            display: flex;
            align-items: center;
            gap: 14px;
            padding: 10px 14px;
            background: linear-gradient(135deg, rgba(255,215,0,0.05), rgba(255,215,0,0.01));
            border-radius: 12px;
            margin-bottom: 6px;
            border: 1px solid rgba(255,215,0,0.08);
            animation: slideIn 0.4s ease;
        }
        .gift-item .avatar {
            width: 40px;
            height: 40px;
            border-radius: 50%;
            border: 2px solid #ffd700;
            object-fit: cover;
            flex-shrink: 0;
        }
        .gift-item .info { flex: 1; }
        .gift-item .name { font-size: 13px; font-weight: 600; color: #ddd; }
        .gift-item .gift-details {
            display: flex;
            align-items: center;
            gap: 10px;
            margin-top: 2px;
            flex-wrap: wrap;
        }
        .gift-item .gift-name { color: #ffd700; font-weight: 700; font-size: 15px; }
        .gift-item .gift-count {
            background: rgba(255,215,0,0.15);
            color: #ffd700;
            padding: 0 12px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 700;
        }
        .gift-item .gift-diamonds { color: #888; font-size: 11px; }
        .activity-item {
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 8px 12px;
            border-radius: 12px;
            margin-bottom: 4px;
            animation: slideIn 0.3s ease;
            background: rgba(255,255,255,0.02);
        }
        .activity-item .icon {
            width: 32px;
            height: 32px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 14px;
            flex-shrink: 0;
        }
        .activity-item .icon.follow { background: rgba(74,222,128,0.15); color: #4ade80; }
        .activity-item .icon.share { background: rgba(96,165,250,0.15); color: #60a5fa; }
        .activity-item .icon.gift { background: rgba(255,215,0,0.15); color: #ffd700; }
        .activity-item .icon.comment { background: rgba(254,44,85,0.15); color: #fe2c55; }
        .activity-item .info { flex: 1; font-size: 13px; color: #ccc; }
        .activity-item .info strong { color: #fff; font-weight: 600; }
        .activity-item .time { font-size: 10px; color: #555; }
        .empty-state {
            text-align: center;
            padding: 40px 20px;
            color: #444;
        }
        .empty-state i { font-size: 48px; margin-bottom: 16px; opacity: 0.3; }
        @keyframes slideIn {
            from { opacity: 0; transform: translateX(-20px); }
            to { opacity: 1; transform: translateX(0); }
        }
        @media (max-width: 768px) {
            .grid { grid-template-columns: 1fr; }
            .header { flex-direction: column; align-items: stretch; }
        }
    </style>
</head>
<body>

    <div class="header">
        <div style="display:flex;align-items:center;gap:12px;flex-wrap:wrap;">
            <div class="logo"><i class="fab fa-tiktok"></i><span>Live</span></div>
            <div class="live-badge"><i class="fas fa-circle"></i> LIVE</div>
            <div class="status">
                <span class="status-dot" id="statusDot"></span>
                <span id="statusText">جاري الاتصال...</span>
            </div>
        </div>
        <div class="stats">
            <div class="stat-box"><div class="num pink" id="sComments">0</div><div class="label">تعليقات</div></div>
            <div class="stat-box"><div class="num gold" id="sGifts">0</div><div class="label">هدايا</div></div>
            <div class="stat-box"><div class="num green" id="sFollows">0</div><div class="label">متابعات</div></div>
            <div class="stat-box"><div class="num blue" id="sShares">0</div><div class="label">مشاركات</div></div>
        </div>
    </div>

    <div class="grid">
        <div class="card">
            <div class="card-title">
                <i class="fas fa-comment" style="color:#fe2c55;"></i>
                التعليقات
                <span class="badge" id="cBadge">0</span>
            </div>
            <div class="scroll-area" id="comments">
                <div class="empty-state"><i class="fas fa-comment-slash"></i><p>⏳ في انتظار التعليقات...</p></div>
            </div>
        </div>

        <div class="card">
            <div class="card-title">
                <i class="fas fa-gift" style="color:#ffd700;"></i>
                الهدايا
                <span class="badge gold" id="gBadge">0</span>
            </div>
            <div class="scroll-area gift-scroll" id="gifts">
                <div class="empty-state"><i class="fas fa-gift"></i><p>⏳ في انتظار الهدايا...</p></div>
            </div>
        </div>
    </div>

    <div class="card" style="margin-top:20px;">
        <div class="card-title">
            <i class="fas fa-bolt" style="color:#60a5fa;"></i>
            النشاطات
        </div>
        <div class="scroll-area" id="activity" style="max-height:200px;">
            <div class="empty-state"><i class="fas fa-clock"></i><p>⏳ في انتظار الأحداث...</p></div>
        </div>
    </div>

    <script>
        const socket = io();
        let stats = { comments: 0, gifts: 0, follows: 0, shares: 0 };

        socket.on('connect', () => {
            document.getElementById('statusDot').className = 'status-dot';
            document.getElementById('statusText').textContent = 'متصل بالخادم';
        });

        socket.on('system', (data) => {
            document.getElementById('statusDot').className = 'status-dot';
            document.getElementById('statusText').textContent = data.msg;
        });

        socket.on('comment', (data) => {
            stats.comments++;
            updateStats();
            const div = document.getElementById('comments');
            if (div.querySelector('.empty-state')) div.innerHTML = '';
            div.insertAdjacentHTML('afterbegin', `
                <div class="comment-item">
                    <img class="avatar" src="${data.avatar || 'https://ui-avatars.com/api/?name='+encodeURIComponent(data.nickname)+'&background=fe2c55&color=fff&size=40'}" onerror="this.src='https://ui-avatars.com/api/?name=${encodeURIComponent(data.nickname)}&background=fe2c55&color=fff&size=40'">
                    <div class="info">
                        <div class="name">${data.nickname}</div>
                        <div class="text">${data.text}</div>
                    </div>
                </div>
            `);
            document.getElementById('cBadge').textContent = stats.comments;
            addActivity('comment', data.nickname, data.text);
        });

        socket.on('gift', (data) => {
            stats.gifts++;
            updateStats();
            const div = document.getElementById('gifts');
            if (div.querySelector('.empty-state')) div.innerHTML = '';
            div.insertAdjacentHTML('afterbegin', `
                <div class="gift-item">
                    <img class="avatar" src="${data.avatar || 'https://ui-avatars.com/api/?name='+encodeURIComponent(data.nickname)+'&background=ffd700&color=fff&size=40'}" onerror="this.src='https://ui-avatars.com/api/?name=${encodeURIComponent(data.nickname)}&background=ffd700&color=fff&size=40'">
                    <div class="info">
                        <div class="name">${data.nickname}</div>
                        <div class="gift-details">
                            <span class="gift-name">🎁 ${data.gift}</span>
                            <span class="gift-count">×${data.count}</span>
                            <span class="gift-diamonds">💎 ${data.diamonds}</span>
                        </div>
                    </div>
                </div>
            `);
            document.getElementById('gBadge').textContent = stats.gifts;
            addActivity('gift', data.nickname, `🎁 ${data.gift} ×${data.count}`);
        });

        socket.on('follow', (data) => {
            stats.follows++;
            updateStats();
            addActivity('follow', data.nickname, 'متابعة جديدة');
        });

        socket.on('share', (data) => {
            stats.shares++;
            updateStats();
            addActivity('share', data.nickname, 'شارك البث');
        });

        function updateStats() {
            document.getElementById('sComments').textContent = stats.comments;
            document.getElementById('sGifts').textContent = stats.gifts;
            document.getElementById('sFollows').textContent = stats.follows;
            document.getElementById('sShares').textContent = stats.shares;
        }

        function addActivity(type, name, action) {
            const div = document.getElementById('activity');
            if (div.querySelector('.empty-state')) div.innerHTML = '';
            const icons = { comment:'comment', gift:'gift', follow:'follow', share:'share' };
            div.insertAdjacentHTML('afterbegin', `
                <div class="activity-item">
                    <div class="icon ${type}"><i class="fas fa-${icons[type]}"></i></div>
                    <div class="info"><strong>${name}</strong> ${action}</div>
                    <span class="time">الآن</span>
                </div>
            `);
        }

        // Limit items
        setInterval(() => {
            ['comments','gifts','activity'].forEach(id => {
                const el = document.getElementById(id);
                const items = el.querySelectorAll('.comment-item, .gift-item, .activity-item');
                if (items.length > 100) {
                    items.forEach((item, i) => { if (i >= 100) item.remove(); });
                }
            });
        }, 10000);
    </script>

</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML)

@socketio.on('connect')
def handle_connect():
    print('✅ واجهة متصلة')
    socketio.emit('system', {'msg': '🟢 متصل بالخادم'})

@client.on(ConnectEvent)
async def on_connect(event):
    print(f"✅ متصل ببث {event.unique_id}")
    socketio.emit('system', {'msg': f'🟢 متصل ببث {event.unique_id}'})

@client.on(CommentEvent)
async def on_comment(event):
    data = {
        'nickname': event.user.nickname,
        'text': event.comment,
        'avatar': event.user.avatar_thumb
    }
    socketio.emit('comment', data)
    print(f"💬 {event.user.nickname}: {event.comment}")

@client.on(GiftEvent)
async def on_gift(event):
    data = {
        'nickname': event.user.nickname,
        'gift': event.gift.name,
        'count': event.count,
        'diamonds': event.gift.diamond_count,
        'avatar': event.user.avatar_thumb
    }
    socketio.emit('gift', data)
    print(f"🎁 {event.user.nickname} → {event.gift.name} ×{event.count}")

@client.on(FollowEvent)
async def on_follow(event):
    data = {
        'nickname': event.user.nickname,
        'avatar': event.user.avatar_thumb
    }
    socketio.emit('follow', data)
    print(f"➕ متابعة: {event.user.nickname}")

@client.on(ShareEvent)
async def on_share(event):
    data = {
        'nickname': event.user.nickname,
        'avatar': event.user.avatar_thumb
    }
    socketio.emit('share', data)
    print(f"🔗 مشاركة: {event.user.nickname}")

def run_tiktok():
    while True:
        try:
            client.run()
        except UserOfflineError:
            print("⏳ البث غير متصل... سأحاول مرة أخرى بعد 30 ثانية")
            time.sleep(30)
        except Exception as e:
            print(f"❌ خطأ: {e}")
            time.sleep(10)

if __name__ == '__main__':
    threading.Thread(target=run_tiktok, daemon=True).start()
    socketio.run(app, host='0.0.0.0', port=5001, debug=False)
