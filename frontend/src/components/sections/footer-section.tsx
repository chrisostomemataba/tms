import React from 'react'
import { Card } from '../ui/card'
import { Input } from '../ui/input'
import { Button } from '../ui/button'
import { Logo } from '../shared/logo'
import { Facebook, Instagram, X, Youtube } from 'lucide-react'
import Link from 'next/link'

const socials = [
    {
        name: 'facebook',
        href: '#',
        icon: <Facebook />
    },
    {
        name: 'twitter',
        href: '#',
        icon: <X />
    },
    {
        name: 'instagram',
        href: '#',
        icon: <Instagram />
    },
    {
        name: 'youtube',
        href: '#',
        icon: <Youtube />
    }
]

const footerLinks = [
    {
        for: 'Company',
        links: [
            {
                name: 'About',
                href: '#'
            },
            {
                name: 'Contact',
                href: '#'
            },
            {
                name: 'Careers',
                href: '#'
            },
        ]
    },
    {
        for: 'Resources',
        links: [
            {
                name: 'Terms of Service',
                href: '#'
            },
            {
                name: 'Privacy Policy',
                href: '#'
            },
            {
                name: 'Cookie Policy',
                href: '#'
            }
        ]
    }
]

export const FooterSection = () => {
    return (
        <footer className='min-h-[50vh] w-full flex flex-col gap-4 space-y-4 justify-end bg-white/70 backdrop-blur-sm'>
            <div className='px-16'>
                <Card className='p-4 w-full mb-10'>
                    <div className='flex items-center justify-center flex-col gap-4'>
                        <h1 className='text-2xl font-bold'>
                            Subscribe to our newsletter
                        </h1>
                        <p className='text-sm'>subscribe to our newsletter</p>
                        <div className='border-2 rounded-full flex items-center overflow-hidden'>
                            <Input
                                placeholder='Enter your email'
                                type='email'
                                className='border-0 ring-0 focus-visible:ring-0'
                            />
                            <Button
                                className='rounded-full'
                            >
                                Subscribe
                            </Button>
                        </div>
                    </div>
                </Card>
                <div className='flex items-center justify-evenly gap-4'>
                    <div>
                        <Logo
                            width={40}
                            height={50}
                        />
                        <h1>
                            the best course for your learning needs
                            in tanzania
                        </h1>
                        <div className='flex items-center justify-start gap-2'>
                            {socials.map((social) => (
                                <Link
                                    key={social.name}
                                    href={social.href}
                                    className='hover:text-primary transition-colors'
                                >
                                    {social.icon}
                                </Link>
                            ))}
                        </div>
                    </div>
                    <div className='flex items-center justify-between gap-4'>
                        {footerLinks.map((link) => (
                            <div key={link.for}>
                                <h1 className='text-xl font-bold'>
                                    {link.for}
                                </h1>
                                <ul>
                                    {link.links.map((link) => (
                                        <li key={link.name}>
                                            <Link
                                                href={link.href}
                                                className='hover:text-primary transition-colors'
                                            >
                                                {link.name}
                                            </Link>
                                        </li>
                                    ))}
                                </ul>
                            </div>
                        ))}
                    </div>
                </div>
            </div>

            <div className='bg-gray-500 flex items-center justify-center p-4'>
                <h1>
                    &copy; 2023 tms. All rights reserved.
                </h1>
            </div>
        </footer>
    )
}
