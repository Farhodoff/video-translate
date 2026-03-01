import { useState, FormEvent } from 'react'
import { Link, useNavigate } from 'react-router-dom'

export default function LoginPage() {
    const navigate = useNavigate()
    const [error, setError] = useState('')
    const [loading, setLoading] = useState(false)

    async function handleSubmit(e: FormEvent<HTMLFormElement>) {
        e.preventDefault()
        setError('')
        setLoading(true)
        const form = new FormData(e.currentTarget)

        try {
            const res = await fetch('/api/login', { method: 'POST', body: form })
            const data = await res.json()
            if (!res.ok || data.status === 'error') {
                setError(data.message || 'Email yoki parol noto\'g\'ri')
            } else {
                localStorage.setItem('token', data.access_token)
                localStorage.setItem('user', JSON.stringify(data.user))
                navigate('/dashboard')
            }
        } catch {
            setError('Server bilan bog\'lanishda xatolik')
        } finally {
            setLoading(false)
        }
    }

    return (
        <div className="min-h-screen flex items-center justify-center px-4" style={{ background: 'var(--bg-dark)' }}>
            <div className="w-full max-w-md">
                <div className="text-center mb-8">
                    <Link to="/" className="text-2xl font-bold">
                        <span style={{ color: 'var(--primary)' }}>🎙️</span> AI Dubbing
                    </Link>
                    <p className="mt-2 text-sm" style={{ color: 'var(--text-muted)' }}>Hisobingizga kiring</p>
                </div>

                <div className="p-8 rounded-2xl border" style={{ background: 'var(--bg-card)', borderColor: 'var(--border-color)' }}>
                    <form onSubmit={handleSubmit} className="flex flex-col gap-4">
                        <div>
                            <label className="block text-sm font-medium mb-1.5" style={{ color: 'var(--text-muted)' }}>Email</label>
                            <input
                                name="username"
                                type="email"
                                required
                                placeholder="email@example.com"
                                className="w-full px-4 py-3 rounded-xl text-sm outline-none border focus:border-purple-500 transition-colors"
                                style={{ background: '#0f172a', borderColor: 'var(--border-color)', color: 'white' }}
                            />
                        </div>
                        <div>
                            <label className="block text-sm font-medium mb-1.5" style={{ color: 'var(--text-muted)' }}>Parol</label>
                            <input
                                name="password"
                                type="password"
                                required
                                placeholder="••••••••"
                                className="w-full px-4 py-3 rounded-xl text-sm outline-none border focus:border-purple-500 transition-colors"
                                style={{ background: '#0f172a', borderColor: 'var(--border-color)', color: 'white' }}
                            />
                        </div>

                        {error && (
                            <div className="px-4 py-3 rounded-xl text-sm" style={{ background: 'rgba(239,68,68,0.1)', color: '#ef4444', border: '1px solid rgba(239,68,68,0.3)' }}>
                                {error}
                            </div>
                        )}

                        <button
                            type="submit"
                            disabled={loading}
                            className="mt-2 py-3 rounded-xl font-semibold text-white transition-all hover:opacity-90 disabled:opacity-50"
                            style={{ background: 'var(--primary)' }}
                        >
                            {loading ? 'Kirilmoqda...' : 'Kirish'}
                        </button>
                    </form>
                </div>

                <p className="text-center mt-6 text-sm" style={{ color: 'var(--text-muted)' }}>
                    Hisob yo'qmi?{' '}
                    <Link to="/register" style={{ color: 'var(--primary)' }} className="font-medium hover:underline">
                        Ro'yxatdan o'ting
                    </Link>
                </p>
            </div>
        </div>
    )
}
