import React from 'react';

export type PlatformType = 'all' | 'google-meet' | 'zoom' | 'teams' | 'unknown' | string;

export interface PlatformIconProps {
  platform: PlatformType;
  size?: 'xs' | 'sm' | 'md' | 'lg' | 'xl' | number;
  className?: string;
  showGlow?: boolean;
}

export const PlatformIcon: React.FC<PlatformIconProps> = ({
  platform,
  size = 'md',
  className = '',
  showGlow = true,
}) => {
  const normalized = platform.toLowerCase().trim();

  // Pixel mapping for standard sizes
  const pixelSize =
    typeof size === 'number'
      ? size
      : size === 'xs'
      ? 16
      : size === 'sm'
      ? 20
      : size === 'md'
      ? 28
      : size === 'lg'
      ? 36
      : 44; // 'xl'

  // Generate unique IDs for SVG gradients & filters to avoid DOM ID collisions
  const uid = React.useId().replace(/:/g, '_');

  // GOOGLE MEET 3D ICON
  if (normalized === 'google-meet' || normalized === 'google' || normalized === 'meet') {
    return (
      <svg
        width={pixelSize}
        height={pixelSize}
        viewBox="0 0 48 48"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
        className={`inline-block shrink-0 transition-transform hover:scale-105 ${className}`}
        style={{
          filter: showGlow ? 'drop-shadow(0 4px 8px rgba(16, 185, 129, 0.35))' : undefined,
        }}
        aria-label="Google Meet 3D"
        role="img"
      >
        <defs>
          {/* Ambient Ground Shadow */}
          <radialGradient id={`${uid}_gmeet_shadow`} cx="50%" cy="50%" r="50%">
            <stop offset="0%" stopColor="#0F9D58" stopOpacity="0.4" />
            <stop offset="100%" stopColor="#0F9D58" stopOpacity="0" />
          </radialGradient>

          {/* Green Camera Body 3D Gradient */}
          <linearGradient id={`${uid}_gmeet_green`} x1="12" y1="12" x2="32" y2="36" gradientUnits="userSpaceOnUse">
            <stop offset="0%" stopColor="#34D399" />
            <stop offset="25%" stopColor="#10B981" />
            <stop offset="100%" stopColor="#047857" />
          </linearGradient>

          {/* Blue Projection Cone 3D Gradient */}
          <linearGradient id={`${uid}_gmeet_blue`} x1="28" y1="14" x2="44" y2="34" gradientUnits="userSpaceOnUse">
            <stop offset="0%" stopColor="#60A5FA" />
            <stop offset="40%" stopColor="#2563EB" />
            <stop offset="100%" stopColor="#1D4ED8" />
          </linearGradient>

          {/* Yellow Corner Facet 3D Gradient */}
          <linearGradient id={`${uid}_gmeet_yellow`} x1="8" y1="28" x2="18" y2="38" gradientUnits="userSpaceOnUse">
            <stop offset="0%" stopColor="#FCD34D" />
            <stop offset="100%" stopColor="#F59E0B" />
          </linearGradient>

          {/* Red Accent Facet 3D Gradient */}
          <linearGradient id={`${uid}_gmeet_red`} x1="18" y1="28" x2="28" y2="38" gradientUnits="userSpaceOnUse">
            <stop offset="0%" stopColor="#F87171" />
            <stop offset="100%" stopColor="#DC2626" />
          </linearGradient>

          {/* Glossy Top Glass Bevel Reflection */}
          <linearGradient id={`${uid}_gmeet_gloss`} x1="12" y1="10" x2="28" y2="24" gradientUnits="userSpaceOnUse">
            <stop offset="0%" stopColor="#FFFFFF" stopOpacity="0.75" />
            <stop offset="50%" stopColor="#FFFFFF" stopOpacity="0.1" />
            <stop offset="100%" stopColor="#FFFFFF" stopOpacity="0" />
          </linearGradient>

          {/* Extruded Depth Bevel */}
          <linearGradient id={`${uid}_gmeet_depth`} x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" stopColor="#064E3B" stopOpacity="0.4" />
            <stop offset="100%" stopColor="#064E3B" stopOpacity="0.9" />
          </linearGradient>
        </defs>

        {/* Soft 3D Ground Shadow */}
        <ellipse cx="24" cy="43" rx="18" ry="4" fill={`url(#${uid}_gmeet_shadow)`} />

        {/* 3D Extruded Base Drop Depth */}
        <rect x="7" y="13" width="22" height="23" rx="6" fill={`url(#${uid}_gmeet_depth)`} />
        <path d="M29 20.5L42 12V36L29 27.5V20.5Z" fill="#1E3A8A" opacity="0.6" />

        {/* Main 3D Camera Body */}
        <rect x="7" y="11" width="22" height="23" rx="6" fill={`url(#${uid}_gmeet_green)`} />

        {/* Yellow Bottom-Left Sub-Quadrant for Authentic Meet Colors */}
        <path
          d="M7 26H16V34H13C9.68629 34 7 31.3137 7 28V26Z"
          fill={`url(#${uid}_gmeet_yellow)`}
        />

        {/* Red Bottom-Right Sub-Quadrant */}
        <path
          d="M16 26H29V34H16V26Z"
          fill={`url(#${uid}_gmeet_red)`}
        />

        {/* 3D Projection Lens Cone */}
        <path
          d="M29 19.5L41.6 11.2C42.4 10.7 43.5 11.3 43.5 12.3V33.7C43.5 34.7 42.4 35.3 41.6 34.8L29 26.5V19.5Z"
          fill={`url(#${uid}_gmeet_blue)`}
        />

        {/* Lens Rim 3D Bevel */}
        <path
          d="M41.6 11.2L29 19.5V20.5L41.6 12.2C42.4 11.7 43.5 12.3 43.5 13.3V12.3C43.5 11.3 42.4 10.7 41.6 11.2Z"
          fill="#93C5FD"
          opacity="0.9"
        />

        {/* Top Gloss Curve for High-Definition 3D Glass Surface */}
        <rect x="8" y="12" width="20" height="9" rx="4" fill={`url(#${uid}_gmeet_gloss)`} />
        <circle cx="14" cy="18" r="3" fill="#FFFFFF" opacity="0.35" />
      </svg>
    );
  }

  // ZOOM 3D ICON
  if (normalized === 'zoom' || normalized === 'zoom-us') {
    return (
      <svg
        width={pixelSize}
        height={pixelSize}
        viewBox="0 0 48 48"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
        className={`inline-block shrink-0 transition-transform hover:scale-105 ${className}`}
        style={{
          filter: showGlow ? 'drop-shadow(0 4px 10px rgba(14, 114, 237, 0.45))' : undefined,
        }}
        aria-label="Zoom 3D"
        role="img"
      >
        <defs>
          {/* Ambient Ground Shadow */}
          <radialGradient id={`${uid}_zoom_shadow`} cx="50%" cy="50%" r="50%">
            <stop offset="0%" stopColor="#0B52B5" stopOpacity="0.5" />
            <stop offset="100%" stopColor="#0B52B5" stopOpacity="0" />
          </radialGradient>

          {/* 3D Blue Squircle Gradient */}
          <linearGradient id={`${uid}_zoom_body`} x1="6" y1="5" x2="42" y2="43" gradientUnits="userSpaceOnUse">
            <stop offset="0%" stopColor="#4AA8FF" />
            <stop offset="35%" stopColor="#2D8CFF" />
            <stop offset="75%" stopColor="#0E72ED" />
            <stop offset="100%" stopColor="#0952B5" />
          </linearGradient>

          {/* 3D Inner Bevel Highlight */}
          <linearGradient id={`${uid}_zoom_rim`} x1="24" y1="5" x2="24" y2="43" gradientUnits="userSpaceOnUse">
            <stop offset="0%" stopColor="#FFFFFF" stopOpacity="0.6" />
            <stop offset="15%" stopColor="#FFFFFF" stopOpacity="0.1" />
            <stop offset="85%" stopColor="#042C69" stopOpacity="0.2" />
            <stop offset="100%" stopColor="#021C44" stopOpacity="0.6" />
          </linearGradient>

          {/* White Camera 3D Gradient */}
          <linearGradient id={`${uid}_zoom_cam`} x1="12" y1="16" x2="28" y2="32" gradientUnits="userSpaceOnUse">
            <stop offset="0%" stopColor="#FFFFFF" />
            <stop offset="85%" stopColor="#F1F5F9" />
            <stop offset="100%" stopColor="#CBD5E1" />
          </linearGradient>

          {/* White Lens Cone 3D Gradient */}
          <linearGradient id={`${uid}_zoom_lens`} x1="27" y1="18" x2="38" y2="30" gradientUnits="userSpaceOnUse">
            <stop offset="0%" stopColor="#FFFFFF" />
            <stop offset="100%" stopColor="#E2E8F0" />
          </linearGradient>

          {/* Gloss Top Specular Light */}
          <linearGradient id={`${uid}_zoom_specular`} x1="12" y1="6" x2="36" y2="22" gradientUnits="userSpaceOnUse">
            <stop offset="0%" stopColor="#FFFFFF" stopOpacity="0.5" />
            <stop offset="100%" stopColor="#FFFFFF" stopOpacity="0" />
          </linearGradient>
        </defs>

        {/* Soft 3D Shadow Base */}
        <ellipse cx="24" cy="44" rx="17" ry="3.5" fill={`url(#${uid}_zoom_shadow)`} />

        {/* 3D Extrusion Back Layer */}
        <rect x="5" y="7" width="38" height="36" rx="12" fill="#063A82" />

        {/* 3D Main Squircle */}
        <rect x="5" y="5" width="38" height="36" rx="12" fill={`url(#${uid}_zoom_body)`} />
        {/* Rim Bevel */}
        <rect x="5" y="5" width="38" height="36" rx="12" stroke={`url(#${uid}_zoom_rim)`} strokeWidth="1.5" />

        {/* Glass Reflection Arc */}
        <path
          d="M7 16C7 11.0294 11.0294 7 16 7H32C36.9706 7 41 11.0294 41 16V20C32 22 16 19 7 24V16Z"
          fill={`url(#${uid}_zoom_specular)`}
        />

        {/* 3D White Camera Body with Drop Shadow */}
        <g style={{ filter: 'drop-shadow(0 2px 4px rgba(0, 26, 77, 0.45))' }}>
          <rect x="11" y="16.5" width="16" height="13" rx="3.5" fill={`url(#${uid}_zoom_cam)`} />
          {/* Camera Lens Cone */}
          <path
            d="M27.5 20.8L35.8 16.5C36.6 16.1 37.5 16.7 37.5 17.6V28.4C37.5 29.3 36.6 29.9 35.8 29.5L27.5 25.2V20.8Z"
            fill={`url(#${uid}_zoom_lens)`}
          />
          {/* Subtle Lens Glint */}
          <ellipse cx="32" cy="23" rx="1.5" ry="3" fill="#38BDF8" opacity="0.3" />
        </g>
      </svg>
    );
  }

  // MICROSOFT TEAMS 3D ICON
  if (normalized === 'teams' || normalized === 'ms-teams' || normalized === 'microsoft-teams') {
    return (
      <svg
        width={pixelSize}
        height={pixelSize}
        viewBox="0 0 48 48"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
        className={`inline-block shrink-0 transition-transform hover:scale-105 ${className}`}
        style={{
          filter: showGlow ? 'drop-shadow(0 4px 10px rgba(99, 102, 241, 0.45))' : undefined,
        }}
        aria-label="Microsoft Teams 3D"
        role="img"
      >
        <defs>
          {/* Ambient Ground Shadow */}
          <radialGradient id={`${uid}_teams_shadow`} cx="50%" cy="50%" r="50%">
            <stop offset="0%" stopColor="#3730A3" stopOpacity="0.5" />
            <stop offset="100%" stopColor="#3730A3" stopOpacity="0" />
          </radialGradient>

          {/* Back Tile 3D Gradient (Avatars) */}
          <linearGradient id={`${uid}_teams_back`} x1="18" y1="8" x2="42" y2="36" gradientUnits="userSpaceOnUse">
            <stop offset="0%" stopColor="#6366F1" />
            <stop offset="40%" stopColor="#4F46E5" />
            <stop offset="100%" stopColor="#3730A3" />
          </linearGradient>

          {/* Front Tile 3D Gradient ('T' Badge) */}
          <linearGradient id={`${uid}_teams_front`} x1="6" y1="12" x2="30" y2="40" gradientUnits="userSpaceOnUse">
            <stop offset="0%" stopColor="#818CF8" />
            <stop offset="30%" stopColor="#6366F1" />
            <stop offset="80%" stopColor="#4338CA" />
            <stop offset="100%" stopColor="#312E81" />
          </linearGradient>

          {/* Embossed White 'T' Gradient */}
          <linearGradient id={`${uid}_teams_t`} x1="14" y1="18" x2="22" y2="32" gradientUnits="userSpaceOnUse">
            <stop offset="0%" stopColor="#FFFFFF" />
            <stop offset="100%" stopColor="#E0E7FF" />
          </linearGradient>

          {/* Gloss Sheen */}
          <linearGradient id={`${uid}_teams_gloss`} x1="8" y1="13" x2="26" y2="25" gradientUnits="userSpaceOnUse">
            <stop offset="0%" stopColor="#FFFFFF" stopOpacity="0.6" />
            <stop offset="100%" stopColor="#FFFFFF" stopOpacity="0" />
          </linearGradient>
        </defs>

        {/* Ambient Ground Shadow */}
        <ellipse cx="24" cy="44" rx="17" ry="3.5" fill={`url(#${uid}_teams_shadow)`} />

        {/* BACK TILE: Microsoft Teams Meeting Participants */}
        {/* Back Tile Depth Extrusion */}
        <rect x="20" y="10" width="22" height="24" rx="6" fill="#1E1B4B" opacity="0.7" />
        {/* Back Tile Face */}
        <rect x="20" y="8" width="22" height="24" rx="6" fill={`url(#${uid}_teams_back)`} />

        {/* Small Avatar Silhouettes on Back Tile */}
        <circle cx="31" cy="15" r="3" fill="#E0E7FF" opacity="0.9" />
        <path
          d="M26 24C26 21.2386 28.2386 19 31 19C33.7614 19 36 21.2386 36 24V25H26V24Z"
          fill="#E0E7FF"
          opacity="0.85"
        />

        {/* FRONT TILE: High-Elevation 'T' Badge */}
        {/* Tile Depth / Ambient Occlusion Drop Shadow */}
        <g style={{ filter: 'drop-shadow(0 4px 6px rgba(15, 23, 42, 0.45))' }}>
          <rect x="6" y="14" width="22" height="24" rx="6" fill="#1E1B4B" />
          <rect x="6" y="12" width="22" height="24" rx="6" fill={`url(#${uid}_teams_front)`} />
          {/* Top Glass Bevel */}
          <rect x="6" y="12" width="22" height="24" rx="6" stroke="#A5B4FC" strokeWidth="1" opacity="0.5" />
          <path
            d="M8 18C8 14.6863 10.6863 12 14 12H20C23.3137 12 26 14.6863 26 18V21C20 22 12 21 8 23V18Z"
            fill={`url(#${uid}_teams_gloss)`}
          />
        </g>

        {/* 3D Embossed White 'T' Emblem */}
        <g style={{ filter: 'drop-shadow(0 1px 2px rgba(30, 27, 75, 0.6))' }}>
          <path
            d="M12 18.5C12 17.6716 12.6716 17 13.5 17H20.5C21.3284 17 22 17.6716 22 18.5V20C22 20.5523 21.5523 21 21 21H18.5V29C18.5 29.5523 18.0523 30 17.5 30H16.5C15.9477 30 15.5 29.5523 15.5 29V21H13C12.4477 21 12 20.5523 12 20V18.5Z"
            fill={`url(#${uid}_teams_t)`}
          />
        </g>
      </svg>
    );
  }

  // ALL PLATFORMS / UNIVERSAL 3D ICON
  if (normalized === 'all' || normalized === 'universal' || normalized === 'all-platforms') {
    return (
      <svg
        width={pixelSize}
        height={pixelSize}
        viewBox="0 0 48 48"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
        className={`inline-block shrink-0 transition-transform hover:scale-105 ${className}`}
        style={{
          filter: showGlow ? 'drop-shadow(0 4px 10px rgba(99, 102, 241, 0.45))' : undefined,
        }}
        aria-label="All Platforms 3D"
        role="img"
      >
        <defs>
          <radialGradient id={`${uid}_all_shadow`} cx="50%" cy="50%" r="50%">
            <stop offset="0%" stopColor="#4F46E5" stopOpacity="0.45" />
            <stop offset="100%" stopColor="#4F46E5" stopOpacity="0" />
          </radialGradient>

          <linearGradient id={`${uid}_all_sphere`} x1="10" y1="8" x2="38" y2="40" gradientUnits="userSpaceOnUse">
            <stop offset="0%" stopColor="#818CF8" />
            <stop offset="35%" stopColor="#6366F1" />
            <stop offset="70%" stopColor="#4F46E5" />
            <stop offset="100%" stopColor="#3730A3" />
          </linearGradient>

          <linearGradient id={`${uid}_ring_gmeet`} x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="#34D399" />
            <stop offset="100%" stopColor="#059669" />
          </linearGradient>

          <linearGradient id={`${uid}_ring_zoom`} x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="#60A5FA" />
            <stop offset="100%" stopColor="#2563EB" />
          </linearGradient>

          <linearGradient id={`${uid}_all_gloss`} x1="16" y1="10" x2="32" y2="24" gradientUnits="userSpaceOnUse">
            <stop offset="0%" stopColor="#FFFFFF" stopOpacity="0.7" />
            <stop offset="100%" stopColor="#FFFFFF" stopOpacity="0" />
          </linearGradient>
        </defs>

        {/* Ambient Ground Shadow */}
        <ellipse cx="24" cy="44" rx="16" ry="3.5" fill={`url(#${uid}_all_shadow)`} />

        {/* Back Orbital Arc (Zoom Blue) */}
        <path
          d="M8 25C9 14 39 12 41 23"
          stroke={`url(#${uid}_ring_zoom)`}
          strokeWidth="2.5"
          strokeLinecap="round"
          opacity="0.8"
        />

        {/* 3D Core Sphere with Depth */}
        <circle cx="24" cy="24" r="14" fill={`url(#${uid}_all_sphere)`} />

        {/* Front Orbital Arc (Google Meet Green) */}
        <path
          d="M7 23C9 35 39 36 41 25"
          stroke={`url(#${uid}_ring_gmeet)`}
          strokeWidth="2.5"
          strokeLinecap="round"
        />

        {/* Inner Holographic 3D Video Badge */}
        <g style={{ filter: 'drop-shadow(0 2px 4px rgba(0,0,0,0.3))' }}>
          <rect x="17" y="19" width="10" height="9" rx="2" fill="#FFFFFF" />
          <path d="M27 21.5L32 18.5V27.5L27 24.5V21.5Z" fill="#FFFFFF" />
        </g>

        {/* Specular Highlight Gloss */}
        <ellipse cx="21" cy="16" rx="6" ry="3" fill={`url(#${uid}_all_gloss)`} transform="rotate(-20 21 16)" />
        <circle cx="27" cy="14" r="1.5" fill="#FFFFFF" opacity="0.6" />
      </svg>
    );
  }

  // DEFAULT / UNKNOWN 3D ICON (Browser / Web Conference)
  return (
    <svg
      width={pixelSize}
      height={pixelSize}
      viewBox="0 0 48 48"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      className={`inline-block shrink-0 transition-transform hover:scale-105 ${className}`}
      style={{
        filter: showGlow ? 'drop-shadow(0 3px 8px rgba(100, 116, 139, 0.3))' : undefined,
      }}
      aria-label="Web Meeting 3D"
      role="img"
    >
      <defs>
        <radialGradient id={`${uid}_def_shadow`} cx="50%" cy="50%" r="50%">
          <stop offset="0%" stopColor="#475569" stopOpacity="0.4" />
          <stop offset="100%" stopColor="#475569" stopOpacity="0" />
        </radialGradient>
        <linearGradient id={`${uid}_def_body`} x1="8" y1="8" x2="40" y2="40" gradientUnits="userSpaceOnUse">
          <stop offset="0%" stopColor="#94A3B8" />
          <stop offset="50%" stopColor="#64748B" />
          <stop offset="100%" stopColor="#475569" />
        </linearGradient>
      </defs>
      <ellipse cx="24" cy="43" rx="16" ry="3.5" fill={`url(#${uid}_def_shadow)`} />
      <rect x="8" y="10" width="32" height="26" rx="8" fill={`url(#${uid}_def_body)`} />
      <circle cx="14" cy="15" r="1.5" fill="#F87171" />
      <circle cx="19" cy="15" r="1.5" fill="#FBBF24" />
      <circle cx="24" cy="15" r="1.5" fill="#34D399" />
      <path d="M16 26L22 21V31L16 26Z" fill="#FFFFFF" />
      <rect x="23" y="22" width="10" height="8" rx="2" fill="#FFFFFF" />
    </svg>
  );
};
