
importScripts('token.js'); // make_token.py 가 만드는 파일(TOK)
const BASE='http://127.0.0.1:8765';
const att=new Set();
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
async function attach(tab){ if(att.has(tab)) return; try{ await chrome.debugger.attach({tabId:tab},'1.3'); }catch(e){ if(!String(e).includes('already')) throw e; } att.add(tab);
  try{ await chrome.debugger.sendCommand({tabId:tab},'Emulation.setFocusEmulationEnabled',{enabled:true}); }catch(e){}
  try{ await chrome.debugger.sendCommand({tabId:tab},'Page.setWebLifecycleState',{state:'active'}); }catch(e){} await forceVisible(tab);
  try{ await chrome.debugger.sendCommand({tabId:tab},'Emulation.setEmulatedVisionDeficiency',{type:'none'}); }catch(e){}
  await chrome.debugger.sendCommand({tabId:tab},'Page.enable'); await chrome.debugger.sendCommand({tabId:tab},'DOM.enable'); }

async function forceVisible(tab){ try{ await chrome.debugger.sendCommand({tabId:tab},'Page.addScriptToEvaluateOnNewDocument',{source:"Object.defineProperty(document,'hidden',{get:()=>false,configurable:true});Object.defineProperty(document,'visibilityState',{get:()=>'visible',configurable:true});document.hasFocus=()=>true;"}); await chrome.debugger.sendCommand({tabId:tab},'Runtime.evaluate',{expression:"Object.defineProperty(document,'hidden',{get:()=>false,configurable:true});Object.defineProperty(document,'visibilityState',{get:()=>'visible',configurable:true});document.hasFocus=()=>true;document.dispatchEvent(new Event('visibilitychange'));"}); }catch(e){} }
chrome.debugger.onDetach.addListener(s=>att.delete(s.tabId));
const send=(tab,m,p)=>chrome.debugger.sendCommand({tabId:tab},m,p||{});
async function waitLoad(tab){ for(let i=0;i<60;i++){ const t=await chrome.tabs.get(tab); if(t.status==='complete') return; await sleep(500);} }
async function run0(c){
  const tab=c.tab;
  switch(c.op){
    case 'front': { await attach(tab); await send(tab,'Page.bringToFront'); const t=await chrome.tabs.get(tab); await chrome.windows.update(t.windowId,{state:'normal',left:c.left??1930,top:c.top??0,width:c.width??1880,height:c.height??1000,focused:true,drawAttention:false}); await sleep(800); return {ok:1}; }
    case 'cdp': { await attach(tab); const r=await send(tab,c.method,c.params||{}); return {result:r}; }
    case 'chrome': { let o=chrome; const parts=c.api.split('.'); const fn=parts.pop(); for(const p of parts) o=o[p]; const r=await o[fn](...(c.args||[])); return {result:r===undefined?null:r}; }
    case 'frame_upload': { await attach(tab); const ft=(await send(tab,'Page.getFrameTree')).frameTree;
      const find=(n)=>{ if(n.frame.url.includes(c.urlpart)) return n.frame.id; for(const k of (n.childFrames||[])){ const r=find(k); if(r) return r;} return null; };
      const all=[]; const col=(n)=>{ if(n.frame.url.includes(c.urlpart)) all.push(n.frame.id); for(const k of (n.childFrames||[])) col(k); }; col(ft);
      const fid=all.length?all[all.length-1]:null; if(!fid) return {error:'frame not found'};
      const w=await send(tab,'Page.createIsolatedWorld',{frameId:fid,worldName:'fu'+Date.now()});
      const ob=await send(tab,'Runtime.evaluate',{expression:c.selector?("document.querySelector('"+c.selector+"')"):"document.querySelector('input[type=file]')",contextId:w.executionContextId});
      if(!ob.result||!ob.result.objectId) return {error:'input not found'};
      await send(tab,'DOM.setFileInputFiles',{files:c.files,objectId:ob.result.objectId}); await send(tab,'Runtime.callFunctionOn',{objectId:ob.result.objectId,functionDeclaration:"function(){this.dispatchEvent(new Event('input',{bubbles:true}));this.dispatchEvent(new Event('change',{bubbles:true}));return this.files.length}",returnByValue:true}); return {ok:1}; }
    case 'ping': return {ok:1,t:Date.now()};
    case 'tabs': return {tabs:(await chrome.tabs.query({})).map(t=>({id:t.id,win:t.windowId,url:t.url,title:t.title}))};
    case 'open': { const w=await chrome.windows.create({url:c.url,left:c.left??1930,top:c.top??0,width:c.width??1900,height:c.height??1040,focused:c.focused??false}); const id=w.tabs[0].id; if(c.minimized){ try{ await chrome.windows.update(w.id,{state:'minimized'}); }catch(e){} } await waitLoad(id); await sleep(1500); return {tab:id,win:w.id}; }
    case 'newtab': { const t=await chrome.tabs.create({url:c.url,windowId:c.win,active:false}); await waitLoad(t.id); await sleep(1500); return {tab:t.id}; }
    case 'nav': await chrome.tabs.update(tab,{url:c.url}); await sleep(800); await waitLoad(tab); await sleep(1500); return {ok:1};
    case 'activate': await chrome.tabs.update(tab,{active:true}); return {ok:1};
    case 'close': await chrome.tabs.remove(tab); att.delete(tab); return {ok:1};
    case 'eval': { await attach(tab); const r=await send(tab,'Runtime.evaluate',{expression:c.code,awaitPromise:true,returnByValue:true}); return {result:r.result?.value,exc:r.exceptionDetails?.exception?.description}; }
    case 'click': { await attach(tab); const o={x:c.x,y:c.y,button:'left',clickCount:1}; await send(tab,'Input.dispatchMouseEvent',{type:'mouseMoved',x:c.x,y:c.y}); await send(tab,'Input.dispatchMouseEvent',{...o,type:'mousePressed'}); await send(tab,'Input.dispatchMouseEvent',{...o,type:'mouseReleased'}); await sleep(600); return {ok:1}; }
    case 'type': await attach(tab); await send(tab,'Input.insertText',{text:c.text}); return {ok:1};
    case 'key': { await attach(tab); const k=c.key; const code={Enter:13,Tab:9,Escape:27,Backspace:8,End:35,Home:36,PageDown:34,PageUp:33}[k]||0; const p={key:k,code:k,windowsVirtualKeyCode:code,nativeVirtualKeyCode:code}; if(k==='Enter') p.text='\r'; await send(tab,'Input.dispatchKeyEvent',{...p,type:'keyDown'}); await send(tab,'Input.dispatchKeyEvent',{...p,type:'keyUp'}); return {ok:1}; }
    case 'scroll': await attach(tab); await send(tab,'Input.dispatchMouseEvent',{type:'mouseWheel',x:c.x??600,y:c.y??500,deltaX:0,deltaY:c.dy}); await sleep(600); return {ok:1};
    case 'shot': { await attach(tab); const r=await send(tab,'Page.captureScreenshot',{format:'png'}); return {data:r.data}; }
    case 'upload': { await attach(tab); const d=await send(tab,'DOM.getDocument',{depth:-1}); const q=await send(tab,'DOM.querySelector',{nodeId:d.root.nodeId,selector:c.selector}); if(!q.nodeId) return {error:'no input'}; await send(tab,'DOM.setFileInputFiles',{files:c.files,nodeId:q.nodeId}); return {ok:1}; }
    default: return {error:'unknown op '+c.op};
  }
}
let running=false;
async function loop(){ if(running) return; running=true;
  for(;;){ try{ const ac=new AbortController(); const to=setTimeout(()=>ac.abort(),30000); const r=await fetch(BASE+'/poll',{headers:{'X-Tok':TOK},signal:ac.signal}); clearTimeout(to); const c=await r.json();
      if(c.id){ let out; try{ out=await run(c);}catch(e){ out={error:String(e)}; } out.id=c.id;
        await fetch(BASE+'/result',{method:'POST',headers:{'X-Tok':TOK},body:JSON.stringify(out)}); } }
    catch(e){ await sleep(2000);} } }
chrome.runtime.onStartup.addListener(loop); chrome.runtime.onInstalled.addListener(loop);
chrome.alarms.create('k',{periodInMinutes:0.5}); chrome.alarms.onAlarm.addListener(()=>{ if(!running) loop(); });
loop();

const withTimeout=(p,ms,tab)=>Promise.race([p,new Promise((_,rej)=>setTimeout(()=>rej(new Error('command timeout '+ms+'ms')),ms))]);
async function run(c){
  const t=c.tab;
  try{ return await withTimeout(run0(c),30000,t); }
  finally{ if(t && att.has(t) && c.op!=='close' && !c.keep){ try{ await chrome.debugger.detach({tabId:t}); }catch(e){} att.delete(t); } }
}
