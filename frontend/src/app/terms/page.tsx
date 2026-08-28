export default function TermsPage() {
  return (
    <div className="min-h-screen py-24 px-6 max-w-4xl mx-auto text-[var(--text-1)]">
      <h1 className="text-4xl font-bold mb-8">Terms of Service</h1>
      <div className="space-y-6 text-[var(--text-2)]">
        <p>Last updated: August 2026</p>
        <section>
          <h2 className="text-2xl font-semibold text-white mb-4">1. Acceptance of Terms</h2>
          <p>By accessing and using this service, you accept and agree to be bound by the terms and provision of this agreement.</p>
        </section>
        <section>
          <h2 className="text-2xl font-semibold text-white mb-4">2. Description of Service</h2>
          <p>VCaaS provides voice cloning and text-to-speech services for creators. We reserve the right to modify or discontinue, temporarily or permanently, the service with or without notice.</p>
        </section>
        <section>
          <h2 className="text-2xl font-semibold text-white mb-4">3. User Conduct</h2>
          <p>You agree not to use the service to clone voices without explicit permission from the voice owner, or to generate harmful, illegal, or deceptive content.</p>
        </section>
      </div>
    </div>
  )
}
