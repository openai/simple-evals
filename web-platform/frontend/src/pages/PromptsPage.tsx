import { useState, useEffect, useCallback, useRef } from 'react'
import {
  Card,
  Button,
  Tabs,
  Input,
  Tag,
  Space,
  Typography,
  message,
  Popconfirm,
  Modal,
  Form,
  Row,
  Col,
  Tooltip
} from 'antd'
import {
  PlusOutlined,
  DeleteOutlined,
  CheckCircleOutlined,
  SaveOutlined,
  ExclamationCircleOutlined,
  FileTextOutlined,
  InfoCircleOutlined
} from '@ant-design/icons'
import { configsApi } from '../api/configs'
import { promptsApi, type PromptVersionSimple } from '../api/prompts'
import type { PromptFileConfig } from '../types'
import dayjs from 'dayjs'

const { Title, Text } = Typography
const { TextArea } = Input
const { TabPane } = Tabs

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

interface VersionData {
  id: string
  version_number: number
  content: string
  is_active: boolean
  created_at: string
  author: string
  description?: string
}

export default function PromptsPage() {
  const [configs, setConfigs] = useState<PromptFileConfig[]>([])
  const [activeKey, setActiveKey] = useState<string>('')
  const [versions, setVersions] = useState<VersionData[]>([])
  const [selectedVersionId, setSelectedVersionId] = useState<string | null>(null)
  const [editorContent, setEditorContent] = useState('')
  const [originalContent, setOriginalContent] = useState('')
  const [loading, setLoading] = useState(false)
  const [saveModalVisible, setSaveModalVisible] = useState(false)
  const [saveForm] = Form.useForm()
  const [activeVersionId, setActiveVersionId] = useState<string | null>(null)
  const syncedConfigsRef = useRef<Set<string>>(new Set())

  // 加载配置列表
  const loadConfigs = async () => {
    try {
      const response = await configsApi.getAll()
      setConfigs(response.data)
      if (response.data.length > 0 && !activeKey) {
        setActiveKey(response.data[0].key)
      }
    } catch (error) {
      message.error('加载配置失败')
    }
  }

  useEffect(() => {
    loadConfigs()
  }, [])

  // 加载指定 Prompt 的版本列表（包含同步外部文件）
  const loadVersions = useCallback(async (configKey: string) => {
    if (!configKey) return
    setLoading(true)
    try {
      const response = await promptsApi.getVersions(configKey)
      const versionsData = response.data.versions
      setActiveVersionId(response.data.active_version_id)

      // 加载每个版本的完整内容
      const versionsWithContent = await Promise.all(
        versionsData.map(async (v: PromptVersionSimple) => {
          const contentRes = await promptsApi.getVersionContent(configKey, v.id)
          return {
            ...v,
            content: contentRes.data.content
          }
        })
      )

      // 默认选中生效版本，如果没有则选第一个
      const activeVersion = versionsWithContent.find((v: VersionData) => v.is_active)
      const defaultVersion = activeVersion || (versionsWithContent.length > 0 ? versionsWithContent[0] : null)
      
      if (defaultVersion) {
        // 同步外部文件内容（只同步一次）
        const config = configs.find(c => c.key === configKey)
        let finalContent = defaultVersion.content
        
        if (config && !syncedConfigsRef.current.has(configKey)) {
          syncedConfigsRef.current.add(configKey)
          try {
            const pathResponse = await configsApi.testPath(config.external_path)
            if (pathResponse.data.readable) {
              const externalContent = pathResponse.data.content || ''
              if (externalContent !== defaultVersion.content) {
                // 更新版本内容
                await promptsApi.updateVersionContent(configKey, defaultVersion.id, externalContent)
                finalContent = externalContent
                // 更新数组中的内容
                const updatedVersions = versionsWithContent.map(v => 
                  v.id === defaultVersion.id 
                    ? { ...v, content: externalContent }
                    : v
                )
                setVersions(updatedVersions)
                message.info('已同步外部文件最新内容')
              } else {
                setVersions(versionsWithContent)
              }
            } else {
              setVersions(versionsWithContent)
            }
          } catch (error) {
            console.error('同步外部内容失败:', error)
            setVersions(versionsWithContent)
          }
        } else {
          setVersions(versionsWithContent)
        }
        
        setSelectedVersionId(defaultVersion.id)
        setEditorContent(finalContent)
        setOriginalContent(finalContent)
      } else {
        // 没有版本时，创建空内容
        setVersions(versionsWithContent)
        setSelectedVersionId(null)
        setEditorContent('')
        setOriginalContent('')
      }
    } catch (error) {
      message.error('加载版本失败')
    } finally {
      setLoading(false)
    }
  }, [configs])

  useEffect(() => {
    if (activeKey) {
      // 清除同步标记，确保切换 Tab 时会同步
      syncedConfigsRef.current.delete(activeKey)
      loadVersions(activeKey)
    }
  }, [activeKey, loadVersions])

  // 切换版本
  const handleVersionClick = (version: VersionData) => {
    // 检查是否有未保存的改动
    if (editorContent !== originalContent) {
      Modal.confirm({
        title: '有未保存的改动',
        icon: <ExclamationCircleOutlined />,
        content: '切换版本将丢失当前改动，是否继续？',
        onOk: () => {
          setSelectedVersionId(version.id)
          setEditorContent(version.content)
          setOriginalContent(version.content)
        }
      })
    } else {
      setSelectedVersionId(version.id)
      setEditorContent(version.content)
      setOriginalContent(version.content)
    }
  }

  // 新建版本
  const handleNewVersion = () => {
    if (editorContent !== originalContent) {
      Modal.confirm({
        title: '有未保存的改动',
        icon: <ExclamationCircleOutlined />,
        content: '新建版本将丢失当前改动，是否继续？',
        onOk: () => {
          setSelectedVersionId(null)
          setEditorContent('')
          setOriginalContent('')
        }
      })
    } else {
      setSelectedVersionId(null)
      setEditorContent('')
      setOriginalContent('')
    }
  }

  // 保存新版本
  const handleSave = async (values: { author: string; description?: string }) => {
    if (!activeKey) return
    if (!editorContent.trim()) {
      message.warning('Prompt 内容不能为空')
      return
    }

    try {
      const response = await promptsApi.createVersion(activeKey, {
        author: values.author,
        content: editorContent,
        description: values.description
      })

      const newVersion = response.data

      // 立即激活新版本
      await promptsApi.activateVersion(activeKey, newVersion.id)

      message.success('新版本已创建并生效')
      setSaveModalVisible(false)
      saveForm.resetFields()

      // 重新加载版本列表
      await loadVersions(activeKey)

      // 选中新创建的版本，并确保编辑器显示正确的内容
      setSelectedVersionId(newVersion.id)
      setEditorContent(editorContent)
      setOriginalContent(editorContent)
    } catch (error: any) {
      message.error(error.response?.data?.detail || '保存失败')
    }
  }

  // 激活版本
  const handleActivate = async (versionId: string, e: React.MouseEvent) => {
    e.stopPropagation()
    if (!activeKey) return

    try {
      const response = await promptsApi.activateVersion(activeKey, versionId)
      message.success(response.data.message)

      // 更新本地状态
      setVersions(prev => prev.map(v => ({
        ...v,
        is_active: v.id === versionId
      })))
      setActiveVersionId(versionId)
      
      // 选中当前生效的版本
      const activatedVersion = versions.find(v => v.id === versionId)
      if (activatedVersion) {
        setSelectedVersionId(versionId)
        setEditorContent(activatedVersion.content)
        setOriginalContent(activatedVersion.content)
      }
    } catch (error: any) {
      message.error(error.response?.data?.detail || '激活失败')
    }
  }

  // 删除版本
  const handleDelete = async (versionId: string, e: React.MouseEvent) => {
    e.stopPropagation()

    try {
      await promptsApi.deleteVersion(versionId)
      message.success('版本已删除')

      // 重新加载
      await loadVersions(activeKey)
    } catch (error: any) {
      message.error(error.response?.data?.detail || '删除失败')
    }
  }

  // 检查是否有改动
  const hasChanges = editorContent !== originalContent

  const currentConfig = configs.find(c => c.key === activeKey)

  return (
    <>
      <Title level={4} style={{ margin: 0, marginBottom: 24, color: GOOGLE_COLORS.gray, fontWeight: 500 }}>Prompt 管理</Title>

      {configs.length === 0 ? (
        <Card style={{ borderRadius: '16px', border: 'none', boxShadow: '0 1px 2px rgba(60,64,67,0.1)' }}>
          <div style={{ textAlign: 'center', padding: 48 }}>
            <FileTextOutlined style={{ fontSize: 48, color: GOOGLE_COLORS.border }} />
            <Title level={5} style={{ marginTop: 16, color: GOOGLE_COLORS.gray }}>暂无 Prompt 配置</Title>
            <Text type="secondary" style={{ color: GOOGLE_COLORS.gray }}>请先前往"Prompt 配置"页面添加 Prompt 文件配置</Text>
          </div>
        </Card>
      ) : (
        <Tabs
          activeKey={activeKey}
          onChange={setActiveKey}
          type="card"
        >
          {configs.map(config => (
            <TabPane tab={config.name} key={config.key}>
              <Row gutter={24}>
                {/* 左侧编辑器 */}
                <Col span={18}>
                  <Card
                    title={
                      <Space>
                        <span style={{ color: GOOGLE_COLORS.gray, fontWeight: 500 }}>编辑 Prompt</span>
                        {selectedVersionId && (
                          <>
                            <Tag style={{ 
                              background: GOOGLE_COLORS.blue + '20', 
                              color: GOOGLE_COLORS.blue,
                              border: 'none',
                              borderRadius: '4px'
                            }}>
                              版本 v{versions.findIndex(v => v.id === selectedVersionId) >= 0 ? versions.length - versions.findIndex(v => v.id === selectedVersionId) : '-'}
                            </Tag>
                            {versions.find(v => v.id === selectedVersionId)?.is_active && (
                              <Tag style={{ 
                                background: GOOGLE_COLORS.green + '20', 
                                color: GOOGLE_COLORS.green,
                                border: 'none',
                                borderRadius: '4px'
                              }}>
                                <CheckCircleOutlined /> 生效
                              </Tag>
                            )}
                          </>
                        )}
                        {!selectedVersionId && (
                          <Tag style={{ 
                            background: GOOGLE_COLORS.yellow + '20', 
                            color: GOOGLE_COLORS.yellow,
                            border: 'none',
                            borderRadius: '4px'
                          }}>
                            新建版本
                          </Tag>
                        )}
                      </Space>
                    }
                    extra={
                      <Button
                        type="primary"
                        icon={<SaveOutlined />}
                        onClick={() => setSaveModalVisible(true)}
                        disabled={!hasChanges}
                        style={{ 
                          borderRadius: '8px', 
                          background: hasChanges ? GOOGLE_COLORS.blue : '#dadce0',
                          border: 'none',
                          boxShadow: 'none',
                          color: hasChanges ? '#fff' : '#9aa0a6'
                        }}
                      >
                        保存
                      </Button>
                    }
                    style={{
                      borderRadius: '16px',
                      border: 'none',
                      height: 'calc(100vh - 200px)',
                      boxShadow: '0 1px 2px rgba(60,64,67,0.1), 0 1px 3px rgba(60,64,67,0.08)'
                    }}
                    bodyStyle={{ padding: '16px', height: 'calc(100vh - 250px)' }}
                  >
                    <TextArea
                      value={editorContent}
                      onChange={e => setEditorContent(e.target.value)}
                      style={{
                        fontFamily: 'monospace',
                        fontSize: 14,
                        height: 'calc(100vh - 284px)',
                        overflow: 'auto',
                        borderRadius: '8px',
                        border: `1px solid ${GOOGLE_COLORS.border}`,
                        resize: 'none'
                      }}
                      placeholder="在此输入 Prompt 内容..."
                      maxLength={undefined}
                    />
                  </Card>
                </Col>

                {/* 右侧版本列表 */}
                <Col span={6}>
                  <Card
                    title={<span style={{ color: GOOGLE_COLORS.gray, fontWeight: 500 }}>版本历史</span>}
                    size="small"
                    style={{
                      height: 'calc(100vh - 200px)',
                      borderRadius: '16px',
                      border: 'none',
                      boxShadow: '0 1px 2px rgba(60,64,67,0.1), 0 1px 3px rgba(60,64,67,0.08)',
                      overflow: 'hidden'
                    }}
                    headStyle={{ padding: '16px 24px' }}
                    bodyStyle={{ padding: '12px', height: 'calc(100vh - 250px)', overflowY: 'auto', overflowX: 'hidden' }}
                  >
                    <div style={{ width: '100%', paddingBottom: '24px' }}>
                      <Space direction="vertical" style={{ width: '100%' }} size="small">
                        {/* 新建版本按钮 */}
                        <Card
                          size="small"
                          hoverable
                          onClick={handleNewVersion}
                          style={{
                            border: `2px dashed ${GOOGLE_COLORS.border}`,
                            textAlign: 'center',
                            cursor: 'pointer',
                            borderRadius: '12px',
                            background: GOOGLE_COLORS.lightGray,
                            minHeight: '86px',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center'
                          }}
                          bodyStyle={{ padding: '12px', width: '100%' }}
                      >
                        <PlusOutlined style={{ color: GOOGLE_COLORS.blue }} />
                        <span style={{ color: GOOGLE_COLORS.blue, marginLeft: 8 }}>新建 Prompt</span>
                      </Card>

                      {/* 版本列表 - 按时间倒序，动态计算版本号 */}
                      {versions.map((version, index) => (
                        <Card
                          key={version.id}
                          size="small"
                          hoverable
                          onClick={() => handleVersionClick(version)}
                          style={{
                            border: selectedVersionId === version.id ? `2px solid ${GOOGLE_COLORS.blue}` : `1px solid ${GOOGLE_COLORS.border}`,
                            background: selectedVersionId === version.id ? '#e8f0fe' : GOOGLE_COLORS.white,
                            borderRadius: '12px',
                            marginBottom: index === versions.length - 1 ? '12px' : undefined
                          }}
                          bodyStyle={{ padding: '12px' }}
                        >
                          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                            <div>
                              <Text strong style={{ color: GOOGLE_COLORS.gray }}>
                                版本 v{versions.length - index}
                                {version.description && (
                                  <Tooltip title={version.description} mouseEnterDelay={0}>
                                    <InfoCircleOutlined 
                                      style={{ marginLeft: 8, color: GOOGLE_COLORS.blue, fontSize: 12, cursor: 'pointer' }}
                                    />
                                  </Tooltip>
                                )}
                              </Text>
                              <br />
                              <Text type="secondary" style={{ fontSize: 12, color: GOOGLE_COLORS.gray }}>
                                {dayjs(version.created_at).format('MM-DD HH:mm')}
                              </Text>
                              <br />
                              <Text type="secondary" style={{ fontSize: 12, color: GOOGLE_COLORS.gray }}>
                                {version.author}
                              </Text>
                            </div>
                            <Space direction="vertical" size="small">
                              {version.is_active ? (
                                <Tag style={{ 
                                  background: GOOGLE_COLORS.green + '20', 
                                  color: GOOGLE_COLORS.green,
                                  border: 'none',
                                  borderRadius: '4px'
                                }}>
                                  <CheckCircleOutlined /> 生效
                                </Tag>
                              ) : (
                                <Button
                                  type="link"
                                  size="small"
                                  onClick={(e) => handleActivate(version.id, e)}
                                  style={{ color: GOOGLE_COLORS.blue, padding: 0 }}
                                >
                                  设为生效
                                </Button>
                              )}
                              {!version.is_active && (
                                <Popconfirm
                                  title="确定删除此版本吗？"
                                  onConfirm={(e) => handleDelete(version.id, e as any)}
                                >
                                  <Button
                                    type="text"
                                    size="small"
                                    icon={<DeleteOutlined style={{ color: GOOGLE_COLORS.red }} />}
                                    onClick={e => e.stopPropagation()}
                                    style={{ padding: 0 }}
                                  />
                                </Popconfirm>
                              )}
                            </Space>
                          </div>
                        </Card>
                      ))}
                      </Space>
                    </div>
                  </Card>
                </Col>
              </Row>
            </TabPane>
          ))}
        </Tabs>
      )}

      {/* 保存弹窗 */}
      <Modal
        title={<span style={{ color: GOOGLE_COLORS.gray, fontWeight: 500 }}>保存新版本</span>}
        open={saveModalVisible}
        onOk={saveForm.submit}
        onCancel={() => setSaveModalVisible(false)}
        style={{ borderRadius: '16px' }}
      >
        <Form
          form={saveForm}
          layout="vertical"
          onFinish={handleSave}
        >
          <Form.Item
            name="author"
            label="作者"
            rules={[{ required: true, message: '请输入作者' }]}
          >
            <Input 
              placeholder="你的名字" 
              style={{ borderRadius: '8px', border: `1px solid ${GOOGLE_COLORS.border}` }}
            />
          </Form.Item>
          <Form.Item
            name="description"
            label="版本描述"
          >
            <Input.TextArea
              rows={3}
              placeholder="描述此次修改的内容..."
              style={{ borderRadius: '8px', border: `1px solid ${GOOGLE_COLORS.border}` }}
            />
          </Form.Item>
        </Form>
      </Modal>
    </>
  )
}
