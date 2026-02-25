// ==================== PromptFileConfig Types ====================

export interface PromptFileConfig {
  id: number
  key: string
  name: string
  description?: string
  external_path: string
  sort_order: number
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface PromptFileConfigCreate {
  key: string
  name: string
  description?: string
  external_path: string
  sort_order?: number
  is_active?: boolean
}

export interface PromptFileConfigUpdate {
  name?: string
  description?: string
  external_path?: string
  sort_order?: number
  is_active?: boolean
}

// ==================== PromptVersion Types ====================

export interface PromptFileContent {
  config_key: string
  content: string
}

export interface PromptFileResponse {
  config_key: string
  content: string
}

export interface PromptVersion {
  id: string
  version_number: number  // 前端动态计算
  created_at: string
  author: string
  description?: string
  is_active: boolean
  parent_version_id?: string
  files: PromptFileResponse[]
}

export interface PromptVersionListItem {
  id: string
  version_number: number  // 前端动态计算
  created_at: string
  author: string
  description?: string
  is_active: boolean
}

export interface PromptVersionCreate {
  author: string
  description?: string
  parent_version_id?: string
  files: PromptFileContent[]
}

export interface VersionDiffResponse {
  version1_id: string
  version2_id: string
  diffs: Record<string, {
    old: string
    new: string
  }>
}

// ==================== Evaluation Types ====================

export interface Evaluation {
  id: string
  version_id: string
  benchmark: string
  num_examples?: number
  n_threads: number
  status: string
  description?: string
  created_at: string
  started_at?: string
  completed_at?: string
  result_summary?: Record<string, any>
  error_message?: string
}

export interface EvaluationListItem {
  id: string
  version_id: string
  benchmark: string
  status: string
  description?: string
  created_at: string
  result_summary?: Record<string, any>
}

export interface EvaluationCreate {
  version_id: string
  benchmark: string
  num_examples?: number
  n_threads: number
  description?: string
}

export interface EvaluationProgressResponse {
  id: string
  status: string
  total: number
  completed: number
  current_score?: number
  latest_samples: Array<{
    index: number
    question: string
    answer: string
    score: number
    timestamp: string
  }>
  metrics?: Record<string, any>
}

// ==================== Common Types ====================

export interface MessageResponse {
  message: string
}

export interface ErrorResponse {
  detail: string
}
