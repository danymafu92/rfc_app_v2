// Small shared utilities for mapping numeric risk scores to UI styles
export const getRiskColor = (riskScore) => {
  if (riskScore <= 3.5) {
    return '#22c55e'
  } else if (riskScore <= 7.4) {
    return '#f59e0b'
  } else {
    return '#ef4444'
  }
}

export const getRiskCategory = (riskScore) => {
  if (riskScore <= 3.5) {
    return 'Low'
  } else if (riskScore <= 7.4) {
    return 'Medium'
  } else {
    return 'High'
  }
}

export const getRiskClass = (riskScore) => {
  if (riskScore <= 3.5) {
    return 'risk-low'
  } else if (riskScore <= 7.4) {
    return 'risk-medium'
  } else {
    return 'risk-high'
  }
}

export const formatRiskScore = (score) => {
  return typeof score === 'number' ? score.toFixed(2) : '0.00'
}
