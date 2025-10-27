import apiClient from './index';

export const fetchStock = (ticker) => {
  return apiClient.get(`/stocks/${ticker}`);
};
