export const FPS = 30;
export const TOTAL_S = 34;
export const TOTAL_FRAMES = TOTAL_S * FPS; // 1020

// Scene start frames and durations
export const SCENES = {
  INTRO: {start: 0,   dur: 60},   // 0–2s   board reveal + tagline
  HOOK:  {start: 60,  dur: 90},   // 2–5s
  PLAN:  {start: 150, dur: 180},  // 5–11s
  GATE1: {start: 330, dur: 120},  // 11–15s
  BUILD: {start: 450, dur: 150},  // 15–20s
  GATE2: {start: 600, dur: 150},  // 20–25s
  CLOSE: {start: 750, dur: 120},  // 25–29s
  BOARD: {start: 870, dur: 150},  // 29–34s
} as const;

export const BG      = '#0f0f10';
export const BLUE    = '#2563eb';
export const GREEN   = '#22c55e';
export const RED     = '#ef4444';
export const TEXT    = '#e2e8f0';
export const MUTED   = '#94a3b8';
export const CARD    = '#161b22';
export const BORDER  = '#1e293b';
export const TERM    = '#4ade80';   // terminal green

export const MONO = "'JetBrains Mono', 'Fira Code', 'Consolas', monospace";
export const SANS = "'-apple-system', 'BlinkMacSystemFont', 'Inter', sans-serif";
