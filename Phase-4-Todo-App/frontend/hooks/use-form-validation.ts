import { useState } from 'react';

interface ValidationRule {
  rule: (value: string) => boolean;
  message: string;
}

interface UseFormValidationReturn {
  errors: Record<string, string>;
  validateField: (fieldName: string, value: string, rules?: ValidationRule[]) => void;
  validateForm: (formData: Record<string, string>, fieldRules: Record<string, ValidationRule[]>) => boolean;
  resetErrors: () => void;
}

export function useFormValidation(): UseFormValidationReturn {
  const [errors, setErrors] = useState<Record<string, string>>({});

  const validateField = (fieldName: string, value: string, rules?: ValidationRule[]) => {
    if (!rules) return;

    for (const rule of rules) {
      if (!rule.rule(value)) {
        setErrors(prev => ({ ...prev, [fieldName]: rule.message }));
        return;
      }
    }

    // If all rules pass, remove the error for this field
    setErrors(prev => {
      const newErrors = { ...prev };
      delete newErrors[fieldName];
      return newErrors;
    });
  };

  const validateForm = (formData: Record<string, string>, fieldRules: Record<string, ValidationRule[]>) => {
    const newErrors: Record<string, string> = {};

    for (const fieldName in fieldRules) {
      const value = formData[fieldName] || '';
      const rules = fieldRules[fieldName];

      for (const rule of rules) {
        if (!rule.rule(value)) {
          newErrors[fieldName] = rule.message;
          break; // Stop at first failing rule
        }
      }
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const resetErrors = () => {
    setErrors({});
  };

  return {
    errors,
    validateField,
    validateForm,
    resetErrors,
  };
}