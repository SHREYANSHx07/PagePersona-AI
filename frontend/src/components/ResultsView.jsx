import { useState } from 'react'
import PagePreview from './PagePreview'
import ChangeLogPanel from './ChangeLogPanel'
import './ResultsView.css'

export default function ResultsView({ data, onReset }) {
  const [activeView, setActiveView] = useState('split') // 'split' | 'original' | 'personalized'
  const [showChangelog, setShowChangelog] = useState(true)

  const { personalized_html, original_html, change_log, ad_analysis, landing_page_url, personalization, validation_warnings } = data

  return (
    <div className="results-view animate-fade-in">
      {/* Results Header */}
      <div className="results-header">
        <div className="results-header-left">
          <div className="results-title-row">
            <h2 className="results-title">
              <span className="gradient-text">✨ Personalization Complete</span>
            </h2>
            <div className="results-badges">
              <span className="badge badge-purple">{change_log.length} Changes</span>
              <span className="badge badge-green">CRO Optimized</span>
              <span className="badge badge-cyan">Ad Aligned</span>
            </div>
          </div>
          <p className="results-subtitle">
            Your landing page has been personalized to match the ad creative's message, tone, and audience.
          </p>
        </div>
        <button id="reset-btn" className="btn-secondary" onClick={onReset}>
          ← New Personalization
        </button>
      </div>

      {/* View Toggle */}
      <div className="view-toggle-bar">
        <div className="view-toggle" role="tablist">
          {[
            { id: 'split', label: '⚡ Side by Side', icon: '' },
            { id: 'original', label: '📄 Original', icon: '' },
            { id: 'personalized', label: '✨ Personalized', icon: '' },
          ].map((view) => (
            <button
              key={view.id}
              id={`view-tab-${view.id}`}
              role="tab"
              aria-selected={activeView === view.id}
              className={`view-tab ${activeView === view.id ? 'active' : ''}`}
              onClick={() => setActiveView(view.id)}
            >
              {view.label}
            </button>
          ))}
        </div>

        <div className="view-actions">
          <button
            id="toggle-changelog-btn"
            className="btn-secondary"
            onClick={() => setShowChangelog(s => !s)}
          >
            {showChangelog ? '📊 Hide Changes' : '📊 Show Changes'}
          </button>
          <a
            href={landing_page_url}
            target="_blank"
            rel="noopener noreferrer"
            className="btn-secondary"
            id="open-original-btn"
          >
            ↗ Open Original
          </a>
        </div>
      </div>

      {/* Personalization Summary Strip */}
      <div className="personalization-strip">
        <div className="strip-item">
          <p className="strip-label">New Headline</p>
          <p className="strip-value">"{personalization.new_headline}"</p>
        </div>
        <div className="strip-divider" />
        <div className="strip-item">
          <p className="strip-label">New CTA</p>
          <p className="strip-value strip-cta">"{personalization.new_cta_text}"</p>
        </div>
        <div className="strip-divider" />
        <div className="strip-item">
          <p className="strip-label">Ad Tone</p>
          <p className="strip-value">{ad_analysis?.emotional_tone || 'Analyzed'}</p>
        </div>
        <div className="strip-divider" />
        <div className="strip-item">
          <p className="strip-label">Target Audience</p>
          <p className="strip-value strip-truncate">{ad_analysis?.target_audience || 'Analyzed'}</p>
        </div>
      </div>

      {/* Preview Area */}
      <div className={`preview-area view-${activeView}`}>
        {(activeView === 'split' || activeView === 'original') && (
          <div className="preview-column">
            <div className="preview-column-label preview-original-label">
              <span className="label-dot label-dot-red" /> Original Page
            </div>
            <PagePreview
              html={original_html}
              title="Original"
              url={landing_page_url}
            />
          </div>
        )}

        {(activeView === 'split' || activeView === 'personalized') && (
          <div className="preview-column">
            <div className="preview-column-label preview-personalized-label">
              <span className="label-dot label-dot-green" /> Personalized Page
            </div>
            <PagePreview
              html={personalized_html}
              title="Personalized ✨"
              url={null}
            />
          </div>
        )}
      </div>

      {/* Change Log Panel */}
      {showChangelog && (
        <div className="changelog-wrapper animate-fade-in-up">
          <ChangeLogPanel
            changeLog={change_log}
            adAnalysis={ad_analysis}
            warnings={validation_warnings || []}
          />
        </div>
      )}
    </div>
  )
}
