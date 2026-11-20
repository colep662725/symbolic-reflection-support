from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]
tarot=(ROOT/'data/tarot.json').read_text(encoding='utf-8').replace('<','\\u003c')
hexs=(ROOT/'data/iching.json').read_text(encoding='utf-8').replace('<','\\u003c')
html=r'''<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="color-scheme" content="light dark">
<title>Symbolic Reflection Support — Offline demo</title>
<style>
:root {--paper:#f8f4ec;--ink:#27232c;--sub:#635c67;--line:#d4cbc2;--cream:#fcf9f4;--gold:#b88a46;--shadow:0 12px 40px #20151a18;}
*{box-sizing:border-box}
body{background:radial-gradient(circle at 15% 2%,#ece2cc 0,transparent 37%),radial-gradient(circle at 90% 25%,#e6d8e1 0,transparent 33%),var(--paper);color:var(--ink);font:16px/1.55 system-ui,-apple-system,"Segoe UI","Noto Sans CJK SC",sans-serif;margin:0}
a{color:inherit}button,select,input{font:inherit}button{cursor:pointer}
main{max-width:1120px;margin:auto;padding:32px 20px 70px}
.head{display:flex;justify-content:space-between;align-items:center;gap:16px;flex-wrap:wrap}
.brand{display:flex;align-items:center;gap:10px;font-size:.9rem;font-weight:800;letter-spacing:.1em;text-transform:uppercase}
.star{display:inline-grid;place-items:center;width:33px;height:33px;border:1px solid var(--gold);border-radius:100%;color:#946a31;font-size:1.3rem}
.pill{border:1px solid var(--line);background:#ffffff85;border-radius:99px;padding:6px 13px;font-size:.77rem}
h1{font-family:Georgia,"Noto Serif CJK SC",serif;font-weight:500;font-size:clamp(2.4rem,6vw,4.7rem);letter-spacing:-.055em;line-height:1.05;max-width:750px;margin:35px 0 18px}
.lead{font-size:1.03rem;color:var(--sub);max-width:740px}
.hero{display:grid;grid-template-columns:1.1fr .9fr;align-items:center;gap:28px;margin-bottom:40px}
.orbit{width:min(100%,370px);aspect-ratio:1;border:1px solid #af996e60;border-radius:50%;margin:auto;display:grid;place-items:center;position:relative;box-shadow:inset 0 0 0 35px #ddc5ad22,inset 0 0 0 88px #d1a87315}
.orbit:before{content:"✦";font-size:7.4rem;font-weight:100;color:#9e7954;filter:drop-shadow(4px 8px 4px #ac896166)}
.orbit:after{content:"S R S   •   1.2.0";position:absolute;top:14%;font: .78rem/1 Georgia;letter-spacing:.2em;color:#7f6e60}
.panel{background:#ffffffc4;border:1px solid #ffffff;box-shadow:var(--shadow);border-radius:22px;padding:26px;margin:20px 0;backdrop-filter:blur(5px)}
.controls{display:grid;grid-template-columns:1fr 1fr;gap:25px}.eyebrow{text-transform:uppercase;letter-spacing:.16em;color:#907047;font-size:.72rem;font-weight:800}
h2{font-family:Georgia,"Noto Serif CJK SC",serif;font-weight:500;font-size:1.65rem;margin:4px 0 11px}
.desc{color:var(--sub);font-size:.88rem;margin-top:3px}
.group{display:flex;gap:9px;flex-wrap:wrap;margin-top:16px}.field{display:flex;gap:8px;flex-direction:column;margin-top:8px}
select,input{border:1px solid var(--line);background:var(--cream);border-radius:10px;padding:11px 12px;color:var(--ink);max-width:100%}
button{border:1px solid #4a3745;background:#4a3745;color:white;border-radius:11px;padding:12px 15px;transition:transform .12s,background .12s;min-height:44px}
button:hover{transform:translateY(-1px);background:#342730}button.secondary{color:var(--ink);background:transparent;border-color:var(--line)}button.secondary:hover{background:#ede7e3}
button:focus-visible,select:focus-visible,input:focus-visible{outline:3px solid #b48c49;outline-offset:2px}
#output{min-height:220px}.results{display:grid;grid-template-columns:repeat(auto-fit,minmax(190px,1fr));gap:12px}
.card{border:1px solid var(--line);border-radius:13px;padding:19px;background:linear-gradient(145deg,#fffefa,#f2e9dd)}
.card .n{font-size:.74rem;letter-spacing:.1em;color:#8b744e;text-transform:uppercase}.card h3{font-family:Georgia,"Noto Serif CJK SC",serif;font-size:1.36rem;margin:8px 0 6px}.card p{margin:7px 0;font-size:.9rem}.card .q{color:var(--sub);font-size:.84rem}
.meta{font: .82rem/1.5 ui-monospace,Consolas,monospace;color:var(--sub);word-wrap:break-word;margin:10px 0}
.hex{display:grid;grid-template-columns:1fr 1fr;gap:12px}.line{display:flex;gap:11px;align-items:center;font-size:.86rem;margin:6px 0}.yin,.yang{width:95px;height:13px;display:flex;justify-content:space-between}.yang:before{content:"";width:100%;border-radius:2px;background:#4d4051}.yin:before,.yin:after{content:"";width:43%;background:#4d4051;border-radius:2px}
small.note{color:var(--sub);font-size:.76rem}.footer{color:var(--sub);font-size:.77rem;margin-top:28px}.error{color:#a43741}.row{display:flex;justify-content:space-between;gap:10px;align-items:center;flex-wrap:wrap}
@media(max-width:780px){.hero{grid-template-columns:1fr}.orbit{width:200px}.controls{grid-template-columns:1fr}.hex{grid-template-columns:1fr}main{padding:23px 14px 40px}}
@media(prefers-reduced-motion:reduce){*{animation:none!important;transition:none!important}}
</style>
</head>
<body>
<main>
<header class="head"><div class="brand"><span class="star" aria-hidden="true">✳</span>Symbolic Reflection Support</div><div class="row"><span class="pill">OFFLINE / 1.2</span><label for="lang" id="language-label">语言</label><select id="lang" aria-label="Language"><option value="zh">简体中文</option><option value="en">English</option><option value="ja">日本語</option><option value="fr">Français</option><option value="es">Español</option><option value="pt">Português</option></select></div></header>
<section class="hero"><div><div class="eyebrow">AN OPEN-SOURCE AGENT SKILL</div><h1 id="hero-title">把象征变成可检验的自我提问。</h1><p class="lead" id="hero-description">离线塔罗与三枚硬币易经。实际抽取、原始记录与象征解读分开呈现；不联网，不索取个人信息。</p><p class="desc" id="hero-disclaimer">象征性自我反思，不是命运预测或专业建议。</p></div><div class="orbit" aria-hidden="true"></div></section>
<section class="panel controls" aria-label="Controls">
<div><div class="eyebrow">01 / RANDOM</div><h2 id="draw-title">随机体验</h2><div class="desc" id="draw-info">使用浏览器安全随机源，不保存结果。</div><div class="group"><button id="one">抽一张塔罗</button><button id="three">抽三张塔罗</button><button id="coins">三枚硬币起卦</button></div></div>
<div><div class="eyebrow">02 / EXPLORE</div><h2 id="lookup-title">浏览解释数据库</h2><div class="desc" id="lookup-info">指定牌或卦属于用户选择，不冒充随机抽取。</div><div class="field"><label for="card-select" id="card-label">选择塔罗牌</label><select id="card-select"></select><label for="orientation-select" id="orientation-label">牌位</label><select id="orientation-select"><option value="upright">正位</option><option value="reversed">逆位</option></select><button id="lookup-card" class="secondary">查看牌义</button></div><div class="field"><label for="hex-select" id="hex-label">选择易经卦序</label><select id="hex-select"></select><button id="lookup-hex" class="secondary">查看卦义</button></div><div class="field"><label for="lines-input" id="lines-label">六爻数值（自下而上）</label><input id="lines-input" inputmode="numeric" value="7 8 7 9 7 8" autocomplete="off" aria-label="Six line values from bottom to top"><button id="lookup-lines" class="secondary">解读输入的六爻</button></div></div>
</section>
<section class="panel" aria-live="polite" aria-atomic="false"><div class="row"><div><div class="eyebrow">03 / RECORD</div><h2 id="result-title">解读结果</h2></div><button id="copy" class="secondary" type="button" disabled>复制 JSON</button></div><div id="status" class="meta"></div><div id="output"><p class="desc" id="start-hint">选择一种方式开始。结果只保存在当前页面内存中。</p></div></section>
<p class="footer" id="footer">原创简短主题不是《周易》经文或经典塔罗引述。浏览器演示独立使用 Web Crypto 随机源；Python CLI 保留自己的来源记录。无 API、无分析脚本、无本地持久化。</p>
</main>
<script type="application/json" id="tarot-data">__TAROT_JSON__</script>
<script type="application/json" id="iching-data">__ICHING_JSON__</script>
<script>
'use strict';
const tarot=JSON.parse(document.getElementById('tarot-data').textContent).cards;
const hexes=JSON.parse(document.getElementById('iching-data').textContent).hexagrams;
const KING_WEN=[[1,43,14,34,9,5,26,11],[10,58,38,54,61,60,41,19],[13,49,30,55,37,63,22,36],[25,17,21,51,42,3,27,24],[44,28,50,32,57,48,18,46],[6,47,64,40,59,29,4,7],[33,31,56,62,53,39,52,15],[12,45,35,16,20,8,23,2]];
const trigrams=['111','110','101','100','011','010','001','000'];
const $=id=>document.getElementById(id);
const ui={
zh:['语言','把象征变成可检验的自我提问。','离线塔罗与三枚硬币易经。实际抽取、原始记录与象征解读分开呈现；不联网，不索取个人信息。','象征性自我反思，不是命运预测或专业建议。','随机体验','使用浏览器安全随机源，不保存结果。','抽一张塔罗','抽三张塔罗','三枚硬币起卦','浏览解释数据库','指定牌或卦属于用户选择，不冒充随机抽取。','选择塔罗牌','查看牌义','选择易经卦序','查看卦义','解读结果','复制 JSON','选择一种方式开始。结果只保存在当前页面内存中。','原创简短主题不是《周易》经文或经典塔罗引述。浏览器演示独立使用 Web Crypto 随机源；Python CLI 保留自己的来源记录。无 API、无分析脚本、无本地持久化。','正位','逆位','反思主题','用户选择','浏览器安全随机','六爻自下而上','动爻','本卦','变卦','无动爻','自我提问','在你的生活中，「{theme}」与什么有关？你能做的一个小行动是什么？'],
en:['Language','Turn symbols into grounded reflection.','Offline Tarot and three-coin I Ching. The draws, exact records and interpretations are separate. No internet or personal data required.','Symbolic self-reflection, not prediction or professional advice.','Random experience','Browser Web Crypto, no saved results.','Draw one Tarot','Draw three Tarot','Cast three coins','Explore interpretation data','Chosen symbols are user-selected, not random draws.','Select Tarot card','Read card','Choose King Wen hexagram','Read hexagram','Your result','Copy JSON','Select a method to begin. Results remain in page memory only.','Original themes are not classical I Ching texts or quoted Tarot guides. Browser Web Crypto draws are independent of the Python CLI. No API, analytics or persistent storage.','upright','reversed','Reflection cue','user selected','browser Web Crypto random','Lines from bottom','Moving lines','Primary','Resulting','No moving lines','Question','Where does “{theme}” matter in your life, and what small step is under your control?'],
ja:['言語','象徴から自分への問いを。','オフラインのタロットと易経三枚硬貨法。結果と解釈を分け、個人情報を集めません。','象徴的な内省であり、予言ではありません。','ランダムに引く','ブラウザーの暗号学的乱数。記録しません。','一枚引き','三枚引き','三枚硬貨で起卦','データを調べる','指定した結果はランダムではありません。','タロットを選択','カードを読む','卦番号を選択','卦を読む','結果','JSONをコピー','方法を選んでください。結果は画面の中だけです。','短いテーマは経文の引用ではありません。通信も記録も行いません。','正位置','逆位置','内省テーマ','利用者の指定','ブラウザーの乱数','下からの六爻','変爻','本卦','変卦','変爻なし','問い','あなたの生活で「{theme}」は何を意味しますか？できる小さな一歩は？'],
fr:['Langue','Transformer les symboles en réflexion.','Tarot et Yi Jing hors ligne. Tirages, données et interprétations sont distincts, sans données personnelles.','Réflexion symbolique, non prédiction.','Tirage','Aléatoire sécurisé du navigateur, sans stockage.','Une carte','Trois cartes','Trois pièces','Explorer les données','Un symbole choisi n’est pas un tirage.','Choisir la carte','Voir la carte','Choisir l’hexagramme','Voir l’hexagramme','Résultat','Copier JSON','Choisissez une méthode. Les résultats ne sont pas enregistrés.','Ces thèmes originaux ne citent pas le Yi Jing classique. Aucun réseau, suivi ni stockage.','à l’endroit','renversée','Piste de réflexion','choix utilisateur','tirage navigateur sécurisé','Traits depuis le bas','Traits mutants','Initial','Résultant','Aucun trait mutant','Question','Où « {theme} » compte-t-il dans votre vie ? Quelle action est possible ?'],
es:['Idioma','Convertir símbolos en reflexión real.','Tarot e I Ching sin conexión. Separamos el sorteo, el registro y la interpretación; sin datos personales.','Reflexión simbólica, no predicción.','Sorteo','Aleatoriedad segura del navegador; sin guardar resultados.','Una carta','Tres cartas','Tres monedas','Explorar datos','Elegir una carta no es un sorteo.','Elegir carta','Ver carta','Elegir hexagrama','Ver hexagrama','Resultado','Copiar JSON','Elige un método. Los resultados no se guardan.','Estos temas originales no citan textos clásicos. Sin red, seguimiento ni almacenamiento.','derecha','invertida','Tema','elección del usuario','sorteo seguro del navegador','Líneas desde abajo','Líneas móviles','Inicial','Resultante','Sin líneas móviles','Pregunta','¿Dónde importa «{theme}» en tu vida y qué pequeño paso puedes dar?'],
pt:['Idioma','Transforme símbolos em reflexão.','Tarô e I Ching off-line. Sorteio, registro e interpretação separados; sem dados pessoais.','Reflexão simbólica, não previsão.','Sorteio','Aleatoriedade segura do navegador; sem guardar resultados.','Uma carta','Três cartas','Três moedas','Explorar dados','Escolhas não são sorteios.','Escolher carta','Ver carta','Escolher hexagrama','Ver hexagrama','Resultado','Copiar JSON','Escolha um método. Os resultados não são salvos.','Temas originais, não citações clássicas. Sem rede, rastreamento ou armazenamento.','normal','invertida','Tema','escolha do usuário','sorteio seguro do navegador','Linhas de baixo para cima','Linhas móveis','Inicial','Resultante','Sem linhas móveis','Pergunta','Onde «{theme}» importa na sua vida e qual pequeno passo você pode dar?']
};
const uiMore={
zh:['牌位','六爻数值（自下而上，6/7/8/9）','解读输入的六爻','三枚硬币（自下而上）','请输入六个6、7、8、9之间的整数。'],
en:['Orientation','Six line values (bottom first, 6/7/8/9)','Decode supplied lines','Coins (bottom first)','Enter six values, each 6, 7, 8 or 9.'],
ja:['正逆位置','六爻の値（下から、6/7/8/9）','入力した六爻を読む','硬貨（下から）','六つの6・7・8・9を入力してください。'],
fr:['Orientation','Six valeurs (du bas, 6/7/8/9)','Décoder les traits fournis','Pièces (depuis le bas)','Saisissez six valeurs : 6, 7, 8 ou 9.'],
es:['Orientación','Seis valores (desde abajo, 6/7/8/9)','Leer las líneas indicadas','Monedas (desde abajo)','Introduce seis valores: 6, 7, 8 o 9.'],
pt:['Orientação','Seis valores (de baixo para cima, 6/7/8/9)','Ler linhas informadas','Moedas (de baixo para cima)','Digite seis valores: 6, 7, 8 ou 9.']
};
const bindIds=['language-label' ,'hero-title','hero-description','hero-disclaimer','draw-title','draw-info','one','three','coins','lookup-title','lookup-info','card-label','lookup-card','hex-label','lookup-hex','result-title','copy','start-hint','footer'];
let lastRecord=null;
function language(){return $('lang').value}
function applyLanguage(){const l=language();document.documentElement.lang=({zh:'zh-CN',en:'en',ja:'ja',fr:'fr',es:'es',pt:'pt'})[l]||l;bindIds.forEach((id,i)=>{const elem=$(id);if(elem)elem.textContent=ui[l][i]});$('orientation-label').textContent=uiMore[l][0];$('lines-label').textContent=uiMore[l][1];$('lookup-lines').textContent=uiMore[l][2];$('orientation-select').options[0].textContent=ui[l][19];$('orientation-select').options[1].textContent=ui[l][20];fillOptions();if(lastRecord){const old=lastRecord;if(old.method==='tarot')showCards(old.outcome,old.source,old.generated_at_utc);else showHex(old.outcome,old.source,old.generated_at_utc)}}
function fillOptions(){const l=language();$('card-select').replaceChildren();tarot.forEach(c=>{const o=document.createElement('option');o.value=c.id;o.textContent=c.names[l];$('card-select').append(o)});$('hex-select').replaceChildren();hexes.forEach(h=>{const o=document.createElement('option');o.value=h.number;o.textContent=`${h.number}. ${h.name_zh} (${h.pinyin})`;$('hex-select').append(o)});}
function rand(n){if(!globalThis.crypto||typeof crypto.getRandomValues!=='function')throw Error('Web Crypto unavailable. Use Python scripts/reflect.py instead.');const top=4294967296;const max=top-(top%n);const a=new Uint32Array(1);do{crypto.getRandomValues(a)}while(a[0]>=max);return a[0]%n;}
function pick(n){const a=Array.from({length:tarot.length},(_,i)=>i);for(let i=0;i<n;i++){const j=i+rand(a.length-i);[a[i],a[j]]=[a[j],a[i]]}return a.slice(0,n).map(i=>({id:tarot[i].id,orientation:rand(2)===0?'upright':'reversed'}))}
function record(source,method,outcome,timestamp){lastRecord={schema_version:'browser-demo-1.2',source,method,generated_at_utc:timestamp||new Date().toISOString(),outcome};const sourceLabel=({zh:'来源',en:'Source',ja:'出典',fr:'Source',es:'Origen',pt:'Origem'})[language()];$('status').textContent=`${sourceLabel}: ${source} · ${lastRecord.generated_at_utc}`;$('status').classList.remove('error');$('copy').disabled=false;}
function labelTheme(theme){const l=language();return ui[l][21]+': '+theme}
function newCard(title,theme,question){const div=document.createElement('article');div.className='card';const h=document.createElement('h3');h.textContent=title;const p=document.createElement('p');p.textContent=labelTheme(theme);const q=document.createElement('p');q.className='q';q.textContent=ui[language()][29]+': '+question;div.append(h,p,q);return div}
function showCards(cards,source,timestamp){const l=language();record(source,'tarot',cards,timestamp);const container=document.createElement('div');container.className='results';for(const item of cards){const card=tarot.find(c=>c.id===item.id);const theme=card.cues[l][item.orientation];const q=ui[l][30].replace('{theme}',theme);container.append(newCard(card.names[l]+' · '+ui[l][item.orientation==='upright'?19:20],theme,q))}$('output').replaceChildren(container)}
function hexFromBits(bits){const k=s=>trigrams.indexOf(s);return KING_WEN[k(bits.slice(0,3).join(''))][k(bits.slice(3).join(''))]}
function showHex(outcome,source,timestamp){const l=language();record(source,'iching',outcome,timestamp);const primary=hexes[outcome.primary-1];const result=outcome.resulting?hexes[outcome.resulting-1]:null;const container=document.createElement('div');container.className='hex';const q=h=>ui[l][30].replace('{theme}',h.themes[l]);container.append(newCard(ui[l][26]+' · #'+primary.number+' '+primary.name_zh,primary.themes[l],q(primary)));if(result)container.append(newCard(ui[l][27]+' · #'+result.number+' '+result.name_zh,result.themes[l],q(result)));const d=document.createElement('div');d.className='card';if(outcome.lines){const label=document.createElement('p');label.textContent=ui[l][24]+': '+outcome.lines.join(', ');d.append(label);for(let i=5;i>=0;i--){const line=document.createElement('div');line.className='line';const span=document.createElement('span');span.textContent=(i+1)+'.';const bar=document.createElement('span');bar.className=outcome.lines[i]%2===1?'yang':'yin';line.append(span,bar);if(outcome.moving.includes(i+1)){const mark=document.createElement('span');mark.textContent='↻';line.append(mark)}d.append(line)}const moving=document.createElement('p');moving.textContent=outcome.moving.length?ui[l][25]+': '+outcome.moving.join(', '):ui[l][28];d.append(moving);if(outcome.coins){const c=document.createElement('p');c.className='meta';c.textContent=uiMore[l][3]+': '+outcome.coins.map(row=>row.join('-')).join(' | ');d.append(c)}}else{const p=document.createElement('p');p.textContent=ui[l][22];d.append(p)}container.append(d);$('output').replaceChildren(container)}
function cast(){const coins=Array.from({length:6},()=>Array.from({length:3},()=>2+rand(2)));const lines=coins.map(x=>x.reduce((a,b)=>a+b,0));const bits=lines.map(n=>n%2);const changed=bits.map((b,i)=>(lines[i]===6||lines[i]===9)?1-b:b);const moving=lines.flatMap((n,i)=>(n===6||n===9)?[i+1]:[]);return {coins,lines,moving,primary:hexFromBits(bits),resulting:moving.length?hexFromBits(changed):null}}
function safe(fn){try{fn()}catch(err){$('status').textContent=String(err.message);$('status').classList.add('error')}}
$('one').addEventListener('click',()=>safe(()=>showCards(pick(1),'browser_webcrypto')));
$('three').addEventListener('click',()=>safe(()=>showCards(pick(3),'browser_webcrypto')));
$('coins').addEventListener('click',()=>safe(()=>showHex(cast(),'browser_webcrypto')));
$('lookup-card').addEventListener('click',()=>safe(()=>showCards([{id:$('card-select').value,orientation:$('orientation-select').value}],'user_selected_card')));
$('lookup-hex').addEventListener('click',()=>safe(()=>showHex({primary:Number($('hex-select').value),resulting:null,moving:[]},'user_selected_hexagram')));
$('lookup-lines').addEventListener('click',()=>safe(()=>{const raw=$('lines-input').value.trim().split(/[\s,，]+/);const lines=raw.map(Number);if(lines.length!==6||lines.some(n=>![6,7,8,9].includes(n)))throw Error(uiMore[language()][4]);const bits=lines.map(n=>n%2);const moved=lines.flatMap((n,i)=>(n===6||n===9)?[i+1]:[]);const changed=bits.map((bit,i)=>(lines[i]===6||lines[i]===9)?1-bit:bit);showHex({lines,moving:moved,primary:hexFromBits(bits),resulting:moved.length?hexFromBits(changed):null},'user_supplied_lines_browser')}));
$('copy').addEventListener('click',async()=>{if(!lastRecord)return;const result=JSON.stringify(lastRecord,null,2);try{await navigator.clipboard.writeText(result);$('copy').textContent='✓'}catch{window.prompt('Copy JSON:',result)}});
$('lang').addEventListener('change',applyLanguage);
applyLanguage();
</script>
</body>
</html>'''
html=html.replace('__TAROT_JSON__',tarot).replace('__ICHING_JSON__',hexs)
target=ROOT/'docs/index.html'
if '--check' in __import__('sys').argv:
    if not target.exists() or target.read_text(encoding='utf-8') != html:
        raise SystemExit('Browser demo HTML is out of sync with the JSON catalogs. Run: python scripts/build_demo.py')
    print('PASS: browser demo matches JSON catalogs')
else:
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(html,encoding='utf-8')
    print('Built demo HTML',len(html),'chars')
