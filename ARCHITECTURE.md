
# 🏗️ TRADING BOT PLATFORM - ПЪЛНА АРХИТЕКТУРА

**Версия:** 2.0  
**Дата:** Януари 2026  
**Статус:** Production Ready  

---

## 📋 СЪДЪРЖАНИЕ

1. [Общ Преглед](#общ-преглед)
2. [Технологии](#технологии)
3. [13-те Стратегии](#13-те-стратегии)
4. [Backend Файлове](#backend-файлове)
5. [Frontend Файлове](#frontend-файлове)
6. [Demo/Real Mode Система](#demoreal-mode-система)
7. [Feedback Система](#feedback-система)
8. [База Данни](#база-данни)
9. [Deployment](#deployment)
10. [Checklist](#checklist)

---

## 🎯 ОБЩ ПРЕГЛЕД

### Мисия
Демократизиране на алгоритмичната търговия за начинаещи с малък капитал ($50-$500).

### Основни Функции
- ✅ 13 автоматизирани стратегии
- ✅ Demo Mode (безплатно, неограничено)
- ✅ Real Mode ($5/месец)
- ✅ Switch с едно копче
- ✅ 10 езика
- ✅ PWA мобилно приложение
- ✅ Telegram сигнали
- ✅ Автоматично хващане на грешки

### Целева Аудитория
- 👤 Начинаещи в крипто
- 💰 Малък капитал ($50-$500)
- ⏰ Нямат време за ръчна търговия
- 📚 Искат да учат чрез практика

---

## 💻 ТЕХНОЛОГИИ

### Backend
Език:           Python 3.11+
Framework:      FastAPI
База данни:     SQLite → PostgreSQL (по-късно)
ORM:            SQLAlchemy
Web Server:     Uvicorn + Nginx
Плащания:       Stripe
Известия:       Telegram Bot API
### Frontend
Език:           TypeScript
Framework:      React 18+
Build Tool:     Vite
Стилове:        Tailwind CSS
Графики:        Recharts
Мобилно:        PWA
### Борси
Spot:           KCEX
Futures:        Hyperliquid (Arbitrum)
DEX:            Uniswap V3
Сигнали:        Telegram API
---

## 🤖 13-ТЕ СТРАТЕГИИ

### Класификация
🟢 ЗА НАЧИНАЕЩИ (5 стратегии)
├─ Grid Bot ⭐⭐⭐⭐⭐
├─ DCA Bot ⭐⭐⭐⭐⭐
├─ Signal Grid Bot ⭐⭐⭐⭐ (НОВА!)
├─ Portfolio Bot ⭐⭐⭐⭐
└─ Trailing Stop Bot ⭐⭐⭐⭐
🟡 СРЕДНО (4 стратегии)
├─ Futures Bot ⭐⭐⭐
├─ Mean Reversion Bot ⭐⭐⭐
├─ Turtle Strategy ⭐⭐⭐
└─ Liquidity Strategy ⭐⭐⭐
🔴 НАПРЕДНАЛИ (4 стратегии)
├─ ICT Strategy 🔥 ⭐⭐⭐
├─ Aggressive Scalper 🔥 ⭐⭐⭐
├─ Trend Master 🔥 ⭐⭐⭐
└─ DEX Arbitrage 🔥 ⭐⭐⭐
### Таблица със Стратегии

| Стратегия | Файл | Борса | Капитал | ROI/М | Win% |
|-----------|------|-------|---------|-------|------|
| Grid | grid_bot.py | KCEX | $100 | 5-15% | 60-70% |
| DCA | dca_bot.py | KCEX | $50 | Market | 70%+ |
| Signal Grid | signal_grid_bot.py | Hyper | $200 | 10-25% | 60-70% |
| Portfolio | portfolio_bot.py | KCEX | $300 | Market | N/A |
| Trailing | trailing_bot.py | KCEX | $100 | Trend | 50-60% |
| Futures | futures_bot.py | Hyper | $300 | 15-40% | 50-60% |
| Mean Rev | mean_reversion_bot.py | KCEX | $200 | 8-15% | 55-65% |
| Turtle | turtle_strategy.py | KCEX | $500 | 20-50%/y | 40-50% |
| Liquidity | liquidity_strategy.py | Hyper | $500 | 15-30% | 55-65% |
| ICT | ict_strategy.py | Both | $500 | 20-50% | 60-70%* |
| Scalper | aggressive_scalper_bot.py | Hyper | $500 | 20-60% | 45-55% |
| Trend | trend_master_bot.py | KCEX | $300 | 15-40% | 50-60% |
| Arbitrage | dex_arbitrage_strategy.py | Uni+Hyper | $1000 | 5-15% | 70-80%* |

*с опит

---

## 📁 СТРУКТУРА НА ПРОЕКТА

### Backend Папки
backend/
├── main.py
├── config.py
├── database.py (ОБНОВЕН)
├── .env.example (ОБНОВЕН)
│
├── core/
│   ├── bot_manager.py (ОБНОВЕН)
│   ├── unified_strategy_manager.py (ОБНОВЕН)
│   ├── demo_mode.py (НОВ)
│   ├── risk_manager.py
│   └── exchange_api.py
│
├── strategies/
│   ├── signal_grid_bot.py (НОВ)
│   ├── ict_strategy.py
│   ├── grid_bot.py
│   ├── dca_bot.py
│   ├── portfolio_bot.py
│   ├── trailing_bot.py
│   ├── futures_bot.py
│   ├── mean_reversion_bot.py
│   ├── turtle_strategy.py
│   ├── liquidity_strategy.py
│   ├── aggressive_scalper_bot.py
│   ├── trend_master_bot.py
│   └── dex_arbitrage_strategy.py
│
├── integrations/
│   ├── telegram_signal_listener.py (НОВ)
│   ├── telegram_alerts.py (НОВ)
│   ├── email_service.py
│   └── payment_service.py
│
├── feedback/
│   ├── feedback_system.py (НОВ)
│   ├── bug_tracker.py (НОВ)
│   └── user_communication.py (НОВ)
│
├── api/
│   ├── api_routers.py
│   └── auth.py
│
└── utils/
├── analyzer.py
├── formatter.py
└── translations.py (ОБНОВЕН)
### Frontend Папки
frontend/
├── public/
│   ├── manifest.json (НОВ)
│   ├── service-worker.js (НОВ)
│   └── icons/
│
├── src/
│   ├── App.tsx
│   ├── main.tsx
│   │
│   ├── pages/
│   │   ├── Dashboard.tsx
│   │   ├── BotSelector.tsx (ОБНОВЕН)
│   │   ├── AdminDashboard.tsx (НОВ)
│   │   └── Onboarding.tsx (ОБНОВЕН)
│   │
│   ├── components/
│   │   ├── bots/
│   │   │   ├── DemoRealToggle.tsx (НОВ)
│   │   │   ├── SignalGridConfig.tsx (НОВ)
│   │   │   └── ICTWarningModal.tsx (НОВ)
│   │   │
│   │   ├── feedback/
│   │   │   ├── FeedbackWidget.tsx (НОВ)
│   │   │   └── FeedbackForm.tsx (НОВ)
│   │   │
│   │   └── admin/
│   │       ├── ErrorLogTable.tsx (НОВ)
│   │       ├── ErrorDetails.tsx (НОВ)
│   │       └── FeedbackInbox.tsx (НОВ)
│   │
│   └── utils/
│       └── translations.ts (ОБНОВЕН)
---

## 🔄 DEMO/REAL MODE

### Как Работи
USER
↓
[DEMO] ←→ [REAL]
↓         ↓
Virtual   Real API
$10,000   User's $
### Demo Mode
- ✅ $10,000 виртуални
- ✅ Реални цени
- ✅ Всички стратегии
- ✅ Неограничено време
- ✅ Без API keys

### Real Mode
- ✅ Реални пари
- ✅ $5/месец
- ✅ Реални борси
- ✅ Реални печалби

---

## 📢 FEEDBACK СИСТЕМА

### 3 Канала

**1. Автоматични Грешки**
Error → DB + Telegram alert до теб
**2. Admin Dashboard**
/admin/dashboard
Списък грешки
Статистика
Търсене
**3. User Feedback**
"Report Problem" бутон
→ Форма
→ Telegram до теб
---

## 💾 НОВИ ТАБЛИЦИ

```sql
-- Telegram Сигнали
CREATE TABLE telegram_signals (
    signal_id INTEGER PRIMARY KEY,
    channel_name TEXT,
    raw_text TEXT,
    parsed_symbol TEXT,
    parsed_direction TEXT,
    timestamp DATETIME
);

-- Demo Портфейли
CREATE TABLE demo_portfolios (
    portfolio_id INTEGER PRIMARY KEY,
    user_id TEXT,
    balance_usdt REAL DEFAULT 10000,
    positions TEXT,
    trades TEXT,
    total_pnl REAL DEFAULT 0
);

-- Грешки
CREATE TABLE error_logs (
    error_id INTEGER PRIMARY KEY,
    user_id TEXT,
    bot_type TEXT,
    error_message TEXT,
    stack_trace TEXT,
    severity TEXT,
    status TEXT DEFAULT 'open',
    timestamp DATETIME
);

-- User Feedback
CREATE TABLE user_feedback (
    feedback_id INTEGER PRIMARY KEY,
    user_id TEXT,
    type TEXT,
    message TEXT,
    screenshot_url TEXT,
    status TEXT DEFAULT 'open',
    timestamp DATETIME
);

-- Добавки към users
ALTER TABLE users ADD COLUMN mode TEXT DEFAULT 'demo';
ALTER TABLE users ADD COLUMN real_mode_activated_at DATETIME;
✅ CHECKLIST
Backend
[ ] Добави нови таблици в database.py
[ ] Обнови bot_manager.py (Signal Grid)
[ ] Създай demo_mode.py
[ ] Създай telegram_signal_listener.py
[ ] Създай telegram_alerts.py
[ ] Създай feedback_system.py
[ ] Обнови .env.example (Telegram keys)
Frontend
[ ] Създай DemoRealToggle.tsx
[ ] Създай SignalGridConfig.tsx
[ ] Създай ICTWarningModal.tsx
[ ] Създай FeedbackWidget.tsx
[ ] Обнови BotSelector.tsx
[ ] Създай AdminDashboard.tsx
[ ] Създай manifest.json (PWA)
Deployment
[ ] docker-compose.yml
[ ] nginx.conf
[ ] deploy.sh
[ ] Telegram bot setup
[ ] Stripe setup
🗓️ ФАЗИ
Фаза 1 (Седм 1-2): Core integration
Фаза 2 (Седм 3-4): Frontend & UX
Фаза 3 (Седм 5-6): Testing
Фаза 4 (Мес 2-3): Closed Beta
Фаза 5 (Мес 4-5): Open Beta
Фаза 6 (Мес 6+): Launch
🎯 МЕТРИКИ
Beta: 100 demo users, 20 paid
Launch: 1000 users, 100 paid ($500/м)
Scale: 10k users, 1k paid ($5k/м)
