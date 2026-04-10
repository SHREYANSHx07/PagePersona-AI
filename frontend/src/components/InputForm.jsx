import { useState, useRef, useCallback } from 'react'
import './InputForm.css'

export default function InputForm({ onSubmit, loading }) {
  const [landingPageUrl, setLandingPageUrl] = useState('')
  const [imageMode, setImageMode] = useState('upload') // 'upload' | 'url'
  const [imageFile, setImageFile] = useState(null)
  const [imageUrl, setImageUrl] = useState('')
  const [imagePreview, setImagePreview] = useState(null)
  const [dragOver, setDragOver] = useState(false)
  const [errors, setErrors] = useState({})
  const fileInputRef = useRef(null)

  const handleFileSelect = (file) => {
    if (!file) return
    if (!file.type.startsWith('image/')) {
      setErrors(e => ({ ...e, image: 'Please upload a valid image file.' }))
      return
    }
    if (file.size > 10 * 1024 * 1024) {
      setErrors(e => ({ ...e, image: 'Image must be under 10MB.' }))
      return
    }
    setErrors(e => ({ ...e, image: null }))
    setImageFile(file)
    const reader = new FileReader()
    reader.onload = (ev) => setImagePreview(ev.target.result)
    reader.readAsDataURL(file)
  }

  const handleDrop = useCallback((e) => {
    e.preventDefault()
    setDragOver(false)
    const file = e.dataTransfer.files[0]
    handleFileSelect(file)
  }, [])

  const handleDragOver = (e) => {
    e.preventDefault()
    setDragOver(true)
  }

  const handleDragLeave = () => setDragOver(false)

  const isValidLandingUrl = (raw) => {
    const t = raw.trim()
    if (!t) return false
    try {
      const withProto = /^https?:\/\//i.test(t) ? t : `https://${t}`
      const u = new URL(withProto)
      const h = u.hostname
      if (h === 'localhost' || /^(\d{1,3}\.){3}\d{1,3}$/.test(h)) return true
      return h.includes('.')
    } catch {
      return false
    }
  }

  const validate = () => {
    const newErrors = {}
    if (!landingPageUrl.trim()) {
      newErrors.url = 'Landing page URL is required.'
    } else if (!isValidLandingUrl(landingPageUrl)) {
      newErrors.url = 'Please enter a valid URL (e.g. https://example.com or http://localhost:3000).'
    }
    if (imageMode === 'upload' && !imageFile) {
      newErrors.image = 'Please upload an ad image.'
    }
    if (imageMode === 'url' && !imageUrl.trim()) {
      newErrors.image = 'Please enter an image URL.'
    }
    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleSubmit = (e) => {
    e.preventDefault()
    if (!validate()) return

    const formData = new FormData()
    formData.append('landing_page_url', landingPageUrl.trim())
    if (imageMode === 'upload' && imageFile) {
      formData.append('image', imageFile)
    } else if (imageMode === 'url' && imageUrl) {
      formData.append('image_url', imageUrl.trim())
    }
    onSubmit(formData)
  }

  const clearImage = () => {
    setImageFile(null)
    setImagePreview(null)
    setErrors(e => ({ ...e, image: null }))
  }

  return (
    <form className="input-form" onSubmit={handleSubmit} noValidate>
      {/* Landing Page URL */}
      <div className="form-group">
        <label className="form-label">
          <span className="label-icon">🌐</span>
          Landing Page URL
        </label>
        <div className="input-wrapper">
          <input
            id="landing-page-url"
            type="url"
            className={`input-field ${errors.url ? 'input-error' : ''}`}
            placeholder="https://yourproduct.com/landing"
            value={landingPageUrl}
            onChange={(e) => {
              setLandingPageUrl(e.target.value)
              setErrors(err => ({ ...err, url: null }))
            }}
          />
          {landingPageUrl && (
            <button
              type="button"
              className="input-clear"
              onClick={() => setLandingPageUrl('')}
            >×</button>
          )}
        </div>
        {errors.url && <p className="error-msg">⚠ {errors.url}</p>}
      </div>

      {/* Ad Creative */}
      <div className="form-group">
        <label className="form-label">
          <span className="label-icon">🎨</span>
          Ad Creative
        </label>

        {/* Mode Toggle */}
        <div className="mode-toggle" role="tablist">
          <button
            type="button"
            role="tab"
            id="tab-upload"
            aria-selected={imageMode === 'upload'}
            className={`mode-btn ${imageMode === 'upload' ? 'active' : ''}`}
            onClick={() => { setImageMode('upload'); clearImage() }}
          >
            📁 Upload Image
          </button>
          <button
            type="button"
            role="tab"
            id="tab-url"
            aria-selected={imageMode === 'url'}
            className={`mode-btn ${imageMode === 'url' ? 'active' : ''}`}
            onClick={() => { setImageMode('url'); clearImage() }}
          >
            🔗 Image URL
          </button>
        </div>

        {/* Upload Zone */}
        {imageMode === 'upload' && (
          <div>
            {!imagePreview ? (
              <div
                id="drop-zone"
                className={`drop-zone ${dragOver ? 'drag-over' : ''} ${errors.image ? 'drop-error' : ''}`}
                onDrop={handleDrop}
                onDragOver={handleDragOver}
                onDragLeave={handleDragLeave}
                onClick={() => fileInputRef.current?.click()}
                role="button"
                tabIndex={0}
                onKeyDown={(e) => e.key === 'Enter' && fileInputRef.current?.click()}
                aria-label="Upload ad image"
              >
                <div className="drop-zone-icon">
                  {dragOver ? '📂' : '🖼️'}
                </div>
                <p className="drop-zone-text">
                  {dragOver ? 'Drop it!' : 'Drag & drop your ad image here'}
                </p>
                <p className="drop-zone-sub">or click to browse • PNG, JPG, WEBP • up to 10MB</p>
                <input
                  ref={fileInputRef}
                  type="file"
                  accept="image/*"
                  style={{ display: 'none' }}
                  onChange={(e) => handleFileSelect(e.target.files[0])}
                />
              </div>
            ) : (
              <div className="image-preview-container">
                <img src={imagePreview} alt="Ad creative preview" className="image-preview" />
                <div className="preview-overlay">
                  <button type="button" className="preview-remove" onClick={clearImage}>
                    ✕ Remove
                  </button>
                </div>
                <div className="preview-badge">
                  ✓ {imageFile?.name}
                </div>
              </div>
            )}
          </div>
        )}

        {/* Image URL Input */}
        {imageMode === 'url' && (
          <div className="input-wrapper">
            <input
              id="image-url-input"
              type="url"
              className={`input-field ${errors.image ? 'input-error' : ''}`}
              placeholder="https://example.com/ad-image.jpg"
              value={imageUrl}
              onChange={(e) => {
                setImageUrl(e.target.value)
                setErrors(err => ({ ...err, image: null }))
              }}
            />
          </div>
        )}

        {errors.image && <p className="error-msg">⚠ {errors.image}</p>}
      </div>

      {/* Submit Button */}
      <button
        id="submit-btn"
        type="submit"
        className="btn-primary submit-btn"
        disabled={loading}
      >
        {loading ? (
          <>
            <span className="spinner" />
            Personalizing...
          </>
        ) : (
          <>
            <span>✨</span>
            Analyze & Personalize
          </>
        )}
      </button>
    </form>
  )
}
