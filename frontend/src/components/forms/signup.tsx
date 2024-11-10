"use client"
import { signup } from "@/app/actions/auth"
import {
    Button
} from "@/components/ui/button"
import {
    Checkbox
} from "@/components/ui/checkbox"
import {
    Form,
    FormControl,
    FormDescription,
    FormField,
    FormItem,
    FormLabel,
    FormMessage,
} from "@/components/ui/form"
import {
    Input
} from "@/components/ui/input"
import {
    PhoneInput
} from "@/components/ui/phone-input"
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue
} from "@/components/ui/select"
import { SignupFormSchema } from "@/lib/definitions"
import {
    zodResolver
} from "@hookform/resolvers/zod"
import { useForm } from "react-hook-form"
// import { toast } from "sonner"
import * as z from "zod"

export default function SignUpFormComponent() {
    const form = useForm<z.infer<typeof SignupFormSchema>>({
        resolver: zodResolver(SignupFormSchema),

    })

    async function onSubmit(values: z.infer<typeof SignupFormSchema>) {
        try {
            console.log('formData', values);
            await signup(values);  // Remove the formData wrapper
            // toast.success("Signup successful!");
            // form.reset();
        } catch (error) {
            console.error("Form submission error", error);
            // toast.error("Failed to submit the form. Please try again.");
        }
    }

    return (
        <Form {...form}>
            <form
                onSubmit={form.handleSubmit(onSubmit)}
                className="space-y-8 max-w-3xl mx-auto py-10"
            >
                <div className="flex items-center w-full gap-4">
                    <FormField
                        control={form.control}
                        name="first_name"
                        render={({ field }) => (
                            <FormItem>
                                <FormLabel>first name</FormLabel>
                                <FormControl>
                                    <Input
                                        placeholder="first name"
                                        type="text"
                                        className="w-full"
                                        {...field} />
                                </FormControl>
                                <FormMessage />
                            </FormItem>
                        )}
                    />
                    <FormField
                        control={form.control}
                        name="last_name"
                        render={({ field }) => (
                            <FormItem>
                                <FormLabel>last name</FormLabel>
                                <FormControl>
                                    <Input
                                        placeholder="last name"
                                        type="text"
                                        {...field} />
                                </FormControl>
                                <FormMessage />
                            </FormItem>
                        )}
                    />
                </div>

                <FormField
                    control={form.control}
                    name="email"
                    render={({ field }) => (
                        <FormItem>
                            <FormLabel>email</FormLabel>
                            <FormControl>
                                <Input
                                    placeholder="passionsteven28@gmail.com"

                                    type="email"
                                    {...field} />
                            </FormControl>
                            <FormDescription>enter your email address </FormDescription>
                            <FormMessage />
                        </FormItem>
                    )}
                />

                <FormField
                    control={form.control}
                    name="phone_number"
                    render={({ field }) => (
                        <FormItem className="flex flex-col items-start">
                            <FormLabel>Phone number</FormLabel>
                            <FormControl className="w-full">
                                <PhoneInput
                                    placeholder=""
                                    {...field}
                                    defaultCountry="TZ"
                                />
                            </FormControl>
                            <FormDescription>Enter your phone number.</FormDescription>
                            <FormMessage />
                        </FormItem>
                    )}
                />

                <div className="flex items-center w-full gap-4">
                    <FormField
                        control={form.control}
                        name="role"
                        render={({ field }) => (
                            <FormItem>
                                <FormLabel>role</FormLabel>
                                <Select onValueChange={field.onChange} defaultValue={field.value}>
                                    <FormControl>
                                        <SelectTrigger>
                                            <SelectValue placeholder="trainer" />
                                        </SelectTrigger>
                                    </FormControl>
                                    <SelectContent>
                                        <SelectItem value="m@example.com">m@example.com</SelectItem>
                                        <SelectItem value="m@google.com">m@google.com</SelectItem>
                                        <SelectItem value="m@support.com">m@support.com</SelectItem>
                                    </SelectContent>
                                </Select>
                                <FormDescription>select role</FormDescription>
                                <FormMessage />
                            </FormItem>
                        )}
                    />
                    <FormField
                        control={form.control}
                        name="active"
                        render={({ field }) => (
                            <FormItem className="flex flex-row items-start space-x-3 space-y-0 rounded-md border p-4">
                                <FormControl>
                                    <Checkbox
                                        checked={field.value}
                                        onCheckedChange={field.onChange}
                                    />
                                </FormControl>
                                <div className="space-y-1 leading-none">
                                    <FormLabel>is active</FormLabel>
                                    <FormMessage />
                                </div>
                            </FormItem>
                        )}
                    />
                </div>

                <Button type="submit">Submit</Button>
            </form>
        </Form>
    )
}
