// FinanceHub Attribution Engine - Rust Implementation
// High-performance financial attribution calculations
// Compile with: rustc --crate-type=cdylib attribution.rs -o attribution.wasm

use std::f64;

#[no_mangle]
pub extern "C" fn calculate_holding_attribution(
    current_values: *const f64,
    avg_costs: *const f64,
    current_prices: *const f64,
    unrealized_pnls: *const f64,
    length: usize,
    period_return: f64,
) -> *mut f64 {
    let mut results = vec![0.0; length * 6]; // weight, return, contribution, percent, value_start, value_end
    
    let total_value: f64;
    unsafe {
        total_value = (0..length).map(|i| *current_values.add(i)).sum();
    }
    
    for i in 0..length {
        let current_value = unsafe { *current_values.add(i) };
        let avg_cost = unsafe { *avg_costs.add(i) };
        let current_price = unsafe { *current_prices.add(i) };
        
        let weight = if total_value > 0.0 { (current_value / total_value) * 100.0 } else { 0.0 };
        let return_pct = if avg_cost > 0.0 { ((current_price - avg_cost) / avg_cost) * 100.0 } else { 0.0 };
        let contribution = (weight / 100.0) * return_pct;
        let contribution_percent = if period_return != 0.0 { (contribution / period_return) * 100.0 } else { 0.0 };
        let value_start = current_value / (1.0 + return_pct / 100.0);
        let value_end = current_value;
        
        let idx = i * 6;
        results[idx] = weight;
        results[idx + 1] = return_pct;
        results[idx + 2] = contribution;
        results[idx + 3] = contribution_percent;
        results[idx + 4] = value_start;
        results[idx + 5] = value_end;
    }
    
    Box::into_raw(results.into_boxed_slice()) as *mut f64
}

#[no_mangle]
pub extern "C" fn calculate_sector_attribution(
    holdings_attribution: *const f64,
    sectors: *const *const u8,
    sector_count: usize,
    holdings_per_sector: *const usize,
) -> *mut f64 {
    let mut results = vec![0.0; sector_count * 4]; // weight, return, contribution, allocation_effect, selection_effect, total_effect
    
    for i in 0..sector_count {
        let sector_holdings_start = unsafe { *holdings_per_sector.add(i) };
        let sector_weight: f64;
        let sector_contribution: f64;
        let holdings_count: usize;
        
        unsafe {
            sector_weight = (sector_holdings_start..sector_holdings_start + 6)
                .map(|j| *holdings_attribution.add(j))
                .sum();
            sector_contribution = (sector_holdings_start + 2..sector_holdings_start + 6)
                .map(|j| *holdings_attribution.add(j))
                .sum();
            holdings_count = 0; // Simplified
        }
        
        let sector_return = if sector_weight > 0.0 { (sector_contribution / (sector_weight / 100.0)) } else { 0.0 };
        let allocation_effect = (sector_weight - 10.0) * sector_return * 0.1;
        let selection_effect = sector_contribution - allocation_effect;
        
        let idx = i * 6;
        results[idx] = sector_weight;
        results[idx + 1] = sector_return;
        results[idx + 2] = sector_contribution;
        results[idx + 3] = allocation_effect;
        results[idx + 4] = selection_effect;
        results[idx + 5] = sector_contribution;
    }
    
    Box::into_raw(results.into_boxed_slice()) as *mut f64
}

#[no_mangle]
pub extern "C" fn calculate_brinson_fachler(
    portfolio_weight: f64,
    benchmark_weight: f64,
    portfolio_return: f64,
    benchmark_return: f64,
) -> *mut f64 {
    let mut results = vec![0.0; 4]; // allocation, selection, interaction, total
    
    let weight_diff = portfolio_weight - benchmark_weight;
    let return_diff = portfolio_return - benchmark_return;
    
    let allocation = weight_diff * benchmark_return;
    let selection = portfolio_weight * return_diff;
    let interaction = weight_diff * return_diff;
    let total = allocation + selection + interaction;
    
    results[0] = (allocation * 100.0).round() / 100.0;
    results[1] = (selection * 100.0).round() / 100.0;
    results[2] = (interaction * 100.0).round() / 100.0;
    results[3] = (total * 100.0).round() / 100.0;
    
    Box::into_raw(results.into_boxed_slice()) as *mut f64
}

#[no_mangle]
pub extern "C" fn free_memory(ptr: *mut f64) {
    unsafe {
        let _ = Box::from_raw(ptr);
    }
}

#[no_mangle]
pub extern "C" fn calculate_correlation(
    returns1: *const f64,
    returns2: *const f64,
    length: usize,
) -> f64 {
    let mut sum1 = 0.0;
    let mut sum2 = 0.0;
    let mut sum1_sq = 0.0;
    let mut sum2_sq = 0.0;
    let mut product_sum = 0.0;
    
    for i in 0..length {
        let r1 = unsafe { *returns1.add(i) };
        let r2 = unsafe { *returns2.add(i) };
        
        sum1 += r1;
        sum2 += r2;
        sum1_sq += r1 * r1;
        sum2_sq += r2 * r2;
        product_sum += r1 * r2;
    }
    
    let n = length as f64;
    let numerator = n * product_sum - sum1 * sum2;
    let denominator = ((n * sum1_sq - sum1 * sum1) * (n * sum2_sq - sum2 * sum2)).sqrt();
    
    if denominator == 0.0 {
        return 0.0;
    }
    
    numerator / denominator
}

#[no_mangle]
pub extern "C" fn calculate_standard_deviation(returns: *const f64, length: usize) -> f64 {
    let mean: f64;
    let mut sum = 0.0;
    
    for i in 0..length {
        sum += unsafe { *returns.add(i) };
    }
    mean = sum / length as f64;
    
    let mut variance = 0.0;
    for i in 0..length {
        let diff = unsafe { *returns.add(i) } - mean;
        variance += diff * diff;
    }
    
    (variance / length as f64).sqrt()
}

#[no_mangle]
pub extern "C" fn calculate_beta(
    portfolio_returns: *const f64,
    benchmark_returns: *const f64,
    length: usize,
) -> f64 {
    let mut port_mean = 0.0;
    let mut bench_mean = 0.0;
    
    for i in 0..length {
        port_mean += unsafe { *portfolio_returns.add(i) };
        bench_mean += unsafe { *benchmark_returns.add(i) };
    }
    port_mean /= length as f64;
    bench_mean /= length as f64;
    
    let mut covariance = 0.0;
    let mut benchmark_variance = 0.0;
    
    for i in 0..length {
        let port_diff = unsafe { *portfolio_returns.add(i) } - port_mean;
        let bench_diff = unsafe { *benchmark_returns.add(i) } - bench_mean;
        covariance += port_diff * bench_diff;
        benchmark_variance += bench_diff * bench_diff;
    }
    
    if benchmark_variance == 0.0 {
        return 1.0;
    }
    
    covariance / benchmark_variance
}

#[no_mangle]
pub extern "C" fn calculate_sharpe_ratio(
    returns: *const f64,
    length: usize,
    risk_free_rate: f64,
) -> f64 {
    let mut sum = 0.0;
    for i in 0..length {
        sum += unsafe { *returns.add(i) };
    }
    let mean = sum / length as f64;
    
    let mut variance = 0.0;
    for i in 0..length {
        let diff = unsafe { *returns.add(i) } - mean;
        variance += diff * diff;
    }
    let std_dev = (variance / length as f64).sqrt();
    
    if std_dev == 0.0 {
        return 0.0;
    }
    
    (mean - risk_free_rate) / std_dev
}

#[no_mangle]
pub extern "C" fn calculate_max_drawdown(values: *const f64, length: usize) -> f64 {
    let mut max_drawdown = 0.0;
    let mut peak = unsafe { *values.add(0) };
    
    for i in 1..length {
        let current = unsafe { *values.add(i) };
        if current > peak {
            peak = current;
        }
        let drawdown = (peak - current) / peak;
        if drawdown > max_drawdown {
            max_drawdown = drawdown;
        }
    }
    
    max_drawdown
}

// Vectorized operations using SIMD-like approach
#[no_mangle]
pub extern "C" fn vector_dot_product(a: *const f64, b: *const f64, length: usize) -> f64 {
    let mut result = 0.0;
    for i in 0..length {
        result += unsafe { *a.add(i) * *b.add(i) };
    }
    result
}

#[no_mangle]
pub extern "C" fn vector_sum(values: *const f64, length: usize) -> f64 {
    let mut result = 0.0;
    for i in 0..length {
        result += unsafe { *values.add(i) };
    }
    result
}

#[no_mangle]
pub extern "C" fn vector_mean(values: *const f64, length: usize) -> f64 {
    if length == 0 {
        return 0.0;
    }
    vector_sum(values, length) / length as f64
}

#[no_mangle]
pub extern "C" fn exponential_moving_average(
    values: *const f64,
    length: usize,
    alpha: f64,
) -> *mut f64 {
    let mut ema = vec![0.0; length];
    
    if length > 0 {
        let first = unsafe { *values.add(0) };
        ema[0] = first;
        
        for i in 1..length {
            let prev_ema = ema[i - 1];
            let current = unsafe { *values.add(i) };
            ema[i] = alpha * current + (1.0 - alpha) * prev_ema;
        }
    }
    
    Box::into_raw(ema.into_boxed_slice()) as *mut f64
}
