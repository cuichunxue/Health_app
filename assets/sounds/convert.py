# TodayOne SoundPack v1 を、単一HTMLに埋め込める形へ変換する。
#  - 44100Hz -> 16000Hz（実測で全パワーの99.99%が5kHz未満のため、8kHzナイキストで
#    可聴帯域は完全に保持される。resample_poly で適切に帯域制限してから間引く）
#  - 末尾の無音を除去（合計441ms）
#  - 16bit PCM モノラルのまま（音量が控えめでrms約10%のため、8bit化すると
#    量子化ノイズが可聴になる。ビット深度は落とさない）
import wave, os, base64, json, io
import numpy as np
from scipy.signal import resample_poly

SRC = os.path.dirname(__file__)                                    # このディレクトリの元WAV
OUT = os.path.join(os.path.dirname(__file__), 'sounds-embed.json')  # index.html に貼る base64
TARGET_SR = 16000

KEYS = {
    '01_done_soft.wav':     'done',
    '02_discovery.wav':     'discovery',
    '03_card_unlock.wav':   'card',
    '04_garden_growth.wav': 'garden',
    '05_adapt_change.wav':  'adapt',
    '06_welcome_back.wav':  'back',
}

def wav_bytes(samples_i16, sr):
    buf = io.BytesIO()
    w = wave.open(buf, 'wb')
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr)
    w.writeframes(samples_i16.tobytes())
    w.close()
    return buf.getvalue()

out = {}
raw_total = enc_total = 0
for fname, key in KEYS.items():
    path = os.path.join(SRC, fname)
    w = wave.open(path); n = w.getnframes(); sr = w.getframerate()
    a = np.frombuffer(w.readframes(n), dtype=np.int16).astype(np.float64); w.close()
    raw_total += n * 2

    # 末尾の無音を除去（ピークの0.1%を下回る区間）。頭は無音ゼロなので触らない。
    thr = np.abs(a).max() * 0.001
    nz = np.where(np.abs(a) > thr)[0]
    a = a[: nz[-1] + 1]
    # 切り口のプチノイズを避けるため、末尾5msだけフェードアウト
    fade = min(int(0.005 * sr), len(a))
    a[-fade:] *= np.linspace(1, 0, fade)

    # 44100 -> 16000 （160/441）。resample_poly が帯域制限も行う。
    r = resample_poly(a, 160, 441)
    peak = np.abs(r).max()
    if peak > 32767:                    # リサンプルのリンギングでの飽和を防ぐ
        r = r * (32767 / peak)
    r = np.clip(np.round(r), -32768, 32767).astype(np.int16)

    data = wav_bytes(r, TARGET_SR)
    enc_total += len(data)
    b64 = base64.b64encode(data).decode('ascii')
    out[key] = b64
    print(f'{fname:22s} -> {key:9s} {n/sr:.2f}s->{len(r)/TARGET_SR:.2f}s  '
          f'{n*2/1024:.0f}KB->{len(data)/1024:.0f}KB  base64 {len(b64)/1024:.0f}KB')

with open(OUT, 'w') as f:
    json.dump(out, f)
b64_total = sum(len(v) for v in out.values())
print(f'\n生WAV合計 {raw_total/1024:.0f}KB -> 変換後 {enc_total/1024:.0f}KB '
      f'-> base64 {b64_total/1024:.0f}KB')
