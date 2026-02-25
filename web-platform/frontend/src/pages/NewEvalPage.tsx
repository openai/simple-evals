import { useState, useEffect } from 'react'
import { 
  Card, 
  Form, 
  Select, 
  InputNumber, 
  Button, 
  message,
  Space,
  Typography,
  Steps,
  Result,
  Descriptions,
  Tag
} from 'antd'
import { ArrowLeftOutlined, PlayCircleOutlined, CheckCircleOutlined } from '@ant-design/icons'
import { evaluationsApi } from '../api/evaluations'
import { versionsApi } from '../api/versions'
import type { PromptVersion } from '../types'
import { Link, useNavigate } from 'react-router-dom'
import dayjs from 'dayjs'

const { Title, Text } = Typography
const { Step } = Steps

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

const BENCHMARK_OPTIONS = [
  { value: 'healthbench', label: 'HealthBench' },
  { value: 'healthbench_hard', label: 'HealthBench Hard' },
  { value: 'healthbench_consensus', label: 'HealthBench Consensus' },
  { value: 'csedb', label: 'CSEDB' },
  { value: 'usmle', label: 'USMLE' },
]

export default function NewEvalPage() {
  const [form] = Form.useForm()
  const navigate = useNavigate()
  const [versions, setVersions] = useState<PromptVersion[]>([])
  const [loading, setLoading] = useState(false)
  const [currentStep, setCurrentStep] = useState(0)
  const [createdEval, setCreatedEval] = useState<any>(null)

  // 加载版本列表
  useEffect(() => {
    const loadVersions = async () => {
      try {
        const response = await versionsApi.getAll()
        setVersions(response.data)
      } catch (error) {
        message.error('加载版本列表失败')
      }
    }
    loadVersions()
  }, [])

  // 提交表单
  const handleSubmit = async (values: any) => {
    setLoading(true)
    try {
      const response = await evaluationsApi.create({
        version_id: values.version_id,
        benchmark: values.benchmark,
        num_examples: values.num_examples,
        n_threads: values.n_threads,
        description: values.description,
      })
      setCreatedEval(response.data)
      setCurrentStep(1)
      message.success('Eval 任务已创建')
    } catch (error: any) {
      message.error(error.response?.data?.detail || '创建失败')
    } finally {
      setLoading(false)
    }
  }

  // 启动任务
  const handleStart = async () => {
    if (!createdEval) return
    
    try {
      await evaluationsApi.start(createdEval.id)
      setCurrentStep(2)
      message.success('任务已启动')
    } catch (error: any) {
      message.error(error.response?.data?.detail || '启动失败')
    }
  }

  // 跳转到任务列表
  const handleGoToList = () => {
    navigate('/evaluations')
  }

  const steps = [
    {
      title: '配置任务',
      content: (
        <Form
          form={form}
          layout="vertical"
          onFinish={handleSubmit}
          initialValues={{
            n_threads: 1,
            benchmark: 'healthbench',
          }}
        >
          <Form.Item
            name="version_id"
            label={<span style={{ color: GOOGLE_COLORS.gray, fontWeight: 500 }}>选择 Prompt 版本</span>}
            rules={[{ required: true, message: '请选择 Prompt 版本' }]}
          >
            <Select
              placeholder="选择要测试的 Prompt 版本"
              style={{ borderRadius: '8px' }}
              options={versions.map(v => ({
                value: v.id,
                label: (
                  <Space>
                    <Text strong style={{ color: GOOGLE_COLORS.blue }}>v{v.version_number}</Text>
                    {v.is_active && <Tag style={{ background: GOOGLE_COLORS.green + '20', color: GOOGLE_COLORS.green, border: 'none', borderRadius: '4px' }}>当前生效</Tag>}
                    <Text type="secondary" style={{ color: GOOGLE_COLORS.gray }}>{v.author}</Text>
                    <Text type="secondary" style={{ color: GOOGLE_COLORS.gray }}>{dayjs(v.created_at).format('MM-DD HH:mm')}</Text>
                  </Space>
                ),
              }))}
            />
          </Form.Item>

          <Form.Item
            name="benchmark"
            label={<span style={{ color: GOOGLE_COLORS.gray, fontWeight: 500 }}>Benchmark</span>}
            rules={[{ required: true, message: '请选择 Benchmark' }]}
          >
            <Select
              placeholder="选择评估数据集"
              style={{ borderRadius: '8px' }}
              options={BENCHMARK_OPTIONS}
            />
          </Form.Item>

          <Form.Item
            name="num_examples"
            label={<span style={{ color: GOOGLE_COLORS.gray, fontWeight: 500 }}>样本数量</span>}
            extra={<span style={{ color: GOOGLE_COLORS.gray }}>不填写表示运行全部样本</span>}
          >
            <InputNumber
              min={1}
              max={10000}
              placeholder="全部"
              style={{ width: '100%', borderRadius: '8px' }}
            />
          </Form.Item>

          <Form.Item
            name="n_threads"
            label={<span style={{ color: GOOGLE_COLORS.gray, fontWeight: 500 }}>并行线程数</span>}
            rules={[{ required: true, message: '请输入并行线程数' }]}
          >
            <InputNumber
              min={1}
              max={16}
              style={{ width: '100%', borderRadius: '8px' }}
            />
          </Form.Item>

          <Form.Item
            name="description"
            label={<span style={{ color: GOOGLE_COLORS.gray, fontWeight: 500 }}>备注</span>}
          >
            <Input.TextArea
              rows={3}
              placeholder="描述此次评估的目的..."
              style={{ borderRadius: '8px', border: `1px solid ${GOOGLE_COLORS.border}` }}
            />
          </Form.Item>

          <Form.Item>
            <Space>
              <Button 
                type="primary" 
                htmlType="submit" 
                loading={loading} 
                icon={<PlayCircleOutlined />}
                style={{ 
                  borderRadius: '8px', 
                  background: GOOGLE_COLORS.blue,
                  border: 'none',
                  boxShadow: 'none'
                }}
              >
                创建任务
              </Button>
              <Link to="/evaluations">
                <Button 
                  icon={<ArrowLeftOutlined />}
                  style={{ borderRadius: '8px' }}
                >
                  返回列表
                </Button>
              </Link>
            </Space>
          </Form.Item>
        </Form>
      ),
    },
    {
      title: '确认启动',
      content: createdEval && (
        <div>
          <Result
            status="success"
            title={<span style={{ color: GOOGLE_COLORS.gray }}>Eval 任务已创建</span>}
            subTitle={<span style={{ color: GOOGLE_COLORS.gray }}>任务 ID: {createdEval.id}</span>}
          />
          <Card 
            style={{ 
              marginBottom: 24, 
              borderRadius: '12px', 
              border: 'none',
              boxShadow: '0 1px 2px rgba(60,64,67,0.1)'
            }}
          >
            <Descriptions 
              bordered 
              column={2}
              labelStyle={{ background: GOOGLE_COLORS.lightGray, color: GOOGLE_COLORS.gray }}
              contentStyle={{ color: GOOGLE_COLORS.gray }}
            >
              <Descriptions.Item label="Prompt 版本">
                {versions.find(v => v.id === createdEval.version_id)?.version_number || createdEval.version_id}
              </Descriptions.Item>
              <Descriptions.Item label="Benchmark">
                {createdEval.benchmark}
              </Descriptions.Item>
              <Descriptions.Item label="样本数">
                {createdEval.num_examples || '全部'}
              </Descriptions.Item>
              <Descriptions.Item label="并行线程">
                {createdEval.n_threads}
              </Descriptions.Item>
              <Descriptions.Item label="备注" span={2}>
                {createdEval.description || '无'}
              </Descriptions.Item>
            </Descriptions>
          </Card>
          <Space>
            <Button 
              type="primary" 
              onClick={handleStart} 
              icon={<PlayCircleOutlined />}
              style={{ 
                borderRadius: '8px', 
                background: GOOGLE_COLORS.green,
                border: 'none',
                boxShadow: 'none'
              }}
            >
              立即启动
            </Button>
            <Button 
              onClick={handleGoToList}
              style={{ borderRadius: '8px' }}
            >
              稍后手动启动
            </Button>
          </Space>
        </div>
      ),
    },
    {
      title: '运行中',
      content: (
        <Result
          icon={<CheckCircleOutlined style={{ color: GOOGLE_COLORS.green }} />}
          title={<span style={{ color: GOOGLE_COLORS.gray }}>任务已启动</span>}
          subTitle={<span style={{ color: GOOGLE_COLORS.gray }}>任务正在运行中，可以前往任务列表查看实时进度</span>}
          extra={[
            <Button 
              type="primary" 
              key="list" 
              onClick={handleGoToList}
              style={{ 
                borderRadius: '8px', 
                background: GOOGLE_COLORS.blue,
                border: 'none',
                boxShadow: 'none'
              }}
            >
              前往任务列表
            </Button>,
          ]}
        />
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
      <div style={{ display: 'flex', alignItems: 'center', marginBottom: 24 }}>
        <Link to="/evaluations" style={{ marginRight: 16 }}>
          <ArrowLeftOutlined style={{ color: GOOGLE_COLORS.gray, fontSize: '18px' }} />
        </Link>
        <Title level={4} style={{ margin: 0, color: GOOGLE_COLORS.gray, fontWeight: 500 }}>新建 Eval 任务</Title>
      </div>

      <Steps 
        current={currentStep} 
        style={{ marginBottom: 32 }}
        items={steps.map(item => ({ title: item.title }))}
      />

      <div style={{ maxWidth: 600, margin: '0 auto' }}>
        {steps[currentStep].content}
      </div>
    </Card>
  )
}
