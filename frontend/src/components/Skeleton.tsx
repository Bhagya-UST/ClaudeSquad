import React from 'react';

interface SkeletonProps {
  className?: string;
  width?: string;
  height?: string;
}

export const Skeleton: React.FC<SkeletonProps> = ({
  className = 'w-full h-8',
  width,
  height,
}) => {
  const style: React.CSSProperties = {};
  if (width) style.width = width;
  if (height) style.height = height;

  return (
    <div
      className={`${className} bg-gray-700 rounded animate-pulse`}
      style={style}
    />
  );
};

export const CardSkeleton: React.FC = () => (
  <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
    <Skeleton className="h-6 w-32 mb-4" />
    <Skeleton className="h-10 w-24 mb-2" />
    <Skeleton className="h-4 w-40" />
  </div>
);

export const ChartSkeleton: React.FC = () => (
  <div className="bg-gray-800 rounded-lg p-6 border border-gray-700 h-80">
    <Skeleton className="h-6 w-48 mb-4" />
    <div className="space-y-2">
      {[...Array(5)].map((_, i) => (
        <Skeleton key={i} className="h-12 w-full" />
      ))}
    </div>
  </div>
);
