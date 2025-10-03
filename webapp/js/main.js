// Главный JavaScript файл для Web App
const { createApp } = Vue;
const { createVuetify } = Vuetify;

const vuetify = createVuetify();

createApp({
    data() {
        return {
            // Данные
            stats: {
                users_count: 0,
                bots_count: 0,
                channels_count: 0,
                news_today: 0
            },
            news: [],
            loading: false,
            
            // Диалоги
            showAddChannelDialog: false,
            showCategoriesDialog: false,
            showAddCategoryDialog: false,
            
            // Формы
            newChannel: '',
            newCategory: {
                name: '',
                keywords: '',
                color: '#1976D2'
            },
            
            // Уведомления
            snackbar: {
                show: false,
                message: '',
                color: 'success'
            }
        }
    },
    
    async mounted() {
        console.log('News Aggregator Web App loaded');
        await this.loadData();
    },
    
    methods: {
        async loadData() {
            this.loading = true;
            try {
                await Promise.all([
                    this.loadStats(),
                    this.loadNews()
                ]);
            } catch (error) {
                console.error('Error loading data:', error);
                this.showSnackbar('Ошибка загрузки данных', 'error');
            } finally {
                this.loading = false;
            }
        },
        
        async loadStats() {
            try {
                const response = await fetch('/api/v1/stats');
                if (response.ok) {
                    this.stats = await response.json();
                }
            } catch (error) {
                console.error('Error loading stats:', error);
            }
        },
        
        async loadNews() {
            try {
                // В MVP версии показываем заглушку
                this.news = [
                    {
                        id: 1,
                        content: 'Это пример новости. В реальной версии здесь будут новости из ваших каналов.',
                        channel_title: 'Пример канала',
                        published_at: new Date().toISOString(),
                        categories: [
                            { name: 'Технологии', color: '#4CAF50', confidence: 0.9 }
                        ]
                    },
                    {
                        id: 2,
                        content: 'Добавьте каналы через Telegram бота для получения реальных новостей.',
                        channel_title: 'Инструкция',
                        published_at: new Date(Date.now() - 3600000).toISOString(),
                        categories: [
                            { name: 'Инструкции', color: '#FF9800', confidence: 1.0 }
                        ]
                    }
                ];
            } catch (error) {
                console.error('Error loading news:', error);
            }
        },
        
        async addChannel() {
            if (!this.newChannel.trim()) {
                this.showSnackbar('Введите имя канала', 'error');
                return;
            }
            
            try {
                // В MVP версии просто показываем сообщение
                this.showSnackbar(
                    `Канал ${this.newChannel} будет добавлен через Telegram бота`, 
                    'info'
                );
                this.showAddChannelDialog = false;
                this.newChannel = '';
            } catch (error) {
                console.error('Error adding channel:', error);
                this.showSnackbar('Ошибка добавления канала', 'error');
            }
        },
        
        async addCategory() {
            if (!this.newCategory.name.trim()) {
                this.showSnackbar('Введите название категории', 'error');
                return;
            }
            
            try {
                // В MVP версии просто показываем сообщение
                this.showSnackbar(
                    `Категория "${this.newCategory.name}" будет создана через Telegram бота`, 
                    'info'
                );
                this.showAddCategoryDialog = false;
                this.newCategory = {
                    name: '',
                    keywords: '',
                    color: '#1976D2'
                };
            } catch (error) {
                console.error('Error adding category:', error);
                this.showSnackbar('Ошибка добавления категории', 'error');
            }
        },
        
        async generateSummary() {
            try {
                this.showSnackbar(
                    'Создание саммари через ИИ будет доступно в полной версии', 
                    'info'
                );
            } catch (error) {
                console.error('Error generating summary:', error);
                this.showSnackbar('Ошибка создания саммари', 'error');
            }
        },
        
        async refreshData() {
            await this.loadData();
            this.showSnackbar('Данные обновлены', 'success');
        },
        
        formatDate(dateString) {
            const date = new Date(dateString);
            return date.toLocaleString('ru-RU', {
                year: 'numeric',
                month: 'short',
                day: 'numeric',
                hour: '2-digit',
                minute: '2-digit'
            });
        },
        
        showSnackbar(message, color = 'success') {
            this.snackbar = {
                show: true,
                message,
                color
            };
        }
    }
}).use(vuetify).mount('#app');
