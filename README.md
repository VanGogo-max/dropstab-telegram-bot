# 🤖 CryptoTradeBot Pro

Професионална платформа за автоматизирана търговия с криптовалути, изградена с React и TypeScript.

## 📋 Съдържание

- [Описание](#описание)
- [Възможности](#възможности)
- [Технологии](#технологии)
- [Инсталация](#инсталация)
- [Стартиране](#стартиране)
- [Структура на проекта](#структура-на-проекта)
- [Скриптове](#скриптове)
- [Конфигурация](#конфигурация)

## 📖 Описание

CryptoTradeBot Pro е модерно уеб приложение за търговия с криптовалути, което предлага автоматизирани стратегии, реално време анализ и интуитивен потребителски интерфейс.

## ✨ Възможности

- 📊 **Реално време данни** - Проследяване на цени и обеми на криптовалути
- 🤖 **Автоматизирана търговия** - Интелигентни ботове с настройваеми стратегии
- 📈 **Визуализация на данни** - Интерактивни графики и диаграми
- 💼 **Управление на портфейл** - Преглед на активи, печалби и загуби
- 🔔 **Известия** - Уведомления за важни събития и сделки
- 📱 **Отзивчив дизайн** - Работи перфектно на всички устройства
- 🎨 **Модерен UI** - Красив интерфейс с плавни анимации

## 🛠 Технологии

### Core
- **React 18.2** - UI библиотека
- **TypeScript 5.3** - Типизиран JavaScript
- **Vite 5.0** - Бърз build tool

### State Management
- **Zustand 4.4** - Лек state management
- **TanStack Query 5.8** - Server state management

### Styling & UI
- **TailwindCSS 3.3** - Utility-first CSS framework
- **Framer Motion 10.16** - Анимации
- **Lucide React 0.294** - Икони

### Data & API
- **Axios 1.6** - HTTP клиент
- **Recharts 2.10** - Графики и диаграми
- **date-fns 2.30** - Работа с дати

### Routing & Notifications
- **React Router 6.20** - Навигация
- **React Hot Toast 2.4** - Toast notifications

## 📦 Инсталация

### Изисквания
- Node.js (v16 или по-нова версия)
- npm или yarn

### Стъпки

1. **Клонирайте репозиторито**
```bash
git clone https://github.com/yourusername/cryptotradebot-frontend.git
cd cryptotradebot-frontend
```

2. **Инсталирайте зависимости**
```bash
npm install
```

3. **Конфигурирайте environment variables**
Създайте `.env` файл в root директорията:
```env
VITE_API_URL=http://localhost:3000/api
VITE_WS_URL=ws://localhost:3000
```

## 🚀 Стартиране

### Development режим
```bash
npm run dev
```
Приложението ще стартира на `http://localhost:5173`

### Production build
```bash
npm run build
```

### Preview на production build
```bash
npm run preview
```

### Lint проверка
```bash
npm run lint
```

## 📁 Структура на проекта

```
cryptotradebot-frontend/
├── public/              # Статични файлове
├── src/
│   ├── components/      # React компоненти
│   │   ├── common/      # Преизползваеми компоненти
│   │   ├── dashboard/   # Dashboard компоненти
│   │   ├── trading/     # Търговски компоненти
│   │   └── charts/      # Графики и визуализации
│   ├── hooks/           # Custom React hooks
│   ├── pages/           # Страници (routes)
│   ├── store/           # Zustand stores
│   ├── services/        # API services
│   ├── utils/           # Utility функции
│   ├── types/           # TypeScript типове
│   ├── styles/          # Глобални стилове
│   ├── App.tsx          # Main App компонент
│   └── main.tsx         # Entry point
├── package.json
├── tsconfig.json
├── vite.config.ts
├── tailwind.config.js
└── README.md
```

## 📜 Скриптове

| Команда | Описание |
|---------|----------|
| `npm run dev` | Стартира development сървър |
| `npm run build` | Създава production build |
| `npm run preview` | Preview на production build |
| `npm run lint` | Проверява кода за грешки |

## ⚙️ Конфигурация

### Vite
Конфигурацията на Vite се намира в `vite.config.ts`

### TailwindCSS
Конфигурацията на Tailwind се намира в `tailwind.config.js`

### TypeScript
TypeScript конфигурацията се намира в `tsconfig.json`

## 🔧 Development

### Добавяне на нов компонент
```bash
# Създайте нов файл в src/components/
src/components/MyComponent.tsx
```

### Добавяне на нова страница
```bash
# Създайте нов файл в src/pages/
src/pages/MyPage.tsx

# Добавете route в App.tsx
```

### Работа със state
- Използвайте **Zustand** за глобално състояние
- Използвайте **TanStack Query** за сървърни данни
- Използвайте **useState** за локално състояние в компонент

## 🎨 Styling Guidelines

- Използвайте TailwindCSS utility classes
- Избягвайте inline styles
- Следвайте mobile-first подход
- Използвайте съществуващата цветова палитра

## 📱 Browser Support

- Chrome (последни 2 версии)
- Firefox (последни 2 версии)
- Safari (последни 2 версии)
- Edge (последни 2 версии)

## 🤝 Contributing

Contributions са добре дошли! Моля следвайте тези стъпки:

1. Fork проекта
2. Създайте feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit промените (`git commit -m 'Add some AmazingFeature'`)
4. Push към branch (`git push origin feature/AmazingFeature`)
5. Отворете Pull Request

## 📄 License

Този проект е licensed под MIT License.

## 👨‍💻 Author

Вашето име - [@yourhandle](https://twitter.com/yourhandle)

## 🙏 Acknowledgments

- React Team за страхотната библиотека
- Anthropic за Claude AI assistance
- Всички open-source contributors

---

**Note:** Това е frontend приложение. За пълна функционалност се изисква backend API сървър.

Направено с ❤️ и ☕
