/**
 * Demo Data Generator
 * Generates realistic mock data for testing all ReturnIQ features
 * Can be used standalone or integrated with actual backend
 */

export interface Return {
  id: string;
  customerId: string;
  customerName: string;
  productName: string;
  category: string;
  amount: number;
  classification: string;
  confidence: number;
  roiPotential: number;
  churnRisk: number;
  fraudScore: number;
  status: 'pending' | 'approved' | 'rejected' | 'implemented';
  returnDate: string;
}

export interface AtRiskCustomer {
  customerId: string;
  name: string;
  email: string;
  phone?: string;
  ltv: number;
  eqScore: number;
  churnRisk: number;
  emotionalState: string;
  returnsLast30Days: number;
  primarySentiment: string;
  sentiment: string[];
  lastReturn: string;
  interventioneRecommended: string;
  successProbability: number;
  suggestedOffer?: string;
  suggestedMessage?: string;
}

export interface ActionItem {
  id: string;
  type: 'recommendation' | 'churn' | 'trend' | 'risk';
  title: string;
  description: string;
  impact: 'high' | 'medium' | 'low';
  priority: 'critical' | 'high' | 'medium' | 'low';
  dueDate: string;
  owner?: string;
  action: string;
  metrics?: { label: string; value: number | string }[];
}

// ============================================================================
// SCENARIO 1: Basic Sizing Issue
// ============================================================================
export const SCENARIO_SIZING_ISSUE = {
  atRiskCustomers: [],
  returns: [
    {
      id: 'RET_001',
      customerId: 'CUST_001',
      customerName: 'John Smith',
      productName: 'Blue T-Shirt Size M',
      category: 'SIZING',
      amount: 45.99,
      classification: 'SIZING',
      confidence: 0.96,
      roiPotential: 3.77,
      churnRisk: 0.15,
      fraudScore: 0.02,
      status: 'pending' as const,
      returnDate: new Date().toISOString(),
    },
  ],
  actionItems: [
    {
      id: 'ACT_001',
      type: 'recommendation' as const,
      title: 'Update Size Chart for SKU #456',
      description: 'Multiple sizing issues detected from supplier',
      impact: 'high' as const,
      priority: 'critical' as const,
      dueDate: new Date(Date.now() + 86400000).toISOString(),
      owner: 'Sarah Chen',
      action: 'Review and approve size chart update',
      metrics: [
        { label: 'Returns Prevented', value: 496 },
        { label: 'Estimated Savings', value: '$18.8K' },
        { label: 'ROI', value: '3.77x' },
        { label: 'Confidence', value: '92%' },
      ],
    },
  ],
};

// ============================================================================
// SCENARIO 2: Quality Defects
// ============================================================================
export const SCENARIO_QUALITY_DEFECTS = {
  atRiskCustomers: [],
  returns: [
    {
      id: 'RET_002',
      customerId: 'CUST_002',
      customerName: 'Jane Doe',
      productName: 'Red Jeans',
      category: 'QUALITY',
      amount: 89.99,
      classification: 'QUALITY',
      confidence: 0.92,
      roiPotential: 2.45,
      churnRisk: 0.68,
      fraudScore: 0.05,
      status: 'pending' as const,
      returnDate: new Date(Date.now() - 86400000).toISOString(),
    },
    {
      id: 'RET_012',
      customerId: 'CUST_087',
      customerName: 'Michael Brown',
      productName: 'Red Jeans',
      category: 'QUALITY',
      amount: 89.99,
      classification: 'QUALITY',
      confidence: 0.89,
      roiPotential: 2.45,
      churnRisk: 0.34,
      fraudScore: 0.03,
      status: 'pending' as const,
      returnDate: new Date(Date.now() - 172800000).toISOString(),
    },
  ],
  actionItems: [
    {
      id: 'ACT_002',
      type: 'recommendation' as const,
      title: 'Quality Audit with Supplier ABC',
      description: '892 returns in 1 week, 18% DOA rate',
      impact: 'high' as const,
      priority: 'high' as const,
      dueDate: new Date(Date.now() + 172800000).toISOString(),
      owner: 'Mike Wilson',
      action: 'Schedule supplier quality audit and implement corrective actions',
      metrics: [
        { label: 'Returns', value: 892 },
        { label: 'DOA Rate', value: '18%' },
        { label: 'Z-Score', value: '2.8σ' },
        { label: 'Savings Potential', value: '$33.8K' },
      ],
    },
  ],
};

// ============================================================================
// SCENARIO 3: Fraud Detection
// ============================================================================
export const SCENARIO_FRAUD_DETECTION = {
  atRiskCustomers: [],
  returns: [
    {
      id: 'RET_003',
      customerId: 'CUST_999',
      customerName: 'Robert Jones',
      productName: 'Premium Headphones',
      category: 'FRAUD',
      amount: 199.99,
      classification: 'FRAUD',
      confidence: 0.94,
      roiPotential: 8.5,
      churnRisk: 0.05,
      fraudScore: 0.92,
      status: 'pending' as const,
      returnDate: new Date(Date.now() - 300000).toISOString(),
    },
  ],
  actionItems: [
    {
      id: 'ACT_003',
      type: 'risk' as const,
      title: 'Suspicious Return Pattern Detected',
      description: 'Customer has returned 5 high-value items in 30 days',
      impact: 'high' as const,
      priority: 'critical' as const,
      dueDate: new Date().toISOString(),
      owner: 'Fraud Team',
      action: 'Review customer account and flag for potential fraud investigation',
      metrics: [
        { label: 'Fraud Score', value: '92%' },
        { label: 'Returns (30d)', value: 5 },
        { label: 'Total Amount', value: '$847.95' },
        { label: 'Confidence', value: '94%' },
      ],
    },
  ],
};

// ============================================================================
// SCENARIO 4: High Churn Risk - Multiple Touchpoints
// ============================================================================
export const SCENARIO_CHURN_CRITICAL = {
  returns: [],
  atRiskCustomers: [
    {
      customerId: 'CUST_12345',
      name: 'Maria Garcia',
      email: 'maria@example.com',
      phone: '(555) 123-4567',
      ltv: 2500,
      eqScore: -4.2,
      churnRisk: 0.92,
      emotionalState: 'VERY FRUSTRATED',
      returnsLast30Days: 3,
      primarySentiment: 'Customer expressed extreme frustration with multiple returns',
      sentiment: ['Anger', 'Frustration', 'Disappointment', 'Resignation'],
      lastReturn: '2 days ago',
      interventioneRecommended: 'Executive Outreach Call',
      successProbability: 0.70,
      suggestedOffer: '$50 Account Credit + Priority Support',
      suggestedMessage: 'We sincerely apologize for your experience. We\'ve reviewed your returns and want to make this right.',
    },
    {
      customerId: 'CUST_67890',
      name: 'Robert Johnson',
      email: 'robert@example.com',
      phone: '(555) 987-6543',
      ltv: 1800,
      eqScore: -3.8,
      churnRisk: 0.85,
      emotionalState: 'FRUSTRATED',
      returnsLast30Days: 2,
      primarySentiment: 'Moderate dissatisfaction, considering alternatives',
      sentiment: ['Frustration', 'Skepticism', 'Disappointment'],
      lastReturn: '5 days ago',
      interventioneRecommended: 'Personalized Email + Loyalty Offer',
      successProbability: 0.65,
      suggestedOffer: '20% off next purchase + Free Shipping',
      suggestedMessage: 'We want to earn back your trust. Here\'s a special offer just for you.',
    },
    {
      customerId: 'CUST_54321',
      name: 'Sarah Williams',
      email: 'sarah@example.com',
      phone: '(555) 456-7890',
      ltv: 3200,
      eqScore: -3.5,
      churnRisk: 0.78,
      emotionalState: 'DISAPPOINTED',
      returnsLast30Days: 2,
      primarySentiment: 'Disappointed but still engaged',
      sentiment: ['Disappointment', 'Concern', 'Hesitation'],
      lastReturn: '1 week ago',
      interventioneRecommended: 'VIP Support Offer',
      successProbability: 0.72,
      suggestedOffer: 'Complimentary Premium Support + $100 Credit',
      suggestedMessage: 'You\'ve been a valued customer. Let\'s ensure this doesn\'t happen again.',
    },
  ],
  actionItems: [
    {
      id: 'ACT_004',
      type: 'churn' as const,
      title: 'Critical Churn Risk: Maria Garcia (CUST_12345)',
      description: 'High-value customer ($2.5K LTV) at 92% churn risk',
      impact: 'high' as const,
      priority: 'critical' as const,
      dueDate: new Date().toISOString(),
      owner: 'John Doe',
      action: 'Execute executive outreach call within 24 hours',
      metrics: [
        { label: 'Customer LTV', value: '$2,500' },
        { label: 'Churn Risk', value: '92%' },
        { label: 'EQ Score', value: '-4.2' },
        { label: 'Returns (30d)', value: '3' },
      ],
    },
  ],
};

// ============================================================================
// SCENARIO 5: Trend Detection - Logistics Issues
// ============================================================================
export const SCENARIO_LOGISTICS_TREND = {
  atRiskCustomers: [],
  returns: Array.from({ length: 12 }, (_, i) => ({
    id: `RET_LOG_${i + 1}`,
    customerId: `CUST_L${i + 1}`,
    customerName: `Customer ${i + 1}`,
    productName: 'Various Products',
    category: 'LOGISTICS',
    amount: 50 + Math.random() * 100,
    classification: 'LOGISTICS',
    confidence: 0.85 + Math.random() * 0.1,
    roiPotential: 1.5 + Math.random() * 1.5,
    churnRisk: 0.2 + Math.random() * 0.3,
    fraudScore: 0.01,
    status: 'pending' as const,
    returnDate: new Date(Date.now() - Math.random() * 604800000).toISOString(),
  })),
  actionItems: [
    {
      id: 'ACT_005',
      type: 'trend' as const,
      title: 'Logistics Damage Pattern - Carrier XYZ',
      description: '567 returns in 2 weeks, 12% damage rate',
      impact: 'high' as const,
      priority: 'high' as const,
      dueDate: new Date(Date.now() + 172800000).toISOString(),
      owner: 'Supply Chain Team',
      action: 'Review packaging standards and coordinate with carrier',
      metrics: [
        { label: 'Returns', value: 567 },
        { label: 'Damage Rate', value: '12%' },
        { label: 'Z-Score', value: '2.1σ' },
        { label: 'Savings Potential', value: '$21.5K' },
      ],
    },
  ],
};

// ============================================================================
// SCENARIO 6: Mixed Returns with Different Statuses
// ============================================================================
export const SCENARIO_MIXED_RETURNS = {
  atRiskCustomers: [],
  actionItems: [],
  returns: [
    // Pending
    {
      id: 'RET_101',
      customerId: 'CUST_101',
      customerName: 'Alice Brown',
      productName: 'Winter Coat',
      category: 'SIZING',
      amount: 159.99,
      classification: 'SIZING',
      confidence: 0.88,
      roiPotential: 2.1,
      churnRisk: 0.25,
      fraudScore: 0.02,
      status: 'pending' as const,
      returnDate: new Date(Date.now() - 86400000).toISOString(),
    },
    // Approved
    {
      id: 'RET_102',
      customerId: 'CUST_102',
      customerName: 'David Lee',
      productName: 'Summer Dress',
      category: 'QUALITY',
      amount: 79.99,
      classification: 'QUALITY',
      confidence: 0.91,
      roiPotential: 3.2,
      churnRisk: 0.15,
      fraudScore: 0.01,
      status: 'approved' as const,
      returnDate: new Date(Date.now() - 172800000).toISOString(),
    },
    // Rejected
    {
      id: 'RET_103',
      customerId: 'CUST_103',
      customerName: 'Emily Chen',
      productName: 'Casual Shoes',
      category: 'OTHER',
      amount: 65.99,
      classification: 'OTHER',
      confidence: 0.45,
      roiPotential: 0.5,
      churnRisk: 0.32,
      fraudScore: 0.08,
      status: 'rejected' as const,
      returnDate: new Date(Date.now() - 259200000).toISOString(),
    },
    // Implemented
    {
      id: 'RET_104',
      customerId: 'CUST_104',
      customerName: 'Frank Miller',
      productName: 'Sports Equipment',
      category: 'DEFECTIVE',
      amount: 199.99,
      classification: 'DEFECTIVE',
      confidence: 0.97,
      roiPotential: 5.8,
      churnRisk: 0.08,
      fraudScore: 0.01,
      status: 'implemented' as const,
      returnDate: new Date(Date.now() - 604800000).toISOString(),
    },
  ],
};

// ============================================================================
// SCENARIO 7: High-Value Returns
// ============================================================================
export const SCENARIO_HIGH_VALUE = {
  atRiskCustomers: [],
  returns: [
    {
      id: 'RET_200',
      customerId: 'CUST_200',
      customerName: 'Grace Zhang',
      productName: 'Premium Electronics Bundle',
      category: 'QUALITY',
      amount: 1299.99,
      classification: 'QUALITY',
      confidence: 0.94,
      roiPotential: 12.5,
      churnRisk: 0.88,
      fraudScore: 0.03,
      status: 'pending' as const,
      returnDate: new Date(Date.now() - 43200000).toISOString(),
    },
    {
      id: 'RET_201',
      customerId: 'CUST_201',
      customerName: 'Henry Adams',
      productName: 'Designer Luggage Set',
      category: 'DEFECTIVE',
      amount: 899.99,
      classification: 'DEFECTIVE',
      confidence: 0.89,
      roiPotential: 9.3,
      churnRisk: 0.72,
      fraudScore: 0.02,
      status: 'pending' as const,
      returnDate: new Date(Date.now() - 21600000).toISOString(),
    },
  ],
  actionItems: [
    {
      id: 'ACT_006',
      type: 'recommendation' as const,
      title: 'Supplier Quality Review - High-Value Items',
      description: 'Multiple defects in premium product line',
      impact: 'high' as const,
      priority: 'critical' as const,
      dueDate: new Date().toISOString(),
      owner: 'Quality Manager',
      action: 'Urgent supplier audit for premium line',
      metrics: [
        { label: 'Total Returns Value', value: '$2,199.98' },
        { label: 'Combined ROI', value: '10.9x' },
        { label: 'Confidence', value: '91.5%' },
        { label: 'Customer LTV Risk', value: '$5,200' },
      ],
    },
  ],
};

// ============================================================================
// MAIN GENERATOR FUNCTION
// ============================================================================
export function generateDemoData(scenario: 'all' | 'sizing' | 'quality' | 'fraud' | 'churn' | 'logistics' | 'mixed' | 'highValue' | 'blackFriday' | 'international' | 'summerSales' | 'enterpriseBatch' | 'lowRisk' = 'all') {
  const scenarios = {
    sizing: SCENARIO_SIZING_ISSUE,
    quality: SCENARIO_QUALITY_DEFECTS,
    fraud: SCENARIO_FRAUD_DETECTION,
    churn: SCENARIO_CHURN_CRITICAL,
    logistics: SCENARIO_LOGISTICS_TREND,
    mixed: SCENARIO_MIXED_RETURNS,
    highValue: SCENARIO_HIGH_VALUE,
    blackFriday: SCENARIO_BLACK_FRIDAY,
    international: SCENARIO_INTERNATIONAL,
    summerSales: SCENARIO_SUMMER_SALES,
    enterpriseBatch: SCENARIO_ENTERPRISE_BATCH,
    lowRisk: SCENARIO_LOW_RISK,
  };

  if (scenario === 'all') {
    return {
      returns: [
        ...SCENARIO_SIZING_ISSUE.returns,
        ...SCENARIO_QUALITY_DEFECTS.returns,
        ...SCENARIO_FRAUD_DETECTION.returns,
        ...SCENARIO_LOGISTICS_TREND.returns,
        ...SCENARIO_MIXED_RETURNS.returns,
        ...SCENARIO_HIGH_VALUE.returns,
        ...SCENARIO_BLACK_FRIDAY.returns,
        ...SCENARIO_INTERNATIONAL.returns,
        ...SCENARIO_SUMMER_SALES.returns,
        ...SCENARIO_ENTERPRISE_BATCH.returns,
        ...SCENARIO_LOW_RISK.returns,
      ],
      atRiskCustomers: SCENARIO_CHURN_CRITICAL.atRiskCustomers,
      actionItems: [
        ...SCENARIO_SIZING_ISSUE.actionItems,
        ...SCENARIO_QUALITY_DEFECTS.actionItems,
        ...SCENARIO_FRAUD_DETECTION.actionItems,
        ...SCENARIO_CHURN_CRITICAL.actionItems,
        ...SCENARIO_LOGISTICS_TREND.actionItems,
        ...SCENARIO_HIGH_VALUE.actionItems,
      ],
    };
  }

  const selected = scenarios[scenario];
  return {
    returns: selected.returns || [],
    atRiskCustomers: selected.atRiskCustomers || SCENARIO_CHURN_CRITICAL.atRiskCustomers,
    actionItems: selected.actionItems || [],
  };
}

// ============================================================================
// HELPER FUNCTIONS
// ============================================================================

/**
 * Generate a random return ID
 */
export function generateReturnId(): string {
  const num = Math.random().toString(36).substring(2, 8).toUpperCase();
  return `RET_${num}`;
}

/**
 * Generate random customer ID
 */
export function generateCustomerId(): string {
  const num = Math.floor(Math.random() * 100000).toString().padStart(5, '0');
  return `CUST_${num}`;
}

/**
 * Generate random test returns with custom count
 */
export function generateRandomReturns(count: number = 10): Return[] {
  const categories = ['SIZING', 'QUALITY', 'DEFECTIVE', 'FRAUD', 'LOGISTICS', 'OTHER'];
  const customerNames = [
    'John Smith', 'Jane Doe', 'Robert Johnson', 'Maria Garcia',
    'Alice Brown', 'David Lee', 'Emily Chen', 'Frank Miller',
    'Grace Zhang', 'Henry Adams'
  ];
  const productNames = [
    'Blue T-Shirt', 'Red Jeans', 'Winter Coat', 'Summer Dress',
    'Casual Shoes', 'Premium Headphones', 'Designer Luggage',
    'Sports Equipment', 'Electronics Bundle'
  ];

  return Array.from({ length: count }, (_, i) => {
    const category = categories[Math.floor(Math.random() * categories.length)];
    return {
      id: generateReturnId(),
      customerId: generateCustomerId(),
      customerName: customerNames[Math.floor(Math.random() * customerNames.length)],
      productName: productNames[Math.floor(Math.random() * productNames.length)],
      category,
      amount: Math.round((30 + Math.random() * 300) * 100) / 100,
      classification: category,
      confidence: 0.8 + Math.random() * 0.19,
      roiPotential: 1 + Math.random() * 8,
      churnRisk: Math.random(),
      fraudScore: Math.random() * 0.3,
      status: (['pending', 'approved', 'rejected', 'implemented'][Math.floor(Math.random() * 4)]) as any,
      returnDate: new Date(Date.now() - Math.random() * 1209600000).toISOString(),
    };
  });
}

// ============================================================================
// SCENARIO 8: Black Friday Peak Load
// ============================================================================
export const SCENARIO_BLACK_FRIDAY = {
  atRiskCustomers: [],
  actionItems: [],
  returns: Array.from({ length: 50 }, (_, i) => ({
    id: `RET_BF_${i + 1}`,
    customerId: `CUST_BF${i + 1}`,
    customerName: `Customer ${i + 1}`,
    productName: 'Holiday Season Items',
    category: 'MIXED',
    amount: 75 + Math.random() * 150,
    classification: ['SIZING', 'QUALITY', 'OTHER'][Math.floor(Math.random() * 3)],
    confidence: 0.85 + Math.random() * 0.14,
    roiPotential: 1.5 + Math.random() * 3,
    churnRisk: 0.1 + Math.random() * 0.2,
    fraudScore: Math.random() * 0.1,
    status: 'pending' as const,
    returnDate: new Date(Date.now() - Math.random() * 86400000).toISOString(),
  })),
};

// ============================================================================
// SCENARIO 9: International Returns
// ============================================================================
export const SCENARIO_INTERNATIONAL = {
  atRiskCustomers: [],
  actionItems: [],
  returns: [
    {
      id: 'RET_INT_001',
      customerId: 'CUST_UK_001',
      customerName: 'James Wilson (UK)',
      productName: 'T-Shirt',
      category: 'SIZING',
      amount: 65.00,
      classification: 'SIZING',
      confidence: 0.93,
      roiPotential: 2.8,
      churnRisk: 0.2,
      fraudScore: 0.01,
      status: 'pending' as const,
      returnDate: new Date(Date.now() - 172800000).toISOString(),
    },
    {
      id: 'RET_INT_002',
      customerId: 'CUST_DE_001',
      customerName: 'Anna Mueller (Germany)',
      productName: 'Jeans',
      category: 'QUALITY',
      amount: 89.99,
      classification: 'QUALITY',
      confidence: 0.88,
      roiPotential: 2.2,
      churnRisk: 0.15,
      fraudScore: 0.02,
      status: 'pending' as const,
      returnDate: new Date(Date.now() - 259200000).toISOString(),
    },
    {
      id: 'RET_INT_003',
      customerId: 'CUST_JP_001',
      customerName: 'Yuki Tanaka (Japan)',
      productName: 'Electronics',
      category: 'DEFECTIVE',
      amount: 299.99,
      classification: 'DEFECTIVE',
      confidence: 0.97,
      roiPotential: 5.5,
      churnRisk: 0.08,
      fraudScore: 0.00,
      status: 'pending' as const,
      returnDate: new Date(Date.now() - 345600000).toISOString(),
    },
  ],
};

// ============================================================================
// SCENARIO 10: Seasonal Pattern - Summer Sales
// ============================================================================
export const SCENARIO_SUMMER_SALES = {
  atRiskCustomers: [],
  actionItems: [],
  returns: Array.from({ length: 25 }, (_, i) => ({
    id: `RET_SUM_${i + 1}`,
    customerId: `CUST_SUM${i + 1}`,
    customerName: `Summer Customer ${i + 1}`,
    productName: 'Summer Apparel',
    category: 'SIZING',
    amount: 30 + Math.random() * 60,
    classification: 'SIZING',
    confidence: 0.90 + Math.random() * 0.09,
    roiPotential: 2.0 + Math.random() * 2,
    churnRisk: 0.12 + Math.random() * 0.15,
    fraudScore: Math.random() * 0.05,
    status: 'pending' as const,
    returnDate: new Date(Date.now() - Math.random() * 604800000).toISOString(),
  })),
};

// ============================================================================
// SCENARIO 11: Enterprise Batch Processing
// ============================================================================
export const SCENARIO_ENTERPRISE_BATCH = {
  atRiskCustomers: [],
  actionItems: [],
  returns: Array.from({ length: 100 }, (_, i) => ({
    id: `RET_BATCH_${i + 1}`,
    customerId: `CUST_BATCH${Math.floor(i / 10) + 1}`,
    customerName: `Enterprise Customer ${Math.floor(i / 10) + 1}`,
    productName: 'Bulk Order Item',
    category: 'QUALITY',
    amount: 150 + Math.random() * 500,
    classification: 'QUALITY',
    confidence: 0.88 + Math.random() * 0.11,
    roiPotential: 3.0 + Math.random() * 4,
    churnRisk: 0.05 + Math.random() * 0.1,
    fraudScore: Math.random() * 0.02,
    status: (['pending', 'approved', 'implemented'][Math.floor(Math.random() * 3)]) as any,
    returnDate: new Date(Date.now() - Math.random() * 1209600000).toISOString(),
  })),
};

// ============================================================================
// SCENARIO 12: Low-Risk Routine Returns
// ============================================================================
export const SCENARIO_LOW_RISK = {
  atRiskCustomers: [],
  actionItems: [],
  returns: Array.from({ length: 30 }, (_, i) => ({
    id: `RET_LOW_${i + 1}`,
    customerId: `CUST_LOW${i + 1}`,
    customerName: `Low Risk Customer ${i + 1}`,
    productName: 'Standard Item',
    category: 'OTHER',
    amount: 20 + Math.random() * 40,
    classification: 'OTHER',
    confidence: 0.75 + Math.random() * 0.2,
    roiPotential: 0.5 + Math.random() * 1,
    churnRisk: 0.02 + Math.random() * 0.08,
    fraudScore: Math.random() * 0.01,
    status: (['pending', 'rejected'][Math.floor(Math.random() * 2)]) as any,
    returnDate: new Date(Date.now() - Math.random() * 1209600000).toISOString(),
  })),
};

/**
 * Export data as JSON for testing
 */
export function exportDemoData(scenario: string = 'all'): string {
  return JSON.stringify(generateDemoData(scenario as any), null, 2);
}

/**
 * Get list of all available scenarios
 */
export function getAvailableScenarios(): string[] {
  return [
    'all',
    'sizing',
    'quality',
    'fraud',
    'churn',
    'logistics',
    'mixed',
    'highValue',
    'blackFriday',
    'international',
    'summerSales',
    'enterpriseBatch',
    'lowRisk',
  ];
}

/**
 * Generate test users for different roles
 */
export const TEST_USERS = {
  csr: {
    id: 'USER_CSR_001',
    name: 'Sarah CSR',
    email: 'sarah@returniq.com',
    role: 'CSR',
    team: 'Customer Support',
  },
  manager: {
    id: 'USER_MGR_001',
    name: 'Bob Manager',
    email: 'bob@returniq.com',
    role: 'Manager',
    team: 'Operations',
  },
  leader: {
    id: 'USER_LEAD_001',
    name: 'Alice Leader',
    email: 'alice@returniq.com',
    role: 'Leadership',
    team: 'Executive',
  },
};

// ============================================================================
// DYNAMIC DATA GENERATION (for auto-refresh feature)
// ============================================================================
export const generateNewReturn = (): Return => {
  const customerNames = ['Alice Johnson', 'Bob Smith', 'Carol White', 'David Lee', 'Emma Davis', 'Frank Miller', 'Grace Chen', 'Henry Wilson'];
  const productNames = ['T-Shirt', 'Jeans', 'Shoes', 'Jacket', 'Hat', 'Socks', 'Sweater', 'Pants'];
  const classifications = ['SIZING', 'QUALITY', 'DEFECTIVE', 'FRAUD', 'LOGISTICS', 'OTHER'];
  const statuses: Array<'pending' | 'approved' | 'rejected' | 'implemented'> = ['pending', 'approved'];

  const timestamp = Date.now();
  const randomId = Math.random().toString(36).substring(7).toUpperCase();

  return {
    id: `RET_${randomId}`,
    customerId: `CUST_${Math.floor(Math.random() * 999)}`,
    customerName: customerNames[Math.floor(Math.random() * customerNames.length)],
    productName: productNames[Math.floor(Math.random() * productNames.length)],
    category: classifications[Math.floor(Math.random() * classifications.length)],
    amount: Math.round(Math.random() * 200) + 20,
    classification: classifications[Math.floor(Math.random() * classifications.length)],
    confidence: Math.round((Math.random() * 0.4 + 0.6) * 100) / 100,
    roiPotential: Math.round((Math.random() * 3 + 1) * 100) / 100,
    churnRisk: Math.round(Math.random() * 100) / 100,
    fraudScore: Math.round(Math.random() * 0.3 * 100) / 100,
    status: statuses[Math.floor(Math.random() * statuses.length)],
    returnDate: new Date(timestamp).toISOString(),
  };
};
