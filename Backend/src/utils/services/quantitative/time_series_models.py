"""
Quantitative Models Module
Time series analysis and forecasting models.
"""
import numpy as np
from typing import Tuple, Optional, Dict, List
from dataclasses import dataclass
from scipy import stats


@dataclass
class ARIMAResult:
    """Result container for ARIMA model."""
    forecast: np.ndarray
    confidence_interval_lower: np.ndarray
    confidence_interval_upper: np.ndarray
    aic: float
    bic: float
    order: Tuple[int, int, int]
    residuals: np.ndarray
    compute_time_ms: float


@dataclass
class GARCHResult:
    """Result container for GARCH model."""
    conditional_volatility: np.ndarray
    forecast_volatility: float
    omega: float
    alpha: float
    beta: float
    total_volatility: float
    compute_time_ms: float


@dataclass
class KalmanFilterResult:
    """Result container for Kalman filter."""
    filtered_state: np.ndarray
    filtered_covariance: np.ndarray
    predicted_state: np.ndarray
    predicted_covariance: np.ndarray
    likelihood: float
    compute_time_ms: float


@dataclass
class HalfLifeResult:
    """Result container for half-life calculation."""
    half_life: float
    hurst_exponent: float
    mean_reversion_strength: str
    compute_time_ms: float


@dataclass
class HurstExponentResult:
    """Result container for Hurst exponent estimation."""
    hurst_exponent: float
    trend_type: str
    interpretation: str
    compute_time_ms: float


class TimeSeriesModels:
    """
    Time series forecasting and volatility models.
    
    Supports:
    - ARIMA (AutoRegressive Integrated Moving Average)
    - GARCH (Generalized AutoRegressive Conditional Heteroskedasticity)
    - Kalman Filter (dynamic linear models)
    """
    
    def __init__(self):
        """Initialize time series models."""
        pass
    
    def arima_forecast(
        self,
        data: np.ndarray,
        order: Tuple[int, int, int] = (1, 0, 1),
        steps: int = 10,
        confidence_level: float = 0.95
    ) -> ARIMAResult:
        """
        ARIMA forecasting with confidence intervals.
        
        Parameters:
        -----------
        data : np.ndarray
            Time series data
        order : Tuple[int, int, int]
            (p, d, q) order of ARIMA model
        steps : int
            Number of forecast steps
        confidence_level : float
            Confidence level for intervals
        
        Returns:
        --------
        ARIMAResult
            Forecast and statistics
        """
        import time
        start_time = time.perf_counter()
        
        p, d, q = order
        
        # Differencing if needed
        diff_data = data.copy()
        for _ in range(d):
            diff_data = np.diff(diff_data)
        
        # Fit AR(p) model using Yule-Walker
        n = len(diff_data)
        acf = np.correlate(diff_data - np.mean(diff_data), diff_data - np.mean(diff_data), mode='full')
        acf = acf[n-1:] / acf[n-1]
        
        # AR coefficients using Levinson-Durbin recursion
        ar_coeffs = self._levinson_durbin(acf, p)
        
        # MA(q) approximation using innovations algorithm
        ma_coeffs = np.zeros(q + 1)
        ma_coeffs[0] = 1.0
        
        # Residual variance
        residuals = diff_data.copy()
        for t in range(p, n):
            ar_pred = np.sum(ar_coeffs * diff_data[t-p:t][::-1])
            residuals[t] = diff_data[t] - ar_pred
        
        residual_var = np.var(residuals[p:])
        
        # Forecast
        forecast = np.zeros(steps)
        ci_lower = np.zeros(steps)
        ci_upper = np.zeros(steps)
        
        last_values = list(diff_data[-p:][::-1])
        
        z_score = stats.norm.ppf((1 + confidence_level) / 2)
        
        for h in range(steps):
            # AR forecast
            ar_term = np.sum(ar_coeffs * last_values)
            forecast[h] = ar_term
            
            # Confidence interval widens with horizon
            interval_width = z_score * np.sqrt(residual_var * (1 + h * 0.1))
            ci_lower[h] = forecast[h] - interval_width
            ci_upper[h] = forecast[h] + interval_width
            
            # Update last values for next step
            last_values = [forecast[h]] + last_values[:-1]
        
        # Integrate back from differencing
        if d > 0:
            last_level = data[-1]
            forecast = self._integrate_forecast(forecast, last_level, d)
            ci_lower = self._integrate_forecast(ci_lower, last_level, d)
            ci_upper = self._integrate_forecast(ci_upper, last_level, d)
        
        # AIC and BIC
        n_params = p + q + 1
        aic = n_params * np.log(residual_var) + 2 * n_params
        bic = n_params * np.log(n) + n_params * np.log(2 * np.pi) + n_params
        
        compute_time_ms = (time.perf_counter() - start_time) * 1000
        
        return ARIMAResult(
            forecast=forecast,
            confidence_interval_lower=ci_lower,
            confidence_interval_upper=ci_upper,
            aic=aic,
            bic=bic,
            order=order,
            residuals=residuals,
            compute_time_ms=compute_time_ms
        )
    
    def _levinson_durbin(self, r: np.ndarray, order: int) -> np.ndarray:
        """
        Levinson-Durbin recursion for AR coefficient estimation.
        """
        n = len(r)
        if order >= n:
            order = n - 1
        
        # Initialize
        a = np.zeros(order + 1)
        sigma = r[0]
        
        for k in range(1, order + 1):
            # Calculate reflection coefficient
            sum_r_a = sum(r[j] * a[j] for j in range(1, k))
            gamma = (r[k] - sum_r_a) / sigma
            
            a[k] = gamma
            
            # Update coefficients
            for j in range(1, (k + 1) // 2):
                temp = a[j] - gamma * a[k - j]
                a[j] = temp
                a[k - j] = temp
            
            # Update variance
            sigma *= (1 - gamma ** 2)
        
        return a[1:]
    
    def _integrate_forecast(self, forecast: np.ndarray, last_level: float, d: int) -> np.ndarray:
        """Integrate differenced forecast back to original level."""
        integrated = np.cumsum(forecast)
        return last_level + integrated
    
    def garch11_forecast(
        self,
        data: np.ndarray,
        omega: float = 0.0001,
        alpha: float = 0.05,
        beta: float = 0.90,
        steps: int = 10
    ) -> GARCHResult:
        """
        GARCH(1,1) volatility forecasting.
        
        Parameters:
        -----------
        data : np.ndarray
            Returns series
        omega : float
            Long-run variance constant
        alpha : float
            ARCH coefficient (impact of past shocks)
        beta : float
            GARCH coefficient (impact of past volatility)
        steps : int
            Forecast horizon
        
        Returns:
        --------
        GARCHResult
            Conditional volatility and forecast
        """
        import time
        start_time = time.perf_counter()
        
        # Calculate squared returns
        squared_returns = data ** 2
        
        # Estimate parameters if not provided
        if omega <= 0:
            omega = np.var(data) * 0.01
        
        if alpha <= 0 or beta <= 0:
            # Simple estimation
            long_run_var = np.var(data)
            alpha = 0.05
            beta = 0.90
        
        # Calculate conditional variance
        n = len(data)
        h = np.zeros(n)
        h[0] = np.var(data)
        
        for t in range(1, n):
            h[t] = omega + alpha * data[t-1]**2 + beta * h[t-1]
        
        # Long-run (unconditional) volatility
        total_volatility = omega / (1 - alpha - beta) if (alpha + beta) < 1 else np.sqrt(np.mean(h))
        
        # Forecast future volatility
        h_forecast = np.zeros(steps)
        h_forecast[0] = omega + alpha * data[-1]**2 + beta * h[-1]
        
        for h_step in range(1, steps):
            h_forecast[h_step] = omega + beta * h_forecast[h_step - 1]
        
        # Forecast volatility
        forecast_volatility = np.sqrt(h_forecast[-1])
        
        compute_time_ms = (time.perf_counter() - start_time) * 1000
        
        return GARCHResult(
            conditional_volatility=np.sqrt(h),
            forecast_volatility=forecast_volatility,
            omega=omega,
            alpha=alpha,
            beta=beta,
            total_volatility=total_volatility,
            compute_time_ms=compute_time_ms
        )
    
    def kalman_filter(
        self,
        observations: np.ndarray,
        state_dim: int = 1,
        process_noise: float = 0.01,
        observation_noise: float = 0.1
    ) -> KalmanFilterResult:
        """
        Kalman filter for dynamic state estimation.
        
        Parameters:
        -----------
        observations : np.ndarray
            Observation sequence
        state_dim : int
            Dimension of state vector
        process_noise : float
            Process noise covariance
        observation_noise : float
            Observation noise covariance
        
        Returns:
        --------
        KalmanFilterResult
            Filtered and predicted states
        """
        import time
        start_time = time.perf_counter()
        
        n = len(observations)
        
        # State transition matrix (identity)
        F = np.eye(state_dim)
        
        # Observation matrix
        H = np.eye(state_dim)
        
        # Initialize state and covariance
        x = np.zeros((n, state_dim))
        P = np.zeros((n, state_dim, state_dim))
        x_pred = np.zeros((n, state_dim))
        P_pred = np.zeros((n, state_dim, state_dim))
        
        # Initial state estimate
        x[0] = observations[0]
        P[0] = np.eye(state_dim) * observation_noise
        
        # Prediction
        x_pred[0] = F @ x[0]
        P_pred[0] = F @ P[0] @ F.T + process_noise * np.eye(state_dim)
        
        # Kalman gain
        S = H @ P_pred[0] @ H.T + observation_noise * np.eye(state_dim)
        K = P_pred[0] @ H.T @ np.linalg.inv(S)
        
        # Update
        x[0] = x_pred[0] + K @ (observations[0] - H @ x_pred[0])
        P[0] = (np.eye(state_dim) - K @ H) @ P_pred[0]
        
        for t in range(1, n):
            # Prediction
            x_pred[t] = F @ x[t-1]
            P_pred[t] = F @ P[t-1] @ F.T + process_noise * np.eye(state_dim)
            
            # Kalman gain
            S = H @ P_pred[t] @ H.T + observation_noise * np.eye(state_dim)
            K = P_pred[t] @ H.T @ np.linalg.inv(S)
            
            # Update
            x[t] = x_pred[t] + K @ (observations[t] - H @ x_pred[t])
            P[t] = (np.eye(state_dim) - K @ H) @ P_pred[t]
        
        # Log-likelihood
        innovations = observations - H @ x_pred
        S = H @ P_pred @ H.T + observation_noise * np.eye(state_dim)
        log_likelihood = -0.5 * np.sum(innovations**2 / np.diag(S) + np.log(np.diag(S)))
        
        compute_time_ms = (time.perf_counter() - start_time) * 1000
        
        return KalmanFilterResult(
            filtered_state=x,
            filtered_covariance=P,
            predicted_state=x_pred,
            predicted_covariance=P_pred,
            likelihood=log_likelihood,
            compute_time_ms=compute_time_ms
        )
    
    def calculate_half_life(
        self,
        data: np.ndarray,
        lookback: Optional[int] = None
    ) -> HalfLifeResult:
        """
        Calculate mean reversion half-life.
        
        Uses Ornstein-Uhlenbeck formula:
        half_life = -ln(2) / ln(phi)
        
        where phi is the speed of mean reversion.
        """
        import time
        start_time = time.perf_counter()
        
        if lookback is None:
            lookback = len(data)
        
        data = data[-lookback:]
        
        # Calculate speed of mean reversion
        delta = np.diff(data)
        lagged = data[:-1]
        
        # Simple OLS: delta = alpha + phi * lagged + epsilon
        phi = np.cov(delta, lagged)[0, 1] / np.var(lagged)
        
        # Half-life
        if phi >= 1 or phi <= -1:
            half_life = float('inf')
        else:
            half_life = -np.log(2) / np.log(phi)
        
        # Hurst exponent for context
        hurst = self.hurst_exponent(data)
        
        # Interpret mean reversion strength
        if half_life == float('inf'):
            strength = "non_mean_reverting"
        elif half_life < 10:
            strength = "strong_mean_reversion"
        elif half_life < 50:
            strength = "moderate_mean_reversion"
        elif half_life < 200:
            strength = "weak_mean_reversion"
        else:
            strength = "non_mean_reverting"
        
        compute_time_ms = (time.perf_counter() - start_time) * 1000
        
        return HalfLifeResult(
            half_life=max(0, half_life),
            hurst_exponent=hurst,
            mean_reversion_strength=strength,
            compute_time_ms=compute_time_ms
        )
    
    def estimate_hurst_exponent(
        self,
        data: np.ndarray,
        max_scale: int = 10
    ) -> HurstExponentResult:
        """
        Estimate Hurst exponent for long-term memory using R/S analysis.
        
        H < 0.5: Mean-reverting (anti-persistent)
        H = 0.5: Random walk (Brownian motion)
        H > 0.5: Trending (persistent)
        """
        import time
        start_time = time.perf_counter()
        
        n = len(data)
        
        # Calculate R/S for different scales
        scales = range(2, min(max_scale + 1, n // 4))
        rs_ratios = []
        
        for tau in scales:
            rs_tau = 0
            for i in range(0, n - tau, tau):
                segment = data[i:i+tau]
                mean = np.mean(segment)
                cumdev = np.cumsum(segment - mean)
                R = np.max(cumdev) - np.min(cumdev)
                S = np.std(segment, ddof=1)
                if S > 0:
                    rs_tau += R / S
            rs_ratios.append(rs_tau / (n // tau))
        
        # Log-log regression: log(R/S) = H * log(n) + c
        log_scales = np.log(list(scales))
        log_rs = np.log(rs_ratios)
        
        slope, intercept, r_value, p_value, std_err = stats.linregress(log_scales, log_rs)
        
        hurst = max(0, min(1, slope))
        
        # Interpret
        if hurst < 0.45:
            trend_type = "mean_reverting"
            interpretation = "H < 0.5: Anti-persistent, mean-reverting behavior"
        elif hurst < 0.55:
            trend_type = "random_walk"
            interpretation = "H ≈ 0.5: Random walk, no predictable pattern"
        else:
            trend_type = "trending"
            interpretation = "H > 0.5: Persistent, trending behavior"
        
        compute_time_ms = (time.perf_counter() - start_time) * 1000
        
        return HurstExponentResult(
            hurst_exponent=hurst,
            trend_type=trend_type,
            interpretation=interpretation,
            compute_time_ms=compute_time_ms
        )
    
    def hurst_exponent(
        self,
        data: np.ndarray,
        max_scale: int = 10
    ) -> float:
        """
        Simple Hurst exponent estimation.
        
        H < 0.5: Mean-reverting
        H = 0.5: Random walk
        H > 0.5: Trending
        """
        n = len(data)
        
        # Calculate RMS for different scales
        scales = range(2, min(max_scale + 1, n // 4))
        rms = []
        
        for tau in scales:
            rms_tau = 0
            for i in range(0, n - tau, tau):
                segment = data[i:i+tau]
                rms_tau += (segment[-1] - segment[0]) ** 2
            rms.append(np.sqrt(rms_tau / (n // tau)))
        
        # Log-log regression
        log_scales = np.log(list(scales))
        log_rms = np.log(rms)
        
        slope, _, _, _, _ = stats.linregress(log_scales, log_rms)
        
        return max(0, min(1, slope))


def get_time_series_models() -> TimeSeriesModels:
    """Get singleton instance of time series models."""
    return TimeSeriesModels()
