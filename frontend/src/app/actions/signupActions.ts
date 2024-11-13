// signupActions.ts
'use server';

import { SignupFormSchema } from './validation';
import { z } from 'zod';
import { signup } from './api';

export async function signupAction(formData: FormData) {
  const values = SignupFormSchema.parse(Object.fromEntries(formData));
  try {
    console.log('formData', values);
    await signup(values);
    // Handle success (e.g., redirect or show a message)
  } catch (error) {
    console.error("Form submission error", error);
    // Handle error (e.g., show error message)
  }
}