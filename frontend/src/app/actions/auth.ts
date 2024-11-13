'use server'

import { createSession } from "@/lib/session";

interface ValidationErrors {
    [key: string]: string[];
}

interface AuthResponse {
    success: boolean;
    errors?: ValidationErrors | string;
    data?: { access?: string } | Record<string, unknown>;
}

export async function signUpAction(formValues: FormData): Promise<AuthResponse> {
    const values = Object.fromEntries(formValues.entries());
    
    try {
        const response = await fetch('http://127.0.0.1:8000/api/auth/register/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(values),
        });

        const data = await response.json();

        if (!response.ok) {
            console.error("Error response from server:", data);
            
            // Handle field-specific validation errors
            if (typeof data === 'object' && Object.keys(data).length > 0) {
                return {
                    success: false,
                    errors: data as ValidationErrors
                };
            }
            
            // Handle generic errors
            return {
                success: false,
                errors: 'Registration failed. Please try again.'
            };
        }

        return {
            success: true,
            data
        };

    } catch (error) {
        console.error('Registration error:', error);
        return {
            success: false,
            errors: 'An unexpected error occurred. Please try again.'
        };
    }
}

export async function signInAction(formValues: FormData): Promise<AuthResponse> { 
    const values = Object.fromEntries(formValues.entries());
    
    try {
        const response = await fetch('http://127.0.0.1:8000/api/auth/token/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(values),
        });

        const data = await response.json();

        if (!response.ok) {
            console.error("Error response from server:", data);
            
            // Handle field-specific validation errors
            if (typeof data === 'object' && Object.keys(data).length > 0) {
                return {
                    success: false,
                    errors: data as ValidationErrors
                };
            }
            
            // Handle generic errors
            return {
                success: false,
                errors: 'Authentication failed. Please try again.'
            };
        }

        createSession(data.refresh, data.access);

        return {
            success: true,
            data
        };
    } catch (error) {
        console.error('Authentication error:', error);
        return {
            success: false,
            errors: 'An unexpected error occurred. Please try again.'
        };
    }
}


export async function getAuthToken(email: string, password: string): Promise<AuthResponse> {
    try {
        const response = await fetch('http://127.0.0.1:8000/api/auth/token/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ email, password }),
        });

        const data = await response.json();

        if (!response.ok) {
            return {
                success: false,
                errors: data.detail || 'Authentication failed'
            };
        }

        return {
            success: true,
            data: data.access
        };

    } catch (error) {
        console.error('Authentication error:', error);
        return {
            success: false,
            errors: 'An unexpected error occurred'
        };
    }
}