import { useState, useEffect } from 'react'
import { 
  Card, 
  Button, 
  Table, 
  Modal, 
  Form, 
  Input, 
  message, 
  Tag,
  Space,
  Typography,
  Timeline,
  Row,
  Col,
  Tabs,
  Empty,
  Popconfirm
} from 'antd'
import { 
  PlusOutlined, 
  CheckCircleOutlined, 
  HistoryOutlined,
  ExportOutlined,
  ImportOutlined,
  DeleteOutlined,
  EyeOutlined,
  DiffOutlined
} from '@ant-design/icons'
import { versionsApi } from '../api/versions'
import { configsApi } from '../api/configs'
import type { PromptVersion, PromptVersionListItem, PromptFileConfig } from '../types'
import dayjs from 'dayjs'

const { Title, Text, Paragraph } = Typography
const { TextArea } = Input

export default function VersionsPage() {
  const [versions, setVersions] = useState<PromptVersionListItem[]>([])
  const [activeVersion, setActiveVersion] = useState<PromptVersion | null>(null)
  const [configs, setConfigs] = useState<PromptFileConfig[]>([])
  const [loading, setLoading] = useState(false)
  const [modalVisible, setModalVisible] = useState(false)
  const [detailModalVisible, setDetailModalVisible] = useState(false)
  const [selectedVersion, setSelectedVersion] = useState<PromptVersion | null>(null)
  const [form] = Form.useForm()
  const [fileContents, setFileContents] = useState<Record<string, string>>({})

  // 加载数据
  const loadData = async () => {
    setLoading(true)
    try {
      const [versionsRes, activeRes, configsRes] = await Promise.all([
        versionsApi.getAll(),
        versionsApi.getActive(),
        configsApi.getAll(),
      ])
      setVersions(versionsRes.data)
      setActiveVersion(activeRes.data)
      setConfigs(configsRes.data)
    } catch (error) {
      message.error('加载数据失败')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadData()
  }, [])

  // 打开创建版本弹窗
  const handleCreate = () => {
    form.resetFields()
    // 如果有活跃版本，使用其内容作为初始值
    const initialContents: Record<string, string> = {}
    if (activeVersion) {
      activeVersion.files.forEach(f => {
        initialContents[f.config_key] = f.content
      })
    } else {
      configs.forEach(c => {
        initialContents[c.key] = `# ${c.name}\n\n`
      })
    }
    setFileContents(initialContents)
    setModalVisible(true)
  }

  // 保存新版本
  const handleSave = async (values: any) => {
    try {
      const files = Object.entries(fileContents).map(([config_key, content]) => ({
        config_key,
        content,
      }))

      await versionsApi.create({
        author: values.author,
        description: values.description,
        parent_version_id: activeVersion?.id,
        files,
      })
      message.success('版本已创建')
      setModalVisible(false)
      loadData()
    } catch (error: any) {
      message.error(error.response?.data?.detail || '创建失败')
    }
  }

  // 激活版本
  const handleActivate = async (versionId: string) => {
    try {
      const response = await versionsApi.activate(versionId)
      message.success(response.data.message)
      loadData()
    } catch (error: any) {
      message.error(error.response?.data?.detail || '激活失败')
    }
  }

  // 查看版本详情
  const handleViewDetail = async (versionId: string) => {
    try {
      const response = await versionsApi.getById(versionId)
      setSelectedVersion(response.data)
      setDetailModalVisible(true)
    } catch (error) {
      message.error('加载详情失败')
    }
  }

  // 从外置系统导入
  const handleImport = async () => {
    try {
      await versionsApi.importFromExternal('system', '从外置系统导入')
      message.success('导入成功')
      loadData()
    } catch (error: any) {
      message.error(error.response?.data?.detail || '导入失败')
    }
  }

  // 删除版本
  const handleDelete = async (versionId: string) => {
    try {
      await versionsApi.delete(versionId)
      message.success('版本已删除')
      loadData()
    } catch (error: any) {
      message.error(error.response?.data?.detail || '删除失败')
    }
  }

  const columns = [
    {
      title: '序号',
      width: 80,
      render: (_: any, __: PromptVersionListItem, index: number) => (
        <Space>
          <Text strong>#{versions.length - index}</Text>
        </Space>
      ),
    },
    {
      title: 'ID',
      dataIndex: 'id',
      ellipsis: true,
      render: (id: string) => <code style={{ fontSize: 12 }}>{id}</code>,
    },
    {
      title: '创建时间',
      dataIndex: 'created_at',
      width: 180,
      render: (date: string) => dayjs(date).format('YYYY-MM-DD HH:mm:ss'),
    },
    {
      title: '作者',
      dataIndex: 'author',
      width: 120,
    },
    {
      title: '描述',
      dataIndex: 'description',
      ellipsis: true,
    },
    {
      title: '操作',
      width: 250,
      render: (_: any, record: PromptVersionListItem) => (
        <Space>
          <Button 
            type="text" 
            icon={<EyeOutlined />} 
            onClick={() => handleViewDetail(record.id)}
          >
            查看
          </Button>
          {!record.is_active && (
            <Button 
              type="text" 
              icon={<CheckCircleOutlined />}
              onClick={() => handleActivate(record.id)}
            >
              生效
            </Button>
          )}
          <Popconfirm
            title="确定删除此版本吗？"
            description="删除后无法恢复"
            onConfirm={() => handleDelete(record.id)}
          >
            <Button type="text" danger icon={<DeleteOutlined />}>
              删除
            </Button>
          </Popconfirm>
        </Space>
      ),
    },
  ]

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 16 }}>
        <Title level={4}>Prompt 版本管理</Title>
        <Space>
          <Button icon={<ImportOutlined />} onClick={handleImport}>
            从外置导入
          </Button>
          <Button type="primary" icon={<PlusOutlined />} onClick={handleCreate}>
            新建版本
          </Button>
        </Space>
      </div>

      {activeVersion && (
        <Card style={{ marginBottom: 16 }}>
          <Row align="middle">
            <Col flex="auto">
              <Space>
                <CheckCircleOutlined style={{ color: '#52c41a', fontSize: 24 }} />
                <div>
                  <Text strong>当前生效版本</Text>
                  <br />
                  <Text type="secondary">
                    {activeVersion.id} · {dayjs(activeVersion.created_at).format('YYYY-MM-DD HH:mm:ss')} · {activeVersion.author}
                  </Text>
                </div>
              </Space>
            </Col>
            <Col>
              <Text type="warning">
                注意：另一个项目需要重启才能读取新版本
              </Text>
            </Col>
          </Row>
        </Card>
      )}

      <Table
        dataSource={versions}
        columns={columns}
        rowKey="id"
        loading={loading}
      />

      {/* 创建版本弹窗 */}
      <Modal
        title="新建 Prompt 版本"
        open={modalVisible}
        onOk={form.submit}
        onCancel={() => setModalVisible(false)}
        width={900}
        okText="创建版本"
      >
        <Form
          form={form}
          layout="vertical"
          onFinish={handleSave}
        >
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                name="author"
                label="作者"
                rules={[{ required: true, message: '请输入作者' }]}
              >
                <Input placeholder="你的名字" />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                name="description"
                label="版本描述"
                rules={[{ required: true, message: '请输入版本描述' }]}
              >
                <Input placeholder="描述此版本的改动内容" />
              </Form.Item>
            </Col>
          </Row>
        </Form>

        <Tabs
          items={configs.map(config => ({
            key: config.key,
            label: config.name,
            children: (
              <TextArea
                value={fileContents[config.key] || ''}
                onChange={e => setFileContents({
                  ...fileContents,
                  [config.key]: e.target.value
                })}
                rows={20}
                style={{ fontFamily: 'monospace' }}
              />
            ),
          }))}
        />
      </Modal>

      {/* 版本详情弹窗 */}
      <Modal
        title={`版本详情: ${selectedVersion?.id}`}
        open={detailModalVisible}
        onCancel={() => setDetailModalVisible(false)}
        width={900}
        footer={null}
      >
        {selectedVersion && (
          <div>
            <Paragraph>
              <Text strong>版本 ID:</Text> {selectedVersion.id}
              <br />
              <Text strong>作者:</Text> {selectedVersion.author}
              <br />
              <Text strong>创建时间:</Text> {dayjs(selectedVersion.created_at).format('YYYY-MM-DD HH:mm:ss')}
              <br />
              <Text strong>描述:</Text> {selectedVersion.description || '无'}
              <br />
              {selectedVersion.is_active && <Tag color="green">当前生效</Tag>}
            </Paragraph>

            <Tabs
              items={selectedVersion.files.map(file => ({
                key: file.config_key,
                label: configs.find(c => c.key === file.config_key)?.name || file.config_key,
                children: (
                  <pre style={{ 
                    background: '#f6f8fa', 
                    padding: 16, 
                    borderRadius: 8,
                    maxHeight: 400,
                    overflow: 'auto'
                  }}>
                    <code>{file.content}</code>
                  </pre>
                ),
              }))}
            />
          </div>
        )}
      </Modal>
    </div>
  )
}
