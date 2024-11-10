import React from 'react'
import { Input } from '../ui/input'
import { Button } from '../ui/button'

export const CourseSearchSection = () => {
    return (
        <div className='flex items-center justify-center flex-col gap-4 min-h-[20vh]'>
            <div className='border-2 rounded-full flex items-center overflow-hidden'>
                <Input
                    placeholder='Enter your course name or category'
                    type='search'
                    className='border-0 ring-0 focus-visible:ring-0'
                />
                <Button
                    className='rounded-full'
                >
                    Search
                </Button>
            </div>
        </div>
    )
}
