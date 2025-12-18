# translations.py - Multilingual support for DropsTab Bot

TRANSLATIONS = {
    'en': {
        # Menu & Navigation
        'welcome': '🎮 Welcome to DropsTab Bot!\n\nTrack the best Telegram crypto games and airdrops.',
        'main_menu': '📋 Main Menu',
        'back': '🔙 Back',
        'language_changed': '✅ Language changed to English',
        
        # Buttons
        'btn_top_games': '🏆 Top Games',
        'btn_new_games': '🆕 New Games',
        'btn_hot_games': '🔥 Hot Games',
        'btn_search': '🔍 Search',
        'btn_favorites': '⭐ Favorites',
        'btn_settings': '⚙️ Settings',
        'btn_language': '🌐 Language',
        'btn_notifications': '🔔 Notifications',
        'btn_add_favorite': '⭐ Add to Favorites',
        'btn_remove_favorite': '❌ Remove from Favorites',
        'btn_open_game': '🎮 Open Game',
        'btn_share': '📤 Share',
        
        # Game Info
        'game_info': '🎮 <b>{name}</b>\n\n📊 Rating: {rating}/10\n👥 Players: {players}\n💰 Reward: {reward}\n📅 Added: {date}\n\n📝 {description}',
        'no_games': 'No games found',
        'loading': '⏳ Loading...',
        'search_prompt': '🔍 Enter game name to search:',
        'search_results': '🔍 Search results for "{query}":',
        
        # Favorites
        'favorites_empty': '⭐ Your favorites list is empty',
        'favorite_added': '✅ Added to favorites',
        'favorite_removed': '✅ Removed from favorites',
        'favorites_list': '⭐ Your Favorite Games:',
        
        # Notifications
        'notifications_on': '🔔 Notifications enabled',
        'notifications_off': '🔕 Notifications disabled',
        'notify_new_game': '🆕 New game available: {name}\n\n{description}\n\n🎮 Check it out now!',
        
        # Errors
        'error': '❌ Error occurred. Please try again.',
        'game_not_found': '❌ Game not found',
        'invalid_command': '❌ Invalid command. Use /help for available commands.',
        
        # Help
        'help': '''
🤖 <b>DropsTab Bot Commands</b>

/start - Start bot
/games - Browse all games
/top - Top rated games
/new - Newly added games
/hot - Trending games
/search - Search games
/favorites - Your favorite games
/settings - Bot settings
/language - Change language
/help - Show this help

💡 <b>Tips:</b>
• Add games to favorites for quick access
• Enable notifications for new games
• Share games with friends

📧 Support: @dropstab_support
        ''',
        
        # Settings
        'settings_menu': '⚙️ Settings',
        'current_language': 'Current language: English 🇬🇧',
    },
    
    'ru': {
        'welcome': '🎮 Добро пожаловать в DropsTab Bot!\n\nОтслеживайте лучшие крипто-игры и аирдропы в Telegram.',
        'main_menu': '📋 Главное меню',
        'back': '🔙 Назад',
        'language_changed': '✅ Язык изменен на Русский',
        
        'btn_top_games': '🏆 Топ игры',
        'btn_new_games': '🆕 Новые игры',
        'btn_hot_games': '🔥 Популярные',
        'btn_search': '🔍 Поиск',
        'btn_favorites': '⭐ Избранное',
        'btn_settings': '⚙️ Настройки',
        'btn_language': '🌐 Язык',
        'btn_notifications': '🔔 Уведомления',
        'btn_add_favorite': '⭐ В избранное',
        'btn_remove_favorite': '❌ Удалить из избранного',
        'btn_open_game': '🎮 Открыть игру',
        'btn_share': '📤 Поделиться',
        
        'game_info': '🎮 <b>{name}</b>\n\n📊 Рейтинг: {rating}/10\n👥 Игроков: {players}\n💰 Награда: {reward}\n📅 Добавлено: {date}\n\n📝 {description}',
        'no_games': 'Игры не найдены',
        'loading': '⏳ Загрузка...',
        'search_prompt': '🔍 Введите название игры:',
        'search_results': '🔍 Результаты поиска "{query}":',
        
        'favorites_empty': '⭐ Список избранного пуст',
        'favorite_added': '✅ Добавлено в избранное',
        'favorite_removed': '✅ Удалено из избранного',
        'favorites_list': '⭐ Ваши любимые игры:',
        
        'notifications_on': '🔔 Уведомления включены',
        'notifications_off': '🔕 Уведомления отключены',
        'notify_new_game': '🆕 Новая игра: {name}\n\n{description}\n\n🎮 Попробуйте сейчас!',
        
        'error': '❌ Произошла ошибка. Попробуйте снова.',
        'game_not_found': '❌ Игра не найдена',
        'invalid_command': '❌ Неверная команда. Используйте /help',
        
        'help': '''
🤖 <b>Команды DropsTab Bot</b>

/start - Запустить бота
/games - Все игры
/top - Топ игры
/new - Новые игры
/hot - Популярные игры
/search - Поиск игр
/favorites - Избранное
/settings - Настройки
/language - Сменить язык
/help - Помощь

💡 <b>Советы:</b>
• Добавляйте игры в избранное
• Включите уведомления о новых играх
• Делитесь играми с друзьями

📧 Поддержка: @dropstab_support
        ''',
        
        'settings_menu': '⚙️ Настройки',
        'current_language': 'Текущий язык: Русский 🇷🇺',
    },
    
    'es': {
        'welcome': '🎮 ¡Bienvenido a DropsTab Bot!\n\nSigue los mejores juegos cripto y airdrops de Telegram.',
        'main_menu': '📋 Menú Principal',
        'back': '🔙 Atrás',
        'language_changed': '✅ Idioma cambiado a Español',
        
        'btn_top_games': '🏆 Top Juegos',
        'btn_new_games': '🆕 Nuevos',
        'btn_hot_games': '🔥 Populares',
        'btn_search': '🔍 Buscar',
        'btn_favorites': '⭐ Favoritos',
        'btn_settings': '⚙️ Ajustes',
        'btn_language': '🌐 Idioma',
        'btn_notifications': '🔔 Notificaciones',
        'btn_add_favorite': '⭐ Añadir a Favoritos',
        'btn_remove_favorite': '❌ Quitar de Favoritos',
        'btn_open_game': '🎮 Abrir Juego',
        'btn_share': '📤 Compartir',
        
        'game_info': '🎮 <b>{name}</b>\n\n📊 Calificación: {rating}/10\n👥 Jugadores: {players}\n💰 Recompensa: {reward}\n📅 Añadido: {date}\n\n📝 {description}',
        'no_games': 'No se encontraron juegos',
        'loading': '⏳ Cargando...',
        'search_prompt': '🔍 Introduce el nombre del juego:',
        'search_results': '🔍 Resultados para "{query}":',
        
        'favorites_empty': '⭐ Tu lista de favoritos está vacía',
        'favorite_added': '✅ Añadido a favoritos',
        'favorite_removed': '✅ Eliminado de favoritos',
        'favorites_list': '⭐ Tus Juegos Favoritos:',
        
        'notifications_on': '🔔 Notificaciones activadas',
        'notifications_off': '🔕 Notificaciones desactivadas',
        'notify_new_game': '🆕 Nuevo juego: {name}\n\n{description}\n\n🎮 ¡Pruébalo ahora!',
        
        'error': '❌ Error. Inténtalo de nuevo.',
        'game_not_found': '❌ Juego no encontrado',
        'invalid_command': '❌ Comando inválido. Usa /help',
        
        'help': '''
🤖 <b>Comandos DropsTab Bot</b>

/start - Iniciar bot
/games - Todos los juegos
/top - Top juegos
/new - Juegos nuevos
/hot - Juegos populares
/search - Buscar juegos
/favorites - Favoritos
/settings - Ajustes
/language - Cambiar idioma
/help - Ayuda

💡 <b>Consejos:</b>
• Añade juegos a favoritos
• Activa notificaciones
• Comparte con amigos

📧 Soporte: @dropstab_support
        ''',
        
        'settings_menu': '⚙️ Ajustes',
        'current_language': 'Idioma actual: Español 🇪🇸',
    },
    
    'fr': {
        'welcome': '🎮 Bienvenue sur DropsTab Bot!\n\nSuivez les meilleurs jeux crypto et airdrops Telegram.',
        'main_menu': '📋 Menu Principal',
        'back': '🔙 Retour',
        'language_changed': '✅ Langue changée en Français',
        
        'btn_top_games': '🏆 Top Jeux',
        'btn_new_games': '🆕 Nouveaux',
        'btn_hot_games': '🔥 Populaires',
        'btn_search': '🔍 Rechercher',
        'btn_favorites': '⭐ Favoris',
        'btn_settings': '⚙️ Paramètres',
        'btn_language': '🌐 Langue',
        'btn_notifications': '🔔 Notifications',
        'btn_add_favorite': '⭐ Ajouter aux Favoris',
        'btn_remove_favorite': '❌ Retirer des Favoris',
        'btn_open_game': '🎮 Ouvrir le Jeu',
        'btn_share': '📤 Partager',
        
        'game_info': '🎮 <b>{name}</b>\n\n📊 Note: {rating}/10\n👥 Joueurs: {players}\n💰 Récompense: {reward}\n📅 Ajouté: {date}\n\n📝 {description}',
        'no_games': 'Aucun jeu trouvé',
        'loading': '⏳ Chargement...',
        'search_prompt': '🔍 Entrez le nom du jeu:',
        'search_results': '🔍 Résultats pour "{query}":',
        
        'favorites_empty': '⭐ Votre liste de favoris est vide',
        'favorite_added': '✅ Ajouté aux favoris',
        'favorite_removed': '✅ Retiré des favoris',
        'favorites_list': '⭐ Vos Jeux Favoris:',
        
        'notifications_on': '🔔 Notifications activées',
        'notifications_off': '🔕 Notifications désactivées',
        'notify_new_game': '🆕 Nouveau jeu: {name}\n\n{description}\n\n🎮 Essayez-le maintenant!',
        
        'error': '❌ Erreur. Réessayez.',
        'game_not_found': '❌ Jeu non trouvé',
        'invalid_command': '❌ Commande invalide. Utilisez /help',
        
        'help': '''
🤖 <b>Commandes DropsTab Bot</b>

/start - Démarrer le bot
/games - Tous les jeux
/top - Top jeux
/new - Nouveaux jeux
/hot - Jeux populaires
/search - Rechercher
/favorites - Favoris
/settings - Paramètres
/language - Changer de langue
/help - Aide

💡 <b>Conseils:</b>
• Ajoutez des jeux aux favoris
• Activez les notifications
• Partagez avec des amis

📧 Support: @dropstab_support
        ''',
        
        'settings_menu': '⚙️ Paramètres',
        'current_language': 'Langue actuelle: Français 🇫🇷',
    },
    
    'de': {
        'welcome': '🎮 Willkommen bei DropsTab Bot!\n\nVerfolge die besten Telegram Krypto-Spiele und Airdrops.',
        'main_menu': '📋 Hauptmenü',
        'back': '🔙 Zurück',
        'language_changed': '✅ Sprache geändert auf Deutsch',
        
        'btn_top_games': '🏆 Top Spiele',
        'btn_new_games': '🆕 Neu',
        'btn_hot_games': '🔥 Beliebt',
        'btn_search': '🔍 Suchen',
        'btn_favorites': '⭐ Favoriten',
        'btn_settings': '⚙️ Einstellungen',
        'btn_language': '🌐 Sprache',
        'btn_notifications': '🔔 Benachrichtigungen',
        'btn_add_favorite': '⭐ Zu Favoriten',
        'btn_remove_favorite': '❌ Aus Favoriten entfernen',
        'btn_open_game': '🎮 Spiel öffnen',
        'btn_share': '📤 Teilen',
        
        'game_info': '🎮 <b>{name}</b>\n\n📊 Bewertung: {rating}/10\n👥 Spieler: {players}\n💰 Belohnung: {reward}\n📅 Hinzugefügt: {date}\n\n📝 {description}',
        'no_games': 'Keine Spiele gefunden',
        'loading': '⏳ Lädt...',
        'search_prompt': '🔍 Spielname eingeben:',
        'search_results': '🔍 Ergebnisse für "{query}":',
        
        'favorites_empty': '⭐ Ihre Favoritenliste ist leer',
        'favorite_added': '✅ Zu Favoriten hinzugefügt',
        'favorite_removed': '✅ Aus Favoriten entfernt',
        'favorites_list': '⭐ Ihre Lieblingsspiele:',
        
        'notifications_on': '🔔 Benachrichtigungen aktiviert',
        'notifications_off': '🔕 Benachrichtigungen deaktiviert',
        'notify_new_game': '🆕 Neues Spiel: {name}\n\n{description}\n\n🎮 Jetzt ausprobieren!',
        
        'error': '❌ Fehler. Bitte erneut versuchen.',
        'game_not_found': '❌ Spiel nicht gefunden',
        'invalid_command': '❌ Ungültiger Befehl. Nutze /help',
        
        'help': '''
🤖 <b>DropsTab Bot Befehle</b>

/start - Bot starten
/games - Alle Spiele
/top - Top Spiele
/new - Neue Spiele
/hot - Beliebte Spiele
/search - Spiele suchen
/favorites - Favoriten
/settings - Einstellungen
/language - Sprache ändern
/help - Hilfe

💡 <b>Tipps:</b>
• Füge Spiele zu Favoriten hinzu
• Aktiviere Benachrichtigungen
• Teile mit Freunden

📧 Support: @dropstab_support
        ''',
        
        'settings_menu': '⚙️ Einstellungen',
        'current_language': 'Aktuelle Sprache: Deutsch 🇩🇪',
    },
    
    'pt': {
        'welcome': '🎮 Bem-vindo ao DropsTab Bot!\n\nAcompanhe os melhores jogos cripto e airdrops do Telegram.',
        'main_menu': '📋 Menu Principal',
        'back': '🔙 Voltar',
        'language_changed': '✅ Idioma alterado para Português',
        
        'btn_top_games': '🏆 Top Jogos',
        'btn_new_games': '🆕 Novos',
        'btn_hot_games': '🔥 Populares',
        'btn_search': '🔍 Pesquisar',
        'btn_favorites': '⭐ Favoritos',
        'btn_settings': '⚙️ Configurações',
        'btn_language': '🌐 Idioma',
        'btn_notifications': '🔔 Notificações',
        'btn_add_favorite': '⭐ Adicionar aos Favoritos',
        'btn_remove_favorite': '❌ Remover dos Favoritos',
        'btn_open_game': '🎮 Abrir Jogo',
        'btn_share': '📤 Compartilhar',
        
        'game_info': '🎮 <b>{name}</b>\n\n📊 Avaliação: {rating}/10\n👥 Jogadores: {players}\n💰 Recompensa: {reward}\n📅 Adicionado: {date}\n\n📝 {description}',
        'no_games': 'Nenhum jogo encontrado',
        'loading': '⏳ Carregando...',
        'search_prompt': '🔍 Digite o nome do jogo:',
        'search_results': '🔍 Resultados para "{query}":',
        
        'favorites_empty': '⭐ Sua lista de favoritos está vazia',
        'favorite_added': '✅ Adicionado aos favoritos',
        'favorite_removed': '✅ Removido dos favoritos',
        'favorites_list': '⭐ Seus Jogos Favoritos:',
        
        'notifications_on': '🔔 Notificações ativadas',
        'notifications_off': '🔕 Notificações desativadas',
        'notify_new_game': '🆕 Novo jogo: {name}\n\n{description}\n\n🎮 Experimente agora!',
        
        'error': '❌ Erro. Tente novamente.',
        'game_not_found': '❌ Jogo não encontrado',
        'invalid_command': '❌ Comando inválido. Use /help',
        
        'help': '''
🤖 <b>Comandos DropsTab Bot</b>

/start - Iniciar bot
/games - Todos os jogos
/top - Top jogos
/new - Novos jogos
/hot - Jogos populares
/search - Pesquisar jogos
/favorites - Favoritos
/settings - Configurações
/language - Mudar idioma
/help - Ajuda

💡 <b>Dicas:</b>
• Adicione jogos aos favoritos
• Ative notificações
• Compartilhe com amigos

📧 Suporte: @dropstab_support
        ''',
        
        'settings_menu': '⚙️ Configurações',
        'current_language': 'Idioma atual: Português 🇵🇹',
    },
    
    'tr': {
        'welcome': '🎮 DropsTab Bot\'a Hoş Geldiniz!\n\nEn iyi Telegram kripto oyunları ve airdropları takip edin.',
        'main_menu': '📋 Ana Menü',
        'back': '🔙 Geri',
        'language_changed': '✅ Dil Türkçe olarak değiştirildi',
        
        'btn_top_games': '🏆 En İyi Oyunlar',
        'btn_new_games': '🆕 Yeni Oyunlar',
        'btn_hot_games': '🔥 Popüler',
        'btn_search': '🔍 Ara',
        'btn_favorites': '⭐ Favoriler',
        'btn_settings': '⚙️ Ayarlar',
        'btn_language': '🌐 Dil',
        'btn_notifications': '🔔 Bildirimler',
        'btn_add_favorite': '⭐ Favorilere Ekle',
        'btn_remove_favorite': '❌ Favorilerden Çıkar',
        'btn_open_game': '🎮 Oyunu Aç',
        'btn_share': '📤 Paylaş',
        
        'game_info': '🎮 <b>{name}</b>\n\n📊 Puan: {rating}/10\n👥 Oyuncular: {players}\n💰 Ödül: {reward}\n📅 Eklenme: {date}\n\n📝 {description}',
        'no_games': 'Oyun bulunamadı',
        'loading': '⏳ Yükleniyor...',
        'search_prompt': '🔍 Oyun adını girin:',
        'search_results': '🔍 "{query}" için sonuçlar:',
        
        'favorites_empty': '⭐ Favori listeniz boş',
        'favorite_added': '✅ Favorilere eklendi',
        'favorite_removed': '✅ Favorilerden çıkarıldı',
        'favorites_list': '⭐ Favori Oyunlarınız:',
        
        'notifications_on': '🔔 Bildirimler açık',
        'notifications_off': '🔕 Bildirimler kapalı',
        'notify_new_game': '🆕 Yeni oyun: {name}\n\n{description}\n\n🎮 Şimdi deneyin!',
        
        'error': '❌ Hata oluştu. Tekrar deneyin.',
        'game_not_found': '❌ Oyun bulunamadı',
        'invalid_command': '❌ Geçersiz komut. /help kullanın',
        
        'help': '''
🤖 <b>DropsTab Bot Komutları</b>

/start - Botu başlat
/games - Tüm oyunlar
/top - En iyi oyunlar
/new - Yeni oyunlar
/hot - Popüler oyunlar
/search - Oyun ara
/favorites - Favoriler
/settings - Ayarlar
/language - Dil değiştir
/help - Yardım

💡 <b>İpuçları:</b>
• Oyunları favorilere ekleyin
• Bildirimleri açın
• Arkadaşlarla paylaşın

📧 Destek: @dropstab_support
        ''',
        
        'settings_menu': '⚙️ Ayarlar',
        'current_language': 'Mevcut dil: Türkçe 🇹🇷',
    },
    
    'zh': {
        'welcome': '🎮 欢迎使用 DropsTab Bot!\n\n追踪最佳Telegram加密游戏和空投。',
        'main_menu': '📋 主菜单',
        'back': '🔙 返回',
        'language_changed': '✅ 语言已更改为中文',
        
        'btn_top_games': '🏆 热门游戏',
        'btn_new_games': '🆕 新游戏',
        'btn_hot_games': '🔥 流行',
        'btn_search': '🔍 搜索',
        'btn_favorites': '⭐ 收藏',
        'btn_settings': '⚙️ 设置',
        'btn_language': '🌐 语言',
        'btn_notifications': '🔔 通知',
        'btn_add_favorite': '⭐ 添加到收藏',
        'btn_remove_favorite': '❌ 从收藏移除',
        'btn_open_game': '🎮 打开游戏',
        'btn_share': '📤 分享',
        
        'game_info': '🎮 <b>{name}</b>\n\n📊 评分: {rating}/10\n👥 玩家: {players}\n💰 奖励: {reward}\n📅 添加时间: {date}\n\n📝 {description}',
        'no_games': '未找到游戏',
        'loading': '⏳ 加载中...',
        'search_prompt': '🔍 输入游戏名称:',
        'search_results': '🔍 "{query}" 的搜索结果:',
        
        'favorites_empty': '⭐ 您的收藏列表为空',
        'favorite_added': '✅ 已添加到收藏',
        'favorite_removed': '✅ 已从收藏移除',
        'favorites_list': '⭐ 您收藏的游戏:',
        
        'notifications_on': '🔔 通知已开启',
        'notifications_off': '🔕 通知已关闭',
        'notify_new_game': '🆕 新游戏: {name}\n\n{description}\n\n🎮 立即试玩!',
        
        'error': '❌ 发生错误。请重试。',
        'game_not_found': '❌ 未找到游戏',
        'invalid_command': '❌ 无效命令。使用 /help',
        
        'help': '''
🤖 <b>DropsTab Bot 命令</b>

/start - 启动机器人
/games - 所有游戏
/top - 热门游戏
/new - 新游戏
/hot - 流行游戏
/search - 搜索游戏
/favorites - 收藏
/settings - 设置
/language - 更改语言
/help - 帮助

💡 <b>提示:</b>
• 添加游戏到收藏
• 开启新游戏通知
• 与朋友分享

📧 支持: @dropstab_support
        ''',
        
        'settings_menu': '⚙️ 设置',
        'current_language': '当前语言: 中文 🇨🇳',
    },
    
    'ar': {
        'welcome': '🎮 مرحباً بك في DropsTab Bot!\n\nتتبع أفضل ألعاب التشفير والإيردروبس على تيليجرام.',
        'main_menu': '📋 القائمة الرئيسية',
        'back': '🔙 رجوع',
        'language_changed': '✅ تم تغيير اللغة إلى العربية',
        
        'btn_top_games': '🏆 أفضل الألعاب',
        'btn_new_games': '🆕 ألعاب جديدة',
        'btn_hot_games': '🔥 رائج',
        'btn_search': '🔍 بحث',
        'btn_favorites': '⭐ المفضلة',
        'btn_settings': '⚙️ الإعدادات',
        'btn_language': '🌐 اللغة',
        'btn_notifications': '🔔 الإشعارات',
        'btn_add_favorite': '⭐ إضافة للمفضلة',
        'btn_remove_favorite': '❌ إزالة من المفضلة',
        'btn_open_game': '🎮 فتح اللعبة',
        'btn_share': '📤 مشاركة',
        
        'game_info': '🎮 <b>{name}</b>\n\n📊 التقييم: {rating}/10\n👥 اللاعبون: {players}\n💰 المكافأة: {reward}\n📅 تاريخ الإضافة: {date}\n\n📝 {description}',
        'no_games': 'لم يتم العثور على ألعاب',
        'loading': '⏳ جاري التحميل...',
        'search_prompt': '🔍 أدخل اسم اللعبة:',
        'search_results': '🔍
