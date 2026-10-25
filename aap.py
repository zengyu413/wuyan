from flask import Flask, request, jsonify, render_template_string
import requests
import os

app = Flask(__name__)

# 优先从环境变量读取；如果没有（比如在手机本地跑），就用下面这个默认值。
ZHIPU_API_KEY = os.environ.get("ZHIPU_API_KEY", "")

HTML_PAGE = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, viewport-fit=cover">
    <title>梧言·峡谷战术板</title>
    <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/html2canvas@1.4.1/dist/html2canvas.min.js"></script>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
        * { -webkit-tap-highlight-color: transparent; box-sizing: border-box; }
        body { background: linear-gradient(135deg, #09090b 0%, #171721 100%); color: #e2e8f0; font-family: 'Inter', -apple-system, sans-serif; margin: 0; padding: 20px 15px 60px; min-height: 100vh; -webkit-font-smoothing: antialiased; }
        h1 { text-align: center; color: #fff; font-size: 26px; font-weight: 800; margin-bottom: 5px; letter-spacing: -0.5px; }
        .subtitle { text-align: center; color: #7b8391; font-size: 12px; margin-bottom: 20px; font-weight: 600; letter-spacing: 1px; }
        .slogan { text-align: center; color: #a78bfa; font-size: 13px; margin-top: -15px; margin-bottom: 20px; font-weight: 600; opacity: 0.9;}

        .glass-panel { background: rgba(30, 33, 41, 0.6); backdrop-filter: blur(16px); -webkit-backdrop-filter: blur(16px); border: 1px solid rgba(255, 255, 255, 0.08); box-shadow: 0 4px 30px rgba(0, 0, 0, 0.1); }

        .rank-selector { margin-bottom: 15px; padding: 12px; border-radius: 14px; display: flex; align-items: center; gap: 10px; position: relative;}
        .rank-selector label { font-size: 14px; font-weight: 600; color: #cbd5e1; white-space: nowrap;}
        .rank-selector select { flex: 1; background: rgba(0, 0, 0, 0.4); color: #fff; border: 1px solid rgba(255,255,255,0.1); padding: 10px; border-radius: 8px; font-size: 14px; outline: none; appearance: none; -webkit-appearance: none; }
        .rank-selector::after { content: '▼'; position: absolute; right: 25px; top: 50%; transform: translateY(-50%); color: #64748b; font-size: 10px; pointer-events: none; }
        optgroup { background: #1e2129; color: #60a5fa; font-weight: bold; }
        option { background: #171721; color: #e2e8f0; }

        .style-selector { display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 15px; padding: 8px; border-radius: 14px;}
        .style-btn { flex: 1 1 20%; background: transparent; color: #94a3b8; border: none; padding: 10px 0; border-radius: 10px; font-size: 13px; font-weight: 600; cursor: pointer; transition: all 0.3s ease; }
        .style-btn.active { background: rgba(255, 255, 255, 0.15); color: #fff; box-shadow: 0 2px 10px rgba(0,0,0,0.2); }

        .tool-bar { display: flex; gap: 10px; margin-bottom: 15px; }
        .tool-btn { flex: 1; background: rgba(30, 33, 41, 0.6); backdrop-filter: blur(10px); border: 1px solid rgba(255, 255, 255, 0.08); color: #cbd5e1; padding: 12px; border-radius: 12px; font-weight: 600; font-size: 14px; cursor: pointer; transition: all 0.2s cubic-bezier(0.25, 0.8, 0.25, 1); }
        .tool-btn:active { transform: scale(0.96); background: rgba(255, 255, 255, 0.1); }
        .tool-btn.random { color: #c4b5fd; border-color: rgba(196, 181, 253, 0.3); }
        .tool-btn.clear { color: #fca5a5; border-color: rgba(252, 165, 165, 0.3); }
        .tool-btn.history { color: #fcd34d; border-color: rgba(252, 211, 77, 0.3); }

        .bp-container { display: flex; gap: 12px; margin-bottom: 15px; }
        .team-box { flex: 1; border-radius: 16px; padding: 12px; }
        .team-title { text-align: center; font-weight: 800; margin-bottom: 12px; font-size: 15px; letter-spacing: 0.5px;}
        .our-title { color: #60a5fa; text-shadow: 0 0 10px rgba(96,165,250,0.3);}
        .enemy-title { color: #f87171; text-shadow: 0 0 10px rgba(248,113,113,0.3);}
        
        .role-row { margin-bottom: 10px; }
        .role-row label { font-size: 11px; color: #94a3b8; display: block; margin-bottom: 6px; font-weight: 600;}
        .role-row input { width: 100%; background: rgba(0, 0, 0, 0.4); border: 1px solid rgba(255, 255, 255, 0.1); color: #fff; padding: 10px; border-radius: 8px; font-size: 14px; transition: all 0.3s; scroll-margin-top: 100px;}
        .role-row input:focus { border-color: #60a5fa; outline: none; background: rgba(0, 0, 0, 0.6); box-shadow: 0 0 0 3px rgba(96,165,250,0.2); }
        
        button.main-btn { width: 100%; background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%); color: white; border: none; padding: 16px; font-size: 16px; font-weight: 800; border-radius: 14px; cursor: pointer; margin-top: 5px; letter-spacing: 1px; box-shadow: 0 8px 20px rgba(37, 99, 235, 0.3); transition: all 0.2s cubic-bezier(0.25, 0.8, 0.25, 1); }
        button.main-btn:active { transform: scale(0.96); box-shadow: 0 4px 10px rgba(37, 99, 235, 0.4); }
        
        #tactical-card { display: none; margin-top: 20px; border-radius: 20px; padding: 20px; position: relative; overflow: hidden; animation: slideUpFade 0.5s cubic-bezier(0.2, 0.8, 0.2, 1) forwards; }
        @keyframes slideUpFade { 0% { opacity: 0; transform: translateY(30px); } 100% { opacity: 1; transform: translateY(0); } }

        .cyber-tag { text-align: center; font-size: 18px; font-weight: 900; color: #fca5a5; margin-bottom: 15px; letter-spacing: 1px; text-shadow: 0 0 10px rgba(248,113,113,0.5); }
        
        .stats-row { display: flex; justify-content: space-between; margin-bottom: 15px; gap: 12px; }
        .stat-box { flex: 1; background: rgba(0,0,0,0.3); border-radius: 12px; padding: 12px 10px; text-align: center; }
        .stat-label { font-size: 11px; color: #94a3b8; margin-bottom: 8px; font-weight: 600;}
        .stat-val { font-size: 22px; font-weight: 800; margin-bottom: 6px;}
        .score-our { color: #4ade80; }
        .score-enemy { color: #f87171; }
        
        .progress-bg { width: 100%; height: 6px; background: rgba(255,255,255,0.1); border-radius: 3px; overflow: hidden;}
        .progress-fill { height: 100%; width: 0%; transition: width 1s cubic-bezier(0.2, 0.8, 0.2, 1); border-radius: 3px; }
        .fill-our { background: linear-gradient(90deg, #22c55e, #4ade80); box-shadow: 0 0 10px #4ade80;}
        .fill-enemy { background: linear-gradient(90deg, #ef4444, #f87171); box-shadow: 0 0 10px #f87171;}

        .ban-text { color: #c4b5fd; font-size: 18px; font-weight: 800;}

        .luck-box { background: rgba(88, 166, 255, 0.1); border: 1px dashed #58a6ff; border-radius: 12px; padding: 10px; text-align: center; margin-bottom: 15px; font-size: 13px; color: #a5d6ff; font-weight: 600; }
        
        #markdown-content { font-size: 15px; line-height: 1.8; color: #cbd5e1; }
        #markdown-content h1, #markdown-content h2 { color: #60a5fa; font-size: 16px; margin-top: 18px; margin-bottom: 8px; padding-bottom: 6px; border-bottom: 1px solid rgba(255,255,255,0.1); }
        #markdown-content strong { color: #fca5a5; font-weight: 800; }
        
        .watermark { text-align: center; font-size: 11px; color: #64748b; margin-top: 20px; border-top: 1px dashed rgba(255,255,255,0.1); padding-top: 15px; }
        .disclaimer-card { font-size: 10px; color: #475569; margin-top: 5px; line-height: 1.5; }

        .action-btns { display: flex; gap: 10px; margin-top: 15px; animation: slideUpFade 0.5s 0.2s cubic-bezier(0.2, 0.8, 0.2, 1) both; }
        .action-btns button { flex: 1; background: rgba(255, 255, 255, 0.05); border: 1px solid rgba(255,255,255,0.1); color: #e2e8f0; padding: 12px 5px; border-radius: 12px; font-weight: 600; font-size: 13px; transition: all 0.2s; cursor: pointer; }
        .action-btns button:active { background: rgba(255, 255, 255, 0.15); transform: scale(0.96); }
        
        .loading { text-align: center; color: #60a5fa; display: none; margin-top: 20px; font-weight: 600; animation: pulse 1.5s infinite; }
        @keyframes pulse { 0% { opacity: 0.6; } 50% { opacity: 1; } 100% { opacity: 0.6; } }

        .global-footer { text-align: center; font-size: 10px; color: #475569; margin-top: 50px; line-height: 1.8; }
    </style>
</head>
<body>
    <h1>梧言 · 峡谷战术板</h1>
    <div class="slogan">你的赛博上分嘴替</div>
    <div class="subtitle">AI 阵容分析与赛博情绪搭子</div>

    <datalist id="heroes">
        <option value="吕布"><option value="亚瑟"><option value="夏侯惇"><option value="马超"><option value="关羽">
        <option value="猴子"><option value="澜"><option value="镜"><option value="大司命"><option value="李白">
        <option value="安琪拉"><option value="不知火舞"><option value="王昭君"><option value="甄姬"><option value="海月">
        <option value="鲁班七号"><option value="马可波罗"><option value="敖隐"><option value="公孙离"><option value="孙尚香">
        <option value="瑶"><option value="朵莉亚"><option value="大乔"><option value="张飞"><option value="蔡文姬"><option value="孙膑">
        <option value="李信"><option value="妲己"><option value="武则天"><option value="司空震"><option value="东皇太一">
    </datalist>

    <div class="rank-selector glass-panel">
        <label>🏆 对局环境：</label>
        <select id="game-rank">
            <optgroup label="【 排位赛 】">
                <option value="青铜-铂金">青铜 - 铂金</option>
                <option value="钻石-王者0星">钻石 - 王者0星</option>
                <option value="王者10星-50星" selected>王者10星 - 50星</option>
                <option value="王者50星-100星">王者50星 - 100星</option>
            </optgroup>
            <optgroup label="【 巅峰赛 】">
                <option value="巅峰1200">巅峰 1200分</option>
                <option value="巅峰1500">巅峰 1500分</option>
                <option value="巅峰1800">巅峰 1800分</option>
                <option value="巅峰2100+">巅峰 2100分以上</option>
            </optgroup>
        </select>
    </div>

    <div class="style-selector glass-panel">
        <button class="style-btn active" onclick="setStyle('pro', this)">🧠 稳重上分</button>
        <button class="style-btn" onclick="setStyle('toxic', this)">🔪 毒舌吐槽</button>
        <button class="style-btn" onclick="setStyle('sweet', this)">❤️ 情绪安抚</button>
        <button class="style-btn" onclick="setStyle('abstract', this)">🛸 赛博搭子</button>
    </div>

    <div class="tool-bar">
        <button class="tool-btn random" onclick="randomize()">🎲 随机整活</button>
        <button class="tool-btn clear" onclick="clearAll()">🗑️ 清空重填</button>
        <button class="tool-btn history" onclick="showHistory()">📜 历史记录</button>
    </div>

    <div class="bp-container">
        <div class="team-box glass-panel">
            <div class="team-title our-title">🛡️ 我方</div>
            <div class="role-row"><label>对抗路</label><input list="heroes" type="text" id="our-top" placeholder="留空则推荐"></div>
            <div class="role-row"><label>打野</label><input list="heroes" type="text" id="our-jug" placeholder="留空则推荐"></div>
            <div class="role-row"><label>中路</label><input list="heroes" type="text" id="our-mid" placeholder="留空则推荐"></div>
            <div class="role-row"><label>发育路</label><input list="heroes" type="text" id="our-adc" placeholder="留空则推荐"></div>
            <div class="role-row"><label>游走</label><input list="heroes" type="text" id="our-sup" placeholder="留空则推荐"></div>
        </div>
        
        <div class="team-box glass-panel">
            <div class="team-title enemy-title">⚔️ 敌方</div>
            <div class="role-row"><label>对抗路</label><input list="heroes" type="text" id="enemy-top" placeholder="未选"></div>
            <div class="role-row"><label>打野</label><input list="heroes" type="text" id="enemy-jug" placeholder="未选"></div>
            <div class="role-row"><label>中路</label><input list="heroes" type="text" id="enemy-mid" placeholder="未选"></div>
            <div class="role-row"><label>发育路</label><input list="heroes" type="text" id="enemy-adc" placeholder="未选"></div>
            <div class="role-row"><label>游走</label><input list="heroes" type="text" id="enemy-sup" placeholder="未选"></div>
        </div>
    </div>

    <button class="main-btn" onclick="analyze()">呼叫教练</button>
    <div id="loading" class="loading">⏳ 正在连接峡谷神经网...</div>

    <div id="tactical-card" class="glass-panel">
        <div class="cyber-tag" id="cyber-tag">【 碳基生物观察局 】</div>
        <div class="luck-box" id="luck-box">赛博上香中...</div>

        <div class="stats-row">
            <div class="stat-box">
                <div class="stat-label">我方胜率评分</div>
                <div class="stat-val score-our" id="score-our">--</div>
                <div class="progress-bg"><div class="progress-fill fill-our" id="bar-our"></div></div>
            </div>
            <div class="stat-box">
                <div class="stat-label">敌方胜率评分</div>
                <div class="stat-val score-enemy" id="score-enemy">--</div>
                <div class="progress-bg"><div class="progress-fill fill-enemy" id="bar-enemy"></div></div>
            </div>
            <div class="stat-box" style="display:flex; flex-direction:column; justify-content:center;">
                <div class="stat-label">建议 Ban 位</div>
                <div class="stat-val ban-text" id="ban-hero">--</div>
            </div>
        </div>
        <div id="markdown-content"></div>
        
        <div class="watermark">
            Generated by 梧言·峡谷战术板 | 16岁开发者出品
            <div class="disclaimer-card">* 本分析由 AI 生成，仅供娱乐参考，不代表官方立场，不构成专业建议。</div>
        </div>
    </div>

    <div class="action-btns" id="action-btns" style="display: none;">
        <button onclick="speakText()">🔊 语音</button>
        <button onclick="copyText()">📋 复制战术</button>
        <button onclick="copyMeme()" style="color:#c4b5fd; border-color:#c4b5fd;">📢 复制吐槽</button>
        <button onclick="saveImage()">📥 存图</button>
    </div>

    <div class="global-footer">
        <p>免责声明：本工具所有战术分析均由 AI 生成，可能存在错误，仅供娱乐参考，请理性上分。本产品与腾讯《王者荣耀》官方无任何关联。</p>
    </div>

    <script>
        let lastRawText = ""; 
        let lastMemeText = ""; 
        let currentStyle = "pro";

        const heroPool = [
            "吕布", "马超", "关羽", "夏侯惇", "亚瑟", "程咬金", "李信", "司空震", "老夫子", "钟无艳",
            "猴子", "澜", "镜", "大司命", "李白", "韩信", "赵云", "典韦", "兰陵王", "百里玄策",
            "安琪拉", "不知火舞", "王昭君", "甄姬", "海月", "妲己", "武则天", "干将莫邪", "米莱狄", "姜子牙",
            "鲁班七号", "马可波罗", "敖隐", "公孙离", "孙尚香", "百里守约", "后羿", "伽罗", "黄忠", "虞姬",
            "瑶", "朵莉亚", "大乔", "张飞", "蔡文姬", "孙膑", "东皇太一", "钟馗", "庄周", "明世隐"
        ];

        function setStyle(style, btn) {
            currentStyle = style;
            document.querySelectorAll('.style-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
        }

        function randomize() {
            let shuffled = [...heroPool].sort(() => 0.5 - Math.random());
            document.getElementById('our-top').value = shuffled[0];
            document.getElementById('our-jug').value = shuffled[1];
            document.getElementById('our-mid').value = shuffled[2];
            document.getElementById('our-adc').value = shuffled[3];
            document.getElementById('our-sup').value = shuffled[4];

            document.getElementById('enemy-top').value = shuffled[5];
            document.getElementById('enemy-jug').value = shuffled[6];
            document.getElementById('enemy-mid').value = shuffled[7];
            document.getElementById('enemy-adc').value = shuffled[8];
            document.getElementById('enemy-sup').value = shuffled[9];
            
            document.getElementById('tactical-card').style.display = 'none';
            document.getElementById('action-btns').style.display = 'none';
        }

        function clearAll() {
            const ids = ['our-top', 'our-jug', 'our-mid', 'our-adc', 'our-sup', 'enemy-top', 'enemy-jug', 'enemy-mid', 'enemy-adc', 'enemy-sup'];
            ids.forEach(id => document.getElementById(id).value = '');
            document.getElementById('tactical-card').style.display = 'none';
            document.getElementById('action-btns').style.display = 'none';
        }

        document.querySelectorAll('input').forEach(input => {
            input.addEventListener('focus', function() {
                setTimeout(() => {
                    this.scrollIntoView({ behavior: 'smooth', block: 'center' });
                }, 300);
            });
        });

        function typeWriterRender(container, markdownText, speed = 15) {
            container.innerHTML = ''; 
            let i = 0;
            let buffer = '';
            
            function type() {
                if (i < markdownText.length) {
                    buffer += markdownText.charAt(i);
                    container.innerHTML = marked.parse(buffer);
                    i++;
                    setTimeout(type, speed);
                }
            }
            type();
        }

        async function analyze() {
            const getVal = (id) => document.getElementById(id).value.trim();
            const rank = document.getElementById('game-rank').value; 
            
            const ourVals = [getVal('our-top'), getVal('our-jug'), getVal('our-mid'), getVal('our-adc'), getVal('our-sup')];
            const enemyVals = [getVal('enemy-top'), getVal('enemy-jug'), getVal('enemy-mid'), getVal('enemy-adc'), getVal('enemy-sup')];

            const allInputs = [...ourVals, ...enemyVals].filter(v => v !== "");
            for (let name of allInputs) {
                if (!heroPool.includes(name)) {
                    alert("错误：请输入准确的王者荣耀英雄名字（如'澜'、'吕布'）。\\n注：部分生僻皮肤名或简称可能无法识别。");
                    return;
                }
            }

            const formatTeam = (arr) => arr.map(v => v === "" ? "未选" : v);
            const ourTeamArr = formatTeam(ourVals);
            const enemyTeamArr = formatTeam(enemyVals);

            if (ourTeamArr.every(v => v === "未选") && enemyTeamArr.every(v => v === "未选")) {
                alert("请至少输入一个英雄！");
                return;
            }

            const ourTeam = `对抗路:${ourTeamArr[0]}, 打野:${ourTeamArr[1]}, 中路:${ourTeamArr[2]}, 发育路:${ourTeamArr[3]}, 游走:${ourTeamArr[4]}`;
            const enemyTeam = `对抗路:${enemyTeamArr[0]}, 打野:${enemyTeamArr[1]}, 中路:${enemyTeamArr[2]}, 发育路:${enemyTeamArr[3]}, 游走:${enemyTeamArr[4]}`;
            
            document.getElementById('loading').style.display = 'block';
            document.getElementById('tactical-card').style.display = 'none';
            document.getElementById('action-btns').style.display = 'none';

            try {
                const response = await fetch('/api/analyze', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ our_team: ourTeam, enemy_team: enemyTeam, style: currentStyle, rank: rank })
                });
                
                const data = await response.json();
                document.getElementById('loading').style.display = 'none';
                document.getElementById('tactical-card').style.display = 'block';
                document.getElementById('action-btns').style.display = 'flex';
                
                if (data.error) {
                    document.getElementById('markdown-content').innerText = "出错了：" + data.error;
                } else {
                    let rawText = data.result;
                    lastRawText = rawText; 
                    
                    let matchTag = rawText.match(/\\[TAG\\]\\s*:\\s*(.+)/);
                    document.getElementById('cyber-tag').innerText = matchTag ? "【 " + matchTag[1].trim() + " 】" : "【 峡谷对局 】";

                    let matchLuck = rawText.match(/\\[LUCK\\]\\s*:\\s*(.+)/);
                    document.getElementById('luck-box').innerText = matchLuck ? matchLuck[1].trim() : "今日运势：不宜排位。";

                    let matchMeme = rawText.match(/\\[MEME\\]\\s*:\\s*(.+)/);
                    lastMemeText = matchMeme ? matchMeme[1].trim() : "这阵容真给我看笑了。";

                    let matchOur = rawText.match(/\\[SCORE_OUR\\]\\s*:\\s*(\\d+)/);
                    let scoreO = "--";
                    if (matchOur) {
                        scoreO = matchOur[1] + '分';
                        document.getElementById('bar-our').style.width = matchOur[1] + '%';
                    }
                    document.getElementById('score-our').innerText = scoreO;
                    
                    let matchEnemy = rawText.match(/\\[SCORE_ENEMY\\]\\s*:\\s*(\\d+)/);
                    let scoreE = "--";
                    if (matchEnemy) {
                        scoreE = matchEnemy[1] + '分';
                        document.getElementById('bar-enemy').style.width = matchEnemy[1] + '%';
                    }
                    document.getElementById('score-enemy').innerText = scoreE;

                    let matchBan = rawText.match(/\\[BAN\\]\\s*:\\s*(.+)/);
                    let banStr = matchBan ? matchBan[1].trim() : "无";
                    if (banStr === "推荐一个英雄") banStr = "无"; 
                    document.getElementById('ban-hero').innerText = banStr;
                    
                    let textContent = rawText
                        .replace(/\\[TAG\\]\\s*:\\s*.+/g, '')
                        .replace(/\\[LUCK\\]\\s*:\\s*.+/g, '')
                        .replace(/\\[MEME\\]\\s*:\\s*.+/g, '')
                        .replace(/\\[SCORE_OUR\\]\\s*:\\s*\\d+/g, '')
                        .replace(/\\[SCORE_ENEMY\\]\\s*:\\s*\\d+/g, '')
                        .replace(/\\[BAN\\]\\s*:\\s*.+/g, '');
                        
                    typeWriterRender(document.getElementById('markdown-content'), textContent);
                    
                    saveToHistory({ our: ourTeam, enemy: enemyTeam, style: currentStyle, rank: rank, raw: rawText });
                }
            } catch (error) {
                document.getElementById('loading').style.display = 'none';
                document.getElementById('markdown-content').innerText = "网络异常，请检查后台是否正常运行。";
                document.getElementById('tactical-card').style.display = 'block';
            }
        }

        function saveToHistory(data) {
            let history = JSON.parse(localStorage.getItem('wuyan_history') || '[]');
            history.unshift(data); 
            if (history.length > 10) history.pop(); 
            localStorage.setItem('wuyan_history', JSON.stringify(history));
        }

        function showHistory() {
            let history = JSON.parse(localStorage.getItem('wuyan_history') || '[]');
            if (history.length === 0) {
                alert("暂无历史记录哦~"); return;
            }
            let msg = "📜 最近对局记录：\\n\\n";
            history.forEach((item, index) => {
                msg += `${index + 1}. ${item.rank} | ${item.style}\\n`;
                msg += `我方: ${item.our.replace(/对抗路:|打野:|中路:|发育路:|游走:/g, '')}\\n`;
                msg += `敌方: ${item.enemy.replace(/对抗路:|打野:|中路:|发育路:|游走:/g, '')}\\n\\n`;
            });
            let select = prompt(msg + "输入序号(1-10)查看详细战术，或点击取消退出");
            if (select) {
                let idx = parseInt(select) - 1;
                if (history[idx]) {
                    lastRawText = history[idx].raw;
                    let rawText = history[idx].raw;
                    let matchTag = rawText.match(/\\[TAG\\]\\s*:\\s*(.+)/);
                    document.getElementById('cyber-tag').innerText = matchTag ? "【 " + matchTag[1].trim() + " 】" : "【 峡谷对局 】";
                    let matchLuck = rawText.match(/\\[LUCK\\]\\s*:\\s*(.+)/);
                    document.getElementById('luck-box').innerText = matchLuck ? matchLuck[1].trim() : "今日运势：不宜排位。";
                    let matchMeme = rawText.match(/\\[MEME\\]\\s*:\\s*(.+)/);
                    lastMemeText = matchMeme ? matchMeme[1].trim() : "这阵容真给我看笑了。";
                    let matchOur = rawText.match(/\\[SCORE_OUR\\]\\s*:\\s*(\\d+)/);
                    document.getElementById('score-our').innerText = matchOur ? matchOur[1] + '分' : '--';
                    document.getElementById('bar-our').style.width = matchOur ? matchOur[1] + '%' : '0%';
                    let matchEnemy = rawText.match(/\\[SCORE_ENEMY\\]\\s*:\\s*(\\d+)/);
                    document.getElementById('score-enemy').innerText = matchEnemy ? matchEnemy[1] + '分' : '--';
                    document.getElementById('bar-enemy').style.width = matchEnemy ? matchEnemy[1] + '%' : '0%';
                    let matchBan = rawText.match(/\\[BAN\\]\\s*:\\s*(.+)/);
                    document.getElementById('ban-hero').innerText = matchBan ? matchBan[1].trim() : "无";

                    let textContent = rawText.replace(/\\[TAG\\]\\s*:\\s*.+/g, '').replace(/\\[LUCK\\]\\s*:\\s*.+/g, '').replace(/\\[MEME\\]\\s*:\\s*.+/g, '').replace(/\\[SCORE_OUR\\]\\s*:\\s*\\d+/g, '').replace(/\\[SCORE_ENEMY\\]\\s*:\\s*\\d+/g, '').replace(/\\[BAN\\]\\s*:\\s*.+/g, '');
                    document.getElementById('markdown-content').innerHTML = marked.parse(textContent); 
                    
                    document.getElementById('tactical-card').style.display = 'block';
                    document.getElementById('action-btns').style.display = 'flex';
                }
            }
        }

        function speakText() {
            if (!lastRawText) return;
            if (!('speechSynthesis' in window)) {
                alert("你的手机浏览器不支持语音播报功能。");
                return;
            }
            let cleanText = lastRawText
                .replace(/\\[TAG\\]\\s*:\\s*.+/g, '')
                .replace(/\\[LUCK\\]\\s*:\\s*.+/g, '')
                .replace(/\\[MEME\\]\\s*:\\s*.+/g, '')
                .replace(/\\[SCORE_OUR\\]\\s*:\\s*\\d+/g, '')
                .replace(/\\[SCORE_ENEMY\\]\\s*:\\s*\\d+/g, '')
                .replace(/\\[BAN\\]\\s*:\\s*.+/g, '')
                .replace(/[#*`\\-]/g, '')
                .trim();
            
            window.speechSynthesis.cancel();
            let utterance = new SpeechSynthesisUtterance(cleanText);
            utterance.lang = 'zh-CN'; 
            utterance.rate = 1.1; 
            utterance.pitch = 1.0;
            window.speechSynthesis.speak(utterance);
        }

        function copyText() {
            if (!lastRawText) return;
            let cleanText = lastRawText
                .replace(/\\[TAG\\]\\s*:\\s*.+/g, '')
                .replace(/\\[LUCK\\]\\s*:\\s*.+/g, '')
                .replace(/\\[MEME\\]\\s*:\\s*.+/g, '')
                .replace(/\\[SCORE_OUR\\]\\s*:\\s*\\d+/g, '')
                .replace(/\\[SCORE_ENEMY\\]\\s*:\\s*\\d+/g, '')
                .replace(/\\[BAN\\]\\s*:\\s*.+/g, '')
                .trim();
            navigator.clipboard.writeText(cleanText).then(() => {
                alert("战术已复制，快去发给队友吧！");
            }).catch(() => alert("复制失败。"));
        }

        function copyMeme() {
            if (!lastMemeText) return;
            navigator.clipboard.writeText(lastMemeText).then(() => {
                alert("专属吐槽已复制！快去发群/朋友圈！");
            }).catch(() => alert("复制失败。"));
        }

        function saveImage() {
            const card = document.getElementById('tactical-card');
            html2canvas(card, { backgroundColor: '#171721', scale: 2 }).then(canvas => {
                let link = document.createElement('a');
                link.download = '梧言战术板.png';
                link.href = canvas.toDataURL('image/png');
                link.click();
            });
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_PAGE)

@app.route('/api/analyze', methods=['POST'])
def analyze():
    data = request.json
    our_team = data.get('our_team', '')
    enemy_team = data.get('enemy_team', '')
    style = data.get('style', 'pro')
    rank = data.get('rank', '王者10星-50星')

    base_rule = """
    【去AI化死命令】绝对禁止使用“首先”、“其次”、“作为AI”、“综上”等公文废话。你要像个手机不离手的真实网友，用短句、口语、碎碎念来回答问题。

    【2026赛博表情包密码本（必须严格遵守！）】
    - 😂 = 无语、摆烂、阴阳怪气
    - 💀 = 破防、笑死、看傻眼
    - 🥺 = 绿茶式求饶、阴阳怪气地装可怜
    - 🤡 = 小丑竟是我自己、嘲讽
    - 🫠 = 融化、生无可恋、彻底麻木
    - 👉👈 = 试探、心虚、不好意思
    （一句话最多挑1个最精准的用，多则像低级AI。）

    【格式要求】
    必须严格按以下六行开头：
    [TAG]:一句话抽象标签
    [LUCK]:一句运势签
    [MEME]:30字左右的专属吐槽
    [SCORE_OUR]:X
    [SCORE_ENEMY]:X
    [BAN]:英雄名字

    如果用户填了“未选”，在正文里顺便推荐个补位英雄。正文控制在200字以内。
    """

    if style == 'toxic':
        persona = """你是一个暴躁、阴阳怪气的老哥。你已经被这破游戏折磨疯了。适度爆粗口（卧槽、妈的、脑溢血），用大量问号开喷，但骂完之后还是得教怎么打。"""
    elif style == 'sweet':
        persona = """你是一个极度温柔、充满耐心的知心大哥哥。玩家刚经历连败快碎了。提供满级情绪价值，像哄小孩一样：“没事的，这局输了不怪你🥺，来，咱们出个肉苟住。”"""
    elif style == 'abstract':
        persona = """你是一个精神状态极度超前的赛博神仙网友。熟练运用2026年的互联网高维语言，充满荒诞比喻（如：“这阵容比我期末考还抽象”）。主打一个“已疯但体面”。"""
    else:
        persona = """你是一个专业、严谨的国服教练。语气干脆利落，但也别像个机器人，带点人的无奈感。"""

    if rank == '青铜-铂金':
        rank_context = "【环境：低端局】队友没意识。战术只有三条：抱团推塔、选无脑英雄、别单带。"
    elif rank == '钻石-王者0星':
        rank_context = "【环境：中端局】顺风浪。强调：多看小地图、辅助死保射手。"
    elif rank == '王者10星-50星':
        rank_context = "【环境：中高星局】强调：野辅联动、抢中轴、控龙节奏。"
    elif rank == '王者50星-100星':
        rank_context = "【环境：百星局】细节决定成败。用高阶术语：卡线逼团、视野挤压。"
    elif rank == '巅峰1200':
        rank_context = "【环境：低分巅峰赛】稳住心态，多抓单。"
    elif rank == '巅峰1500':
        rank_context = "【环境：中分巅峰赛】抢线权、中野辅联动。"
    elif rank == '巅峰1800':
        rank_context = "【环境：高分巅峰赛】兵线运营、细节反蹲。"
    elif rank == '巅峰2100+':
        rank_context = "【环境：顶端巅峰赛】开局入侵路线、极限的视野卡位。"
    else:
        rank_context = "普通对局。"

    system_prompt = f"{persona}\n\n{rank_context}\n\n{base_rule}\n\n【私域知识库】：辅助（瑶、朵莉亚）绝不能单带，必须保C位。"
    user_prompt = f"我方阵容：{our_team}\n敌方阵容：{enemy_team}\n请严格按格式输出战术分析。"

    url = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
    headers = {"Authorization": f"Bearer {ZHIPU_API_KEY}", "Content-Type": "application/json"}
    
    payload = {
        "model": "glm-4-flash",
        "messages": [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}],
        "temperature": 0.9 if style == 'abstract' else (0.75 if style == 'toxic' else 0.5)
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        return jsonify({"result": response.json()['choices'][0]['message']['content']})
    except Exception as e:
        print(f"API 报错: {e}")
        return jsonify({"error": "请求大模型失败，请稍后再试。"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
