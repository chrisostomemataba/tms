import React from 'react'
import { TitleSectionLayouts } from '../layouts/title-section-layout'
import { CourseCard } from '../shared/course-card'

const courses = [
    {
        price: 100,
        image: 'https://images.unsplash.com/photo-1660616246653-e2c57d1077b9?q=80&w=1631&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D',
        title: 'Python for Everyone',
        Category: 'Python',
        level: 'Beginner',
        Duration: '2 hrs 30 mins'
    },
    {
        price: 200,
        image: 'https://images.unsplash.com/photo-1660616246653-e2c57d1077b9?q=80&w=1631&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D',
        title: 'Python for Everyone',
        Category: 'Python',
        level: 'Beginner',
        Duration: '2 hrs 30 mins'
    },
    {
        price: 300,
        image: 'https://images.unsplash.com/photo-1660616246653-e2c57d1077b9?q=80&w=1631&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D',
        title: 'Python for Everyone',
        Category: 'Python',
        level: 'Beginner',
        Duration: '2 hrs 30 mins'
    },
    {
        price: 400,
        image: 'https://images.unsplash.com/photo-1660616246653-e2c57d1077b9?q=80&w=1631&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D',
        title: 'Python for Everyone',
        Category: 'Python',
        level: 'Beginner',
        Duration: '2 hrs 30 mins'
    }
]

export const PopularCoursesSection = () => {
    return (
        <TitleSectionLayouts
            title="Popular Courses"
            paragraph="Here are some of the most popular courses on the platform."
        >
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 mt-4">
                {
                    courses.map((course, index) => {
                        return (
                            <CourseCard key={index} {...course} />
                        )
                    })
                }
            </div>
        </TitleSectionLayouts>
    )
}
