// Three vibe directions, each rendering one of four states.
// Each is a self-contained 460×720 panel meant to live inside a DCArtboard.

// ─────────────────────────────────────────────────────────────
// 1) GLOW — refined dark-purple, glassmorphism, breathing orb,
//    dual-wave audio viz, soft depth.
// ─────────────────────────────────────────────────────────────
function GlowApp({ state }) {
  const info = STATE_INFO[state];
  const transcript = state === 'connected' ? SAMPLE_TRANSCRIPT.slice(0,4)
                   : state === 'ended'     ? SAMPLE_TRANSCRIPT
                   : [];
  return (
    <div className="glow-root" dir="rtl">
      {/* ambient gradient */}
      <div className="glow-bg"></div>
      <div className="glow-bg-2"></div>

      {/* titlebar */}
      <div className="glow-titlebar">
        <div className="glow-tb-left">
          <div className="glow-mono">أوريس</div>
          <div className="glow-tb-divider"></div>
          <div className="glow-tb-meta">AURIS · AI VOICE</div>
        </div>
        <div className="glow-ctrls">
          <span className="glow-ctrl yellow"></span>
          <span className="glow-ctrl red"></span>
        </div>
      </div>

      {/* hero */}
      <div className="glow-hero">
        <GlowOrb state={state}/>
        <div className="glow-status-text">
          <div className="glow-status-ar">{info.ar}</div>
          <div className="glow-status-en">{info.en}</div>
        </div>
      </div>

      {/* waveform */}
      <div className="glow-wave">
        <DualWave active={state === 'connected'}/>
      </div>

      {/* buttons */}
      <div className="glow-actions">
        {state === 'idle' && (
          <button className="glow-btn primary">
            <span className="glow-btn-ring"></span>
            <span>اتصل بيا</span>
            <span className="glow-btn-en">CALL ME</span>
          </button>
        )}
        {state === 'ringing' && (
          <>
            <button className="glow-btn ghost"><span>إلغاء</span></button>
            <button className="glow-btn answer">
              <span className="glow-btn-ring pulse"></span>
              <span>رد</span>
            </button>
          </>
        )}
        {state === 'connected' && (
          <button className="glow-btn danger" style={{flex:1}}>
            <span>إنهاء المكالمة</span>
          </button>
        )}
        {state === 'ended' && (
          <button className="glow-btn primary" style={{flex:1}}>
            <span>اتصل تاني</span>
          </button>
        )}
      </div>

      {/* stats pill */}
      <div className="glow-stats">
        <div className="glow-stat">
          <div className="glow-stat-val">{fmtTime(info.dur)}</div>
          <div className="glow-stat-key">المدة</div>
        </div>
        <div className="glow-stat-div"></div>
        <div className="glow-stat">
          <div className="glow-stat-val">{info.msgs}</div>
          <div className="glow-stat-key">رسائل</div>
        </div>
        <div className="glow-stat-div"></div>
        <div className="glow-stat">
          <div className="glow-stat-val sm">ElevenLabs</div>
          <div className="glow-stat-key">الوكيل</div>
        </div>
      </div>

      {/* transcript */}
      <div className="glow-transcript-wrap">
        <div className="glow-section-label">
          <span>النص المباشر</span>
          {state === 'connected' && <EqBars active count={4} color="#7c72ff"/>}
        </div>
        <div className="glow-transcript">
          {transcript.length === 0 ? (
            <div className="glow-empty">— النص هيظهر هنا —</div>
          ) : transcript.map((m, i) => (
            <div key={i} className={`glow-bubble ${m.who === 'BOT' ? 'bot' : 'user'}`}>
              <div className="glow-bubble-tag">{m.who === 'BOT' ? '🤖 أوريس' : '🎤 أنت'}</div>
              <div className="glow-bubble-text">{m.text}</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

// ─────────────────────────────────────────────────────────────
// 2) BRUTALIST — terminal aesthetic, all mono, ASCII waveform,
//    bracketed status, dense info.
// ─────────────────────────────────────────────────────────────
function BrutalApp({ state }) {
  const info = STATE_INFO[state];
  const transcript = state === 'connected' ? SAMPLE_TRANSCRIPT.slice(0,4)
                   : state === 'ended'     ? SAMPLE_TRANSCRIPT
                   : [];
  const stateTag = { idle:'IDLE', ringing:'RINGING', connected:'LIVE', ended:'ENDED' }[state];
  const stateColor = { idle:'#6a6a8a', ringing:'#febc2e', connected:'#28c840', ended:'#ff5f57' }[state];

  return (
    <div className="brut-root" dir="rtl">
      <div className="brut-titlebar">
        <span className="brut-tb-meta">[ AURIS ]</span>
        <span className="brut-tb-meta dim">VOICE_BRIDGE_v2.4</span>
        <span className="brut-tb-meta dim" style={{marginInlineStart:'auto'}}>—  ☐  ✕</span>
      </div>

      <div className="brut-grid">
        {/* row 1: status */}
        <div className="brut-cell brut-status" style={{'--accent': stateColor}}>
          <div className="brut-line">
            <span className="brut-prompt">&gt;&gt;</span>
            <span className="brut-key">STATUS</span>
            <span className="brut-val" style={{color: stateColor}}>
              [ {stateTag} ]
              <span className="brut-cursor">█</span>
            </span>
          </div>
          <div className="brut-line ar">
            <span className="brut-key" style={{fontFamily:'Cairo,sans-serif'}}>{info.ar}</span>
          </div>
        </div>

        {/* row 2: ascii wave */}
        <div className="brut-cell brut-wave-cell">
          <div className="brut-cell-tag">// AUDIO_STREAM</div>
          <AsciiWave active={state === 'connected'}/>
          <div className="brut-wave-meta">
            <span>{state === 'connected' ? '◉ LIVE' : '○ MUTED'}</span>
            <span>·</span>
            <span>16kHz · μ-law</span>
          </div>
        </div>

        {/* row 3: stats */}
        <div className="brut-stats">
          <div className="brut-stat">
            <span className="brut-stat-key">DUR</span>
            <span className="brut-stat-val">{fmtTime(info.dur)}</span>
          </div>
          <div className="brut-stat">
            <span className="brut-stat-key">MSG</span>
            <span className="brut-stat-val">{String(info.msgs).padStart(3,'0')}</span>
          </div>
          <div className="brut-stat">
            <span className="brut-stat-key">AGT</span>
            <span className="brut-stat-val">11LABS</span>
          </div>
          <div className="brut-stat">
            <span className="brut-stat-key">LANG</span>
            <span className="brut-stat-val">AR-EG</span>
          </div>
        </div>

        {/* row 4: actions */}
        <div className="brut-actions">
          {state === 'idle' && (
            <button className="brut-btn primary">
              [ CALL_ME ]<span className="brut-btn-sub">اتصل بيا</span>
            </button>
          )}
          {state === 'ringing' && (
            <>
              <button className="brut-btn ghost">[ REJECT ]</button>
              <button className="brut-btn primary">[ ANSWER ]<span className="brut-btn-sub">رد</span></button>
            </>
          )}
          {state === 'connected' && (
            <button className="brut-btn danger" style={{flex:1}}>[ HANG_UP ]<span className="brut-btn-sub">إنهاء</span></button>
          )}
          {state === 'ended' && (
            <button className="brut-btn primary" style={{flex:1}}>[ CALL_AGAIN ]<span className="brut-btn-sub">اتصل تاني</span></button>
          )}
        </div>

        {/* row 5: transcript */}
        <div className="brut-transcript">
          <div className="brut-cell-tag">// TRANSCRIPT_STREAM</div>
          <div className="brut-trans-body">
            {transcript.length === 0 ? (
              <div className="brut-empty">$ awaiting_stream...<span className="brut-cursor">█</span></div>
            ) : transcript.map((m, i) => (
              <div key={i} className="brut-line">
                <span className={`brut-tag ${m.who === 'BOT' ? 'bot' : 'usr'}`}>
                  [{m.who === 'BOT' ? 'BOT' : 'USR'}]
                </span>
                <span className="brut-msg">{m.text}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

// ─────────────────────────────────────────────────────────────
// 3) EDITORIAL — Arabic typography-led, warm dark, saffron accent,
//    big display type as hero, calligraphic flourish.
// ─────────────────────────────────────────────────────────────
function EditorialApp({ state }) {
  const info = STATE_INFO[state];
  const transcript = state === 'connected' ? SAMPLE_TRANSCRIPT.slice(0,4)
                   : state === 'ended'     ? SAMPLE_TRANSCRIPT
                   : [];

  // Word that sits above the title, signaling state in Arabic
  const heroState = {
    idle:      'استعداد',
    ringing:   'طنين',
    connected: 'حوار',
    ended:     'ختام',
  }[state];

  return (
    <div className="ed-root" dir="rtl">
      <div className="ed-grain"></div>

      {/* top meta */}
      <div className="ed-top">
        <span className="ed-meta">No. 01</span>
        <span className="ed-meta-line"></span>
        <span className="ed-meta">AURIS · 2026</span>
        <span className="ed-meta-line"></span>
        <span className="ed-meta dim">{state.toUpperCase()}</span>
      </div>

      {/* hero typography */}
      <div className="ed-hero">
        <div className="ed-state-word">{heroState}</div>
        <div className="ed-title-row">
          <div className="ed-flourish">
            <svg viewBox="0 0 80 80" width="64" height="64">
              <circle cx="40" cy="40" r={state==='ringing'?34:28} fill="none"
                      stroke="#f4b942" strokeWidth="1" opacity=".5"/>
              <circle cx="40" cy="40" r="20" fill="none" stroke="#f4b942" strokeWidth="1.5"/>
              <circle cx="40" cy="40" r={state==='connected'?14:6}
                      fill="#f4b942"
                      style={{transition:'r .6s'}}/>
              {state === 'connected' && (
                <g>
                  <circle cx="40" cy="40" r="28" fill="none" stroke="#f4b942" strokeWidth="1" opacity=".3"
                          style={{animation:'edPulse 2s infinite'}}/>
                </g>
              )}
            </svg>
          </div>
          <div className="ed-title">أوريس</div>
        </div>
        <div className="ed-tagline">
          <span>ذكاء اصطناعي يتكلّم</span>
          <span className="ed-em">بالمصري</span>
        </div>
      </div>

      {/* status row */}
      <div className="ed-status-row">
        <div className={`ed-status-pill ${state}`}>
          <span className="ed-status-dot"></span>
          <span>{info.ar}</span>
        </div>
        <div className="ed-status-en">{info.en}</div>
      </div>

      {/* transcript or idle composition */}
      <div className="ed-body">
        {transcript.length === 0 ? (
          <div className="ed-idle-quote">
            <div className="ed-idle-mark">"</div>
            <div className="ed-idle-text">
              {state === 'idle'    && 'اضغط زرّ الاتصال وأنا هردّ عليك في ثواني.'}
              {state === 'ringing' && 'افتح المتصفح ورد على المكالمة لتبدأ المحادثة.'}
              {state === 'ended'   && 'شكراً ليك. المحادثة اتسجلت في سجل المكالمات.'}
            </div>
          </div>
        ) : (
          <div className="ed-transcript">
            {transcript.map((m, i) => (
              <div key={i} className={`ed-msg ${m.who === 'BOT' ? 'bot' : 'user'}`}>
                <div className="ed-msg-byline">
                  <span className="ed-msg-num">{String(i+1).padStart(2,'0')}</span>
                  <span className="ed-msg-who">{m.who === 'BOT' ? 'أوريس' : 'أنت'}</span>
                  <span className="ed-msg-rule"></span>
                </div>
                <div className="ed-msg-text">{m.text}</div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* footer with action + stats */}
      <div className="ed-foot">
        <div className="ed-foot-stats">
          <div className="ed-foot-stat">
            <span className="ed-foot-key">المدة</span>
            <span className="ed-foot-val">{fmtTime(info.dur)}</span>
          </div>
          <div className="ed-foot-stat">
            <span className="ed-foot-key">رسائل</span>
            <span className="ed-foot-val">{info.msgs}</span>
          </div>
        </div>

        {state === 'idle' && (
          <button className="ed-btn primary"><span>ابدأ الحوار</span><span className="ed-btn-arrow">←</span></button>
        )}
        {state === 'ringing' && (
          <button className="ed-btn answer"><span>رد على المكالمة</span><span className="ed-btn-arrow">←</span></button>
        )}
        {state === 'connected' && (
          <button className="ed-btn danger"><span>إنهاء</span></button>
        )}
        {state === 'ended' && (
          <button className="ed-btn primary"><span>اتصل تاني</span><span className="ed-btn-arrow">←</span></button>
        )}
      </div>
    </div>
  );
}

Object.assign(window, { GlowApp, BrutalApp, EditorialApp });
