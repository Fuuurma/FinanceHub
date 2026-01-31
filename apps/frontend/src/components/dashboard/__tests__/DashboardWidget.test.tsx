import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
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
    const maximizeBtn = screen.getByRole('button', { name: /maximize/i });
    expect(maximizeBtn).toBeInTheDocument();
  });

  it('calls onDelete when delete button clicked', () => {
    const onDelete = jest.fn();
    render(
      <DashboardWidget
        config={mockWidget}
        onEdit={() => {}}
        onDelete={onDelete}
        isEditMode={true}
      />
    );
    const deleteBtn = screen.getByRole('button', { name: /delete/i });
    fireEvent.click(deleteBtn);
    expect(onDelete).toHaveBeenCalledWith('test-widget-1');
  });

  it('applies correct size classes for medium', () => {
    render(
      <DashboardWidget
        config={mockWidget}
        onEdit={() => {}}
        onDelete={() => {}}
      />
    );
    const card = screen.getByRole('article');
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
    const card = screen.getByRole('article');
    expect(card).toHaveClass('row-span-2');
  });

  it('shows resize menu in edit mode', () => {
    render(
      <DashboardWidget
        config={mockWidget}
        onEdit={() => {}}
        onDelete={() => {}}
        onResize={() => {}}
        isEditMode={true}
      />
    );
    const settingsBtn = screen.getByRole('button', { name: /settings/i });
    expect(settingsBtn).toBeInTheDocument();
  });
});
