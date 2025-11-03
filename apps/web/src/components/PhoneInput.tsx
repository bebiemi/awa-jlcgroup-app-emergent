import { useState, useEffect } from 'react'
import { ChevronDownIcon } from '@heroicons/react/24/outline'

interface Country {
  id: string
  name: string
  phone_code: string
}

interface PhoneInputProps {
  value: string
  onChange: (value: string) => void
  defaultCountryCode?: string
  className?: string
  placeholder?: string
  error?: string
  required?: boolean
}

export default function PhoneInput({
  value,
  onChange,
  defaultCountryCode = '+241',
  className = '',
  placeholder = 'Numéro de téléphone',
  error,
  required = false,
}: PhoneInputProps) {
  const [selectedCode, setSelectedCode] = useState(defaultCountryCode)
  const [phoneNumber, setPhoneNumber] = useState('')
  const [countries, setCountries] = useState<Country[]>([])
  const [showDropdown, setShowDropdown] = useState(false)

  // Common countries with phone codes (can be loaded from API later)
  const commonCountries = [
    { id: 'ga', name: 'Gabon', phone_code: '+241' },
    { id: 'fr', name: 'France', phone_code: '+33' },
    { id: 'us', name: 'États-Unis', phone_code: '+1' },
    { id: 'uk', name: 'Royaume-Uni', phone_code: '+44' },
    { id: 'cm', name: 'Cameroun', phone_code: '+237' },
    { id: 'cg', name: 'Congo-Brazzaville', phone_code: '+242' },
    { id: 'cd', name: 'RD Congo', phone_code: '+243' },
    { id: 'ci', name: 'Côte d\'Ivoire', phone_code: '+225' },
    { id: 'sn', name: 'Sénégal', phone_code: '+221' },
    { id: 'ma', name: 'Maroc', phone_code: '+212' },
  ]

  useEffect(() => {
    // TODO: Load from API /auth-api/locations?type=country
    setCountries(commonCountries)
  }, [])

  useEffect(() => {
    // Parse existing value
    if (value && !phoneNumber) {
      const country = countries.find(c => value.startsWith(c.phone_code))
      if (country) {
        setSelectedCode(country.phone_code)
        setPhoneNumber(value.substring(country.phone_code.length))
      } else {
        setPhoneNumber(value)
      }
    }
  }, [value, countries])

  const handlePhoneChange = (phone: string) => {
    // Only allow numbers and spaces
    const cleaned = phone.replace(/[^\d\s]/g, '')
    setPhoneNumber(cleaned)
    onChange(`${selectedCode}${cleaned.replace(/\s/g, '')}`)
  }

  const handleCodeChange = (code: string) => {
    setSelectedCode(code)
    setShowDropdown(false)
    onChange(`${code}${phoneNumber.replace(/\s/g, '')}`)
  }

  return (
    <div className={`relative ${className}`}>
      <div className="flex">
        {/* Country Code Selector */}
        <div className="relative">
          <button
            type="button"
            onClick={() => setShowDropdown(!showDropdown)}
            className={`px-3 py-2 border rounded-l-lg bg-gray-50 hover:bg-gray-100 transition flex items-center space-x-1 ${
              error ? 'border-red-500' : 'border-gray-300'
            }`}
          >
            <span className="font-medium text-gray-700">{selectedCode}</span>
            <ChevronDownIcon className="h-4 w-4 text-gray-500" />
          </button>

          {/* Dropdown */}
          {showDropdown && (
            <div className="absolute z-10 mt-1 w-64 bg-white border border-gray-300 rounded-lg shadow-lg max-h-60 overflow-y-auto">
              {countries.map((country) => (
                <button
                  key={country.id}
                  type="button"
                  onClick={() => handleCodeChange(country.phone_code)}
                  className={`w-full px-4 py-2 text-left hover:bg-gray-100 transition flex justify-between items-center ${
                    selectedCode === country.phone_code ? 'bg-jlc-purple-50' : ''
                  }`}
                >
                  <span className="text-sm text-gray-900">{country.name}</span>
                  <span className="text-sm font-medium text-gray-600">{country.phone_code}</span>
                </button>
              ))}
            </div>
          )}
        </div>

        {/* Phone Number Input */}
        <input
          type="tel"
          value={phoneNumber}
          onChange={(e) => handlePhoneChange(e.target.value)}
          placeholder={placeholder}
          required={required}
          className={`flex-1 px-3 py-2 border-t border-b border-r rounded-r-lg focus:ring-2 focus:ring-jlc-purple-500 focus:border-transparent transition ${
            error ? 'border-red-500' : 'border-gray-300'
          }`}
        />
      </div>

      {error && (
        <p className="text-red-500 text-sm mt-1">{error}</p>
      )}
    </div>
  )
}
