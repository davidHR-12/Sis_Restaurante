module.exports = {
  content: [
    './Web_Restaurante/templates/**/*.html',
    './Web_Restaurante/static/js/**/*.js',
  ],
  safelist: [
    'bg-gray-400',
    'text-gray-700',
    'cursor-not-allowed',
    'bg-destructive',
    'hover:bg-destructive/90',
    'text-destructive-gray-100',
    'bg-primary-foreground/10',
    'hover:bg-primary-foreground/20',
    // y todas las clases dinámicas que usas
  ],
  theme: {
    extend: {
      colors: {
        background: "#0a0a0a",
        foreground: "#fafafa",
        card: "#1a1a1a",
        "card-foreground": "#fafafa",
        primary: "#3b82f6",
        "primary-foreground": "#fafafa",
        orange: "#ff7b00",
        "orange-foreground": "#fafafa",
        secondary: "#262626",
        "secondary-foreground": "#fafafa",
        muted: "#262626",
        "muted-foreground": "#a3a3a3",
        accent: "#10b981",
        "accent-foreground": "#fafafa",
        destructive: "#ef4444",
        "destructive-foreground": "#fafafa",
        border: "#404040",
        input: "#262626",
        ring: "#3b82f6",
      },
    },
  },
};
