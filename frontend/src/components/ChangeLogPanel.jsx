import { useState } from 'react'
import './ChangeLogPanel.css'

const TYPE_CONFIG = {
  headline: { color: '#7c3aed', bg: 'rgba(124,58,237,0.1)', border: 'rgba(124,58,237,0.25)' },
  subheadline: { color: '#2563eb', bg: 'rgba(37,99,235,0.1)', border: 'rgba(37,99,235,0.25)' },
  cta: { color: '#06b6d4', bg: 'rgba(6,182,212,0.1)', border: 'rgba(6,182,212,0.25)' },
  hero: { color: '#10b981', bg: 'rgba(16,185,129,0.1)', border: 'rgba(16,185,129,0.25)' },
  social_proof: { color: '#f59e0b', bg: 'rgba(245,158,11,0.1)', border: 'rgba(245,158,11,0.25)' },
}

function ChangeCard({ change, index }) {
  const [expanded, setExpanded] = useState(false)
  const config = TYPE_CONFIG[change.type] || TYPE_CONFIG.headline

  return (
    <div
      id={`change-card-${index}`}
      className="change-card"
      style={{
        '--card-color': config.color,
        '--card-bg': config.bg,
        '--card-border': config.border,
        animationDelay: `${index * 100}ms`,
      }}
    >
      <div
        className="change-card-header"
        onClick={() => setExpanded(e => !e)}
        role="button"
        tabIndex={0}
        onKeyDown={(e) => e.key === 'Enter' && setExpanded(ex => !ex)}
        aria-expanded={expanded}
      >
        <div className="change-card-left">
          <span className="change-icon">{change.icon}</span>
          <div>
            <p className="change-label">{change.label}</p>
            <p className="change-updated">"{change.updated}"</p>
          </div>
        </div>
        <div className="change-card-right">
          <span className="change-expand-icon" style={{ transform: expanded ? 'rotate(180deg)' : 'rotate(0deg)' }}>
            ▾
          </span>
        </div>
      </div>

      {expanded && (
        <div className="change-card-detail animate-fade-in">
          {change.original && (
            <div className="change-diff">
              <div className="diff-row diff-original">
                <span className="diff-label">Before</span>
                <p className="diff-text">"{change.original}"</p>
              </div>
              <div className="diff-arrow">→</div>
              <div className="diff-row diff-updated">
                <span className="diff-label">After</span>
                <p className="diff-text">"{change.updated}"</p>
              </div>
            </div>
          )}
          <div className="change-reasoning">
            <p className="reasoning-label">💡 Why this change?</p>
            <p className="reasoning-text">{change.reasoning}</p>
          </div>
        </div>
      )}
    </div>
  )
}

export default function ChangeLogPanel({ changeLog, adAnalysis, warnings = [] }) {
  const [showAdAnalysis, setShowAdAnalysis] = useState(false)

  return (
    <div className="changelog-panel">
      <div className="changelog-header">
        <div className="changelog-title-row">
          <h3 className="changelog-title">📊 Change Log</h3>
          <span className="changelog-count">{changeLog.length} changes applied</span>
        </div>
        <p className="changelog-subtitle">
          Each modification is aligned with CRO principles and message scent from your ad creative.
        </p>
      </div>

      {/* Warnings */}
      {warnings.length > 0 && (
        <div className="warnings-section">
          <p className="warning-title">⚠ Validation Notes</p>
          {warnings.map((w, i) => (
            <p key={i} className="warning-item">{w}</p>
          ))}
        </div>
      )}

      {/* Change cards */}
      <div className="change-list">
        {changeLog.map((change, i) => (
          <ChangeCard key={i} change={change} index={i} />
        ))}
      </div>

      {/* Ad Analysis Accordion */}
      {adAnalysis && (
        <div className="ad-analysis-section">
          <button
            id="toggle-ad-analysis"
            className="ad-analysis-toggle"
            onClick={() => setShowAdAnalysis(s => !s)}
          >
            <span>🎨 Ad Creative Analysis</span>
            <span style={{ transform: showAdAnalysis ? 'rotate(180deg)' : 'rotate(0deg)', transition: 'transform 0.2s' }}>▾</span>
          </button>

          {showAdAnalysis && (
            <div className="ad-analysis-grid animate-fade-in">
              {[
                { label: 'Core Message', value: adAnalysis.core_message, icon: '💬' },
                { label: 'Target Audience', value: adAnalysis.target_audience, icon: '🎯' },
                { label: 'Emotional Tone', value: adAnalysis.emotional_tone, icon: '💡' },
                { label: 'Offer / Promotion', value: adAnalysis.offer_details, icon: '🏷️' },
                { label: 'Pain Point', value: adAnalysis.pain_point_addressed, icon: '🩹' },
                { label: 'Brand Personality', value: adAnalysis.brand_personality, icon: '✨' },
                { label: 'Visual Style', value: adAnalysis.visual_style, icon: '🖼️' },
                { label: 'Color Palette', value: adAnalysis.color_palette, icon: '🎨' },
              ].filter(item => item.value).map((item, i) => (
                <div key={i} className="analysis-item">
                  <p className="analysis-item-label">{item.icon} {item.label}</p>
                  <p className="analysis-item-value">{item.value}</p>
                </div>
              ))}

              {adAnalysis.key_benefits?.length > 0 && (
                <div className="analysis-item analysis-item-full">
                  <p className="analysis-item-label">🌟 Key Benefits</p>
                  <div className="benefits-list">
                    {adAnalysis.key_benefits.map((b, i) => (
                      <span key={i} className="benefit-tag">✓ {b}</span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  )
}
