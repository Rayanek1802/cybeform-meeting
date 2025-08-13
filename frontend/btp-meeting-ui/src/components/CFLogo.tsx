import React from 'react'

interface CFLogoProps {
  className?: string
  size?: number
}

const CFLogo: React.FC<CFLogoProps> = ({ className = '', size = 24 }) => {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 100 100"
      fill="currentColor"
      xmlns="http://www.w3.org/2000/svg"
      className={className}
    >
      {/* Logo CF moderne inspiré de votre image */}
      <g>
        {/* Lettre C stylisée */}
        <path
          d="M20 25 C20 18, 27 15, 35 15 C43 15, 50 18, 50 25 L50 35 C50 42, 43 45, 35 45 C27 45, 20 42, 20 35 L20 65 C20 72, 27 75, 35 75 C43 75, 50 72, 50 65 L50 75 C50 82, 43 85, 35 85 C27 85, 20 82, 20 75 Z"
          fill="currentColor"
        />
        
        {/* Lettre F stylisée */}
        <rect x="60" y="15" width="8" height="70" rx="4" fill="currentColor" />
        <rect x="60" y="15" width="20" height="8" rx="4" fill="currentColor" />
        <rect x="60" y="41" width="15" height="8" rx="4" fill="currentColor" />
      </g>
    </svg>
  )
}

export default CFLogo
