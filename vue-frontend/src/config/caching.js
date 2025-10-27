// Vue Query default options for the app
export const vueQueryOptions = {
  queries: {
    // Data stays fresh for 5 minutes
    staleTime: 5 * 60 * 1000,

    // Keep cached data even if unused
    cacheTime: 15 * 60 * 1000,

    // Retry failed requests automatically
    retry: 2,

    // Refetch when window/tab gains focus
    refetchOnWindowFocus: true,
  },
};
