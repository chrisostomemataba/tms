import SignUpFormComponent from '@/components/forms/signup'
import Image from 'next/image'
import React from 'react'

export default function SignUpPage() {
    return (
        <main className='grid grid-cols-2 place-content-center size-full max-h-screen'>
            <SignUpFormComponent />
            <div className='h-full relative flex items-center justify-center'>
                <Image
                    src={'/images/student.jpg'}
                    alt='img'
                    fill
                    className='size-full object-cover'
                />
            </div>
        </main>
    )
}
