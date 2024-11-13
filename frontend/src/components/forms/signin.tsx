"use client"
import {
    Button
} from "@/components/ui/button"
import {
    Input
} from "@/components/ui/input"
import { SigninFormSchema } from "@/lib/definitions"
import { useActionState, useState } from "react"
// import { toast } from "sonner"
import { signInAction } from "@/app/actions/auth"
import { useToast } from "@/hooks/use-toast"
import { useRouter } from "next/navigation"
import { z } from "zod"
import { Label } from "../ui/label"

export default function SignInFormComponent() {
    const [error, setError] = useState<Record<string, string> | null>(null)
    // eslint-disable-next-line @typescript-eslint/no-unused-vars
    const [state, formAction, isPending] = useActionState(handleFormSubmit, { error: "", status: "INITIAL" })
    const { toast } = useToast()
    const router = useRouter()


    async function handleFormSubmit(prevState: { error: string, status: string } | undefined, formData: FormData) {
        try {
            const formValues = {
                email: formData.get("email") as string,
                password: formData.get("password") as string,
            }

            await SigninFormSchema.parseAsync(formValues)

            const result = await signInAction(formData);
            if (!result.success && result.errors) {
                if (typeof result.errors === 'string') {
                    // Show generic error message
                    setError({ form: result.errors });
                } else {
                    // Set field-specific errors
                    const fieldErrors: Record<string, string> = {};
                    Object.entries(result.errors).forEach(([field, messages]) => {
                        fieldErrors[field] = messages[0];
                    });
                    setError(fieldErrors);
                }
            } else {
                // Handle success
                router.push('/');
            }
        } catch (error) {
            if (error instanceof z.ZodError) {
                const fieldErrors = error.flatten().fieldErrors
                setError(fieldErrors as unknown as Record<string, string>)
                return {
                    ...prevState,
                    error: "Failed to submit the form. Please try again.",
                    status: "ERROR"
                }
            }

            // console.log("Form values", formValues)
            
            toast({
                title: "Form submitted successfully",
                description: "We have received your form submission",
                variant: "default"
            })
        }
    }

    return (
        <form
            action={formAction}
            className="space-y-8 max-w-3xl mx-auto py-10"
        >
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
                <Label>Password</Label>
                <Input
                    name="password"
                    type="password"
                    placeholder="********"
                />
                {error?.password && <p className="text-xs text-red-500">{error.password}</p>}
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
