'use server'
import 'server-only';
import { cookies } from 'next/headers';
import { redirect } from 'next/navigation';

const cookie = {
    name: 'auth_token',
    options: {
        httpOnly: true,
        secure: true,
        sameSite: 'strict' as 'strict' | 'lax' | 'none',
        path: '/',
        maxAge: 60 * 60 * 24 * 7, // 7 days
    }
}

// create user session
export async function createSession(refresh: string, access: string) {
    try {
        // Explicitly mark as server action
        (await cookies()).set({
            name: cookie.name,
            value: JSON.stringify({
                refresh: refresh,
                access: access,
            }),
            ...cookie.options
        })

        const cookieStore = await cookies()
        const cookieValue = cookieStore.get(cookie.name)
        console.log('cookieValue', cookieValue)
        
        return { success: true }
    } catch (error) {
        console.error('Failed to create session:', error)
        return { success: false, error: 'Failed to create session' }
    }
}

interface SessionData {
    refresh: string;
    access: string;
}

export async function getSession(): Promise<{ success: boolean; data?: SessionData }> {
    try {
        const cookieStore = await cookies()
        const sessionCookie = cookieStore.get(cookie.name)
        
        if (!sessionCookie?.value) {
            console.log('No session found')
            redirect('/login')
        }

        try {
            const sessionData = JSON.parse(sessionCookie.value) as SessionData
            
            if (!sessionData.access || !sessionData.refresh) {
                throw new Error('Invalid session data')
            }

            return { 
                success: true, 
                data: sessionData 
            }
        } catch (parseError) {
            console.error('Invalid session format:', parseError)
            redirect('/login')
        }

    } catch (error) {
        console.error('Failed to get session:', error)
        redirect('/login')
    }
}