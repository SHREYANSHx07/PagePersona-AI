import './StepProgress.css'

const STEPS = [
  { id: 1, icon: '🌐', label: 'Scraping Page', description: 'Extracting content from your landing page' },
  { id: 2, icon: '🎨', label: 'Analyzing Ad', description: 'Understanding your ad creative with AI vision' },
  { id: 3, icon: '✨', label: 'Personalizing', description: 'Generating CRO-optimized copy aligned with your ad' },
  { id: 4, icon: '🚀', label: 'Done!', description: 'Your personalized page is ready' },
]

export default function StepProgress({ currentStep, error }) {
  return (
    <div className="step-progress-container">
      <div className="step-progress">
        {STEPS.map((step, index) => {
          const isActive = currentStep === step.id
          const isCompleted = currentStep > step.id
          const isError = error && isActive
          const isUpcoming = currentStep < step.id

          return (
            <div
              key={step.id}
              id={`step-${step.id}`}
              className={`step-item ${isActive ? 'active' : ''} ${isCompleted ? 'completed' : ''} ${isError ? 'error' : ''} ${isUpcoming ? 'upcoming' : ''}`}
            >
              {/* Connector line */}
              {index > 0 && (
                <div className={`step-connector ${isCompleted || (isActive && !isError) ? 'filled' : ''}`} />
              )}

              {/* Step circle */}
              <div className="step-circle">
                {isError ? (
                  <span className="step-icon-error">✕</span>
                ) : isCompleted ? (
                  <span className="step-check">✓</span>
                ) : isActive ? (
                  <div className="step-spinner" />
                ) : (
                  <span className="step-number">{step.id}</span>
                )}

                {/* Pulse ring for active */}
                {isActive && !isError && (
                  <div className="step-pulse-ring" />
                )}
              </div>

              {/* Step info */}
              <div className="step-info">
                <p className="step-label">
                  {step.icon} {step.label}
                </p>
                <p className="step-description">
                  {isError ? error : step.description}
                </p>
              </div>
            </div>
          )
        })}
      </div>

      {/* Overall progress bar */}
      <div className="progress-bar-track">
        <div
          className="progress-bar-fill"
          style={{ width: `${Math.min(((currentStep - 1) / (STEPS.length - 1)) * 100, 100)}%` }}
        />
      </div>

      <p className="step-global-label">
        Step {Math.min(currentStep, STEPS.length)} of {STEPS.length} — {STEPS[Math.min(currentStep, STEPS.length) - 1]?.description}
      </p>
    </div>
  )
}
