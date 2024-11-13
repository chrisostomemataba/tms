import SignInFormComponent from '@/components/forms/signin'
import Image from 'next/image'

export default function SignInPage() {
    return (
        <main className='grid grid-cols-2 place-content-center size-full max-h-screen'>
            <SignInFormComponent />
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
