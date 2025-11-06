/**
 * Custom Hook for API calls
 * Centralized API call handling with error management
 */
import { useState, useCallback } from 'react';
import api from '../services/api';

export const useApi = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const callApi = useCallback(async (apiFunc, ...args) => {
    setLoading(true);
    setError(null);

    try {
      const response = await apiFunc(...args);
      setLoading(false);
      return response.data;
    } catch (err) {
      setError(err.message || 'An error occurred');
      setLoading(false);
      throw err;
    }
  }, []);

  return { callApi, loading, error };
};
