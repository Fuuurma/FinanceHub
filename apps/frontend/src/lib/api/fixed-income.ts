/**
 * Fixed Income Analytics API Client
 * Bond pricing, yield curves, and fixed income analytics integration
 */

import { apiClient } from './client'
import type {
  BondPricingRequest,
  BondPricingResponse,
  ZeroCouponBondRequest,
  ZeroCouponBondResponse,
  YieldCurveBootstrapRequest,
  YieldCurveResponse,
  BondCashFlowRequest,
  BondCashFlowResponse,
  DurationConvexityRequest,
  DurationConvexityResponse,
  OASRequest,
  OASResponse,
  ZSpreadRequest,
  ZSpreadResponse,
  CouponFrequency,
  PriceType,
} from '@/lib/types/fixed-income'

export const fixedIncomeApi = {
  /**
   * Price a fixed-rate bond with full analytics
   * Returns clean price, duration, convexity, OAS, and Z-spread
   */
  priceBond: (data: BondPricingRequest) =>
    apiClient.post<BondPricingResponse>('/fixed-income/price', {
      face_value: data.face_value,
      coupon_rate: data.coupon_rate,
      yield_rate: data.yield_rate,
      time_to_maturity: data.time_to_maturity,
      frequency: data.frequency || 2,
      price_type: data.price_type || 'clean',
    }),

  /**
   * Price a zero-coupon bond
   * Zero-coupon bonds are priced as: Price = Face Value / (1 + y * T)
   */
  priceZeroCoupon: (data: ZeroCouponBondRequest) =>
    apiClient.post<ZeroCouponBondResponse>('/fixed-income/zero-coupon', data),

  /**
   * Bootstrap yield curve from bond prices
   * Uses bond prices to derive zero rates and spot curve
   */
  bootstrapYieldCurve: (data: YieldCurveBootstrapRequest) =>
    apiClient.post<YieldCurveResponse>('/fixed-income/yield-curve', {
      bond_prices: data.bond_prices,
      maturities: data.maturities,
      frequencies: data.frequencies,
    }),

  /**
   * Generate bond cash flows schedule
   * Returns all coupon payments and principal repayment
   */
  getCashFlows: (data: BondCashFlowRequest) =>
    apiClient.post<BondCashFlowResponse>('/fixed-income/cash-flows', {
      face_value: data.face_value,
      coupon_rate: data.coupon_rate,
      time_to_maturity: data.time_to_maturity,
      frequency: data.frequency || 2,
    }),

  /**
   * Calculate bond duration and convexity
   * Returns Macaulay duration, modified duration, and convexity
   * Also shows price change for 1bp yield movement
   */
  calculateDurationConvexity: (data: DurationConvexityRequest) =>
    apiClient.post<DurationConvexityResponse>('/fixed-income/duration-convexity', {
      price: data.price,
      yield_rate: data.yield_rate,
      time_to_maturity: data.time_to_maturity,
      frequency: data.frequency || 2,
    }),

  /**
   * Calculate Option-Adjusted Spread (OAS)
   */
  calculateOAS: (params: OASRequest) =>
    apiClient.get<OASResponse>('/fixed-income/oas', {
      params: {
        price: params.price,
        yield_rate: params.yield_rate,
        time_to_maturity: params.time_to_maturity,
        frequency: params.frequency || 2,
      },
    }),

  /**
   * Calculate Z-Spread
   */
  calculateZSpread: (data: ZSpreadRequest) =>
    apiClient.post<ZSpreadResponse>('/fixed-income/z-spread', {
      price: data.price,
      yield_rate: data.yield_rate,
      time_to_maturity: data.time_to_maturity,
      treasury_yields: data.treasury_yields,
      frequency: data.frequency || 2,
    }),
}
