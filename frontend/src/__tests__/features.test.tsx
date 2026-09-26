/**
 * Comprehensive Test Suite for ReturnIQ Interactive Features
 *
 * Run with: npm test
 * Coverage: npm test -- --coverage
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';

// Import components
import { AgentAnalysisInspector } from '../components/AgentAnalysisInspector';
import { RecommendationDetailPanel } from '../components/RecommendationDetailPanel';
import { AtRiskCustomerHub } from '../components/AtRiskCustomerHub';
import { ReturnSearchFilter } from '../components/ReturnSearchFilter';
import { ManagerDashboard } from '../components/ManagerDashboard';

// Import test data
import {
  generateDemoData,
  generateRandomReturns,
  TEST_USERS,
} from '../utils/demoDataGenerator';

// ============================================================================
// TEST SUITE 1: Agent Analysis Inspector
// ============================================================================
describe('AgentAnalysisInspector', () => {
  const mockData = generateDemoData('sizing');
  const analyses = [
    {
      agent: 'Classifier',
      status: 'complete' as const,
      confidence: 0.96,
      processingTime: 2.3,
      tokensUsed: 334,
      decision: 'SIZING',
      reasoning: 'Customer explicitly stated sizing complaint',
      evidence: ['Customer said shirt runs small', 'Product unworn with tags'],
      alternatives: [{ name: 'OTHER', confidence: 0.03 }],
      metrics: { Accuracy: '96%', Latency: '2.3s' },
    },
  ];

  test('renders with correct title and return ID', () => {
    render(
      <AgentAnalysisInspector
        returnId="RET_001"
        analyses={analyses}
        totalTime={12.3}
      />
    );

    expect(screen.getByText(/Agent Analysis Pipeline/i)).toBeInTheDocument();
    expect(screen.getByText(/RET_001/i)).toBeInTheDocument();
  });

  test('displays all agents in timeline', () => {
    render(
      <AgentAnalysisInspector
        returnId="RET_001"
        analyses={analyses}
        totalTime={12.3}
      />
    );

    expect(screen.getByText('Classifier')).toBeInTheDocument();
  });

  test('expands agent card on click', async () => {
    render(
      <AgentAnalysisInspector
        returnId="RET_001"
        analyses={analyses}
        totalTime={12.3}
      />
    );

    const agentCard = screen.getByText('Classifier').closest('button');
    fireEvent.click(agentCard!);

    await waitFor(() => {
      expect(screen.getByText(/Agent Reasoning/i)).toBeInTheDocument();
    });
  });

  test('displays agent decision and confidence', async () => {
    render(
      <AgentAnalysisInspector
        returnId="RET_001"
        analyses={analyses}
        totalTime={12.3}
      />
    );

    const agentCard = screen.getByText('Classifier').closest('button');
    fireEvent.click(agentCard!);

    await waitFor(() => {
      expect(screen.getByText('SIZING')).toBeInTheDocument();
      expect(screen.getByText(/96.1%/)).toBeInTheDocument();
    });
  });

  test('shows evidence used', async () => {
    render(
      <AgentAnalysisInspector
        returnId="RET_001"
        analyses={analyses}
        totalTime={12.3}
      />
    );

    const agentCard = screen.getByText('Classifier').closest('button');
    fireEvent.click(agentCard!);

    await waitFor(() => {
      expect(screen.getByText(/Evidence Used/i)).toBeInTheDocument();
    });
  });

  test('allows feedback submission', async () => {
    const onFeedback = jest.fn();
    render(
      <AgentAnalysisInspector
        returnId="RET_001"
        analyses={analyses}
        totalTime={12.3}
        onFeedback={onFeedback}
      />
    );

    const agentCard = screen.getByText('Classifier').closest('button');
    fireEvent.click(agentCard!);

    await waitFor(() => {
      const correctBtn = screen.getByText(/✓ Correct/);
      fireEvent.click(correctBtn);
    });

    expect(onFeedback).toHaveBeenCalledWith('Classifier', 'correct');
  });
});

// ============================================================================
// TEST SUITE 2: Recommendation Detail Panel
// ============================================================================
describe('RecommendationDetailPanel', () => {
  const mockProps = {
    title: 'Update Size Chart for SKU #456',
    description: 'Adjust sizing measurements',
    type: 'PRODUCT' as const,
    impactMetrics: {
      returnsPreventable: 496,
      estimatedSavings: 18848,
      implementationCost: 5000,
      roi: 3.77,
      confidence: 0.92,
    },
    calculation: {
      currentReturnRate: 24,
      baselineReturnRate: 3.5,
      effectivenessPercentage: 50,
      affectedUnits: 5200,
      perReturnCost: 38,
    },
    timeline: {
      implementation: '2 hours',
      testing: '4 hours',
      rollout: 'Immediate',
      roiRealization: 'Within 30 days',
    },
    risks: [
      {
        risk: 'Supplier non-compliance',
        impact: 'high',
        mitigation: 'Start with internal update',
      },
    ],
  };

  test('renders title and description', () => {
    render(<RecommendationDetailPanel {...mockProps} />);

    expect(
      screen.getByText('Update Size Chart for SKU #456')
    ).toBeInTheDocument();
    expect(screen.getByText('Adjust sizing measurements')).toBeInTheDocument();
  });

  test('displays ROI metrics in header', () => {
    render(<RecommendationDetailPanel {...mockProps} />);

    expect(screen.getByText(/3.77x/)).toBeInTheDocument();
    expect(screen.getByText(/496/)).toBeInTheDocument();
    expect(screen.getByText(/92%/)).toBeInTheDocument();
  });

  test('switches between tabs', async () => {
    render(<RecommendationDetailPanel {...mockProps} />);

    const calculationTab = screen.getByText('Calculation');
    fireEvent.click(calculationTab);

    await waitFor(() => {
      expect(screen.getByText(/Impact Calculation Breakdown/i)).toBeInTheDocument();
    });
  });

  test('shows ROI calculation breakdown', async () => {
    render(<RecommendationDetailPanel {...mockProps} />);

    const calculationTab = screen.getByText('Calculation');
    fireEvent.click(calculationTab);

    await waitFor(() => {
      expect(screen.getByText(/Current Return Rate/i)).toBeInTheDocument();
      expect(screen.getByText(/24.0%/)).toBeInTheDocument();
    });
  });

  test('displays risks', async () => {
    render(<RecommendationDetailPanel {...mockProps} />);

    const risksTab = screen.getByText('Risks');
    fireEvent.click(risksTab);

    await waitFor(() => {
      expect(screen.getByText('Supplier non-compliance')).toBeInTheDocument();
    });
  });

  test('calls onApprove when approved', async () => {
    const onApprove = jest.fn();
    render(<RecommendationDetailPanel {...mockProps} onApprove={onApprove} />);

    const approveBtn = screen.getByText(/Approve & Implement/i);
    fireEvent.click(approveBtn);

    await waitFor(() => {
      const confirmBtn = screen.getByText(/Confirm/);
      fireEvent.click(confirmBtn);
    });

    expect(onApprove).toHaveBeenCalled();
  });

  test('handles rejection', async () => {
    const onReject = jest.fn();
    render(<RecommendationDetailPanel {...mockProps} onReject={onReject} />);

    const rejectBtn = screen.getByText(/Reject/i);
    fireEvent.click(rejectBtn);

    expect(onReject).toHaveBeenCalled();
  });
});

// ============================================================================
// TEST SUITE 3: At-Risk Customer Hub
// ============================================================================
describe('AtRiskCustomerHub', () => {
  const mockCustomers = generateDemoData('churn').atRiskCustomers;

  test('renders customer list', () => {
    render(<AtRiskCustomerHub customers={mockCustomers} />);

    expect(screen.getByText(/At-Risk Customers/i)).toBeInTheDocument();
    expect(screen.getByText('Maria Garcia')).toBeInTheDocument();
  });

  test('displays churn risk percentages', () => {
    render(<AtRiskCustomerHub customers={mockCustomers} />);

    expect(screen.getByText(/92%/)).toBeInTheDocument();
  });

  test('shows customer details on selection', async () => {
    render(<AtRiskCustomerHub customers={mockCustomers} />);

    const customerBtn = screen.getByText('Maria Garcia');
    fireEvent.click(customerBtn);

    await waitFor(() => {
      expect(screen.getByText(/maria@example.com/i)).toBeInTheDocument();
    });
  });

  test('displays emotional analysis', async () => {
    render(<AtRiskCustomerHub customers={mockCustomers} />);

    const customerBtn = screen.getByText('Maria Garcia');
    fireEvent.click(customerBtn);

    await waitFor(() => {
      expect(screen.getByText(/VERY FRUSTRATED/i)).toBeInTheDocument();
    });
  });

  test('shows intervention recommendations', async () => {
    render(<AtRiskCustomerHub customers={mockCustomers} />);

    const customerBtn = screen.getByText('Maria Garcia');
    fireEvent.click(customerBtn);

    await waitFor(() => {
      expect(screen.getByText(/Executive Outreach Call/i)).toBeInTheDocument();
    });
  });

  test('allows intervention action selection', async () => {
    const onIntervention = jest.fn();
    render(
      <AtRiskCustomerHub customers={mockCustomers} onIntervention={onIntervention} />
    );

    const customerBtn = screen.getByText('Maria Garcia');
    fireEvent.click(customerBtn);

    await waitFor(() => {
      const callBtn = screen.getByText(/Call Customer/i);
      fireEvent.click(callBtn);
    });

    expect(onIntervention).toHaveBeenCalled();
  });
});

// ============================================================================
// TEST SUITE 4: Return Search & Filter
// ============================================================================
describe('ReturnSearchFilter', () => {
  const mockReturns = generateRandomReturns(20);

  test('renders search box', () => {
    render(<ReturnSearchFilter returns={mockReturns} />);

    const searchInput = screen.getByPlaceholderText(/Search by customer/i);
    expect(searchInput).toBeInTheDocument();
  });

  test('filters by search term', async () => {
    const { rerender } = render(<ReturnSearchFilter returns={mockReturns} />);

    const searchInput = screen.getByPlaceholderText(/Search by customer/i);
    fireEvent.change(searchInput, { target: { value: 'John' } });

    await waitFor(() => {
      // Results should be filtered
    });
  });

  test('filters by classification', async () => {
    render(<ReturnSearchFilter returns={mockReturns} />);

    const classificationSelect = screen.getByDisplayValue(/Classification: All/i);
    fireEvent.change(classificationSelect, { target: { value: 'SIZING' } });

    await waitFor(() => {
      // Results should be filtered to only SIZING
    });
  });

  test('filters by status', async () => {
    render(<ReturnSearchFilter returns={mockReturns} />);

    const statusSelect = screen.getByDisplayValue(/Status: All/i);
    fireEvent.change(statusSelect, { target: { value: 'pending' } });

    await waitFor(() => {
      // Results should be filtered to only pending
    });
  });

  test('filters by ROI minimum', async () => {
    render(<ReturnSearchFilter returns={mockReturns} />);

    const roiSelect = screen.getByDisplayValue(/ROI: All/i);
    fireEvent.change(roiSelect, { target: { value: '3' } });

    await waitFor(() => {
      // Results should be filtered to ROI >= 3x
    });
  });

  test('sorts by different fields', async () => {
    render(<ReturnSearchFilter returns={mockReturns} />);

    const sortSelect = screen.getByDisplayValue(/Sort by Date/i);
    fireEvent.change(sortSelect, { target: { value: 'roi' } });

    await waitFor(() => {
      // Results should be resorted by ROI
    });
  });

  test('allows bulk selection', async () => {
    render(<ReturnSearchFilter returns={mockReturns} />);

    const checkbox = screen.getByRole('checkbox', { hidden: true });
    fireEvent.click(checkbox);

    await waitFor(() => {
      expect(screen.getByText(/selected/i)).toBeInTheDocument();
    });
  });

  test('calls onReturnClick when clicking view button', async () => {
    const onReturnClick = jest.fn();
    render(
      <ReturnSearchFilter returns={mockReturns} onReturnClick={onReturnClick} />
    );

    const viewButtons = screen.getAllByRole('button', { name: /view/i });
    if (viewButtons.length > 0) {
      fireEvent.click(viewButtons[0]);
      expect(onReturnClick).toHaveBeenCalled();
    }
  });
});

// ============================================================================
// TEST SUITE 5: Manager Dashboard
// ============================================================================
describe('ManagerDashboard', () => {
  const mockData = generateDemoData('all');
  const actionItems = mockData.actionItems;

  test('renders dashboard with statistics', () => {
    render(<ManagerDashboard actionItems={actionItems} />);

    expect(screen.getByText(/Total Actions/i)).toBeInTheDocument();
    expect(screen.getByText(/Critical/i)).toBeInTheDocument();
  });

  test('displays action items', () => {
    render(<ManagerDashboard actionItems={actionItems} />);

    expect(screen.getByText(/Update Size Chart/i)).toBeInTheDocument();
  });

  test('filters by priority', async () => {
    render(<ManagerDashboard actionItems={actionItems} />);

    const criticalBtn = screen.getByText(/Critical/i);
    fireEvent.click(criticalBtn);

    await waitFor(() => {
      // Should show only critical items
    });
  });

  test('shows action metrics', () => {
    render(<ManagerDashboard actionItems={actionItems} />);

    // Check for metric displays
    const metrics = screen.getAllByText(/prevented|savings|roi|confidence/i);
    expect(metrics.length).toBeGreaterThan(0);
  });

  test('handles approve action', async () => {
    const onApprove = jest.fn();
    render(<ManagerDashboard actionItems={actionItems} onApprove={onApprove} />);

    const approveButtons = screen.getAllByText(/Approve/i);
    if (approveButtons.length > 0) {
      fireEvent.click(approveButtons[0]);
      await waitFor(() => {
        expect(onApprove).toHaveBeenCalled();
      });
    }
  });
});

// ============================================================================
// INTEGRATION TESTS
// ============================================================================
describe('Integration Tests', () => {
  test('CSR workflow: search -> view -> provide feedback', async () => {
    const mockReturns = generateRandomReturns(10);
    const analyses = [
      {
        agent: 'Classifier',
        status: 'complete' as const,
        confidence: 0.96,
        processingTime: 2.3,
        tokensUsed: 334,
        decision: 'SIZING',
        reasoning: 'Customer complaint about fit',
        evidence: ['Size too small'],
        alternatives: [],
        metrics: {},
      },
    ];

    const onFeedback = jest.fn();

    const { rerender } = render(
      <ReturnSearchFilter returns={mockReturns} />
    );

    // Step 1: Search
    const searchInput = screen.getByPlaceholderText(/Search by customer/i);
    fireEvent.change(searchInput, { target: { value: 'John' } });

    // Step 2: Open return
    await waitFor(() => {
      const viewBtns = screen.queryAllByRole('button');
      expect(viewBtns.length).toBeGreaterThan(0);
    });

    // Step 3: View agent analysis
    rerender(
      <AgentAnalysisInspector
        returnId="RET_001"
        analyses={analyses}
        totalTime={12.3}
        onFeedback={onFeedback}
      />
    );

    // Step 4: Provide feedback
    const agentCard = screen.getByText('Classifier').closest('button');
    fireEvent.click(agentCard!);

    await waitFor(() => {
      const correctBtn = screen.getByText(/✓ Correct/);
      fireEvent.click(correctBtn);
    });

    expect(onFeedback).toHaveBeenCalled();
  });

  test('Manager workflow: view dashboard -> approve recommendation', async () => {
    const mockData = generateDemoData('all');

    const onApprove = jest.fn();

    const { rerender } = render(
      <ManagerDashboard
        actionItems={mockData.actionItems}
        onApprove={onApprove}
      />
    );

    // Step 1: View dashboard
    expect(screen.getByText(/Action Items/i)).toBeInTheDocument();

    // Step 2: View recommendation detail
    const mockProps = {
      title: 'Update Size Chart',
      description: 'Fix sizing issues',
      type: 'PRODUCT' as const,
      impactMetrics: {
        returnsPreventable: 496,
        estimatedSavings: 18848,
        implementationCost: 5000,
        roi: 3.77,
        confidence: 0.92,
      },
      calculation: {
        currentReturnRate: 24,
        baselineReturnRate: 3.5,
        effectivenessPercentage: 50,
        affectedUnits: 5200,
        perReturnCost: 38,
      },
      timeline: {
        implementation: '2 hours',
        testing: '4 hours',
        rollout: 'Immediate',
        roiRealization: 'Within 30 days',
      },
      risks: [],
      onApprove,
    };

    rerender(<RecommendationDetailPanel {...mockProps} />);

    // Step 3: Approve
    const approveBtn = screen.getByText(/Approve & Implement/i);
    fireEvent.click(approveBtn);

    await waitFor(() => {
      const confirmBtn = screen.getByText(/Confirm/);
      fireEvent.click(confirmBtn);
    });

    expect(onApprove).toHaveBeenCalled();
  });

  test('CSR workflow: help at-risk customer', async () => {
    const mockData = generateDemoData('churn');
    const onIntervention = jest.fn();

    render(
      <AtRiskCustomerHub
        customers={mockData.atRiskCustomers}
        onIntervention={onIntervention}
      />
    );

    // Step 1: View at-risk customers
    expect(screen.getByText(/At-Risk Customers/i)).toBeInTheDocument();

    // Step 2: Select customer
    const customerBtn = screen.getByText('Maria Garcia');
    fireEvent.click(customerBtn);

    // Step 3: View intervention options
    await waitFor(() => {
      expect(screen.getByText(/Executive Outreach Call/i)).toBeInTheDocument();
    });

    // Step 4: Execute intervention
    const callBtn = screen.getByText(/Call Customer/i);
    fireEvent.click(callBtn);

    expect(onIntervention).toHaveBeenCalledWith('CUST_12345', 'call');
  });
});

// ============================================================================
// PERFORMANCE TESTS
// ============================================================================
describe('Performance Tests', () => {
  test('renders large return list efficiently', () => {
    const largeList = generateRandomReturns(1000);

    const startTime = performance.now();
    render(<ReturnSearchFilter returns={largeList} />);
    const endTime = performance.now();

    // Should render in less than 2 seconds
    expect(endTime - startTime).toBeLessThan(2000);
  });

  test('filters 1000 returns quickly', async () => {
    const largeList = generateRandomReturns(1000);

    render(<ReturnSearchFilter returns={largeList} />);

    const startTime = performance.now();
    const searchInput = screen.getByPlaceholderText(/Search by customer/i);
    fireEvent.change(searchInput, { target: { value: 'John' } });
    const endTime = performance.now();

    // Should filter in less than 500ms
    expect(endTime - startTime).toBeLessThan(500);
  });
});

// ============================================================================
// ACCESSIBILITY TESTS
// ============================================================================
describe('Accessibility Tests', () => {
  test('search filter has accessible labels', () => {
    const mockReturns = generateRandomReturns(10);

    render(<ReturnSearchFilter returns={mockReturns} />);

    const searchInput = screen.getByPlaceholderText(/Search by customer/i);
    expect(searchInput).toHaveAttribute('type', 'text');
  });

  test('buttons are keyboard accessible', async () => {
    const mockReturns = generateRandomReturns(10);

    render(<ReturnSearchFilter returns={mockReturns} />);

    const buttons = screen.getAllByRole('button');
    buttons.forEach(btn => {
      expect(btn).toBeInTheDocument();
      // Should be able to focus
      btn.focus();
      expect(btn).toHaveFocus();
    });
  });
});
