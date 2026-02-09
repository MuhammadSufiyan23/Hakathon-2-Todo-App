import { cn } from '@/lib/utils';

interface SkeletonLoaderProps extends React.HTMLAttributes<HTMLDivElement> {
  className?: string;
  count?: number;
}

export function SkeletonLoader({
  className,
  count = 1,
  ...props
}: SkeletonLoaderProps) {
  return (
    <>
      {Array.from({ length: count }).map((_, index) => (
        <div
          key={index}
          className={cn(
            'animate-pulse-custom rounded-md bg-muted',
            className
          )}
          {...props}
        />
      ))}
    </>
  );
}