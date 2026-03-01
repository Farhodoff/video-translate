import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import api from '../api/client'

interface Project {
    id: number
    title: string
    status: string
    thumbnail: string | null
    video_url: string | null
    final_video_url: string | null
    quality: string
    created_at: string
    error_message: string | null
}

interface User {
    id: number
    email: string
    full_name: string | null
}

const STATUS_COLOR: Record<string, string> = {
    Ready: '#10b981',
    Processing: '#f59e0b',
    Transcribing: '#3b82f6',
    Translating: '#8b5cf6',
    Dubbing: '#ec4899',
    Error: '#ef4444',
}

export default function DashboardPage() {
    const navigate = useNavigate()
    const [projects, setProjects] = useState<Project[]>([])
    const [user, setUser] = useState<User | null>(null)
    const [loading, setLoading] = useState(true)
    const [creating, setCreating] = useState(false)
    const [youtubeUrl, setYoutubeUrl] = useState('')
    const [title, setTitle] = useState('')
    const [showForm, setShowForm] = useState(false)

    useEffect(() => {
        const stored = localStorage.getItem('user')
        if (stored) setUser(JSON.parse(stored))
        fetchProjects()
    }, [])

    async function fetchProjects() {
        try {
            const res = await api.get('/projects')
            setProjects(res.data.data || [])
        } catch {
            // 401 → apiClient interceptor login ga yo'naltiradi
        } finally {
            setLoading(false)
        }
    }

    async function createProject(e: React.FormEvent) {
        e.preventDefault()
        setCreating(true)
        const form = new FormData()
        form.append('youtube_url', youtubeUrl)
        form.append('title', title || 'Yangi loyiha')
        try {
            await api.post('/projects', form, { headers: { 'Content-Type': 'multipart/form-data' } })
            setYoutubeUrl('')
            setTitle('')
            setShowForm(false)
            fetchProjects()
        } catch {
            alert('Loyiha yaratishda xatolik')
        } finally {
            setCreating(false)
        }
    }

    async function deleteProject(id: number) {
        if (!confirm('O\'chirilsinmi?')) return
        await api.delete(`/project/${id}`)
        fetchProjects()
    }

    function logout() {
        localStorage.removeItem('token')
        localStorage.removeItem('user')
        navigate('/login')
    }

    return (
        <div className="min-h-screen" style={{ background: 'var(--bg-dark)', color: 'white' }}>
            {/* Navbar */}
            <header className="flex items-center justify-between px-8 py-4 border-b" style={{ borderColor: 'var(--border-color)', background: 'var(--bg-card)' }}>
                <span className="text-lg font-bold">
                    <span style={{ color: 'var(--primary)' }}>🎙️</span> AI Dubbing
                </span>
                <div className="flex items-center gap-4">
                    <span className="text-sm" style={{ color: 'var(--text-muted)' }}>
                        {user?.full_name || user?.email}
                    </span>
                    <button
                        onClick={() => setShowForm(!showForm)}
                        className="px-4 py-2 text-sm rounded-lg font-medium transition-all hover:opacity-90"
                        style={{ background: 'var(--primary)' }}
                    >
                        + Yangi loyiha
                    </button>
                    <button onClick={logout} className="text-sm px-3 py-2 rounded-lg border hover:bg-white/5 transition-colors"
                        style={{ borderColor: 'var(--border-color)', color: 'var(--text-muted)' }}>
                        Chiqish
                    </button>
                </div>
            </header>

            <main className="max-w-6xl mx-auto px-6 py-10">
                {/* Create Form */}
                {showForm && (
                    <div className="mb-8 p-6 rounded-2xl border" style={{ background: 'var(--bg-card)', borderColor: 'var(--border-color)' }}>
                        <h2 className="text-lg font-semibold mb-4">Yangi loyiha yaratish</h2>
                        <form onSubmit={createProject} className="flex flex-col gap-4 md:flex-row md:items-end">
                            <div className="flex-1">
                                <label className="block text-sm mb-1.5" style={{ color: 'var(--text-muted)' }}>YouTube URL</label>
                                <input
                                    value={youtubeUrl}
                                    onChange={e => setYoutubeUrl(e.target.value)}
                                    required
                                    placeholder="https://youtube.com/watch?v=..."
                                    className="w-full px-4 py-3 rounded-xl text-sm border outline-none focus:border-purple-500 transition-colors"
                                    style={{ background: '#0f172a', borderColor: 'var(--border-color)', color: 'white' }}
                                />
                            </div>
                            <div className="flex-1">
                                <label className="block text-sm mb-1.5" style={{ color: 'var(--text-muted)' }}>Nomi (ixtiyoriy)</label>
                                <input
                                    value={title}
                                    onChange={e => setTitle(e.target.value)}
                                    placeholder="Loyiha nomi"
                                    className="w-full px-4 py-3 rounded-xl text-sm border outline-none focus:border-purple-500 transition-colors"
                                    style={{ background: '#0f172a', borderColor: 'var(--border-color)', color: 'white' }}
                                />
                            </div>
                            <button
                                type="submit"
                                disabled={creating}
                                className="px-6 py-3 rounded-xl font-semibold text-white transition-all hover:opacity-90 disabled:opacity-50 whitespace-nowrap"
                                style={{ background: 'var(--primary)' }}
                            >
                                {creating ? 'Yaratilmoqda...' : 'Boshlash'}
                            </button>
                        </form>
                    </div>
                )}

                {/* Projects Grid */}
                <h1 className="text-2xl font-bold mb-6">Loyihalarim</h1>

                {loading ? (
                    <div className="text-center py-20" style={{ color: 'var(--text-muted)' }}>Yuklanmoqda...</div>
                ) : projects.length === 0 ? (
                    <div className="text-center py-20 rounded-2xl border" style={{ borderColor: 'var(--border-color)', color: 'var(--text-muted)' }}>
                        <p className="text-4xl mb-4">📽️</p>
                        <p className="text-lg">Hali loyihalar yo'q</p>
                        <p className="text-sm mt-2">Yuqoridagi "Yangi loyiha" tugmasini bosing</p>
                    </div>
                ) : (
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
                        {projects.map(p => (
                            <div key={p.id} className="rounded-2xl border overflow-hidden hover:border-purple-500/40 transition-all group"
                                style={{ background: 'var(--bg-card)', borderColor: 'var(--border-color)' }}>
                                {/* Thumbnail */}
                                <div className="h-44 flex items-center justify-center" style={{ background: '#0f172a' }}>
                                    {p.thumbnail ? (
                                        <img src={p.thumbnail} alt={p.title} className="w-full h-full object-cover" />
                                    ) : (
                                        <span className="text-5xl">🎬</span>
                                    )}
                                </div>
                                <div className="p-4">
                                    <div className="flex items-start justify-between gap-2 mb-3">
                                        <h3 className="font-semibold text-sm leading-snug line-clamp-2">{p.title}</h3>
                                        <span className="text-xs px-2 py-0.5 rounded-full whitespace-nowrap shrink-0 font-medium"
                                            style={{ background: `${STATUS_COLOR[p.status] || '#64748b'}20`, color: STATUS_COLOR[p.status] || '#64748b' }}>
                                            {p.status}
                                        </span>
                                    </div>
                                    {p.error_message && (
                                        <p className="text-xs mb-3 line-clamp-2" style={{ color: '#ef4444' }}>{p.error_message}</p>
                                    )}
                                    <div className="flex gap-2 mt-3">
                                        {p.final_video_url && (
                                            <a href={p.final_video_url} target="_blank" rel="noopener noreferrer"
                                                className="flex-1 text-center text-xs py-2 rounded-lg font-medium transition-all hover:opacity-90"
                                                style={{ background: 'var(--primary)', color: 'white' }}>
                                                ▶ Ko'rish
                                            </a>
                                        )}
                                        <button onClick={() => deleteProject(p.id)}
                                            className="px-3 py-2 rounded-lg text-xs border transition-all hover:bg-red-500/10 hover:border-red-500/40"
                                            style={{ borderColor: 'var(--border-color)', color: 'var(--text-muted)' }}>
                                            🗑
                                        </button>
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                )}
            </main>
        </div>
    )
}
