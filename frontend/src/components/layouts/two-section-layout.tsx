import React from 'react'

interface Props {
    children: React.ReactNode
}

export const TwoSectionLayout = ({ children }: Props) => {
    return (
        <section className='flex items-center justify-between gap-4 py-16 px-4 min-h-screen'>
            {children}
        </section>
    )
}
