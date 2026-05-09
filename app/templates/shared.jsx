// Shared bits used across variations: sample transcript, helpers, waveform components.

const SAMPLE_TRANSCRIPT = [
  { who: 'BOT',  text: 'أهلاً! معاك أوريس. إزاي أقدر أساعدك النهاردة؟' },
  { who: 'USER', text: 'السلام عليكم، عايز أعرف حالة طلبي' },
  { who: 'BOT',  text: 'وعليكم السلام، تمام يا فندم. ممكن تديني رقم الطلب؟' },
  { who: 'USER', text: 'تمنية تمنية اتنين أربعة' },
  { who: 'BOT',  text: 'لحظة بس... طلبك خرج من المخزن وفي الطريق ليك، هيوصل بكره الصبح إن شاء الله.' },
];

// Pretty seconds → mm:ss
const fmtTime = (s) => `${String(Math.floor(s/60)).padStart(2,'0')}:${String(s%60).padStart(2,'0')}`;

// State -> labels (Arabic + EN)
const STATE_INFO = {
  idle:      { ar: 'جاهز للاتصال',           en: 'Idle — ready',          dur: 0,   msgs: 0 },
  ringing:   { ar: 'جاري الاتصال...',         en: 'Ringing — pick up',     dur: 4,   msgs: 0 },
  connected: { ar: 'متصل — اتكلم',           en: 'Live — agent speaking', dur: 47,  msgs: 5 },
  ended:     { ar: 'انتهت المكالمة',          en: 'Call ended',            dur: 113, msgs: 9 },
};

// Animated dual sine wave (Glow vibe)
function DualWave({ active, height = 64, colorA = '#7c72ff', colorB = '#00d4ff' }) {
  const [t, setT] = React.useState(0);
  React.useEffect(() => {
    if (!active) return;
    let raf, start = performance.now();
    const tick = (now) => { setT((now - start) / 1000); raf = requestAnimationFrame(tick); };
    raf = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(raf);
  }, [active]);

  const W = 460, H = height, mid = H / 2;
  const path = (phase, amp, freq) => {
    const pts = [];
    for (let x = 0; x <= W; x += 4) {
      const y = mid + Math.sin((x / W) * Math.PI * freq + phase) * amp
                    + Math.sin((x / W) * Math.PI * (freq * 2.3) + phase * 1.7) * (amp * 0.35);
      pts.push(`${x},${y.toFixed(1)}`);
    }
    return 'M' + pts.join(' L');
  };

  const amp = active ? mid * 0.55 : 2;
  return (
    <svg width="100%" height={H} viewBox={`0 0 ${W} ${H}`} preserveAspectRatio="none">
      <defs>
        <linearGradient id="wgA" x1="0" x2="1">
          <stop offset="0" stopColor={colorA} stopOpacity="0"/>
          <stop offset=".5" stopColor={colorA} stopOpacity="1"/>
          <stop offset="1" stopColor={colorA} stopOpacity="0"/>
        </linearGradient>
        <linearGradient id="wgB" x1="0" x2="1">
          <stop offset="0" stopColor={colorB} stopOpacity="0"/>
          <stop offset=".5" stopColor={colorB} stopOpacity=".9"/>
          <stop offset="1" stopColor={colorB} stopOpacity="0"/>
        </linearGradient>
      </defs>
      <path d={path(t * 2.4, amp, 4)}      stroke="url(#wgA)" strokeWidth="2" fill="none"/>
      <path d={path(t * -1.8 + 1, amp*0.7, 5)} stroke="url(#wgB)" strokeWidth="1.5" fill="none" opacity=".7"/>
    </svg>
  );
}

// Equalizer bars (compact)
function EqBars({ active, count = 5, color = '#7c72ff', height = 18 }) {
  const [t, setT] = React.useState(0);
  React.useEffect(() => {
    if (!active) return;
    let raf, start = performance.now();
    const tick = (now) => { setT((now - start) / 1000); raf = requestAnimationFrame(tick); };
    raf = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(raf);
  }, [active]);
  return (
    <div style={{display:'flex',gap:3,alignItems:'center',height}}>
      {Array.from({length:count}).map((_,i) => {
        const h = active ? 30 + Math.abs(Math.sin(t*4 + i*0.7)) * 70 : 12;
        return <div key={i} style={{width:3,height:`${h}%`,background:color,borderRadius:2,transition:'height 80ms'}}/>;
      })}
    </div>
  );
}

// Breathing orb (Glow vibe hero)
function GlowOrb({ state }) {
  const colors = {
    idle:      ['#3a3a5a', '#1a1a2e'],
    ringing:   ['#febc2e', '#7c4a0e'],
    connected: ['#7c72ff', '#00d4ff'],
    ended:     ['#ff5f57', '#3a1010'],
  }[state];
  const pulse = state === 'ringing' || state === 'connected';
  return (
    <div className={`glow-orb ${state} ${pulse?'pulse':''}`}
         style={{'--c1':colors[0],'--c2':colors[1]}}>
      <div className="orb-core"></div>
      <div className="orb-ring r1"></div>
      <div className="orb-ring r2"></div>
      <div className="orb-ring r3"></div>
      {state === 'connected' && <div className="orb-glyph">●</div>}
      {state === 'ringing'   && <div className="orb-glyph">📞</div>}
      {state === 'idle'      && <div className="orb-glyph">𝛼</div>}
      {state === 'ended'     && <div className="orb-glyph">✕</div>}
    </div>
  );
}

// ASCII waveform (Brutalist vibe)
function AsciiWave({ active }) {
  const [t, setT] = React.useState(0);
  React.useEffect(() => {
    if (!active) { setT(0); return; }
    const id = setInterval(() => setT(x => x + 1), 80);
    return () => clearInterval(id);
  }, [active]);
  const blocks = '▁▂▃▄▅▆▇█';
  const N = 36;
  const line = Array.from({length:N}).map((_, i) => {
    if (!active) return '─';
    const v = (Math.sin((i*0.5) + t*0.4) + Math.sin((i*0.13)+t*0.7)) * 0.5 + 0.5;
    return blocks[Math.min(blocks.length-1, Math.floor(v * blocks.length))];
  }).join('');
  return <div className="ascii-wave">{line}</div>;
}

Object.assign(window, { SAMPLE_TRANSCRIPT, STATE_INFO, fmtTime, DualWave, EqBars, GlowOrb, AsciiWave });
