# VyasaQuant Frontend

This is the React TypeScript frontend application for the VyasaQuant stock analysis system.

## Overview

The frontend provides a modern, responsive web interface for users to:
- Enter stock symbols for analysis
- View comprehensive stock analysis results
- Get buy/sell recommendations
- Monitor key financial metrics
- Access stability scores and value analysis

## Features

### 🎨 Modern UI
- **Material-UI (MUI)** components for consistent design
- **Responsive layout** that works on desktop and mobile
- **Dark/Light theme** support
- **Loading states** and error handling

### 📊 Stock Analysis Dashboard
- **Real-time stock analysis** results
- **Interactive charts** (using Recharts)
- **Key metrics display** (P/E ratio, P/B ratio, ROE, etc.)
- **Recommendation alerts** with color-coded indicators

### 🔍 Search & Analysis
- **Stock symbol search** with autocomplete
- **Real-time data** fetching from backend
- **Error handling** for invalid symbols
- **Loading indicators** during analysis

## Technology Stack

- **React 18** with TypeScript
- **Material-UI (MUI)** for components
- **Axios** for API calls
- **React Router** for navigation
- **Recharts** for data visualization
- **React Scripts** for development

## Setup & Installation

### Prerequisites
- Node.js 16 or higher
- npm or yarn package manager

### Installation Steps

1. **Navigate to frontend directory:**
```bash
cd frontend
```

2. **Install dependencies:**
```bash
npm install
```

3. **Set up environment variables:**
Create a `.env` file in the frontend directory:
```env
REACT_APP_API_URL=http://localhost:8000
REACT_APP_API_VERSION=v1
```

4. **Start development server:**
```bash
npm start
```

The application will open at `http://localhost:3000`

## Available Scripts

### `npm start`
Runs the app in development mode.
Open [http://localhost:3000](http://localhost:3000) to view it in the browser.

### `npm test`
Launches the test runner in interactive watch mode.

### `npm run build`
Builds the app for production to the `build` folder.
It correctly bundles React in production mode and optimizes the build for the best performance.

### `npm run eject`
**Note: this is a one-way operation. Once you `eject`, you can't go back!**

## Project Structure

```
frontend/
├── public/
│   ├── index.html          # Main HTML file
│   └── manifest.json       # PWA manifest
├── src/
│   ├── components/         # Reusable React components
│   │   ├── StockSearch.tsx
│   │   ├── AnalysisResults.tsx
│   │   └── MetricsCard.tsx
│   ├── services/           # API service layer
│   │   └── api.ts
│   ├── types/              # TypeScript type definitions
│   │   └── stock.ts
│   ├── utils/              # Utility functions
│   │   └── formatters.ts
│   ├── App.tsx             # Main app component
│   ├── index.tsx           # Entry point
│   └── index.css           # Global styles
├── package.json            # Dependencies and scripts
├── tsconfig.json           # TypeScript configuration
└── README.md               # This file
```

## API Integration

The frontend communicates with the backend API for stock analysis:

### Endpoints Used
- `POST /api/analyze` - Analyze a stock symbol
- `GET /api/stocks` - Get list of available stocks
- `GET /api/metrics/{symbol}` - Get specific stock metrics

### Example API Call
```typescript
const analyzeStock = async (symbol: string) => {
  const response = await axios.post('/api/analyze', {
    symbol: symbol.toUpperCase(),
  });
  return response.data;
};
```

## Component Architecture

### Main Components

1. **App.tsx** - Main application component
2. **StockSearch** - Search input and analyze button
3. **AnalysisResults** - Display analysis results
4. **MetricsCard** - Individual metric display
5. **RecommendationAlert** - Buy/sell recommendation display

### State Management
- Uses React hooks (useState, useEffect)
- Local state for UI components
- API state management with error handling

## Styling

- **Material-UI theme** for consistent design
- **CSS-in-JS** with emotion
- **Responsive design** using MUI Grid system
- **Custom theme colors** matching VyasaQuant branding

## Error Handling

- **Network errors** - Display user-friendly messages
- **Invalid symbols** - Show validation errors
- **Loading states** - Prevent multiple submissions
- **Fallback UI** - Graceful degradation

## Performance Optimizations

- **Code splitting** with React.lazy
- **Memoization** for expensive calculations
- **Debounced search** to reduce API calls
- **Optimized bundle size** with tree shaking

## Testing

```bash
# Run all tests
npm test

# Run tests with coverage
npm test -- --coverage

# Run tests in watch mode
npm test -- --watch
```

## Deployment

### Production Build
```bash
npm run build
```

### Deployment Options
- **Netlify** - Connect GitHub repository
- **Vercel** - Deploy with zero configuration
- **AWS S3** - Static website hosting
- **Heroku** - Platform as a Service

## Environment Variables

Create a `.env` file in the frontend directory:

```env
# API Configuration
REACT_APP_API_URL=http://localhost:8000
REACT_APP_API_VERSION=v1

# Feature Flags
REACT_APP_ENABLE_CHARTS=true
REACT_APP_ENABLE_DARK_MODE=true

# Analytics (optional)
REACT_APP_GA_TRACKING_ID=UA-XXXXXX-X
```

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)
- Internet Explorer is not supported

## Contributing

1. Follow the existing code style
2. Write tests for new components
3. Update documentation
4. Ensure accessibility standards
5. Test on multiple browsers

## Troubleshooting

### Common Issues

1. **Port already in use**
   ```bash
   Error: Something is already running on port 3000
   ```
   Solution: Kill the process or use a different port

2. **Module not found**
   ```bash
   Module not found: Can't resolve 'react'
   ```
   Solution: Run `npm install` to install dependencies

3. **Build fails**
   ```bash
   Failed to compile
   ```
   Solution: Check for TypeScript errors and fix them

## License

This project is licensed under the MIT License - see the LICENSE file for details. 