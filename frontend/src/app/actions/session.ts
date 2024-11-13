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


export async function getSession() {
    const cookieStore = await cookies()
    const cookieValue = cookieStore.get(cookie.name)

    if (!cookieValue) {
        redirect('/signin')
    }

    return { success: true, data: cookieValue }
}

export async function destroySession() {
    try {
        (await cookies()).set({
            name: cookie.name,
            value: '',
            ...cookie.options,
            maxAge: 0
        })

        return { success: true }
    } catch (error) {
        console.error('Failed to destroy session:', error)
        return { success: false, error: 'Failed to destroy session' }
    }
}