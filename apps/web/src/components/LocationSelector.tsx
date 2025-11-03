import { useState, useEffect } from 'react'
import { useGetLocationsQuery } from '@/features/admin/api/locationsApi'
import type { LocationType } from '@/features/admin/api/locationsApi'

interface LocationSelectorProps {
  value: {
    country_id?: string
    province_id?: string
    city_id?: string
    district_id?: string
    neighborhood_id?: string
    custom_country?: string
  }
  onChange: (value: any) => void
  showCustomCountry?: boolean
}

export default function LocationSelector({ value, onChange, showCustomCountry = true }: LocationSelectorProps) {
  const [selectedCountry, setSelectedCountry] = useState(value.country_id || '')
  const [selectedProvince, setSelectedProvince] = useState(value.province_id || '')
  const [selectedCity, setSelectedCity] = useState(value.city_id || '')
  const [selectedDistrict, setSelectedDistrict] = useState(value.district_id || '')
  const [selectedNeighborhood, setSelectedNeighborhood] = useState(value.neighborhood_id || '')
  const [useCustomCountry, setUseCustomCountry] = useState(!!value.custom_country)
  const [customCountry, setCustomCountry] = useState(value.custom_country || '')

  // Fetch locations dynamically
  const { data: countries = [] } = useGetLocationsQuery({ type: 'country' as LocationType })
  const { data: provinces = [] } = useGetLocationsQuery(
    { type: 'province' as LocationType, parent_id: selectedCountry },
    { skip: !selectedCountry || useCustomCountry }
  )
  const { data: cities = [] } = useGetLocationsQuery(
    { type: 'city' as LocationType, parent_id: selectedProvince },
    { skip: !selectedProvince || useCustomCountry }
  )
  const { data: districts = [] } = useGetLocationsQuery(
    { type: 'district' as LocationType, parent_id: selectedCity },
    { skip: !selectedCity || useCustomCountry }
  )
  const { data: neighborhoods = [] } = useGetLocationsQuery(
    { type: 'neighborhood' as LocationType, parent_id: selectedDistrict || selectedCity },
    { skip: (!selectedDistrict && !selectedCity) || useCustomCountry }
  )

  useEffect(() => {
    const newValue: any = {}
    
    if (useCustomCountry) {
      newValue.custom_country = customCountry
    } else {
      if (selectedCountry) newValue.country_id = selectedCountry
      if (selectedProvince) newValue.province_id = selectedProvince
      if (selectedCity) newValue.city_id = selectedCity
      if (selectedDistrict) newValue.district_id = selectedDistrict
      if (selectedNeighborhood) newValue.neighborhood_id = selectedNeighborhood
    }
    
    onChange(newValue)
  }, [selectedCountry, selectedProvince, selectedCity, selectedDistrict, selectedNeighborhood, useCustomCountry, customCountry])

  const handleCountryChange = (countryId: string) => {
    setSelectedCountry(countryId)
    setSelectedProvince('')
    setSelectedCity('')
    setSelectedDistrict('')
    setSelectedNeighborhood('')
  }

  const handleProvinceChange = (provinceId: string) => {
    setSelectedProvince(provinceId)
    setSelectedCity('')
    setSelectedDistrict('')
    setSelectedNeighborhood('')
  }

  const handleCityChange = (cityId: string) => {
    setSelectedCity(cityId)
    setSelectedDistrict('')
    setSelectedNeighborhood('')
  }

  const handleDistrictChange = (districtId: string) => {
    setSelectedDistrict(districtId)
    setSelectedNeighborhood('')
  }

  if (useCustomCountry) {
    return (
      <div className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Pays * <span className="text-xs text-orange-600">(Non disponible dans notre base)</span>
          </label>
          <input
            type="text"
            value={customCountry}
            onChange={(e) => setCustomCountry(e.target.value)}
            className="w-full px-3 py-2 border border-orange-300 rounded-lg focus:ring-2 focus:ring-orange-500 bg-orange-50"
            placeholder="Entrez le nom du pays"
            required
          />
          {showCustomCountry && (
            <button
              type="button"
              onClick={() => {
                setUseCustomCountry(false)
                setCustomCountry('')
              }}
              className="text-sm text-jlc-purple-600 hover:underline mt-1"
            >
              ← Choisir dans la liste
            </button>
          )}
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-4">
      {/* Country */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">Pays *</label>
        <select
          value={selectedCountry}
          onChange={(e) => handleCountryChange(e.target.value)}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-jlc-purple-500"
          required
        >
          <option value="">Sélectionnez un pays</option>
          {countries.map((country) => (
            <option key={country.id} value={country.id}>
              {country.name}
            </option>
          ))}
        </select>
        {showCustomCountry && (
          <button
            type="button"
            onClick={() => setUseCustomCountry(true)}
            className="text-sm text-gray-600 hover:text-jlc-purple-600 mt-1"
          >
            Mon pays n'est pas dans la liste →
          </button>
        )}
      </div>

      {/* Province */}
      {selectedCountry && provinces.length > 0 && (
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Province</label>
          <select
            value={selectedProvince}
            onChange={(e) => handleProvinceChange(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-jlc-purple-500"
          >
            <option value="">Sélectionnez une province</option>
            {provinces.map((province) => (
              <option key={province.id} value={province.id}>
                {province.name}
              </option>
            ))}
          </select>
        </div>
      )}

      {/* City */}
      {(selectedProvince || selectedCountry) && cities.length > 0 && (
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Ville (Chef-lieu) *</label>
          <select
            value={selectedCity}
            onChange={(e) => handleCityChange(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-jlc-purple-500"
            required
          >
            <option value="">Sélectionnez une ville</option>
            {cities.map((city) => (
              <option key={city.id} value={city.id}>
                {city.name}
              </option>
            ))}
          </select>
        </div>
      )}

      {/* District */}
      {selectedCity && districts.length > 0 && (
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Arrondissement</label>
          <select
            value={selectedDistrict}
            onChange={(e) => handleDistrictChange(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-jlc-purple-500"
          >
            <option value="">Sélectionnez un arrondissement</option>
            {districts.map((district) => (
              <option key={district.id} value={district.id}>
                {district.name}
              </option>
            ))}
          </select>
        </div>
      )}

      {/* Neighborhood */}
      {(selectedDistrict || selectedCity) && neighborhoods.length > 0 && (
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Quartier *</label>
          <select
            value={selectedNeighborhood}
            onChange={(e) => setSelectedNeighborhood(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-jlc-purple-500"
            required
          >
            <option value="">Sélectionnez un quartier</option>
            {neighborhoods.map((neighborhood) => (
              <option key={neighborhood.id} value={neighborhood.id}>
                {neighborhood.name}
              </option>
            ))}
          </select>
        </div>
      )}
    </div>
  )
}
