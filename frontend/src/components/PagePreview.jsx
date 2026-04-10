import { useRef, useState, useEffect } from 'react'
import './PagePreview.css'

export default function PagePreview({ html, title, url }) {
  const iframeRef = useRef(null)
  const [loaded, setLoaded] = useState(false)

  useEffect(() => {
    setLoaded(false)
  }, [html])

  return (
    <div className="page-preview">
      {/* Header bar */}
      <div className="preview-header">
        <div className="preview-header-left">
          <div className="preview-dots">
            <span /><span /><span />
          </div>
          <div className="preview-title-badge">{title}</div>
        </div>
        {url && (
          <a
            href={url}
            target="_blank"
            rel="noopener noreferrer"
            className="preview-external-link"
            title="Open original page"
          >
            ↗
          </a>
        )}
      </div>

      {/* Address bar */}
      {url && (
        <div className="preview-address-bar">
          <span className="address-lock">🔒</span>
          <span className="address-text">{url}</span>
        </div>
      )}

      {/* iframe */}
      <div className="preview-iframe-wrapper">
        {!loaded && <div className="preview-skeleton"><div className="skeleton-shimmer" /></div>}
        <iframe
          ref={iframeRef}
          srcDoc={html}
          sandbox="allow-scripts allow-same-origin"
          className={`preview-iframe ${loaded ? 'loaded' : ''}`}
          title={title}
          onLoad={() => setLoaded(true)}
        />
      </div>
    </div>
  )
}
