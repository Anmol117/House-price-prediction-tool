import { FormData, ValidationErrors } from '../types';

export function validateAreaSqft(value: string): string | null {
  if (!value || value.trim() === '') {
    return 'Area in square feet is required';
  }
  const num = Number(value);
  if (isNaN(num)) {
    return 'Area must be a valid number';
  }
  if (num < 200 || num > 20000) {
    return 'Area must be between 200 and 20,000 sq ft';
  }
  return null;
}

export function validateBHK(value: string): string | null {
  if (!value || value.trim() === '') {
    return 'Number of BHK / bedrooms is required';
  }
  const num = Number(value);
  if (isNaN(num) || !Number.isInteger(num)) {
    return 'BHK must be a whole number';
  }
  if (num < 1 || num > 10) {
    return 'BHK must be between 1 and 10';
  }
  return null;
}

export function validateBathrooms(value: string): string | null {
  if (!value || value.trim() === '') {
    return 'Number of bathrooms is required';
  }
  const num = Number(value);
  if (isNaN(num)) {
    return 'Bathrooms must be a valid number';
  }
  if (num < 1 || num > 10) {
    return 'Bathrooms must be between 1 and 10';
  }
  // Precision check: multiple of 0.5
  if (Math.round(num * 2) !== num * 2) {
    return 'Bathrooms must be in increments of 0.5 (e.g. 1.0, 1.5, 2.0)';
  }
  return null;
}

export function validateCity(value: string): string | null {
  if (!value || value.trim() === '') {
    return 'Please select a city';
  }
  return null;
}

export function validateLocality(value: string): string | null {
  if (!value || value.trim() === '') {
    return 'Please select or enter a locality';
  }
  if (value.length > 100) {
    return 'Locality cannot exceed 100 characters';
  }
  return null;
}

export function validatePropertyType(value: string): string | null {
  if (!value || value.trim() === '') {
    return 'Please select a property type';
  }
  return null;
}

export function validateFurnishing(value: string): string | null {
  if (!value || value.trim() === '') {
    return 'Please select furnishing status';
  }
  return null;
}

export function validateField(field: keyof FormData, value: string): string | null {
  switch (field) {
    case 'area_sqft':
      return validateAreaSqft(value);
    case 'bhk':
      return validateBHK(value);
    case 'bathrooms':
      return validateBathrooms(value);
    case 'city':
      return validateCity(value);
    case 'locality':
      return validateLocality(value);
    case 'property_type':
      return validatePropertyType(value);
    case 'furnishing':
      return validateFurnishing(value);
    default:
      return null;
  }
}

export function validateForm(formData: FormData): { isValid: boolean; errors: ValidationErrors } {
  const errors: ValidationErrors = {};

  const areaErr = validateAreaSqft(formData.area_sqft);
  if (areaErr) errors.area_sqft = areaErr;

  const bhkErr = validateBHK(formData.bhk);
  if (bhkErr) errors.bhk = bhkErr;

  const bathErr = validateBathrooms(formData.bathrooms);
  if (bathErr) errors.bathrooms = bathErr;

  const cityErr = validateCity(formData.city);
  if (cityErr) errors.city = cityErr;

  const locErr = validateLocality(formData.locality);
  if (locErr) errors.locality = locErr;

  const typeErr = validatePropertyType(formData.property_type);
  if (typeErr) errors.property_type = typeErr;

  const furnErr = validateFurnishing(formData.furnishing);
  if (furnErr) errors.furnishing = furnErr;

  const isValid = Object.keys(errors).length === 0;
  return { isValid, errors };
}
