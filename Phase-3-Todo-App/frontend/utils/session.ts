// Utility functions for session management

// Check if user is authenticated by checking for a valid token
export function isAuthenticated(): boolean {
  const authData = localStorage.getItem('auth');
  if (!authData) {
    return false;
  }

  try {
    const parsedAuth = JSON.parse(authData);
    const token = parsedAuth.token;
    if (!token) {
      return false;
    }

    // In a real implementation, we would decode and validate the JWT
    // For now, we'll just check if it exists
    return true;
  } catch (e) {
    console.error('Error parsing auth data:', e);
    return false;
  }
}

// Get the current user token
export function getUserToken(): string | null {
  const authData = localStorage.getItem('auth');
  if (!authData) {
    return null;
  }

  try {
    const parsedAuth = JSON.parse(authData);
    return parsedAuth.token || null;
  } catch (e) {
    console.error('Error parsing auth data:', e);
    return null;
  }
}

// Store user token
export function setUserToken(token: string): void {
  localStorage.setItem('auth', JSON.stringify({ token }));
}

// Remove user token
export function removeUserToken(): void {
  localStorage.removeItem('auth');
}

// Decode JWT token (basic implementation)
export function decodeToken(token: string): any {
  try {
    const parts = token.split('.');
    if (parts.length !== 3) {
      throw new Error('Invalid token format');
    }

    const payload = parts[1];
    // Add padding if needed
    const decodedPayload = atob(payload.replace(/-/g, '+').replace(/_/g, '/'));
    return JSON.parse(decodedPayload);
  } catch (error) {
    console.error('Error decoding token:', error);
    return null;
  }
}

// Check if token is expired
export function isTokenExpired(token?: string): boolean {
  try {
    // If the token parameter is provided, use it directly
    // Otherwise, get the token from localStorage
    const tokenToCheck = token || getUserToken();
    if (!tokenToCheck) {
      return true;
    }

    const decoded = decodeToken(tokenToCheck);
    if (!decoded || !decoded.exp) {
      return true;
    }

    const currentTime = Math.floor(Date.now() / 1000);
    return decoded.exp < currentTime;
  } catch (error) {
    console.error('Error checking token expiration:', error);
    return true;
  }
}