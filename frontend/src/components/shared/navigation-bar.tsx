import React from 'react'
import { Logo } from './logo'
import Link from 'next/link'
import { Button } from '../ui/button'

const navLinks = [
    { name: 'Home', href: '/' },
    { name: 'Courses', href: '/courses' },
    { name: 'About', href: '/about' },
    { name: 'Contact', href: '/contact' },
]

const NavigationBar = () => {
    return (
        <nav className="p-4 flex justify-evenly items-center sticky top-0 bg-white/70 backdrop-blur-sm z-50">
            <div>
                <Logo
                    width={40}
                    height={50}
                />
            </div>
            
            <ul className='flex items-center justify-between gap-2 font-semibold leading-tight text-lg capitalize'>
                {navLinks.map((link) => (
                    <li
                        key={link.name}
                    >
                        <Link
                            href={link.href}
                            className='hover:underline underline-offset-2 transition-all duration-200 ease-in-out'
                        >
                            {link.name}
                        </Link>
                    </li>
                ))}
            </ul>

            <div className='flex items-center gap-4'>
                <Button>
                    login
                </Button>
                <Button variant={'outline'} asChild>
                    <Link
                        href='/signup'
                    >
                    sign up
                    </Link>
                </Button>
            </div>
        </nav>
    )
}

export default NavigationBar
