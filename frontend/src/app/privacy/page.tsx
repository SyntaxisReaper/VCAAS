export default function PrivacyPage() {
  return (
    <div className="min-h-screen py-24 px-6 max-w-4xl mx-auto text-[var(--text-1)]">
      <h1 className="text-4xl font-bold mb-8">Privacy Policy</h1>
      <div className="space-y-8 text-[var(--text-2)] leading-relaxed">
        <p className="text-sm opacity-70">Last updated: August 2026</p>
        
        <section>
          <h2 className="text-2xl font-semibold text-white mb-4">1. Information We Collect</h2>
          <p className="mb-4">We collect information you provide directly to us when using VCaaS, including:</p>
          <ul className="list-disc pl-6 space-y-2">
            <li><strong>Account Information:</strong> Your email address and basic profile information via Firebase Authentication.</li>
            <li><strong>Biometric Data (Voice References):</strong> Audio samples uploaded for the purpose of zero-shot voice cloning.</li>
            <li><strong>Prompts:</strong> The text inputs you provide for synthesis.</li>
            <li><strong>Usage Data:</strong> API call frequency, processing times, and diagnostic telemetry.</li>
          </ul>
        </section>
        
        <section>
          <h2 className="text-2xl font-semibold text-white mb-4">2. Handling of Biometric Data & Voice References</h2>
          <p>Because VCaaS deals with voice data, we handle it with extreme care. <strong>Voice reference files uploaded for zero-shot cloning are stored ephemerally.</strong> They are held in memory only for the duration of the inference process on our Render-hosted GPU instances and are not permanently saved to our databases unless you explicitly opt to save them to your account's Voice Library. We do not use your personal voice references to train our foundational models.</p>
        </section>

        <section>
          <h2 className="text-2xl font-semibold text-white mb-4">3. Deepfake Detection & Watermarking Logs</h2>
          <p>To comply with ethical AI guidelines, when you generate audio using our platform, we automatically embed a cryptographic watermark. We retain logs of generated watermarks (including timestamps, associated account IDs, and cryptographic hashes) to aid in the verification of deepfakes and the prevention of platform abuse.</p>
        </section>
        
        <section>
          <h2 className="text-2xl font-semibold text-white mb-4">4. Third-Party Data Processors</h2>
          <p className="mb-4">We rely on carefully vetted third-party services to operate the platform:</p>
          <ul className="list-disc pl-6 space-y-2">
            <li><strong>Google Firebase:</strong> Used exclusively for secure user authentication and account management.</li>
            <li><strong>Render:</strong> Hosts our secure backend inference APIs and processes the actual audio generation.</li>
            <li><strong>Vercel:</strong> Hosts our frontend web application and edge network.</li>
          </ul>
          <p className="mt-4">These providers are contractually obligated to protect your data and do not have rights to use your biometric inputs for their own purposes.</p>
        </section>

        <section>
          <h2 className="text-2xl font-semibold text-white mb-4">5. Data Retention & Deletion</h2>
          <p>You can delete your account at any time from your settings page. Upon deletion, your email, saved voice models, and generation history are permanently purged from our active databases. Cryptographic logs of previously generated audio may be retained for security and audit purposes to trace malicious deepfakes if requested by law enforcement.</p>
        </section>

        <section>
          <h2 className="text-2xl font-semibold text-white mb-4">6. Security Measures</h2>
          <p>We implement strict access controls, transport-layer security (HTTPS/TLS) for all API communications, and encrypted at-rest storage for databases. However, no internet transmission is 100% secure, and we cannot guarantee absolute security.</p>
        </section>

        <section>
          <h2 className="text-2xl font-semibold text-white mb-4">7. Contact Us</h2>
          <p>If you have questions regarding this Privacy Policy, your biometric data, or wish to exercise your data rights (including GDPR and CCPA requests), please contact our privacy team via the Help center.</p>
        </section>
      </div>
    </div>
  )
}
