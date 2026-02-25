import apiClient from './client'
import type { PromptVersion, MessageResponse } from '../types'

export interface PromptVersionSimple {
  id: string
  version_number: number
  is_active: boolean
  created_at: string
  author: string
  description?: string
}

export interface PromptVersionsResponse {
  config_key: string
  config_name: string
  active_version_id: string | null
  versions: PromptVersionSimple[]
}

export interface CreatePromptVersionRequest {
  author: string
  content: string
  description?: string
}

export const promptsApi = {
  // 获取指定 Prompt 的所有版本
  getVersions: (configKey: string) => 
    apiClient.get<PromptVersionsResponse>(`/versions/prompt/${configKey}`),
  
  // 获取指定版本的完整内容
  getVersionContent: (configKey: string, versionId: string) => 
    apiClient.get<{ id: string; config_key: string; content: string }>(`/versions/prompt/${configKey}/content/${versionId}`),
  
  // 创建新版本
  createVersion: (configKey: string, data: CreatePromptVersionRequest) => 
    apiClient.post<PromptVersion>(`/versions/prompt/${configKey}`, data),
  
  // 激活指定版本
  activateVersion: (configKey: string, versionId: string) => 
    apiClient.post<MessageResponse>(`/versions/prompt/${configKey}/activate/${versionId}`),
  
  // 删除版本
  deleteVersion: (versionId: string) => 
    apiClient.delete<MessageResponse>(`/versions/${versionId}`),
  
  // 更新版本内容（用于同步外部文件）
  updateVersionContent: (configKey: string, versionId: string, content: string) => 
    apiClient.put<MessageResponse>(`/versions/prompt/${configKey}/content/${versionId}`, { content }),
}
