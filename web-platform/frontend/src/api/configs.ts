import apiClient from './client'
import type { 
  PromptFileConfig, 
  PromptFileConfigCreate, 
  PromptFileConfigUpdate,
  MessageResponse 
} from '../types'

export interface TestPathResponse {
  readable: boolean
  content?: string
  error?: string
}

export const configsApi = {
  // 获取所有配置
  getAll: () => apiClient.get<PromptFileConfig[]>('/configs'),
  
  // 获取单个配置
  getByKey: (key: string) => apiClient.get<PromptFileConfig>(`/configs/${key}`),
  
  // 创建配置
  create: (data: PromptFileConfigCreate) => apiClient.post<PromptFileConfig>('/configs', data),
  
  // 更新配置
  update: (key: string, data: PromptFileConfigUpdate) => 
    apiClient.put<PromptFileConfig>(`/configs/${key}`, data),
  
  // 删除配置
  delete: (key: string, force?: boolean) => 
    apiClient.delete<MessageResponse>(`/configs/${key}`, { params: { force } }),
  
  // 调整排序
  reorder: (keys: string[]) => apiClient.post<MessageResponse>('/configs/reorder', keys),
  
  // 测试文件路径
  testPath: (path: string) => apiClient.post<TestPathResponse>('/configs/test-path', { path }),
}
