// JARVIS 3.0 - Controle de Tema

class ThemeManager {
    constructor() {
        this.currentTheme = this.getStoredTheme() || 'dark';
        this.init();
    }
    
    init() {
        this.applyTheme(this.currentTheme);
        this.setupEventListeners();
    }
    
    setupEventListeners() {
        const themeToggle = document.getElementById('theme-toggle');
        if (themeToggle) {
            themeToggle.addEventListener('click', () => {
                this.toggleTheme();
            });
        }
        
        // Detecta preferência do sistema
        if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
            // Sistema prefere tema escuro
        }
        
        // Escuta mudanças na preferência do sistema
        window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
            if (!this.getStoredTheme()) {
                this.applyTheme(e.matches ? 'dark' : 'light');
            }
        });
    }
    
    toggleTheme() {
        const newTheme = this.currentTheme === 'dark' ? 'light' : 'dark';
        this.applyTheme(newTheme);
        this.storeTheme(newTheme);
    }
    
    applyTheme(theme) {
        this.currentTheme = theme;
        
        if (theme === 'light') {
            document.documentElement.setAttribute('data-theme', 'light');
        } else {
            document.documentElement.removeAttribute('data-theme');
        }
        
        this.updateThemeToggleIcon();
        this.updateChartThemes();
    }
    
    updateThemeToggleIcon() {
        const themeToggle = document.getElementById('theme-toggle');
        if (themeToggle) {
            themeToggle.textContent = this.currentTheme === 'dark' ? '☀️' : '🌙';
            themeToggle.title = this.currentTheme === 'dark' ? 'Mudar para tema claro' : 'Mudar para tema escuro';
        }
    }
    
    updateChartThemes() {
        // Atualiza temas dos gráficos Chart.js
        if (window.dashboard && window.dashboard.charts) {
            const textColor = this.currentTheme === 'dark' ? '#ffffff' : '#212529';
            const gridColor = this.currentTheme === 'dark' ? '#333333' : '#dee2e6';
            
            Object.values(window.dashboard.charts).forEach(chart => {
                if (chart && chart.options) {
                    // Atualiza cores do texto
                    if (chart.options.plugins && chart.options.plugins.legend) {
                        chart.options.plugins.legend.labels.color = textColor;
                    }
                    
                    // Atualiza cores dos eixos
                    if (chart.options.scales) {
                        Object.values(chart.options.scales).forEach(scale => {
                            if (scale.ticks) scale.ticks.color = textColor;
                            if (scale.grid) scale.grid.color = gridColor;
                        });
                    }
                    
                    chart.update();
                }
            });
        }
    }
    
    getStoredTheme() {
        return localStorage.getItem('jarvis-theme');
    }
    
    storeTheme(theme) {
        localStorage.setItem('jarvis-theme', theme);
    }
}

// Inicializa o gerenciador de tema o mais cedo possível
document.addEventListener('DOMContentLoaded', () => {
    window.themeManager = new ThemeManager();
});

// Aplica tema antes mesmo do DOM carregar para evitar flash
(function() {
    const storedTheme = localStorage.getItem('jarvis-theme');
    if (storedTheme === 'light') {
        document.documentElement.setAttribute('data-theme', 'light');
    }
})();
