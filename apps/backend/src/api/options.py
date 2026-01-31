from ninja import Router
from pydantic import BaseModel
from typing import List, Optional
from datetime import date
from investments.lib.options import OptionsPricing

router = Router(tags=["Options"])


class OptionsRequest(BaseModel):
    S: float
    K: float
    T: float
    r: float
    sigma: float
    option_type: str = "call"


class OptionsChainRequest(BaseModel):
    S: float
    T: float
    r: float
    sigma: float
    strikes: List[float]
    option_type: str = "call"


class ImpliedVolatilityRequest(BaseModel):
    S: float
    K: float
    T: float
    r: float
    price: float
    option_type: str = "call"


class StraddleRequest(BaseModel):
    S: float
    K: float
    T: float
    r: float
    sigma: float
    call_strike: float
    put_strike: float
    call_premium: float = 0
    put_premium: float = 0


class IronCondorRequest(BaseModel):
    S: float
    T: float
    r: float
    sigma: float
    put_short_strike: float
    put_long_strike: float
    call_short_strike: float
    call_long_strike: float
    put_short_premium: float
    put_long_premium: float
    call_short_premium: float
    call_long_premium: float


@router.post("/options/calculate")
def calculate_option(request, data: OptionsRequest):
    result = OptionsPricing.black_scholes(
        data.S, data.K, data.T, data.r, data.sigma, data.option_type
    )
    return {
        "price": result.price,
        "delta": result.delta,
        "gamma": result.gamma,
        "theta": result.theta,
        "vega": result.vega,
        "rho": result.rho,
    }


@router.post("/options/chain")
def calculate_chain(request, data: OptionsChainRequest):
    chain = OptionsPricing.calculate_option_chain(
        data.S, data.T, data.r, data.sigma, data.strikes, data.option_type
    )
    return {"chain": chain}


@router.post("/options/implied-volatility")
def calculate_iv(request, data: ImpliedVolatilityRequest):
    iv = OptionsPricing.implied_volatility(
        data.price, data.S, data.K, data.T, data.r, data.option_type
    )
    return {"implied_volatility": iv}


@router.post("/options/greeks")
def calculate_greeks(request, data: OptionsRequest):
    greeks = OptionsPricing.calculate_greeks(
        data.S, data.K, data.T, data.r, data.sigma, data.option_type
    )
    return {
        "delta": greeks.delta,
        "gamma": greeks.gamma,
        "theta": greeks.theta,
        "vega": greeks.vega,
        "rho": greeks.rho,
        "vanna": greeks.vanna,
        "charm": greeks.charm,
        "speed": greeks.speed,
        "zomma": greeks.zomma,
        "color": greeks.color,
    }


@router.post("/options/strategies/straddle")
def calculate_straddle(request, data: StraddleRequest):
    underlying_prices = [data.S * (1 + i * 0.05) for i in range(-20, 21)]
    payoff = OptionsPricing.calculate_straddle_payoff(
        data.call_strike,
        data.put_strike,
        underlying_prices,
        data.call_premium,
        data.put_premium,
    )
    return {"payoff": payoff}


@router.post("/options/strategies/iron-condor")
def calculate_iron_condor(request, data: IronCondorRequest):
    underlying_prices = [data.S * (1 + i * 0.02) for i in range(-30, 31)]
    payoff = OptionsPricing.calculate_iron_condor_payoff(
        data.put_short_strike,
        data.put_long_strike,
        data.call_short_strike,
        data.call_long_strike,
        data.put_short_premium,
        data.put_long_premium,
        data.call_short_premium,
        data.call_long_premium,
        underlying_prices,
    )
    return {"payoff": payoff}
