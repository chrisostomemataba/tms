import HeroSection from "@/components/layouts/hero-section";
import { FooterSection } from "@/components/sections/footer-section";
import { PopularCoursesSection } from "@/components/sections/popular-courses-section";
import { TestimonySection } from "@/components/sections/testimony-section";
import { WhyUsSection } from "@/components/sections/why-us-section";
import { getSession } from "./actions/session";
import { redirect } from "next/navigation";

export default async function Home() {
  const session = await getSession();
  if (!session?.success) redirect('/signin');

  return (
    <main className="grid place-items-center min-h-screen w-full">
      <HeroSection />
      <PopularCoursesSection />
      <WhyUsSection />
      <TestimonySection />
      <FooterSection />
    </main>
  );
}
