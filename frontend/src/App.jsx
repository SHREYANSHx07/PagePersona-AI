import { useState } from 'react'
import InputForm from './components/InputForm'
import StepProgress from './components/StepProgress'
import ResultsView from './components/ResultsView'
import './App.css'

/** Dev: Vite proxies /api → Django. Production: same host must proxy /api, or set VITE_API_BASE when building. */
const API_BASE = (import.meta.env.VITE_API_BASE || '/api').replace(/\/$/, '')

export default function App() {
  const [phase, setPhase] = useState('input')       // 'input' | 'loading' | 'results' | 'error'
  const [currentStep, setCurrentStep] = useState(1)
  const [stepError, setStepError] = useState(null)
  const [results, setResults] = useState(null)
  const [globalError, setGlobalError] = useState(null)

  const handleSubmit = async (formData) => {
    setPhase('loading')
    setCurrentStep(1)
    setStepError(null)
    setGlobalError(null)

    try {
      // All 3 steps are called by the single /personalize/ endpoint
      // We simulate step progress while waiting

      // Animate through steps
      const stepTimings = [0, 3000, 6000] // simulate: scraping→analyzing→personalizing
      stepTimings.forEach((delay, i) => {
        setTimeout(() => {
          if (i < 3) setCurrentStep(i + 1)
        }, delay)
      })

      const response = await fetch(`${API_BASE}/personalize/`, {
        method: 'POST',
        body: formData,
      })

      const raw = await response.text()
      let data
      try {
        data = raw ? JSON.parse(raw) : {}
      } catch {
        const preview = raw.trim().slice(0, 140).replace(/\s+/g, ' ')
        const deployHint =
          'Usually the live site returned an HTML error page (404/502) instead of JSON because /api is not routed to Django. Fix: reverse-proxy /api to your backend, or rebuild the frontend with VITE_API_BASE set to your API root (e.g. https://your-api.onrender.com/api).'
        const msg = `Server response was not JSON (HTTP ${response.status}). ${deployHint} Body starts with: "${preview}${raw.length > 140 ? '…' : ''}"`
        setCurrentStep(3)
        setStepError(msg)
        setGlobalError(msg)
        setPhase('error')
        return
      }

      if (!response.ok) {
        const errorMsg = data.error || 'An error occurred during personalization.'
        const errorStep = data.step === 'scraping' ? 1 : data.step === 'ad_analysis' ? 2 : 3
        setCurrentStep(errorStep)
        setStepError(errorMsg)
        setGlobalError(errorMsg)
        setPhase('error')
        return
      }

      setCurrentStep(4)
      // Brief pause to show completion animation
      await new Promise(r => setTimeout(r, 800))
      setResults(data)
      setPhase('results')

    } catch (err) {
      const msg =
        err.name === 'TypeError' && err.message.includes('fetch')
          ? 'Network error: cannot reach the API. If local, run Django on port 8000; if deployed, check VITE_API_BASE and that /api is proxied to Django.'
          : err.message || 'Unexpected error occurred.'
      setGlobalError(msg)
      setStepError(msg)
      setPhase('error')
    }
  }

  const handleReset = () => {
    setPhase('input')
    setCurrentStep(1)
    setStepError(null)
    setGlobalError(null)
    setResults(null)
  }

  return (
    <div className="app-layout">
      {/* Floating orbs for ambiance */}
      <div className="ambient-orb orb-1" />
      <div className="ambient-orb orb-2" />
      <div className="ambient-orb orb-3" />

      {/* Header */}
      <header className="app-header">
        <div className="header-inner">
          <div className="header-logo">
            <div className="logo-icon">✦</div>
            <span className="logo-text">PagePersona</span>
            <span className="logo-tag">AI</span>
          </div>
          <nav className="header-nav">
            <span className="nav-item">Powered by Gemini API</span>
            <div className="header-status">
              <span className="status-dot" />
              <span className="status-text">Live</span>
            </div>
          </nav>
        </div>
      </header>

      {/* Hero section — only shown on input phase */}
      {phase === 'input' && (
        <section className="hero-section animate-fade-in-up">
          <div className="hero-badge">
            <span>🚀</span> AI-Powered CRO Personalization
          </div>
          <h1 className="hero-title">
            Turn Your Ad Creative Into a{' '}
            <span className="gradient-text">Personalized Landing Page</span>
          </h1>
          <p className="hero-subtitle">
            Upload your ad + paste a landing page URL. Our AI analyzes your ad's message, tone,
            and audience — then surgically personalizes the landing page for maximum conversion alignment.
          </p>
          <div className="hero-features">
            {[
              { icon: '🎯', label: 'Message Scent Matching' },
              { icon: '⚡', label: 'Real-time Personalization' },
              { icon: '📊', label: 'CRO Change Log' },
              { icon: '🔍', label: 'Side-by-Side Preview' },
            ].map((f) => (
              <div key={f.label} className="feature-chip">
                <span>{f.icon}</span>
                <span>{f.label}</span>
              </div>
            ))}
          </div>
        </section>
      )}

      {/* Main Content */}
      <main className="app-main">
        {/* INPUT PHASE */}
        {phase === 'input' && (
          <div className="input-layout animate-fade-in-up" style={{ animationDelay: '0.1s' }}>
            <div className="input-card glass-card shine">
              <div className="input-card-header">
                <h2 className="input-card-title">Start Personalizing</h2>
                <p className="input-card-subtitle">Takes ~15 seconds • Powered by Gemini AI</p>
              </div>
              <InputForm onSubmit={handleSubmit} loading={false} />
            </div>

            {/* How it works panel */}
            <div className="how-it-works glass-card">
              <h3 className="how-title">How It Works</h3>
              <div className="how-steps">
                {[
                  { n: '01', title: 'Scrape & Parse', desc: 'We extract headlines, CTAs, and hero content from your landing page.', icon: '🌐' },
                  { n: '02', title: 'Analyze Ad', desc: 'Gemini Vision reads your ad creative to identify tone, audience, and message.', icon: '🎨' },
                  { n: '03', title: 'Personalize', desc: 'AI generates CRO-optimized copy aligned with your ad\'s promise.', icon: '✨' },
                  { n: '04', title: 'Inject & Preview', desc: 'Changes are surgically applied to the original HTML — no new page created.', icon: '🚀' },
                ].map((step) => (
                  <div key={step.n} className="how-step">
                    <div className="how-step-num">{step.n}</div>
                    <div className="how-step-info">
                      <p className="how-step-title">{step.icon} {step.title}</p>
                      <p className="how-step-desc">{step.desc}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* LOADING PHASE */}
        {phase === 'loading' && (
          <div className="loading-layout animate-fade-in">
            <div className="loading-card glass-card">
              <div className="loading-animation">
                <div className="loading-rings">
                  <div className="ring ring-1" />
                  <div className="ring ring-2" />
                  <div className="ring ring-3" />
                </div>
                <div className="loading-icon animate-float">✨</div>
              </div>
              <h2 className="loading-title">AI is working its magic...</h2>
              <p className="loading-subtitle">Analyzing your ad and personalizing your landing page</p>
              <StepProgress currentStep={currentStep} error={null} />
            </div>
          </div>
        )}

        {/* ERROR PHASE */}
        {phase === 'error' && (
          <div className="error-layout animate-fade-in">
            <div className="error-card glass-card">
              <div className="error-icon">⚠</div>
              <h2 className="error-title">Something went wrong</h2>
              <p className="error-message">{globalError}</p>
              <StepProgress currentStep={currentStep} error={stepError} />
              <button id="retry-btn" className="btn-primary" onClick={handleReset} style={{ marginTop: '24px' }}>
                ← Try Again
              </button>
            </div>
          </div>
        )}

        {/* RESULTS PHASE */}
        {phase === 'results' && results && (
          <ResultsView data={results} onReset={handleReset} />
        )}
      </main>

      {/* Footer */}
      <footer className="app-footer">
        <p>Built with Gemini • Django REST • React • CRO Principles</p>
      </footer>
    </div>
  )
}
