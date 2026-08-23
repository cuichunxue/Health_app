Today One Sound Pack v1

01_done_soft.wav      「できた」直後。最重要。
02_discovery.wav      今日の発見・新しい傾向。
03_card_unlock.wav    わたしカード解放。
04_garden_growth.wav  庭が成長段階を上がった時。
05_adapt_change.wav   「今日は難しい」→代替案への切替。
06_welcome_back.wav   数日空いて再開できた時。

推奨設計
・最初は 01 / 02 / 05 の3音だけでも十分。
・BGMは使わない。
・「今日は難しい」に失敗音やブザーを使わない。
・カード解放をガチャ風の音にしない。
・音量は控えめ。音ON/OFFを用意する。
・音は報酬そのものではなく Immediate Feedback の補強に使う。

Web例
const sound = new Audio('./sounds/01_done_soft.wav');
sound.volume = 0.35;
sound.play().catch(()=>{});
