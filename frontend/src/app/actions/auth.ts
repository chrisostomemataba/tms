interface SignupData {
    email: string;
    first_name: string;
    last_name: string;
    phone_number: string;
    role: string;
}

export async function signup(data: SignupData) {
    const email = data.email
    const first_name = data.first_name
    const last_name = data.last_name
    const phone_number = data.phone_number
    const role = data.role
    console.log(email, first_name, last_name, phone_number, role)


    // call auth endpoint from django rest framework
    await fetch('http://127.0.0.1:8000/api/users/users/', {
        method: 'POST',
        body: JSON.stringify({
            "email": email,
            "first_name": first_name,
            "last_name": last_name,
            "role": null,
            "is_active": false,
        })
    })

}
