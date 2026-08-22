import { VoiceLicense, VoiceModel } from '../types/voice';
import { v4 as uuidv4 } from 'uuid';

export interface LicenseTemplate {
  id: string;
  name: string;
  type: 'personal' | 'commercial' | 'enterprise';
  description: string;
  permissions: LicensePermissions;
  restrictions: LicenseRestrictions;
  pricing: LicensePricing;
  duration: LicenseDuration;
}

export interface LicensePermissions {
  allowCommercialUse: boolean;
  allowModification: boolean;
  allowDistribution: boolean;
  allowSubLicensing: boolean;
  allowPublicPerformance: boolean;
  allowBroadcast: boolean;
  allowOnlineStreaming: boolean;
  allowSynchronization: boolean;
  requireAttribution: boolean;
  allowDerivativeWorks: boolean;
}

export interface LicenseRestrictions {
  maxUsageCount?: number;
  maxDurationPerUse?: number; // in seconds
  maxConcurrentUsers?: number;
  restrictedTerritories: string[];
  restrictedPlatforms: string[];
  restrictedIndustries: string[];
  contentRestrictions: string[];
  qualityRestrictions?: {
    maxSampleRate: number;
    maxBitrate: number;
    maxChannels: number;
  };
}

export interface LicensePricing {
  basePrice: number;
  currency: 'USD' | 'EUR' | 'GBP';
  pricingModel: 'one-time' | 'subscription' | 'usage-based' | 'tiered';
  usageRates?: {
    perSecond?: number;
    perGeneration?: number;
    perDownload?: number;
    perStream?: number;
  };
  subscriptionTiers?: Array<{
    name: string;
    monthlyPrice: number;
    usageLimit: number;
    features: string[];
  }>;
}

export interface LicenseDuration {
  type: 'perpetual' | 'time-limited' | 'usage-limited';
  duration?: number; // in days for time-limited
  usageLimit?: number; // for usage-limited
  renewalOptions?: {
    autoRenew: boolean;
    renewalPrice: number;
    renewalDiscount: number;
  };
}

export interface LicenseAgreement {
  id: string;
  licenseId: string;
  voiceId: string;
  licenseeId: string;
  licensorId: string;
  signedAt: Date;
  expiresAt?: Date;
  status: 'active' | 'expired' | 'suspended' | 'terminated';
  terms: LicenseTemplate;
  usage: LicenseUsage;
  payments: LicensePayment[];
  violations: LicenseViolation[];
}

export interface LicenseUsage {
  totalGenerations: number;
  totalDuration: number;
  totalDownloads: number;
  totalStreams: number;
  lastUsed: Date;
  usageByPlatform: Record<string, number>;
  usageByTerritory: Record<string, number>;
  monthlyUsage: Array<{
    month: string;
    generations: number;
    duration: number;
    cost: number;
  }>;
}

export interface LicensePayment {
  id: string;
  amount: number;
  currency: string;
  paidAt: Date;
  paymentMethod: string;
  transactionId: string;
  type: 'initial' | 'renewal' | 'usage-fee' | 'penalty';
  status: 'pending' | 'completed' | 'failed' | 'refunded';
}

export interface LicenseViolation {
  id: string;
  type: 'usage-exceeded' | 'unauthorized-use' | 'territory-violation' | 'platform-violation' | 'content-violation';
  description: string;
  detectedAt: Date;
  severity: 'minor' | 'major' | 'critical';
  resolved: boolean;
  penalty?: number;
  action: 'warning' | 'suspension' | 'termination' | 'fine';
}

export class LicensingManager {
  private templates: Map<string, LicenseTemplate> = new Map();
  private agreements: Map<string, LicenseAgreement> = new Map();
  private activeMonitoring: Map<string, LicenseMonitor> = new Map();

  constructor() {
    this.initializeDefaultTemplates();
  }

  /**
   * Initialize default license templates
   */
  private initializeDefaultTemplates(): void {
    // Personal License
    const personalTemplate: LicenseTemplate = {
      id: 'personal-basic',
      name: 'Personal Use License',
      type: 'personal',
      description: 'Basic license for personal, non-commercial use',
      permissions: {
        allowCommercialUse: false,
        allowModification: false,
        allowDistribution: false,
        allowSubLicensing: false,
        allowPublicPerformance: false,
        allowBroadcast: false,
        allowOnlineStreaming: true,
        allowSynchronization: false,
        requireAttribution: true,
        allowDerivativeWorks: false
      },
      restrictions: {
        maxUsageCount: 100,
        maxDurationPerUse: 300, // 5 minutes
        maxConcurrentUsers: 1,
        restrictedTerritories: [],
        restrictedPlatforms: ['commercial-broadcast', 'paid-streaming'],
        restrictedIndustries: ['adult-content', 'political-campaigns'],
        contentRestrictions: ['no-hate-speech', 'no-illegal-content'],
        qualityRestrictions: {
          maxSampleRate: 44100,
          maxBitrate: 192,
          maxChannels: 2
        }
      },
      pricing: {
        basePrice: 0,
        currency: 'USD',
        pricingModel: 'one-time'
      },
      duration: {
        type: 'time-limited',
        duration: 365, // 1 year
        renewalOptions: {
          autoRenew: false,
          renewalPrice: 0,
          renewalDiscount: 0
        }
      }
    };

    // Commercial License
    const commercialTemplate: LicenseTemplate = {
      id: 'commercial-standard',
      name: 'Commercial Use License',
      type: 'commercial',
      description: 'Standard license for commercial applications',
      permissions: {
        allowCommercialUse: true,
        allowModification: true,
        allowDistribution: true,
        allowSubLicensing: false,
        allowPublicPerformance: true,
        allowBroadcast: true,
        allowOnlineStreaming: true,
        allowSynchronization: true,
        requireAttribution: false,
        allowDerivativeWorks: true
      },
      restrictions: {
        maxUsageCount: 10000,
        maxDurationPerUse: 1800, // 30 minutes
        maxConcurrentUsers: 50,
        restrictedTerritories: [],
        restrictedPlatforms: [],
        restrictedIndustries: ['adult-content'],
        contentRestrictions: ['no-hate-speech', 'no-illegal-content', 'no-defamatory-content']
      },
      pricing: {
        basePrice: 299,
        currency: 'USD',
        pricingModel: 'subscription',
        subscriptionTiers: [
          {
            name: 'Starter',
            monthlyPrice: 29,
            usageLimit: 1000,
            features: ['Basic support', 'Standard quality', 'Attribution required']
          },
          {
            name: 'Professional',
            monthlyPrice: 99,
            usageLimit: 5000,
            features: ['Priority support', 'High quality', 'No attribution', 'API access']
          },
          {
            name: 'Enterprise',
            monthlyPrice: 299,
            usageLimit: 20000,
            features: ['24/7 support', 'Ultra quality', 'White-label', 'Custom integration']
          }
        ]
      },
      duration: {
        type: 'time-limited',
        duration: 365,
        renewalOptions: {
          autoRenew: true,
          renewalPrice: 299,
          renewalDiscount: 10
        }
      }
    };

    // Enterprise License
    const enterpriseTemplate: LicenseTemplate = {
      id: 'enterprise-unlimited',
      name: 'Enterprise Unlimited License',
      type: 'enterprise',
      description: 'Unlimited license for enterprise applications',
      permissions: {
        allowCommercialUse: true,
        allowModification: true,
        allowDistribution: true,
        allowSubLicensing: true,
        allowPublicPerformance: true,
        allowBroadcast: true,
        allowOnlineStreaming: true,
        allowSynchronization: true,
        requireAttribution: false,
        allowDerivativeWorks: true
      },
      restrictions: {
        restrictedTerritories: [],
        restrictedPlatforms: [],
        restrictedIndustries: [],
        contentRestrictions: ['no-illegal-content']
      },
      pricing: {
        basePrice: 2999,
        currency: 'USD',
        pricingModel: 'one-time'
      },
      duration: {
        type: 'perpetual'
      }
    };

    this.templates.set(personalTemplate.id, personalTemplate);
    this.templates.set(commercialTemplate.id, commercialTemplate);
    this.templates.set(enterpriseTemplate.id, enterpriseTemplate);
  }

  /**
   * Create a new license agreement
   */
  async createLicenseAgreement(
    voiceId: string,
    templateId: string,
    licenseeId: string,
    licensorId: string,
    customTerms?: Partial<LicenseTemplate>
  ): Promise<LicenseAgreement> {
    const template = this.templates.get(templateId);
    if (!template) {
      throw new Error(`License template ${templateId} not found`);
    }

    const agreement: LicenseAgreement = {
      id: uuidv4(),
      licenseId: templateId,
      voiceId,
      licenseeId,
      licensorId,
      signedAt: new Date(),
      expiresAt: this.calculateExpiryDate(template.duration),
      status: 'active',
      terms: { ...template, ...customTerms },
      usage: {
        totalGenerations: 0,
        totalDuration: 0,
        totalDownloads: 0,
        totalStreams: 0,
        lastUsed: new Date(),
        usageByPlatform: {},
        usageByTerritory: {},
        monthlyUsage: []
      },
      payments: [],
      violations: []
    };

    this.agreements.set(agreement.id, agreement);
    
    // Start monitoring if usage-based
    if (template.pricing.pricingModel === 'usage-based') {
      this.startLicenseMonitoring(agreement.id);
    }

    return agreement;
  }

  /**
   * Track usage for a license agreement
   */
  async trackUsage(
    agreementId: string,
    usage: {
      generations?: number;
      duration?: number;
      downloads?: number;
      streams?: number;
      platform?: string;
      territory?: string;
    }
  ): Promise<void> {
    const agreement = this.agreements.get(agreementId);
    if (!agreement) {
      throw new Error(`License agreement ${agreementId} not found`);
    }

    // Update usage counters
    if (usage.generations) agreement.usage.totalGenerations += usage.generations;
    if (usage.duration) agreement.usage.totalDuration += usage.duration;
    if (usage.downloads) agreement.usage.totalDownloads += usage.downloads;
    if (usage.streams) agreement.usage.totalStreams += usage.streams;

    // Track platform usage
    if (usage.platform) {
      agreement.usage.usageByPlatform[usage.platform] = 
        (agreement.usage.usageByPlatform[usage.platform] || 0) + 1;
    }

    // Track territory usage
    if (usage.territory) {
      agreement.usage.usageByTerritory[usage.territory] = 
        (agreement.usage.usageByTerritory[usage.territory] || 0) + 1;
    }

    agreement.usage.lastUsed = new Date();

    // Check for violations
    await this.checkViolations(agreement);

    // Calculate usage-based fees
    if (agreement.terms.pricing.pricingModel === 'usage-based') {
      await this.calculateUsageFees(agreement);
    }
  }

  /**
   * Check for license violations
   */
  private async checkViolations(agreement: LicenseAgreement): Promise<void> {
    const violations: LicenseViolation[] = [];

    // Check usage limits
    const restrictions = agreement.terms.restrictions;
    
    if (restrictions.maxUsageCount && agreement.usage.totalGenerations > restrictions.maxUsageCount) {
      violations.push({
        id: uuidv4(),
        type: 'usage-exceeded',
        description: `Usage count exceeded: ${agreement.usage.totalGenerations}/${restrictions.maxUsageCount}`,
        detectedAt: new Date(),
        severity: 'major',
        resolved: false,
        action: 'suspension'
      });
    }

    // Check restricted platforms
    const platformViolations = Object.keys(agreement.usage.usageByPlatform)
      .filter(platform => restrictions.restrictedPlatforms.includes(platform));
    
    platformViolations.forEach(platform => {
      violations.push({
        id: uuidv4(),
        type: 'platform-violation',
        description: `Unauthorized use on restricted platform: ${platform}`,
        detectedAt: new Date(),
        severity: 'critical',
        resolved: false,
        action: 'termination'
      });
    });

    // Check restricted territories
    const territoryViolations = Object.keys(agreement.usage.usageByTerritory)
      .filter(territory => restrictions.restrictedTerritories.includes(territory));
    
    territoryViolations.forEach(territory => {
      violations.push({
        id: uuidv4(),
        type: 'territory-violation',
        description: `Unauthorized use in restricted territory: ${territory}`,
        detectedAt: new Date(),
        severity: 'major',
        resolved: false,
        action: 'fine',
        penalty: 500
      });
    });

    // Add violations to agreement
    agreement.violations.push(...violations);

    // Take action for critical violations
    const criticalViolations = violations.filter(v => v.severity === 'critical');
    if (criticalViolations.length > 0) {
      agreement.status = 'suspended';
    }
  }

  /**
   * Calculate usage-based fees
   */
  private async calculateUsageFees(agreement: LicenseAgreement): Promise<void> {
    const rates = agreement.terms.pricing.usageRates;
    if (!rates) return;

    let totalFee = 0;

    if (rates.perGeneration) {
      totalFee += agreement.usage.totalGenerations * rates.perGeneration;
    }

    if (rates.perSecond) {
      totalFee += agreement.usage.totalDuration * rates.perSecond;
    }

    if (rates.perDownload) {
      totalFee += agreement.usage.totalDownloads * rates.perDownload;
    }

    if (rates.perStream) {
      totalFee += agreement.usage.totalStreams * rates.perStream;
    }

    if (totalFee > 0) {
      const payment: LicensePayment = {
        id: uuidv4(),
        amount: totalFee,
        currency: agreement.terms.pricing.currency,
        paidAt: new Date(),
        paymentMethod: 'auto-charge',
        transactionId: uuidv4(),
        type: 'usage-fee',
        status: 'pending'
      };

      agreement.payments.push(payment);
    }
  }

  /**
   * Start monitoring for a license agreement
   */
  private startLicenseMonitoring(agreementId: string): void {
    const monitor = new LicenseMonitor(agreementId, this);
    this.activeMonitoring.set(agreementId, monitor);
    monitor.start();
  }

  /**
   * Validate if an action is allowed under a license
   */
  async validateAction(
    agreementId: string,
    action: {
      type: 'generate' | 'download' | 'stream' | 'modify' | 'distribute' | 'broadcast';
      platform?: string;
      territory?: string;
      duration?: number;
    }
  ): Promise<{ allowed: boolean; reason?: string }> {
    const agreement = this.agreements.get(agreementId);
    if (!agreement) {
      return { allowed: false, reason: 'License agreement not found' };
    }

    if (agreement.status !== 'active') {
      return { allowed: false, reason: `License is ${agreement.status}` };
    }

    if (agreement.expiresAt && agreement.expiresAt < new Date()) {
      return { allowed: false, reason: 'License has expired' };
    }

    const permissions = agreement.terms.permissions;
    const restrictions = agreement.terms.restrictions;

    // Check permissions
    switch (action.type) {
      case 'generate':
        if (restrictions.maxUsageCount && agreement.usage.totalGenerations >= restrictions.maxUsageCount) {
          return { allowed: false, reason: 'Usage limit exceeded' };
        }
        if (action.duration && restrictions.maxDurationPerUse && action.duration > restrictions.maxDurationPerUse) {
          return { allowed: false, reason: 'Duration exceeds limit' };
        }
        break;

      case 'modify':
        if (!permissions.allowModification) {
          return { allowed: false, reason: 'Modification not allowed' };
        }
        break;

      case 'distribute':
        if (!permissions.allowDistribution) {
          return { allowed: false, reason: 'Distribution not allowed' };
        }
        break;

      case 'broadcast':
        if (!permissions.allowBroadcast) {
          return { allowed: false, reason: 'Broadcasting not allowed' };
        }
        break;

      case 'stream':
        if (!permissions.allowOnlineStreaming) {
          return { allowed: false, reason: 'Online streaming not allowed' };
        }
        break;
    }

    // Check platform restrictions
    if (action.platform && restrictions.restrictedPlatforms.includes(action.platform)) {
      return { allowed: false, reason: `Platform ${action.platform} is restricted` };
    }

    // Check territory restrictions
    if (action.territory && restrictions.restrictedTerritories.includes(action.territory)) {
      return { allowed: false, reason: `Territory ${action.territory} is restricted` };
    }

    return { allowed: true };
  }

  /**
   * Get license agreement by ID
   */
  getLicenseAgreement(agreementId: string): LicenseAgreement | undefined {
    return this.agreements.get(agreementId);
  }

  /**
   * Get all license agreements for a voice
   */
  getLicenseAgreementsForVoice(voiceId: string): LicenseAgreement[] {
    return Array.from(this.agreements.values())
      .filter(agreement => agreement.voiceId === voiceId);
  }

  /**
   * Get license templates
   */
  getLicenseTemplates(): LicenseTemplate[] {
    return Array.from(this.templates.values());
  }

  /**
   * Calculate expiry date based on duration settings
   */
  private calculateExpiryDate(duration: LicenseDuration): Date | undefined {
    if (duration.type === 'perpetual') {
      return undefined;
    }

    if (duration.type === 'time-limited' && duration.duration) {
      const expiryDate = new Date();
      expiryDate.setDate(expiryDate.getDate() + duration.duration);
      return expiryDate;
    }

    return undefined;
  }
}

/**
 * License monitoring for real-time compliance
 */
class LicenseMonitor {
  private agreementId: string;
  private licensingManager: LicensingManager;
  private intervalId?: NodeJS.Timeout;
  private monitoringInterval = 60000; // 1 minute

  constructor(agreementId: string, licensingManager: LicensingManager) {
    this.agreementId = agreementId;
    this.licensingManager = licensingManager;
  }

  start(): void {
    this.intervalId = setInterval(() => {
      this.performCheck();
    }, this.monitoringInterval);
  }

  stop(): void {
    if (this.intervalId) {
      clearInterval(this.intervalId);
      this.intervalId = undefined;
    }
  }

  private async performCheck(): Promise<void> {
    const agreement = this.licensingManager.getLicenseAgreement(this.agreementId);
    if (!agreement) {
      this.stop();
      return;
    }

    // Check for expiry
    if (agreement.expiresAt && agreement.expiresAt < new Date()) {
      agreement.status = 'expired';
    }

    // Perform other compliance checks
    // This could include checking usage patterns, detecting anomalies, etc.
  }
}

// Export singleton instance
export const licensingManager = new LicensingManager();