/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './core/templates/**/*.html', 
    './accounts/templates/**/*.html', 
    './planner/templates/**/*.html',   
    './reminders/templates/**/*.html',  
    './accounts/forms.py',
  ],

  // Tu tema de colores está perfecto.
  theme: {
    extend: {
      colors: {
        'background': '#0c0c0c',
        'foreground': '#f8fafc',
        'card': '#121212',
        'card-foreground': '#f8fafc',
        'primary': '#a855f7',
        'primary-foreground': '#f8fafc',
        'primary-hover': '#7c3aed',
        'secondary': '#1e1e1e',
        'secondary-foreground': '#f8fafc',
        'muted': '#1e1e1e',
        'muted-foreground': '#94a3b8',
        'accent': '#2d2d2d',
        'accent-foreground': '#f8fafc',
        'destructive': '#ef4444',
        'destructive-foreground': '#f8fafc',
        'warning': '#f59e0b',
        'warning-foreground': '#f8fafc',
        'success': '#22c55e',
        'success-foreground': '#f8fafc',
        'border': '#2d2d2d',
        'input': '#2d2d2d',
        'ring': '#a855f7',
        'sidebar-bg': '#211a2e',
        'sidebar-border': '#2c2438',
        'sidebar-muted': '#a692c9',
        'sidebar-active': '#66d870',
      },
      borderRadius: {
        'lg': '0.75rem',
      }
    },
  },
  plugins: [],
}