// WebAssembly Attribution Module - TypeScript Bindings
// High-performance financial calculations using Rust WebAssembly

export interface WasmAttributionResult {
  weights: Float64Array
  returns: Float64Array
  contributions: Float64Array
  contributionPercents: Float64Array
  valueStarts: Float64Array
  valueEnds: Float64Array
}

export interface WasmBrinsonResult {
  allocation: number
  selection: number
  interaction: number
  total: number
}

export interface WasmFinancialMetrics {
  correlation: number
  beta: number
  sharpeRatio: number
  maxDrawdown: number
  standardDeviation: number
}

let wasmModule: WebAssembly.Instance | null = null
let wasmMemory: WebAssembly.Memory | null = null

async function loadWasmModule(): Promise<WebAssembly.Instance> {
  if (wasmModule) return wasmModule

  try {
    const response = await fetch('/wasm/attribution.wasm')
    const wasmBytes = await response.arrayBuffer()
    
    const importObject = {
      env: {
        memory: wasmMemory || (wasmMemory = new WebAssembly.Memory({ initial: 256, maximum: 512 })),
      },
    }

    const wasmModuleInstance = await WebAssembly.instantiate(wasmBytes, importObject)
    wasmModule = wasmModuleInstance.instance
    return wasmModule
  } catch (error) {
    console.warn('WebAssembly module not available, falling back to JavaScript implementation')
    throw error
  }
}

function createFloat64ArrayFromPointer(pointer: number, length: number): Float64Array {
  return new Float64Array(wasmMemory!.buffer, pointer, length)
}

export async function calculateHoldingAttributionWasm(
  currentValues: number[],
  avgCosts: number[],
  currentPrices: number[],
  unrealizedPnls: number[],
  periodReturn: number = 0
): Promise<WasmAttributionResult> {
  try {
    await loadWasmModule()
    
    const length = currentValues.length
    const inputValues = new Float64Array([
      ...currentValues,
      ...avgCosts,
      ...currentPrices,
      ...unrealizedPnls,
    ])
    
    const resultsPtr = wasmModule!.exports.calculate_holding_attribution(
      inputValues.byteOffset,
      inputValues.byteOffset + length * 8,
      inputValues.byteOffset + length * 16,
      inputValues.byteOffset + length * 24,
      length,
      periodReturn
    ) as number
    
    const results = createFloat64ArrayFromPointer(resultsPtr, length * 6)
    
    return {
      weights: results.subarray(0, length),
      returns: results.subarray(length, length * 2),
      contributions: results.subarray(length * 2, length * 3),
      contributionPercents: results.subarray(length * 3, length * 4),
      valueStarts: results.subarray(length * 4, length * 5),
      valueEnds: results.subarray(length * 5, length * 6),
    }
  } catch {
    return calculateHoldingAttributionJs(currentValues, avgCosts, currentPrices, unrealizedPnls, periodReturn)
  }
}

export async function calculateBrinsonFachlerWasm(
  portfolioWeight: number,
  benchmarkWeight: number,
  portfolioReturn: number,
  benchmarkReturn: number
): Promise<WasmBrinsonResult> {
  try {
    await loadWasmModule()
    
    const resultsPtr = wasmModule!.exports.calculate_brinson_fachler(
      portfolioWeight,
      benchmarkWeight,
      portfolioReturn,
      benchmarkReturn
    ) as number
    
    const results = createFloat64ArrayFromPointer(resultsPtr, 4)
    
    return {
      allocation: results[0],
      selection: results[1],
      interaction: results[2],
      total: results[3],
    }
  } catch {
    return calculateBrinsonFachlerJs(portfolioWeight, benchmarkWeight, portfolioReturn, benchmarkReturn)
  }
}

export async function calculateCorrelationWasm(
  returns1: number[],
  returns2: number[]
): Promise<number> {
  try {
    await loadWasmModule()
    
    const arr1 = new Float64Array(returns1)
    const arr2 = new Float64Array(returns2)
    
    return wasmModule!.exports.calculate_correlation(
      arr1.byteOffset,
      arr2.byteOffset,
      returns1.length
    ) as number
  } catch {
    return calculateCorrelationJs(returns1, returns2)
  }
}

export async function calculateBetaWasm(
  portfolioReturns: number[],
  benchmarkReturns: number[]
): Promise<number> {
  try {
    await loadWasmModule()
    
    const arr1 = new Float64Array(portfolioReturns)
    const arr2 = new Float64Array(benchmarkReturns)
    
    return wasmModule!.exports.calculate_beta(
      arr1.byteOffset,
      arr2.byteOffset,
      portfolioReturns.length
    ) as number
  } catch {
    return calculateBetaJs(portfolioReturns, benchmarkReturns)
  }
}

export async function calculateSharpeRatioWasm(
  returns: number[],
  riskFreeRate: number = 0.02
): Promise<number> {
  try {
    await loadWasmModule()
    
    const arr = new Float64Array(returns)
    
    return wasmModule!.exports.calculate_sharpe_ratio(
      arr.byteOffset,
      returns.length,
      riskFreeRate
    ) as number
  } catch {
    return calculateSharpeRatioJs(returns, riskFreeRate)
  }
}

export async function calculateMaxDrawdownWasm(values: number[]): Promise<number> {
  try {
    await loadWasmModule()
    
    const arr = new Float64Array(values)
    
    return wasmModule!.exports.calculate_max_drawdown(arr.byteOffset, values.length) as number
  } catch {
    return calculateMaxDrawdownJs(values)
  }
}

export async function calculateStandardDeviationWasm(returns: number[]): Promise<number> {
  try {
    await loadWasmModule()
    
    const arr = new Float64Array(returns)
    
    return wasmModule!.exports.calculate_standard_deviation(arr.byteOffset, returns.length) as number
  } catch {
    return calculateStandardDeviationJs(returns)
  }
}

// JavaScript Fallback Implementations
function calculateHoldingAttributionJs(
  currentValues: number[],
  avgCosts: number[],
  currentPrices: number[],
  unrealizedPnls: number[],
  periodReturn: number
): WasmAttributionResult {
  const length = currentValues.length
  const totalValue = currentValues.reduce((sum, v) => sum + v, 0)
  
  const weights = new Float64Array(length)
  const returns = new Float64Array(length)
  const contributions = new Float64Array(length)
  const contributionPercents = new Float64Array(length)
  const valueStarts = new Float64Array(length)
  const valueEnds = new Float64Array(length)
  
  for (let i = 0; i < length; i++) {
    weights[i] = totalValue > 0 ? (currentValues[i] / totalValue) * 100 : 0
    returns[i] = avgCosts[i] > 0 ? ((currentPrices[i] - avgCosts[i]) / avgCosts[i]) * 100 : 0
    contributions[i] = (weights[i] / 100) * returns[i]
    contributionPercents[i] = periodReturn !== 0 ? (contributions[i] / periodReturn) * 100 : 0
    valueStarts[i] = currentValues[i] / (1 + returns[i] / 100)
    valueEnds[i] = currentValues[i]
  }
  
  return { weights, returns, contributions, contributionPercents, valueStarts, valueEnds }
}

function calculateBrinsonFachlerJs(
  portfolioWeight: number,
  benchmarkWeight: number,
  portfolioReturn: number,
  benchmarkReturn: number
): WasmBrinsonResult {
  const weightDiff = portfolioWeight - benchmarkWeight
  const returnDiff = portfolioReturn - benchmarkReturn
  
  const allocation = weightDiff * benchmarkReturn
  const selection = portfolioWeight * returnDiff
  const interaction = weightDiff * returnDiff
  const total = allocation + selection + interaction
  
  return {
    allocation: Math.round(allocation * 100) / 100,
    selection: Math.round(selection * 100) / 100,
    interaction: Math.round(interaction * 100) / 100,
    total: Math.round(total * 100) / 100,
  }
}

function calculateCorrelationJs(returns1: number[], returns2: number[]): number {
  const n = returns1.length
  const mean1 = returns1.reduce((a, b) => a + b, 0) / n
  const mean2 = returns2.reduce((a, b) => a + b, 0) / n
  
  let numerator = 0
  let denom1 = 0
  let denom2 = 0
  
  for (let i = 0; i < n; i++) {
    const diff1 = returns1[i] - mean1
    const diff2 = returns2[i] - mean2
    numerator += diff1 * diff2
    denom1 += diff1 * diff1
    denom2 += diff2 * diff2
  }
  
  const denominator = Math.sqrt(denom1 * denom2)
  return denominator === 0 ? 0 : numerator / denominator
}

function calculateBetaJs(portfolioReturns: number[], benchmarkReturns: number[]): number {
  const n = portfolioReturns.length
  const portMean = portfolioReturns.reduce((a, b) => a + b, 0) / n
  const benchMean = benchmarkReturns.reduce((a, b) => a + b, 0) / n
  
  let covariance = 0
  let benchmarkVariance = 0
  
  for (let i = 0; i < n; i++) {
    const portDiff = portfolioReturns[i] - portMean
    const benchDiff = benchmarkReturns[i] - benchMean
    covariance += portDiff * benchDiff
    benchmarkVariance += benchDiff * benchDiff
  }
  
  return benchmarkVariance === 0 ? 1 : covariance / benchmarkVariance
}

function calculateSharpeRatioJs(returns: number[], riskFreeRate: number): number {
  const mean = returns.reduce((a, b) => a + b, 0) / returns.length
  const variance = returns.reduce((sum, r) => sum + Math.pow(r - mean, 2), 0) / returns.length
  const stdDev = Math.sqrt(variance)
  return stdDev === 0 ? 0 : (mean - riskFreeRate) / stdDev
}

function calculateMaxDrawdownJs(values: number[]): number {
  let maxDrawdown = 0
  let peak = values[0]
  
  for (const current of values) {
    if (current > peak) peak = current
    const drawdown = (peak - current) / peak
    if (drawdown > maxDrawdown) maxDrawdown = drawdown
  }
  
  return maxDrawdown
}

function calculateStandardDeviationJs(returns: number[]): number {
  const mean = returns.reduce((a, b) => a + b, 0) / returns.length
  const variance = returns.reduce((sum, r) => sum + Math.pow(r - mean, 2), 0) / returns.length
  return Math.sqrt(variance)
}

// Export all functions
export const wasmAttribution = {
  calculateHoldingAttribution: calculateHoldingAttributionWasm,
  calculateBrinsonFachler: calculateBrinsonFachlerWasm,
  calculateCorrelation: calculateCorrelationWasm,
  calculateBeta: calculateBetaWasm,
  calculateSharpeRatio: calculateSharpeRatioWasm,
  calculateMaxDrawdown: calculateMaxDrawdownWasm,
  calculateStandardDeviation: calculateStandardDeviationWasm,
}

export const jsAttribution = {
  calculateHoldingAttribution: calculateHoldingAttributionJs,
  calculateBrinsonFachler: calculateBrinsonFachlerJs,
  calculateCorrelation: calculateCorrelationJs,
  calculateBeta: calculateBetaJs,
  calculateSharpeRatio: calculateSharpeRatioJs,
  calculateMaxDrawdown: calculateMaxDrawdownJs,
  calculateStandardDeviation: calculateStandardDeviationJs,
}
