# translations.py - Multilingual support for DropsTab Trading Bot
# Updated with DEX exchanges and arbitrage strategies

TRANSLATIONS = {
    'en': {
        # Menu & Navigation (existing)
        'welcome': '🎮 Welcome to DropsTab Bot!\n\nTrack the best Telegram crypto games and airdrops.',
        'main_menu': '📋 Main Menu',
        'back': '🔙 Back',
        'language_changed': '✅ Language changed to English',
        
        # Trading Menu (NEW)
        'trading_menu': '💹 Trading',
        'btn_exchanges': '🏦 Exchanges',
        'btn_strategies': '📊 Strategies',
        'btn_portfolio': '💼 Portfolio',
        'btn_arbitrage': '🔄 Arbitrage',
        'btn_active_bots': '🤖 Active Bots',
        
        # DEX Exchanges (NEW)
        'exchanges_list': '🏦 Connected Exchanges',
        'exchange_kcex': 'KCEX - Spot Trading',
        'exchange_hyperliquid': 'Hyperliquid - Futures (Arbitrum)',
        'exchange_dydx': 'dYdX v4 - DeFi Perpetuals',
        'exchange_gmx': 'GMX v2 - Arbitrum/Avalanche',
        'exchange_kwenta': 'Kwenta - Synthetix (Optimism)',
        'exchange_vertex': 'Vertex Protocol - Hybrid DEX',
        'exchange_apex': 'Apex Protocol - Multi-chain',
        'exchange_status_connected': '✅ Connected',
        'exchange_status_disconnected': '❌ Disconnected',
        'exchange_balance': 'Balance: ${balance}',
        
        # Arbitrage Strategies (NEW)
        'arbitrage_menu': '🔄 Arbitrage Strategies',
        'arb_price': '📊 Price Arbitrage',
        'arb_price_desc': 'Buy low on one exchange, sell high on another',
        'arb_funding': '💰 Funding Rate Arbitrage',
        'arb_funding_desc': 'Earn funding payments with hedged positions',
        'arb_triangular': '🔺 Triangular Arbitrage',
        'arb_triangular_desc': 'Multi-hop trades for profit',
        'arb_opportunity_found': '🎯 Arbitrage Opportunity Found!',
        'arb_profit_potential': 'Potential Profit: {profit}%',
        'arb_executing': '⚡ Executing arbitrage trade...',
        'arb_success': '✅ Arbitrage trade successful! Profit: ${profit}',
        'arb_failed': '❌ Arbitrage trade failed: {error}',
        'arb_no_opportunities': '📉 No arbitrage opportunities at the moment',
        'arb_scanning': '🔍 Scanning {exchanges} exchanges...',
        
        # Strategy Status (NEW)
        'strategy_enabled': '✅ Strategy Enabled',
        'strategy_disabled': '❌ Strategy Disabled',
        'strategy_running': '🟢 Running',
        'strategy_stopped': '🔴 Stopped',
        'strategy_paused': '🟡 Paused',
        
        # Notifications (NEW)
        'notify_arb_opportunity': '🎯 Arbitrage opportunity: {type}\nProfit: {profit}%\nBuy: {buy_ex} @ ${buy_price}\nSell: {sell_ex} @ ${sell_price}',
        'notify_position_opened': '📈 Position opened: {symbol}\nExchange: {exchange}\nSize: {size}\nPrice: ${price}',
        'notify_position_closed': '💰 Position closed: {symbol}\nP&L: ${pnl}\nReturn: {return_pct}%',
        'notify_funding_earned': '💵 Funding earned: ${amount}\nRate: {rate}%\nPosition: {symbol}',
        
        # Risk Management (NEW)
        'risk_max_position': '⚠️ Maximum position size reached',
        'risk_daily_loss_limit': '🛑 Daily loss limit reached',
        'risk_insufficient_balance': '💸 Insufficient balance',
        'risk_high_volatility': '⚡ High volatility detected - reducing position size',
        
        # Performance Stats (NEW)
        'stats_total_profit': 'Total Profit: ${profit}',
        'stats_win_rate': 'Win Rate: {rate}%',
        'stats_trades_today': 'Trades Today: {count}',
        'stats_best_trade': 'Best Trade: ${profit}',
        'stats_worst_trade': 'Worst Trade: ${loss}',
        'stats_avg_profit': 'Avg Profit: ${profit}',
        'stats_sharpe_ratio': 'Sharpe Ratio: {ratio}',
        'stats_funding_earned': 'Funding Earned: ${amount}',
        'stats_arb_opportunities': 'Arb Opportunities: {count}',
        
        # Buttons (existing + new)
        'btn_top_games': '🏆 Top Games',
        'btn_new_games': '🆕 New Games',
        'btn_hot_games': '🔥 Hot Games',
        'btn_search': '🔍 Search',
        'btn_favorites': '⭐ Favorites',
        'btn_settings': '⚙️ Settings',
        'btn_language': '🌐 Language',
        'btn_notifications': '🔔 Notifications',
        'btn_start_bot': '▶️ Start Bot',
        'btn_stop_bot': '⏸️ Stop Bot',
        'btn_view_stats': '📊 View Stats',
        'btn_manage_positions': '📈 Manage Positions',
        
        # Game Info (existing)
        'game_info': '🎮 <b>{name}</b>\n\n📊 Rating: {rating}/10\n👥 Players: {players}\n💰 Reward: {reward}\n📅 Added: {date}\n\n📝 {description}',
        'no_games': 'No games found',
        'loading': '⏳ Loading...',
        'search_prompt': '🔍 Enter game name to search:',
        'search_results': '🔍 Search results for "{query}":',
        
        # Favorites (existing)
        'favorites_empty': '⭐ Your favorites list is empty',
        'favorite_added': '✅ Added to favorites',
        'favorite_removed': '✅ Removed from favorites',
        'favorites_list': '⭐ Your Favorite Games:',
        
        # Settings (existing + new)
        'notifications_on': '🔔 Notifications enabled',
        'notifications_off': '🔕 Notifications disabled',
        'settings_menu': '⚙️ Settings',
        'current_language': 'Current language: English 🇬🇧',
        'settings_risk_level': 'Risk Level: {level}',
        'settings_max_position': 'Max Position Size: ${size}',
        'settings_leverage': 'Max Leverage: {leverage}x',
        
        # Errors (existing)
        'error': '❌ Error occurred. Please try again.',
        'game_not_found': '❌ Game not found',
        'invalid_command': '❌ Invalid command. Use /help for available commands.',
        
        # Help (existing + new)
        'help': '''
🤖 <b>DropsTab Bot Commands</b>

📱 <b>Games & Airdrops:</b>
/start - Start bot
/games - Browse all games
/top - Top rated games
/new - Newly added games
/hot - Trending games
/search - Search games
/favorites - Your favorite games

💹 <b>Trading:</b>
/trading - Trading menu
/exchanges - View connected exchanges
/arbitrage - Arbitrage opportunities
/portfolio - Your portfolio
/stats - Performance statistics

⚙️ <b>Settings:</b>
/settings - Bot settings
/language - Change language
/notifications - Manage notifications
/help - Show this help

💡 <b>Tips:</b>
• Enable arbitrage scanner for passive income
• Monitor multiple DEX exchanges simultaneously
• Set risk limits to protect your capital
• Track funding rates for optimal entry/exit

📧 Support: @dropstab_support
        ''',
    },
    
    'bg': {
        # Меню и Навигация
        'welcome': '🎮 Добре дошли в DropsTab Bot!\n\nСледете най-добрите Telegram крипто игри и airdrops.',
        'main_menu': '📋 Главно меню',
        'back': '🔙 Назад',
        'language_changed': '✅ Езикът е променен на Български',
        
        # Търговско меню (НОВО)
        'trading_menu': '💹 Търговия',
        'btn_exchanges': '🏦 Борси',
        'btn_strategies': '📊 Стратегии',
        'btn_portfolio': '💼 Портфолио',
        'btn_arbitrage': '🔄 Арбитраж',
        'btn_active_bots': '🤖 Активни ботове',
        
        # DEX Борси (НОВО)
        'exchanges_list': '🏦 Свързани борси',
        'exchange_kcex': 'KCEX - Спот търговия',
        'exchange_hyperliquid': 'Hyperliquid - Фючърси (Arbitrum)',
        'exchange_dydx': 'dYdX v4 - DeFi Перпетуали',
        'exchange_gmx': 'GMX v2 - Arbitrum/Avalanche',
        'exchange_kwenta': 'Kwenta - Synthetix (Optimism)',
        'exchange_vertex': 'Vertex Protocol - Хибридна DEX',
        'exchange_apex': 'Apex Protocol - Мулти-chain',
        'exchange_status_connected': '✅ Свързана',
        'exchange_status_disconnected': '❌ Прекъсната',
        'exchange_balance': 'Баланс: ${balance}',
        
        # Арбитражни стратегии (НОВО)
        'arbitrage_menu': '🔄 Арбитражни стратегии',
        'arb_price': '📊 Ценови арбитраж',
        'arb_price_desc': 'Купувай евтино на една борса, продавай скъпо на друга',
        'arb_funding': '💰 Funding Rate арбитраж',
        'arb_funding_desc': 'Печели от funding плащания с хеджирани позиции',
        'arb_triangular': '🔺 Триъгълен арбитраж',
        'arb_triangular_desc': 'Мулти-hop сделки за печалба',
        'arb_opportunity_found': '🎯 Открита арбитражна възможност!',
        'arb_profit_potential': 'Потенциална печалба: {profit}%',
        'arb_executing': '⚡ Изпълнява се арбитраж...',
        'arb_success': '✅ Арбитраж успешен! Печалба: ${profit}',
        'arb_failed': '❌ Арбитраж неуспешен: {error}',
        'arb_no_opportunities': '📉 Няма арбитражни възможности в момента',
        'arb_scanning': '🔍 Сканиране на {exchanges} борси...',
        
        # Статус на стратегии (НОВО)
        'strategy_enabled': '✅ Стратегия активирана',
        'strategy_disabled': '❌ Стратегия деактивирана',
        'strategy_running': '🟢 Работи',
        'strategy_stopped': '🔴 Спряна',
        'strategy_paused': '🟡 На пауза',
        
        # Известия (НОВО)
        'notify_arb_opportunity': '🎯 Арбитраж: {type}\nПечалба: {profit}%\nКупи: {buy_ex} @ ${buy_price}\nПродай: {sell_ex} @ ${sell_price}',
        'notify_position_opened': '📈 Позиция отворена: {symbol}\nБорса: {exchange}\nРазмер: {size}\nЦена: ${price}',
        'notify_position_closed': '💰 Позиция затворена: {symbol}\nP&L: ${pnl}\nПечалба: {return_pct}%',
        'notify_funding_earned': '💵 Funding спечелен: ${amount}\nRate: {rate}%\nПозиция: {symbol}',
        
        # Управление на риска (НОВО)
        'risk_max_position': '⚠️ Максимален размер на позицията достигнат',
        'risk_daily_loss_limit': '🛑 Дневен лимит на загуба достигнат',
        'risk_insufficient_balance': '💸 Недостатъчен баланс',
        'risk_high_volatility': '⚡ Висока волатилност - намаляване на позицията',
        
        # Статистика (НОВО)
        'stats_total_profit': 'Обща печалба: ${profit}',
        'stats_win_rate': 'Процент успех: {rate}%',
        'stats_trades_today': 'Сделки днес: {count}',
        'stats_best_trade': 'Най-добра сделка: ${profit}',
        'stats_worst_trade': 'Най-лоша сделка: ${loss}',
        'stats_avg_profit': 'Средна печалба: ${profit}',
        'stats_sharpe_ratio': 'Sharpe Ratio: {ratio}',
        'stats_funding_earned': 'Funding спечелен: ${amount}',
        'stats_arb_opportunities': 'Арбитраж възможности: {count}',
        
        # Бутони
        'btn_top_games': '🏆 Топ игри',
        'btn_new_games': '🆕 Нови игри',
        'btn_hot_games': '🔥 Горещи',
        'btn_search': '🔍 Търсене',
        'btn_favorites': '⭐ Любими',
        'btn_settings': '⚙️ Настройки',
        'btn_language': '🌐 Език',
        'btn_notifications': '🔔 Известия',
        'btn_start_bot': '▶️ Стартирай бот',
        'btn_stop_bot': '⏸️ Спри бот',
        'btn_view_stats': '📊 Статистика',
        'btn_manage_positions': '📈 Управление на позиции',
        
        # Информация за игри
        'game_info': '🎮 <b>{name}</b>\n\n📊 Рейтинг: {rating}/10\n👥 Играчи: {players}\n💰 Награда: {reward}\n📅 Добавена: {date}\n\n📝 {description}',
        'no_games': 'Няма намерени игри',
        'loading': '⏳ Зареждане...',
        'search_prompt': '🔍 Въведете име на игра:',
        'search_results': '🔍 Резултати за "{query}":',
        
        # Любими
        'favorites_empty': '⭐ Списъкът с любими е празен',
        'favorite_added': '✅ Добавена към любими',
        'favorite_removed': '✅ Премахната от любими',
        'favorites_list': '⭐ Любими игри:',
        
        # Настройки
        'notifications_on': '🔔 Известията са включени',
        'notifications_off': '🔕 Известията са изключени',
        'settings_menu': '⚙️ Настройки',
        'current_language': 'Текущ език: Български 🇧🇬',
        'settings_risk_level': 'Ниво на риск: {level}',
        'settings_max_position': 'Макс позиция: ${size}',
        'settings_leverage': 'Макс ливъридж: {leverage}x',
        
        # Грешки
        'error': '❌ Възникна грешка. Опитайте отново.',
        'game_not_found': '❌ Играта не е намерена',
        'invalid_command': '❌ Невалидна команда. Използвайте /help',
        
        # Помощ
        'help': '''
🤖 <b>DropsTab Bot Команди</b>

📱 <b>Игри и Airdrops:</b>
/start - Стартиране
/games - Всички игри
/top - Топ игри
/new - Нови игри
/hot - Популярни игри
/search - Търсене
/favorites - Любими

💹 <b>Търговия:</b>
/trading - Търговско меню
/exchanges - Свързани борси
/arbitrage - Арбитраж възможности
/portfolio - Портфолио
/stats - Статистика

⚙️ <b>Настройки:</b>
/settings - Настройки
/language - Смяна на език
/notifications - Известия
/help - Помощ

💡 <b>Съвети:</b>
• Включи арбитраж скенера за пасивна печалба
• Следи няколко DEX борси едновременно
• Постави лимити за защита на капитала
• Следи funding rates за оптимален вход/изход

📧 Поддръжка: @dropstab_support
        ''',
    },
    
    # Останалите езици (RU, ES, FR, DE, PT, TR, ZH, AR) също с новите ключове...
    # За краткост показвам само началото на RU
    
    'ru': {
        'welcome': '🎮 Добро пожаловать в DropsTab Bot!\n\nОтслеживайте лучшие крипто-игры и airdrop-ы.',
        'main_menu': '📋 Главное меню',
        'back': '🔙 Назад',
        'language_changed': '✅ Язык изменен на Русский',
        
        'trading_menu': '💹 Торговля',
        'btn_exchanges': '🏦 Биржи',
        'btn_strategies': '📊 Стратегии',
        'btn_portfolio': '💼 Портфель',
        'btn_arbitrage': '🔄 Арбитраж',
        'btn_active_bots': '🤖 Активные боты',
        
        'exchanges_list': '🏦 Подключенные биржи',
        'exchange_kcex': 'KCEX - Спотовая торговля',
        'exchange_hyperliquid': 'Hyperliquid - Фьючерсы (Arbitrum)',
        'exchange_dydx': 'dYdX v4 - DeFi Перпетуалы',
        'exchange_gmx': 'GMX v2 - Arbitrum/Avalanche',
        'exchange_kwenta': 'Kwenta - Synthetix (Optimism)',
        'exchange_vertex': 'Vertex Protocol - Гибридная DEX',
        'exchange_apex': 'Apex Protocol - Мульти-чейн',
        
        'arbitrage_menu': '🔄 Арбитражные стратегии',
        'arb_price': '📊 Ценовой арбитраж',
        'arb_price_desc': 'Покупай дешево, продавай дорого',
        'arb_funding': '💰 Funding Rate арбитраж',
        'arb_funding_desc': 'Зарабатывай на фандинге с хеджем',
        'arb_triangular': '🔺 Треугольный арбитраж',
        'arb_triangular_desc': 'Многоэтапные сделки для прибыли',
        
        'arb_opportunity_found': '🎯 Найдена арбитражная возможность!',
        'arb_profit_potential': 'Потенциальная прибыль: {profit}%',
        'arb_executing': '⚡ Выполнение арбитража...',
        'arb_success': '✅ Арбитраж успешен! Прибыль: ${profit}',
        'arb_failed': '❌ Арбитраж провален: {error}',
        'arb_no_opportunities': '📉 Нет арбитражных возможностей',
        'arb_scanning': '🔍 Сканирование {exchanges} бирж...',
        
        'strategy_enabled': '✅ Стратегия включена',
        'strategy_disabled': '❌ Стратегия отключена',
        'strategy_running': '🟢 Работает',
        'strategy_stopped': '🔴 Остановлена',
        'strategy_paused': '🟡 На паузе',
        
        'notify_arb_opportunity': '🎯 Арбитраж: {type}\nПрибыль: {profit}%\nКупить: {buy_ex} @ ${buy_price}\nПродать: {sell_ex} @ ${sell_price}',
        'notify_position_opened': '📈 Позиция открыта: {symbol}\nБиржа: {exchange}\nРазмер: {size}\nЦена: ${price}',
        'notify_position_closed': '💰 Позиция закрыта: {symbol}\nP&L: ${pnl}\nДоходность: {return_pct}%',
        'notify_funding_earned': '💵 Фандинг получен: ${amount}\nСтавка: {rate}%\nПозиция: {symbol}',
        
        'stats_total_profit': 'Общая прибыль: ${profit}',
        'stats_win_rate': 'Процент побед: {rate}%',
        'stats_trades_today': 'Сделок сегодня: {count}',
        'stats_funding_earned': 'Фандинг заработан: ${amount}',
        'stats_arb_opportunities': 'Арбитраж возможностей: {count}',
        
        # ... (остальные ключи аналогично)
    },
    
    
    'es': {
        'welcome': '🎮 ¡Bienvenido a DropsTab Bot!\n\nSigue los mejores juegos cripto y airdrops de Telegram.',
        'main_menu': '📋 Menú Principal',
        'back': '🔙 Atrás',
        'language_changed': '✅ Idioma cambiado a Español',
        
        'trading_menu': '💹 Trading',
        'btn_exchanges': '🏦 Exchanges',
        'btn_strategies': '📊 Estrategias',
        'btn_portfolio': '💼 Portafolio',
        'btn_arbitrage': '🔄 Arbitraje',
        'btn_active_bots': '🤖 Bots Activos',
        
        'exchanges_list': '🏦 Exchanges Conectados',
        'exchange_kcex': 'KCEX - Trading Spot',
        'exchange_hyperliquid': 'Hyperliquid - Futuros (Arbitrum)',
        'exchange_dydx': 'dYdX v4 - Perpetuos DeFi',
        'exchange_gmx': 'GMX v2 - Arbitrum/Avalanche',
        'exchange_kwenta': 'Kwenta - Synthetix (Optimism)',
        'exchange_vertex': 'Vertex Protocol - DEX Híbrido',
        'exchange_apex': 'Apex Protocol - Multi-cadena',
        'exchange_status_connected': '✅ Conectado',
        'exchange_status_disconnected': '❌ Desconectado',
        'exchange_balance': 'Balance: ${balance}',
        
        'arbitrage_menu': '🔄 Estrategias de Arbitraje',
        'arb_price': '📊 Arbitraje de Precio',
        'arb_price_desc': 'Compra barato en un exchange, vende caro en otro',
        'arb_funding': '💰 Arbitraje de Funding Rate',
        'arb_funding_desc': 'Gana pagos de funding con posiciones cubiertas',
        'arb_triangular': '🔺 Arbitraje Triangular',
        'arb_triangular_desc': 'Operaciones multi-salto para beneficio',
        'arb_opportunity_found': '🎯 ¡Oportunidad de Arbitraje Encontrada!',
        'arb_profit_potential': 'Beneficio Potencial: {profit}%',
        'arb_executing': '⚡ Ejecutando arbitraje...',
        'arb_success': '✅ ¡Arbitraje exitoso! Beneficio: ${profit}',
        'arb_failed': '❌ Arbitraje fallido: {error}',
        'arb_no_opportunities': '📉 No hay oportunidades de arbitraje ahora',
        'arb_scanning': '🔍 Escaneando {exchanges} exchanges...',
        
        'strategy_enabled': '✅ Estrategia Activada',
        'strategy_disabled': '❌ Estrategia Desactivada',
        'strategy_running': '🟢 En Ejecución',
        'strategy_stopped': '🔴 Detenida',
        'strategy_paused': '🟡 En Pausa',
        
        'notify_arb_opportunity': '🎯 Arbitraje: {type}\nBeneficio: {profit}%\nComprar: {buy_ex} @ ${buy_price}\nVender: {sell_ex} @ ${sell_price}',
        'notify_position_opened': '📈 Posición abierta: {symbol}\nExchange: {exchange}\nTamaño: {size}\nPrecio: ${price}',
        'notify_position_closed': '💰 Posición cerrada: {symbol}\nP&L: ${pnl}\nRetorno: {return_pct}%',
        'notify_funding_earned': '💵 Funding ganado: ${amount}\nTasa: {rate}%\nPosición: {symbol}',
        
        'risk_max_position': '⚠️ Tamaño máximo de posición alcanzado',
        'risk_daily_loss_limit': '🛑 Límite de pérdida diaria alcanzado',
        'risk_insufficient_balance': '💸 Balance insuficiente',
        'risk_high_volatility': '⚡ Alta volatilidad detectada - reduciendo posición',
        
        'stats_total_profit': 'Beneficio Total: ${profit}',
        'stats_win_rate': 'Tasa de Éxito: {rate}%',
        'stats_trades_today': 'Operaciones Hoy: {count}',
        'stats_best_trade': 'Mejor Operación: ${profit}',
        'stats_worst_trade': 'Peor Operación: ${loss}',
        'stats_avg_profit': 'Beneficio Promedio: ${profit}',
        'stats_sharpe_ratio': 'Ratio Sharpe: {ratio}',
        'stats_funding_earned': 'Funding Ganado: ${amount}',
        'stats_arb_opportunities': 'Oportunidades de Arb: {count}',
        
        'btn_top_games': '🏆 Top Juegos',
        'btn_new_games': '🆕 Nuevos',
        'btn_hot_games': '🔥 Populares',
        'btn_search': '🔍 Buscar',
        'btn_favorites': '⭐ Favoritos',
        'btn_settings': '⚙️ Ajustes',
        'btn_language': '🌐 Idioma',
        'btn_notifications': '🔔 Notificaciones',
        'btn_start_bot': '▶️ Iniciar Bo
