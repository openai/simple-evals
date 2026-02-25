import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Button, Input, message } from 'antd'
import { UserOutlined, LockOutlined } from '@ant-design/icons'

// 硬编码的登录凭证
const VALID_USERNAME = 'oushu'
const VALID_PASSWORD = 'oushu666'

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

export default function LoginPage() {
  const navigate = useNavigate()
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)

  const handleLogin = async () => {
    if (!username.trim() || !password.trim()) {
      message.warning('请输入用户名和密码')
      return
    }

    setLoading(true)
    try {
      // 模拟登录验证
      await new Promise(resolve => setTimeout(resolve, 500))
      
      // 验证用户名和密码
      if (username === VALID_USERNAME && password === VALID_PASSWORD) {
        localStorage.setItem('token', 'mock-token')
        message.success('登录成功')
        navigate('/')
      } else {
        message.error('用户名或密码错误')
      }
    } catch (error) {
      message.error('登录失败')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div
      style={{
        minHeight: '100vh',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        backgroundColor: GOOGLE_COLORS.white,
        padding: '20px'
      }}
    >
      {/* Logo 区域 */}
      <div style={{ marginBottom: '40px', display: 'flex', alignItems: 'center', gap: '16px' }}>
        {/* W Logo */}
        <div
          style={{
            width: '48px',
            height: '48px',
            background: `linear-gradient(135deg, ${GOOGLE_COLORS.blue} 0%, ${GOOGLE_COLORS.green} 100%)`,
            borderRadius: '12px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            boxShadow: '0 4px 12px rgba(26, 115, 232, 0.3)'
          }}
        >
          <span style={{ color: '#fff', fontSize: '24px', fontWeight: 'bold' }}>W</span>
        </div>
        {/* 系统名称 */}
        <span style={{ 
          color: GOOGLE_COLORS.gray, 
          fontSize: '24px', 
          fontWeight: 500,
          letterSpacing: '-0.5px'
        }}>
          Wandou Benchmark
        </span>
      </div>

      {/* 登录表单 */}
      <div style={{ width: '100%', maxWidth: '360px' }}>
        <div style={{ marginBottom: '16px' }}>
          <Input
            size="large"
            placeholder="用户名"
            prefix={<UserOutlined style={{ color: GOOGLE_COLORS.gray }} />}
            value={username}
            onChange={e => setUsername(e.target.value)}
            onPressEnter={handleLogin}
            style={{
              borderRadius: '8px',
              border: `1px solid ${GOOGLE_COLORS.border}`,
              height: '48px',
              fontSize: '16px',
              backgroundColor: GOOGLE_COLORS.white
            }}
          />
        </div>

        <div style={{ marginBottom: '32px' }}>
          <Input.Password
            size="large"
            placeholder="密码"
            prefix={<LockOutlined style={{ color: GOOGLE_COLORS.gray }} />}
            value={password}
            onChange={e => setPassword(e.target.value)}
            onPressEnter={handleLogin}
            style={{
              borderRadius: '8px',
              border: `1px solid ${GOOGLE_COLORS.border}`,
              height: '48px',
              fontSize: '16px',
              backgroundColor: GOOGLE_COLORS.white
            }}
          />
        </div>

        <Button
          type="primary"
          size="large"
          block
          loading={loading}
          onClick={handleLogin}
          style={{
            height: '48px',
            borderRadius: '8px',
            fontSize: '16px',
            fontWeight: 500,
            background: GOOGLE_COLORS.blue,
            border: 'none',
            boxShadow: 'none'
          }}
        >
          登录
        </Button>
      </div>
    </div>
  )
}
