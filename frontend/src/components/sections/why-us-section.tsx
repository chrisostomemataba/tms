import React from 'react'
import { TwoSectionLayout } from '../layouts/two-section-layout'
import { Smile } from 'lucide-react'
import { Card } from '../ui/card'
import { Button } from '../ui/button'

const whyUs = [
    {
        title: 'Best Courses',
        description: 'get the best course for your learning needs',
        icon: <Smile />
    },
    {
        title: 'Best',
        description: 'get the best course for your learning needs',
        icon: <Smile />
    },
    {
        title: 'Best Course',
        description: 'get the best course for your learning needs',
        icon: <Smile />
    },
    {
        title: 'Best technology',
        description: 'get the best course for your learning needs',
        icon: <Smile />
    }
]

export const WhyUsSection = () => {
    return (
        <div className='grid grid-cols-12 gap-4'>
            <div className='col-start-3 col-end-10'>
                <TwoSectionLayout>
                    <div className='grid grid-cols-2 gap-4'>
                        {whyUs.map((why) => (
                            <Card
                                key={why.title}
                                className='p-4 hover:shadow-xl transition-shadow'
                            >
                                {why.icon}
                                <div>
                                    <h1 className='text-xl font-bold'>
                                        {why.title}
                                    </h1>
                                    <p className='text-sm'>
                                        {why.description}
                                    </p>
                                </div>
                            </Card>
                        ))}
                    </div>
                    <div className='flex flex-col gap-4'>
                        <h1 className='text-4xl font-bold'>
                            find out why work with us
                        </h1>
                        <p className='text-lg'>
                            our instructors are experts in their field and have years of experience in teaching and learning.
                        </p>
                        <div>
                            <ul>
                                <li>customer support</li>
                                <li>24/7 customer support</li>
                                <li>24/7 customer support</li>
                                <li>customer support</li>
                            </ul>
                            <Button>
                                Learn more
                            </Button>
                        </div>
                    </div>
                </TwoSectionLayout>
            </div>
        </div>
    )
}
