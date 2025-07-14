import React, { useState } from 'react';
import {
  Container,
  Typography,
  TextField,
  Button,
  Paper,
  Box,
  Grid,
  Card,
  CardContent,
  CircularProgress,
  Alert,
  ThemeProvider,
  createTheme,
} from '@mui/material';
import { Search, TrendingUp, Assessment, Recommend } from '@mui/icons-material';
import axios from 'axios';

const theme = createTheme({
  palette: {
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#dc004e',
    },
  },
});

interface StockAnalysis {
  symbol: string;
  company_name: string;
  stability_score: number;
  value_analysis: {
    intrinsic_value: number;
    current_price: number;
    recommendation: string;
  };
  key_metrics: {
    pe_ratio: number;
    pb_ratio: number;
    debt_equity: number;
    roe: number;
  };
}

function App() {
  const [symbol, setSymbol] = useState('');
  const [loading, setLoading] = useState(false);
  const [analysis, setAnalysis] = useState<StockAnalysis | null>(null);
  const [error, setError] = useState('');

  const handleAnalyze = async () => {
    if (!symbol.trim()) {
      setError('Please enter a stock symbol');
      return;
    }

    setLoading(true);
    setError('');
    setAnalysis(null);

    try {
      const response = await axios.post('/api/analyze', {
        symbol: symbol.toUpperCase(),
      });
      setAnalysis(response.data);
    } catch (err) {
      setError('Failed to analyze stock. Please try again.');
      console.error('Analysis error:', err);
    } finally {
      setLoading(false);
    }
  };

  const getRecommendationColor = (recommendation: string) => {
    switch (recommendation.toLowerCase()) {
      case 'buy':
        return 'success';
      case 'sell':
        return 'error';
      default:
        return 'warning';
    }
  };

  return (
    <ThemeProvider theme={theme}>
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <Box textAlign="center" mb={4}>
          <Typography variant="h3" component="h1" gutterBottom>
            VyasaQuant
          </Typography>
          <Typography variant="h6" color="text.secondary">
            Comprehensive Stock Analysis System
          </Typography>
        </Box>

        <Paper elevation={3} sx={{ p: 3, mb: 4 }}>
          <Box display="flex" gap={2} alignItems="center">
            <TextField
              fullWidth
              label="Stock Symbol (e.g., RELIANCE, TCS)"
              variant="outlined"
              value={symbol}
              onChange={(e) => setSymbol(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleAnalyze()}
              disabled={loading}
            />
            <Button
              variant="contained"
              onClick={handleAnalyze}
              disabled={loading}
              startIcon={loading ? <CircularProgress size={20} /> : <Search />}
              sx={{ minWidth: 120 }}
            >
              {loading ? 'Analyzing...' : 'Analyze'}
            </Button>
          </Box>
          {error && (
            <Alert severity="error" sx={{ mt: 2 }}>
              {error}
            </Alert>
          )}
        </Paper>

        {analysis && (
          <Grid container spacing={3}>
            <Grid item xs={12}>
              <Card>
                <CardContent>
                  <Box display="flex" alignItems="center" mb={2}>
                    <TrendingUp sx={{ mr: 1 }} />
                    <Typography variant="h5">
                      {analysis.company_name} ({analysis.symbol})
                    </Typography>
                  </Box>
                  <Typography variant="h6" color="text.secondary">
                    Overall Stability Score: {analysis.stability_score}/100
                  </Typography>
                </CardContent>
              </Card>
            </Grid>

            <Grid item xs={12} md={6}>
              <Card>
                <CardContent>
                  <Box display="flex" alignItems="center" mb={2}>
                    <Assessment sx={{ mr: 1 }} />
                    <Typography variant="h6">Value Analysis</Typography>
                  </Box>
                  <Grid container spacing={2}>
                    <Grid item xs={6}>
                      <Typography variant="body2" color="text.secondary">
                        Current Price
                      </Typography>
                      <Typography variant="h6">
                        ₹{analysis.value_analysis.current_price.toFixed(2)}
                      </Typography>
                    </Grid>
                    <Grid item xs={6}>
                      <Typography variant="body2" color="text.secondary">
                        Intrinsic Value
                      </Typography>
                      <Typography variant="h6">
                        ₹{analysis.value_analysis.intrinsic_value.toFixed(2)}
                      </Typography>
                    </Grid>
                  </Grid>
                </CardContent>
              </Card>
            </Grid>

            <Grid item xs={12} md={6}>
              <Card>
                <CardContent>
                  <Box display="flex" alignItems="center" mb={2}>
                    <Recommend sx={{ mr: 1 }} />
                    <Typography variant="h6">Recommendation</Typography>
                  </Box>
                  <Alert
                    severity={getRecommendationColor(analysis.value_analysis.recommendation)}
                    sx={{ fontSize: '1.1rem' }}
                  >
                    {analysis.value_analysis.recommendation.toUpperCase()}
                  </Alert>
                </CardContent>
              </Card>
            </Grid>

            <Grid item xs={12}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Key Metrics
                  </Typography>
                  <Grid container spacing={2}>
                    <Grid item xs={6} md={3}>
                      <Typography variant="body2" color="text.secondary">
                        P/E Ratio
                      </Typography>
                      <Typography variant="h6">
                        {analysis.key_metrics.pe_ratio.toFixed(2)}
                      </Typography>
                    </Grid>
                    <Grid item xs={6} md={3}>
                      <Typography variant="body2" color="text.secondary">
                        P/B Ratio
                      </Typography>
                      <Typography variant="h6">
                        {analysis.key_metrics.pb_ratio.toFixed(2)}
                      </Typography>
                    </Grid>
                    <Grid item xs={6} md={3}>
                      <Typography variant="body2" color="text.secondary">
                        Debt/Equity
                      </Typography>
                      <Typography variant="h6">
                        {analysis.key_metrics.debt_equity.toFixed(2)}
                      </Typography>
                    </Grid>
                    <Grid item xs={6} md={3}>
                      <Typography variant="body2" color="text.secondary">
                        ROE (%)
                      </Typography>
                      <Typography variant="h6">
                        {analysis.key_metrics.roe.toFixed(2)}%
                      </Typography>
                    </Grid>
                  </Grid>
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        )}

        {!analysis && !loading && (
          <Paper elevation={1} sx={{ p: 4, textAlign: 'center' }}>
            <Typography variant="h6" color="text.secondary">
              Enter a stock symbol to get started with comprehensive analysis
            </Typography>
          </Paper>
        )}
      </Container>
    </ThemeProvider>
  );
}

export default App; 