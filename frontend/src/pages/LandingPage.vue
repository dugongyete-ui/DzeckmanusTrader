<template>
  <div class="page" :class="{ dark: theme === 'dark', 'is-loaded': isLoaded }">

    <!-- Navbar -->
    <nav class="nav">
      <div class="nav-inner">
        <a href="/" class="nav-logo">
          <Bot :size="22" />
          <span class="nav-logo-text">Dzeck</span>
        </a>
        <div class="nav-right">
          <button @click="toggleTheme" class="icon-btn" :title="theme === 'dark' ? 'Light mode' : 'Dark mode'">
            <Sun v-if="theme === 'dark'" :size="16" />
            <Moon v-else :size="16" />
          </button>
          <a href="/login" class="btn-secondary">Sign in</a>
          <a href="/login" class="btn-primary">Sign up</a>
        </div>
      </div>
    </nav>

    <!-- Main -->
    <main class="main">
      <div class="hero-section">
        <h1 class="headline fade-up-1">Command your analytical edge.</h1>
        <p class="sub-headline fade-up-2">Autonomous market intelligence. No fixed rules. Just adaptive reasoning across Forex, Crypto, Gold, and Stocks.</p>
      </div>

      <!-- Input box -->
      <div class="input-wrap fade-up-3">
        <div class="input-box" :class="{ focused: isFocused }">
          <textarea
            ref="textareaRef"
            v-model="message"
            class="input-textarea"
            placeholder="Command Dzeck to analyze a market or asset..."
            rows="1"
            @focus="isFocused = true"
            @blur="isFocused = false"
            @input="autoResize"
            @keydown.enter.exact.prevent="handleSend"
          />
          <div class="input-actions">
            <button class="attach-btn" title="Attach context">
              <Plus :size="18" />
            </button>
            <button
              class="send-btn"
              :class="{ active: message.trim().length > 0 }"
              @click="handleSend"
              title="Send Command"
            >
              <ArrowUp :size="16" />
            </button>
          </div>
        </div>
      </div>

      <!-- Suggestion pills -->
      <div class="suggestions fade-up-4">
        <button
          v-for="sug in suggestions"
          :key="sug.id"
          class="suggestion-pill"
          @click="selectSuggestion(sug)"
        >
          <component :is="sug.icon" :size="14" class="pill-icon" />
          {{ sug.label }}
        </button>
      </div>
    </main>

  </div>
</template>

<script setup lang="ts">
import { ref, nextTick, markRaw, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import {
  Bot, Sun, Moon, Plus, ArrowUp, X,
  TrendingUp, TrendingDown, BarChart2, Activity, Search, Globe, Clock, Calendar, Zap, Target
} from 'lucide-vue-next'
import { useTheme } from '@/composables/useTheme'

const { theme, toggleTheme } = useTheme()
const router = useRouter()

const message = ref('')
const isFocused = ref(false)
const textareaRef = ref<HTMLTextAreaElement | null>(null)
const isLoaded = ref(false)

onMounted(() => {
  setTimeout(() => {
    isLoaded.value = true
  }, 50)
})

interface Suggestion {
  id: string
  label: string
  icon: any
  prompt: string
}

const suggestions: Suggestion[] = [
  { id: 'xauusd', label: 'Cari entry XAUUSD sekarang', icon: markRaw(Target), prompt: 'Cari entry XAUUSD sekarang' },
  { id: 'btc', label: 'Scan momentum BTC', icon: markRaw(Zap), prompt: 'Scan momentum BTC' },
  { id: 'eurusd', label: 'Analisa EURUSD multi-timeframe', icon: markRaw(BarChart2), prompt: 'Analisa EURUSD multi-timeframe' },
  { id: 'calendar', label: 'Cek economic calendar', icon: markRaw(Calendar), prompt: 'Cek economic calendar hari ini dan dampaknya' },
  { id: 'gbpusd', label: 'Posisi terbaik GBPUSD', icon: markRaw(Activity), prompt: 'Posisi terbaik GBPUSD hari ini' },
]

const autoResize = () => {
  const el = textareaRef.value
  if (!el) return
  el.style.height = 'auto'
  el.style.height = Math.min(el.scrollHeight, 200) + 'px'
}

const selectSuggestion = async (sug: Suggestion) => {
  message.value = sug.prompt
  await nextTick()
  autoResize()
  textareaRef.value?.focus()
  const end = message.value.length
  textareaRef.value?.setSelectionRange(end, end)
}

const PENDING_KEY = 'dzeck_pending_prompt'

const handleSend = () => {
  if (!message.value.trim()) return
  localStorage.setItem(PENDING_KEY, message.value.trim())
  router.push('/login')
}
</script>

<style scoped>
.page {
  min-height: 100vh;
  background: var(--background-gray-main);
  color: var(--text-primary);
  display: flex;
  flex-direction: column;
  font-family: ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
  overflow-x: hidden;
}

/* Animations */
.fade-up-1, .fade-up-2, .fade-up-3, .fade-up-4 {
  opacity: 0;
  transform: translateY(20px);
  transition: opacity 0.8s cubic-bezier(0.16, 1, 0.3, 1), transform 0.8s cubic-bezier(0.16, 1, 0.3, 1);
}

.is-loaded .fade-up-1 { opacity: 1; transform: translateY(0); transition-delay: 0.1s; }
.is-loaded .fade-up-2 { opacity: 1; transform: translateY(0); transition-delay: 0.2s; }
.is-loaded .fade-up-3 { opacity: 1; transform: translateY(0); transition-delay: 0.3s; }
.is-loaded .fade-up-4 { opacity: 1; transform: translateY(0); transition-delay: 0.4s; }

/* ── Navbar ── */
.nav {
  position: sticky;
  top: 0;
  z-index: 50;
  background: var(--background-gray-main);
  border-bottom: 1px solid var(--border-light);
}
.nav-inner {
  max-width: 1100px;
  margin: 0 auto;
  padding: 0 20px;
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.nav-logo {
  display: flex;
  align-items: center;
  gap: 8px;
  text-decoration: none;
  color: var(--text-primary);
  transition: opacity 0.2s;
}
.nav-logo:hover {
  opacity: 0.8;
}
.nav-logo-text {
  font-size: 16px;
  font-weight: 600;
  letter-spacing: -0.02em;
  color: var(--text-primary);
  text-transform: uppercase;
}
.nav-right { display: flex; align-items: center; gap: 12px; }

.icon-btn {
  display: flex; align-items: center; justify-content: center;
  width: 32px; height: 32px; border-radius: 6px;
  border: 1px solid transparent; background: transparent;
  color: var(--text-secondary); cursor: pointer;
  transition: all 0.2s;
}
.icon-btn:hover { background: var(--fill-tsp-white-main); border-color: var(--border-main); color: var(--text-primary); }

.btn-primary {
  padding: 8px 18px; border-radius: 6px;
  background: var(--text-primary); color: var(--background-gray-main);
  font-size: 13px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.04em;
  text-decoration: none; border: 1px solid var(--text-primary); cursor: pointer;
  transition: all 0.2s;
}
.btn-primary:hover { background: transparent; color: var(--text-primary); }

.btn-secondary {
  padding: 8px 18px; border-radius: 6px; background: transparent;
  color: var(--text-secondary); font-size: 13px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.04em;
  text-decoration: none; border: 1px solid var(--border-btn-main); cursor: pointer;
  transition: all 0.2s;
}
.btn-secondary:hover { color: var(--text-primary); border-color: var(--text-primary); background: var(--fill-tsp-white-main); }

/* ── Main ── */
.main {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px 120px;
  position: relative;
}

.hero-section {
  text-align: center;
  margin-bottom: 40px;
  max-width: 700px;
}

.headline {
  font-size: clamp(32px, 5vw, 48px);
  font-weight: 500;
  letter-spacing: -0.03em;
  color: var(--text-primary);
  margin: 0 0 16px;
  line-height: 1.1;
}

.sub-headline {
  font-size: clamp(15px, 2vw, 18px);
  font-weight: 400;
  color: var(--text-secondary);
  line-height: 1.5;
  margin: 0 auto;
  max-width: 560px;
}

/* ── Input wrap + box ── */
.input-wrap {
  width: 100%;
  max-width: 720px;
  margin-bottom: 24px;
}

.input-box {
  background: var(--background-card);
  border: 1px solid var(--border-dark);
  border-radius: 12px;
  padding: 16px 16px 12px 20px;
  cursor: text;
  box-shadow: 0 4px 20px var(--shadow-XS);
  transition: box-shadow 0.2s, border-color 0.2s;
}
.input-box:hover { border-color: var(--text-tertiary); }
.input-box.focused { border-color: var(--text-primary); box-shadow: 0 4px 24px var(--shadow-S); }

.input-textarea {
  width: 100%;
  min-height: 24px;
  max-height: 240px;
  background: transparent;
  border: none; outline: none; resize: none;
  font-size: 16px; line-height: 1.5;
  color: var(--text-primary); font-family: inherit;
  margin-bottom: 12px;
  overflow-y: auto;
}
.input-textarea::placeholder { color: var(--text-disable); font-weight: 400; }

.input-actions {
  display: flex; align-items: center; justify-content: space-between;
}
.attach-btn {
  display: flex; align-items: center; justify-content: center;
  width: 32px; height: 32px; border-radius: 6px;
  border: 1px solid var(--border-btn-main);
  background: transparent; color: var(--text-secondary); cursor: pointer;
  transition: all 0.2s;
}
.attach-btn:hover { background: var(--fill-tsp-white-main); color: var(--text-primary); border-color: var(--text-tertiary); }

.send-btn {
  display: flex; align-items: center; justify-content: center;
  width: 32px; height: 32px; border-radius: 6px;
  border: 1px solid transparent; background: var(--background-gray-main);
  color: var(--text-disable); cursor: pointer;
  transition: all 0.2s;
}
.send-btn.active { background: var(--text-primary); color: var(--background-gray-main); border-color: var(--text-primary); }
.send-btn.active:hover { opacity: 0.9; transform: translateY(-1px); }

/* ── Suggestion pills ── */
.suggestions {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  justify-content: center;
  max-width: 760px;
}
.suggestion-pill {
  display: inline-flex; align-items: center; gap: 8px;
  padding: 8px 16px; border-radius: 6px;
  border: 1px solid var(--border-btn-main);
  background: var(--background-card);
  color: var(--text-secondary);
  font-size: 13px; font-weight: 500; cursor: pointer;
  transition: all 0.2s;
}
.pill-icon {
  color: var(--text-tertiary);
  transition: color 0.2s;
}
.suggestion-pill:hover { background: var(--background-gray-main); color: var(--text-primary); border-color: var(--text-tertiary); }
.suggestion-pill:hover .pill-icon { color: var(--text-primary); }

/* ── Responsive ── */
@media (max-width: 600px) {
  .headline { font-size: 28px; }
  .nav-right .btn-secondary { display: none; }
  .main { padding: 40px 16px 80px; }
  .suggestion-pill { font-size: 12px; padding: 7px 12px; }
}
</style>
