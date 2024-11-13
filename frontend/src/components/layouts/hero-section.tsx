import React from 'react'
import { Badge } from '../ui/badge'
import { Button } from '../ui/button'
import { PlayIcon } from '@radix-ui/react-icons'
import { Card } from '../ui/card'
import Image from 'next/image'

const heroSectionData = [
    {
        title: 'ongoing students',
        value: '100k +'
    },
    {
        title: 'ongoing courses',
        value: '100k +'
    },
    {
        title: 'successful stories',
        value: '1k +'
    }
]

const HeroSection = () => {
    return (
        <section className='grid grid-cols-12 gap-4 w-full min-h-[70vh]'>
            <div className='col-start-3 col-end-7 flex flex-col items-start justify-center gap-4'>
                <Badge>
                    best training platform
                </Badge>
                <h1 className='text-4xl font-bold'>
                    get the best training, <span className='text-orange-400'>any</span> time, anywhere
                </h1>
                <p>
                    TMS is the best training platform for people. We provide the best training for people, and we are here to help you get the best training.
                </p>
                <div className='flex gap-4'>
                    <Button variant={'outline'}>
                        start learning
                    </Button>
                    <Button variant={'secondary'}>
                        <PlayIcon />
                        how it works
                    </Button>
                </div>
            </div>

            <div className='col-start-8 col-end-10 flex justify-end items-center size-full'>
                <Image
                    src='/images/Student.png'
                    alt='hero image'
                    width={700}
                    height={400}
                />
            </div>

            <div className='col-start-3 col-end-11 flex justify-center sm:flex-col md:flex-row gap-2'>
                {heroSectionData.map((data) => (
                    <Card
                        key={data.title}
                        className='grid p-4 size-full'
                    >
                        <h1 className='text-3xl font-bold'>
                            {data.value}
                        </h1>
                        <p className='text-xl text-foreground'>
                            {data.title}
                        </p>
                    </Card>
                ))}
            </div>  
        </section>
    )
}

export default HeroSection
