/**
 * LapIQ shared TypeScript type definitions.
 * Matches backend API response shapes.
 */

export interface LaptopVariantSummary {
  variant_id?: number
  laptop_brand?: string
  laptop_model?: string
  price_inr?: number
  min_discount_price_inr?: number
  max_mrp_price_inr?: number
  max_discount_percentage?: number
  cpu_model?: string
  gpu_model?: string
  ram_gb?: number
  storage_gb?: number
  storage_type?: string
  display_size_inches?: number
  total_score?: number
  confidence_score?: number

  // Aliases for camelCase
  variantId?: number
  laptopBrand?: string
  laptopModel?: string
  priceInr?: number
  minDiscountPriceInr?: number
  maxMrpPriceInr?: number
  maxDiscountPercentage?: number
  cpuModel?: string
  gpuModel?: string
  ramGb?: number
  storageGb?: number
  storageType?: string
  displaySizeInches?: number
  totalScore?: number
  confidenceScore?: number
}

export interface RecommendationResponse {
  request_id?: string
  is_partial?: boolean
  recommendations: LaptopVariantSummary[]
  requestId?: string
  isPartial?: boolean
}

export interface UserPreferencesPayload {
  budgetInr: number
  useCase: string
  targetSegment: 'Students' | 'Professionals' | 'Gamers' | 'Creators'
  minRamGb?: number
  requiresDedicatedGpu?: boolean
  prefersLightweight?: boolean
}
