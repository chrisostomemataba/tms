import { Badge } from '@/components/ui/badge'
import { Clock, Star } from 'lucide-react'
import Image from 'next/image'
import React from 'react'

const SingleCoursePage = () => {
    return (
        <main className='grid grid-cols-12'>
            <div className='col-start-2 col-end-12 flex item-center justify-between'>
                <div className='flex items-center justify-between gap-4'>
                        <h1 className="text-4xl font-bold">course title</h1>
                        <Badge variant={'outline'}>
                            course category
                        </Badge>
                </div>
                <div className='flex items-center gap-4'>
                    <span className='flex items-center gap-2'>
                        <Clock />
                        course period
                    </span>
                    <span className='flex items-center gap-2'>
                        <Star />
                        course late
                    </span>
                </div>
            </div>

            <section className='col-start-3 col-end-7 flex item-center justify-between'>
                <div className='w-full min-h-[50vh] relative rounded overflow-hidden'>
                    <Image
                        src='/images/board.jpg'
                        alt='image'
                        fill
                        className='size-full object-cover'
                    />
                </div>
            </section>

            <section></section>
        </main>
    )
}

export default SingleCoursePage