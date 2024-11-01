import React from 'react'

interface Props {
    title: string
    paragraph?: string
    children: React.ReactNode
}

export const TitleSectionLayouts = ({ title, paragraph, children }: Props) => {
    return (
        <section className="flex flex-col items-center justify-center gap-4">
            <div className="flex flex-col items-center justify-center gap-2">
                <h1 className="text-3xl font-bold">{title}</h1>
                <p className="text-lg">{paragraph}</p>
            </div>
            <div className="size-max">
                {children}
            </div>
        </section>
    )
}
