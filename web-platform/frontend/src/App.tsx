import { Layout, Menu, Typography, Dropdown, Space, Avatar } from 'antd'
import {
  SettingOutlined,
  FileTextOutlined,
  ExperimentOutlined,
  BarChartOutlined,
  EditOutlined,
  UserOutlined,
  LogoutOutlined
} from '@ant-design/icons'
import { BrowserRouter as Router, Routes, Route, Link, useLocation, Navigate, useNavigate } from 'react-router-dom'
import ConfigsPage from './pages/ConfigsPage'
import PromptsPage from './pages/PromptsPage'
import EvaluationsPage from './pages/EvaluationsPage'
import NewEvalPage from './pages/NewEvalPage'
import LoginPage from './pages/LoginPage'

const { Header, Content, Sider } = Layout
const { Title } = Typography

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

// 检查是否已登录
const isAuthenticated = () => {
  return localStorage.getItem('token') !== null
}

// 需要登录才能访问的页面布局
function AppLayout() {
  const location = useLocation()
  const navigate = useNavigate()

  // 如果未登录，跳转到登录页
  if (!isAuthenticated()) {
    return <Navigate to="/login" replace />
  }

  const handleLogout = () => {
    localStorage.removeItem('token')
    navigate('/login')
  }

  const userMenuItems = [
    {
      key: 'user-info',
      label: <div style={{ color: GOOGLE_COLORS.gray, textAlign: 'center' }}>oushu</div>,
      disabled: true
    },
    {
      type: 'divider' as const
    },
    {
      key: 'logout',
      icon: <LogoutOutlined />,
      label: '退出登录',
      onClick: handleLogout
    }
  ]

  const menuItems = [
    {
      key: '/configs',
      icon: <SettingOutlined style={{ color: GOOGLE_COLORS.blue }} />,
      label: <Link to="/configs" style={{ color: GOOGLE_COLORS.gray }}>Prompt 配置</Link>,
    },
    {
      key: '/prompts',
      icon: <EditOutlined style={{ color: GOOGLE_COLORS.green }} />,
      label: <Link to="/prompts" style={{ color: GOOGLE_COLORS.gray }}>Prompt 管理</Link>,
    },
    {
      key: '/evaluations',
      icon: <ExperimentOutlined style={{ color: GOOGLE_COLORS.yellow }} />,
      label: <Link to="/evaluations" style={{ color: GOOGLE_COLORS.gray }}>Eval 任务</Link>,
    },
    {
      key: '/new-eval',
      icon: <BarChartOutlined style={{ color: GOOGLE_COLORS.red }} />,
      label: <Link to="/new-eval" style={{ color: GOOGLE_COLORS.gray }}>新建 Eval</Link>,
    },
  ]

  return (
    <Layout style={{ minHeight: '100vh', background: GOOGLE_COLORS.lightGray }}>
      {/* Google 风格 Header */}
      <Header
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          background: GOOGLE_COLORS.white,
          borderBottom: `1px solid ${GOOGLE_COLORS.border}`,
          boxShadow: '0 1px 2px rgba(60,64,67,0.1)',
          padding: '0 16px',
          height: '64px'
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          {/* Logo */}
          <div
            style={{
              width: '40px',
              height: '40px',
              background: `linear-gradient(135deg, ${GOOGLE_COLORS.blue} 0%, ${GOOGLE_COLORS.green} 100%)`,
              borderRadius: '8px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center'
            }}
          >
            <span style={{ color: '#fff', fontSize: '18px', fontWeight: 'bold' }}>W</span>
          </div>
          <Title level={4} style={{ color: GOOGLE_COLORS.gray, margin: 0, fontWeight: 500 }}>
            Wandou Benchmark
          </Title>
        </div>
        <Dropdown menu={{ items: userMenuItems }} placement="bottomRight">
          <div 
            style={{ 
              cursor: 'pointer', 
              color: GOOGLE_COLORS.gray,
              padding: '8px',
              borderRadius: '8px',
              transition: 'background 0.2s',
              display: 'flex',
              alignItems: 'center'
            }} 
            className="user-dropdown"
          >
            <Avatar 
              icon={<UserOutlined />} 
              style={{ 
                backgroundColor: GOOGLE_COLORS.blue,
                width: '32px',
                height: '32px'
              }} 
            />
          </div>
        </Dropdown>
      </Header>
      <Layout style={{ background: GOOGLE_COLORS.lightGray }}>
        {/* Google 风格侧边栏 */}
        <Sider 
          width={240} 
          style={{ 
            background: GOOGLE_COLORS.white,
            borderRight: `1px solid ${GOOGLE_COLORS.border}`,
            padding: '16px 0'
          }}
        >
          <Menu
            mode="inline"
            selectedKeys={[location.pathname]}
            style={{ 
              height: '100%', 
              borderRight: 0,
              background: 'transparent'
            }}
            items={menuItems}
            theme="light"
          />
        </Sider>
        <Layout style={{ padding: '24px', background: GOOGLE_COLORS.lightGray }}>
          <Content
            style={{
              padding: 0,
              margin: 0,
              minHeight: 280,
              background: 'transparent'
            }}
          >
            <Routes>
              <Route path="/configs" element={<ConfigsPage />} />
              <Route path="/prompts" element={<PromptsPage />} />
              <Route path="/evaluations" element={<EvaluationsPage />} />
              <Route path="/new-eval" element={<NewEvalPage />} />
              <Route path="/" element={<Navigate to="/configs" replace />} />
            </Routes>
          </Content>
        </Layout>
      </Layout>
    </Layout>
  )
}

// 登录页面（独立布局，不带侧边栏）
function LoginRoute() {
  // 如果已登录，跳转到首页
  if (isAuthenticated()) {
    return <Navigate to="/" replace />
  }
  return <LoginPage />
}

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/login" element={<LoginRoute />} />
        <Route path="/*" element={<AppLayout />} />
      </Routes>
    </Router>
  )
}

export default App
