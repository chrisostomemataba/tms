import { cn } from '@/lib/utils'
import Image from 'next/image'
import Link from 'next/link'
import React from 'react'

interface Props {
    width: number
    height: number
}

export const Logo = ({ width, height }: Props) => {
    return (
        <Link
            href={'/'}
            className={cn('flex items-center')}
        >
            <Image
                src="/logo.svg"
                alt="logo"
                width={width}
                height={height}
            />
        </Link>
    )
}
