export default function PrivacyPage() {
  return (
    <div className="min-h-screen py-24 px-6 max-w-4xl mx-auto text-[var(--text-1)]">
      <h1 className="text-4xl font-bold mb-8">Privacy Policy</h1>
      <div className="space-y-6 text-[var(--text-2)]">
        <p>Last updated: August 2026</p>
        <section>
          <h2 className="text-2xl font-semibold text-white mb-4">1. Information We Collect</h2>
          <p>We collect information you provide directly to us, such as when you create or modify your account, request on-demand services, or contact customer support. This includes audio samples uploaded for voice training.</p>
        </section>
        <section>
          <h2 className="text-2xl font-semibold text-white mb-4">2. How We Use Information</h2>
          <p>We use the information we collect to provide, maintain, and improve our services, including training custom voice models solely for your account.</p>
        </section>
        <section>
          <h2 className="text-2xl font-semibold text-white mb-4">3. Data Security</h2>
          <p>We implement appropriate technical and organizational measures to protect the security of your personal information and voice data.</p>
        </section>
      </div>
    </div>
  )
}
