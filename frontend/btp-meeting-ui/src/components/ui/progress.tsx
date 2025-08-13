import * as React from "react"
import { cn } from '../../lib/utils'

interface ProgressProps extends React.HTMLAttributes<HTMLDivElement> {
  value?: number
  max?: number
  showLabel?: boolean
  size?: 'sm' | 'default' | 'lg'
  variant?: 'default' | 'success' | 'warning' | 'danger'
}

const Progress = React.forwardRef<HTMLDivElement, ProgressProps>(
  ({ className, value = 0, max = 100, showLabel = false, size = 'default', variant = 'default', ...props }, ref) => {
    const percentage = Math.min(Math.max((value / max) * 100, 0), 100)
    
    const sizeClasses = {
      sm: 'h-2',
      default: 'h-3',
      lg: 'h-4'
    }
    
    const variantClasses = {
      default: 'bg-brand-primary',
      success: 'bg-brand-success',
      warning: 'bg-brand-warning',
      danger: 'bg-brand-danger'
    }
    
    return (
      <div className="w-full">
        {showLabel && (
          <div className="flex justify-between text-sm text-muted-foreground mb-2">
            <span>Progression</span>
            <span>{Math.round(percentage)}%</span>
          </div>
        )}
        <div
          ref={ref}
          className={cn(
            "relative w-full overflow-hidden rounded-full bg-secondary",
            sizeClasses[size],
            className
          )}
          {...props}
        >
          <div
            className={cn(
              "h-full transition-all duration-300 ease-in-out",
              variantClasses[variant]
            )}
            style={{ width: `${percentage}%` }}
          />
        </div>
      </div>
    )
  }
)
Progress.displayName = "Progress"

export { Progress }
