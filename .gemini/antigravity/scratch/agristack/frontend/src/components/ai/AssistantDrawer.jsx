import { useState } from 'react'
import { useTranslation } from 'react-i18next'
import api from '../../services/api'

export default function AssistantDrawer() {
  const { t, i18n } = useTranslation()
  const [open, setOpen] = useState(false)
  const [topic, setTopic] = useState('crop')
  const [query, setQuery] = useState('')
  const [answer, setAnswer] = useState(null)
  const [error, setError] = useState('')

  const ask = async (e) => {
    e.preventDefault()
    setError('')
    try {
      const { data } = await api.post('/predictions/ai-assistant', {
        topic,
        language: i18n.language.slice(0, 2),
        query_text: query,
      })
      setAnswer(data)
    } catch (err) {
      setError(err.response?.data?.error?.message || 'Assistant unavailable')
    }
  }

  return (
    <>
      <button
        onClick={() => setOpen(true)}
        className="fixed bottom-5 right-5 z-40 rounded-full bg-agri-700 text-white px-4 py-3 shadow-lg"
      >
        {t('assistant')}
      </button>
      {open && (
        <div className="fixed inset-0 z-50 bg-black/30" onClick={() => setOpen(false)}>
          <aside
            className="absolute right-0 top-0 h-full w-full max-w-md bg-white p-5 overflow-y-auto"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex justify-between items-center mb-4">
              <h2 className="font-semibold text-agri-900">{t('assistant')}</h2>
              <button onClick={() => setOpen(false)}>✕</button>
            </div>
            <form onSubmit={ask} className="space-y-3">
              <select className="w-full rounded-md" value={topic} onChange={(e) => setTopic(e.target.value)}>
                <option value="crop">Crop advice</option>
                <option value="schemes">Govt schemes</option>
              </select>
              <textarea
                className="w-full rounded-md"
                rows={3}
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Ask in EN / HI / MR"
              />
              <button className="w-full bg-agri-700 text-white rounded-md py-2">{t('submit')}</button>
            </form>
            {error && <p className="text-red-600 text-sm mt-3">{error}</p>}
            {answer && (
              <div className="mt-4 text-sm space-y-2 bg-emerald-50 p-3 rounded-lg">
                <p className="font-semibold">{answer.title || answer.topic}</p>
                <pre className="whitespace-pre-wrap text-xs">{JSON.stringify(answer, null, 2)}</pre>
              </div>
            )}
          </aside>
        </div>
      )}
    </>
  )
}
