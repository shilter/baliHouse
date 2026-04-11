import { useState } from 'react'
import { getMemberFromStorage, clearAuth } from './api'
import LoginPage from './LoginPage'
import RegisterPage from './RegisterPage'
import LeadsPage from './LeadsPage'

export default function App() {
  const [member, setMember] = useState(() => getMemberFromStorage())
  const [page, setPage] = useState('login')

  function handleLogin(memberData) {
    setMember(memberData)
  }

  function handleLogout() {
    clearAuth()
    setMember(null)
    setPage('login')
  }

  if (member) {
    return <LeadsPage member={member} onLogout={handleLogout} />
  }

  if (page === 'register') {
    return (
      <RegisterPage
        onLogin={handleLogin}
        onGoLogin={() => setPage('login')}
      />
    )
  }

  return (
    <LoginPage
      onLogin={handleLogin}
      onGoRegister={() => setPage('register')}
    />
  )
}