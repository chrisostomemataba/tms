import React from 'react'
import { Card } from '../ui/card'

const categories = [
    {
        name: 'Business',
        icon: '💼'
    },
    {
        name: 'Design',
        icon: '🎨'
    },
    {
        name: 'Development',
        icon: '💻'
    },
    {
        name: 'Finance',
        icon: '💰'
    },
    {
        name: 'Health',
        icon: '🏥'
    },
    {
        name: 'IT',
        icon: '💻'
    },
    {
        name: 'Lifestyle',
        icon: '💼'
    },
    {
        name: 'Marketing',
        icon: '📈'
    },
    {
        name: 'Music',
        icon: '🎵'
    },
    {
        name: 'Photography',
        icon: '📷'
    },
    {
        name: 'Productivity',
        icon: '💻'
    },
    {
        name: 'Science',
        icon: '🔬'
    },
    {
        name: 'Sports',
        icon: '🏈'
    },
]

export const CategorySection = () => {
    return (
        <section>
            <h1 className='text-3xl font-bold'>All Categories</h1>
            <div className='grid grid-cols-2 md:grid-cols-4 gap-4 mt-4'>
                {categories.map((category) => (
                    <Card
                        key={category.name}
                        className='p-4 w-full hover:shadow-xl transition-shadow'
                    >
                        <h2>{category.name}</h2>
                        <p>{category.icon}</p>
                    </Card>
                ))}
            </div>
        </section>
    )
}
