import { FormData, ValidationErrors } from '../types';

export function validateSquareFootage(value: string): string | null {
  if (!value || value.trim() === '') {
    return 'Square footage is required';
  }
  const num = Number(value);
  if (isNaN(num)) {
    return 'Square footage must be a valid number';
  }
  if (num < 1 || num > 100000) {
    return 'Square footage must be between 1 and 100,000 sq ft';
  }
  return null;
}

export function validateBedrooms(value: string): string | null {
  if (!value || value.trim() === '') {
    return 'Number of bedrooms is required';
  }
  const num = Number(value);
  if (isNaN(num) || !Number.isInteger(num)) {
    return 'Bedrooms must be a whole number';
  }
  if (num < 0 || num > 20) {
    return 'Bedrooms must be between 0 and 20';
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
  if (num < 0 || num > 20) {
    return 'Bathrooms must be between 0 and 20';
  }
  // Precision check: multiple of 0.5
  if (Math.round(num * 2) !== num * 2) {
    return 'Bathrooms must be in increments of 0.5 (e.g. 1.5, 2.0)';
  }
  return null;
}

export function validateLocation(value: string): string | null {
  if (!value || value.trim() === '') {
    return 'Location is required';
  }
  if (value.length > 200) {
    return 'Location cannot exceed 200 characters';
  }
  const pattern = /^[a-zA-Z0-9 ,.\-']+$/;
  if (!pattern.test(value)) {
    return 'Location can only contain letters, numbers, spaces, commas, periods, hyphens, and apostrophes';
  }
  return null;
}

export function validateYearBuilt(value: string): string | null {
  if (!value || value.trim() === '') {
    return 'Year built is required';
  }
  const num = Number(value);
  const currentYear = new Date().getFullYear();
  const maxYear = currentYear + 1;

  if (isNaN(num) || !Number.isInteger(num)) {
    return 'Year built must be a whole year';
  }
  if (num < 1800 || num > maxYear) {
    return `Year built must be between 1800 and ${maxYear}`;
  }
  return null;
}

export function validateField(field: keyof FormData, value: string): string | null {
  switch (field) {
    case 'square_footage':
      return validateSquareFootage(value);
    case 'bedrooms':
      return validateBedrooms(value);
    case 'bathrooms':
      return validateBathrooms(value);
    case 'location':
      return validateLocation(value);
    case 'year_built':
      return validateYearBuilt(value);
    default:
      return null;
  }
}

export function validateForm(formData: FormData): { isValid: boolean; errors: ValidationErrors } {
  const errors: ValidationErrors = {};

  const sqftErr = validateSquareFootage(formData.square_footage);
  if (sqftErr) errors.square_footage = sqftErr;

  const bedErr = validateBedrooms(formData.bedrooms);
  if (bedErr) errors.bedrooms = bedErr;

  const bathErr = validateBathrooms(formData.bathrooms);
  if (bathErr) errors.bathrooms = bathErr;

  const locErr = validateLocation(formData.location);
  if (locErr) errors.location = locErr;

  const yearErr = validateYearBuilt(formData.year_built);
  if (yearErr) errors.year_built = yearErr;

  const isValid = Object.keys(errors).length === 0;
  return { isValid, errors };
}
