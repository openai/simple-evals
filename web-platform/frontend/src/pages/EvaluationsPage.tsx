import { useState, useEffect, useCallback } from 'react'
import { 
  Card, 
  Button, 
  Table, 
  Tag, 
  Space,
  Typography,
  Progress,
  Modal,
  Descriptions,
  Timeline,
  Badge,
  message,
  Popconfirm
} from 'antd'
import { 
  PlayCircleOutlined, 
  PauseCircleOutlined,
  DeleteOutlined,
  EyeOutlined,
  ReloadOutlined,
  CheckCircleOutlined,
  CloseCircleOutlined,
  ClockCircleOutlined,
  PlusOutlined
} from '@ant-design/icons'
import { evaluationsApi } from '../api/evaluations'
import { versionsApi } from '../api/versions'
import type { Evaluation, EvaluationListItem, EvaluationProgressResponse, PromptVersion } from '../types'
import dayjs from 'dayjs'
import { Link } from 'react-router-dom'

const { Title, Text } = Typography

// Google 风格配色
const GOOGLE_COLORS = {
  blue: '#1a73e8',
  red: '#ea4335',
  yellow: '#fbbc04',
  green: '#34a853',
  gray: '#5f6368',
  lightGray: '#f8f9fa',
  white: '#ffffff',
  border: '#dadce0'
}

export default function EvaluationsPage() {
  const [evaluations, setEvaluations] = useState<EvaluationListItem[]>([])
  const [loading, setLoading] = useState(false)
  const [detailModalVisible, setDetailModalVisible] = useState(false)
  const [selectedEval, setSelectedEval] = useState<Evaluation | null>(null)
  const [progress, setProgress] = useState<EvaluationProgressResponse | null>(null)
  const [versions, setVersions] = useState<Record<string, PromptVersion>>({})
  const [pollingInterval, setPollingInterval] = useState<NodeJS.Timeout | null>(null)

  // 加载 Eval 列表
  const loadEvaluations = async () => {
    setLoading(true)
    try {
      const response = await evaluationsApi.getAll()
      setEvaluations(response.data)
    } catch (error) {
      message.error('加载任务列表失败')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadEvaluations()
  }, [])

  // 加载版本信息
  const loadVersionInfo = async (versionId: string) => {
    if (versions[versionId]) return
    try {
      const response = await versionsApi.getById(versionId)
      setVersions(prev => ({ ...prev, [versionId]: response.data }))
    } catch (error) {
      console.error('加载版本信息失败', error)
    }
  }

  // 查看详情并开始轮询
  const handleViewDetail = async (evalId: string) => {
    try {
      const response = await evaluationsApi.getById(evalId)
      setSelectedEval(response.data)
      setDetailModalVisible(true)
      
      // 加载版本信息
      loadVersionInfo(response.data.version_id)
      
      // 立即获取进度
      await loadProgress(evalId)
      
      // 如果任务正在运行，开始轮询
      if (response.data.status === 'running') {
        startPolling(evalId)
      }
    } catch (error) {
      message.error('加载详情失败')
    }
  }

  // 加载进度
  const loadProgress = async (evalId: string) => {
    try {
      const response = await evaluationsApi.getProgress(evalId)
      setProgress(response.data)
    } catch (error) {
      console.error('加载进度失败', error)
    }
  }

  // 开始轮询
  const startPolling = (evalId: string) => {
    // 清除现有轮询
    if (pollingInterval) {
      clearInterval(pollingInterval)
    }
    
    // 每3秒轮询一次
    const interval = setInterval(() => {
      loadProgress(evalId)
    }, 3000)
    
    setPollingInterval(interval)
  }

  // 停止轮询
  const stopPolling = () => {
    if (pollingInterval) {
      clearInterval(pollingInterval)
      setPollingInterval(null)
    }
  }

  // 关闭弹窗时停止轮询
  const handleCloseDetail = () => {
    stopPolling()
    setDetailModalVisible(false)
    setSelectedEval(null)
    setProgress(null)
  }

  // 启动任务
  const handleStart = async (evalId: string) => {
    try {
      await evaluationsApi.start(evalId)
      message.success('任务已启动')
      loadEvaluations()
    } catch (error: any) {
      message.error(error.response?.data?.detail || '启动失败')
    }
  }

  // 取消任务
  const handleCancel = async (evalId: string) => {
    try {
      await evaluationsApi.cancel(evalId)
      message.success('任务已取消')
      loadEvaluations()
    } catch (error: any) {
      message.error(error.response?.data?.detail || '取消失败')
    }
  }

  // 删除任务
  const handleDelete = async (evalId: string) => {
    try {
      await evaluationsApi.delete(evalId)
      message.success('任务已删除')
      loadEvaluations()
    } catch (error: any) {
      message.error(error.response?.data?.detail || '删除失败')
    }
  }

  // 获取状态标签
  const getStatusTag = (status: string) => {
    const statusMap: Record<string, { color: string; icon: React.ReactNode; text: string; bgColor: string }> = {
      pending: { color: GOOGLE_COLORS.gray, icon: <ClockCircleOutlined />, text: '待运行', bgColor: GOOGLE_COLORS.gray + '20' },
      running: { color: GOOGLE_COLORS.blue, icon: <ReloadOutlined spin />, text: '运行中', bgColor: GOOGLE_COLORS.blue + '20' },
      success: { color: GOOGLE_COLORS.green, icon: <CheckCircleOutlined />, text: '已完成', bgColor: GOOGLE_COLORS.green + '20' },
      failed: { color: GOOGLE_COLORS.red, icon: <CloseCircleOutlined />, text: '失败', bgColor: GOOGLE_COLORS.red + '20' },
    }
    const { color, icon, text, bgColor } = statusMap[status] || statusMap.pending
    return (
      <Tag 
        icon={icon} 
        style={{ 
          background: bgColor, 
          color: color, 
          border: 'none',
          borderRadius: '4px'
        }}
      >
        {text}
      </Tag>
    )
  }

  const columns = [
    {
      title: '任务 ID',
      dataIndex: 'id',
      ellipsis: true,
      render: (id: string) => (
        <code style={{ fontSize: 12, color: GOOGLE_COLORS.gray, fontFamily: 'monospace' }}>
          {id.slice(0, 12)}...
        </code>
      ),
    },
    {
      title: '状态',
      dataIndex: 'status',
      width: 120,
      render: (status: string) => getStatusTag(status),
    },
    {
      title: 'Prompt 版本',
      dataIndex: 'version_id',
      ellipsis: true,
      render: (versionId: string) => {
        const version = versions[versionId]
        return version ? (
          <Tag style={{ background: GOOGLE_COLORS.blue + '20', color: GOOGLE_COLORS.blue, border: 'none', borderRadius: '4px' }}>
            v{version.version_number}
          </Tag>
        ) : (
          <Text type="secondary" style={{ color: GOOGLE_COLORS.gray }}>{versionId.slice(0, 8)}...</Text>
        )
      },
    },
    {
      title: 'Benchmark',
      dataIndex: 'benchmark',
      width: 150,
      render: (benchmark: string) => (
        <Text style={{ color: GOOGLE_COLORS.gray }}>{benchmark}</Text>
      ),
    },
    {
      title: '样本数',
      dataIndex: 'num_examples',
      width: 100,
      render: (num: number | undefined) => (
        <Text style={{ color: GOOGLE_COLORS.gray }}>{num || '全部'}</Text>
      ),
    },
    {
      title: '创建时间',
      dataIndex: 'created_at',
      width: 180,
      render: (date: string) => (
        <Text style={{ color: GOOGLE_COLORS.gray }}>{dayjs(date).format('MM-DD HH:mm')}</Text>
      ),
    },
    {
      title: '结果',
      dataIndex: 'result_summary',
      width: 120,
      render: (summary: any) => {
        if (!summary) return <Text style={{ color: GOOGLE_COLORS.gray }}>-</Text>
        return (
          <Text strong style={{ color: GOOGLE_COLORS.green }}>
            {(summary.overall_score * 100).toFixed(1)}%
          </Text>
        )
      },
    },
    {
      title: '操作',
      width: 200,
      render: (_: any, record: EvaluationListItem) => (
        <Space>
          <Button 
            type="text" 
            icon={<EyeOutlined style={{ color: GOOGLE_COLORS.blue }} />} 
            onClick={() => handleViewDetail(record.id)}
            style={{ color: GOOGLE_COLORS.blue }}
          >
            查看
          </Button>
          {record.status === 'pending' && (
            <Button 
              type="text" 
              icon={<PlayCircleOutlined style={{ color: GOOGLE_COLORS.green }} />}
              onClick={() => handleStart(record.id)}
              style={{ color: GOOGLE_COLORS.green }}
            >
              启动
            </Button>
          )}
          {record.status === 'running' && (
            <Popconfirm
              title="确定取消此任务吗？"
              onConfirm={() => handleCancel(record.id)}
            >
              <Button type="text" icon={<PauseCircleOutlined style={{ color: GOOGLE_COLORS.red }} />} style={{ color: GOOGLE_COLORS.red }}>
                取消
              </Button>
            </Popconfirm>
          )}
          {record.status !== 'running' && (
            <Popconfirm
              title="确定删除此任务吗？"
              onConfirm={() => handleDelete(record.id)}
            >
              <Button type="text" icon={<DeleteOutlined style={{ color: GOOGLE_COLORS.red }} />} style={{ color: GOOGLE_COLORS.red }}>
                删除
              </Button>
            </Popconfirm>
          )}
        </Space>
      ),
    },
  ]

  return (
    <Card 
      style={{ 
        borderRadius: '16px', 
        boxShadow: '0 1px 2px rgba(60,64,67,0.1), 0 1px 3px rgba(60,64,67,0.08)',
        border: 'none'
      }}
      bodyStyle={{ padding: '24px' }}
    >
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 24 }}>
        <Title level={4} style={{ margin: 0, color: GOOGLE_COLORS.gray, fontWeight: 500 }}>Eval 任务管理</Title>
        <Link to="/new-eval">
          <Button 
            type="primary" 
            icon={<PlusOutlined />}
            style={{ 
              borderRadius: '8px', 
              background: GOOGLE_COLORS.blue,
              border: 'none',
              boxShadow: 'none'
            }}
          >
            新建 Eval
          </Button>
        </Link>
      </div>

      <Table
        dataSource={evaluations}
        columns={columns}
        rowKey="id"
        loading={loading}
        style={{ 
          '.ant-table-thead > tr > th': {
            background: GOOGLE_COLORS.lightGray,
            color: GOOGLE_COLORS.gray,
            fontWeight: 500
          }
        }}
      />

      {/* 详情弹窗 */}
      <Modal
        title={<span style={{ color: GOOGLE_COLORS.gray, fontWeight: 500 }}>任务详情</span>}
        open={detailModalVisible}
        onCancel={handleCloseDetail}
        width={1000}
        style={{ borderRadius: '16px' }}
        footer={[
          <Button 
            key="close" 
            onClick={handleCloseDetail}
            style={{ borderRadius: '8px' }}
          >
            关闭
          </Button>,
        ]}
      >
        {selectedEval && (
          <div>
            <Descriptions 
              bordered 
              column={2} 
              style={{ marginBottom: 24 }}
              labelStyle={{ background: GOOGLE_COLORS.lightGray, color: GOOGLE_COLORS.gray }}
              contentStyle={{ color: GOOGLE_COLORS.gray }}
            >
              <Descriptions.Item label="状态">
                {getStatusTag(selectedEval.status)}
              </Descriptions.Item>
              <Descriptions.Item label="Benchmark">
                {selectedEval.benchmark}
              </Descriptions.Item>
              <Descriptions.Item label="Prompt 版本">
                {versions[selectedEval.version_id] ? (
                  <Tag style={{ background: GOOGLE_COLORS.blue + '20', color: GOOGLE_COLORS.blue, border: 'none', borderRadius: '4px' }}>
                    v{versions[selectedEval.version_id].version_number}
                  </Tag>
                ) : selectedEval.version_id}
              </Descriptions.Item>
              <Descriptions.Item label="样本数">
                {selectedEval.num_examples || '全部'}
              </Descriptions.Item>
              <Descriptions.Item label="并行数">
                {selectedEval.n_threads} 线程
              </Descriptions.Item>
              <Descriptions.Item label="创建时间">
                {dayjs(selectedEval.created_at).format('YYYY-MM-DD HH:mm:ss')}
              </Descriptions.Item>
              {selectedEval.started_at && (
                <Descriptions.Item label="开始时间">
                  {dayjs(selectedEval.started_at).format('YYYY-MM-DD HH:mm:ss')}
                </Descriptions.Item>
              )}
              {selectedEval.completed_at && (
                <Descriptions.Item label="完成时间">
                  {dayjs(selectedEval.completed_at).format('YYYY-MM-DD HH:mm:ss')}
                </Descriptions.Item>
              )}
            </Descriptions>

            {/* 进度显示 */}
            {progress && selectedEval.status !== 'pending' && (
              <Card 
                title={<span style={{ color: GOOGLE_COLORS.gray, fontWeight: 500 }}>运行进度</span>}
                style={{ 
                  marginBottom: 24, 
                  borderRadius: '12px', 
                  border: 'none',
                  boxShadow: '0 1px 2px rgba(60,64,67,0.1)'
                }}
              >
                <Progress 
                  percent={Math.round((progress.completed / progress.total) * 100)}
                  status={selectedEval.status === 'failed' ? 'exception' : 'active'}
                  format={(percent) => `${progress.completed}/${progress.total} (${percent}%)`}
                  strokeColor={GOOGLE_COLORS.blue}
                />
                <div style={{ marginTop: 16 }}>
                  <Text style={{ color: GOOGLE_COLORS.gray }}>当前分数: </Text>
                  <Text strong style={{ fontSize: 18, color: GOOGLE_COLORS.blue }}>
                    {progress.current_score ? (progress.current_score * 100).toFixed(1) : '-'}%
                  </Text>
                </div>
              </Card>
            )}

            {/* 实时问答流 */}
            {progress && progress.latest_samples.length > 0 && (
              <Card 
                title={<span style={{ color: GOOGLE_COLORS.gray, fontWeight: 500 }}>实时问答</span>}
                style={{ 
                  marginBottom: 24, 
                  borderRadius: '12px', 
                  border: 'none',
                  boxShadow: '0 1px 2px rgba(60,64,67,0.1)'
                }}
              >
                <Timeline
                  items={progress.latest_samples.map((sample, index) => ({
                    key: index,
                    dot: <Badge count={sample.index} style={{ backgroundColor: GOOGLE_COLORS.blue }} />,
                    children: (
                      <div style={{ marginBottom: 16 }}>
                        <div style={{ marginBottom: 8 }}>
                          <Text type="secondary" style={{ color: GOOGLE_COLORS.gray }}>问题:</Text>
                          <div style={{ color: GOOGLE_COLORS.gray }}>{sample.question}</div>
                        </div>
                        <div style={{ marginBottom: 8 }}>
                          <Text type="secondary" style={{ color: GOOGLE_COLORS.gray }}>回答:</Text>
                          <div style={{ color: GOOGLE_COLORS.gray }}>{sample.answer}</div>
                        </div>
                        <div>
                          <Tag 
                            style={{ 
                              background: sample.score > 0.7 ? GOOGLE_COLORS.green + '20' : sample.score > 0.4 ? GOOGLE_COLORS.yellow + '20' : GOOGLE_COLORS.red + '20',
                              color: sample.score > 0.7 ? GOOGLE_COLORS.green : sample.score > 0.4 ? GOOGLE_COLORS.yellow : GOOGLE_COLORS.red,
                              border: 'none',
                              borderRadius: '4px'
                            }}
                          >
                            分数: {(sample.score * 100).toFixed(0)}%
                          </Tag>
                        </div>
                      </div>
                    ),
                  }))}
                />
              </Card>
            )}

            {/* 最终结果 */}
            {selectedEval.result_summary && (
              <Card 
                title={<span style={{ color: GOOGLE_COLORS.gray, fontWeight: 500 }}>评估结果</span>}
                style={{ 
                  borderRadius: '12px', 
                  border: 'none',
                  boxShadow: '0 1px 2px rgba(60,64,67,0.1)'
                }}
              >
                <div style={{ textAlign: 'center', marginBottom: 24 }}>
                  <Text style={{ fontSize: 16, color: GOOGLE_COLORS.gray }}>总体分数</Text>
                  <div style={{ fontSize: 48, fontWeight: 'bold', color: GOOGLE_COLORS.green }}>
                    {(selectedEval.result_summary.overall_score * 100).toFixed(1)}%
                  </div>
                </div>
                {selectedEval.result_summary.metrics && (
                  <Descriptions 
                    bordered 
                    column={3}
                    labelStyle={{ background: GOOGLE_COLORS.lightGray, color: GOOGLE_COLORS.gray }}
                    contentStyle={{ color: GOOGLE_COLORS.gray }}
                  >
                    {Object.entries(selectedEval.result_summary.metrics).map(([key, value]: [string, any]) => (
                      <Descriptions.Item key={key} label={key}>
                        <Text strong style={{ color: GOOGLE_COLORS.blue }}>{(value * 100).toFixed(1)}%</Text>
                      </Descriptions.Item>
                    ))}
                  </Descriptions>
                )}
              </Card>
            )}

            {/* 错误信息 */}
            {selectedEval.error_message && (
              <Card 
                title={<span style={{ color: GOOGLE_COLORS.gray, fontWeight: 500 }}>错误信息</span>}
                style={{ 
                  marginTop: 24, 
                  borderRadius: '12px', 
                  border: 'none',
                  boxShadow: '0 1px 2px rgba(60,64,67,0.1)',
                  background: GOOGLE_COLORS.red + '10'
                }}
              >
                <Text type="danger" style={{ color: GOOGLE_COLORS.red }}>{selectedEval.error_message}</Text>
              </Card>
            )}
          </div>
        )}
      </Modal>
    </Card>
  )
}
