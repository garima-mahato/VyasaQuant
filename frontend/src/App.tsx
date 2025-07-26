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
  Chip,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
} from '@mui/material';
import { Search, TrendingUp, Assessment, Recommend, ShowChart } from '@mui/icons-material';
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

interface EPSData {
  data: Record<string, number>;
  years_available: string[];
  total_years: number;
}

interface StabilityAnalysis {
  eps_data: EPSData;
  eps_growth_rate: number;
  is_eps_increasing: boolean;
  passes_stability_criteria: boolean;
  recommendation: string;
  reasoning: string;
}

interface StockAnalysis {
  symbol: string;
  company_name: string;
  analysis_date: string;
  stability_analysis: StabilityAnalysis;
  raw_agent_response?: string;
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
      case 'further_analysis':
        return 'info';
      default:
        return 'warning';
    }
  };

  const formatRecommendation = (recommendation: string) => {
    return recommendation.replace('_', ' ').toUpperCase();
  };

  return (
    <ThemeProvider theme={theme}>
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <Box textAlign="center" mb={4}>
          <Typography variant="h3" component="h1" gutterBottom>
            VyasaQuant
          </Typography>
          <Typography variant="h6" color="text.secondary">
            Stock Stability Analysis System
          </Typography>
        </Box>

        <Paper elevation={3} sx={{ p: 3, mb: 4 }}>
          <Box display="flex" gap={2} alignItems="center">
            <TextField
              fullWidth
              label="Stock Symbol or Company Name (e.g., RELIANCE, TCS, HINDUSTAN AERONAUTICS LIMITED)"
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
            {/* Company Header */}
            <Grid item xs={12}>
              <Card>
                <CardContent>
                  <Box display="flex" alignItems="center" justifyContent="space-between" mb={2}>
                    <Box display="flex" alignItems="center">
                      <TrendingUp sx={{ mr: 1 }} />
                      <Typography variant="h5">
                        {analysis.company_name} ({analysis.symbol})
                      </Typography>
                    </Box>
                    <Typography variant="body2" color="text.secondary">
                      Analysis Date: {analysis.analysis_date}
                    </Typography>
                  </Box>
                  
                  <Box display="flex" gap={2} flexWrap="wrap">
                    <Chip
                      label={analysis.stability_analysis.is_eps_increasing ? "EPS Increasing" : "EPS Not Increasing"}
                      color={analysis.stability_analysis.is_eps_increasing ? "success" : "error"}
                      variant="outlined"
                    />
                    <Chip
                      label={analysis.stability_analysis.passes_stability_criteria ? "Passes Criteria" : "Fails Criteria"}
                      color={analysis.stability_analysis.passes_stability_criteria ? "success" : "error"}
                      variant="outlined"
                    />
                    <Chip
                      label={`Growth Rate: ${analysis.stability_analysis.eps_growth_rate.toFixed(2)}%`}
                      color="info"
                      variant="outlined"
                    />
                  </Box>
                </CardContent>
              </Card>
            </Grid>

            {/* EPS Data Table */}
            <Grid item xs={12} md={6}>
              <Card>
                <CardContent>
                  <Box display="flex" alignItems="center" mb={2}>
                    <ShowChart sx={{ mr: 1 }} />
                    <Typography variant="h6">EPS Data ({analysis.stability_analysis.eps_data.total_years} Years)</Typography>
                  </Box>
                  
                  {analysis.stability_analysis.eps_data.total_years > 0 ? (
                    <TableContainer>
                      <Table size="small">
                        <TableHead>
                          <TableRow>
                            <TableCell><strong>Year</strong></TableCell>
                            <TableCell align="right"><strong>EPS (₹)</strong></TableCell>
                          </TableRow>
                        </TableHead>
                        <TableBody>
                          {analysis.stability_analysis.eps_data.years_available.map((year) => (
                            <TableRow key={year}>
                              <TableCell>{year}</TableCell>
                              <TableCell align="right">
                                {analysis.stability_analysis.eps_data.data[year].toFixed(2)}
                              </TableCell>
                            </TableRow>
                          ))}
                        </TableBody>
                      </Table>
                    </TableContainer>
                  ) : (
                    <Alert severity="warning">
                      No EPS data available
                    </Alert>
                  )}
                </CardContent>
              </Card>
            </Grid>

            {/* Recommendation */}
            <Grid item xs={12} md={6}>
              <Card>
                <CardContent>
                  <Box display="flex" alignItems="center" mb={2}>
                    <Recommend sx={{ mr: 1 }} />
                    <Typography variant="h6">Recommendation</Typography>
                  </Box>
                  <Alert
                    severity={getRecommendationColor(analysis.stability_analysis.recommendation)}
                    sx={{ fontSize: '1.1rem', mb: 2 }}
                  >
                    {formatRecommendation(analysis.stability_analysis.recommendation)}
                  </Alert>
                  
                  <Typography variant="body2" color="text.secondary" gutterBottom>
                    Growth Rate Analysis:
                  </Typography>
                  <Typography variant="h6" color={analysis.stability_analysis.eps_growth_rate > 10 ? "success.main" : "warning.main"}>
                    {analysis.stability_analysis.eps_growth_rate.toFixed(2)}% CAGR
                  </Typography>
                </CardContent>
              </Card>
            </Grid>

            {/* Detailed Analysis */}
            <Grid item xs={12}>
              <Card>
                <CardContent>
                  <Box display="flex" alignItems="center" mb={2}>
                    <Assessment sx={{ mr: 1 }} />
                    <Typography variant="h6">Detailed Analysis</Typography>
                  </Box>
                  
                  <Paper variant="outlined" sx={{ p: 2, backgroundColor: 'grey.50' }}>
                    <Typography variant="body1" style={{ whiteSpace: 'pre-line' }}>
                      {analysis.stability_analysis.reasoning}
                    </Typography>
                  </Paper>

                  {analysis.raw_agent_response && (
                    <Box mt={2}>
                      <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                        Raw Agent Response (Debug):
                      </Typography>
                      <Paper variant="outlined" sx={{ p: 1, backgroundColor: 'grey.100' }}>
                        <Typography variant="caption" style={{ whiteSpace: 'pre-line', fontFamily: 'monospace' }}>
                          {analysis.raw_agent_response}
                        </Typography>
                      </Paper>
                    </Box>
                  )}
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        )}

        {!analysis && !loading && (
          <Paper elevation={1} sx={{ p: 4, textAlign: 'center' }}>
            <Typography variant="h6" color="text.secondary" gutterBottom>
              Enter a stock symbol or company name to get started
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Our system analyzes EPS growth trends and provides stability recommendations
            </Typography>
          </Paper>
        )}
      </Container>
    </ThemeProvider>
  );
}

export default App; 