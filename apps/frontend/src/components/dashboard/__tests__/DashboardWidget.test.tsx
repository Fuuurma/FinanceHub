import React from 'react';
import { render, screen } from '@testing-library/react';
import { DashboardWidget } from '../DashboardWidget';
import { WidgetConfig } from '../types';

const mockWidget: WidgetConfig = {
  id: 'test-widget-1',
  type: 'chart',
  title: 'Test Chart',
  size: 'medium',
  position: { x: 0, y: 0 },
  config: { symbol: 'AAPL' },
  visible: true,
};

describe('DashboardWidget', () => {
  it('renders widget title', () => {
    render(
      <DashboardWidget
        config={mockWidget}
        onEdit={() => {}}
        onDelete={() => {}}
      />
    );
    expect(screen.getByText('Test Chart')).toBeInTheDocument();
  });

  it('shows maximize button', () => {
    render(
      <DashboardWidget
        config={mockWidget}
        onEdit={() => {}}
        onDelete={() => {}}
      />
    );
    const buttons = screen.getAllByRole('button');
    expect(buttons.length).toBeGreaterThan(0);
  });

  it('applies correct size classes for medium', () => {
    render(
      <DashboardWidget
        config={mockWidget}
        onEdit={() => {}}
        onDelete={() => {}}
      />
    );
    const card = screen.getByText('Test Chart').closest('[class*="col-span"]');
    expect(card).toHaveClass('col-span-1');
  });

  it('applies correct size classes for large', () => {
    const largeWidget = { ...mockWidget, size: 'large' as const };
    render(
      <DashboardWidget
        config={largeWidget}
        onEdit={() => {}}
        onDelete={() => {}}
      />
    );
    const card = screen.getByText('Test Chart').closest('[class*="row-span"]');
    expect(card).toHaveClass('row-span-2');
  });

  it('renders in edit mode', () => {
    render(
      <DashboardWidget
        config={mockWidget}
        onEdit={() => {}}
        onDelete={() => {}}
        isEditMode={true}
      />
    );
    expect(screen.getByText('Test Chart')).toBeInTheDocument();
  });
});
