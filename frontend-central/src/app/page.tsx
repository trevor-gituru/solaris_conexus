'use client';
// @/app/pages.tsx
import HeroSection from '@/components/ui/HeroSection';
import WorkSection from '@/components/ui/WorkSection';
import FeatureSection from '@/components/ui/FeatureSection';
import CtaSection from '@/components/ui/CtaSection';
import FooterSection from '@/components/ui/FooterSection';

export default function Home() {
  return (
    <>
      <HeroSection />
      <WorkSection />
      <FeatureSection />
      <CtaSection />
      <FooterSection />
    </>
  );
}
