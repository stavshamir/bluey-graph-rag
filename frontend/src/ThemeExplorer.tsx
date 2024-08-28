import React, { useState } from 'react';
import axios from "axios";
import { Link } from '@mui/material';
import OpenInNewIcon from '@mui/icons-material/OpenInNew'; 

import {
  TextField,
  Button,
  List,
  ListItem,
  Typography,
  Paper,
  Box,
  CircularProgress,
  Alert,
  Chip,
  Divider
} from '@mui/material';
import { ExpandMore, ExpandLess, Star } from '@mui/icons-material';

interface ThemeItem {
  id: string;
  title: string;
  episodeTitle: string;
  episodeUrl: string; 
  score: number;
  explanation: string;
  description?: string;
  quotes: string[];
  isBestMatch: boolean;
  answer: string;
}

interface APIResponse {
  similarThemes: ThemeItem[];
}

interface ThemeResponse {
  episode_title: string;
  episode_url: string;
  semantic_id: string;
  title: string;
  description: string;
  explanation: string;
  supporting_quotes: string[];

}

interface SimilarThemesResponse {
  themes: {
    theme: ThemeResponse,
    score: number,
    is_best_match: boolean,
    answer: string
  }[];
}

axios.defaults.withCredentials = true;

const ThemeExplorer: React.FC = () => {
  const [theme, setTheme] = useState<string>('');
  const [results, setResults] = useState<APIResponse | null>(null);
  const [selectedTheme, setSelectedTheme] = useState<ThemeItem | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [expandedItems, setExpandedItems] = useState<Record<string, boolean>>({});
  const [answer, setAnswer] = useState<string | null>(null);
  const suggestions = [
    "The importance of cooperation",
    "Recognizing the significance of guidelines",
    "Solving conflicts between siblings"
  ];

  const handleSuggestionClick = (suggestion: string) => {
    setTheme(suggestion);
  };

  const getSimilarThemes = async (theme: string): Promise<APIResponse> => {
    const response = await axios.post<SimilarThemesResponse>('http://localhost:8000/themes/find_similar', { theme: theme });

    return {
      similarThemes: response.data.themes.map(t => ({
        id: t.theme.semantic_id,
        title: t.theme.title,
        episodeTitle: t.theme.episode_title,
        episodeUrl: `https://blueypedia.fandom.com${t.theme.episode_url}`,
        score: t.score,
        explanation: t.theme.explanation,
        description: t.theme.description,
        quotes: t.theme.supporting_quotes,
        isBestMatch: t.is_best_match,
        answer: t.answer
      }))
    };
  };

  const getThemeAnswer = async (theme: string, similarThemeId: string): Promise<string> => {
    const response = await axios.post<string>('http://localhost:8000/themes/answer', {
      theme: theme,
      similar_theme_id: similarThemeId
    });
    return response.data;
  };

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setIsLoading(true);
    setError(null);
    setResults(null);
    setSelectedTheme(null);
    setExpandedItems({});

    try {
      const data = await getSimilarThemes(theme);
      setResults(data);
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setIsLoading(false);
    }
  };

  const handleExpand = (id: string) => {
    setExpandedItems(prev => ({ ...prev, [id]: !prev[id] }));
  };

  const handleSelectTheme = async (item: ThemeItem) => {
    setSelectedTheme(item);
    setAnswer(null);
    setIsLoading(true);
    setError(null);

    try {
      const answerText = await getThemeAnswer(theme, item.id);
      setAnswer(answerText);
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setIsLoading(false);
    }
  };

  const ResultList: React.FC<{ data: ThemeItem[]; theme: string }> = ({ data, theme }) => {
    const [expandedItem, setExpandedItem] = useState<string | null>(null);
    const [loadingAnswer, setLoadingAnswer] = useState<string | null>(null);

    const handleExpand = (id: string) => {
      setExpandedItem(expandedItem === id ? null : id);
    };

    const handleGetAnswer = async (item: ThemeItem) => {
      setLoadingAnswer(item.id);
      try {
        const answerText = await getThemeAnswer(theme, item.id);
        setResults(prevResults => {
          if (!prevResults) return prevResults;
          return {
            ...prevResults,
            similarThemes: prevResults.similarThemes.map(t =>
              t.id === item.id ? { ...t, answer: answerText } : t
            )
          };
        });
      } catch (err) {
        console.error("Error fetching answer:", err);
      } finally {
        setLoadingAnswer(null);
      }
    };

    return (
      <Box mt={4}>
        <List>
          {data.map((item) => (
            <Paper key={item.id} elevation={1} sx={{ mb: 2, overflow: 'hidden' }}>
              <ListItem
                button
                onClick={() => handleExpand(item.id)}
                sx={{
                  display: 'flex',
                  flexDirection: 'column',
                  alignItems: 'stretch',
                  p: 2,
                }}
              >
                <Box display="flex" justifyContent="space-between" width="100%" alignItems="center">
                  <Box>
                    <Box display="flex" alignItems="center">
                      <Typography variant="subtitle1" fontWeight="bold">
                        {item.title}
                      </Typography>
                      {item.isBestMatch && (
                        <Chip
                          label="Best Match"
                          size="small"
                          sx={{
                            backgroundColor: 'primary.main',
                            color: 'primary.contrastText',
                            ml: 1,
                            height: '20px',
                          }}
                        />
                      )}
                    </Box>
                    <Box display="flex" alignItems="center">
                      <Link
                        href={item.episodeUrl}
                        target="_blank"
                        rel="noopener noreferrer"
                        onClick={(e) => e.stopPropagation()}
                        sx={{
                          display: 'flex',
                          alignItems: 'center',
                          color: 'primary.main',
                          textDecoration: 'underline',
                          '&:hover': {
                            textDecoration: 'none',
                          },
                        }}
                      >
                        <OpenInNewIcon sx={{ fontSize: 16, mr: 0.5 }} />
                        {item.episodeTitle}
                      </Link>
                      <Typography variant="body2" color="text.secondary" sx={{ ml: 1 }}>
                        | Score: {item.score.toFixed(2)}
                      </Typography>
                    </Box>
                  </Box>
                  {expandedItem === item.id ? <ExpandLess /> : <ExpandMore />}
                </Box>
              </ListItem>
              {expandedItem === item.id && (
                <Box p={2} bgcolor="background.paper">
                  <Box mb={2}>
                    <Typography variant="body2">
                      {item.answer}
                    </Typography>
                  </Box>
                  <Divider style={{ margin: '16px 0' }} />
                  <Typography variant="body2" paragraph>
                    <strong>Description:</strong> {item.description}
                  </Typography>
                  <Typography variant="body2" paragraph>
                    <strong>Explanation:</strong> {item.explanation}
                  </Typography>
                  <Typography variant="body2" gutterBottom>
                    <strong>Supporting Quotes:</strong>
                  </Typography>
                  <Box mb={2}>
                    {item.quotes.map((quote, index) => (
                      <Typography key={index} variant="body2" sx={{ fontStyle: 'italic', mb: 1 }}>
                        "{quote}"
                      </Typography>
                    ))}
                  </Box>
                </Box>
              )}
            </Paper>
          ))}
        </List>
      </Box>
    );
  };

  return (
    <Box maxWidth="md" margin="auto" p={4}>
      <form onSubmit={handleSubmit}>
        <Typography variant="body1" gutterBottom>
          An episode exploring the theme of
        </Typography>
        <Box display="flex" gap={2}>
          <TextField
            fullWidth
            value={theme}
            onChange={(e: React.ChangeEvent<HTMLInputElement>) => setTheme(e.target.value)}
            placeholder="Enter theme"
            disabled={isLoading}
          />
          <Button type="submit" variant="contained" disabled={isLoading}>
            {isLoading ? <CircularProgress size={24} /> : 'Find'}
          </Button>
        </Box>
        <Box display="flex" flexWrap="wrap" gap={1} mt={2}>
          {suggestions.map((suggestion, index) => (
            <Chip
              key={index}
              label={suggestion}
              onClick={() => handleSuggestionClick(suggestion)}
              disabled={isLoading}
              clickable
              color="primary"
              variant="outlined"
            />
          ))}
        </Box>
      </form>

      {error && (
        <Alert severity="error" sx={{ mt: 2 }}>
          {error}
        </Alert>
      )}

      {results && (
        <ResultList data={results.similarThemes} theme={theme} />
      )}

    </Box>
  );
};

export default ThemeExplorer;