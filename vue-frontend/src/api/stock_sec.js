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

export const fetchStockInfo = async (ticker) => {
  const response = await apiClient.get(`/stock_info/${ticker}`);
  return response.data;
};

export const fetchKpis = async (ticker) => {
  const response = await apiClient.get(`/kpis/${ticker}`);
  return response.data;
};

export const fetchEarnings = async (ticker) => {
  const response = await apiClient.get(`/earnings/${ticker}`);
  return response.data;
};
