import { clsx, type ClassValue } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

// Safe length helper to prevent undefined errors
export const safeLength = (arr: any[] | null | undefined) => arr?.length ?? 0;
