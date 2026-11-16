"""숨김(최소화) 창에서 유튜브 댓글창이 뜨는지 시험. 사용: python test_hidden.py"""
import json, subprocess, time

import os
D = os.path.dirname(os.path.abspath(__file__))


def x(c):
    o = subprocess.run(['python', '-X', 'utf8', 'x.py', json.dumps(c, ensure_ascii=True)],
                       capture_output=True, text=True, cwd=D).stdout.strip()
    try:
        return json.loads(o)
    except Exception:
        return {'raw': o}


o = x({"op": "open", "url": "https://example.com", "minimized": True, "timeout": 40})
print('open', o)
tab, win = o['tab'], o['win']
x({"op": "chrome", "api": "windows.update", "args": [win, {"state": "minimized"}]})
print(x({"op": "nav", "tab": tab, "url": "https://www.youtube.com/watch?v=Nvmdf4traUc", "timeout": 40}))
time.sleep(8)
js = ("(async()=>{const s=ms=>new Promise(r=>setTimeout(r,ms));"
      "const c=document.querySelector('ytd-comments'); if(c) c.scrollIntoView({block:'start'});"
      "await s(4000);"
      "return 'vis:'+document.visibilityState+' hidden:'+document.hidden+"
      "' ph:'+!!document.querySelector('#placeholder-area')+"
      "' threads:'+document.querySelectorAll('ytd-comment-thread-renderer').length+"
      "' avatar:'+!!document.querySelector('#avatar-btn')})()")
print(x({"op": "eval", "tab": tab, "code": js}))
x({"op": "close", "tab": tab})
