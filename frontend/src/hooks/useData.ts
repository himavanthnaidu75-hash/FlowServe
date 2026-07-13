import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '../lib/api';

export const useFetch = <T>(key: string[], endpoint: string) => {
  return useQuery<T>({
    queryKey: key,
    queryFn: async () => {
      const { data } = await api.get(endpoint);
      return data;
    },
  });
};

export const useCreate = <T, U>(key: string[], endpoint: string) => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (payload: U) => {
      const { data } = await api.post<T>(endpoint, payload);
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: key });
    },
  });
};

export const useUpdate = <T, U>(key: string[], endpoint: string) => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async ({ id, ...payload }: U & { id: string }) => {
      const { data } = await api.patch<T>(`${endpoint}/${id}`, payload);
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: key });
    },
  });
};

export const useDelete = (key: string[], endpoint: string) => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (id: string) => {
      await api.delete(`${endpoint}/${id}`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: key });
    },
  });
};
