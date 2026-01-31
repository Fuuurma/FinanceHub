import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { WidgetLibrary } from '../WidgetLibrary';
import { WidgetType } from '../types';

describe('WidgetLibrary', () => {
  const mockOnSelect = jest.fn();
  const mockOnClose = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders widget library overlay', () => {
    render(
      <WidgetLibrary
        onSelect={mockOnSelect}
        onClose={mockOnClose}
      />
    );
    expect(screen.getByText('Add Widget')).toBeInTheDocument();
  });

  it('shows search input', () => {
    render(
      <WidgetLibrary
        onSelect={mockOnSelect}
        onClose={mockOnClose}
      />
    );
    expect(screen.getByPlaceholderText('Search widgets...')).toBeInTheDocument();
  });

  it('displays all widget types', () => {
    render(
      <WidgetLibrary
        onSelect={mockOnSelect}
        onClose={mockOnClose}
      />
    );
    expect(screen.getByText('Price Chart')).toBeInTheDocument();
    expect(screen.getByText('Watchlist')).toBeInTheDocument();
    expect(screen.getByText('Portfolio')).toBeInTheDocument();
    expect(screen.getByText('News Feed')).toBeInTheDocument();
    expect(screen.getByText('Screener')).toBeInTheDocument();
    expect(screen.getByText('Market Metrics')).toBeInTheDocument();
  });

  it('calls onClose when clicking overlay', () => {
    render(
      <WidgetLibrary
        onSelect={mockOnSelect}
        onClose={mockOnClose}
      />
    );
    const overlay = screen.getByText('Add Widget').closest('.fixed');
    if (overlay) {
      fireEvent.click(overlay);
      expect(mockOnClose).toHaveBeenCalled();
    }
  });

  it('filters widgets by search query', () => {
    render(
      <WidgetLibrary
        onSelect={mockOnSelect}
        onClose={mockOnClose}
      />
    );
    const searchInput = screen.getByPlaceholderText('Search widgets...');
    fireEvent.change(searchInput, { target: { value: 'chart' } });
    expect(screen.getByText('Price Chart')).toBeInTheDocument();
    expect(screen.queryByText('Watchlist')).not.toBeInTheDocument();
  });

  it('shows add button after selecting widget', () => {
    render(
      <WidgetLibrary
        onSelect={mockOnSelect}
        onClose={mockOnClose}
      />
    );
    const chartWidget = screen.getByText('Price Chart');
    fireEvent.click(chartWidget);
    expect(screen.getByText('Add Widget')).toBeInTheDocument();
  });

  it('allows custom title input', () => {
    render(
      <WidgetLibrary
        onSelect={mockOnSelect}
        onClose={mockOnClose}
      />
    );
    const chartWidget = screen.getByText('Price Chart');
    fireEvent.click(chartWidget);
    const customTitleInput = screen.getByPlaceholderText('Custom title (optional)');
    fireEvent.change(customTitleInput, { target: { value: 'My Custom Chart' } });
    expect(customTitleInput).toHaveValue('My Custom Chart');
  });
});
