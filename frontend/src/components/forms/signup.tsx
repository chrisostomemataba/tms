"use client"
import {
    Button
} from "@/components/ui/button"
import {
    Input
} from "@/components/ui/input"
import { SignupFormSchema } from "@/lib/definitions"
import { useActionState, useState } from "react"
// import { toast } from "sonner"
import { useToast } from "@/hooks/use-toast"
import { z } from "zod"
import { Label } from "../ui/label"
import { signUpAction } from "@/app/actions/auth"

export default function SignUpFormComponent() {
    const [error, setError] = useState<Record<string, string> | null>(null)
    const [state, formAction, isPending] = useActionState(handleFormSubmit, { error: "", status: "INITIAL" })
    const {toast} = useToast()


    async function handleFormSubmit(prevState: { error: string, status: string } | undefined, formData: FormData) {
        try {
            const formValues = {
                email: formData.get("email") as string,
                first_name: formData.get("first_name") as string,
                last_name: formData.get("last_name") as string,
                phone_number: formData.get("phone_number") as string,
            }

            await SignupFormSchema.parseAsync(formValues)

            await signUpAction(prevState, formData)

            console.log("Form values", formValues)
            
            toast({
                title: "Form submitted successfully",
                description: "We have received your form submission",
                variant: "default"
            })
        } catch (error) {
            if (error instanceof z.ZodError) {
                const fieldErrors = error.flatten().fieldErrors

                setError(fieldErrors as unknown as Record<string, string>)

                return {
                    ...prevState,
                    error: "Failed to submit the form. Please try again.",
                    status: "ERROR"
                }
                toast({
                    title: "Form submission failed",
                    description: "Failed to submit the form. Please try again.",
                    variant: "destructive"
                })
            } else {
                setError({ form: "Failed to submit the form. Please try again." })

                return {
                    ...prevState,
                    error: "Failed to submit the form. Please try again.",
                    status: "ERROR"
                }
                toast({
                    title: "Form submission failed",
                    description: "Failed to submit the form. Please try again.",
                    variant: "destructive"
                })
            }
        }
    }

    return (
        <form
            action={formAction}
            className="space-y-8 max-w-3xl mx-auto py-10"
        >
            <div className="flex items-center w-full gap-4">
                <div>
                    <Label>First Name</Label>
                    <Input
                        name="first_name"
                        placeholder="first name"
                        type="text"
                        className="w-full"
                    />
                    {error?.first_name && <p className="text-xs text-red-500">{error.first_name}</p>}
                </div>
                <div>
                    <Label>Last Name</Label>
                    <Input
                        name="last_name"
                        placeholder="last name"
                        type="text"
                    />
                    {error?.last_name && <p className="text-xs text-red-500">{error.last_name}</p>}
                </div>
            </div>

            <div>
                <Label>Email</Label>
                <Input
                    name="email"
                    placeholder="passionsteven28@gmail.com"
                    type="email"
                />
                {error?.email && <p className="text-xs text-red-500">{error.email}</p>}
            </div>

            <div>
                <Label>Phone Number</Label>
                <Input
                    name="phone_number"
                    type="number"
                    placeholder="phone number"
                />
                {error?.phone_number && <p className="text-xs text-red-500">{error.phone_number}</p>}
            </div>
            <Button
                type="submit"
                disabled={isPending}
            >
                {isPending ? "Submitting..." : "Submit"}
                Submit
            </Button>
        </form>
    )
}
