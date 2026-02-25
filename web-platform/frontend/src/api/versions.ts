import apiClient from './client'
import type { 
  PromptVersion, 
  PromptVersionCreate, 
  PromptVersionListItem,
  VersionDiffResponse,
  MessageResponse 
} from '../types'

export const versionsApi = {
  // 获取所有版本
  getAll: (skip = 0, limit = 100) => 
    apiClient.get<PromptVersionListItem[]>(`/versions?skip=${skip}&limit=${limit}`),
  
  // 获取当前生效版本
  getActive: () => apiClient.get<PromptVersion | null>('/versions/active'),
  
  // 获取单个版本
  getById: (id: string) => apiClient.get<PromptVersion>(`/versions/${id}`),
  
  // 创建版本
  create: (data: PromptVersionCreate) => apiClient.post<PromptVersion>('/versions', data),
  
  // 激活版本
  activate: (id: string) => apiClient.post<MessageResponse>(`/versions/${id}/activate`),
  
  // 对比版本
  compare: (id1: string, id2: string) => 
    apiClient.get<VersionDiffResponse>(`/versions/${id1}/diff/${id2}`),
  
  // 删除版本
  delete: (id: string) => apiClient.delete<MessageResponse>(`/versions/${id}`),
  
  // 从外置系统导入
  importFromExternal: (author: string, description?: string) => 
    apiClient.post<PromptVersion>('/versions/import-from-external', null, {
      params: { author, description }
    }),
}
