import React from 'react'
import { Card, CardContent } from '../ui/card'
import Image from 'next/image'
import { Button } from '../ui/button'
import { Badge } from '../ui/badge'

interface Props {
    price: number
    image: string
    title: string
    Category: string
    level: string
    Duration: string
}

export const CourseCard = (props: Props) => {
    return (
        <Card className='overflow-hidden z-10'>
            <div className='aspect-square relative overflow-hidden'>
                <Image
                    src={props.image}
                    alt={props.title}
                    fill
                    className='object-cover hover:scale-110 transition-transform'
                />
            </div>
            <CardContent>
                <h1 className='text-xl font-bold'>
                    {props.title}
                </h1>
                <div className='flex items-center justify-between gap-2'>
                    <Badge variant={'outline'}>
                        {props.Category}
                    </Badge>
                    <h1>
                        {props.level}
                    </h1>
                </div>
                
                <div className='flex items-center justify-between gap-2'>
                    <h1>
                        ${props.price}
                    </h1>
                    <Button>
                        Book Now
                    </Button>
                </div>
            </CardContent>
        </Card>
    )
}
