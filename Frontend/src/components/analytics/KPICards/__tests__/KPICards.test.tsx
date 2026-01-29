import { render, screen, fireEvent } from '@testing-library/react'
import { ReturnCard } from '../ReturnCard'
import { ValueCard } from '../ValueCard'
import { RiskCard } from '../RiskCard'
import { DrawdownCard } from '../DrawdownCard'
import { CAGRCard } from '../CAGRCard'

describe('ReturnCard', () => {
  it('should display positive return with green styling', () => {
    render(<ReturnCard value={15.5} />)
    expect(screen.getByText('+15.50%')).toBeInTheDocument()
    expect(screen.getByText(/Total Return/i)).toBeInTheDocument()
  })

  it('should display negative return with red styling', () => {
    render(<ReturnCard value={-8.3} />)
    expect(screen.getByText('-8.30%')).toBeInTheDocument()
  })

  it('should display zero return correctly', () => {
    render(<ReturnCard value={0} />)
    expect(screen.getByText('+0.00%')).toBeInTheDocument()
  })
})

describe('ValueCard', () => {
  it('should display value in USD format', () => {
    render(<ValueCard value={100000} />)
    expect(screen.getByText('$100,000.00')).toBeInTheDocument()
  })

  it('should display positive change with label', () => {
    render(<ValueCard value={100000} change={5000} />)
    expect(screen.getByText(/\+\$5,000\.00/i)).toBeInTheDocument()
  })

  it('should display negative change with label', () => {
    render(<ValueCard value={100000} change={-3000} />)
    expect(screen.getByText(/\$3,000\.00/i)).toBeInTheDocument()
  })

  it('should format large numbers correctly', () => {
    render(<ValueCard value={1234567.89} />)
    expect(screen.getByText('$1,234,567.89')).toBeInTheDocument()
  })
})

describe('RiskCard', () => {
  it('should display volatility, beta, and sharpe ratio', () => {
    render(<RiskCard volatility={18.5} beta={1.1} sharpeRatio={1.25} />)
    expect(screen.getByText(/volatility/i)).toBeInTheDocument()
    expect(screen.getByText('18.50%')).toBeInTheDocument()
    expect(screen.getByText(/beta/i)).toBeInTheDocument()
    expect(screen.getByText('1.10')).toBeInTheDocument()
    expect(screen.getByText(/sharpe/i)).toBeInTheDocument()
    expect(screen.getByText('1.25')).toBeInTheDocument()
  })

  it('should display risk level badge', () => {
    render(<RiskCard volatility={18.5} beta={1.1} sharpeRatio={1.25} />)
    expect(screen.getByText(/Medium Risk/i)).toBeInTheDocument()
  })

  it('should display low risk for low volatility', () => {
    render(<RiskCard volatility={5} beta={0.8} sharpeRatio={1.5} />)
    expect(screen.getByText(/Low Risk/i)).toBeInTheDocument()
  })
})

describe('DrawdownCard', () => {
  it('should display max drawdown with date', () => {
    render(<DrawdownCard maxDrawdown={12.5} maxDrawdownDate="2024-03-15" recoveryTime={45} />)
    expect(screen.getByText(/max drawdown/i)).toBeInTheDocument()
    expect(screen.getByText('-12.50%')).toBeInTheDocument()
    expect(screen.getByText(/Largest drop on/i)).toBeInTheDocument()
    expect(screen.getByText(/45 days/i)).toBeInTheDocument()
  })

  it('should handle missing date', () => {
    render(<DrawdownCard maxDrawdown={8.5} />)
    expect(screen.getByText('-8.50%')).toBeInTheDocument()
    expect(screen.queryByText(/2024/)).not.toBeInTheDocument()
  })

  it('should display negative drawdown as positive percentage', () => {
    render(<DrawdownCard maxDrawdown={-15.2} />)
    expect(screen.getByText('15.20%')).toBeInTheDocument()
  })
})

describe('CAGRCard', () => {
  it('should display CAGR', () => {
    render(<CAGRCard cagr={22.5} annualizedReturn={18.3} />)
    expect(screen.getByText(/cagr/i)).toBeInTheDocument()
    expect(screen.getByText('+22.50%')).toBeInTheDocument()
    expect(screen.getByText('Compound Annual Growth Rate')).toBeInTheDocument()
  })

  it('should handle zero values', () => {
    render(<CAGRCard cagr={0} annualizedReturn={0} />)
    expect(screen.getByText('+0.00%')).toBeInTheDocument()
  })

  it('should display negative CAGR correctly', () => {
    render(<CAGRCard cagr={-5.2} annualizedReturn={-3.8} />)
    expect(screen.getByText('-5.20%')).toBeInTheDocument()
  })
})
