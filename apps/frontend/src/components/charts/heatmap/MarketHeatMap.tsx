'use client';

import React, { useState, useMemo, useCallback } from 'react';
import { HeatMapNode, HeatMapLayoutNode } from './types';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from '@/components/ui/tooltip';
import { cn } from '@/lib/utils';

interface MarketHeatMapProps {
  data: HeatMapNode[];
  onNodeClick?: (node: HeatMapNode) => void;
  className?: string;
}

interface HeatMapContainerProps {
  data: HeatMapNode[];
  width: number;
  height: number;
  onNodeClick?: (node: HeatMapNode) => void;
}

const getColor = (change: number, colorScheme: 'green-red' | 'blue-orange' = 'green-red'): string => {
  const intensity = Math.min(Math.abs(change) / 5, 1);

  if (colorScheme === 'green-red') {
    if (change >= 0) {
      return `rgba(34, 197, 94, ${0.25 + intensity * 0.75})`;
    } else {
      return `rgba(239, 68, 68, ${0.25 + intensity * 0.75})`;
    }
  } else {
    if (change >= 0) {
      return `rgba(59, 130, 246, ${0.25 + intensity * 0.75})`;
    } else {
      return `rgba(249, 115, 22, ${0.25 + intensity * 0.75})`;
    }
  }
};

const calculateTreemapLayout = (
  nodes: HeatMapNode[],
  containerWidth: number,
  containerHeight: number
): HeatMapLayoutNode[] => {
  if (nodes.length === 0) return [];

  const totalValue = nodes.reduce((sum, node) => sum + node.value, 0);
  if (totalValue === 0) return [];

  const sortedNodes = [...nodes].sort((a, b) => b.value - a.value);
  const layout: HeatMapLayoutNode[] = [];

  const area = containerWidth * containerHeight;

  const squarify = (
    children: HeatMapNode[],
    x: number,
    y: number,
    width: number,
    height: number
  ): void => {
    if (children.length === 0) return;

    if (children.length === 1) {
      layout.push({
        node: children[0],
        x,
        y,
        width,
        height
      });
      return;
    }

    const longerSide = width > height ? height : width;
    let row: Array<{ node: HeatMapNode; area: number }> = [];
    let rowArea = 0;

    for (let i = 0; i < children.length; i++) {
      const child = children[i];
      const childArea = (child.value / totalValue) * area;
      
      if (row.length === 0) {
        row.push({ node: child, area: childArea });
        rowArea = childArea;
        continue;
      }

      const testRow = [...row, { node: child, area: childArea }];
      const testRowArea = testRow.reduce((sum, item) => sum + item.area, 0);
      
      const worstRatio = Math.max(
        (longerSide * longerSide) / (testRowArea / testRow.length),
        (testRowArea / (longerSide * longerSide)) * testRow.length
      );

      const currentWorstRatio = Math.max(
        (longerSide * longerSide) / (rowArea / row.length),
        (rowArea / (longerSide * longerSide)) * row.length
      );

      if (worstRatio >= currentWorstRatio || row.length === testRow.length - 1) {
        const remainingWidth = width - x;
        const remainingHeight = height - y;
        const isHorizontal = remainingWidth >= remainingHeight;

        if (isHorizontal) {
          const rowLength = remainingWidth * (rowArea / (rowArea + childArea));
          const colHeight = remainingHeight;
          
          let posX = x;
          for (const item of row) {
            const boxWidth = (item.area / rowArea) * rowLength;
            layout.push({
              node: item.node,
              x: posX,
              y,
              width: boxWidth,
              height: colHeight
            });
            posX += boxWidth;
          }
          
          const remainingChildren = children.slice(row.length);
          squarify(remainingChildren, x + rowLength, y, width - rowLength, height);
          return;
        } else {
          const rowLength = remainingHeight * (rowArea / (rowArea + childArea));
          const colWidth = remainingWidth;
          
          let posY = y;
          for (const item of row) {
            const boxHeight = (item.area / rowArea) * rowLength;
            layout.push({
              node: item.node,
              x,
              y: posY,
              width: colWidth,
              height: boxHeight
            });
            posY += boxHeight;
          }
          
          const remainingChildren = children.slice(row.length);
          squarify(remainingChildren, x, y + rowLength, width, height - rowLength);
          return;
        }
      } else {
        row = testRow;
        rowArea = testRowArea;
      }
    }
  };

  squarify(sortedNodes, 0, 0, containerWidth, containerHeight);
  return layout;
};

const HeatMapNodeComponent = ({
  layoutNode,
  onClick,
  colorScheme,
}: {
  layoutNode: HeatMapLayoutNode;
  onClick?: (node: HeatMapNode) => void;
  colorScheme: 'green-red' | 'blue-orange';
}) => {
  const { node, x, y, width, height } = layoutNode;
  const [isHovered, setIsHovered] = useState(false);

  const fontSize = Math.min(width, height) / 6;
  const changeFontSize = fontSize * 0.6;

  const canShowLabel = width > 40 && height > 30;
  const canShowChange = width > 30 && height > 20;

  return (
    <Tooltip>
      <TooltipTrigger asChild>
        <g
          onClick={() => onClick?.(node)}
          className="cursor-pointer transition-all duration-150"
          onMouseEnter={() => setIsHovered(true)}
          onMouseLeave={() => setIsHovered(false)}
          style={{ transformOrigin: 'center' }}
        >
          <rect
            x={x}
            y={y}
            width={width}
            height={height}
            fill={getColor(node.change, colorScheme)}
            stroke={isHovered ? '#fff' : 'rgba(255,255,255,0.3)'}
            strokeWidth={isHovered ? 3 : 1}
            rx={2}
          />
          {canShowLabel && (
            <text
              x={x + width / 2}
              y={y + height / 2 - (canShowChange ? changeFontSize : 0)}
              textAnchor="middle"
              dominantBaseline="middle"
              fill="#fff"
              fontSize={fontSize}
              fontWeight="600"
              style={{
                textShadow: '0 1px 2px rgba(0,0,0,0.5)',
                pointerEvents: 'none',
              }}
            >
              {node.name.length > 10 ? node.name.substring(0, 8) + '...' : node.name}
            </text>
          )}
          {canShowChange && (
            <text
              x={x + width / 2}
              y={y + height / 2 + (canShowLabel ? fontSize : 0)}
              textAnchor="middle"
              dominantBaseline="middle"
              fill="#fff"
              fontSize={changeFontSize}
              fontWeight="500"
              style={{
                textShadow: '0 1px 2px rgba(0,0,0,0.5)',
                pointerEvents: 'none',
              }}
            >
              {node.change >= 0 ? '+' : ''}{node.change.toFixed(2)}%
            </text>
          )}
        </g>
      </TooltipTrigger>
      <TooltipContent className="bg-popover border shadow-lg">
        <div className="space-y-1.5 p-1">
          <div className="flex items-center gap-2">
            <span className="font-semibold">{node.name}</span>
            {node.symbol && (
              <Badge variant="outline" className="text-xs">
                {node.symbol}
              </Badge>
            )}
          </div>
          <div className="grid grid-cols-2 gap-x-4 text-sm">
            <div>
              <span className="text-muted-foreground">Change: </span>
              <span className={cn(
                'font-medium',
                node.change >= 0 ? 'text-green-500' : 'text-red-500'
              )}>
                {node.change >= 0 ? '+' : ''}{node.change.toFixed(2)}%
              </span>
            </div>
            <div>
              <span className="text-muted-foreground">Value: </span>
              <span className="font-medium">
                ${(node.value / 1000000).toFixed(1)}M
              </span>
            </div>
            {node.type === 'sector' && (
              <>
                <div>
                  <span className="text-muted-foreground">Gain/Loss: </span>
                  <span className={cn(
                    'font-medium',
                    node.changeAmount >= 0 ? 'text-green-500' : 'text-red-500'
                  )}>
                    {node.changeAmount >= 0 ? '+' : ''}${Math.abs(node.changeAmount / 1000000).toFixed(1)}M
                  </span>
                </div>
                <div>
                  <span className="text-muted-foreground">Type: </span>
                  <span className="font-medium capitalize">{node.type}</span>
                </div>
              </>
            )}
          </div>
        </div>
      </TooltipContent>
    </Tooltip>
  );
};

const HeatMapContainer = ({ data, width, height, onNodeClick }: HeatMapContainerProps) => {
  const layout = useMemo(() => {
    return calculateTreemapLayout(data, width, height);
  }, [data, width, height]);

  return (
    <svg width="100%" height="100%" viewBox={`0 0 ${width} ${height}`} preserveAspectRatio="xMidYMid meet">
      <TooltipProvider>
        {layout.map((layoutNode) => (
          <HeatMapNodeComponent
            key={layoutNode.node.id}
            layoutNode={layoutNode}
            onClick={onNodeClick}
            colorScheme="green-red"
          />
        ))}
      </TooltipProvider>
    </svg>
  );
};

export function MarketHeatMap({ data, onNodeClick, className }: MarketHeatMapProps) {
  const [hoveredNode, setHoveredNode] = useState<HeatMapNode | null>(null);

  const handleNodeClick = useCallback((node: HeatMapNode) => {
    if (node.children && node.children.length > 0) {
      setHoveredNode(node);
    }
    onNodeClick?.(node);
  }, [onNodeClick]);

  const displayData = hoveredNode?.children && hoveredNode.children.length > 0
    ? hoveredNode.children
    : data;

  const handleBack = () => {
    setHoveredNode(null);
  };

  return (
    <Card className={cn('w-full', className)}>
      <CardHeader className="pb-2">
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center gap-2">
            Market Heat Map
            {hoveredNode && (
              <Badge variant="secondary" className="cursor-pointer" onClick={handleBack}>
                ← Back to Sectors
              </Badge>
            )}
          </CardTitle>
          <div className="flex items-center gap-2 text-sm">
            <span className="text-green-500">▲ Gainers</span>
            <span className="text-red-500">▼ Losers</span>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <div
          className="relative w-full"
          style={{ height: '600px' }}
        >
          {data.length === 0 ? (
            <div className="flex items-center justify-center h-full text-muted-foreground">
              No data available
            </div>
          ) : (
            <HeatMapContainer
              data={displayData}
              width={1000}
              height={600}
              onNodeClick={handleNodeClick}
            />
          )}
        </div>
        {hoveredNode && (
          <div className="mt-2 text-sm text-muted-foreground text-center">
            Viewing: {hoveredNode.name} stocks ({hoveredNode.children?.length || 0} holdings)
          </div>
        )}
      </CardContent>
    </Card>
  );
}
