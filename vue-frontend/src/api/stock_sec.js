import apiClient from './index';

export const fetchStock = (ticker) => {
  return apiClient.get(`/stocks/${ticker}`);
};

export async function fetchFundamentals(ticker, form) {
  const response = await apiClient.get(`/fundamentals_history/${ticker}`, {
    params: { form },
  });
  return response.data;
}