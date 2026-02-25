import { useState, useEffect, useRef } from 'react'
import {
  Card,
  Button,
  Table,
  Modal,
  Form,
  Input,
  message,
  Space,
  Typography,
  Empty,
  Tooltip,
  Spin
} from 'antd'
import { PlusOutlined, EditOutlined, DeleteOutlined, CheckCircleOutlined, CloseCircleOutlined, EyeOutlined, MenuOutlined } from '@ant-design/icons'
import { configsApi } from '../api/configs'
import type { PromptFileConfig } from '../types'
import type { ColumnsType } from 'antd/es/table'
import { arrayMoveImmutable } from 'array-move'

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

// 可拖拽表格组件
interface SortableTableProps {
  dataSource: PromptFileConfig[]
  columns: ColumnsType<PromptFileConfig>
  rowKey: string
  loading: boolean
  pagination: false
  onDragSort: (oldIndex: number, newIndex: number) => void
}

function SortableTable({ dataSource, columns, rowKey, loading, onDragSort }: SortableTableProps) {
  const [draggingIndex, setDraggingIndex] = useState<number | null>(null)
  const [dragOverIndex, setDragOverIndex] = useState<number | null>(null)
  const tableRef = useRef<HTMLDivElement>(null)

  const handleDragStart = (index: number) => {
    setDraggingIndex(index)
  }

  const handleDragOver = (e: React.DragEvent, index: number) => {
    e.preventDefault()
    if (draggingIndex !== null && draggingIndex !== index) {
      setDragOverIndex(index)
    }
  }

  const handleDragLeave = () => {
    setDragOverIndex(null)
  }

  const handleDrop = (e: React.DragEvent, index: number) => {
    e.preventDefault()
    if (draggingIndex !== null && draggingIndex !== index) {
      onDragSort(draggingIndex, index)
    }
    setDraggingIndex(null)
    setDragOverIndex(null)
  }

  const handleDragEnd = () => {
    setDraggingIndex(null)
    setDragOverIndex(null)
  }

  // 添加拖拽手柄列
  const columnsWithDrag = [
    {
      title: '',
      width: 50,
      render: (_: any, __: any, index: number) => (
        <div
          draggable
          onDragStart={() => handleDragStart(index)}
          onDragOver={(e) => handleDragOver(e, index)}
          onDragLeave={handleDragLeave}
          onDrop={(e) => handleDrop(e, index)}
          onDragEnd={handleDragEnd}
          style={{
            cursor: 'move',
            opacity: draggingIndex === index ? 0.5 : 1,
            background: dragOverIndex === index ? '#e8f0fe' : 'transparent',
            padding: '8px',
            borderRadius: '4px',
            transition: 'background 0.2s'
          }}
        >
          <MenuOutlined style={{ color: GOOGLE_COLORS.gray }} />
        </div>
      )
    },
    ...columns
  ]

  return (
    <div ref={tableRef}>
      <Table
        dataSource={dataSource}
        columns={columnsWithDrag}
        rowKey={rowKey}
        loading={loading}
        pagination={false}
        rowClassName={(_, index) => 
          dragOverIndex === index ? 'drag-over-row' : ''
        }
      />
      <style>{`
        .drag-over-row {
          background-color: #e8f0fe !important;
        }
        .drag-over-row td {
          border-top: 2px dashed ${GOOGLE_COLORS.blue} !important;
          border-bottom: 2px dashed ${GOOGLE_COLORS.blue} !important;
        }
      `}</style>
    </div>
  )
}

// 文件内容预览组件
function FileContentPreview({ path }: { path: string }) {
  const [content, setContent] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchContent = async () => {
      setLoading(true)
      try {
        const response = await configsApi.testPath(path)
        if (response.data.readable) {
          setContent(response.data.content || '')
          setError(null)
        } else {
          setError(response.data.error || '读取失败')
          setContent(null)
        }
      } catch (err) {
        setError('读取失败')
        setContent(null)
      } finally {
        setLoading(false)
      }
    }
    fetchContent()
  }, [path])

  if (loading) {
    return <Spin size="small" />
  }

  if (error) {
    return <Text type="danger">{error}</Text>
  }

  return (
    <pre style={{ 
      marginTop: 8, 
      fontSize: 12, 
      whiteSpace: 'pre-wrap', 
      wordBreak: 'break-word',
      color: '#262626'
    }}>
      {content}
    </pre>
  )
}

export default function ConfigsPage() {
  const [configs, setConfigs] = useState<PromptFileConfig[]>([])
  const [loading, setLoading] = useState(false)
  const [modalVisible, setModalVisible] = useState(false)
  const [editingConfig, setEditingConfig] = useState<PromptFileConfig | null>(null)
  const [form] = Form.useForm()
  const [testingPath, setTestingPath] = useState<string | null>(null)
  const [pathTestResult, setPathTestResult] = useState<{ readable: boolean; content?: string; error?: string } | null>(null)


  // 加载配置列表
  const loadConfigs = async () => {
    setLoading(true)
    try {
      const response = await configsApi.getAll()
      setConfigs(response.data)
    } catch (error) {
      message.error('加载配置失败')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadConfigs()
  }, [])

  // 打开创建弹窗
  const handleCreate = () => {
    setEditingConfig(null)
    form.resetFields()
    setPathTestResult(null)
    setModalVisible(true)
  }

  // 打开编辑弹窗
  const handleEdit = (config: PromptFileConfig) => {
    setEditingConfig(config)
    form.setFieldsValue({
      name: config.name,
      description: config.description,
      external_path: config.external_path,
    })
    setPathTestResult(null)
    setModalVisible(true)
  }

  // 生成 uuid 作为 key
  const generateKey = (): string => {
    return crypto.randomUUID()
  }

  // 保存配置
  const handleSave = async (values: any) => {
    try {
      if (editingConfig) {
        await configsApi.update(editingConfig.key, values)
        message.success('配置已更新')
      } else {
        // 自动生成 key
        const key = generateKey()
        await configsApi.create({
          ...values,
          key,
          sort_order: configs.length + 1,
        })
        message.success('配置已创建')
      }
      setModalVisible(false)
      loadConfigs()
    } catch (error: any) {
      message.error(error.response?.data?.detail || '保存失败')
    }
  }

  // 删除配置
  const handleDelete = async (key: string, force: boolean = false) => {
    try {
      const response = await configsApi.delete(key, force)
      message.success(response.data.message)
      loadConfigs()
    } catch (error: any) {
      const status = error.response?.status
      const detail = error.response?.data?.detail
      
      // 409 表示有版本引用，需要二次确认
      if (status === 409 && detail) {
        Modal.confirm({
          title: '确认删除',
          content: detail,
          okText: '确认删除',
          okType: 'danger',
          cancelText: '取消',
          onOk: () => handleDelete(key, true), // 强制删除
        })
      } else {
        message.error(detail || '删除失败')
      }
    }
  }

  // 测试文件路径
  const handleTestPath = async () => {
    const path = form.getFieldValue('external_path')
    if (!path) {
      message.warning('请先输入外置文件路径')
      return
    }

    setTestingPath(path)
    try {
      const response = await configsApi.testPath(path)
      setPathTestResult(response.data)
      if (response.data.readable) {
        message.success('文件可读')
      } else {
        message.error(response.data.error || '无法读取文件')
      }
    } catch (error) {
      message.error('测试失败')
    } finally {
      setTestingPath(null)
    }
  }

  // 处理拖拽排序
  const handleDragSort = (oldIndex: number, newIndex: number) => {
    if (oldIndex === newIndex) return
    
    const newConfigs = arrayMoveImmutable(configs, oldIndex, newIndex)
    // 更新排序号（从1开始）
    const updatedConfigs = newConfigs.map((config, index) => ({
      ...config,
      sort_order: index + 1
    }))
    setConfigs(updatedConfigs)
    
    // 保存到后端
    const keys = updatedConfigs.map(c => c.key)
    configsApi.reorder(keys).catch(() => {
      message.error('保存排序失败')
      loadConfigs() // 重新加载
    })
  }

  const columns: ColumnsType<PromptFileConfig> = [
    {
      title: '排序',
      dataIndex: 'sort_order',
      width: 80,
      render: (order: number) => <Text type="secondary" style={{ color: GOOGLE_COLORS.gray }}>{order}</Text>,
    },
    {
      title: 'Prompt 名称',
      dataIndex: 'name',
      render: (name: string, record: PromptFileConfig) => (
        <Tooltip
          title={
            <div style={{ 
              width: '50vw',
              maxHeight: '50vh', 
              overflow: 'auto',
              padding: '12px'
            }}>
              <Text strong style={{ color: '#262626' }}>文件内容预览:</Text>
              <FileContentPreview path={record.external_path} />
            </div>
          }
          placement="topLeft"
          color="#fafafa"
          overlayStyle={{ 
            maxWidth: 'none',
            boxShadow: '0 4px 12px rgba(0,0,0,0.15)'
          }}
          mouseEnterDelay={0}
        >
          <span style={{ cursor: 'help', textDecoration: 'underline dotted', color: GOOGLE_COLORS.blue }}>{name}</span>
        </Tooltip>
      ),
    },
    {
      title: '描述',
      dataIndex: 'description',
      ellipsis: true,
      render: (desc: string) => <Text style={{ color: GOOGLE_COLORS.gray }}>{desc}</Text>,
    },
    {
      title: '外置文件路径',
      dataIndex: 'external_path',
      ellipsis: true,
      render: (path: string) => (
        <Text ellipsis style={{ maxWidth: 300, color: GOOGLE_COLORS.gray, fontFamily: 'monospace', fontSize: '12px' }}>
          {path}
        </Text>
      ),
    },
    {
      title: '操作',
      width: 150,
      render: (_: any, record: PromptFileConfig) => (
        <Space>
          <Button
            type="text"
            icon={<EditOutlined style={{ color: GOOGLE_COLORS.blue }} />}
            onClick={() => handleEdit(record)}
            style={{ borderRadius: '8px' }}
          />
          <Button 
            type="text" 
            icon={<DeleteOutlined style={{ color: GOOGLE_COLORS.red }} />} 
            onClick={() => handleDelete(record.key)}
            style={{ borderRadius: '8px' }}
          />
        </Space>
      ),
    },
  ]

  return (
    <>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 24 }}>
        <Title level={4} style={{ margin: 0, color: GOOGLE_COLORS.gray, fontWeight: 500 }}>Prompt 配置</Title>
        <Button 
          type="primary" 
          icon={<PlusOutlined />} 
          onClick={handleCreate}
          style={{ 
            borderRadius: '8px', 
            background: GOOGLE_COLORS.blue,
            border: 'none',
            boxShadow: 'none'
          }}
        >
          添加配置
        </Button>
      </div>

      <Card 
        style={{ 
          borderRadius: '16px', 
          boxShadow: '0 1px 2px rgba(60,64,67,0.1), 0 1px 3px rgba(60,64,67,0.08)',
          border: 'none'
        }}
        bodyStyle={{ padding: '24px' }}
      >
        <Text type="secondary" style={{ display: 'block', marginBottom: 24, color: GOOGLE_COLORS.gray }}>
          配置 Prompt 文件的名称和外置路径。每个配置对应一个 Prompt 文件，用于版本管理。
        </Text>

        {configs.length === 0 ? (
          <Empty description="暂无配置，请先添加 Prompt 文件配置">
            <Button 
              type="primary" 
              onClick={handleCreate}
              style={{ 
                borderRadius: '8px', 
                background: GOOGLE_COLORS.blue,
                border: 'none'
              }}
            >
              立即添加
            </Button>
          </Empty>
        ) : (
          <SortableTable
            dataSource={configs}
            columns={columns}
            rowKey="key"
            loading={loading}
            pagination={false}
            onDragSort={handleDragSort}
          />
        )}
      </Card>

      <Modal
        title={editingConfig ? '编辑配置' : '添加配置'}
        open={modalVisible}
        onOk={form.submit}
        onCancel={() => setModalVisible(false)}
        width={600}
        style={{ borderRadius: '16px' }}
      >
        {/* 标题下方分割线 */}
        <div style={{ borderBottom: `1px solid ${GOOGLE_COLORS.border}`, marginBottom: '24px', marginTop: '16px' }} />
        <Form
          form={form}
          layout="vertical"
          onFinish={handleSave}
        >
          <Form.Item
            name="name"
            label="Prompt 名称"
            rules={[{ required: true, message: '请输入 Prompt 名称' }]}
          >
            <Input 
              placeholder="如: 意图识别" 
              style={{ borderRadius: '8px', border: `1px solid ${GOOGLE_COLORS.border}` }}
            />
          </Form.Item>

          <Form.Item
            name="description"
            label="描述"
          >
            <Input.TextArea 
              rows={4} 
              placeholder="简要描述此 Prompt 的用途" 
              style={{ borderRadius: '8px', border: `1px solid ${GOOGLE_COLORS.border}` }}
            />
          </Form.Item>

          <Form.Item
            name="external_path"
            label="外置文件路径"
            rules={[{ required: true, message: '请输入外置文件路径' }]}
          >
            <Input
              placeholder="如: /path/to/project/prompts/intent.md"
              style={{ borderRadius: '8px', border: `1px solid ${GOOGLE_COLORS.border}` }}
              addonAfter={
                <Tooltip title="测试文件路径">
                  <Button
                    type="text"
                    size="small"
                    icon={testingPath ? <Spin size="small" /> : (pathTestResult?.readable ? <CheckCircleOutlined style={{ color: GOOGLE_COLORS.green }} /> : <EyeOutlined />)}
                    onClick={handleTestPath}
                    loading={testingPath === form.getFieldValue('external_path')}
                    style={{ margin: -4 }}
                  />
                </Tooltip>
              }
            />
          </Form.Item>

          {pathTestResult && (
            <div style={{ 
              marginTop: 8, 
              padding: 16, 
              background: pathTestResult.readable ? '#e8f0fe' : '#fce8e6', 
              borderRadius: '8px', 
              border: `1px solid ${pathTestResult.readable ? GOOGLE_COLORS.blue : GOOGLE_COLORS.red}` 
            }}>
              {pathTestResult.readable ? (
                <div>
                  <Text type="success" strong style={{ color: GOOGLE_COLORS.green }}><CheckCircleOutlined /> 文件可读</Text>
                  <pre style={{ 
                    marginTop: 8, 
                    maxHeight: 200, 
                    overflow: 'auto', 
                    background: GOOGLE_COLORS.white, 
                    padding: 12, 
                    borderRadius: '8px',
                    border: `1px solid ${GOOGLE_COLORS.border}`
                  }}>
                    <code>{pathTestResult.content}</code>
                  </pre>
                </div>
              ) : (
                <Text type="danger" style={{ color: GOOGLE_COLORS.red }}><CloseCircleOutlined /> {pathTestResult.error || '无法读取文件'}</Text>
              )}
            </div>
          )}
        </Form>
      </Modal>
    </>
  )
}
