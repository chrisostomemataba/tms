'use server'

export async function signUpAction(state: unknown, formData: FormData) {
    const formValues = {
        email: formData.get("email") as string,
        first_name: formData.get("first_name") as string,
        last_name: formData.get("last_name") as string,
        phone_number: formData.get("phone_number") as string,
    }

    console.log("Form values from server", formValues)

    // call auth endpoint from django rest framework
    await fetch('http://127.0.0.1:8000/api/users/users/', {
        method: 'POST',
        body: JSON.stringify(formValues),
    })

}
