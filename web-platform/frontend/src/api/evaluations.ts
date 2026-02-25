import apiClient from './client'
import type { 
  Evaluation, 
  EvaluationCreate, 
  EvaluationListItem,
  EvaluationProgressResponse,
  MessageResponse 
} from '../types'

export const evaluationsApi = {
  // 获取所有任务
  getAll: (skip = 0, limit = 100, status?: string) => 
    apiClient.get<EvaluationListItem[]>(`/evaluations?skip=${skip}&limit=${limit}${status ? `&status=${status}` : ''}`),
  
  // 获取单个任务
  getById: (id: string) => apiClient.get<Evaluation>(`/evaluations/${id}`),
  
  // 创建任务
  create: (data: EvaluationCreate) => apiClient.post<Evaluation>('/evaluations', data),
  
  // 启动任务
  start: (id: string) => apiClient.post<MessageResponse>(`/evaluations/${id}/start`),
  
  // 获取进度
  getProgress: (id: string) => apiClient.get<EvaluationProgressResponse>(`/evaluations/${id}/progress`),
  
  // 取消任务
  cancel: (id: string) => apiClient.post<MessageResponse>(`/evaluations/${id}/cancel`),
  
  // 删除任务
  delete: (id: string) => apiClient.delete<MessageResponse>(`/evaluations/${id}`),
  
  // 获取结果
  getResult: (id: string) => apiClient.get<Record<string, any>>(`/evaluations/${id}/result`),
}
